
#include "data.h"
#include "pt1.h"
#include <math.h>

void ui_data_configure(data *d) {
    d->ui_data.wheel_diameter = VESC_IF->get_cfg_float(CFG_PARAM_si_wheel_diameter);
    d->ui_data.motor_poles = VESC_IF->get_cfg_float(CFG_PARAM_si_motor_poles);

    float fq = 0.5;
    d->ui_data.voltage_lowpass_k = pt1_calculate_k(fq, d->balance_conf.hertz);
    d->ui_data.voltage_lowpass_state = 0;

    // Calculate voltage limits from battery cell count
    // 2.8V per cell minimum, 4.3V per cell maximum
    int battery_cells = VESC_IF->get_cfg_int(CFG_PARAM_si_battery_cells);
    d->ui_data.voltage_min = 2.8f * battery_cells;
    d->ui_data.voltage_max = 4.3f * battery_cells;
}

void ui_data_reset(data *d) {
    d->ui_data.voltage_lowpass_state = 0;

    d->erpm_accel = 0;
	d->motor_load = 0;
	d->motor_accel_load = 0;
}

void ui_data_update(data *d) {
    // speed in km/h
    float rpm = d->erpm * 2 / d->ui_data.motor_poles;
    float circumference = d->ui_data.wheel_diameter * M_PI;
    float speed_ms = rpm * circumference / 60.0;
    d->ui_data.speed_kmh = speed_ms * 3.6;

    // voltage
    d->ui_data.voltage = VESC_IF->mc_get_input_voltage_filtered();
    d->ui_data.voltage_lowpass_state = pt1_process_lowpass(&d->ui_data.voltage_lowpass_state, d->ui_data.voltage_lowpass_k, d->ui_data.voltage);

    // experimental values
    d->erpm_accel = (d->diff_time > 0) ? (d->erpm - d->last_erpm) / d->diff_time : 0.0;

    // Current per ERPM and per ERPM acceleration (avoid division by zero / tiny values)
    // multiply by 1000 because erpms are in thousands
    if (fabsf(d->erpm) > 0.01f) {
        d->motor_load = fabsf(d->motor_current / d->erpm * 1000.0);
    } else {
        d->motor_load = 0.0f;
    }

    if (fabsf(d->erpm_accel) > 0.01f) {
        d->motor_accel_load = fabsf(d->motor_current / d->erpm_accel * 1000.0);
    } else {
        d->motor_accel_load = 0.0f;
    }    
}