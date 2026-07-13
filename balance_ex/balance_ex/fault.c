#include "fault.h"
#include "data.h"

#include <math.h>

void engage_centering(BalanceApp *app) {
	BalanceState *d = &app->state;
	reset_vars(app);
	d->setpoint = app->input.pitch_angle;
	d->state = CENTERING;
}

void engage_ready(BalanceApp *app) {
	BalanceState *d = &app->state;
	reset_vars(app);
	// Trigger a fault so we need to meet start conditions to start
	d->state = READY;
}

void engage_killspin(BalanceApp *app) {
	BalanceState *d = &app->state;

	if(d->state == KILLSPIN) {
		// allready engaged, do nothing
		return;
	}

	if(d->abs_erpm > 2000) {
		// for safety, don't trigger the kill spin if the motor is running
		return;
	}

	d->state = KILLSPIN;
}

void disengage_killspin(BalanceApp *app) {
	BalanceState *d = &app->state;

	if(d->state != KILLSPIN) {
		// allready disengaged, do nothing
		return;
	}

	engage_ready(app);
}

bool check_faults(BalanceApp *app, bool ignoreTimers){
	BalanceState *d = &app->state;
	BalanceInput *input = &app->input;

	// Check pitch angle
	if (fabsf(input->pitch_angle) > d->balance_conf.fault_pitch) {
		if ((1000.0 * (input->current_time_s - d->fault_angle_pitch_timer_s)) > d->balance_conf.fault_delay_pitch_ms || ignoreTimers) {
			d->state = FAULT_ANGLE_PITCH;
			return true;
		}
	} else {
		d->fault_angle_pitch_timer_s = input->current_time_s;
	}

	// Check roll angle
	if (fabsf(input->roll_angle) > d->balance_conf.fault_roll) {
		if ((1000.0 * (input->current_time_s - d->fault_angle_roll_timer_s)) > d->balance_conf.fault_delay_roll_ms || ignoreTimers) {
			d->state = FAULT_ANGLE_ROLL;
			return true;
		}
	} else {
		d->fault_angle_roll_timer_s = input->current_time_s;
	}

	// Check for duty
	if (d->abs_duty_cycle > d->balance_conf.fault_duty){
		if ((1000.0 * (input->current_time_s - d->fault_duty_timer_s)) > d->balance_conf.fault_delay_duty_ms || ignoreTimers) {
			d->state = FAULT_DUTY;
			return true;
		}
	} else {
		d->fault_duty_timer_s = input->current_time_s;
	}

	return false;
}
