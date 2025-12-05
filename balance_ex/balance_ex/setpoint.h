#ifndef SETPOINT_H
#define SETPOINT_H

#include "data.h"

float get_setpoint_adjustment_step_size(data *d);
void process_tiltback(data *d);
void apply_noseangling(data *d);
void apply_torquetilt(data *d);
void apply_turntilt(data *d);

#endif // SETPOINT_H

