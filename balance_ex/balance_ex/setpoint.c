#include "setpoint.h"
#include "util.h"
#include "biquad.h"
#include "vesc_c_if.h"

#include <math.h>
#include <stdbool.h>

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

void apply_tiltback(data *d) {
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
		d->tiltback_target = 0;
	} else {
		// TODO: it should not have been under if
		// but the wheel is jerky otherwise
		d->setpoint += d->tiltback_target_interpolated;
	}
}

void apply_speed_tilt(data *d){
	// TODO:: consider using sma value
	float effective_erpm = d->motor_data.erpm_abs - d->balance_conf.setpoint_speed_based_deadzone;
	clampf_min(&effective_erpm, 0);
	effective_erpm = effective_erpm * d->motor_data.erpm_sign;

	// Setting is per 1000 ERPM/s, convert to per ERPM/s
	float k = d->balance_conf.setpoint_speed_based / 1000;
	d->setpoint += k * effective_erpm;
}

void apply_accel_tilt(data *d){
	float effective_accel = d->motor_data.accel_abs - d->balance_conf.setpoint_accel_based_deadzone;
	clampf_min(&effective_accel, 0);

	float k = (d->motor_data.accel_sign > 0)
		? d->balance_conf.setpoint_accel_based_fwd
		: d->balance_conf.setpoint_accel_based_bwd;

	float apply_accel_tilt_target = k * effective_accel * d->motor_data.accel_sign;
	advance_interpolation(&d->setpoint_accel_based_interpolated, apply_accel_tilt_target, d->setpoint_accel_based_step_size);
	d->setpoint += d->setpoint_accel_based_interpolated;
}

void apply_accel2_tilt(data *d){
	float effective_accel2 = d->motor_data.accel2_abs - d->balance_conf.setpoint_accel2_based_deadzone;
	clampf_min(&effective_accel2, 0);

	float k = (d->motor_data.accel2_sign > 0)
		? d->balance_conf.setpoint_accel2_based_fwd
		: d->balance_conf.setpoint_accel2_based_bwd;

	float apply_accel2_tilt_target = k * effective_accel2 * d->motor_data.accel2_sign;
	advance_interpolation(&d->setpoint_accel2_based_interpolated, apply_accel2_tilt_target, d->setpoint_accel2_based_step_size);
	d->setpoint += d->setpoint_accel2_based_interpolated;
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

void setpoing_spring_reset(SetpointSpring *data) {
	data->x = 0;
	data->a = 0;
	data->v = 0;
	data->f_user = 0;
	data->f_user_sign = 1;
	data->f_user_abs = 0;
}

void setpoing_spring_configure(SetpointSpring *data) {
	data->k = 1;
	data->c = 2;

	data->f_deadzone = 1;
}

void setpoing_spring_update(SetpointSpring *data) {
	float f_eff = data->f_user_sign * max(data->f_user_abs - data->f_deadzone, 0);
	float f_spring = data->k * data->x;
	float f_damp = data->c * data->v;

	data->a = f_eff - f_spring - f_damp;

	// treat dt as 1 (the same way as in the balance loop)
	data->v += data->a ;
	data->x += data->v;
}