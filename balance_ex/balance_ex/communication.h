#ifndef COMMUNICATION_H
#define COMMUNICATION_H

#include "data.h"

// Balance commands
#define BALANCE_COMMAND_GET_REALTIME_DATA		0x01
#define BALANCE_COMMAND_TRIGGER_KILLSPIN		0x02
#define BALANCE_COMMAND_ADJUST_F_USER			0x03

void on_command_recieved(data* d, unsigned char *buffer, unsigned int len);
void send_realtime_data(data *d);

#endif // COMMUNICATION_H