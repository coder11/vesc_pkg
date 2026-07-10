"""Balance application settings expressed as typed Python objects."""

from __future__ import annotations

from dataclasses import dataclass
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


@dataclass(frozen=True, slots=True)
class GeneralParameters:
    balance_enabled: BoolParameter
    error_linear_limit: DoubleParameter
    error_ln_slope: DoubleParameter

@dataclass(frozen=True, slots=True)
class PidParameters:
    pid_mode: EnumParameter
    kp: DoubleParameter
    kexp: DoubleParameter
    ki: DoubleParameter
    kd: DoubleParameter
    kp2: DoubleParameter
    ki2: DoubleParameter
    kd2: DoubleParameter

@dataclass(frozen=True, slots=True)
class MainLoopParameters:
    hertz: IntParameter
    loop_time_filter: IntParameter

@dataclass(frozen=True, slots=True)
class FilterParameters:
    ki_limit: DoubleParameter
    kd_pt1_lowpass_frequency: IntParameter
    kd2_pt1_lowpass_frequency: IntParameter
    kd_pt1_highpass_frequency: IntParameter

@dataclass(frozen=True, slots=True)
class SetpointParameters:
    setpoint_min: DoubleParameter
    setpoint_max: DoubleParameter
    setpoint_constant: DoubleParameter
    setpoint_speed_based: DoubleParameter
    setpoint_change_speed: DoubleParameter

@dataclass(frozen=True, slots=True)
class BoosterParameters:
    booster_angle: DoubleParameter
    booster_ramp: DoubleParameter
    booster_current: DoubleParameter

@dataclass(frozen=True, slots=True)
class TorqueTiltParameters:
    torquetilt_start_current: DoubleParameter
    torquetilt_angle_limit: DoubleParameter
    torquetilt_on_speed: DoubleParameter
    torquetilt_off_speed: DoubleParameter
    torquetilt_strength: DoubleParameter
    torquetilt_filter: DoubleParameter

@dataclass(frozen=True, slots=True)
class TurnTiltParameters:
    turntilt_strength: DoubleParameter
    turntilt_angle_limit: DoubleParameter
    turntilt_start_angle: DoubleParameter
    turntilt_start_erpm: IntParameter
    turntilt_speed: DoubleParameter
    turntilt_erpm_boost: IntParameter
    turntilt_erpm_boost_end: IntParameter

@dataclass(frozen=True, slots=True)
class StartupParameters:
    startup_pitch_tolerance: DoubleParameter
    startup_roll_tolerance: DoubleParameter
    startup_speed: DoubleParameter
    brake_current: DoubleParameter
    brake_timeout: IntParameter

@dataclass(frozen=True, slots=True)
class TiltbackParameters:
    tiltback_enabled: BoolParameter
    tiltback_return_speed: DoubleParameter
    tiltback_duty_angle: DoubleParameter
    tiltback_duty_speed: DoubleParameter
    tiltback_duty: DoubleParameter
    tiltback_hv_angle: DoubleParameter
    tiltback_hv_speed: DoubleParameter
    tiltback_hv: DoubleParameter
    tiltback_lv_angle: DoubleParameter
    tiltback_lv_speed: DoubleParameter
    tiltback_lv: DoubleParameter

@dataclass(frozen=True, slots=True)
class FaultParameters:
    fault_pitch: DoubleParameter
    fault_roll: DoubleParameter
    fault_duty: DoubleParameter
    fault_delay_pitch: IntParameter
    fault_delay_roll: IntParameter
    fault_delay_duty: IntParameter


