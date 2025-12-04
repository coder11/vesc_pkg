#ifndef BALANCE_H
#define BALANCE_H

#include "conf/datatypes.h"

#include "biquad.h"
#include "pt1.h"

#include <math.h>
#include <string.h>
#include "util.h"
#include "data.h"

void configure(data *d);



float get_setpoint_adjustment_step_size(data *d);

void calculate_setpoint_target(data *d);

void calculate_setpoint_interpolated(data *d);

void apply_noseangling(data *d);

void apply_torquetilt(data *d);

void apply_turntilt(data *d);

void brake(data *d);

void set_current(data *d, float current);

void balance_loop_tick(data *d);

#endif // BALANCE_H
