"""Deterministic VESC Tool settings.xml rendering and safe file replacement."""

from __future__ import annotations

import os
import tempfile
import xml.etree.ElementTree as ET
from html import escape as escape_html
from pathlib import Path
from typing import Iterable, Union
from xml.sax.saxutils import escape

from settings_schema import (
    BitfieldParameter,
    BoolParameter,
    DoubleParameter,
    EnumParameter,
    Group,
    IntParameter,
    Parameter,
    RawDescription,
    Separator,
    SettingsXml,
    StringParameter,
    Subgroup,
    TextDescription,
    UndefinedParameter,
    validate_settings,
)


Scalar = Union[str, int, float, bool]

_HTML_HEADER = (
    '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" '
    '"http://www.w3.org/TR/REC-html40/strict.dtd">\n'
    '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
    'p, li { white-space: pre-wrap; }\n'
    '</style></head><body style=" font-family:\'Roboto\'; ; font-weight:400; '
    'font-style:normal;">\n'
)
_PARAGRAPH_STYLE = (
    " margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; "
    "-qt-block-indent:0; text-indent:0px;"
)


def _format_scalar(value: Scalar) -> str:
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, float):
        return format(value, ".15g")
    return str(value)


def _text(value: Scalar) -> str:
    return escape(_format_scalar(value), {'"': "&quot;"})


def _element(lines: list[str], level: int, name: str, value: Scalar) -> None:
    indent = "    " * level
    lines.append(f"{indent}<{name}>{_text(value)}</{name}>")


def _render_text_description(description: TextDescription) -> str:
    normalized = description.text.replace("\r\n", "\n").replace("\r", "\n")
    if not normalized:
        paragraph = (
            f'<p style="-qt-paragraph-type:empty;{_PARAGRAPH_STYLE}"><br /></p>'
        )
        return f"{_HTML_HEADER}{paragraph}</body></html>"

    paragraphs: list[str] = []
    for text in normalized.split("\n\n"):
        content = escape_html(text, quote=False).replace("\n", "<br />\n")
        paragraphs.append(f'<p style="{_PARAGRAPH_STYLE}">{content}</p>')
    body = "\n".join(paragraphs)
    return f"{_HTML_HEADER}{body}</body></html>"


def _render_description(parameter: Parameter) -> str:
    description = parameter.description
    if isinstance(description, RawDescription):
        return description.content
    if isinstance(description, TextDescription):
        return _render_text_description(description)
    raise AssertionError(f"unhandled description type: {type(description)!r}")


def _parameter_fields(parameter: Parameter) -> Iterable[tuple[str, Scalar]]:
    yield "longName", parameter.long_name
    yield "type", int(parameter.type)
    yield "transmittable", parameter.transmittable
    yield "description", _render_description(parameter)
    yield "cDefine", parameter.c_define

    if isinstance(parameter, DoubleParameter):
        yield "editorDecimalsDouble", parameter.decimals
        yield "editorScale", parameter.editor_scale
        yield "editAsPercentage", parameter.edit_as_percentage
        yield "maxDouble", parameter.maximum
        yield "minDouble", parameter.minimum
        yield "showDisplay", parameter.show_display
        yield "stepDouble", parameter.step
        yield "valDouble", parameter.default
        yield "vTxDoubleScale", parameter.tx_scale
        yield "suffix", parameter.suffix
        yield "vTx", int(parameter.tx_type)
    elif isinstance(parameter, IntParameter):
        yield "editorScale", parameter.editor_scale
        yield "editAsPercentage", parameter.edit_as_percentage
        yield "maxInt", parameter.maximum
        yield "minInt", parameter.minimum
        yield "showDisplay", parameter.show_display
        yield "stepInt", parameter.step
        yield "valInt", parameter.default
        yield "suffix", parameter.suffix
        yield "vTx", int(parameter.tx_type)
    elif isinstance(parameter, StringParameter):
        yield "valString", parameter.default
        yield "maxLen", parameter.max_length
    elif isinstance(parameter, EnumParameter):
        yield "valInt", parameter.default
        for choice in parameter.choices:
            yield "enumNames", choice
    elif isinstance(parameter, BoolParameter):
        yield "valInt", parameter.default
    elif isinstance(parameter, BitfieldParameter):
        yield "valInt", parameter.default
        for bit_name in parameter.bit_names:
            yield "enumNames", bit_name
    elif not isinstance(parameter, UndefinedParameter):
        raise AssertionError(f"unhandled parameter type: {type(parameter)!r}")


def _render_subgroup(lines: list[str], subgroup: Subgroup) -> None:
    lines.append("            <subgroup>")
    _element(lines, 4, "subgroupName", subgroup.name)
    lines.append("                <subgroupParams>")
    for item in subgroup.items:
        if isinstance(item, Separator):
            value = f"::sep::{item.title}"
        else:
            value = item.name
        _element(lines, 5, "param", value)
    lines.append("                </subgroupParams>")
    lines.append("            </subgroup>")


def _render_group(lines: list[str], group: Group) -> None:
    lines.append("        <group>")
    _element(lines, 3, "groupName", group.name)
    for subgroup in group.subgroups:
        _render_subgroup(lines, subgroup)
    lines.append("        </group>")


def render_settings(settings: SettingsXml) -> str:
    """Validate and render settings in VESC Tool's canonical element order."""
    validate_settings(settings)
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', "<ConfigParams>", "    <Params>"]

    for parameter in settings.parameters:
        lines.append(f"        <{parameter.name}>")
        for field_name, value in _parameter_fields(parameter):
            _element(lines, 3, field_name, value)
        lines.append(f"        </{parameter.name}>")

    lines.append("    </Params>")
    lines.append("    <SerOrder>")
    for name in settings.serialization_order:
        _element(lines, 2, "ser", name)
    lines.append("    </SerOrder>")
    lines.append("    <Grouping>")
    for group in settings.groups:
        _render_group(lines, group)
    lines.append("    </Grouping>")
    lines.append("</ConfigParams>")
    return "\n".join(lines) + "\n"


def _validate_rendered_xml(xml_text: str, settings: SettingsXml) -> None:
    root = ET.fromstring(xml_text)
    if root.tag != "ConfigParams":
        raise ValueError(f"unexpected root element {root.tag!r}")
    if [child.tag for child in root] != ["Params", "SerOrder", "Grouping"]:
        raise ValueError("rendered XML has an unexpected top-level layout")

    params_element = root.find("Params")
    assert params_element is not None
    rendered_names = [element.tag for element in params_element]
    expected_names = [parameter.name for parameter in settings.parameters]
    if rendered_names != expected_names:
        raise ValueError("rendered XML parameter order changed")

    order_element = root.find("SerOrder")
    assert order_element is not None
    rendered_order = tuple(element.text or "" for element in order_element.findall("ser"))
    if rendered_order != settings.serialization_order:
        raise ValueError("rendered XML serialization order changed")


def write_settings(settings: SettingsXml, destination: Path) -> None:
    """Render, parse-check, and atomically replace destination."""
    xml_text = render_settings(settings)
    _validate_rendered_xml(xml_text, settings)
    destination.parent.mkdir(parents=True, exist_ok=True)

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=destination.parent,
            delete=False,
        ) as temporary:
            temporary.write(xml_text)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_path = Path(temporary.name)
        os.replace(temporary_path, destination)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