general: Final[GeneralParameters] = GeneralParameters(
    balance_enabled=BoolParameter(
        name='balance_enabled',
        long_name='Balancing enabled',
        description=TextDescription(('Enable/disable balancing. Turn it off to experiment with base motor settings without the '
         'balance interfering.')),
        c_define='APPCONF_BALANCE_ENABLED',
    ),
    error_linear_limit=DoubleParameter(
        name='error_linear_limit',
        long_name='Error response linear limit',
        description=RawDescription(('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" '
         '"http://www.w3.org/TR/REC-html40/strict.dtd">\n'
         '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
         'p, li { white-space: pre-wrap; }\n'
         '</style></head><body style=" font-family:\'Roboto\'; ; font-weight:400; '
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
         'the pitch in degrees.</p>\n'
         '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; '
         'margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>\n'
         '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; '
         '-qt-block-indent:0; text-indent:0px;">It starts linear up to a limit and then descreses '
         'logarithmically with a specific slope.</p>\n'
         '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; '
         'margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>\n'
         '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; '
         '-qt-block-indent:0; text-indent:0px;">This parameter controls <span style=" '
         'font-weight:600;">d</span></p></body></html>')),
        c_define='APPCONF_ERROR_LINEAR_LIMIT',
        default=90.0,
        maximum=90.0,
        step=0.1,
        decimals=1,
    ),
    error_ln_slope=DoubleParameter(
        name='error_ln_slope',
        long_name='Error logarithm slope',
        description=RawDescription(('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" '
         '"http://www.w3.org/TR/REC-html40/strict.dtd">\n'
         '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
         'p, li { white-space: pre-wrap; }\n'
         '</style></head><body style=" font-family:\'Roboto\'; ; font-weight:400; '
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
         'the pitch in degrees.</p>\n'
         '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; '
         'margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>\n'
         '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; '
         '-qt-block-indent:0; text-indent:0px;">It starts linear up to a limit and then descreses '
         'logarithmically with a specific slope.</p>\n'
         '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; '
         'margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>\n'
         '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; '
         '-qt-block-indent:0; text-indent:0px;">This parameter controls <span style=" '
         'font-weight:600;">k</span></p></body></html>')),
        c_define='APPCONF_ERROR_LN_SLOPE',
        default=0.1,
        minimum=0.1,
        maximum=50.0,
        step=0.1,
        decimals=1,
    ),
)

pid: Final[PidParameters] = PidParameters(
    pid_mode=EnumParameter(
        name='pid_mode',
        long_name='PID Mode',
        description=TextDescription('PID loop mode, Angle or Cascadeing Angle Rate.'),
        c_define='APPCONF_BALANCE_PID_MODE',
        choices=('BALANCE_PID_MODE_ANGLE', 'BALANCE_PID_MODE_ANGLE_RATE_CASCADE'),
    ),
    kp=DoubleParameter(
        name='kp',
        long_name='Angle P',
        description=TextDescription('P value for the PID balance loop.'),
        c_define='APPCONF_BALANCE_KP',
        maximum=100000.0,
        step=0.1,
        decimals=4,
        tx_scale=1000.0,
    ),
    kexp=DoubleParameter(
        name='kexp',
        long_name='Angle exponential',
        description=TextDescription(('Exponential component defined as e^(kx) - 1\n'
         '\n'
         'This parameter controls the "steepness" of the exponent, k')),
        c_define='APPCONF_BALANCE_KEXP',
        maximum=20.0,
        step=0.1,
    ),
    ki=DoubleParameter(
        name='ki',
        long_name='Angle I',
        description=TextDescription('I value for the PID balance loop.'),
        c_define='APPCONF_BALANCE_KI',
        maximum=100000.0,
        step=0.1,
        decimals=4,
        tx_scale=1000.0,
    ),
    kd=DoubleParameter(
        name='kd',
        long_name='Angle D',
        description=TextDescription('D value for the PID balance loop.'),
        c_define='APPCONF_BALANCE_KD',
        maximum=100000.0,
        step=0.1,
        decimals=4,
        tx_scale=1000.0,
    ),
    kp2=DoubleParameter(
        name='kp2',
        long_name='Rate P',
        description=TextDescription('P value for the PID balance loop.'),
        c_define='APPCONF_BALANCE_KP2',
        maximum=100000.0,
        step=0.1,
        decimals=4,
        tx_scale=1000.0,
    ),
    ki2=DoubleParameter(
        name='ki2',
        long_name='Rate I',
        description=TextDescription('I value for the PID balance loop.'),
        c_define='APPCONF_BALANCE_KI2',
        maximum=100000.0,
        step=0.1,
        decimals=4,
        tx_scale=1000.0,
    ),
    kd2=DoubleParameter(
        name='kd2',
        long_name='Rate D',
        description=TextDescription('D value for the PID balance loop.'),
        c_define='APPCONF_BALANCE_KD2',
        maximum=100000.0,
        step=0.1,
        decimals=4,
        tx_scale=1000.0,
    ),
)

