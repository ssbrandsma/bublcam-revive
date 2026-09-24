"""Stitch a Bublcam four-fisheye JPEG using its companion THM calibration."""

from __future__ import annotations

import argparse
import base64
import json
import math
import re
from pathlib import Path

import cv2
import numpy as np


NAMES = ("topLeft", "topRight", "bottomLeft", "bottomRight")
COLORS = np.array(((64, 64, 240), (64, 210, 64), (240, 160, 64), (210, 64, 210)), np.uint8)


def read_calibration(path: Path) -> dict:
    data = path.read_bytes()
    for match in re.finditer(rb"calibration=([A-Za-z0-9+/=]+)", data):
        try:
            decoded = base64.b64decode(match.group(1), validate=True)
            calibration = json.loads(decoded)
            if all(name in calibration["cameras"] for name in NAMES):
                return calibration
        except (ValueError, KeyError, UnicodeError):
            continue
    raise ValueError(f"No valid calibration= Base64 JSON found in {path}")


def directions(width: int, y0: int, y1: int, height: int) -> np.ndarray:
    lon = ((np.arange(width, dtype=np.float32) + .5) / width * 2 - 1) * np.pi
    lat = (.5 - (np.arange(y0, y1, dtype=np.float32) + .5) / height) * np.pi
    coslat = np.cos(lat)[:, None]
    return np.stack(np.broadcast_arrays(coslat * np.sin(lon)[None, :],
                                         coslat * np.cos(lon)[None, :],
                                         np.sin(lat)[:, None]), axis=-1)


def radial(theta: np.ndarray, half_fov: float, radius: float, model: str) -> np.ndarray:
    if model == "equidistant":
        return radius * theta / half_fov
    if model == "equisolid":
        return radius * np.sin(theta / 2) / np.sin(half_fov / 2)
    if model == "stereographic":
        return radius * np.tan(theta / 2) / np.tan(half_fov / 2)
    raise ValueError(model)


