from __future__ import annotations

"""
Small example showing the intended style:
- readable plain-text descriptions
- sensible defaults (via helper constructors/constants)
- ability to reuse constants / functions
- fully typed config in Python
"""

from settings_gen.model import (
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


def D(text: str) -> Description:
    return Description(text=text, format="plain")


VTX_DOUBLE_MILLI = 1000


CONFIG = ConfigParams(
    params=[
        StringParam(
            id="config_name",
            long_name="none",
            transmittable=False,
            description=D(""),
            c_define="",
            value="balance_config",
            max_len=0,
        ),
        InfoParam(
            id="hw_name",
            long_name="Balance ex Settings",
            transmittable=False,
            description=D("This is the VESC Logging and Communication Module."),
        ),
        BoolParam(
            id="balance_enabled",
            long_name="Balancing enabled",
            transmittable=True,
            description=D(
                "Enable/disable balancing.\n"
                "Turn it off to experiment with base motor settings without the balance interfering."
            ),
            c_define="APPCONF_BALANCE_ENABLED",
            value=False,
        ),
        DoubleParam(
            id="error_linear_limit",
            long_name="Error response linear limit",
            transmittable=True,
            description=D(
                "PID error is computed from pitch using a linear segment up to a limit, then log.\n"
                "This parameter is the linear limit (d) in degrees."
            ),
            c_define="APPCONF_ERROR_LINEAR_LIMIT",
            editor_decimals=1,
            editor_scale=1.0,
            edit_as_percentage=False,
            min_double=0.0,
            max_double=90.0,
            step_double=0.1,
            value=90.0,
            vtx_double_scale=1,
            suffix="",
            vtx=9,
        ),
        EnumParam(
            id="pid_mode",
            long_name="PID Mode",
            transmittable=True,
            description=D("PID loop mode, Angle or Cascading Angle Rate."),
            c_define="APPCONF_BALANCE_PID_MODE",
            value=1,
            enum_names=[
                "BALANCE_PID_MODE_ANGLE",
                "BALANCE_PID_MODE_ANGLE_RATE_CASCADE",
                "BALANCE_PID_MODE_ANGLE_RATE_CASCADE_ALT",
            ],
        ),
        IntParam(
            id="hertz",
            long_name="Loop Hertz",
            transmittable=True,
            description=D("Loop frequency for the balancing control loop."),
            c_define="APPCONF_BALANCE_HERTZ",
            editor_scale=1,
            edit_as_percentage=False,
            min_int=50,
            max_int=4000,
            step_int=100,
            value=1000,
            suffix=" Hz",
            vtx=3,
        ),
        DoubleParam(
            id="torquetilt_filter",
            long_name="Current Filter",
            transmittable=True,
            description=D(
                "Biquad low-pass filter for the current used to compute torque-tilt.\n"
                "Higher = smoother, lower = more responsive."
            ),
            c_define="APPCONF_BALANCE_TORQUETILT_FILTER",
            editor_decimals=1,
            editor_scale=1.0,
            edit_as_percentage=False,
            min_double=0.0,
            max_double=500.0,
            step_double=0.5,
            value=2.0,
            vtx_double_scale=VTX_DOUBLE_MILLI,
            suffix=" Hz",
            vtx=9,
        ),
    ],
    ser_order=[
        "balance_enabled",
        "error_linear_limit",
        "pid_mode",
        "hertz",
        "torquetilt_filter",
    ],
    grouping=[
        Group(
            name="General",
            subgroups=[
                SubGroup(
                    name="Tune",
                    items=[
                        Sep("General"),
                        Ref("balance_enabled"),
                        Ref("error_linear_limit"),
                        Sep("PID"),
                        Ref("pid_mode"),
                        Sep("Main Loop"),
                        Ref("hertz"),
                        Sep("Filters"),
                        Ref("torquetilt_filter"),
                    ],
                )
            ],
        )
    ],
)