main_loop: Final[MainLoopParameters] = MainLoopParameters(
    hertz=IntParameter(
        name='hertz',
        long_name='Loop Hertz',
        description=TextDescription('Loop Hertz.'),
        c_define='APPCONF_BALANCE_HERTZ',
        default=1000,
        minimum=50,
        maximum=4000,
        step=100,
        suffix=' Hz',
    ),
    loop_time_filter=IntParameter(
        name='loop_time_filter',
        long_name='Loop Time Correction Filter',
        description=TextDescription('Filter overshoot and correct for it.'),
        c_define='APPCONF_BALANCE_LOOP_TIME_FILTER',
        maximum=1000,
        step=10,
        suffix=' Hz',
    ),
)

filters: Final[FilterParameters] = FilterParameters(
    ki_limit=DoubleParameter(
        name='ki_limit',
        long_name='I term limit',
        description=TextDescription('I term limiter, used to prevent windup. 0 = disabled.'),
        c_define='APPCONF_BALANCE_KI_LIMIT',
        maximum=500.0,
        step=2.0,
        decimals=1,
        tx_scale=1000.0,
        suffix=' A',
    ),
    kd_pt1_lowpass_frequency=IntParameter(
        name='kd_pt1_lowpass_frequency',
        long_name='D term PT1 Low Pass Filter',
        description=TextDescription('D term filter above this frequency. 0 = Disabled.'),
        c_define='APPCONF_BALANCE_KD_PT1_LOWPASS_FREQUENCY',
        maximum=4000,
        step=10,
        suffix=' Hz',
    ),
    kd2_pt1_lowpass_frequency=IntParameter(
        name='kd2_pt1_lowpass_frequency',
        long_name='Rate D term PT1 Low Pass Filter',
        description=TextDescription('Rate D term filter above this frequency. 0 = Disabled.'),
        c_define='APPCONF_BALANCE_KD2_PT1_LOWPASS_FREQUENCY',
        maximum=4000,
        step=10,
        suffix=' Hz',
    ),
    kd_pt1_highpass_frequency=IntParameter(
        name='kd_pt1_highpass_frequency',
        long_name='D term PT1 High Pass Filter',
        description=TextDescription('D term filter below this frequency. 0 = Disabled.'),
        c_define='APPCONF_BALANCE_KD_PT1_HIGHPASS_FREQUENCY',
        maximum=4000,
        step=10,
        suffix=' Hz',
    ),
)

setpoint: Final[SetpointParameters] = SetpointParameters(
    setpoint_min=DoubleParameter(
        name='setpoint_min',
        long_name='Setpoint min',
        description=TextDescription('Absolute minimum value allowed for the setpoint. Any setpoint change will stop at this point.'),
        c_define='APPCONF_SETPOINT_MIN',
        minimum=-90.0,
        maximum=0.0,
        decimals=1,
        tx_type=TxType.DOUBLE16,
    ),
    setpoint_max=DoubleParameter(
        name='setpoint_max',
        long_name='Setpoint max',
        description=TextDescription('Absolute maximum value allowed for the setpoint. Any setpoint change will stop at this point.'),
        c_define='APPCONF_SETPOINT_MAX',
        maximum=90.0,
        decimals=1,
        tx_type=TxType.DOUBLE16,
    ),
    setpoint_constant=DoubleParameter(
        name='setpoint_constant',
        long_name='Constant tilt',
        description=TextDescription(('Setpoint adjustment (tilt) by a constant value in degrees. Positive value increases the '
         'pitch angle tilting the PEV up. Negative value decreases the pitch angle tilting the PEV '
         'down.\n'
         '\n'
         'All setpoint adjustments do not go below Setpoint min or above Setpoint max values.')),
        c_define='APPCONF_SETPOINT_CONSTANT',
        minimum=-10.0,
        maximum=10.0,
        decimals=1,
        tx_type=TxType.DOUBLE16,
    ),
    setpoint_speed_based=DoubleParameter(
        name='setpoint_speed_based',
        long_name='Speed based tilt',
        description=TextDescription(('Setpoint adjustment (tilt) that will be applied depending on speed, specified in degrees per '
         '1000 erpm, applied linearly. Can be downwards (negative) too. Applies in addition to '
         'constant tiltback.\n'
         '\n'
         'All setpoint adjustments do not go below Setpoint min or above Setpoint max values.')),
        c_define='APPCONF_SETPOINT_SPEED_BASED',
        minimum=-1.0,
        maximum=1.0,
        step=0.01,
        suffix=' °/1000 ERPM',
    ),
    setpoint_change_speed=DoubleParameter(
        name='setpoint_change_speed',
        long_name='Setpoint change speed',
        description=TextDescription('Speed at which setpoint changes will go towards chaning target'),
        c_define='APPCONF_SETPOINT_CHANGE_SPEED',
        default=5.0,
        maximum=100.0,
        step=0.5,
        decimals=1,
        tx_type=TxType.DOUBLE16,
        tx_scale=100.0,
        suffix=' °/s',
    ),
)

