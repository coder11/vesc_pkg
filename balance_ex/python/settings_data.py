"""Balance application settings expressed as typed Python objects."""

from __future__ import annotations

from typing import Final

from settings_schema import (
    BoolParameter,
    DoubleParameter,
    EnumParameter,
    Group,
    IntParameter,
    RawDescription,
    Separator,
    SettingsXml,
    Subgroup,
    TextDescription,
    TxType,
)


general_balance_enabled: Final[BoolParameter] = BoolParameter(
    name="balance_enabled",
    long_name="Balancing enabled",
    description=TextDescription(
        (
            "Enable/disable balancing. Turn it off to experiment with base motor settings without the "
            "balance interfering."
        )
    ),
)


general_error_linear_limit: Final[DoubleParameter] = DoubleParameter(
    name="error_linear_limit",
    long_name="Error response linear limit",
    description=RawDescription(
        (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" '
            '"http://www.w3.org/TR/REC-html40/strict.dtd">\n'
            '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
            "p, li { white-space: pre-wrap; }\n"
            "</style></head><body style=\" font-family:'Roboto'; ; font-weight:400; "
            'font-style:normal;">\n'
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; '
            '-qt-block-indent:0; text-indent:0px;">PID error is calculated using this function (<a '
            'href="https://www.desmos.com/calculator/d0ergbkhie"><span style=" text-decoration: '
            'underline; color:#9696ff;">desmos</span></a>):</p>\n'
            '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; '
            'margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>\n'
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; '
            '-qt-block-indent:0; text-indent:0px;">y = x { 0&lt;x&lt;d }</p>\n'
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; '
            '-qt-block-indent:0; text-indent:0px;">y = k ln( (x-d)/k +1 ) + d, { x &gt;= d }</p>\n'
            '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; '
            'margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>\n'
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; '
            '-qt-block-indent:0; text-indent:0px;">Where <span style=" font-weight:600;">y</span> is the '
            '<span style=" font-weight:600;">error</span>; <span style=" font-weight:600;">x</span> is '
            "the pitch in degrees.</p>\n"
            '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; '
            'margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>\n'
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; '
            '-qt-block-indent:0; text-indent:0px;">It starts linear up to a limit and then descreses '
            "logarithmically with a specific slope.</p>\n"
            '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; '
            'margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>\n'
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; '
            '-qt-block-indent:0; text-indent:0px;">This parameter controls <span style=" '
            'font-weight:600;">d</span></p></body></html>'
        )
    ),
    default=90.0,
    maximum=90.0,
    step=0.1,
    decimals=1,
)


general_error_ln_slope: Final[DoubleParameter] = DoubleParameter(
    name="error_ln_slope",
    long_name="Error logarithm slope",
    description=RawDescription(
        (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" '
            '"http://www.w3.org/TR/REC-html40/strict.dtd">\n'
            '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
            "p, li { white-space: pre-wrap; }\n"
            "</style></head><body style=\" font-family:'Roboto'; ; font-weight:400; "
            'font-style:normal;">\n'
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; '
            '-qt-block-indent:0; text-indent:0px;">PID error is calculated using this function (<a '
            'href="https://www.desmos.com/calculator/d0ergbkhie"><span style=" text-decoration: '
            'underline; color:#9696ff;">desmos</span></a>):</p>\n'
            '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; '
            'margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>\n'
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; '
            '-qt-block-indent:0; text-indent:0px;">y = x { 0&lt;x&lt;d }</p>\n'
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; '
            '-qt-block-indent:0; text-indent:0px;">y = k ln( (x-d)/k +1 ) + d, { x &gt;= d }</p>\n'
            '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; '
            'margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>\n'
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; '
            '-qt-block-indent:0; text-indent:0px;">Where <span style=" font-weight:600;">y</span> is the '
            '<span style=" font-weight:600;">error</span>; <span style=" font-weight:600;">x</span> is '
            "the pitch in degrees.</p>\n"
            '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; '
            'margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>\n'
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; '
            '-qt-block-indent:0; text-indent:0px;">It starts linear up to a limit and then descreses '
            "logarithmically with a specific slope.</p>\n"
            '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; '
            'margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>\n'
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; '
            '-qt-block-indent:0; text-indent:0px;">This parameter controls <span style=" '
            'font-weight:600;">k</span></p></body></html>'
        )
    ),
    default=0.1,
    minimum=0.1,
    maximum=50.0,
    step=0.1,
    decimals=1,
)


