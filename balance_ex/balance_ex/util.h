#ifndef BALANCE_EX_UTIL_H
#define BALANCE_EX_UTIL_H

#include <stdbool.h>

// Return the sign of the argument. -1.0 if negative, 1.0 if zero or positive.
#define SIGN(x)				(((x) < 0.0) ? -1.0 : 1.0)

#define DEG2RAD_f(deg)		((deg) * (float)(M_PI / 180.0))
#define RAD2DEG_f(rad) 		((rad) * (float)(180.0 / M_PI))

#define min(a, b)                                                                                  \
    ({                                                                                             \
        __typeof__(a) _a = (a);                                                                    \
        __typeof__(b) _b = (b);                                                                    \
        _a < _b ? _a : _b;                                                                         \
    })

#define max(a, b)                                                                                  \
    ({                                                                                             \
        __typeof__(a) _a = (a);                                                                    \
        __typeof__(b) _b = (b);                                                                    \
        _a > _b ? _a : _b;                                                                         \
    })

// Advance interpolation by one step, modifying the current value
// If the interpolation has finished return true, false otherwise
bool advance_interpolation(float *value, float target, float step);

void clampf(float *value, float min, float max);
void clampf_min(float *value, float min);
void clampf_max(float *value, float max);

void clamp(int *value, int min, int max);
void clamp_min(int *value, int min);
void clamp_max(int *value, int max);

#endif // BALANCE_EX_UTIL_H