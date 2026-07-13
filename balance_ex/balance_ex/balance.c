#include "balance.h"
#include "fault.h"
#include "conf/datatypes.h"

#include "biquad.h"
#include "pt1.h"
#include "data_ui.h"
#include "setpoint.h"

#include <math.h>
#include <stdbool.h>
#include <string.h>
#include "util.h"
#include "data.h"

// Disable output and break according to configuration
void brake(BalanceApp *app) {
	BalanceState *d = &app->state;
	BalanceInput *input = &app->input;

	// Brake timeout logic
	if (d->balance_conf.brake_timeout_s > 0 && (d->abs_erpm > 1 || d->brake_timeout_s == 0)) {
		d->brake_timeout_s = input->current_time_s + d->balance_conf.brake_timeout_s;
	}

	if (d->brake_timeout_s != 0 && input->current_time_s > d->brake_timeout_s) {
		return;
	}

	app->output = BALANCE_OUTPUT_BRAKE;
}

void set_current(BalanceApp *app) {
	BalanceState *d = &app->state;
	BalanceInput *input = &app->input;

	// Limit current output to configured max output
	if (d->output_current > 0 && d->output_current > input->current_max) {
		d->output_current = input->current_max;
	} else if(d->output_current < 0 && d->output_current < input->current_min) {
		d->output_current = input->current_min;
	}

	app->output = BALANCE_OUTPUT_CURRENT;
}

void calculate_balance_current(BalanceApp *app) {
	BalanceState *d = &app->state;
	BalanceInput *input = &app->input;

	// Calcualte error
	d->error = d->setpoint - input->pitch_angle;
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
		d->proportional2 = d->pid_value - input->gyro[1];
		d->integral2 = d->integral2 + d->proportional2;
		d->derivative2 = d->last_gyro_y - input->gyro[1];

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

bool is_valid_startup_position(BalanceApp *app, bool ignore_pitch) {
	BalanceState *d = &app->state;
	BalanceInput *input = &app->input;

	bool is_pitch_good = ignore_pitch
		|| fabsf(input->pitch_angle) < d->balance_conf.startup_pitch_tolerance;

	bool is_roll_good = fabsf(input->roll_angle) < d->balance_conf.startup_roll_tolerance;
	return is_pitch_good && is_roll_good;
}

void balance_loop_tick(BalanceApp *app) {
	BalanceState *d = &app->state;
	BalanceInput *input = &app->input;

	app->output = BALANCE_OUTPUT_NONE;

    // Update times
	if (d->last_time_s == 0) {
		d->last_time_s = input->current_time_s;
    }

	d->diff_time_s = input->current_time_s - d->last_time_s;
	d->filtered_diff_time_s = 0.03 * d->diff_time_s + 0.97 * d->filtered_diff_time_s; // Purely a metric
	d->last_time_s = input->current_time_s;

	if (d->balance_conf.loop_time_filter > 0) {
		d->loop_overshoot_s = d->diff_time_s - (d->loop_time_s - roundf(d->filtered_loop_overshoot_s));
		d->filtered_loop_overshoot_s = d->loop_overshoot_alpha * d->loop_overshoot_s + (1.0 - d->loop_overshoot_alpha) * d->filtered_loop_overshoot_s;
    }

	// Update values derived from the current input snapshot.
	d->abs_roll_angle = fabsf(input->roll_angle);
    d->abs_roll_angle_sin = sinf(DEG2RAD_f(d->abs_roll_angle));
	d->abs_duty_cycle = fabsf(input->duty_cycle);
	d->abs_erpm = fabsf(input->erpm);
	ui_data_update(app);
	d->last_erpm = input->erpm;

    if(d->balance_conf.balance_enabled) {
        // Control Loop State Logic
        switch(d->state) {
        case (KILLSPIN):
            brake(app);
            break;

        case (STARTUP):
			brake(app);
			if (input->imu_startup_done) {
				engage_ready(app);
			}
			break;

		// Use explicit case in case (pun intended) we would need to customize
		// Centering logic in future. E.g smooth out, use different PIDs or whatever
		case (CENTERING):
			// Check for faults in case we roll the wheel while its centering
			if (check_faults(app, false)) {
				break;
			}

			if(advance_interpolation(&d->setpoint, d->center_target, d->centering_step_size)) {
				d->state = RUNNING;
			}
			calculate_balance_current(app);
			set_current(app);
			break;

        case (RUNNING):
            // Check for faults
            if (check_faults(app, false)) {
                break;
            }

			// apply various setpoint adjustments
			d->setpoint = d->center_target;
			apply_speed_tilt(app);
            apply_torquetilt(app);
            apply_turntilt(app);
			clampf(&d->setpoint, d->balance_conf.setpoint_min, d->balance_conf.setpoint_max);

			if(d->balance_conf.tiltback_enabled) {
				// allow tiltback to work outside of clamp
				apply_tiltback(app);
			}

			calculate_balance_current(app);
			set_current(app);
            break;

        case (FAULT_ANGLE_PITCH):
        case (FAULT_ANGLE_ROLL):
        case (READY):
            if (is_valid_startup_position(app, false)) {
				engage_centering(app);
                break;
            }

            brake(app);
            break;

        case (FAULT_DUTY):
            // We need another fault to clear duty fault.
            // Otherwise duty fault will clear itself as soon as motor pauses, then motor will spool up again.
            // Rendering this fault useless.
            check_faults(app, true);

            brake(app);
            break;
        }
    }

	d->last_pitch_angle = input->pitch_angle;
	d->last_gyro_y = input->gyro[1];
	app->requested_sleep_us = (uint32_t)((d->loop_time_s -
			roundf(d->filtered_loop_overshoot_s)) * 1000000.0f);
}
