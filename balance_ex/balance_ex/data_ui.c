
#include "data.h"
#include "pt1.h"
#include <math.h>

void ui_data_configure(BalanceApp *app) {
	BalanceState *d = &app->state;
	BalanceInput *input = &app->input;

    d->ui_data.wheel_diameter = input->wheel_diameter;
    d->ui_data.motor_poles = input->motor_poles;

    float fq = 0.5;
    d->ui_data.voltage_lowpass_k = pt1_calculate_k(fq, d->balance_conf.hertz);
    d->ui_data.voltage_lowpass_state = 0;

    float motor_load_fq = 1;
    float motor_accel_load_fq = motor_load_fq;

    d->ui_data.motor_load_lowpass_k = pt1_calculate_k(motor_load_fq, d->balance_conf.hertz);
    d->ui_data.motor_load_lowpass_state = 0;

    d->ui_data.motor_accel_load_lowpass_k = pt1_calculate_k(motor_accel_load_fq, d->balance_conf.hertz);
    d->ui_data.motor_accel_load_lowpass_state = 0;

    // Calculate voltage limits from battery cell count
    // 2.8V per cell minimum, 4.3V per cell maximum
    int battery_cells = input->battery_cells;
    d->ui_data.voltage_min = 2.8f * battery_cells;
    d->ui_data.voltage_max = 4.3f * battery_cells;
}

void ui_data_reset(BalanceApp *app) {
	BalanceState *d = &app->state;

    d->ui_data.voltage_lowpass_state = 0;
    d->ui_data.motor_load_lowpass_state = 0;
    d->ui_data.motor_accel_load_lowpass_state = 0;

    d->erpm_accel = 0;
	d->motor_load = 0;
	d->motor_accel_load = 0;
}

void ui_data_update(BalanceApp *app) {
	BalanceState *d = &app->state;
	BalanceInput *input = &app->input;

    // speed in km/h
    d->ui_data.rpm = input->erpm * 2.0 / d->ui_data.motor_poles;
    float circumference = d->ui_data.wheel_diameter * M_PI;
    float speed_ms = d->ui_data.rpm * circumference / 60.0;
    d->ui_data.speed_kmh = speed_ms * 3.6;

    // voltage
    d->ui_data.voltage = input->input_voltage;
    d->ui_data.voltage_lowpass_state = pt1_process_lowpass(&d->ui_data.voltage_lowpass_state, d->ui_data.voltage_lowpass_k, d->ui_data.voltage);

    // experimental values
	d->erpm_accel = (d->diff_time_s > 0) ? (input->erpm - d->last_erpm) / d->diff_time_s : 0.0;

    // Current per ERPM and per ERPM acceleration (avoid division by zero / tiny values)
    // multiply by 1000 because erpms are in thousands
    if (fabsf(input->erpm) > 0.01f) {
        d->motor_load = fabsf(input->motor_current / input->erpm * 1000.0f);
    } else {
        d->motor_load = 0.0f;
    }

    if (fabsf(d->erpm_accel) > 0.01f) {
        d->motor_accel_load = fabsf(input->motor_current / d->erpm_accel * 1000.0f);
    } else {
        d->motor_accel_load = 0.0f;
    }

    // Filter motor_load and motor_accel_load
    d->ui_data.motor_load_lowpass_state = pt1_process_lowpass(&d->ui_data.motor_load_lowpass_state, d->ui_data.motor_load_lowpass_k, d->motor_load);
    d->ui_data.motor_accel_load_lowpass_state = pt1_process_lowpass(&d->ui_data.motor_accel_load_lowpass_state, d->ui_data.motor_accel_load_lowpass_k, d->motor_accel_load);
}
