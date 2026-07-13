#include "vesc_balance.h"

#include "balance.h"
#include "util.h"

#define MOTOR_OUTPUT_ENABLED false

void vesc_read_input(VescBalanceApp *app) {
	BalanceInput *input = &app->balance.input;

	input->current_time_s = VESC_IF->system_time();
	input->motor_current = VESC_IF->mc_get_tot_current_directional_filtered();
	input->pitch_angle = RAD2DEG_f(VESC_IF->imu_get_pitch());
	input->roll_angle = RAD2DEG_f(VESC_IF->imu_get_roll());
	VESC_IF->imu_get_gyro(input->gyro);
	input->duty_cycle = VESC_IF->mc_get_duty_cycle_now();
	input->erpm = VESC_IF->mc_get_rpm();
	input->input_voltage = VESC_IF->mc_get_input_voltage_filtered();
	input->adc1 = VESC_IF->io_read_analog(VESC_PIN_ADC1);
	input->adc2 = VESC_IF->io_read_analog(VESC_PIN_ADC2);
	if (input->adc2 < 0.0f) {
		input->adc2 = 0.0f;
	}
	input->imu_startup_done = VESC_IF->imu_startup_done();

	input->current_max = VESC_IF->get_cfg_float(CFG_PARAM_l_current_max);
	input->current_min = VESC_IF->get_cfg_float(CFG_PARAM_l_current_min);
	input->wheel_diameter = VESC_IF->get_cfg_float(CFG_PARAM_si_wheel_diameter);
	input->motor_poles = VESC_IF->get_cfg_int(CFG_PARAM_si_motor_poles);
	input->battery_cells = VESC_IF->get_cfg_int(CFG_PARAM_si_battery_cells);
}

static void vesc_apply_output(VescBalanceApp *app) {
	BalanceApp *balance = &app->balance;
	BalanceState *state = &balance->state;

	if (!MOTOR_OUTPUT_ENABLED) {
		return;
	}

	switch (balance->output) {
	case BALANCE_OUTPUT_CURRENT:
		VESC_IF->timeout_reset();
		VESC_IF->mc_set_current_off_delay(state->motor_timeout_s);
		VESC_IF->mc_set_current(state->output_current);
		break;

	case BALANCE_OUTPUT_BRAKE:
		VESC_IF->timeout_reset();
		VESC_IF->mc_set_brake_current(state->balance_conf.brake_current);
		break;

	case BALANCE_OUTPUT_NONE:
	default:
		break;
	}
}

void vesc_balance_loop(VescBalanceApp *app) {
	while (!VESC_IF->should_terminate()) {
		vesc_read_input(app);
		balance_loop_tick(&app->balance);
		vesc_apply_output(app);
		VESC_IF->sleep_us(app->balance.requested_sleep_us);
	}
}
