#include "vesc_c_if.h"
#include "communication.h"
#include "balance.h"
#include "fault.h"
#include "conf/buffer.h"

bool is_killspin_engaged(BalanceState *d) {
	return d->state == KILLSPIN;
}

void trigger_killspin(BalanceApp *app) {
	BalanceState *d = &app->state;

	if(is_killspin_engaged(d)) {
		disengage_killspin(app);
	} else {
		engage_killspin(app);
	}
}

void send_realtime_data(BalanceApp *app) {
	BalanceState *d = &app->state;
	BalanceInput *input = &app->input;

	int32_t ind = 0;
	uint8_t send_buffer[100];
	buffer_append_float32_auto(send_buffer, d->pid_value, &ind);
	buffer_append_float32_auto(send_buffer, input->pitch_angle, &ind);
	buffer_append_float32_auto(send_buffer, input->roll_angle, &ind);
	buffer_append_float32_auto(send_buffer, d->diff_time_s, &ind);
	buffer_append_float32_auto(send_buffer, input->motor_current, &ind);
	buffer_append_uint16(send_buffer, d->state, &ind);
	buffer_append_float32_auto(send_buffer, d->setpoint, &ind);
	buffer_append_float32_auto(send_buffer, d->ui_data.motor_load_lowpass_state, &ind);
	buffer_append_float32_auto(send_buffer, d->ui_data.motor_accel_load_lowpass_state, &ind);
	buffer_append_uint16(send_buffer, is_killspin_engaged(d), &ind);
	buffer_append_uint16(send_buffer, d->tiltback_type, &ind);
	// UI data values
	buffer_append_float32_auto(send_buffer, d->ui_data.rpm, &ind);
	buffer_append_float32_auto(send_buffer, d->ui_data.speed_kmh, &ind);
	buffer_append_float32_auto(send_buffer, d->ui_data.voltage_lowpass_state, &ind);
	buffer_append_float32_auto(send_buffer, d->ui_data.voltage_min, &ind);
	buffer_append_float32_auto(send_buffer, d->ui_data.voltage_max, &ind);
	
	VESC_IF->send_app_data(send_buffer, ind);
}

void on_command_recieved(BalanceApp *app, unsigned char *buffer, unsigned int len) {
	if(len > 0){
		uint8_t command = buffer[0];
		if(command == BALANCE_COMMAND_GET_REALTIME_DATA) {
			send_realtime_data(app);
		} else if(command == BALANCE_COMMAND_TRIGGER_KILLSPIN) {
			trigger_killspin(app);
		} else {
			VESC_IF->printf("Unknown command received %d", command);
		}
	}
}