booster: Final[BoosterParameters] = BoosterParameters(
    booster_angle=DoubleParameter(
        name='booster_angle',
        long_name='Start Angle',
        description=TextDescription('Angle at which booster is applied (actually measued as absolute deviation from setpoint).'),
        c_define='APPCONF_BALANCE_BOOSTER_ANGLE',
        default=8.0,
        maximum=80.0,
        step=0.5,
        decimals=1,
        suffix=' °',
    ),
    booster_ramp=DoubleParameter(
        name='booster_ramp',
        long_name='Ramp Up',
        description=TextDescription(('Degrees over which booster will ramp from 0A to the Configured Current, starting at start '
         'Angle.')),
        c_define='APPCONF_BALANCE_BOOSTER_RAMP',
        default=1.0,
        minimum=1.0,
        maximum=80.0,
        step=0.5,
        decimals=1,
        suffix=' °',
    ),
    booster_current=DoubleParameter(
        name='booster_current',
        long_name='Current Boost',
        description=TextDescription('Extra current to be applied when booster angle is reached.'),
        c_define='APPCONF_BALANCE_BOOSTER_CURRENT',
        maximum=100.0,
        decimals=1,
        tx_scale=1000.0,
        suffix=' A',
    ),
)

torque_tilt: Final[TorqueTiltParameters] = TorqueTiltParameters(
    torquetilt_start_current=DoubleParameter(
        name='torquetilt_start_current',
        long_name='Start Current Threshold',
        description=TextDescription('Minimum output current threshold for torque tiltback to start applying.'),
        c_define='APPCONF_BALANCE_TORQUETILT_START_CURRENT',
        default=10.0,
        maximum=100.0,
        step=2.0,
        decimals=1,
        tx_scale=1000.0,
        suffix=' A',
    ),
    torquetilt_angle_limit=DoubleParameter(
        name='torquetilt_angle_limit',
        long_name='Tilitback Angle Limit',
        description=TextDescription('Max angle to which torque tiltback will tilt.'),
        c_define='APPCONF_BALANCE_TORQUETILT_ANGLE_LIMIT',
        default=5.0,
        maximum=80.0,
        step=0.5,
        decimals=1,
        suffix=' °',
    ),
    torquetilt_on_speed=DoubleParameter(
        name='torquetilt_on_speed',
        long_name='Max Tiltback Speed',
        description=TextDescription(('Max speed at which torque tiltback will tilt to the desired angle (tilt will be slower if '
         'current increases slowly).')),
        c_define='APPCONF_BALANCE_TORQUETILT_ON_SPEED',
        default=5.0,
        maximum=100.0,
        step=0.5,
        decimals=1,
        tx_scale=1000.0,
        suffix=' °/s',
    ),
    torquetilt_off_speed=DoubleParameter(
        name='torquetilt_off_speed',
        long_name='Max Tiltback Release Speed',
        description=TextDescription(('Max speed at which torque tiltback will release to the desired angle back to 0 (tilt will be '
         'slower if current decreases slowly).')),
        c_define='APPCONF_BALANCE_TORQUETILT_OFF_SPEED',
        default=3.0,
        maximum=100.0,
        step=0.5,
        decimals=1,
        tx_scale=1000.0,
        suffix=' °/s',
    ),
    torquetilt_strength=DoubleParameter(
        name='torquetilt_strength',
        long_name='Strength',
        description=TextDescription('How much tiltback should be applied based on output current.'),
        c_define='APPCONF_BALANCE_TORQUETILT_STRENGTH',
        maximum=1.0,
        step=0.05,
        tx_scale=1000.0,
        suffix=' °/A',
    ),
    torquetilt_filter=DoubleParameter(
        name='torquetilt_filter',
        long_name='Current Filter',
        description=TextDescription(('Biquad Low pass filter on the current used for calculating the torquetilt. This smooths out '
         'spikes in the current, and prevents torquetilt from being twitchy.')),
        c_define='APPCONF_BALANCE_TORQUETILT_FILTER',
        default=2.0,
        maximum=500.0,
        step=0.5,
        decimals=1,
        tx_scale=1000.0,
        suffix=' Hz',
    ),
)

