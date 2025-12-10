#include "data_motor.h"
#include "util.h"
#include "vesc_c_if.h"
#include <math.h>
#include <string.h>

void data_motor_reset(DataMotor *m) {
    m->erpm = 0;
    m->erpm_abs = 0;
    m->erpm_sign = 0;
    m->erpm_last = 0;

    m->erpm_sma_size = 0;
    m->erpm_sma_buffer_ix = 0;
    m->erpm_sma = 0;
    m->erpm_sma_last = 0;
    memset(m->erpm_sma_buffer, 0, sizeof(m->erpm_sma_buffer));

    m->accel = 0;
    m->accel_abs = 0;
    m->accel_sign = 0;
    m->accel_last = 0;
    m->accel2 = 0;
}

void data_motor_configure(DataMotor *m) {
    m->erpm_sma_size = 40;
    m->erpm_sma_buffer_ix = 0;
    m->erpm_sma = 0;
    m->erpm_sma_last = 0;
}

void data_motor_update(DataMotor *m) {
    // update all `last` values 
    m->erpm_last = m->erpm;
    m->erpm_sma_last = m->erpm_sma;
    m->accel_last = m->accel;

    // get current data from VESC
    m->erpm = VESC_IF->mc_get_rpm();

    m->erpm_abs = fabsf(m->erpm);
    m->erpm_sign = SIGN(m->erpm);

    // Inefficient and lacks edge case handling but should work
    // A tiny lag in erpm values shouldn't be noticable at the very start
    m->erpm_sma_buffer[m->erpm_sma_buffer_ix] = m->erpm;
    float sum = 0;
    for (int i = 0; i < m->erpm_sma_size; i++) {
        sum += m->erpm_sma_buffer[i];
    }
    m->erpm_sma = sum / m->erpm_sma_size;
    m->erpm_sma_buffer_ix = (m->erpm_sma_buffer_ix + 1) % m->erpm_sma_size;

    m->erpm_sma_abs = fabsf(m->erpm_sma);
    m->erpm_sma_sign = SIGN(m->erpm_sma);

    m->accel = m->erpm_sma - m->erpm_sma_last;
    m->accel_abs = fabsf(m->accel);
    m->accel_sign = SIGN(m->accel);
    m->accel2 = m->accel - m->accel_last;
}


