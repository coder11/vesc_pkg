#include "data_motor.h"
#include "util.h"
#include "vesc_c_if.h"
#include "pt1.h"
#include <math.h>
#include <string.h>

void data_motor_reset(DataMotor *m) {
    m->erpm = 0;
    m->erpm_abs = 0;
    m->erpm_sign = 0;
    m->erpm_last = 0;

    m->erpm_pt1_state = 0;
    m->erpm_pt1 = 0;
    m->erpm_pt1_last = 0;

    m->accel = 0;
    m->accel_abs = 0;
    m->accel_sign = 0;
    m->accel_last = 0;
    m->accel2 = 0;
    m->accel2_abs = 0;
    m->accel2_sign = 0;
}

void data_motor_configure(DataMotor *m, float accel_pt1_k) {
    m->erpm_pt1_state = 0;
    m->erpm_pt1 = 0;
    m->erpm_pt1_last = 0;
    m->erpm_pt1_k = accel_pt1_k;
}

void data_motor_update(DataMotor *m) {
    // update all `last` values 
    m->erpm_last = m->erpm;
    m->erpm_pt1_last = m->erpm_pt1;
    m->accel_last = m->accel;

    // get current data from VESC
    m->erpm = VESC_IF->mc_get_rpm();

    m->erpm_abs = fabsf(m->erpm);
    m->erpm_sign = SIGN(m->erpm);

    m->erpm_pt1 = pt1_process_lowpass(&m->erpm_pt1_state, m->erpm_pt1_k, m->erpm);
    m->erpm_pt1_abs = fabsf(m->erpm_pt1);
    m->erpm_pt1_sign = SIGN(m->erpm_pt1);

    m->accel = m->erpm_pt1 - m->erpm_pt1_last;
    m->accel_abs = fabsf(m->accel);
    m->accel_sign = SIGN(m->accel);
    
    m->accel2 = m->accel - m->accel_last;
    m->accel2_abs = fabsf(m->accel2);
    m->accel2_sign = SIGN(m->accel2);
}


