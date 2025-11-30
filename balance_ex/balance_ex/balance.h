#ifndef BALANCE_H
#define BALANCE_H

#include "conf/datatypes.h"
#include "conf/confparser.h"
#include "conf/confxml.h"
#include "conf/buffer.h"

#include "biquad.h"
#include "pt1.h"

#include <math.h>
#include <string.h>
#include "util.h"
#include "data.h"
#include "communication.h"

void configure(data *d);

void reset_vars(data *d);

float get_setpoint_adjustment_step_size(data *d);

// Fault checking order does not really matter. From a UX perspective, switch should be before angle.
bool check_faults(data *d, bool ignoreTimers);

void calculate_setpoint_target(data *d);

void calculate_setpoint_interpolated(data *d);

void apply_noseangling(data *d);

void apply_torquetilt(data *d);

void apply_turntilt(data *d);

void brake(data *d);

void set_current(data *d, float current);

bool is_kill_switch_triggered(data *d);

void trigger_kill_switch(data *d);

void balance_loop_tick(data *d);

#endif // BALANCE_H
