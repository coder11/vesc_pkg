#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
import xml.etree.ElementTree as ET


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Convert Balance EX settings.xml into a typed Python config stub.")
    p.add_argument(
        "--conf-dir",
        default=None,
        help="Path to Balance EX conf directory (default: ../balance_ex/conf relative to this script).",
    )
    p.add_argument("--in", dest="in_path", required=True, help="Input settings.xml path")
    p.add_argument("--out", dest="out_path", required=True, help="Output .py path")
    p.add_argument("--var", default="CONFIG", help='Variable name to write (default: "CONFIG")')
    return p.parse_args()


def _get_text(parent: ET.Element, tag: str, default: str | None = None) -> str:
    el = parent.find(tag)
    if el is None or el.text is None:
        if default is None:
            raise KeyError(f"missing <{tag}> in <{parent.tag}>")
        return default
    return el.text


def _get_int(parent: ET.Element, tag: str, default: int | None = None) -> int:
    el = parent.find(tag)
    if el is None or el.text is None:
        if default is None:
            raise KeyError(f"missing <{tag}> in <{parent.tag}>")
        return default
    return int(el.text)


def _get_float(parent: ET.Element, tag: str, default: float | None = None) -> float:
    el = parent.find(tag)
    if el is None or el.text is None:
        if default is None:
            raise KeyError(f"missing <{tag}> in <{parent.tag}>")
        return default
    return float(el.text)


def main() -> int:
    args = _parse_args()

    tools_dir = os.path.dirname(os.path.abspath(__file__))
    conf_dir = (
        os.path.abspath(args.conf_dir)
        if args.conf_dir
        else os.path.abspath(os.path.join(tools_dir, "..", "balance_ex", "conf"))
    )
    sys.path.insert(0, tools_dir)  # settings_gen

    from settings_gen.model import (  # noqa: E402
        BoolParam,
        ConfigParams,
        Description,
        DoubleParam,
        EnumParam,
        Group,
        InfoParam,
        IntParam,
        Ref,
        Sep,
        StringParam,
        SubGroup,
    )

    in_path = os.path.abspath(args.in_path)
    out_path = os.path.abspath(args.out_path)

    tree = ET.parse(in_path)
    root = tree.getroot()

    params_el = root.find("Params")
    if params_el is None:
        raise SystemExit("Invalid XML: missing <Params>")

    params = []
    for p_el in list(params_el):
        pid = p_el.tag
        long_name = _get_text(p_el, "longName", "")
        typ = _get_int(p_el, "type")
        trans = _get_int(p_el, "transmittable", 0) != 0
        desc = Description(_get_text(p_el, "description", ""), format="qrich")
        c_define = _get_text(p_el, "cDefine", "")

        if typ == 0:
            params.append(InfoParam(pid, long_name, trans, desc, c_define=c_define))
        elif typ == 1:
            params.append(
                DoubleParam(
                    pid,
                    long_name,
                    trans,
                    desc,
                    c_define=c_define,
                    editor_decimals=_get_int(p_el, "editorDecimalsDouble", 1),
                    editor_scale=_get_float(p_el, "editorScale", 1.0),
                    edit_as_percentage=_get_int(p_el, "editAsPercentage", 0) != 0,
                    max_double=_get_float(p_el, "maxDouble"),
                    min_double=_get_float(p_el, "minDouble"),
                    show_display=_get_int(p_el, "showDisplay", 0) != 0,
                    step_double=_get_float(p_el, "stepDouble"),
                    value=_get_float(p_el, "valDouble"),
                    vtx_double_scale=_get_int(p_el, "vTxDoubleScale", 1000),
                    suffix=_get_text(p_el, "suffix", ""),
                    vtx=_get_int(p_el, "vTx", 9),
                )
            )
        elif typ == 2:
            params.append(
                IntParam(
                    pid,
                    long_name,
                    trans,
                    desc,
                    c_define=c_define,
                    editor_scale=_get_int(p_el, "editorScale", 1),
                    edit_as_percentage=_get_int(p_el, "editAsPercentage", 0) != 0,
                    max_int=_get_int(p_el, "maxInt"),
                    min_int=_get_int(p_el, "minInt"),
                    show_display=_get_int(p_el, "showDisplay", 0) != 0,
                    step_int=_get_int(p_el, "stepInt"),
                    value=_get_int(p_el, "valInt"),
                    suffix=_get_text(p_el, "suffix", ""),
                    vtx=_get_int(p_el, "vTx", 3),
                )
            )
        elif typ == 3:
            params.append(
                StringParam(
                    pid,
                    long_name,
                    trans,
                    desc,
                    c_define=c_define,
                    value=_get_text(p_el, "valString", ""),
                    max_len=_get_int(p_el, "maxLen", 0),
                )
            )
        elif typ == 4:
            enum_names = [e.text or "" for e in p_el.findall("enumNames")]
            params.append(
                EnumParam(
                    pid,
                    long_name,
                    trans,
                    desc,
                    c_define=c_define,
                    value=_get_int(p_el, "valInt"),
                    enum_names=enum_names,
                )
            )
        elif typ == 5:
            params.append(
                BoolParam(
                    pid,
                    long_name,
                    trans,
                    desc,
                    c_define=c_define,
                    value=_get_int(p_el, "valInt", 0) != 0,
                )
            )
        else:
            raise ValueError(f"Unsupported param type code: {typ} for {pid}")

    ser = root.find("SerOrder")
    ser_order = [e.text or "" for e in ser.findall("ser")] if ser is not None else []

    grouping_el = root.find("Grouping")
    groups: list[Group] = []
    if grouping_el is not None:
        for g_el in grouping_el.findall("group"):
            g_name = _get_text(g_el, "groupName", "")
            subgroups: list[SubGroup] = []
            for sg_el in g_el.findall("subgroup"):
                sg_name = _get_text(sg_el, "subgroupName", "")
                sg_params_el = sg_el.find("subgroupParams")
                items = []
                if sg_params_el is not None:
                    for p in sg_params_el.findall("param"):
                        txt = (p.text or "").strip()
                        if txt.startswith("::sep::"):
                            items.append(Sep(txt[len("::sep::") :]))
                        elif txt:
                            items.append(Ref(txt))
                subgroups.append(SubGroup(name=sg_name, items=items))
            groups.append(Group(name=g_name, subgroups=subgroups))

    cfg = ConfigParams(params=params, ser_order=ser_order, grouping=groups)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("from __future__ import annotations\n\n")
        f.write("from settings_gen.model import (\n")
        f.write("    BoolParam, ConfigParams, Description, DoubleParam, EnumParam,\n")
        f.write("    Group, InfoParam, IntParam, Ref, Sep, StringParam, SubGroup,\n")
        f.write(")\n\n")
        f.write("# Converted from settings.xml. Descriptions are kept as qrich HTML.\n")
        f.write("# You can gradually replace Description(..., format='qrich') with plain text.\n\n")
        f.write(f"{args.var} = ConfigParams(\n")
        f.write("    params=[\n")
        for p in params:
            f.write("        " + repr(p) + ",\n")
        f.write("    ],\n")
        f.write("    ser_order=[\n")
        for s in ser_order:
            f.write(f"        {s!r},\n")
        f.write("    ],\n")
        f.write("    grouping=[\n")
        for g in groups:
            f.write("        " + repr(g) + ",\n")
        f.write("    ],\n")
        f.write(")\n")

    # Unused but keeps the default conf-dir discoverable for users.
    _ = conf_dir

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


