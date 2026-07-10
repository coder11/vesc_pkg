"""Typed data model and validation for VESC Tool parameter definitions."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from enum import IntEnum
from typing import Final, Union


class ParameterType(IntEnum):
    UNDEFINED = 0
    DOUBLE = 1
    INT = 2
    STRING = 3
    ENUM = 4
    BOOL = 5
    BITFIELD = 6


class TxType(IntEnum):
    UNDEFINED = 0
    UINT8 = 1
    INT8 = 2
    UINT16 = 3
    INT16 = 4
    UINT32 = 5
    INT32 = 6
    DOUBLE16 = 7
    DOUBLE32 = 8
    DOUBLE32_AUTO = 9


@dataclass(frozen=True, slots=True)
class RawDescription:
    """Description already encoded as content understood by Qt rich-text widgets."""

    content: str


@dataclass(frozen=True, slots=True)
class TextDescription:
    """Human-readable text converted to Qt-compatible HTML during rendering."""

    text: str


Description = Union[RawDescription, TextDescription]


@dataclass(frozen=True, slots=True, kw_only=True)
class ParameterBase:
    name: str
    long_name: str
    description: Description = TextDescription("")
    c_define: str = ""
    transmittable: bool = True


@dataclass(frozen=True, slots=True, kw_only=True)
class UndefinedParameter(ParameterBase):
    type: Final[ParameterType] = ParameterType.UNDEFINED


@dataclass(frozen=True, slots=True, kw_only=True)
class DoubleParameter(ParameterBase):
    default: float = 0.0
    minimum: float = 0.0
    maximum: float = 99.0
    step: float = 1.0
    decimals: int = 2
    tx_type: TxType = TxType.DOUBLE32_AUTO
    tx_scale: float = 1.0
    editor_scale: float = 1.0
    edit_as_percentage: bool = False
    show_display: bool = False
    suffix: str = ""
    type: Final[ParameterType] = ParameterType.DOUBLE


@dataclass(frozen=True, slots=True, kw_only=True)
class IntParameter(ParameterBase):
    default: int = 0
    minimum: int = 0
    maximum: int = 99
    step: int = 1
    tx_type: TxType = TxType.UINT16
    editor_scale: float = 1.0
    edit_as_percentage: bool = False
    show_display: bool = False
    suffix: str = ""
    type: Final[ParameterType] = ParameterType.INT


@dataclass(frozen=True, slots=True, kw_only=True)
class StringParameter(ParameterBase):
    default: str = ""
    max_length: int = 0
    type: Final[ParameterType] = ParameterType.STRING


@dataclass(frozen=True, slots=True, kw_only=True)
class EnumParameter(ParameterBase):
    choices: tuple[str, ...]
    default: int = 0
    type: Final[ParameterType] = ParameterType.ENUM


@dataclass(frozen=True, slots=True, kw_only=True)
class BoolParameter(ParameterBase):
    default: bool = False
    type: Final[ParameterType] = ParameterType.BOOL


@dataclass(frozen=True, slots=True, kw_only=True)
class BitfieldParameter(ParameterBase):
    bit_names: tuple[str, ...]
    default: int = 0
    type: Final[ParameterType] = ParameterType.BITFIELD


Parameter = Union[
    UndefinedParameter,
    DoubleParameter,
    IntParameter,
    StringParameter,
    EnumParameter,
    BoolParameter,
    BitfieldParameter,
]


@dataclass(frozen=True, slots=True)
class Separator:
    title: str


GroupItem = Union[Parameter, Separator]


@dataclass(frozen=True, slots=True)
class Subgroup:
    name: str
    items: tuple[GroupItem, ...]


@dataclass(frozen=True, slots=True)
class Group:
    name: str
    subgroups: tuple[Subgroup, ...]


def iter_group_parameters(groups: tuple[Group, ...]) -> tuple[Parameter, ...]:
    """Return parameters in their first-class UI/group declaration order."""
    return tuple(
        item
        for group in groups
        for subgroup in group.subgroups
        for item in subgroup.items
        if not isinstance(item, Separator)
    )


@dataclass(frozen=True, slots=True)
class SettingsXml:
    config_name: str
    settings_name: str
    groups: tuple[Group, ...]

    @property
    def parameters(self) -> tuple[Parameter, ...]:
        """All XML parameters, including VESC Tool's two synthetic parameters."""
        magic_parameters: tuple[Parameter, ...] = (
            StringParameter(
                name="config_name",
                long_name="none",
                default=self.config_name,
                transmittable=False,
            ),
            UndefinedParameter(
                name="hw_name",
                long_name=self.settings_name,
                transmittable=False,
            ),
        )
        return magic_parameters + iter_group_parameters(self.groups)

    @property
    def serialization_order(self) -> tuple[str, ...]:
        """Serialized parameter names in the same order as the group declarations."""
        return tuple(
            parameter.name
            for parameter in iter_group_parameters(self.groups)
            if parameter.transmittable
        )


