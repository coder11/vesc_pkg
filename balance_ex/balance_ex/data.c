#include "data.h"
#include "data_motor.h"
#include "data_ui.h"
#include "setpoint.h"
#include "util.h"
#include "math.h"
#include "pt1.h"

void reset_vars(data *d) {
	// Clear accumulated values.
	d->integral = 0;
	d->last_error = 0;
	d->last_error2 = 0;
	d->integral2 = 0;
	d->d_pt1_lowpass_state = 0;
	d->d_pt1_highpass_state = 0;
	d->d2_pt1_lowpass_state = 0;
	
	// Set values for centering
	// We assume centering is about to start
	// Begin the process starting from the current pitch angle up to d->balance_conf.pitch_adjustment
	// TOOD:: consider moving this part into a more appropriate place
	d->state = CENTERING;
	d->setpoint = d->pitch_angle;
	
	d->tiltback_type = TITLBACK_NONE;
	d->tiltback_target_interpolated = 0;
	d->tiltback_target = 0;

	d->setpoint_speed_based_interpolated = 0;
	d->setpoint_accel_based_interpolated = 0;
	d->setpoint_accel2_based_interpolated = 0;
	d->torquetilt_target = 0;
	d->torquetilt_interpolated = 0;
	d->torquetilt_filtered_current = 0;
	biquad_reset(&d->torquetilt_current_biquad);
	d->turntilt_target = 0;
	d->turntilt_interpolated = 0;
	d->current_time = 0;
	d->last_time = 0;
	d->diff_time = 0;
	d->brake_timeout = 0;
	d->last_erpm = d->erpm;

	ui_data_reset(d);
	data_motor_reset(&d->motor_data);
	setpoint_spring_reset(&d->setpoint_spring);
}

void configure(data *d) {
	// Set calculated values from config
	d->loop_time_seconds = 1.0 / d->balance_conf.hertz;

	d->motor_timeout_seconds = d->loop_time_seconds * 20; // Times 20 for a nice long grace period

	d->center_target = d->balance_conf.setpoint_constant;
	d->centering_step_size = d->balance_conf.startup_speed / d->balance_conf.hertz;
	d->tiltback_duty_step_size = d->balance_conf.tiltback_duty_speed / d->balance_conf.hertz;
	d->tiltback_hv_step_size = d->balance_conf.tiltback_hv_speed / d->balance_conf.hertz;
	d->tiltback_lv_step_size = d->balance_conf.tiltback_lv_speed / d->balance_conf.hertz;
	d->tiltback_return_step_size = d->balance_conf.tiltback_return_speed / d->balance_conf.hertz;
	d->torquetilt_on_step_size = d->balance_conf.torquetilt_on_speed / d->balance_conf.hertz;
	d->torquetilt_off_step_size = d->balance_conf.torquetilt_off_speed / d->balance_conf.hertz;
	d->turntilt_step_size = d->balance_conf.turntilt_speed / d->balance_conf.hertz;
	d->setpoint_speed_based_step_size = d->balance_conf.setpoint_change_rate / d->balance_conf.hertz;
	d->setpoint_accel_based_step_size = d->balance_conf.setpoint_change_rate / d->balance_conf.hertz;
	d->setpoint_accel2_based_step_size = d->balance_conf.setpoint_change_rate / d->balance_conf.hertz;

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

	// Reset loop time variables
	d->last_time = 0.0;
	d->filtered_loop_overshoot = 0.0;

	ui_data_configure(d);
	
	int erpm_sma_size = d->balance_conf.erpm_sma_size;
	clamp(&erpm_sma_size, 1, ERPM_SMA_BUFFER_MAX_SIZE);
	data_motor_configure(&d->motor_data, erpm_sma_size);
	setpoint_spring_configure(&d->setpoint_spring, d->balance_conf.setpoint_spring_k, d->balance_conf.setpoint_spring_c);
}