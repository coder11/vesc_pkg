#ifndef DATA_MOTOR_H
#define DATA_MOTOR_H


typedef struct {
    float erpm;
    float erpm_abs;
    float erpm_sign;
    float erpm_last;

    float erpm_pt1_k;
    float erpm_pt1_state;
    float erpm_pt1;
    float erpm_pt1_abs;
    float erpm_pt1_sign;
    float erpm_pt1_last;

    float accel;
    float accel_abs;
    float accel_sign;
    float accel_last;
    float accel2;
    float accel2_abs;
    float accel2_sign;
} DataMotor;

void data_motor_reset(DataMotor *m);

void data_motor_configure(DataMotor *m, float accel_pt1_k);

void data_motor_update(DataMotor *m);

#endif // DATA_MOTOR_H

