from __future__ import annotations

from typing import Any, Literal, Sequence, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class _FrozenModel(BaseModel):
    # Strict, immutable models: good for "config as code".
    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)


class Description(_FrozenModel):
    """
    Human-friendly parameter description.

    - format="plain": plain text; generator will wrap into Qt-richtext HTML.
    - format="qrich": already a Qt-richtext HTML string; will be embedded as-is.
    """

    text: str
    format: Literal["plain", "qrich"] = "plain"


class ParamBase(_FrozenModel):
    """
    Base info shared by all parameter types.

    `id` is the XML element name (e.g. "kp" or "haptic.strength_curvature").
    """

    id: str
    long_name: str
    transmittable: bool
    description: Description
    c_define: str = ""

    def type_code(self) -> int:  # overridden by subclasses
        raise NotImplementedError

    @field_validator("id")
    @classmethod
    def _non_empty_id(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("id must not be empty")
        return v


class InfoParam(ParamBase):
    """A non-transmittable informational header/label (type 0)."""

    def type_code(self) -> int:
        return 0


class StringParam(ParamBase):
    value: str
    max_len: int = 0

    def type_code(self) -> int:
        return 3

    @field_validator("max_len")
    @classmethod
    def _max_len_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("max_len must be >= 0")
        return v


class BoolParam(ParamBase):
    value: bool

    def type_code(self) -> int:
        return 5


class IntParam(ParamBase):
    value: int
    min_int: int
    max_int: int
    step_int: int
    editor_scale: int = 1
    edit_as_percentage: bool = False
    show_display: bool = False
    suffix: str = ""
    vtx: int = 3

    def type_code(self) -> int:
        return 2

    @field_validator("value", "min_int", "max_int", "step_int", "editor_scale", "vtx")
    @classmethod
    def _no_bools(cls, v: int) -> int:
        # bool is a subclass of int; reject it explicitly.
        if isinstance(v, bool):
            raise TypeError("bool is not allowed where int is required")
        return v

    @model_validator(mode="after")
    def _check_int_ranges(self) -> "IntParam":
        if self.min_int > self.max_int:
            raise ValueError("min_int must be <= max_int")
        if not (self.min_int <= self.value <= self.max_int):
            raise ValueError(f"value {self.value} out of [{self.min_int}, {self.max_int}]")
        if self.step_int <= 0:
            raise ValueError("step_int must be > 0")
        return self


class DoubleParam(ParamBase):
    # Accept int for float-y values (matches Python typing behavior), but reject strings.
    value: float = Field(...)
    min_double: float = Field(...)
    max_double: float = Field(...)
    step_double: float = Field(...)
    editor_decimals: int = 1
    editor_scale: float = 1.0
    edit_as_percentage: bool = False
    show_display: bool = False
    vtx_double_scale: int = 1000
    suffix: str = ""
    vtx: int = 9

    def type_code(self) -> int:
        return 1

    @field_validator(
        "value",
        "min_double",
        "max_double",
        "step_double",
        "editor_scale",
        mode="before",
    )
    @classmethod
    def _allow_ints_for_floats(cls, v: Any) -> Any:
        if isinstance(v, bool):
            raise TypeError("bool is not allowed where float is required")
        if isinstance(v, int):
            return float(v)
        return v

    @field_validator("editor_decimals", "vtx_double_scale", "vtx", mode="before")
    @classmethod
    def _no_bool_for_int_fields(cls, v: Any) -> Any:
        if isinstance(v, bool):
            raise TypeError("bool is not allowed where int is required")
        return v

    @model_validator(mode="after")
    def _check_double_ranges(self) -> "DoubleParam":
        if self.min_double > self.max_double:
            raise ValueError("min_double must be <= max_double")
        if not (self.min_double <= self.value <= self.max_double):
            raise ValueError(f"value {self.value} out of [{self.min_double}, {self.max_double}]")
        if self.step_double <= 0:
            raise ValueError("step_double must be > 0")
        if self.editor_decimals < 0:
            raise ValueError("editor_decimals must be >= 0")
        return self


class EnumParam(ParamBase):
    """
    Enum parameter: VESC stores it as an integer with repeated <enumNames> tags.
    """

    value: int
    enum_names: Sequence[str]

    def type_code(self) -> int:
        return 4

    @field_validator("value", mode="before")
    @classmethod
    def _no_bool_for_value(cls, v: Any) -> Any:
        if isinstance(v, bool):
            raise TypeError("bool is not allowed where int is required")
        return v

    @model_validator(mode="after")
    def _check_enum(self) -> "EnumParam":
        if not self.enum_names:
            raise ValueError("enum_names must not be empty")
        if self.value < 0 or self.value >= len(self.enum_names):
            raise ValueError(f"value {self.value} outside enum_names range")
        return self


Param = Union[InfoParam, StringParam, BoolParam, IntParam, DoubleParam, EnumParam]


class Sep(_FrozenModel):
    title: str

    def __init__(self, title: str) -> None:
        super().__init__(title=title)


class Ref(_FrozenModel):
    param_id: str

    def __init__(self, param_id: str) -> None:
        super().__init__(param_id=param_id)


GroupItem = Union[Sep, Ref]


class SubGroup(_FrozenModel):
    name: str
    items: Sequence[GroupItem]


class Group(_FrozenModel):
    name: str
    subgroups: Sequence[SubGroup]


class ConfigParams(_FrozenModel):
    params: Sequence[Param]
    ser_order: Sequence[str]
    grouping: Sequence[Group]

    @model_validator(mode="after")
    def _check_cross_refs(self) -> "ConfigParams":
        ids = [p.id for p in self.params]
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        if dupes:
            raise ValueError(f"Duplicate param ids: {dupes}")

        id_set = set(ids)

        missing_ser = [p for p in self.ser_order if p not in id_set]
        if missing_ser:
            raise ValueError(f"ser_order references unknown params: {missing_ser}")

        missing_group: set[str] = set()
        for g in self.grouping:
            for sg in g.subgroups:
                for item in sg.items:
                    if isinstance(item, Ref) and item.param_id not in id_set:
                        missing_group.add(item.param_id)
        if missing_group:
            raise ValueError(f"grouping references unknown params: {sorted(missing_group)}")

        return self