pid_mode: Final[EnumParameter] = EnumParameter(
    name="pid_mode",
    long_name="PID Mode",
    description=TextDescription("PID loop mode, Angle or Cascadeing Angle Rate."),
    choices=("BALANCE_PID_MODE_ANGLE", "BALANCE_PID_MODE_ANGLE_RATE_CASCADE"),
)


pid_kp: Final[DoubleParameter] = DoubleParameter(
    name="kp",
    long_name="Angle P",
    description=TextDescription("P value for the PID balance loop."),
    maximum=100000.0,
    step=0.1,
    decimals=4,
    tx_scale=1000.0,
)


pid_kexp: Final[DoubleParameter] = DoubleParameter(
    name="kexp",
    long_name="Angle exponential",
    description=TextDescription(
        (
            "Exponential component defined as e^(kx) - 1\n"
            "\n"
            'This parameter controls the "steepness" of the exponent, k'
        )
    ),
    maximum=20.0,
    step=0.1,
)


pid_ki: Final[DoubleParameter] = DoubleParameter(
    name="ki",
    long_name="Angle I",
    description=TextDescription("I value for the PID balance loop."),
    maximum=100000.0,
    step=0.1,
    decimals=4,
    tx_scale=1000.0,
)


pid_kd: Final[DoubleParameter] = DoubleParameter(
    name="kd",
    long_name="Angle D",
    description=TextDescription("D value for the PID balance loop."),
    maximum=100000.0,
    step=0.1,
    decimals=4,
    tx_scale=1000.0,
)


pid_kp2: Final[DoubleParameter] = DoubleParameter(
    name="kp2",
    long_name="Rate P",
    description=TextDescription("P value for the PID balance loop."),
    maximum=100000.0,
    step=0.1,
    decimals=4,
    tx_scale=1000.0,
)


pid_ki2: Final[DoubleParameter] = DoubleParameter(
    name="ki2",
    long_name="Rate I",
    description=TextDescription("I value for the PID balance loop."),
    maximum=100000.0,
    step=0.1,
    decimals=4,
    tx_scale=1000.0,
)


pid_kd2: Final[DoubleParameter] = DoubleParameter(
    name="kd2",
    long_name="Rate D",
    description=TextDescription("D value for the PID balance loop."),
    maximum=100000.0,
    step=0.1,
    decimals=4,
    tx_scale=1000.0,
)


main_loop_hertz: Final[IntParameter] = IntParameter(
    name="hertz",
    long_name="Loop Hertz",
    description=TextDescription("Loop Hertz."),
    default=1000,
    minimum=50,
    maximum=4000,
    step=100,
    suffix=" Hz",
)


main_loop_time_filter: Final[IntParameter] = IntParameter(
    name="loop_time_filter",
    long_name="Loop Time Correction Filter",
    description=TextDescription("Filter overshoot and correct for it."),
    maximum=1000,
    step=10,
    suffix=" Hz",
)


filters_ki_limit: Final[DoubleParameter] = DoubleParameter(
    name="ki_limit",
    long_name="I term limit",
    description=TextDescription(
        "I term limiter, used to prevent windup. 0 = disabled."
    ),
    maximum=500.0,
    step=2.0,
    decimals=1,
    tx_scale=1000.0,
    suffix=" A",
)


filters_kd_pt1_lowpass_frequency: Final[IntParameter] = IntParameter(
    name="kd_pt1_lowpass_frequency",
    long_name="D term PT1 Low Pass Filter",
    description=TextDescription(
        "D term filter above this frequency. 0 = Disabled."
    ),
    maximum=4000,
    step=10,
    suffix=" Hz",
)


filters_kd2_pt1_lowpass_frequency: Final[IntParameter] = IntParameter(
    name="kd2_pt1_lowpass_frequency",
    long_name="Rate D term PT1 Low Pass Filter",
    description=TextDescription(
        "Rate D term filter above this frequency. 0 = Disabled."
    ),
    maximum=4000,
    step=10,
    suffix=" Hz",
)


filters_kd_pt1_highpass_frequency: Final[IntParameter] = IntParameter(
    name="kd_pt1_highpass_frequency",
    long_name="D term PT1 High Pass Filter",
    description=TextDescription(
        "D term filter below this frequency. 0 = Disabled."
    ),
    maximum=4000,
    step=10,
    suffix=" Hz",
)