turn_tilt: Final[TurnTiltParameters] = TurnTiltParameters(
    turntilt_strength=DoubleParameter(
        name='turntilt_strength',
        long_name='Strength',
        description=TextDescription(('How much tiltback should be applied based on the sine of the roll angle. A strength value of '
         'N will give N degrees of tiltback when the vehicle is rolled to 90 degrees.')),
        c_define='APPCONF_BALANCE_TURNTILT_STRENGTH',
        maximum=90.0,
        step=0.5,
        decimals=1,
        tx_scale=1000.0,
        suffix=' ',
    ),
    turntilt_angle_limit=DoubleParameter(
        name='turntilt_angle_limit',
        long_name='Tilitback Angle Limit',
        description=TextDescription(('Max angle to which turn tiltback will tilt. This wont change the power curve, only stop it '
         'at the limit.')),
        c_define='APPCONF_BALANCE_TURNTILT_ANGLE_LIMIT',
        default=5.0,
        maximum=30.0,
        step=0.5,
        decimals=1,
        tx_scale=1000.0,
        suffix=' °',
    ),
    turntilt_start_angle=DoubleParameter(
        name='turntilt_start_angle',
        long_name='Roll Angle Threshold',
        description=TextDescription(('Min angle threshold to apply turntilt. Similar to a deadzone, except after reaching the '
         'angle, it will apply as if it started from 0.')),
        c_define='APPCONF_BALANCE_TURNTILT_START_ANGLE',
        default=1.0,
        maximum=45.0,
        step=0.5,
        decimals=1,
        suffix=' °',
    ),
    turntilt_start_erpm=IntParameter(
        name='turntilt_start_erpm',
        long_name='ERPM Threshold',
        description=TextDescription('ERPM threshold to apply turntilt.'),
        c_define='APPCONF_BALANCE_TURNTILT_START_ERPM',
        default=100,
        minimum=100,
        maximum=65535,
        step=100,
        suffix=' ERPM',
    ),
    turntilt_speed=DoubleParameter(
        name='turntilt_speed',
        long_name='Max Tiltback Speed',
        description=TextDescription(('Max speed at which turntilt will tilt to the desired angle (tilt will be slower if roll '
         'angle increases slowly).')),
        c_define='APPCONF_BALANCE_TURNTILT_SPEED',
        default=5.0,
        maximum=100.0,
        step=0.5,
        decimals=1,
        tx_scale=1000.0,
        suffix=' °/s',
    ),
    turntilt_erpm_boost=IntParameter(
        name='turntilt_erpm_boost',
        long_name='Speed Boost %',
        description=TextDescription(('Increase the strength based on ERPM. Boost percent is added linearly from 0 erpm (0% boost) '
         'to max erpm (Full configured boost % is applied).')),
        c_define='APPCONF_BALANCE_TURNTILT_ERPM_BOOST',
        default=20,
        maximum=10000,
        step=5,
        suffix=' %',
    ),
    turntilt_erpm_boost_end=IntParameter(
        name='turntilt_erpm_boost_end',
        long_name='Speed Boost Max ERPM',
        description=TextDescription(('ERPM (absolute value) to end boosting the turn tilt effect, above this erpm there will be '
         'constant boost % (at your configured boost %).')),
        c_define='APPCONF_BALANCE_TURNTILT_ERPM_BOOST_END',
        default=20000,
        minimum=100,
        maximum=65535,
        step=100,
        suffix=' ERPM',
    ),
)

