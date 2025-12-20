#ifndef SETPOINT_SPRING_H
#define SETPOINT_SPRING_H

typedef struct {
	// state
    float x, v, a;    // spring end coordinate, speed, acceleration
    float f_user;     // "force" applied to stream
    
    // config
    float k, c;       // spring stiffness and damping
    float f_deadzone;
} SetpointSpring;

void setpoint_spring_reset(SetpointSpring *m);

void setpoint_spring_configure(SetpointSpring *m, float k, float c);

void setpoint_spring_update(SetpointSpring *m);

#endif // SETPOINT_SPRING_H

