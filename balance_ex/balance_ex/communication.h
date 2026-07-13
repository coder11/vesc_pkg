#ifndef COMMUNICATION_H
#define COMMUNICATION_H

#include "data.h"

// Balance commands
#define BALANCE_COMMAND_GET_REALTIME_DATA		0x01
#define BALANCE_COMMAND_TRIGGER_KILLSPIN		0x02

void on_command_recieved(BalanceApp *app, unsigned char *buffer, unsigned int len);
void send_realtime_data(BalanceApp *app);

#endif // COMMUNICATION_H
