#ifndef FAULT_H
#define FAULT_H

#include "data.h"

void engage_centering(BalanceApp *app);

void engage_ready(BalanceApp *app);

void engage_killspin(BalanceApp *app);

void disengage_killspin(BalanceApp *app);

// Fault checking order does not really matter. From a UX perspective, switch should be before angle.
bool check_faults(BalanceApp *app, bool ignoreTimers);

#endif // FAULT_H

