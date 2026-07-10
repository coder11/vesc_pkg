#!/usr/bin/env python3
"""Generate balance_ex's VESC Tool settings.xml from typed Python data."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Final, Sequence

from settings_data import XML
from settings_schema import ValidationError
from settings_xml import write_settings


OUTPUT_PATH: Final[Path] = (
    Path(__file__).resolve().parents[1] / "balance_ex" / "conf" / "settings.xml"
)


def main(arguments: Sequence[str] | None = None) -> int:
    args = tuple(sys.argv[1:] if arguments is None else arguments)
    if args:
        print("usage: generate_settings.py", file=sys.stderr)
        return 2

    try:
        write_settings(XML, OUTPUT_PATH)
    except (OSError, ValidationError, ValueError) as error:
        print(f"settings.xml was not written: {error}", file=sys.stderr)
        return 1

    print(f"wrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
