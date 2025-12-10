#ifndef DATA_MOTOR_H
#define DATA_MOTOR_H

#define ERPM_SMA_BUFFER_MAX_SIZE 200

typedef struct {
    float erpm;
    float erpm_abs;
    float erpm_sign;
    float erpm_last;

    float erpm_sma_buffer[ERPM_SMA_BUFFER_MAX_SIZE];
    int erpm_sma_size;
    int erpm_sma_buffer_ix;
    float erpm_sma;
    float erpm_sma_abs;
    float erpm_sma_sign;
    float erpm_sma_last;

    float accel;
    float accel_abs;
    float accel_sign;
    float accel_last;
    float accel2;
} DataMotor;

void data_motor_reset(DataMotor *m);

void data_motor_configure(DataMotor *m);

void data_motor_update(DataMotor *m);

#endif // DATA_MOTOR_H

