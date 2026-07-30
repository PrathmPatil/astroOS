#!/usr/bin/env python3
"""Download a minimal Swiss Ephemeris file set into backend/ephe/."""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

# Official public mirror (astro.com FTP path is unstable)
BASE = "https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/"
FILES = [
    "seas_18.se1",
    "semo_18.se1",
    "sepl_18.se1",
]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    dest = root / "ephe"
    dest.mkdir(parents=True, exist_ok=True)

    for name in FILES:
        target = dest / name
        if target.exists() and target.stat().st_size > 1000:
            print(f"OK  {name} (exists)")
            continue
        url = BASE + name
        print(f"GET {url}")
        try:
            urllib.request.urlretrieve(url, target)
            print(f"OK  {name} ({target.stat().st_size} bytes)")
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL {name}: {exc}", file=sys.stderr)
            return 1
    print(f"Ephemeris path: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
