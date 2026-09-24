"""Compare lens models and R conventions with matched features in one JPG/THM pair.

Prints scores only; never writes or prints source pixels or calibration values.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bubl_stitch import infer_turns, read_calibration, split_image  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jpg", type=Path)
    parser.add_argument("thm", type=Path)
    args = parser.parse_args()

    image = cv2.imread(str(args.jpg), cv2.IMREAD_COLOR)
    if image is None:
        parser.error(f"Cannot read JPEG: {args.jpg}")
    quads = split_image(image)
    cameras = read_calibration(args.thm)["cameras"]
    print("model,convention,turns,score")
    for model in ("equidistant", "equisolid", "stereographic"):
        for convention in ("camera-to-world", "world-to-camera"):
            try:
                turns, score = infer_turns(quads, cameras, model, convention)
                print(f"{model},{convention},{'/'.join(map(str, turns))},{score:.2f}")
            except ValueError as error:
                print(f"{model},{convention},unavailable,{error}", file=sys.stderr)


if __name__ == "__main__":
    main()
