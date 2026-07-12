"""C ``datatypes.h`` rendering and safe file replacement."""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field
from datetime import date
from functools import singledispatch
from pathlib import Path

from settings_schema import (
    BitfieldParameter,
    BoolParameter,
    DoubleParameter,
    EnumParameter,
    IntParameter,
    Parameter,
    SettingsXml,
    StringParameter,
    TxType,
    iter_group_parameters,
    validate_settings,
)


_INTEGER_C_TYPES = {
    TxType.UINT8: "uint8_t",
    TxType.INT8: "int8_t",
    TxType.UINT16: "uint16_t",
    TxType.INT16: "int16_t",
    TxType.UINT32: "uint32_t",
    TxType.INT32: "int32_t",
}

_DEFAULT_LICENSE_TEXT = """\tThis file is part of the VESC firmware.

\tThe VESC firmware is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    The VESC firmware is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


@dataclass(frozen=True, slots=True, kw_only=True)
class CHeaderLicense:
    """Copyright attribution and license text for a generated C header."""

    author: str = "Benjamin Vedder"
    author_email: str = "benjamin@vedder.se"
    year: int = field(default_factory=lambda: date.today().year)
    text: str = _DEFAULT_LICENSE_TEXT


def _render_license(license: CHeaderLicense) -> str:
    values = {
        "author": license.author,
        "author_email": license.author_email,
        "text": license.text,
    }
    for name, value in values.items():
        if not isinstance(value, str) or not value:
            raise ValueError(f"license {name} must be a non-empty string")
        if "\x00" in value or "*/" in value:
            raise ValueError(f"license {name} contains invalid C comment text")
    if not isinstance(license.year, int) or isinstance(license.year, bool):
        raise ValueError("license year must be an integer")
    if license.year < 1:
        raise ValueError("license year must be positive")

    return (
        "/*\n"
        f"\tCopyright {license.year} {license.author}\t{license.author_email}\n\n"
        f"{license.text.rstrip()}\n"
        " */\n"
    )


@singledispatch
def _field_declaration(parameter: object) -> str:
    raise AssertionError(f"unhandled parameter type: {type(parameter)!r}")


@_field_declaration.register
def _(parameter: DoubleParameter) -> str:
    return f"float {parameter.name};"


@_field_declaration.register
def _(parameter: IntParameter) -> str:
    return f"{_INTEGER_C_TYPES[parameter.tx_type]} {parameter.name};"


@_field_declaration.register
def _(parameter: StringParameter) -> str:
    return f"char {parameter.name}[{parameter.max_length + 1}];"


@_field_declaration.register
def _(parameter: EnumParameter) -> str:
    return f"{parameter.c_type_name} {parameter.name};"


@_field_declaration.register
def _(parameter: BoolParameter) -> str:
    return f"bool {parameter.name};"


@_field_declaration.register
def _(parameter: BitfieldParameter) -> str:
    return f"uint8_t {parameter.name};"


def _serialized_parameters(settings: SettingsXml) -> tuple[Parameter, ...]:
    return tuple(
        parameter
        for parameter in iter_group_parameters(settings.groups)
        if parameter.transmittable
    )


def render_datatypes(
    settings: SettingsXml, *, license: CHeaderLicense | None = None
) -> str:
    """Validate and render the C enum and configuration struct declarations."""
    validate_settings(settings)
    header_license = CHeaderLicense() if license is None else license
    if not isinstance(header_license, CHeaderLicense):
        raise ValueError("license must be a CHeaderLicense")
    parameters = _serialized_parameters(settings)
    enum_parameters = tuple(
        parameter for parameter in parameters if isinstance(parameter, EnumParameter)
    )

    sections = [
        _render_license(header_license),
        "#ifndef DATATYPES_H_\n#define DATATYPES_H_\n",
        "#include <stdint.h>\n#include <stdbool.h>\n",
    ]
    for parameter in enum_parameters:
        choices = ",\n".join(
            f"\t{choice} = {index}" for index, choice in enumerate(parameter.choices)
        )
        sections.append(
            f"typedef enum {{\n{choices}\n}} {parameter.c_type_name};\n"
        )

    fields = "\n".join(f"\t{_field_declaration(parameter)}" for parameter in parameters)
    sections.append(
        f"typedef struct {{\n{fields}\n}} {settings.config_structure_name};\n"
    )
    sections.append("// DATATYPES_H_\n#endif\n")
    return "\n".join(sections)


def write_datatypes(
    settings: SettingsXml,
    destination: Path,
    *,
    license: CHeaderLicense | None = None,
) -> None:
    """Render and atomically replace a generated ``datatypes.h`` file."""
    header_text = render_datatypes(settings, license=license)
    destination.parent.mkdir(parents=True, exist_ok=True)

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="UTF-8",
            newline="\n",
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=destination.parent,
            delete=False,
        ) as temporary:
            temporary.write(header_text)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_path = Path(temporary.name)
        os.replace(temporary_path, destination)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