setpoint_min: Final[DoubleParameter] = DoubleParameter(
    name="setpoint_min",
    long_name="Setpoint min",
    description=TextDescription(
        "Absolute minimum value allowed for the setpoint. Any setpoint change will stop at this point."
    ),
    minimum=-90.0,
    maximum=0.0,
    decimals=1,
    tx_type=TxType.DOUBLE16,
)


setpoint_max: Final[DoubleParameter] = DoubleParameter(
    name="setpoint_max",
    long_name="Setpoint max",
    description=TextDescription(
        "Absolute maximum value allowed for the setpoint. Any setpoint change will stop at this point."
    ),
    maximum=90.0,
    decimals=1,
    tx_type=TxType.DOUBLE16,
)


setpoint_constant: Final[DoubleParameter] = DoubleParameter(
    name="setpoint_constant",
    long_name="Constant tilt",
    description=TextDescription(
        (
            "Setpoint adjustment (tilt) by a constant value in degrees. Positive value increases the "
            "pitch angle tilting the PEV up. Negative value decreases the pitch angle tilting the PEV "
            "down.\n"
            "\n"
            "All setpoint adjustments do not go below Setpoint min or above Setpoint max values."
        )
    ),
    minimum=-10.0,
    maximum=10.0,
    decimals=1,
    tx_type=TxType.DOUBLE16,
)


setpoint_speed_based: Final[DoubleParameter] = DoubleParameter(
    name="setpoint_speed_based",
    long_name="Speed based tilt",
    description=TextDescription(
        (
            "Setpoint adjustment (tilt) that will be applied depending on speed, specified in degrees per "
            "1000 erpm, applied linearly. Can be downwards (negative) too. Applies in addition to "
            "constant tiltback.\n"
            "\n"
            "All setpoint adjustments do not go below Setpoint min or above Setpoint max values."
        )
    ),
    minimum=-1.0,
    maximum=1.0,
    step=0.01,
    suffix=" °/1000 ERPM",
)


setpoint_change_speed: Final[DoubleParameter] = DoubleParameter(
    name="setpoint_change_speed",
    long_name="Setpoint change speed",
    description=TextDescription(
        "Speed at which setpoint changes will go towards chaning target"
    ),
    default=5.0,
    maximum=100.0,
    step=0.5,
    decimals=1,
    tx_type=TxType.DOUBLE16,
    tx_scale=100.0,
    suffix=" °/s",
)


booster_angle: Final[DoubleParameter] = DoubleParameter(
    name="booster_angle",
    long_name="Start Angle",
    description=TextDescription(
        "Angle at which booster is applied (actually measued as absolute deviation from setpoint)."
    ),
    default=8.0,
    maximum=80.0,
    step=0.5,
    decimals=1,
    suffix=" °",
)


booster_ramp: Final[DoubleParameter] = DoubleParameter(
    name="booster_ramp",
    long_name="Ramp Up",
    description=TextDescription(
        (
            "Degrees over which booster will ramp from 0A to the Configured Current, starting at start "
            "Angle."
        )
    ),
    default=1.0,
    minimum=1.0,
    maximum=80.0,
    step=0.5,
    decimals=1,
    suffix=" °",
)


booster_current: Final[DoubleParameter] = DoubleParameter(
    name="booster_current",
    long_name="Current Boost",
    description=TextDescription(
        "Extra current to be applied when booster angle is reached."
    ),
    maximum=100.0,
    decimals=1,
    tx_scale=1000.0,
    suffix=" A",
)


torque_tilt_start_current: Final[DoubleParameter] = DoubleParameter(
    name="torquetilt_start_current",
    long_name="Start Current Threshold",
    description=TextDescription(
        "Minimum output current threshold for torque tiltback to start applying."
    ),
    default=10.0,
    maximum=100.0,
    step=2.0,
    decimals=1,
    tx_scale=1000.0,
    suffix=" A",
)


torque_tilt_angle_limit: Final[DoubleParameter] = DoubleParameter(
    name="torquetilt_angle_limit",
    long_name="Tilitback Angle Limit",
    description=TextDescription("Max angle to which torque tiltback will tilt."),
    default=5.0,
    maximum=80.0,
    step=0.5,
    decimals=1,
    suffix=" °",
)


