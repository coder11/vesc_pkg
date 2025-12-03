#include "vesc_c_if.h"
#include "communication.h"
#include "balance.h"
#include "conf/buffer.h"

void send_realtime_data(data *d) {
	int32_t ind = 0;
	uint8_t send_buffer[100];
	buffer_append_float32_auto(send_buffer, d->pid_value, &ind);
	buffer_append_float32_auto(send_buffer, d->pitch_angle, &ind);
	buffer_append_float32_auto(send_buffer, d->roll_angle, &ind);
	buffer_append_float32_auto(send_buffer, d->diff_time, &ind);
	buffer_append_float32_auto(send_buffer, d->motor_current, &ind);
	buffer_append_uint16(send_buffer, d->state, &ind);
	buffer_append_uint16(send_buffer, d->switch_state, &ind);
	buffer_append_float32_auto(send_buffer, d->adc1, &ind);
	buffer_append_float32_auto(send_buffer, d->adc2, &ind);
	buffer_append_float32_auto(send_buffer, d->setpoint, &ind);
	buffer_append_float32_auto(send_buffer, d->ui_data.motor_load_lowpass_state, &ind);
	buffer_append_float32_auto(send_buffer, d->ui_data.motor_accel_load_lowpass_state, &ind);
	buffer_append_uint16(send_buffer, is_kill_switch_triggered(d), &ind);
	// UI data values
	buffer_append_float32_auto(send_buffer, d->ui_data.speed_kmh, &ind);
	buffer_append_float32_auto(send_buffer, d->ui_data.voltage_lowpass_state, &ind);
	buffer_append_float32_auto(send_buffer, d->ui_data.voltage_min, &ind);
	buffer_append_float32_auto(send_buffer, d->ui_data.voltage_max, &ind);
	
	VESC_IF->send_app_data(send_buffer, ind);
}

void on_command_recieved(data* d, unsigned char *buffer, unsigned int len) {
	if(len > 0){
		uint8_t command = buffer[0];
		if(command == BALANCE_COMMAND_GET_REALTIME_DATA) {
			send_realtime_data(d);
		} else if(command == BALANCE_COMMAND_KILL_SWITCH_TRIGGER) {
			trigger_kill_switch(d);
		} else {
			VESC_IF->printf("Unknown command received %d", command);
		}
	}
}