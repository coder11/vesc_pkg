#ifndef SETPOINT_H
#define SETPOINT_H

#include "data.h"

void apply_tiltback(data *d);
void apply_speed_tilt(data *d);
void apply_torquetilt(data *d);
void apply_turntilt(data *d);

// spring mechanic impact
void apply_accel_impact(data *d);
void apply_rpm_accel_impact(data *d);
void apply_rpm_accel2_impact(data *d);

// candidates for removal
void apply_accel_tilt(data *d);
void apply_accel2_tilt(data *d);

#endif // SETPOINT_H

