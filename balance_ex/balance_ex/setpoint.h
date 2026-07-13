#ifndef SETPOINT_H
#define SETPOINT_H

#include "data.h"

void apply_tiltback(BalanceApp *app);
void apply_speed_tilt(BalanceApp *app);
void apply_torquetilt(BalanceApp *app);
void apply_turntilt(BalanceApp *app);

#endif // SETPOINT_H
