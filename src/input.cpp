
#include "cafe/vpad.h"
#include <cstdint>

uint32_t GetInput(uint32_t mask) {
	VPADStatus input;
	int error;
	VPADRead(0, &input, 1, &error);
	return input.pressed & mask;
}

uint32_t WaitInput(uint32_t mask) {
	VPADStatus input;
	int error;
	while (true) {
		VPADRead(0, &input, 1, &error);
		if (input.pressed & mask) {
			return input.pressed & mask;
		}
	}
}
