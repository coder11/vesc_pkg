#ifndef SETPOINT_SPRING_H
#define SETPOINT_SPRING_H

typedef struct {
	// state
    float x, v;       // spring end coordinate, speed
    float f_user;     // external "force" applied to string
    
    // config
    float dt;         // time constant between loop ticks
    float k, c;       // spring stiffness and damping
    float f_deadzone;
} SetpointSpring;

void setpoint_spring_reset(SetpointSpring *m);

void setpoint_spring_configure(SetpointSpring *m, float k, float c, float dt);

void setpoint_spring_update(SetpointSpring *m);

#endif // SETPOINT_SPRING_H