startup: Final[StartupParameters] = StartupParameters(
    startup_pitch_tolerance=DoubleParameter(
        name='startup_pitch_tolerance',
        long_name='Startup Pitch Axis Angle Tolerance',
        description=TextDescription('Angle at which balancing will start (on the main axis). Measured in degrees from upright (0).'),
        c_define='APPCONF_BALANCE_STARTUP_PITCH_TOLERANCE',
        default=20.0,
        maximum=80.0,
        step=0.1,
        decimals=1,
        tx_scale=1000.0,
        suffix=' °',
    ),
    startup_roll_tolerance=DoubleParameter(
        name='startup_roll_tolerance',
        long_name='Startup Roll Axis Angle Tolerance',
        description=TextDescription('Angle at which balancing will start (on the cross axis). Measured in degrees from upright (0).'),
        c_define='APPCONF_BALANCE_STARTUP_ROLL_TOLERANCE',
        default=8.0,
        maximum=80.0,
        step=0.1,
        decimals=1,
        tx_scale=1000.0,
        suffix=' °',
    ),
    startup_speed=DoubleParameter(
        name='startup_speed',
        long_name='Startup Centering Speed',
        description=TextDescription('Speed at which wheel will center itself on startup.'),
        c_define='APPCONF_BALANCE_STARTUP_SPEED',
        default=30.0,
        maximum=100.0,
        step=0.1,
        decimals=1,
        tx_scale=1000.0,
        suffix=' °/s',
    ),
    brake_current=DoubleParameter(
        name='brake_current',
        long_name='Brake Current',
        description=TextDescription('Breaking current to be applied when balance app is not actively balancing.'),
        c_define='APPCONF_BALANCE_BRAKE_CURRENT',
        maximum=100.0,
        step=2.0,
        tx_scale=1000.0,
        suffix=' A',
    ),
    brake_timeout=IntParameter(
        name='brake_timeout',
        long_name='Brake Timeout',
        description=TextDescription(('Turn off the brake after this many seconds. It will automatically reactivate if the motor '
         'moves. 0 = Disabled.')),
        c_define='APPCONF_BALANCE_BRAKE_TIMEOUT',
        default=10,
        maximum=10000,
        step=5,
        suffix=' s',
    ),
)

tiltback: Final[TiltbackParameters] = TiltbackParameters(
    tiltback_enabled=BoolParameter(
        name='tiltback_enabled',
        long_name='Tiltback enabled',
        description=TextDescription(('Enable/disable tilbacks completely. Bulletproof way to disable tiltbacks in case of any bugs '
         'in the implementation - omits the whole function call which does tiltbacks processing.')),
        c_define='APPCONF_TILTBACK_ENABLED',
    ),
    tiltback_return_speed=DoubleParameter(
        name='tiltback_return_speed',
        long_name='Return To Level Speed',
        description=TextDescription(('Speed at which vehicle is being returned back to normal after a tiltback condition has been '
         'cleared (should be equal to or slower than slowest tiltback speed).')),
        c_define='APPCONF_BALANCE_TILTBACK_RETURN_SPEED',
        default=1.0,
        maximum=100.0,
        step=0.5,
        decimals=1,
        tx_type=TxType.DOUBLE16,
        tx_scale=100.0,
        suffix=' °/s',
    ),
    tiltback_duty_angle=DoubleParameter(
        name='tiltback_duty_angle',
        long_name='Angle',
        description=TextDescription('Angle of rise for duty cycle tiltback.'),
        c_define='APPCONF_BALANCE_TILTBACK_DUTY_ANGLE',
        default=10.0,
        maximum=45.0,
        decimals=1,
        tx_type=TxType.DOUBLE16,
        tx_scale=100.0,
        suffix=' °',
    ),
    tiltback_duty_speed=DoubleParameter(
        name='tiltback_duty_speed',
        long_name='Speed',
        description=TextDescription(('Speed at which vehicle is being tilted back when exceeding duty cycle limit (fast tiltback '
         'can be dangerous!).')),
        c_define='APPCONF_BALANCE_TILTBACK_DUTY_SPEED',
        default=3.0,
        maximum=100.0,
        step=0.5,
        decimals=1,
        tx_type=TxType.DOUBLE16,
        tx_scale=100.0,
        suffix=' °/s',
    ),
    tiltback_duty=DoubleParameter(
        name='tiltback_duty',
        long_name='Duty Cycle',
        description=TextDescription(('Duty cycle threshold to trigger a safety tiltback (Tiltback raises the nose of the vehicle '
         'informing you to slow down).')),
        c_define='APPCONF_BALANCE_TILTBACK_DUTY',
        default=0.75,
        maximum=1.0,
        step=0.01,
        tx_type=TxType.DOUBLE16,
        tx_scale=1000.0,
    ),
    tiltback_hv_angle=DoubleParameter(
        name='tiltback_hv_angle',
        long_name='Angle',
        description=TextDescription('Angle of rise for high voltage tiltback.'),
        c_define='APPCONF_BALANCE_TILTBACK_HV_ANGLE',
        default=10.0,
        maximum=45.0,
        decimals=1,
        tx_type=TxType.DOUBLE16,
        tx_scale=100.0,
        suffix=' °',
    ),
    tiltback_hv_speed=DoubleParameter(
        name='tiltback_hv_speed',
        long_name='Speed',
        description=TextDescription(('Speed at which vehicle is being tilted back when exceeding high voltage limit (fast tiltback '
         'can be dangerous!).')),
        c_define='APPCONF_BALANCE_TILTBACK_HV_SPEED',
        default=3.0,
        maximum=100.0,
        step=0.5,
        decimals=1,
        tx_type=TxType.DOUBLE16,
        tx_scale=100.0,
        suffix=' °/s',
    ),
    tiltback_hv=DoubleParameter(
        name='tiltback_hv',
        long_name='High Voltage',
        description=TextDescription(('High voltage threshold to trigger a safety tiltback (Tiltback raises the nose of the vehicle '
         'to alert you). High voltage tiltback is most likely to be triggered when braking or going '
         'downhill on a full battery, sometimes resulting in a tail drag on board shaped vehicles.')),
        c_define='APPCONF_BALANCE_TILTBACK_HV',
        default=100.0,
        maximum=700.0,
        step=0.1,
        tx_scale=1000.0,
        suffix=' V',
    ),
    tiltback_lv_angle=DoubleParameter(
        name='tiltback_lv_angle',
        long_name='Angle',
        description=TextDescription('Angle of rise for low voltage tiltback.'),
        c_define='APPCONF_BALANCE_TILTBACK_LV_ANGLE',
        default=10.0,
        maximum=45.0,
        decimals=1,
        tx_type=TxType.DOUBLE16,
        tx_scale=100.0,
        suffix=' °',
    ),
    tiltback_lv_speed=DoubleParameter(
        name='tiltback_lv_speed',
        long_name='Speed',
        description=TextDescription(('Speed at which vehicle is being tilted back when below low voltage threshold (fast tiltback '
         'can be dangerous and further contribute to voltage sag!).')),
        c_define='APPCONF_BALANCE_TILTBACK_LV_SPEED',
        default=3.0,
        maximum=100.0,
        step=0.5,
        decimals=1,
        tx_type=TxType.DOUBLE16,
        tx_scale=100.0,
        suffix=' °/s',
    ),
    tiltback_lv=DoubleParameter(
        name='tiltback_lv',
        long_name='Low Voltage',
        description=TextDescription(('Low voltage threshold to trigger a safety tiltback (Tiltback raises the nose of the vehicle '
         'informing you to slow down).')),
        c_define='APPCONF_BALANCE_TILTBACK_LV',
        maximum=700.0,
        step=0.1,
        tx_scale=1000.0,
        suffix=' V',
    ),
)

