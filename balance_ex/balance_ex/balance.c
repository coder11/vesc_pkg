#include "balance.h"
#include "conf/datatypes.h"

#include "biquad.h"
#include "pt1.h"
#include "ui_data.h"

#include <math.h>
#include <string.h>
#include "util.h"
#include "data.h"

void configure(data *d) {
	// Set calculated values from config
	d->loop_time_seconds = 1.0 / d->balance_conf.hertz;

	d->motor_timeout_seconds = d->loop_time_seconds * 20; // Times 20 for a nice long grace period

	d->startup_step_size = d->balance_conf.startup_speed / d->balance_conf.hertz;
	d->tiltback_duty_step_size = d->balance_conf.tiltback_duty_speed / d->balance_conf.hertz;
	d->tiltback_hv_step_size = d->balance_conf.tiltback_hv_speed / d->balance_conf.hertz;
	d->tiltback_lv_step_size = d->balance_conf.tiltback_lv_speed / d->balance_conf.hertz;
	d->tiltback_return_step_size = d->balance_conf.tiltback_return_speed / d->balance_conf.hertz;
	d->torquetilt_on_step_size = d->balance_conf.torquetilt_on_speed / d->balance_conf.hertz;
	d->torquetilt_off_step_size = d->balance_conf.torquetilt_off_speed / d->balance_conf.hertz;
	d->turntilt_step_size = d->balance_conf.turntilt_speed / d->balance_conf.hertz;
	d->noseangling_step_size = d->balance_conf.noseangling_speed / d->balance_conf.hertz;

	// Init Filters
	if (d->balance_conf.loop_time_filter > 0) {
		d->loop_overshoot_alpha = 2.0 * M_PI * ((float)1.0 / (float)d->balance_conf.hertz) *
				(float)d->balance_conf.loop_time_filter / (2.0 * M_PI * (1.0 / (float)d->balance_conf.hertz) *
						(float)d->balance_conf.loop_time_filter + 1.0);
	}

	if (d->balance_conf.kd_pt1_lowpass_frequency > 0) {
		d->d_pt1_lowpass_k = pt1_calculate_k(d->balance_conf.kd_pt1_lowpass_frequency, d->balance_conf.hertz);
	}

	if (d->balance_conf.kd2_pt1_lowpass_frequency > 0) {
		d->d2_pt1_lowpass_k = pt1_calculate_k(d->balance_conf.kd2_pt1_lowpass_frequency, d->balance_conf.hertz);
	}

	if (d->balance_conf.kd_pt1_highpass_frequency > 0) {
		d->d_pt1_highpass_k = pt1_calculate_k(d->balance_conf.kd_pt1_highpass_frequency, d->balance_conf.hertz);
	}

	if (d->balance_conf.torquetilt_filter > 0) { // Torquetilt Current Biquad
		float fc = d->balance_conf.torquetilt_filter / d->balance_conf.hertz;
		biquad_config(&d->torquetilt_current_biquad, BQ_LOWPASS, fc);
	}

	// Variable nose angle adjustment / tiltback (setting is per 1000erpm, convert to per erpm)
	d->tiltback_variable = d->balance_conf.tiltback_variable / 1000;
	if (d->tiltback_variable > 0) {
		// just keep max/min setpoint clamp for now
		// d->tiltback_variable_max_erpm = fabsf(d->balance_conf.setpoint_max / d->tiltback_variable);
	} else {
		d->tiltback_variable_max_erpm = 100000;
	}

	// Reset loop time variables
	d->last_time = 0.0;
	d->filtered_loop_overshoot = 0.0;

	ui_data_configure(d);
}

void reset_vars(data *d) {
	// Clear accumulated values.
	d->integral = 0;
	d->last_error = 0;
	d->integral2 = 0;
	d->d_pt1_lowpass_state = 0;
	d->d_pt1_highpass_state = 0;
	d->d2_pt1_lowpass_state = 0;
	// Set values for startup
	d->setpoint = d->pitch_angle;
	d->setpoint_target_interpolated = d->pitch_angle;
	d->setpoint_target = 0;
	d->noseangling_interpolated = 0;
	d->torquetilt_target = 0;
	d->torquetilt_interpolated = 0;
	d->torquetilt_filtered_current = 0;
	biquad_reset(&d->torquetilt_current_biquad);
	d->turntilt_target = 0;
	d->turntilt_interpolated = 0;
	d->setpointAdjustmentType = CENTERING;
	d->state = RUNNING;
	d->current_time = 0;
	d->last_time = 0;
	d->diff_time = 0;
	d->brake_timeout = 0;
	d->last_erpm = d->erpm;

	ui_data_reset(d);
}

