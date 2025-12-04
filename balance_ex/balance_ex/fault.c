#include "fault.h"

#include <math.h>

void engage_ready(data *d) {
	reset_vars(d);
	// Trigger a fault so we need to meet start conditions to start
	d->state = READY;
}

void engage_kill_spin(data *d) {
	if(d->state == KILL_SPIN) {
		// allready engaged, do nothing
		return;
	}

	if(d->abs_erpm > 2000) {
		// for safety, don't trigger the kill spin if the motor is running
		return;
	}

	d->state = KILL_SPIN;
}

void disengage_kill_spin(data *d) {
	if(d->state != KILL_SPIN) {
		// allready disengaged, do nothing
		return;
	}

	engage_ready(d);
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