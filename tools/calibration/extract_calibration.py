#!/usr/bin/env python3
"""Extract Bublcam factory calibration from a THM JPEG without changing it."""

import argparse
import base64
import binascii
import json
from pathlib import Path


MARKER = b"calibration="
ALPHABET = frozenset(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")


def extract(path: str | Path) -> dict:
    data = Path(path).read_bytes()
    if not data.startswith(b"\xff\xd8"):
        raise ValueError("THM is not a JPEG")
    start = data.find(MARKER)
    if start < 0:
        raise ValueError("calibration= marker not found")
    start += len(MARKER)
    end = start
    while end < len(data) and data[end] in ALPHABET:
        end += 1
    if end == start:
        raise ValueError("empty calibration payload")
    try:
        decoded = base64.b64decode(data[start:end], validate=True)
        result = json.loads(decoded.decode("utf-8"))
    except (binascii.Error, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid calibration payload: {exc}") from exc
    if not isinstance(result, dict) or not isinstance(result.get("cameras"), dict):
        raise ValueError("calibration JSON has no cameras object")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("thm", help="original THM JPEG")
    parser.add_argument("-o", "--output", help="write decoded JSON here")
    args = parser.parse_args()
    try:
        content = json.dumps(extract(args.thm), indent=2) + "\n"
        if args.output:
            Path(args.output).write_text(content, encoding="utf-8")
        else:
            print(content, end="")
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Calibration extraction failed: {exc}\n")


if __name__ == "__main__":
    main()
