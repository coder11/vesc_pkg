#ifndef SETPOINT_H
#define SETPOINT_H

#include "data.h"

typedef struct {
	// state
    float x, v, a;    // spring end coordinate, speed, acceleration
    float f_user;     // "force" applied to stream
    float f_user_sign, f_user_abs;
    
    // config
    float k, c;       // spring stiffness and damping
    float f_deadzone;
} SetpointSpring;

void apply_tiltback(data *d);
void apply_speed_tilt(data *d);
void apply_accel_tilt(data *d);
void apply_accel2_tilt(data *d);
void apply_torquetilt(data *d);
void apply_turntilt(data *d);

void setpoing_spring_reset(SetpointSpring *m);

void setpoing_spring_configure(SetpointSpring *m);

void setpoing_spring_update(SetpointSpring *m);

#endif // SETPOINT_H

