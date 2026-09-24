"""Batch-stitch every calibrated JPG/THM pair in a Bublcam DCIM directory."""

from __future__ import annotations

import argparse
import contextlib
import csv
import io
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import cv2

from bubl_stitch import stitch


def render(job: tuple[Path, Path, Path, int, int]) -> tuple[str, str]:
    jpg, thm, output, width, height = job
    cv2.setNumThreads(1)
    args = argparse.Namespace(jpg=jpg, thm=thm, output=output,
        width=width, height=height, model="equisolid", blend="feather",
        convention="camera-to-world", turns="0,0,0,0", debug_dir=None,
        verbose=False)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            stitch(args)
        return jpg.name, "ok"
    except Exception as error:
        output.unlink(missing_ok=True)
        return jpg.name, f"error: {error}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path("sd_contents/dcim"))
    parser.add_argument("--output-dir", type=Path, default=Path("stitched"))
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--width", type=int, default=4096)
    parser.add_argument("--height", type=int, default=2048)
    args = parser.parse_args()
    if args.workers < 1 or args.width < 2 or args.height < 2 or args.width != 2 * args.height:
        parser.error("workers must be positive and output dimensions must be positive with 2:1 aspect ratio")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    jobs = []
    results = []
    for jpg in sorted(args.input_dir.glob("*.JPG")):
        thm = jpg.with_suffix(".THM")
        output = args.output_dir / f"{jpg.stem}_equirect.jpg"
        if not thm.exists():
            results.append((jpg.name, "missing THM"))
        elif output.exists() and output.stat().st_size > 0:
            results.append((jpg.name, "skipped: output exists"))
        else:
            jobs.append((jpg, thm, output, args.width, args.height))
    print(f"Rendering {len(jobs)} pairs with {args.workers} workers", flush=True)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(render, job) for job in jobs]
        for number, future in enumerate(as_completed(futures), 1):
            result = future.result()
            results.append(result)
            if number % 25 == 0 or number == len(jobs) or result[1] != "ok":
                print(f"{number}/{len(jobs)} complete: {result[0]} {result[1]}", flush=True)
    report = args.output_dir / "batch_report.csv"
    with report.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("source", "status"))
        writer.writerows(sorted(results))
    failures = [row for row in results if row[1] not in ("ok", "skipped: output exists")]
    print(f"Report: {report}; failures: {len(failures)}", flush=True)
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