torque_tilt_on_speed: Final[DoubleParameter] = DoubleParameter(
    name="torquetilt_on_speed",
    long_name="Max Tiltback Speed",
    description=TextDescription(
        (
            "Max speed at which torque tiltback will tilt to the desired angle (tilt will be slower if "
            "current increases slowly)."
        )
    ),
    default=5.0,
    maximum=100.0,
    step=0.5,
    decimals=1,
    tx_scale=1000.0,
    suffix=" °/s",
)


torque_tilt_off_speed: Final[DoubleParameter] = DoubleParameter(
    name="torquetilt_off_speed",
    long_name="Max Tiltback Release Speed",
    description=TextDescription(
        (
            "Max speed at which torque tiltback will release to the desired angle back to 0 (tilt will be "
            "slower if current decreases slowly)."
        )
    ),
    default=3.0,
    maximum=100.0,
    step=0.5,
    decimals=1,
    tx_scale=1000.0,
    suffix=" °/s",
)


torque_tilt_strength: Final[DoubleParameter] = DoubleParameter(
    name="torquetilt_strength",
    long_name="Strength",
    description=TextDescription(
        "How much tiltback should be applied based on output current."
    ),
    maximum=1.0,
    step=0.05,
    tx_scale=1000.0,
    suffix=" °/A",
)


torque_tilt_filter: Final[DoubleParameter] = DoubleParameter(
    name="torquetilt_filter",
    long_name="Current Filter",
    description=TextDescription(
        (
            "Biquad Low pass filter on the current used for calculating the torquetilt. This smooths out "
            "spikes in the current, and prevents torquetilt from being twitchy."
        )
    ),
    default=2.0,
    maximum=500.0,
    step=0.5,
    decimals=1,
    tx_scale=1000.0,
    suffix=" Hz",
)


turn_tilt_strength: Final[DoubleParameter] = DoubleParameter(
    name="turntilt_strength",
    long_name="Strength",
    description=TextDescription(
        (
            "How much tiltback should be applied based on the sine of the roll angle. A strength value of "
            "N will give N degrees of tiltback when the vehicle is rolled to 90 degrees."
        )
    ),
    maximum=90.0,
    step=0.5,
    decimals=1,
    tx_scale=1000.0,
    suffix=" ",
)


turn_tilt_angle_limit: Final[DoubleParameter] = DoubleParameter(
    name="turntilt_angle_limit",
    long_name="Tilitback Angle Limit",
    description=TextDescription(
        (
            "Max angle to which turn tiltback will tilt. This wont change the power curve, only stop it "
            "at the limit."
        )
    ),
    default=5.0,
    maximum=30.0,
    step=0.5,
    decimals=1,
    tx_scale=1000.0,
    suffix=" °",
)


turn_tilt_start_angle: Final[DoubleParameter] = DoubleParameter(
    name="turntilt_start_angle",
    long_name="Roll Angle Threshold",
    description=TextDescription(
        (
            "Min angle threshold to apply turntilt. Similar to a deadzone, except after reaching the "
            "angle, it will apply as if it started from 0."
        )
    ),
    default=1.0,
    maximum=45.0,
    step=0.5,
    decimals=1,
    suffix=" °",
)


turn_tilt_start_erpm: Final[IntParameter] = IntParameter(
    name="turntilt_start_erpm",
    long_name="ERPM Threshold",
    description=TextDescription("ERPM threshold to apply turntilt."),
    default=100,
    minimum=100,
    maximum=65535,
    step=100,
    suffix=" ERPM",
)


turn_tilt_speed: Final[DoubleParameter] = DoubleParameter(
    name="turntilt_speed",
    long_name="Max Tiltback Speed",
    description=TextDescription(
        (
            "Max speed at which turntilt will tilt to the desired angle (tilt will be slower if roll "
            "angle increases slowly)."
        )
    ),
    default=5.0,
    maximum=100.0,
    step=0.5,
    decimals=1,
    tx_scale=1000.0,
    suffix=" °/s",
)


turn_tilt_erpm_boost: Final[IntParameter] = IntParameter(
    name="turntilt_erpm_boost",
    long_name="Speed Boost %",
    description=TextDescription(
        (
            "Increase the strength based on ERPM. Boost percent is added linearly from 0 erpm (0% boost) "
            "to max erpm (Full configured boost % is applied)."
        )
    ),
    default=20,
    maximum=10000,
    step=5,
    suffix=" %",
)


