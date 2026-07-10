"""Typed data model and aggregated validation for VESC Tool settings."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
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


LocationPart = Union[str, int]
Location = tuple[LocationPart, ...]


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    location: Location
    message: str
    code: str

    def as_dict(self) -> dict[str, object]:
        return {
            "loc": self.location,
            "msg": self.message,
            "type": self.code,
        }


@dataclass(slots=True)
class ValidationContext:
    issues: list[ValidationIssue] = field(default_factory=list)

    def add(self, location: Location, message: str, code: str) -> None:
        self.issues.append(ValidationIssue(location, message, code))

    def require(
        self,
        condition: bool,
        location: Location,
        message: str,
        code: str,
    ) -> None:
        if not condition:
            self.add(location, message, code)


class ValidationError(ValueError):
    """One exception containing every issue found in the settings model."""

    def __init__(self, model_name: str, issues: tuple[ValidationIssue, ...]) -> None:
        self.model_name = model_name
        self.issues = issues
        super().__init__(self._format_message())

    def errors(self) -> list[dict[str, object]]:
        """Return Pydantic-style structured error dictionaries."""
        return [issue.as_dict() for issue in self.issues]

    def _format_message(self) -> str:
        count = len(self.issues)
        heading = (
            f"{count} validation error{'s' if count != 1 else ''} for {self.model_name}"
        )
        details = []
        for issue in self.issues:
            location = ".".join(str(part) for part in issue.location) or "__root__"
            details.append(f"{location}\n  {issue.message} [type={issue.code}]")
        return "\n".join((heading, *details))


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
_DOUBLE_TX_TYPES: Final[tuple[TxType, ...]] = (
    TxType.DOUBLE16,
    TxType.DOUBLE32,
    TxType.DOUBLE32_AUTO,
)


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


@dataclass(frozen=True, slots=True)
class RawDescription:
    """Description already encoded as content understood by Qt rich-text widgets."""

    content: str

    def validate_into(self, context: ValidationContext, location: Location) -> None:
        if not isinstance(self.content, str):
            context.add(location, "content must be a string", "string_type")
        else:
            context.require(
                "\x00" not in self.content,
                location,
                "content contains NUL",
                "nul_character",
            )


@dataclass(frozen=True, slots=True)
class TextDescription:
    """Human-readable text converted to Qt-compatible HTML during rendering."""

    text: str

    def validate_into(self, context: ValidationContext, location: Location) -> None:
        if not isinstance(self.text, str):
            context.add(location, "text must be a string", "string_type")
        else:
            context.require(
                "\x00" not in self.text, location, "text contains NUL", "nul_character"
            )


Description = Union[RawDescription, TextDescription]


@dataclass(frozen=True, slots=True, kw_only=True)
class ParameterBase:
    name: str
    long_name: str
    description: Description = TextDescription("")
    c_define: str = ""
    transmittable: bool = True

    def validate_into(self, context: ValidationContext, location: Location) -> None:
        if not isinstance(self.name, str):
            context.add(location + ("name",), "name must be a string", "string_type")
        else:
            context.require(
                bool(_XML_NAME.fullmatch(self.name)),
                location + ("name",),
                "name is not a valid XML element name",
                "xml_name",
            )
            context.require(
                bool(_C_NAME.fullmatch(self.name)),
                location + ("name",),
                "name is not a valid C field name",
                "c_identifier",
            )

        if not isinstance(self.long_name, str):
            context.add(
                location + ("long_name",), "long_name must be a string", "string_type"
            )
        else:
            context.require(
                bool(self.long_name),
                location + ("long_name",),
                "long_name must not be empty",
                "empty_string",
            )

        if isinstance(self.description, (RawDescription, TextDescription)):
            self.description.validate_into(context, location + ("description",))
        else:
            context.add(
                location + ("description",),
                "description must be RawDescription or TextDescription",
                "description_type",
            )

        if not isinstance(self.c_define, str):
            context.add(
                location + ("c_define",), "c_define must be a string", "string_type"
            )
        else:
            context.require(
                "\x00" not in self.c_define,
                location + ("c_define",),
                "c_define contains NUL",
                "nul_character",
            )
        context.require(
            type(self.transmittable) is bool,
            location + ("transmittable",),
            "transmittable must be a bool",
            "bool_type",
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class UndefinedParameter(ParameterBase):
    type: Final[ParameterType] = ParameterType.UNDEFINED

    def validate_into(self, context: ValidationContext, location: Location) -> None:
        ParameterBase.validate_into(self, context, location)
        context.require(
            self.transmittable is False,
            location + ("transmittable",),
            "undefined parameters cannot be transmittable",
            "undefined_transmittable",
        )


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

    def validate_into(self, context: ValidationContext, location: Location) -> None:
        ParameterBase.validate_into(self, context, location)
        numeric_values = {
            "default": self.default,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "step": self.step,
            "tx_scale": self.tx_scale,
            "editor_scale": self.editor_scale,
        }
        valid_numbers: dict[str, float] = {}
        for field_name, value in numeric_values.items():
            field_location = location + (field_name,)
            if not _is_number(value):
                context.add(field_location, "value must be a number", "number_type")
            elif not math.isfinite(value):
                context.add(field_location, "value must be finite", "finite_number")
            else:
                valid_numbers[field_name] = float(value)

        if "minimum" in valid_numbers and "maximum" in valid_numbers:
            context.require(
                valid_numbers["minimum"] <= valid_numbers["maximum"],
                location + ("minimum",),
                "minimum exceeds maximum",
                "invalid_range",
            )
        if all(name in valid_numbers for name in ("minimum", "default", "maximum")):
            context.require(
                valid_numbers["minimum"]
                <= valid_numbers["default"]
                <= valid_numbers["maximum"],
                location + ("default",),
                "default is outside [minimum, maximum]",
                "default_out_of_range",
            )
        if "step" in valid_numbers:
            context.require(
                valid_numbers["step"] > 0.0,
                location + ("step",),
                "step must be positive",
                "positive_number",
            )
        if "editor_scale" in valid_numbers:
            context.require(
                valid_numbers["editor_scale"] > 0.0,
                location + ("editor_scale",),
                "editor_scale must be positive",
                "positive_number",
            )
        if "tx_scale" in valid_numbers:
            context.require(
                valid_numbers["tx_scale"] > 0.0,
                location + ("tx_scale",),
                "tx_scale must be positive",
                "positive_number",
            )

        if not _is_int(self.decimals):
            context.add(
                location + ("decimals",), "decimals must be an integer", "int_type"
            )
        else:
            context.require(
                self.decimals >= 0,
                location + ("decimals",),
                "decimals must not be negative",
                "non_negative_integer",
            )

        tx_valid = isinstance(self.tx_type, TxType) and self.tx_type in _DOUBLE_TX_TYPES
        context.require(
            tx_valid,
            location + ("tx_type",),
            "transport must be DOUBLE16, DOUBLE32, or DOUBLE32_AUTO",
            "double_transport",
        )
        if (
            tx_valid
            and self.tx_type in _DOUBLE_TX_LIMITS
            and all(
                name in valid_numbers for name in ("minimum", "maximum", "tx_scale")
            )
        ):
            tx_min, tx_max = _DOUBLE_TX_LIMITS[self.tx_type]
            scaled_min = valid_numbers["minimum"] * valid_numbers["tx_scale"]
            scaled_max = valid_numbers["maximum"] * valid_numbers["tx_scale"]
            context.require(
                tx_min <= scaled_min <= tx_max and tx_min <= scaled_max <= tx_max,
                location + ("tx_scale",),
                f"scaled range does not fit {self.tx_type.name}",
                "transport_range",
            )


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

    def validate_into(self, context: ValidationContext, location: Location) -> None:
        ParameterBase.validate_into(self, context, location)
        integer_values = {
            "default": self.default,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "step": self.step,
        }
        valid_integers: dict[str, int] = {}
        for field_name, value in integer_values.items():
            if _is_int(value):
                valid_integers[field_name] = value
            else:
                context.add(
                    location + (field_name,), "value must be an integer", "int_type"
                )

        if "minimum" in valid_integers and "maximum" in valid_integers:
            context.require(
                valid_integers["minimum"] <= valid_integers["maximum"],
                location + ("minimum",),
                "minimum exceeds maximum",
                "invalid_range",
            )
        if all(name in valid_integers for name in ("minimum", "default", "maximum")):
            context.require(
                valid_integers["minimum"]
                <= valid_integers["default"]
                <= valid_integers["maximum"],
                location + ("default",),
                "default is outside [minimum, maximum]",
                "default_out_of_range",
            )
        if "step" in valid_integers:
            context.require(
                valid_integers["step"] > 0,
                location + ("step",),
                "step must be positive",
                "positive_integer",
            )

        if not _is_number(self.editor_scale):
            context.add(
                location + ("editor_scale",), "value must be a number", "number_type"
            )
        elif not math.isfinite(self.editor_scale):
            context.add(
                location + ("editor_scale",), "value must be finite", "finite_number"
            )
        else:
            context.require(
                self.editor_scale > 0.0,
                location + ("editor_scale",),
                "editor_scale must be positive",
                "positive_number",
            )

        tx_valid = isinstance(self.tx_type, TxType) and self.tx_type in _INT_TX_RANGES
        context.require(
            tx_valid,
            location + ("tx_type",),
            "transport must be a supported integer transport",
            "integer_transport",
        )
        if tx_valid and "minimum" in valid_integers and "maximum" in valid_integers:
            tx_min, tx_max = _INT_TX_RANGES[self.tx_type]
            context.require(
                tx_min <= valid_integers["minimum"]
                and valid_integers["maximum"] <= tx_max,
                location + ("maximum",),
                f"range does not fit {self.tx_type.name}",
                "transport_range",
            )


@dataclass(frozen=True, slots=True, kw_only=True)
class StringParameter(ParameterBase):
    default: str = ""
    max_length: int = 0
    type: Final[ParameterType] = ParameterType.STRING

    def validate_into(self, context: ValidationContext, location: Location) -> None:
        ParameterBase.validate_into(self, context, location)
        default_valid = isinstance(self.default, str)
        if not default_valid:
            context.add(
                location + ("default",), "default must be a string", "string_type"
            )
        max_length_valid = _is_int(self.max_length)
        if not max_length_valid:
            context.add(
                location + ("max_length",), "max_length must be an integer", "int_type"
            )
        else:
            context.require(
                self.max_length >= 0,
                location + ("max_length",),
                "max_length must not be negative",
                "non_negative_integer",
            )
        if default_valid and max_length_valid and self.max_length > 0:
            context.require(
                len(self.default.encode("utf-8")) <= self.max_length,
                location + ("default",),
                "UTF-8 default exceeds max_length",
                "string_too_long",
            )
        if self.transmittable is True and max_length_valid:
            context.require(
                self.max_length > 0,
                location + ("max_length",),
                "serialized strings require a non-zero max_length",
                "serialized_string_length",
            )


@dataclass(frozen=True, slots=True, kw_only=True)
class EnumParameter(ParameterBase):
    choices: tuple[str, ...]
    default: int = 0
    type: Final[ParameterType] = ParameterType.ENUM

    def validate_into(self, context: ValidationContext, location: Location) -> None:
        ParameterBase.validate_into(self, context, location)
        choices_valid = isinstance(self.choices, tuple)
        if not choices_valid:
            context.add(
                location + ("choices",), "choices must be a tuple", "tuple_type"
            )
        else:
            context.require(
                bool(self.choices),
                location + ("choices",),
                "enum must have at least one choice",
                "empty_enum",
            )
            context.require(
                len(self.choices) <= 256,
                location + ("choices",),
                "enum does not fit its one-byte encoding",
                "enum_too_large",
            )
            for index, choice in enumerate(self.choices):
                if not isinstance(choice, str):
                    context.add(
                        location + ("choices", index),
                        "choice must be a string",
                        "string_type",
                    )
                else:
                    context.require(
                        bool(choice),
                        location + ("choices", index),
                        "choice must not be empty",
                        "empty_string",
                    )
            if all(isinstance(choice, str) for choice in self.choices):
                context.require(
                    len(set(self.choices)) == len(self.choices),
                    location + ("choices",),
                    "enum choices must be unique",
                    "duplicate_enum_choice",
                )

        if not _is_int(self.default):
            context.add(
                location + ("default",), "default must be an integer", "int_type"
            )
        elif choices_valid and self.choices:
            context.require(
                0 <= self.default < len(self.choices),
                location + ("default",),
                "default is not a valid choice index",
                "enum_default",
            )


@dataclass(frozen=True, slots=True, kw_only=True)
class BoolParameter(ParameterBase):
    default: bool = False
    type: Final[ParameterType] = ParameterType.BOOL

    def validate_into(self, context: ValidationContext, location: Location) -> None:
        ParameterBase.validate_into(self, context, location)
        context.require(
            type(self.default) is bool,
            location + ("default",),
            "default must be a bool",
            "bool_type",
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class BitfieldParameter(ParameterBase):
    bit_names: tuple[str, ...]
    default: int = 0
    type: Final[ParameterType] = ParameterType.BITFIELD

    def validate_into(self, context: ValidationContext, location: Location) -> None:
        ParameterBase.validate_into(self, context, location)
        bit_names_valid = isinstance(self.bit_names, tuple)
        if not bit_names_valid:
            context.add(
                location + ("bit_names",), "bit_names must be a tuple", "tuple_type"
            )
        else:
            context.require(
                len(self.bit_names) <= 8,
                location + ("bit_names",),
                "bitfield does not fit its one-byte encoding",
                "bitfield_too_large",
            )
            for index, bit_name in enumerate(self.bit_names):
                if not isinstance(bit_name, str):
                    context.add(
                        location + ("bit_names", index),
                        "bit name must be a string",
                        "string_type",
                    )
                else:
                    context.require(
                        bool(bit_name),
                        location + ("bit_names", index),
                        "bit name must not be empty",
                        "empty_string",
                    )
        if not _is_int(self.default):
            context.add(
                location + ("default",), "default must be an integer", "int_type"
            )
        else:
            context.require(
                0 <= self.default <= 0xFF,
                location + ("default",),
                "default does not fit one byte",
                "bitfield_default",
            )


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

    def validate_into(self, context: ValidationContext, location: Location) -> None:
        if not isinstance(self.title, str):
            context.add(location + ("title",), "title must be a string", "string_type")
        else:
            context.require(
                bool(self.title),
                location + ("title",),
                "separator title must not be empty",
                "empty_string",
            )
            context.require(
                not self.title.startswith("::sep::"),
                location + ("title",),
                "separator title must not contain the XML prefix",
                "separator_prefix",
            )


GroupItem = Union[Parameter, Separator]


@dataclass(frozen=True, slots=True)
class Subgroup:
    name: str
    items: tuple[GroupItem, ...]

    def validate_into(self, context: ValidationContext, location: Location) -> None:
        if not isinstance(self.name, str):
            context.add(location + ("name",), "name must be a string", "string_type")
        else:
            context.require(
                bool(self.name),
                location + ("name",),
                "subgroup name must not be empty",
                "empty_string",
            )
        if not isinstance(self.items, tuple):
            context.add(location + ("items",), "items must be a tuple", "tuple_type")
            return
        context.require(
            bool(self.items),
            location + ("items",),
            "subgroup must not be empty",
            "empty_subgroup",
        )
        for index, item in enumerate(self.items):
            item_location = location + ("items", index)
            if isinstance(item, Separator):
                item.validate_into(context, item_location)
            elif isinstance(item, UndefinedParameter):
                context.add(
                    item_location,
                    "undefined parameters cannot be grouped",
                    "undefined_grouped",
                )
            elif not isinstance(item, ParameterBase):
                context.add(
                    item_location,
                    "item must be a parameter or separator",
                    "group_item_type",
                )


@dataclass(frozen=True, slots=True)
class Group:
    name: str
    subgroups: tuple[Subgroup, ...]

    def validate_into(self, context: ValidationContext, location: Location) -> None:
        if not isinstance(self.name, str):
            context.add(location + ("name",), "name must be a string", "string_type")
        else:
            context.require(
                bool(self.name),
                location + ("name",),
                "group name must not be empty",
                "empty_string",
            )
        if not isinstance(self.subgroups, tuple):
            context.add(
                location + ("subgroups",), "subgroups must be a tuple", "tuple_type"
            )
            return

        seen_subgroups: dict[str, int] = {}
        for index, subgroup in enumerate(self.subgroups):
            subgroup_location = location + ("subgroups", index)
            if not isinstance(subgroup, Subgroup):
                context.add(
                    subgroup_location, "value must be a Subgroup", "subgroup_type"
                )
                continue
            subgroup.validate_into(context, subgroup_location)
            if isinstance(subgroup.name, str):
                normalized = subgroup.name.casefold()
                if normalized in seen_subgroups:
                    context.add(
                        subgroup_location + ("name",),
                        f"duplicate subgroup name; first declared at index {seen_subgroups[normalized]}",
                        "duplicate_subgroup",
                    )
                else:
                    seen_subgroups[normalized] = index


def iter_group_parameters(groups: tuple[Group, ...]) -> tuple[Parameter, ...]:
    """Return valid parameter objects in their UI/group declaration order."""
    parameters: list[Parameter] = []
    if not isinstance(groups, tuple):
        return ()
    for group in groups:
        if not isinstance(group, Group) or not isinstance(group.subgroups, tuple):
            continue
        for subgroup in group.subgroups:
            if not isinstance(subgroup, Subgroup) or not isinstance(
                subgroup.items, tuple
            ):
                continue
            parameters.extend(
                item for item in subgroup.items if isinstance(item, ParameterBase)
            )
    return tuple(parameters)


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
            if parameter.transmittable is True and isinstance(parameter.name, str)
        )

    def validate_into(
        self, context: ValidationContext, location: Location = ()
    ) -> None:
        if not isinstance(self.config_name, str):
            context.add(
                location + ("config_name",),
                "config_name must be a string",
                "string_type",
            )
        else:
            context.require(
                bool(_C_NAME.fullmatch(self.config_name)),
                location + ("config_name",),
                "config_name must be a non-empty C identifier",
                "c_identifier",
            )
        if not isinstance(self.settings_name, str):
            context.add(
                location + ("settings_name",),
                "settings_name must be a string",
                "string_type",
            )
        else:
            context.require(
                bool(self.settings_name),
                location + ("settings_name",),
                "settings_name must not be empty",
                "empty_string",
            )

        if not isinstance(self.groups, tuple):
            context.add(location + ("groups",), "groups must be a tuple", "tuple_type")
        else:
            context.require(
                bool(self.groups),
                location + ("groups",),
                "at least one group is required",
                "empty_groups",
            )
            seen_groups: dict[str, int] = {}
            for index, group in enumerate(self.groups):
                group_location = location + ("groups", index)
                if not isinstance(group, Group):
                    context.add(group_location, "value must be a Group", "group_type")
                    continue
                group.validate_into(context, group_location)
                if isinstance(group.name, str):
                    normalized = group.name.casefold()
                    if normalized in seen_groups:
                        context.add(
                            group_location + ("name",),
                            f"duplicate group name; first declared at index {seen_groups[normalized]}",
                            "duplicate_group",
                        )
                    else:
                        seen_groups[normalized] = index

        parameters = self.parameters
        seen_parameters: dict[str, int] = {}
        for index, parameter in enumerate(parameters):
            parameter_name = (
                parameter.name
                if isinstance(parameter.name, str) and parameter.name
                else index
            )
            parameter_location = location + ("parameters", parameter_name)
            parameter.validate_into(context, parameter_location)
            if isinstance(parameter.name, str):
                if parameter.name in seen_parameters:
                    context.add(
                        parameter_location + ("name",),
                        f"duplicate parameter name; first declared at index {seen_parameters[parameter.name]}",
                        "duplicate_parameter",
                    )
                else:
                    seen_parameters[parameter.name] = index

        seen_serialized: dict[str, int] = {}
        for index, name in enumerate(self.serialization_order):
            if name in seen_serialized:
                context.add(
                    location + ("serialization_order", index),
                    f"duplicate serialized parameter; first declared at index {seen_serialized[name]}",
                    "duplicate_serialized_parameter",
                )
            else:
                seen_serialized[name] = index

    def validation_issues(self) -> tuple[ValidationIssue, ...]:
        context = ValidationContext()
        self.validate_into(context)
        return tuple(context.issues)

    def validate(self) -> None:
        issues = self.validation_issues()
        if issues:
            raise ValidationError(type(self).__name__, issues)


def collect_validation_issues(settings: SettingsXml) -> tuple[ValidationIssue, ...]:
    """Return all validation issues without raising an exception."""
    return settings.validation_issues()


def validate_settings(settings: SettingsXml) -> None:
    """Raise one ValidationError containing every issue in settings."""
    settings.validate()
