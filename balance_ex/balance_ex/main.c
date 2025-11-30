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

HEADER

static void balance_thd(void *arg) {
	data *d = (data*)arg;
	
	while (!VESC_IF->should_terminate()) {
		balance_loop_tick(d);
	}
}

// Handler for incoming app commands
static void on_command_recieved_handler(unsigned char *buffer, unsigned int len) {
	data *d = (data*)ARG;

	on_command_recieved(d, buffer, len);
}

static lbm_value ext_get_proportional(lbm_value *args, lbm_uint argn) {
	(void)args;
	(void)argn;
	data *d = (data*)ARG;
	return VESC_IF->lbm_enc_float(d->proportional * d->balance_conf.kp);
}

static lbm_value ext_get_proportional2(lbm_value *args, lbm_uint argn) {
	(void)args;
	(void)argn;
	data *d = (data*)ARG;
	return VESC_IF->lbm_enc_float(d->proportional2 * d->balance_conf.kp2);
}

static lbm_value ext_get_integral(lbm_value *args, lbm_uint argn) {
	(void)args;
	(void)argn;
	data *d = (data*)ARG;
	return VESC_IF->lbm_enc_float(d->integral * d->balance_conf.ki);
}

static lbm_value ext_get_integral2(lbm_value *args, lbm_uint argn) {
	(void)args;
	(void)argn;
	data *d = (data*)ARG;
	return VESC_IF->lbm_enc_float(d->integral2 * d->balance_conf.ki2);
}

static lbm_value ext_get_derivative(lbm_value *args, lbm_uint argn) {
	(void)args;
	(void)argn;
	data *d = (data*)ARG;
	return VESC_IF->lbm_enc_float(d->derivative * d->balance_conf.kd);
}

static lbm_value ext_get_derivative2(lbm_value *args, lbm_uint argn) {
	(void)args;
	(void)argn;
	data *d = (data*)ARG;
	return VESC_IF->lbm_enc_float(d->derivative2 * d->balance_conf.kd2);
}

static lbm_value ext_get_pid_value(lbm_value *args, lbm_uint argn) {
	(void)args;
	(void)argn;
	data *d = (data*)ARG;
	return VESC_IF->lbm_enc_float(d->pid_value);
}

static lbm_value ext_get_pid_rate_value(lbm_value *args, lbm_uint argn) {
	(void)args;
	(void)argn;
	data *d = (data*)ARG;
	return VESC_IF->lbm_enc_float(d->pid_value2);
}

static lbm_value ext_get_erpm_accel(lbm_value *args, lbm_uint argn) {
	(void)args;
	(void)argn;
	data *d = (data*)ARG;
	return VESC_IF->lbm_enc_float(d->erpm_accel);
}

static lbm_value ext_get_erpm_accel_divided_by_current(lbm_value *args, lbm_uint argn) {
	(void)args;
	(void)argn;
	data *d = (data*)ARG;
	return VESC_IF->lbm_enc_float(d->erpm_accel_divided_by_current);
}

// These functions are used to send the config page to VESC Tool
// and to make persistent read and write work
static int get_cfg(uint8_t *buffer, bool is_default) {
	data *d = (data*)ARG;
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
	data *d = (data*)ARG;
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

		configure(d);
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
	data *d = (data*)arg;
	VESC_IF->set_app_data_handler(NULL);
	VESC_IF->conf_custom_clear_configs();
	VESC_IF->request_terminate(d->thread);
	VESC_IF->printf("Balance App Terminated");
	VESC_IF->free(d);
}

INIT_FUN(lib_info *info) {
	INIT_START

	data *d = VESC_IF->malloc(sizeof(data));
	memset(d, 0, sizeof(data));
	
	if (!d) {
		VESC_IF->printf("Out of memory!");
		return false;
	}

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
		memcpy(&(d->balance_conf), buffer, sizeof(balance_config));
	} else {
		confparser_set_defaults_balance_config(&(d->balance_conf));
	}
	
	VESC_IF->free(buffer);

	info->stop_fun = stop;	
	info->arg = d;
	
	VESC_IF->conf_custom_add_config(get_cfg, set_cfg, get_cfg_xml);

	configure(d);

	d->thread = VESC_IF->spawn(balance_thd, 2048, "Balance Main", d);

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
	VESC_IF->lbm_add_extension("ext-balance-get-erpm-accel-div-current", ext_get_erpm_accel_divided_by_current);

	return true;
}