turn_tilt_erpm_boost_end: Final[IntParameter] = IntParameter(
    name="turntilt_erpm_boost_end",
    long_name="Speed Boost Max ERPM",
    description=TextDescription(
        (
            "ERPM (absolute value) to end boosting the turn tilt effect, above this erpm there will be "
            "constant boost % (at your configured boost %)."
        )
    ),
    default=20000,
    minimum=100,
    maximum=65535,
    step=100,
    suffix=" ERPM",
)


startup_pitch_tolerance: Final[DoubleParameter] = DoubleParameter(
    name="startup_pitch_tolerance",
    long_name="Startup Pitch Axis Angle Tolerance",
    description=TextDescription(
        "Angle at which balancing will start (on the main axis). Measured in degrees from upright (0)."
    ),
    default=20.0,
    maximum=80.0,
    step=0.1,
    decimals=1,
    tx_scale=1000.0,
    suffix=" °",
)


startup_roll_tolerance: Final[DoubleParameter] = DoubleParameter(
    name="startup_roll_tolerance",
    long_name="Startup Roll Axis Angle Tolerance",
    description=TextDescription(
        "Angle at which balancing will start (on the cross axis). Measured in degrees from upright (0)."
    ),
    default=8.0,
    maximum=80.0,
    step=0.1,
    decimals=1,
    tx_scale=1000.0,
    suffix=" °",
)


startup_speed: Final[DoubleParameter] = DoubleParameter(
    name="startup_speed",
    long_name="Startup Centering Speed",
    description=TextDescription(
        "Speed at which wheel will center itself on startup."
    ),
    default=30.0,
    maximum=100.0,
    step=0.1,
    decimals=1,
    tx_scale=1000.0,
    suffix=" °/s",
)


startup_brake_current: Final[DoubleParameter] = DoubleParameter(
    name="brake_current",
    long_name="Brake Current",
    description=TextDescription(
        "Breaking current to be applied when balance app is not actively balancing."
    ),
    maximum=100.0,
    step=2.0,
    tx_scale=1000.0,
    suffix=" A",
)


startup_brake_timeout: Final[IntParameter] = IntParameter(
    name="brake_timeout",
    long_name="Brake Timeout",
    description=TextDescription(
        (
            "Turn off the brake after this many seconds. It will automatically reactivate if the motor "
            "moves. 0 = Disabled."
        )
    ),
    default=10,
    maximum=10000,
    step=5,
    suffix=" s",
)


tiltback_enabled: Final[BoolParameter] = BoolParameter(
    name="tiltback_enabled",
    long_name="Tiltback enabled",
    description=TextDescription(
        (
            "Enable/disable tilbacks completely. Bulletproof way to disable tiltbacks in case of any bugs "
            "in the implementation - omits the whole function call which does tiltbacks processing."
        )
    ),
)


tiltback_return_speed: Final[DoubleParameter] = DoubleParameter(
    name="tiltback_return_speed",
    long_name="Return To Level Speed",
    description=TextDescription(
        (
            "Speed at which vehicle is being returned back to normal after a tiltback condition has been "
            "cleared (should be equal to or slower than slowest tiltback speed)."
        )
    ),
    default=1.0,
    maximum=100.0,
    step=0.5,
    decimals=1,
    tx_type=TxType.DOUBLE16,
    tx_scale=100.0,
    suffix=" °/s",
)


tiltback_duty_angle: Final[DoubleParameter] = DoubleParameter(
    name="tiltback_duty_angle",
    long_name="Angle",
    description=TextDescription("Angle of rise for duty cycle tiltback."),
    default=10.0,
    maximum=45.0,
    decimals=1,
    tx_type=TxType.DOUBLE16,
    tx_scale=100.0,
    suffix=" °",
)


tiltback_duty_speed: Final[DoubleParameter] = DoubleParameter(
    name="tiltback_duty_speed",
    long_name="Speed",
    description=TextDescription(
        (
            "Speed at which vehicle is being tilted back when exceeding duty cycle limit (fast tiltback "
            "can be dangerous!)."
        )
    ),
    default=3.0,
    maximum=100.0,
    step=0.5,
    decimals=1,
    tx_type=TxType.DOUBLE16,
    tx_scale=100.0,
    suffix=" °/s",
)


