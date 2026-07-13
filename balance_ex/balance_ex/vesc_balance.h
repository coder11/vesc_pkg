#ifndef VESC_BALANCE_H
#define VESC_BALANCE_H

#include "data.h"
#include "vesc_c_if.h"

typedef struct {
	BalanceApp balance;
	lib_thread thread;
} VescBalanceApp;

void vesc_read_input(VescBalanceApp *app);
void vesc_balance_loop(VescBalanceApp *app);

#endif // VESC_BALANCE_H
