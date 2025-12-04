#include "util.h"
#include "data.h"

#include <math.h>
#include <stdbool.h>

bool advance_interpolation(float *value, float target, float step) {
	if (*value == target) {
		return true;
	}

	// If we are less than one step size away, go all the way
	if (fabsf(*value - target) < step) {
		*value = target;
		return true;
	} 
	
	if (target - *value > 0) {
		*value += step;
	} else {
		*value -= step;
	}
	return false;
}

float clampf(float value, float min, float max) {
    const float m = value < min ? min : value;
    return m > max ? max : m;
}
