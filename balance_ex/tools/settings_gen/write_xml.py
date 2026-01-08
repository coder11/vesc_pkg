from __future__ import annotations

import xml.etree.ElementTree as ET

from .model import (
    BoolParam,
    ConfigParams,
    DoubleParam,
    EnumParam,
    InfoParam,
    IntParam,
    Ref,
    Sep,
    StringParam,
)
from .qrichtext import description_to_qrich


def _t(parent: ET.Element, tag: str, text: str) -> ET.Element:
    el = ET.SubElement(parent, tag)
    el.text = text
    return el


def _fmt_float(v: float) -> str:
    if float(v).is_integer():
        return str(int(v))
    return str(v)


def _indent(elem: ET.Element, level: int = 0) -> None:
    i = "\n" + " " * (level * 4)
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + " " * 4
        for child in elem:
            _indent(child, level + 1)
        if not elem[-1].tail or not elem[-1].tail.strip():
            elem[-1].tail = i
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i


def build_tree(cfg: ConfigParams) -> ET.ElementTree:
    root = ET.Element("ConfigParams")

    params_el = ET.SubElement(root, "Params")
    for p in cfg.params:
        p_el = ET.SubElement(params_el, p.id)
        _t(p_el, "longName", p.long_name)
        _t(p_el, "type", str(p.type_code()))
        _t(p_el, "transmittable", "1" if p.transmittable else "0")
        _t(p_el, "description", description_to_qrich(p.description))
        _t(p_el, "cDefine", p.c_define)

        if isinstance(p, InfoParam):
            pass
        elif isinstance(p, StringParam):
            _t(p_el, "valString", p.value)
            _t(p_el, "maxLen", str(p.max_len))
        elif isinstance(p, BoolParam):
            _t(p_el, "valInt", "1" if p.value else "0")
        elif isinstance(p, EnumParam):
            _t(p_el, "valInt", str(p.value))
            for name in p.enum_names:
                _t(p_el, "enumNames", name)
        elif isinstance(p, IntParam):
            _t(p_el, "editorScale", str(p.editor_scale))
            _t(p_el, "editAsPercentage", "1" if p.edit_as_percentage else "0")
            _t(p_el, "maxInt", str(p.max_int))
            _t(p_el, "minInt", str(p.min_int))
            _t(p_el, "showDisplay", "1" if p.show_display else "0")
            _t(p_el, "stepInt", str(p.step_int))
            _t(p_el, "valInt", str(p.value))
            _t(p_el, "suffix", p.suffix)
            _t(p_el, "vTx", str(p.vtx))
        elif isinstance(p, DoubleParam):
            _t(p_el, "editorDecimalsDouble", str(p.editor_decimals))
            _t(p_el, "editorScale", _fmt_float(p.editor_scale))
            _t(p_el, "editAsPercentage", "1" if p.edit_as_percentage else "0")
            _t(p_el, "maxDouble", _fmt_float(p.max_double))
            _t(p_el, "minDouble", _fmt_float(p.min_double))
            _t(p_el, "showDisplay", "1" if p.show_display else "0")
            _t(p_el, "stepDouble", _fmt_float(p.step_double))
            _t(p_el, "valDouble", _fmt_float(p.value))
            _t(p_el, "vTxDoubleScale", str(p.vtx_double_scale))
            _t(p_el, "suffix", p.suffix)
            _t(p_el, "vTx", str(p.vtx))
        else:  # pragma: no cover
            raise TypeError(f"Unhandled param type: {type(p).__name__}")

    ser = ET.SubElement(root, "SerOrder")
    for pid in cfg.ser_order:
        _t(ser, "ser", pid)

    grouping = ET.SubElement(root, "Grouping")
    for g in cfg.grouping:
        group_el = ET.SubElement(grouping, "group")
        _t(group_el, "groupName", g.name)
        for sg in g.subgroups:
            sg_el = ET.SubElement(group_el, "subgroup")
            _t(sg_el, "subgroupName", sg.name)
            sg_params = ET.SubElement(sg_el, "subgroupParams")
            for item in sg.items:
                if isinstance(item, Sep):
                    _t(sg_params, "param", f"::sep::{item.title}")
                elif isinstance(item, Ref):
                    _t(sg_params, "param", item.param_id)
                else:  # pragma: no cover
                    raise TypeError(f"Unhandled GroupItem: {type(item).__name__}")

    _indent(root)
    return ET.ElementTree(root)


def to_bytes(cfg: ConfigParams) -> bytes:
    root = build_tree(cfg).getroot()
    body = ET.tostring(
        root,
        encoding="utf-8",
        xml_declaration=False,
        short_empty_elements=False,
    )
    header = b'<?xml version="1.0" encoding="UTF-8"?>\n'
    return header + body


