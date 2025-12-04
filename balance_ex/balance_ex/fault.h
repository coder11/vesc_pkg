#ifndef FAULT_H
#define FAULT_H

#include "data.h"

void engage_centering(data *d);

void engage_ready(data *d);

void engage_kill_spin(data *d);

void disengage_kill_spin(data *d);

// Fault checking order does not really matter. From a UX perspective, switch should be before angle.
bool check_faults(data *d, bool ignoreTimers);

#endif // FAULT_H