fault: Final[FaultParameters] = FaultParameters(
    fault_pitch=DoubleParameter(
        name='fault_pitch',
        long_name='Pitch Axis Fault Cutoff',
        description=TextDescription('Angle to turn off driving (on the pitch axis).'),
        c_define='APPCONF_BALANCE_FAULT_PITCH',
        default=30.0,
        minimum=-180.0,
        maximum=180.0,
        decimals=1,
        tx_scale=1000.0,
        suffix=' °',
    ),
    fault_roll=DoubleParameter(
        name='fault_roll',
        long_name='Roll Axis Fault Cutoff',
        description=TextDescription('Angle to turn off driving (on the roll axis).'),
        c_define='APPCONF_BALANCE_FAULT_ROLL',
        default=45.0,
        minimum=-180.0,
        maximum=180.0,
        decimals=1,
        tx_scale=1000.0,
        suffix=' °',
    ),
    fault_duty=DoubleParameter(
        name='fault_duty',
        long_name='Duty Cycle Fault Cutoff',
        description=TextDescription(('Duty cycle value to trigger a safety cutoff 0-1% (This cutoff will lock the app untill '
         'another fault occurs).')),
        c_define='APPCONF_BALANCE_FAULT_DUTY',
        default=0.95,
        maximum=1.0,
        step=0.01,
        tx_scale=1000.0,
    ),
    fault_delay_pitch=IntParameter(
        name='fault_delay_pitch',
        long_name='Pitch Fault Delay',
        description=TextDescription('Pitch fault cutoff time delay in ms.'),
        c_define='APPCONF_BALANCE_FAULT_DELAY_PITCH',
        default=500,
        maximum=10000,
        step=10,
        suffix=' ms',
    ),
    fault_delay_roll=IntParameter(
        name='fault_delay_roll',
        long_name='Roll Fault Delay',
        description=TextDescription('Roll fault cutoff time delay in ms.'),
        c_define='APPCONF_BALANCE_FAULT_DELAY_ROLL',
        maximum=10000,
        step=10,
        suffix=' ms',
    ),
    fault_delay_duty=IntParameter(
        name='fault_delay_duty',
        long_name='Duty Fault Delay',
        description=TextDescription('Duty cycle cutoff time delay in ms.'),
        c_define='APPCONF_BALANCE_FAULT_DELAY_DUTY',
        default=1000,
        maximum=10000,
        step=10,
        suffix=' ms',
    ),
)


