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

#include "pt1.h"
#include <math.h>

float pt1_calculate_k(float frequency, float sample_rate) {
	float dT = 1.0 / sample_rate;
	float RC = 1.0 / (2.0 * M_PI * frequency);
	return dT / (RC + dT);
}

float pt1_process_lowpass(float *state, float pt1_k, float in) {
	*state = *state + pt1_k * (in - *state);
	return *state;
}

float pt1_process_highpass(float *state, float pt1_k, float in) {
	*state = *state + pt1_k * (in - *state);
	return in - *state;
}