tiltback_duty: Final[DoubleParameter] = DoubleParameter(
    name="tiltback_duty",
    long_name="Duty Cycle",
    description=TextDescription(
        (
            "Duty cycle threshold to trigger a safety tiltback (Tiltback raises the nose of the vehicle "
            "informing you to slow down)."
        )
    ),
    default=0.75,
    maximum=1.0,
    step=0.01,
    tx_type=TxType.DOUBLE16,
    tx_scale=1000.0,
)


tiltback_hv_angle: Final[DoubleParameter] = DoubleParameter(
    name="tiltback_hv_angle",
    long_name="Angle",
    description=TextDescription("Angle of rise for high voltage tiltback."),
    default=10.0,
    maximum=45.0,
    decimals=1,
    tx_type=TxType.DOUBLE16,
    tx_scale=100.0,
    suffix=" °",
)


tiltback_hv_speed: Final[DoubleParameter] = DoubleParameter(
    name="tiltback_hv_speed",
    long_name="Speed",
    description=TextDescription(
        (
            "Speed at which vehicle is being tilted back when exceeding high voltage limit (fast tiltback "
            "can be dangerous!)."
        )
    ),
    default=3.0,
    maximum=100.0,
    step=0.5,
    decimals=1,
    tx_type=TxType.DOUBLE16,
    tx_scale=100.0,
    suffix=" °/s",
)


tiltback_hv: Final[DoubleParameter] = DoubleParameter(
    name="tiltback_hv",
    long_name="High Voltage",
    description=TextDescription(
        (
            "High voltage threshold to trigger a safety tiltback (Tiltback raises the nose of the vehicle "
            "to alert you). High voltage tiltback is most likely to be triggered when braking or going "
            "downhill on a full battery, sometimes resulting in a tail drag on board shaped vehicles."
        )
    ),
    default=100.0,
    maximum=700.0,
    step=0.1,
    tx_scale=1000.0,
    suffix=" V",
)


tiltback_lv_angle: Final[DoubleParameter] = DoubleParameter(
    name="tiltback_lv_angle",
    long_name="Angle",
    description=TextDescription("Angle of rise for low voltage tiltback."),
    default=10.0,
    maximum=45.0,
    decimals=1,
    tx_type=TxType.DOUBLE16,
    tx_scale=100.0,
    suffix=" °",
)


tiltback_lv_speed: Final[DoubleParameter] = DoubleParameter(
    name="tiltback_lv_speed",
    long_name="Speed",
    description=TextDescription(
        (
            "Speed at which vehicle is being tilted back when below low voltage threshold (fast tiltback "
            "can be dangerous and further contribute to voltage sag!)."
        )
    ),
    default=3.0,
    maximum=100.0,
    step=0.5,
    decimals=1,
    tx_type=TxType.DOUBLE16,
    tx_scale=100.0,
    suffix=" °/s",
)


tiltback_lv: Final[DoubleParameter] = DoubleParameter(
    name="tiltback_lv",
    long_name="Low Voltage",
    description=TextDescription(
        (
            "Low voltage threshold to trigger a safety tiltback (Tiltback raises the nose of the vehicle "
            "informing you to slow down)."
        )
    ),
    maximum=700.0,
    step=0.1,
    tx_scale=1000.0,
    suffix=" V",
)


fault_pitch: Final[DoubleParameter] = DoubleParameter(
    name="fault_pitch",
    long_name="Pitch Axis Fault Cutoff",
    description=TextDescription("Angle to turn off driving (on the pitch axis)."),
    default=30.0,
    minimum=-180.0,
    maximum=180.0,
    decimals=1,
    tx_scale=1000.0,
    suffix=" °",
)


fault_roll: Final[DoubleParameter] = DoubleParameter(
    name="fault_roll",
    long_name="Roll Axis Fault Cutoff",
    description=TextDescription("Angle to turn off driving (on the roll axis)."),
    default=45.0,
    minimum=-180.0,
    maximum=180.0,
    decimals=1,
    tx_scale=1000.0,
    suffix=" °",
)


fault_duty: Final[DoubleParameter] = DoubleParameter(
    name="fault_duty",
    long_name="Duty Cycle Fault Cutoff",
    description=TextDescription(
        (
            "Duty cycle value to trigger a safety cutoff 0-1% (This cutoff will lock the app untill "
            "another fault occurs)."
        )
    ),
    default=0.95,
    maximum=1.0,
    step=0.01,
    tx_scale=1000.0,
)