GROUPS: Final[tuple[Group, ...]] = (
    Group(
        name="General",
        subgroups=(
            Subgroup(
                name="Tune",
                items=(
                    Separator("General"),
                    general.balance_enabled,
                    general.error_ln_slope,
                    general.error_linear_limit,
                    Separator("PID"),
                    pid.pid_mode,
                    pid.kp,
                    pid.kexp,
                    pid.ki,
                    pid.kd,
                    pid.kp2,
                    pid.ki2,
                    pid.kd2,
                    Separator("Main Loop"),
                    main_loop.hertz,
                    main_loop.loop_time_filter,
                    Separator("Filters"),
                    filters.ki_limit,
                    filters.kd_pt1_lowpass_frequency,
                    filters.kd2_pt1_lowpass_frequency,
                    filters.kd_pt1_highpass_frequency,
                ),
            ),
            Subgroup(
                name="Setpoint",
                items=(
                    Separator("Global"),
                    setpoint.setpoint_max,
                    setpoint.setpoint_min,
                    setpoint.setpoint_constant,
                    Separator("Speed based"),
                    setpoint.setpoint_speed_based,
                    setpoint.setpoint_change_speed,
                ),
            ),
            Subgroup(
                name="Tune Modifiers",
                items=(
                    Separator("Booster"),
                    booster.booster_angle,
                    booster.booster_ramp,
                    booster.booster_current,
                    Separator("Torque Tiltback"),
                    torque_tilt.torquetilt_strength,
                    torque_tilt.torquetilt_start_current,
                    torque_tilt.torquetilt_angle_limit,
                    torque_tilt.torquetilt_on_speed,
                    torque_tilt.torquetilt_off_speed,
                    torque_tilt.torquetilt_filter,
                    Separator("Turn/Roll Tiltback"),
                    turn_tilt.turntilt_strength,
                    turn_tilt.turntilt_angle_limit,
                    turn_tilt.turntilt_start_angle,
                    turn_tilt.turntilt_start_erpm,
                    turn_tilt.turntilt_speed,
                    turn_tilt.turntilt_erpm_boost,
                    turn_tilt.turntilt_erpm_boost_end,
                ),
            ),
            Subgroup(
                name="Startup",
                items=(
                    Separator("Tolerances"),
                    startup.startup_pitch_tolerance,
                    startup.startup_roll_tolerance,
                    Separator("Centering"),
                    startup.startup_speed,
                    Separator("Holding"),
                    startup.brake_current,
                    startup.brake_timeout,
                ),
            ),
            Subgroup(
                name="Tiltback",
                items=(
                    Separator("General Config"),
                    tiltback.tiltback_enabled,
                    tiltback.tiltback_return_speed,
                    Separator("Duty Cycle Tiltback"),
                    tiltback.tiltback_duty,
                    tiltback.tiltback_duty_angle,
                    tiltback.tiltback_duty_speed,
                    Separator("High Voltage Tiltback"),
                    tiltback.tiltback_hv,
                    tiltback.tiltback_hv_angle,
                    tiltback.tiltback_hv_speed,
                    Separator("Low Voltage Tiltback"),
                    tiltback.tiltback_lv,
                    tiltback.tiltback_lv_angle,
                    tiltback.tiltback_lv_speed,
                ),
            ),
            Subgroup(
                name="Fault",
                items=(
                    Separator("Angle Faults"),
                    fault.fault_pitch,
                    fault.fault_delay_pitch,
                    fault.fault_roll,
                    fault.fault_delay_roll,
                    Separator("Speed Faults"),
                    fault.fault_duty,
                    fault.fault_delay_duty,
                ),
            ),
        ),
    ),
)


XML: Final[SettingsXml] = SettingsXml(
    config_name="balance_config",
    settings_name="Balance ex Settings",
    groups=GROUPS,
)

