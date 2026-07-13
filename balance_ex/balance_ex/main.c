/*
    Copyright 2019 - 2022 Mitch Lustig
	Copyright 2022 Benjamin Vedder	benjamin@vedder.se

	This file is part of the VESC firmware.

	The VESC firmware is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    The VESC firmware is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "balance.h"
#include "vesc_c_if.h"

#include "conf/datatypes.h"
#include "conf/confparser.h"
#include "conf/confxml.h"

#include "data.h"
#include "communication.h"
#include "vesc_balance.h"

HEADER

// Beeper on servo/PPM pin (active buzzer). Same IO path as float package beeper.
// Passive-buzzer PWM is not exposed via vesc_c_if; use GPIO only here.
static const VESC_PIN buzzer_pin = VESC_PIN_PPM;

static void buzzer_on(void) {
	VESC_IF->io_set_mode(buzzer_pin, VESC_PIN_MODE_OUTPUT);
	VESC_IF->io_write(buzzer_pin, 1);
}

static void buzzer_off(void) {
	VESC_IF->io_write(buzzer_pin, 0);
}

static void beep_ms(int duration_ms) {
	buzzer_on();
	VESC_IF->sleep_ms(duration_ms);
	buzzer_off();
}


static void balance_thd(void *arg) {
	VescBalanceApp *app = (VescBalanceApp*)arg;

	beep_ms(100);
	VESC_IF->sleep_ms(50);
	beep_ms(100);

	vesc_balance_loop(app);
}

static VescBalanceApp *vesc_app_from_arg(void) {
	return (VescBalanceApp*)ARG;
}

static BalanceApp *balance_app_from_arg(void) {
	return &vesc_app_from_arg()->balance;
}

// Handler for incoming app commands
static void on_command_recieved_handler(unsigned char *buffer, unsigned int len) {
	on_command_recieved(balance_app_from_arg(), buffer, len);
}

static lbm_value ext_get_proportional(lbm_value *args, lbm_uint argn) {
	(void)args;
	(void)argn;
	BalanceState *d = &balance_app_from_arg()->state;
	return VESC_IF->lbm_enc_float(d->proportional * d->balance_conf.kp);
}

static lbm_value ext_get_proportional2(lbm_value *args, lbm_uint argn) {
	(void)args;
	(void)argn;
	BalanceState *d = &balance_app_from_arg()->state;
	return VESC_IF->lbm_enc_float(d->proportional2 * d->balance_conf.kp2);
}

static lbm_value ext_get_integral(lbm_value *args, lbm_uint argn) {
	(void)args;
	(void)argn;
	BalanceState *d = &balance_app_from_arg()->state;
	return VESC_IF->lbm_enc_float(d->integral * d->balance_conf.ki);
}

static lbm_value ext_get_integral2(lbm_value *args, lbm_uint argn) {
	(void)args;
	(void)argn;
	BalanceState *d = &balance_app_from_arg()->state;
	return VESC_IF->lbm_enc_float(d->integral2 * d->balance_conf.ki2);
}

static lbm_value ext_get_derivative(lbm_value *args, lbm_uint argn) {
	(void)args;
	(void)argn;
	BalanceState *d = &balance_app_from_arg()->state;
	return VESC_IF->lbm_enc_float(d->derivative * d->balance_conf.kd);
}

static lbm_value ext_get_derivative2(lbm_value *args, lbm_uint argn) {
	(void)args;
	(void)argn;
	BalanceState *d = &balance_app_from_arg()->state;
	return VESC_IF->lbm_enc_float(d->derivative2 * d->balance_conf.kd2);
}

static lbm_value ext_get_pid_value(lbm_value *args, lbm_uint argn) {
	(void)args;
	(void)argn;
	BalanceState *d = &balance_app_from_arg()->state;
	return VESC_IF->lbm_enc_float(d->pid_value);
}

static lbm_value ext_get_pid_rate_value(lbm_value *args, lbm_uint argn) {
	(void)args;
	(void)argn;
	BalanceState *d = &balance_app_from_arg()->state;
	return VESC_IF->lbm_enc_float(d->pid_value2);
}

static lbm_value ext_get_erpm_accel(lbm_value *args, lbm_uint argn) {
	(void)args;
	(void)argn;
	BalanceState *d = &balance_app_from_arg()->state;
	return VESC_IF->lbm_enc_float(d->erpm_accel);
}

static lbm_value ext_get_motor_load(lbm_value *args, lbm_uint argn) {
	(void)args;
	(void)argn;
	BalanceState *d = &balance_app_from_arg()->state;
	return VESC_IF->lbm_enc_float(d->motor_load);
}

static lbm_value ext_get_motor_accel_load(lbm_value *args, lbm_uint argn) {
	(void)args;
	(void)argn;
	BalanceState *d = &balance_app_from_arg()->state;
	return VESC_IF->lbm_enc_float(d->motor_accel_load);
}

static lbm_value ext_get_voltage_filtered(lbm_value *args, lbm_uint argn) {
	(void)args;
	(void)argn;
	BalanceState *d = &balance_app_from_arg()->state;
	return VESC_IF->lbm_enc_float(d->ui_data.voltage_lowpass_state);
}

static lbm_value ext_get_motor_load_filtered(lbm_value *args, lbm_uint argn) {
	(void)args;
	(void)argn;
	BalanceState *d = &balance_app_from_arg()->state;
	return VESC_IF->lbm_enc_float(d->ui_data.motor_load_lowpass_state);
}

static lbm_value ext_get_motor_accel_load_filtered(lbm_value *args, lbm_uint argn) {
	(void)args;
	(void)argn;
	BalanceState *d = &balance_app_from_arg()->state;
	return VESC_IF->lbm_enc_float(d->ui_data.motor_accel_load_lowpass_state);
}

static lbm_value ext_get_rpm(lbm_value *args, lbm_uint argn) {
	(void)args;
	(void)argn;
	BalanceState *d = &balance_app_from_arg()->state;
	return VESC_IF->lbm_enc_float(d->ui_data.rpm);
}

// These functions are used to send the config page to VESC Tool
// and to make persistent read and write work
static int get_cfg(uint8_t *buffer, bool is_default) {
	BalanceState *d = &balance_app_from_arg()->state;
	balance_config *cfg = VESC_IF->malloc(sizeof(balance_config));

	*cfg = d->balance_conf;

	if (is_default) {
		confparser_set_defaults_balance_config(cfg);
	}

	int res = confparser_serialize_balance_config(buffer, cfg);
	VESC_IF->free(cfg);

	return res;
}

static bool set_cfg(uint8_t *buffer) {
	BalanceApp *app = balance_app_from_arg();
	BalanceState *d = &app->state;
	bool res = confparser_deserialize_balance_config(buffer, &(d->balance_conf));

	// Store to EEPROM
	if (res) {
		uint32_t ints = sizeof(balance_config) / 4 + 1;
		uint32_t *buffer = VESC_IF->malloc(ints * sizeof(uint32_t));
		bool write_ok = true;
		memcpy(buffer, &(d->balance_conf), sizeof(balance_config));
		for (uint32_t i = 0;i < ints;i++) {
			eeprom_var v;
			v.as_u32 = buffer[i];
			if (!VESC_IF->store_eeprom_var(&v, i + 1)) {
				write_ok = false;
				break;
			}
		}

		VESC_IF->free(buffer);

		if (write_ok) {
			eeprom_var v;
			v.as_u32 = BALANCE_CONFIG_SIGNATURE;
			VESC_IF->store_eeprom_var(&v, 0);
		}

		configure(app);
	}

	return res;
}

static int get_cfg_xml(uint8_t **buffer) {
	// Note: As the address of data_balance_config_ is not known
	// at compile time it will be relative to where it is in the
	// linked binary. Therefore we add PROG_ADDR to it so that it
	// points to where it ends up on the STM32.
	*buffer = data_balance_config_ + PROG_ADDR;
	return DATA_BALANCE_CONFIG__SIZE;
}

// Called when code is stopped
static void stop(void *arg) {
	VescBalanceApp *app = (VescBalanceApp*)arg;
	VESC_IF->set_app_data_handler(NULL);
	VESC_IF->conf_custom_clear_configs();
	VESC_IF->request_terminate(app->thread);
	VESC_IF->printf("Balance App Terminated");
	VESC_IF->free(app);
}

INIT_FUN(lib_info *info) {
	INIT_START

	VescBalanceApp *app = VESC_IF->malloc(sizeof(VescBalanceApp));
	if (!app) {
		VESC_IF->printf("Out of memory!");
		return false;
	}

	memset(app, 0, sizeof(VescBalanceApp));
	BalanceState *state = &app->balance.state;

	// Read config from EEPROM if signature is correct
	eeprom_var v;
	uint32_t ints = sizeof(balance_config) / 4 + 1;
	uint32_t *buffer = VESC_IF->malloc(ints * sizeof(uint32_t));
	bool read_ok = VESC_IF->read_eeprom_var(&v, 0);
	if (read_ok && v.as_u32 == BALANCE_CONFIG_SIGNATURE) {
		for (uint32_t i = 0;i < ints;i++) {
			if (!VESC_IF->read_eeprom_var(&v, i + 1)) {
				read_ok = false;
				break;
			}
			buffer[i] = v.as_u32;
		}
	} else {
		read_ok = false;
	}

	if (read_ok) {
		memcpy(&state->balance_conf, buffer, sizeof(balance_config));
	} else {
		confparser_set_defaults_balance_config(&state->balance_conf);
	}

	VESC_IF->free(buffer);

	info->stop_fun = stop;
	info->arg = app;

	VESC_IF->conf_custom_add_config(get_cfg, set_cfg, get_cfg_xml);

	vesc_read_input(app);
	configure(&app->balance);

	app->thread = VESC_IF->spawn(balance_thd, 2048, "Balance Main", app);

	VESC_IF->set_app_data_handler(on_command_recieved_handler);

	VESC_IF->lbm_add_extension("ext-balance-get-p", ext_get_proportional);
	VESC_IF->lbm_add_extension("ext-balance-get-ratep", ext_get_proportional2);
	VESC_IF->lbm_add_extension("ext-balance-get-i", ext_get_integral);
	VESC_IF->lbm_add_extension("ext-balance-get-ratei", ext_get_integral2);
	VESC_IF->lbm_add_extension("ext-balance-get-d", ext_get_derivative);
	VESC_IF->lbm_add_extension("ext-balance-get-rated", ext_get_derivative2);
	VESC_IF->lbm_add_extension("ext-balance-get-pid", ext_get_pid_value);
	VESC_IF->lbm_add_extension("ext-balance-get-pid_rate", ext_get_pid_rate_value);
	VESC_IF->lbm_add_extension("ext-balance-get-erpm-accel", ext_get_erpm_accel);
	VESC_IF->lbm_add_extension("ext-balance-get-motor-load", ext_get_motor_load);
	VESC_IF->lbm_add_extension("ext-balance-get-motor-accel-load", ext_get_motor_accel_load);
	VESC_IF->lbm_add_extension("ext-balance-get-voltage-filtered", ext_get_voltage_filtered);
	VESC_IF->lbm_add_extension("ext-balance-get-motor-load-filtered", ext_get_motor_load_filtered);
	VESC_IF->lbm_add_extension("ext-balance-get-motor-accel-load-filtered", ext_get_motor_accel_load_filtered);
	VESC_IF->lbm_add_extension("ext-balance-get-rpm", ext_get_rpm);

	return true;
}