def project(world: np.ndarray, camera: dict, size: int, model: str,
            convention: str, turn: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rotation = np.asarray(camera["orientation"]["R"], dtype=np.float32)
    # R is camera-to-world in the supplied calibration. Retain the alternative
    # to make the reverse-engineering result reproducible.
    camera_xyz = world @ (rotation if convention == "camera-to-world" else rotation.T)
    z = np.clip(camera_xyz[..., 2], -1, 1)
    theta = np.arccos(z)
    half_fov = np.deg2rad(float(camera["fov"])) / 2
    cx = float(camera["centre"]["x"]) * size
    cy = float(camera["centre"]["y"]) * size
    radius = min(cx, cy, size - 1 - cx, size - 1 - cy)
    r = radial(theta, half_fov, radius, model)
    norm = np.maximum(np.hypot(camera_xyz[..., 0], camera_xyz[..., 1]), 1e-8)
    dx = r * camera_xyz[..., 0] / norm
    dy = r * camera_xyz[..., 1] / norm
    # Clockwise quarter-turns of the camera's +x,+y projection in the source.
    turn %= 4
    if turn == 1:
        dx, dy = -dy, dx
    elif turn == 2:
        dx, dy = -dx, -dy
    elif turn == 3:
        dx, dy = dy, -dx
    mapx, mapy = (cx + dx).astype(np.float32), (cy + dy).astype(np.float32)
    valid = ((theta <= half_fov) & (mapx >= 1) & (mapx < size - 2)
             & (mapy >= 1) & (mapy < size - 2))
    weight = np.maximum(0, 1 - (theta / half_fov) ** 2) ** 2
    return mapx, mapy, np.where(valid, weight, 0).astype(np.float32)


def split_image(image: np.ndarray) -> list[np.ndarray]:
    h, w = image.shape[:2]
    if h != w or h % 2:
        raise ValueError(f"Expected an even square 2x2 mosaic, got {w}x{h}")
    s = w // 2
    return [image[:s, :s], image[:s, s:], image[s:, :s], image[s:, s:]]


def sample(quad: np.ndarray, maps: tuple) -> np.ndarray:
    mx, my, weight = maps
    out = cv2.remap(quad, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    out[weight == 0] = 0
    return out


def infer_turns(quads: list[np.ndarray], cameras: dict, model: str,
                convention: str) -> tuple[list[int], float]:
    """Choose turns by comparing 3D rays of matched SIFT features."""
    size = 960
    small = [cv2.resize(q, (size, size), interpolation=cv2.INTER_AREA) for q in quads]
    sift = cv2.SIFT_create(nfeatures=5000)
    features = [sift.detectAndCompute(cv2.cvtColor(q, cv2.COLOR_BGR2GRAY), None) for q in small]
    matcher = cv2.BFMatcher()
    pair_scores = {}
    for a in range(4):
        for b in range(a + 1, 4):
            if features[a][1] is None or features[b][1] is None:
                continue
            matches = [pair[0] for pair in matcher.knnMatch(features[a][1], features[b][1], k=2)
                       if len(pair) == 2 and pair[0].distance < .75 * pair[1].distance]
            if len(matches) < 5:
                continue
            pa = np.array([features[a][0][m.queryIdx].pt for m in matches])
            pb = np.array([features[b][0][m.trainIdx].pt for m in matches])
            rays_a = [unproject_points(pa, cameras[NAMES[a]], size, model, convention, turn)
                      for turn in range(4)]
            rays_b = [unproject_points(pb, cameras[NAMES[b]], size, model, convention, turn)
                      for turn in range(4)]
            scores = np.zeros((4, 4), np.float64)
            for ta in range(4):
                for tb in range(4):
                    angle = np.rad2deg(np.arccos(np.clip(np.sum(rays_a[ta] * rays_b[tb], axis=1), -1, 1)))
                    # A true correspondence should map to nearly the same ray.
                    # Nearby objects retain a few degrees of camera parallax.
                    scores[ta, tb] = np.count_nonzero(angle < 5) + .25 * np.count_nonzero(angle < 2)
            pair_scores[a, b] = scores
    if not pair_scores:
        raise ValueError("Could not infer source rotations: no matching features; supply --turns")
    best, best_score = None, -1.0
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(4):
                    turns = (a, b, c, d)
                    score = sum(pair_scores[i, j][turns[i], turns[j]] for i, j in pair_scores)
                    if score > best_score:
                        best, best_score = turns, score
    return list(best), best_score


def unproject_points(points: np.ndarray, camera: dict, size: int, model: str,
                     convention: str, turn: int) -> np.ndarray:
    cx, cy = float(camera["centre"]["x"]) * size, float(camera["centre"]["y"]) * size
    dx, dy = points[:, 0] - cx, points[:, 1] - cy
    if turn == 1:
        dx, dy = dy, -dx
    elif turn == 2:
        dx, dy = -dx, -dy
    elif turn == 3:
        dx, dy = -dy, dx
    rho = np.hypot(dx, dy)
    radius = min(cx, cy, size - 1 - cx, size - 1 - cy)
    half = np.deg2rad(float(camera["fov"])) / 2
    if model == "equidistant":
        theta = rho / radius * half
    elif model == "equisolid":
        theta = 2 * np.arcsin(np.clip(rho / radius * np.sin(half / 2), 0, 1))
    else:
        theta = 2 * np.arctan(rho / radius * np.tan(half / 2))
    ray = np.stack((np.sin(theta) * dx / np.maximum(rho, 1e-8),
                    np.sin(theta) * dy / np.maximum(rho, 1e-8), np.cos(theta)), axis=1)
    rotation = np.asarray(camera["orientation"]["R"])
    return ray @ (rotation.T if convention == "camera-to-world" else rotation)


def write_image(path: Path, image: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), image):
        raise OSError(f"Could not write {path}")


def stitch(args: argparse.Namespace) -> None:
    calibration = read_calibration(args.thm)
    if args.verbose:
        print(json.dumps(calibration, indent=2))
    mosaic = cv2.imread(str(args.jpg), cv2.IMREAD_COLOR)
    if mosaic is None:
        raise ValueError(f"Could not read {args.jpg}")
    quads = split_image(mosaic)
    cameras = calibration["cameras"]
    size = quads[0].shape[0]
    if args.turns == "auto":
        turns, score = infer_turns(quads, cameras, args.model, args.convention)
        print(f"Inferred clockwise quarter-turns: {dict(zip(NAMES, turns))}; feature agreement score {score:.2f}")
    else:
        turns = [int(x) for x in args.turns.split(",")]
        if len(turns) != 4 or any(x not in range(4) for x in turns):
            raise ValueError("--turns requires four comma-separated values from 0 to 3")
    debug = args.debug_dir
    if debug:
        labeled = mosaic.copy()
        for index, name in enumerate(NAMES):
            ox, oy = (index % 2) * size, (index // 2) * size
            cv2.putText(labeled, name, (ox + 35, oy + 75), cv2.FONT_HERSHEY_SIMPLEX,
                        1.8, (255, 255, 255), 5, cv2.LINE_AA)
        write_image(debug / "quadrants.jpg", labeled)
    output = np.zeros((args.height, args.width, 3), np.uint8)
    no_blend = np.zeros_like(output) if debug else None
    feather = np.zeros_like(output) if debug else None
    coverage = np.zeros_like(output) if debug else None
    individual = [np.zeros_like(output) for _ in NAMES] if debug else None
    for y0 in range(0, args.height, 128):
        y1 = min(args.height, y0 + 128)
        world = directions(args.width, y0, y1, args.height)
        accum = np.zeros((y1 - y0, args.width, 3), np.float32)
        total = np.zeros((y1 - y0, args.width), np.float32)
        hard = np.zeros_like(accum, np.uint8)
        max_weight = np.zeros_like(total)
        bits = np.zeros_like(total, np.uint8)
        for index, (name, quad) in enumerate(zip(NAMES, quads)):
            maps = project(world, cameras[name], size, args.model, args.convention, turns[index])
            pixels = sample(quad, maps)
            weight = maps[2]
            valid = weight > 0
            bits[valid] |= 1 << index
            choose = weight > max_weight
            hard[choose] = pixels[choose]
            max_weight = np.maximum(max_weight, weight)
            accum += pixels.astype(np.float32) * weight[..., None]
            total += weight
            if debug:
                individual[index][y0:y1] = pixels
        blended = np.clip(accum / np.maximum(total[..., None], 1e-8), 0, 255).astype(np.uint8)
        output[y0:y1] = blended if args.blend == "feather" else hard
        if debug:
            no_blend[y0:y1] = hard
            feather[y0:y1] = blended
            col = np.zeros_like(hard)
            for index in range(4):
                col += ((bits & (1 << index)) != 0)[..., None] * (COLORS[index] // 4)
            coverage[y0:y1] = col
    write_image(args.output, output)
    if debug:
        write_image(debug / "coverage.png", coverage)
        for name, image in zip(NAMES, individual):
            write_image(debug / f"camera_{name}.png", image)
        write_image(debug / "panorama_no_blend.jpg", no_blend)
        write_image(debug / "panorama_feather.jpg", feather)
        (debug / "settings.json").write_text(json.dumps({"model": args.model,
            "convention": args.convention, "clockwise_quarter_turns": dict(zip(NAMES, turns))}, indent=2))
    print(f"Wrote {args.output}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jpg", type=Path)
    parser.add_argument("thm", type=Path)
    parser.add_argument("-o", "--output", type=Path, default=Path("panorama.jpg"))
    parser.add_argument("--width", type=int, default=4096)
    parser.add_argument("--height", type=int, default=2048)
    parser.add_argument("--model", choices=("equidistant", "equisolid", "stereographic"), default="equisolid")
    parser.add_argument("--blend", choices=("none", "feather"), default="feather")
    parser.add_argument("--convention", choices=("camera-to-world", "world-to-camera"), default="camera-to-world")
    parser.add_argument("--turns", default="auto", help="auto or four clockwise quarter-turns, e.g. 0,1,2,3")
    parser.add_argument("--debug-dir", type=Path)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    if args.width < 2 or args.height < 2 or args.width != 2 * args.height:
        parser.error("Output must have 2:1 aspect ratio")
    stitch(args)


if __name__ == "__main__":
    main()