float get_setpoint_adjustment_step_size(data *d) {
	switch(d->setpointAdjustmentType){
		case (CENTERING):
			return d->startup_step_size;
		case (TILTBACK_DUTY):
			return d->tiltback_duty_step_size;
		case (TILTBACK_HV):
			return d->tiltback_hv_step_size;
		case (TILTBACK_LV):
			return d->tiltback_lv_step_size;
		case (TILTBACK_NONE):
			return d->tiltback_return_step_size;
		default:
			;
	}
	return 0;
}

bool check_faults(data *d, bool ignoreTimers){
	// Check pitch angle
	if (fabsf(d->pitch_angle) > d->balance_conf.fault_pitch) {
		if ((1000.0 * (d->current_time - d->fault_angle_pitch_timer)) > d->balance_conf.fault_delay_pitch || ignoreTimers) {
			d->state = FAULT_ANGLE_PITCH;
			return true;
		}
	} else {
		d->fault_angle_pitch_timer = d->current_time;
	}

	// Check roll angle
	if (fabsf(d->roll_angle) > d->balance_conf.fault_roll) {
		if ((1000.0 * (d->current_time - d->fault_angle_roll_timer)) > d->balance_conf.fault_delay_roll || ignoreTimers) {
			d->state = FAULT_ANGLE_ROLL;
			return true;
		}
	} else {
		d->fault_angle_roll_timer = d->current_time;
	}

	// Check for duty
	if (d->abs_duty_cycle > d->balance_conf.fault_duty){
		if ((1000.0 * (d->current_time - d->fault_duty_timer)) > d->balance_conf.fault_delay_duty || ignoreTimers) {
			d->state = FAULT_DUTY;
			return true;
		}
	} else {
		d->fault_duty_timer = d->current_time;
	}

	return false;
}

void calculate_setpoint_target(data *d) {
	if (d->setpointAdjustmentType == CENTERING && d->setpoint_target_interpolated != d->setpoint_target) {
		// Ignore tiltback during centering sequence
		d->state = RUNNING;
	} else if (d->abs_duty_cycle > d->balance_conf.tiltback_duty) {
		if (d->erpm > 0) {
			d->setpoint_target = d->balance_conf.tiltback_duty_angle;
		} else {
			d->setpoint_target = -d->balance_conf.tiltback_duty_angle;
		}
		d->setpointAdjustmentType = TILTBACK_DUTY;
		d->state = RUNNING_TILTBACK_DUTY;
	} else if (d->abs_duty_cycle > 0.05 && VESC_IF->mc_get_input_voltage_filtered() > d->balance_conf.tiltback_hv) {
		if (d->erpm > 0){
			d->setpoint_target = d->balance_conf.tiltback_hv_angle;
		} else {
			d->setpoint_target = -d->balance_conf.tiltback_hv_angle;
		}

		d->setpointAdjustmentType = TILTBACK_HV;
		d->state = RUNNING_TILTBACK_HIGH_VOLTAGE;
	} else if (d->abs_duty_cycle > 0.05 && VESC_IF->mc_get_input_voltage_filtered() < d->balance_conf.tiltback_lv) {
		if (d->erpm > 0) {
			d->setpoint_target = d->balance_conf.tiltback_lv_angle;
		} else {
			d->setpoint_target = -d->balance_conf.tiltback_lv_angle;
		}

		d->setpointAdjustmentType = TILTBACK_LV;
		d->state = RUNNING_TILTBACK_LOW_VOLTAGE;
	} else {
		d->setpointAdjustmentType = TILTBACK_NONE;
		d->setpoint_target = 0;
		d->state = RUNNING;
	}
}

void calculate_setpoint_interpolated(data *d) {
	if (d->setpoint_target_interpolated != d->setpoint_target) {
		// If we are less than one step size away, go all the way
		if (fabsf(d->setpoint_target - d->setpoint_target_interpolated) < get_setpoint_adjustment_step_size(d)) {
			d->setpoint_target_interpolated = d->setpoint_target;
		} else if (d->setpoint_target - d->setpoint_target_interpolated > 0) {
			d->setpoint_target_interpolated += get_setpoint_adjustment_step_size(d);
		} else {
			d->setpoint_target_interpolated -= get_setpoint_adjustment_step_size(d);
		}
	}
}

