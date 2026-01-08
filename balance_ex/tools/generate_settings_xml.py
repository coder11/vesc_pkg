#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import os
import sys


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate Balance EX VESC Tool settings.xml from a typed Python config.")
    p.add_argument(
        "--conf-dir",
        default=None,
        help="Path to Balance EX conf directory (default: ../balance_ex/conf relative to this script).",
    )
    p.add_argument(
        "--module",
        default="settings_src",
        help='Python module (in conf-dir) that provides CONFIG (default: "settings_src").',
    )
    p.add_argument(
        "--var",
        default="CONFIG",
        help='Variable name inside the module that holds the ConfigParams instance (default: "CONFIG").',
    )
    p.add_argument("--out", default="settings.xml", help='Output XML filename (default: "settings.xml").')
    p.add_argument("--check-only", action="store_true", help="Only validate the config, do not write output.")
    return p.parse_args()


def main() -> int:
    args = _parse_args()

    tools_dir = os.path.dirname(os.path.abspath(__file__))
    conf_dir = (
        os.path.abspath(args.conf_dir)
        if args.conf_dir
        else os.path.abspath(os.path.join(tools_dir, "..", "balance_ex", "conf"))
    )

    # Ensure the config modules can import settings_gen, and the CLI can import both.
    sys.path.insert(0, tools_dir)  # settings_gen
    sys.path.insert(0, conf_dir)  # settings_src

    from settings_gen.model import ConfigParams  # noqa: E402
    from settings_gen.write_xml import to_bytes  # noqa: E402

    mod = importlib.import_module(args.module)
    if not hasattr(mod, args.var):
        raise SystemExit(f"Config module {args.module!r} does not define {args.var!r}")

    cfg = getattr(mod, args.var)
    if not isinstance(cfg, ConfigParams):
        raise SystemExit(f"{args.module}.{args.var} must be a ConfigParams, got {type(cfg).__name__}")

    # Force full validation (including cross-reference checks) even if CONFIG was created elsewhere.
    cfg = ConfigParams.model_validate(cfg.model_dump())
    if args.check_only:
        return 0

    out_path = os.path.join(conf_dir, args.out)
    data = to_bytes(cfg)
    with open(out_path, "wb") as f:
        f.write(data)
        f.write(b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


