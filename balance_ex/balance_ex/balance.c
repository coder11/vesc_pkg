#include "balance.h"
#include "fault.h"
#include "conf/datatypes.h"

#include "biquad.h"
#include "pt1.h"
#include "data_ui.h"

#include <math.h>
#include <stdbool.h>
#include <string.h>
#include "util.h"
#include "data.h"

float get_setpoint_adjustment_step_size(data *d) {
	switch(d->tiltback_type){
		case (TILTBACK_DUTY):
			return d->tiltback_duty_step_size;
		case (TILTBACK_HV):
			return d->tiltback_hv_step_size;
		case (TILTBACK_LV):
			return d->tiltback_lv_step_size;
		case (TILTBACK_BACKING_OFF):
			return d->tiltback_return_step_size;
		default:
			;
	}
	return 0;
}

void process_tiltback(data *d) {
	if (d->abs_duty_cycle > d->balance_conf.tiltback_duty) {
		if (d->erpm > 0) {
			d->tiltback_target = d->balance_conf.tiltback_duty_angle;
		} else {
			d->tiltback_target = -d->balance_conf.tiltback_duty_angle;
		}
		d->tiltback_type = TILTBACK_DUTY;
	} else if (d->abs_duty_cycle > 0.05 && VESC_IF->mc_get_input_voltage_filtered() > d->balance_conf.tiltback_hv) {
		if (d->erpm > 0){
			d->tiltback_target = d->balance_conf.tiltback_hv_angle;
		} else {
			d->tiltback_target = -d->balance_conf.tiltback_hv_angle;
		}

		d->tiltback_type = TILTBACK_HV;
	} else if (d->abs_duty_cycle > 0.05 && VESC_IF->mc_get_input_voltage_filtered() < d->balance_conf.tiltback_lv) {
		if (d->erpm > 0) {
			d->tiltback_target = d->balance_conf.tiltback_lv_angle;
		} else {
			d->tiltback_target = -d->balance_conf.tiltback_lv_angle;
		}

		d->tiltback_type = TILTBACK_LV;
	} 

	if(d->tiltback_type == TITLBACK_NONE) {
		// nothing to do, we've finished
		return;
	}

	bool has_finished = advance_interpolation(&d->tiltback_target_interpolated, d->tiltback_target, get_setpoint_adjustment_step_size(d));
	if(has_finished && d->tiltback_type == TILTBACK_BACKING_OFF) {
		// if the backing off sequence finished, we're done
		d->tiltback_type = TITLBACK_NONE;
	} else if(has_finished) {
		// proceed to backing off sequence
		d->tiltback_type = TILTBACK_BACKING_OFF;
	}

	d->setpoint += d->tiltback_target_interpolated;
}

void apply_noseangling(data *d){
	// Nose angle adjustment, add variable tiltback
	float noseangling_target = d->tiltback_variable * d->erpm;

	advance_interpolation(&d->noseangling_interpolated, noseangling_target, d->noseangling_step_size);
	d->setpoint += d->noseangling_interpolated;
}

// candidate for removal. Don't touch it for now
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
	advance_interpolation(&d->turntilt_interpolated, d->turntilt_target, d->turntilt_step_size);
	d->setpoint += d->turntilt_interpolated;
}

// Disable output and break according to configuration
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

void calculate_balance_current(data *d) {
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

	d->pid_value = (d->balance_conf.kp * d->proportional) + d->exponential + (d->balance_conf.ki * d->integral) + (d->balance_conf.kd * d->derivative);
	d->output_current = d->pid_value;

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
				d->output_current = d->pid_value2;
	}

	// Apply Booster
	if (d->abs_error > d->balance_conf.booster_angle) {
		if (d->abs_error - d->balance_conf.booster_angle < d->balance_conf.booster_ramp) {
			d->output_current += (d->balance_conf.booster_current * d->sign_error) *
					((d->abs_error - d->balance_conf.booster_angle) / d->balance_conf.booster_ramp);
		} else {
			d->output_current += d->balance_conf.booster_current * d->sign_error;
		}
	}

	d->last_error = d->error;
}

bool is_valid_startup_position(data *d, bool ignore_pitch) {
	bool is_pitch_good = ignore_pitch 
		|| fabsf(d->pitch_angle) < d->balance_conf.startup_pitch_tolerance;

	bool is_roll_good = fabsf(d->roll_angle) < d->balance_conf.startup_roll_tolerance;
	return is_pitch_good && is_roll_good;
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

    d->adc1 = VESC_IF->io_read_analog(VESC_PIN_ADC1);
    d->adc2 = VESC_IF->io_read_analog(VESC_PIN_ADC2); // Returns -1.0 if the pin is missing on the hardware
    if (d->adc2 < 0.0) {
        d->adc2 = 0.0;
    }

    if(d->balance_conf.balance_enabled) {
        // Control Loop State Logic
        switch(d->state) {
        case (KILLSPIN):
            brake(d);
            break;

        case (STARTUP):
			brake(d);
			if (VESC_IF->imu_startup_done()) {
				engage_ready(d);
			}
			break;

		// Use explicit case in case (pun intended) we would need to customize
		// Centering logic in future. E.g smooth out, use different PIDs or whatever
		case (CENTERING):
			// Check for faults in case we roll the wheel while its centering
			if (check_faults(d, false)) {
				break;
			}

			if(advance_interpolation(&d->setpoint, d->center_target, d->centering_step_size)) {
				d->state = RUNNING;
			}
			calculate_balance_current(d);
			set_current(d, d->output_current);
			break;

        case (RUNNING):
            // Check for faults
            if (check_faults(d, false)) {
                break;
            }

			// apply various setpoint adjustments
			d->setpoint = d->center_target;
			apply_noseangling(d);
            apply_torquetilt(d);
            apply_turntilt(d);
			clampf(&d->setpoint, d->balance_conf.setpoint_min, d->balance_conf.setpoint_max);

			// allow tiltback to work outside of clamp
			process_tiltback(d);
			
			calculate_balance_current(d);
			set_current(d, d->output_current);
            break;

        case (FAULT_ANGLE_PITCH):
        case (FAULT_ANGLE_ROLL):
        case (READY):
            if (is_valid_startup_position(d, false)) {
				engage_centering(d);
                break;
            }

            brake(d);
            break;

        case (FAULT_DUTY):
            // We need another fault to clear duty fault.
            // Otherwise duty fault will clear itself as soon as motor pauses, then motor will spool up again.
            // Rendering this fault useless.
            check_faults(d, true);

            brake(d);
            break;
        }
    }

    // Delay between loops
    VESC_IF->sleep_us((uint32_t)((d->loop_time_seconds - roundf(d->filtered_loop_overshoot)) * 1000000.0));
}