void apply_noseangling(data *d){
	// Nose angle adjustment, add variable tiltback
	float noseangling_target = 0;
	// if (fabsf(d->erpm) > d->tiltback_variable_max_erpm) {
	// 	noseangling_target = fabsf(d->balance_conf.setpoint_max) * SIGN(d->erpm);
	// } else {
	    // just keep setpoint max/min clamp for now
		noseangling_target = d->tiltback_variable * d->erpm;
	//}

	if (fabsf(noseangling_target - d->noseangling_interpolated) < d->noseangling_step_size) {
		d->noseangling_interpolated = noseangling_target;
	} else if (noseangling_target - d->noseangling_interpolated > 0) {
		d->noseangling_interpolated += d->noseangling_step_size;
	} else {
		d->noseangling_interpolated -= d->noseangling_step_size;
	}

	d->setpoint += d->noseangling_interpolated;
}

void apply_torquetilt(data *d) {
	// Filter current (Biquad)
	if (d->balance_conf.torquetilt_filter > 0) {
		d->torquetilt_filtered_current = biquad_process(&d->torquetilt_current_biquad, d->motor_current);
	} else {
		d->torquetilt_filtered_current = d->motor_current;
	}

	// Wat is this line O_o
	// Take abs motor current, subtract start offset, and take the max of that with 0 to get the current above our start threshold (absolute).
	// Then multiply it by "power" to get our desired angle, and min with the limit to respect boundaries.
	// Finally multiply it by sign motor current to get directionality back
	d->torquetilt_target = fminf(fmaxf((fabsf(d->torquetilt_filtered_current) - d->balance_conf.torquetilt_start_current), 0) *
			d->balance_conf.torquetilt_strength, d->balance_conf.torquetilt_angle_limit) * SIGN(d->torquetilt_filtered_current);

	float step_size;
	if ((d->torquetilt_interpolated - d->torquetilt_target > 0 && d->torquetilt_target > 0) ||
			(d->torquetilt_interpolated - d->torquetilt_target < 0 && d->torquetilt_target < 0)) {
		step_size = d->torquetilt_off_step_size;
	} else {
		step_size = d->torquetilt_on_step_size;
	}

	if (fabsf(d->torquetilt_target - d->torquetilt_interpolated) < step_size) {
		d->torquetilt_interpolated = d->torquetilt_target;
	} else if (d->torquetilt_target - d->torquetilt_interpolated > 0) {
		d->torquetilt_interpolated += step_size;
	} else {
		d->torquetilt_interpolated -= step_size;
	}

	d->setpoint += d->torquetilt_interpolated;
}

void apply_turntilt(data *d) {
	// Calculate desired angle
	d->turntilt_target = d->abs_roll_angle_sin * d->balance_conf.turntilt_strength;

	// Apply cutzone
	if (d->abs_roll_angle < d->balance_conf.turntilt_start_angle) {
		d->turntilt_target = 0;
	}

	// Disable below erpm threshold otherwise add directionality
	if (d->abs_erpm < d->balance_conf.turntilt_start_erpm) {
		d->turntilt_target = 0;
	} else {
		d->turntilt_target *= SIGN(d->erpm);
	}

	// Apply speed scaling
	if (d->abs_erpm < d->balance_conf.turntilt_erpm_boost_end) {
		d->turntilt_target *= 1 + ((d->balance_conf.turntilt_erpm_boost / 100.0f) *
				(d->abs_erpm / d->balance_conf.turntilt_erpm_boost_end));
	} else {
		d->turntilt_target *= 1 + (d->balance_conf.turntilt_erpm_boost / 100.0f);
	}

	// Limit angle to max angle
	if (d->turntilt_target > 0) {
		d->turntilt_target = fminf(d->turntilt_target, d->balance_conf.turntilt_angle_limit);
	} else {
		d->turntilt_target = fmaxf(d->turntilt_target, -d->balance_conf.turntilt_angle_limit);
	}

	// Move towards target limited by max speed
	if (fabsf(d->turntilt_target - d->turntilt_interpolated) < d->turntilt_step_size) {
		d->turntilt_interpolated = d->turntilt_target;
	} else if (d->turntilt_target - d->turntilt_interpolated > 0) {
		d->turntilt_interpolated += d->turntilt_step_size;
	} else {
		d->turntilt_interpolated -= d->turntilt_step_size;
	}

	d->setpoint += d->turntilt_interpolated;
}

void brake(data *d) {
	// Brake timeout logic
	if (d->balance_conf.brake_timeout > 0 && (d->abs_erpm > 1 || d->brake_timeout == 0)) {
		d->brake_timeout = d->current_time + d->balance_conf.brake_timeout;
	}

	if (d->brake_timeout != 0 && d->current_time > d->brake_timeout) {
		return;
	}

	// Reset the timeout
	VESC_IF->timeout_reset();

	// Set current
	VESC_IF->mc_set_brake_current(d->balance_conf.brake_current);
}

