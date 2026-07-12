#!/usr/bin/env python3
"""Generate VESC Tool settings and C data types for the package."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Final, Sequence

from settings_c import render_datatypes, write_datatypes
from settings_data import DATATYPES_LICENSE, XML
from settings_schema import ValidationError
from settings_xml import render_settings, write_settings

OUTPUT_PATH: Final[Path] = (
    Path(__file__).resolve().parents[1] / "balance_ex" / "conf" / "settings.xml"
)
DATATYPES_OUTPUT_PATH: Final[Path] = OUTPUT_PATH.with_name("datatypes.h")


def main(arguments: Sequence[str] | None = None) -> int:
    args = tuple(sys.argv[1:] if arguments is None else arguments)
    if args:
        print("usage: generate_settings.py", file=sys.stderr)
        return 2

    try:
        # Render both files before replacing either one so model/rendering errors
        # cannot leave a mismatched generated pair.
        render_settings(XML)
        render_datatypes(XML, license=DATATYPES_LICENSE)
        write_settings(XML, OUTPUT_PATH)
        write_datatypes(XML, DATATYPES_OUTPUT_PATH, license=DATATYPES_LICENSE)
    except (OSError, ValidationError, ValueError) as error:
        print(f"generated settings were not written: {error}", file=sys.stderr)
        return 1

    print(f"wrote {OUTPUT_PATH}")
    print(f"wrote {DATATYPES_OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
