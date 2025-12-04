/*
    Copyright 2019 - 2022 Mitch Lustig
	Copyright 2022 Benjamin Vedder	benjamin@vedder.se

	This file is part of the VESC firmware.

	The VESC firmware is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    The VESC firmware is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef DATA_H_
#define DATA_H_

#include "vesc_c_if.h"
#include "conf/datatypes.h"
#include "biquad.h"

typedef enum {
	STARTUP = 0,
	RUNNING = 1,
	RUNNING_TILTBACK_DUTY = 2,
	RUNNING_TILTBACK_HIGH_VOLTAGE = 3,
	RUNNING_TILTBACK_LOW_VOLTAGE = 4,
	FAULT_ANGLE_PITCH = 5,
	FAULT_ANGLE_ROLL = 6,
	FAULT_DUTY = 7,
	READY = 8,
	KILL_SPIN = 9
} BalanceState;

typedef enum {
	CENTERING = 0,
	TILTBACK_DUTY,
	TILTBACK_HV,
	TILTBACK_LV,
	TILTBACK_NONE
} SetpointAdjustmentType;

typedef struct {
	// Config values
	float wheel_diameter;
	float motor_poles;
	float voltage_max;
	float voltage_min;
	float voltage_lowpass_k;
	float motor_load_lowpass_k;
	float motor_accel_load_lowpass_k;

	// runtime values
	float voltage, voltage_lowpass_state;
	float motor_load_lowpass_state;
	float motor_accel_load_lowpass_state;
	float speed_kmh;
} UIData;

// This is all persistent state of the application, which will be allocated in init. It
// is put here because variables can only be read-only when this program is loaded
// in flash without virtual memory in RAM (as all RAM already is dedicated to the
// main firmware and managed from there). This is probably the main limitation of
// loading applications in runtime, but it is not too bad to work around.
typedef struct {
	lib_thread thread; // Balance Thread

	balance_config balance_conf;

	// Config values
	float loop_time_seconds;
	float startup_step_size;
	float tiltback_duty_step_size, tiltback_hv_step_size, tiltback_lv_step_size, tiltback_return_step_size;
	float torquetilt_on_step_size, torquetilt_off_step_size, turntilt_step_size;
	float tiltback_variable, tiltback_variable_max_erpm, noseangling_step_size;

	// Runtime values read from elsewhere
	float pitch_angle, last_pitch_angle, roll_angle, abs_roll_angle, abs_roll_angle_sin, last_gyro_y;
	float gyro[3];
	float duty_cycle, abs_duty_cycle;
	float erpm, abs_erpm, last_erpm;
	float motor_current;
	float adc1, adc2;

	// Data for UI
	UIData ui_data;

	// Experimental
	float erpm_accel;
	float motor_load, motor_accel_load;


	// Rumtime state values
	BalanceState state;
	float proportional, exponential, integral, derivative, proportional2, integral2, derivative2;
	float error, last_error, abs_error, sign_error;
	float pid_value, pid_value2;
	float setpoint, setpoint_target, setpoint_target_interpolated;
	float noseangling_interpolated;
	float torquetilt_filtered_current, torquetilt_target, torquetilt_interpolated;
	Biquad torquetilt_current_biquad;
	float turntilt_target, turntilt_interpolated;
	SetpointAdjustmentType setpointAdjustmentType;
	float current_time, last_time, diff_time, loop_overshoot; // Seconds
	float filtered_loop_overshoot, loop_overshoot_alpha, filtered_diff_time;
	float fault_angle_pitch_timer, fault_angle_roll_timer, fault_duty_timer; // Seconds
	float d_pt1_lowpass_state, d_pt1_lowpass_k, d_pt1_highpass_state, d_pt1_highpass_k;
	float d2_pt1_lowpass_state, d2_pt1_lowpass_k;
	float motor_timeout_seconds;
	float brake_timeout; // Seconds
} data;

#endif // DATA_H_