fault_delay_pitch: Final[IntParameter] = IntParameter(
    name="fault_delay_pitch",
    long_name="Pitch Fault Delay",
    description=TextDescription("Pitch fault cutoff time delay in ms."),
    default=500,
    maximum=10000,
    step=10,
    suffix=" ms",
)


fault_delay_roll: Final[IntParameter] = IntParameter(
    name="fault_delay_roll",
    long_name="Roll Fault Delay",
    description=TextDescription("Roll fault cutoff time delay in ms."),
    maximum=10000,
    step=10,
    suffix=" ms",
)


fault_delay_duty: Final[IntParameter] = IntParameter(
    name="fault_delay_duty",
    long_name="Duty Fault Delay",
    description=TextDescription("Duty cycle cutoff time delay in ms."),
    default=1000,
    maximum=10000,
    step=10,
    suffix=" ms",
)


GROUPS: Final[tuple[Group, ...]] = (
    Group(
        name="General",
        subgroups=(
            Subgroup(
                name="Tune",
                items=(
                    Separator("General"),
                    general_balance_enabled,
                    general_error_ln_slope,
                    general_error_linear_limit,
                    Separator("PID"),
                    pid_mode,
                    pid_kp,
                    pid_kexp,
                    pid_ki,
                    pid_kd,
                    pid_kp2,
                    pid_ki2,
                    pid_kd2,
                    Separator("Main Loop"),
                    main_loop_hertz,
                    main_loop_time_filter,
                    Separator("Filters"),
                    filters_ki_limit,
                    filters_kd_pt1_lowpass_frequency,
                    filters_kd2_pt1_lowpass_frequency,
                    filters_kd_pt1_highpass_frequency,
                ),
            ),
            Subgroup(
                name="Setpoint",
                items=(
                    Separator("Global"),
                    setpoint_max,
                    setpoint_min,
                    setpoint_constant,
                    Separator("Speed based"),
                    setpoint_speed_based,
                    setpoint_change_speed,
                ),
            ),
            Subgroup(
                name="Tune Modifiers",
                items=(
                    Separator("Booster"),
                    booster_angle,
                    booster_ramp,
                    booster_current,
                    Separator("Torque Tiltback"),
                    torque_tilt_strength,
                    torque_tilt_start_current,
                    torque_tilt_angle_limit,
                    torque_tilt_on_speed,
                    torque_tilt_off_speed,
                    torque_tilt_filter,
                    Separator("Turn/Roll Tiltback"),
                    turn_tilt_strength,
                    turn_tilt_angle_limit,
                    turn_tilt_start_angle,
                    turn_tilt_start_erpm,
                    turn_tilt_speed,
                    turn_tilt_erpm_boost,
                    turn_tilt_erpm_boost_end,
                ),
            ),
            Subgroup(
                name="Startup",
                items=(
                    Separator("Tolerances"),
                    startup_pitch_tolerance,
                    startup_roll_tolerance,
                    Separator("Centering"),
                    startup_speed,
                    Separator("Holding"),
                    startup_brake_current,
                    startup_brake_timeout,
                ),
            ),
            Subgroup(
                name="Tiltback",
                items=(
                    Separator("General Config"),
                    tiltback_enabled,
                    tiltback_return_speed,
                    Separator("Duty Cycle Tiltback"),
                    tiltback_duty,
                    tiltback_duty_angle,
                    tiltback_duty_speed,
                    Separator("High Voltage Tiltback"),
                    tiltback_hv,
                    tiltback_hv_angle,
                    tiltback_hv_speed,
                    Separator("Low Voltage Tiltback"),
                    tiltback_lv,
                    tiltback_lv_angle,
                    tiltback_lv_speed,
                ),
            ),
            Subgroup(
                name="Fault",
                items=(
                    Separator("Angle Faults"),
                    fault_pitch,
                    fault_delay_pitch,
                    fault_roll,
                    fault_delay_roll,
                    Separator("Speed Faults"),
                    fault_duty,
                    fault_delay_duty,
                ),
            ),
        ),
    ),
)


XML: Final[SettingsXml] = SettingsXml(
    config_name="balance_config",
    settings_name="Balance ex Settings",
    c_define_prefix="APPCONF_BALANCE",
    groups=GROUPS,
)