class ValidationError(ValueError):
    """Raised when settings could produce an invalid VESC configuration."""


_XML_NAME: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")
_C_NAME: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_INT_TX_RANGES: Final[dict[TxType, tuple[int, int]]] = {
    TxType.UINT8: (0, (1 << 8) - 1),
    TxType.INT8: (-(1 << 7), (1 << 7) - 1),
    TxType.UINT16: (0, (1 << 16) - 1),
    TxType.INT16: (-(1 << 15), (1 << 15) - 1),
    TxType.UINT32: (0, (1 << 32) - 1),
    TxType.INT32: (-(1 << 31), (1 << 31) - 1),
}
_DOUBLE_TX_LIMITS: Final[dict[TxType, tuple[int, int]]] = {
    TxType.DOUBLE16: (-(1 << 15), (1 << 15) - 1),
    TxType.DOUBLE32: (-(1 << 31), (1 << 31) - 1),
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def _require_finite(value: float, field: str, parameter: str) -> None:
    _require(math.isfinite(value), f"{parameter}: {field} must be finite")


def _validate_common(parameter: Parameter) -> None:
    name = parameter.name
    _require(bool(_XML_NAME.fullmatch(name)), f"{name!r} is not a valid XML name")
    _require(bool(_C_NAME.fullmatch(name)), f"{name!r} is not a valid C field name")
    _require(bool(parameter.long_name), f"{name}: long_name must not be empty")
    _require(isinstance(parameter.description, (RawDescription, TextDescription)),
             f"{name}: description must be RawDescription or TextDescription")
    description_text = (
        parameter.description.content
        if isinstance(parameter.description, RawDescription)
        else parameter.description.text
    )
    _require("\x00" not in description_text, f"{name}: description contains NUL")
    _require("\x00" not in parameter.c_define, f"{name}: c_define contains NUL")


def _validate_parameter(parameter: Parameter) -> None:
    _validate_common(parameter)
    name = parameter.name

    if isinstance(parameter, UndefinedParameter):
        _require(not parameter.transmittable, f"{name}: undefined parameters cannot be transmittable")
        return

    if isinstance(parameter, DoubleParameter):
        for field, value in (
            ("default", parameter.default),
            ("minimum", parameter.minimum),
            ("maximum", parameter.maximum),
            ("step", parameter.step),
            ("editor_scale", parameter.editor_scale),
            ("tx_scale", parameter.tx_scale),
        ):
            _require_finite(value, field, name)
        _require(parameter.minimum <= parameter.maximum, f"{name}: minimum exceeds maximum")
        _require(parameter.minimum <= parameter.default <= parameter.maximum,
                 f"{name}: default is outside [minimum, maximum]")
        _require(parameter.step > 0.0, f"{name}: step must be positive")
        _require(parameter.decimals >= 0, f"{name}: decimals must not be negative")
        _require(parameter.editor_scale > 0.0, f"{name}: editor_scale must be positive")
        _require(parameter.tx_scale > 0.0, f"{name}: tx_scale must be positive")
        _require(parameter.tx_type in (TxType.DOUBLE16, TxType.DOUBLE32, TxType.DOUBLE32_AUTO),
                 f"{name}: invalid transport {parameter.tx_type.name} for a double")
        if parameter.tx_type in _DOUBLE_TX_LIMITS:
            tx_min, tx_max = _DOUBLE_TX_LIMITS[parameter.tx_type]
            scaled_min = parameter.minimum * parameter.tx_scale
            scaled_max = parameter.maximum * parameter.tx_scale
            _require(tx_min <= scaled_min <= tx_max and tx_min <= scaled_max <= tx_max,
                     f"{name}: scaled range does not fit {parameter.tx_type.name}")
        return

    if isinstance(parameter, IntParameter):
        _require(parameter.minimum <= parameter.maximum, f"{name}: minimum exceeds maximum")
        _require(parameter.minimum <= parameter.default <= parameter.maximum,
                 f"{name}: default is outside [minimum, maximum]")
        _require(parameter.step > 0, f"{name}: step must be positive")
        _require_finite(parameter.editor_scale, "editor_scale", name)
        _require(parameter.editor_scale > 0.0, f"{name}: editor_scale must be positive")
        _require(parameter.tx_type in _INT_TX_RANGES,
                 f"{name}: invalid transport {parameter.tx_type.name} for an integer")
        tx_min, tx_max = _INT_TX_RANGES[parameter.tx_type]
        _require(tx_min <= parameter.minimum and parameter.maximum <= tx_max,
                 f"{name}: range does not fit {parameter.tx_type.name}")
        return

    if isinstance(parameter, StringParameter):
        _require(parameter.max_length >= 0, f"{name}: max_length must not be negative")
        _require(parameter.max_length == 0 or len(parameter.default.encode("utf-8")) <= parameter.max_length,
                 f"{name}: UTF-8 default exceeds max_length")
        return

    if isinstance(parameter, EnumParameter):
        _require(bool(parameter.choices), f"{name}: enum must have at least one choice")
        _require(len(parameter.choices) <= 256, f"{name}: enum does not fit its one-byte encoding")
        _require(0 <= parameter.default < len(parameter.choices), f"{name}: invalid enum default")
        _require(all(parameter.choices), f"{name}: enum choices must not be empty")
        _require(len(set(parameter.choices)) == len(parameter.choices), f"{name}: duplicate enum choices")
        return

    if isinstance(parameter, BoolParameter):
        _require(type(parameter.default) is bool, f"{name}: bool default must be bool")
        return

    if isinstance(parameter, BitfieldParameter):
        _require(len(parameter.bit_names) <= 8, f"{name}: bitfield does not fit its one-byte encoding")
        _require(0 <= parameter.default <= 0xFF, f"{name}: bitfield default does not fit one byte")
        _require(all(parameter.bit_names), f"{name}: bit names must not be empty")
        return

    raise AssertionError(f"unhandled parameter type: {type(parameter)!r}")


def validate_settings(settings: SettingsXml) -> None:
    """Validate invariants used by VESC Tool's XML and C generators."""
    _require(bool(_C_NAME.fullmatch(settings.config_name)),
             "config_name must be a non-empty C identifier")
    _require(bool(settings.settings_name), "settings_name must not be empty")
    _require(bool(settings.groups), "at least one group is required")

    parameters = settings.parameters
    parameter_names = [parameter.name for parameter in parameters]
    _require(len(parameter_names) == len(set(parameter_names)), "parameter names must be unique")
    for parameter in parameters:
        _validate_parameter(parameter)

    serialized = settings.serialization_order
    _require(len(serialized) == len(set(serialized)), "serialization order contains duplicates")

    group_names: set[str] = set()
    for group in settings.groups:
        normalized_group = group.name.casefold()
        _require(bool(group.name), "group names must not be empty")
        _require(normalized_group not in group_names, f"duplicate group name {group.name!r}")
        group_names.add(normalized_group)

        subgroup_names: set[str] = set()
        for subgroup in group.subgroups:
            normalized_subgroup = subgroup.name.casefold()
            _require(bool(subgroup.name), f"{group.name}: subgroup names must not be empty")
            _require(normalized_subgroup not in subgroup_names,
                     f"{group.name}: duplicate subgroup name {subgroup.name!r}")
            subgroup_names.add(normalized_subgroup)
            _require(bool(subgroup.items), f"{group.name}/{subgroup.name}: subgroup must not be empty")

            for item in subgroup.items:
                if isinstance(item, Separator):
                    _require(bool(item.title), f"{group.name}/{subgroup.name}: empty separator title")
                    _require(not item.title.startswith("::sep::"),
                             f"{group.name}/{subgroup.name}: separator contains its XML prefix")
                elif not isinstance(item, ParameterBase):
                    raise ValidationError(
                        f"{group.name}/{subgroup.name}: items must be parameters or separators"
                    )

    for parameter in iter_group_parameters(settings.groups):
        _require(not isinstance(parameter, UndefinedParameter),
                 f"{parameter.name}: undefined parameters cannot be grouped")
        if parameter.transmittable and isinstance(parameter, StringParameter):
            _require(parameter.max_length > 0,
                     f"{parameter.name}: serialized strings require a non-zero max_length")