void set_current(data *d, float current){
	// Limit current output to configured max output
	if (current > 0 && current > VESC_IF->get_cfg_float(CFG_PARAM_l_current_max)) {
		current = VESC_IF->get_cfg_float(CFG_PARAM_l_current_max);
	} else if(current < 0 && current < VESC_IF->get_cfg_float(CFG_PARAM_l_current_min)) {
		current = VESC_IF->get_cfg_float(CFG_PARAM_l_current_min);
	}

	// Reset the timeout
	VESC_IF->timeout_reset();

	// Set the current delay
	VESC_IF->mc_set_current_off_delay(d->motor_timeout_seconds);
	// Set Current
	VESC_IF->mc_set_current(current);
}

bool is_kill_switch_triggered(data *d) {
	return d->state == KILL_SWITCH_TRIGGERED;
}

void trigger_kill_switch(data *d) {
	if(d->state == KILL_SWITCH_TRIGGERED) {
		// Same as in startup
		reset_vars(d);
		d->state = FAULT_STARTUP; // Trigger a fault so we need to meet start conditions to start
		return;
	}

	if(d->abs_erpm > 2000) {
		// for safety, don't trigger the kill switch if the motor is running
		return;
	}

	d->state = KILL_SWITCH_TRIGGERED;
}

void balance_loop_tick(data *d) {
    // Update times
    d->current_time = VESC_IF->system_time();
    if (d->last_time == 0) {
        d->last_time = d->current_time;
    }

    d->diff_time = d->current_time - d->last_time;
    d->filtered_diff_time = 0.03 * d->diff_time + 0.97 * d->filtered_diff_time; // Purely a metric
    d->last_time = d->current_time;

    if (d->balance_conf.loop_time_filter > 0) {
        d->loop_overshoot = d->diff_time - (d->loop_time_seconds - roundf(d->filtered_loop_overshoot));
        d->filtered_loop_overshoot = d->loop_overshoot_alpha * d->loop_overshoot + (1.0 - d->loop_overshoot_alpha) * d->filtered_loop_overshoot;
    }

    // Set "last" values to previous loops values
    d->last_pitch_angle = d->pitch_angle;
    d->last_gyro_y = d->gyro[1];
	
    // Get the values we want
    d->motor_current = VESC_IF->mc_get_tot_current_directional_filtered();
    d->pitch_angle = RAD2DEG_f(VESC_IF->imu_get_pitch());
    d->roll_angle = RAD2DEG_f(VESC_IF->imu_get_roll());
    d->abs_roll_angle = fabsf(d->roll_angle);
    d->abs_roll_angle_sin = sinf(DEG2RAD_f(d->abs_roll_angle));
    VESC_IF->imu_get_gyro(d->gyro);
    d->duty_cycle = VESC_IF->mc_get_duty_cycle_now();
    d->abs_duty_cycle = fabsf(d->duty_cycle);
    d->erpm = VESC_IF->mc_get_rpm();
    d->abs_erpm = fabsf(d->erpm);
	ui_data_update(d);
    d->last_erpm = d->erpm;

    if(d->balance_conf.balance_enabled) {
        // Control Loop State Logic
        switch(d->state) {
        case (KILL_SWITCH_TRIGGERED):
            // Disable output
            brake(d);
            break;

        case (STARTUP):
                // Disable output
                brake(d);
                if (VESC_IF->imu_startup_done()) {
                    reset_vars(d);
                    d->state = FAULT_STARTUP; // Trigger a fault so we need to meet start conditions to start
                }
                break;

        case (RUNNING):
        case (RUNNING_TILTBACK_DUTY):
        case (RUNNING_TILTBACK_HIGH_VOLTAGE):
        case (RUNNING_TILTBACK_LOW_VOLTAGE):
            // Check for faults
            if (check_faults(d, false)) {
                break;
            }

            // Calculate setpoint and interpolation
			d->setpoint = d->balance_conf.pitch_adjustment;
			calculate_setpoint_target(d);
            calculate_setpoint_interpolated(d);
            d->setpoint += d->setpoint_target_interpolated;
			apply_noseangling(d);
            apply_torquetilt(d);
            apply_turntilt(d);

			if(d->setpoint > d->balance_conf.setpoint_max) {
				d->setpoint = d->balance_conf.setpoint_max;
			}

			if(d->setpoint < d->balance_conf.setpoint_min) {
				d->setpoint = d->balance_conf.setpoint_min;
			}

            // Calcualte error
            d->error = d->setpoint - d->pitch_angle;
            d->abs_error = fabsf(d->error);
            d->sign_error = SIGN(d->error);
            float kk = d->balance_conf.error_ln_slope;
            float dd = d->balance_conf.error_linear_limit;
            // Are we in ln already?
            if(d->abs_error > dd) {
				d->abs_error = kk * logf( (d->abs_error - dd) / kk + 1 ) + dd;
                d->error = d->sign_error * d->abs_error;
            }

            // Do PID maths
            d->proportional = d->error;
			d->exponential = d->sign_error * (expf( d->balance_conf.kexp * d->abs_error) - 1.0f);
            d->integral = d->integral + d->error;
            d->derivative = d->error - d->last_error;

            // Apply I term Filter
            if (d->balance_conf.ki_limit > 0 && fabsf(d->integral * d->balance_conf.ki) > d->balance_conf.ki_limit) {
                d->integral = d->balance_conf.ki_limit / d->balance_conf.ki * SIGN(d->integral);
            }

            // Apply D term filters
            if (d->balance_conf.kd_pt1_lowpass_frequency > 0) {
                d->derivative = pt1_process_lowpass(&d->d_pt1_lowpass_state, d->d_pt1_lowpass_k, d->derivative);
            }

            if (d->balance_conf.kd_pt1_highpass_frequency > 0){
                d->derivative = pt1_process_highpass(&d->d_pt1_highpass_state, d->d_pt1_highpass_k, d->derivative);
            }

            float resulting_pid_value;
            d->pid_value = (d->balance_conf.kp * d->proportional) + d->exponential + (d->balance_conf.ki * d->integral) + (d->balance_conf.kd * d->derivative);
            resulting_pid_value = d->pid_value;

            if (d->balance_conf.pid_mode == BALANCE_PID_MODE_ANGLE_RATE_CASCADE) {
                d->proportional2 = d->pid_value - d->gyro[1];
                d->integral2 = d->integral2 + d->proportional2;
                d->derivative2 = d->last_gyro_y - d->gyro[1];

                // Apply D term filter
                if (d->balance_conf.kd2_pt1_lowpass_frequency > 0) {
                    d->derivative2 = pt1_process_lowpass(&d->d2_pt1_lowpass_state, d->d2_pt1_lowpass_k, d->derivative2);
                }

                // Apply I term Filter
                if (d->balance_conf.ki_limit > 0 && fabsf(d->integral2 * d->balance_conf.ki2) > d->balance_conf.ki_limit) {
                    d->integral2 = d->balance_conf.ki_limit / d->balance_conf.ki2 * SIGN(d->integral2);
                }

                d->pid_value2 = (d->balance_conf.kp2 * d->proportional2) +
                        (d->balance_conf.ki2 * d->integral2) + (d->balance_conf.kd2 * d->derivative2);
                resulting_pid_value = d->pid_value2;
            }

            // Apply Booster
            if (d->abs_error > d->balance_conf.booster_angle) {
                if (d->abs_error - d->balance_conf.booster_angle < d->balance_conf.booster_ramp) {
                    resulting_pid_value += (d->balance_conf.booster_current * d->sign_error) *
                            ((d->abs_error - d->balance_conf.booster_angle) / d->balance_conf.booster_ramp);
                } else {
                    resulting_pid_value += d->balance_conf.booster_current * d->sign_error;
                }
            }

            // Output to motor
            d->last_error = d->error;
            set_current(d, resulting_pid_value);
            break;

        case (FAULT_ANGLE_PITCH):
        case (FAULT_ANGLE_ROLL):
        case (FAULT_STARTUP):
            // Check for valid startup position
            if (fabsf(d->pitch_angle) < d->balance_conf.startup_pitch_tolerance &&
                    fabsf(d->roll_angle) < d->balance_conf.startup_roll_tolerance) {
                reset_vars(d);
                break;
            }

            // Disable output
            brake(d);
            break;

        case (FAULT_DUTY):
            // We need another fault to clear duty fault.
            // Otherwise duty fault will clear itself as soon as motor pauses, then motor will spool up again.
            // Rendering this fault useless.
            check_faults(d, true);

            // Disable output
            brake(d);
            break;
        }
    }

    // Delay between loops
    VESC_IF->sleep_us((uint32_t)((d->loop_time_seconds - roundf(d->filtered_loop_overshoot)) * 1000000.0));
}
