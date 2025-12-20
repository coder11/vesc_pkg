#include "balance.h"
#include "fault.h"
#include "conf/datatypes.h"

#include "biquad.h"
#include "data_motor.h"
#include "pt1.h"
#include "data_ui.h"
#include "setpoint.h"

#include <math.h>
#include <stdbool.h>
#include <string.h>
#include "util.h"
#include "data.h"

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

void set_current(data *d) {
	// Limit current output to configured max output
	if (d->output_current > 0 && d->output_current > VESC_IF->get_cfg_float(CFG_PARAM_l_current_max)) {
		d->output_current = VESC_IF->get_cfg_float(CFG_PARAM_l_current_max);
	} else if(d->output_current < 0 && d->output_current < VESC_IF->get_cfg_float(CFG_PARAM_l_current_min)) {
		d->output_current = VESC_IF->get_cfg_float(CFG_PARAM_l_current_min);
	}

	// Reset the timeout
	VESC_IF->timeout_reset();

	// Set the current delay
	VESC_IF->mc_set_current_off_delay(d->motor_timeout_seconds);
	// Set Current
	VESC_IF->mc_set_current(d->output_current);
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

	// Leave the OG cascade mode as it is
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

	// Alt cascade mode with deadzone and rate P not affecting the PID output directly
	if(d->balance_conf.pid_mode == BALANCE_PID_MODE_ANGLE_RATE_CASCADE_ALT) {
		d->error2 = 0 - d->gyro[1];
		d->abs_error2 = fabs(d->error2);
		d->sign_error2 = SIGN(d->error2);
		
		// apply deadzone
		d->abs_error2 -= d->balance_conf.setpoint_speed_based_deadzone;
		clampf_min(&d->abs_error2, 0);
		d->error2 = d->sign_error2 * d->abs_error2;

		d->proportional2 = d->error2;
		d->integral2 = d->integral2 + d->error2;
		d->derivative2 = d->last_gyro_y - d->gyro[1];

		// Apply D term filter
		if (d->balance_conf.kd2_pt1_lowpass_frequency > 0) {
			d->derivative2 = pt1_process_lowpass(&d->d2_pt1_lowpass_state, d->d2_pt1_lowpass_k, d->derivative2);
		}

		// Apply I term Filter
		if (d->balance_conf.ki_limit > 0 && fabsf(d->integral2 * d->balance_conf.ki2) > d->balance_conf.ki_limit) {
			d->integral2 = d->balance_conf.ki_limit / d->balance_conf.ki2 * SIGN(d->integral2);
		}

		d->pid_value2 = d->pid_value +
			d->balance_conf.kp2 * d->proportional2 +
			d->balance_conf.ki2 * d->integral2 + 
			d->balance_conf.kd2 * d->derivative2;
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
	data_motor_update(&d->motor_data);
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
			set_current(d);
			break;

        case (RUNNING):
            // Check for faults
            if (check_faults(d, false)) {
                break;
            }

			// apply various setpoint adjustments
			d->setpoint = d->center_target;
			apply_speed_tilt(d);
			apply_accel_tilt(d);
			apply_accel2_tilt(d);
            apply_torquetilt(d);
            apply_turntilt(d);
			clampf(&d->setpoint, d->balance_conf.setpoint_min, d->balance_conf.setpoint_max);

			if(d->balance_conf.tiltback_enabled) {
				// allow tiltback to work outside of clamp
				apply_tiltback(d);
			}
			
			calculate_balance_current(d);
			set_current(d);
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

	// do it outside the loop for debugging purposes
	setpoint_spring_update(&d->setpoint_spring);
	clampf(&d->setpoint_spring.x, d->balance_conf.setpoint_min, d->balance_conf.setpoint_max);

    // Delay between loops
    VESC_IF->sleep_us((uint32_t)((d->loop_time_seconds - roundf(d->filtered_loop_overshoot)) * 1000000.0));
}
