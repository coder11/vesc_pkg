#ifndef BALANCE_EX_UTIL_H
#define BALANCE_EX_UTIL_H

// Return the sign of the argument. -1.0 if negative, 1.0 if zero or positive.
#define SIGN(x)				(((x) < 0.0) ? -1.0 : 1.0)

#define DEG2RAD_f(deg)		((deg) * (float)(M_PI / 180.0))
#define RAD2DEG_f(rad) 		((rad) * (float)(180.0 / M_PI))

#endif // BALANCE_EX_UTIL_H