#!/usr/bin/env python3
"""Read-only OSC probes for Bublcam firmware 2.1.1."""

import argparse
import json
import urllib.error
import urllib.request


def request(host: str, command: str, fingerprint: str | None = None) -> dict:
    if command == "info":
        path, method, payload = "/osc/info", "GET", None
    elif command == "state":
        path, method, payload = "/osc/state", "POST", {}
    else:
        if fingerprint is None:
            raise ValueError("updates requires --fingerprint from a prior state response")
        path, method = "/osc/checkForUpdates", "POST"
        payload = {"stateFingerprint": fingerprint, "waitTimeout": 0}

    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"X-XSRF-Protected": "1"}
    if data is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
    req = urllib.request.Request(
        f"http://{host}{path}", data=data, headers=headers, method=method
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.load(response)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("info", "state", "updates"))
    parser.add_argument("--host", default="192.168.0.100")
    parser.add_argument("--fingerprint", help="state fingerprint for updates")
    args = parser.parse_args()
    try:
        print(json.dumps(request(args.host, args.command, args.fingerprint), indent=2))
    except (OSError, ValueError, urllib.error.URLError) as exc:
        parser.exit(1, f"Request failed: {exc}\n")


if __name__ == "__main__":
    main()
