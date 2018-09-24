
#pragma once

#include <cstdint>

enum VPADButtons {
	VPAD_BUTTON_A = 0x8000,
	VPAD_BUTTON_B = 0x4000,
	VPAD_BUTTON_X = 0x2000,
	VPAD_BUTTON_Y = 0x1000,
	VPAD_BUTTON_LEFT = 0x0800,
	VPAD_BUTTON_RIGHT = 0x0400,
	VPAD_BUTTON_UP = 0x0200,
	VPAD_BUTTON_DOWN = 0x0100,
	VPAD_BUTTON_ZL = 0x0080,
	VPAD_BUTTON_ZR = 0x0040,
	VPAD_BUTTON_L = 0x0020,
	VPAD_BUTTON_R = 0x0010,
	VPAD_BUTTON_PLUS = 0x0008,
	VPAD_BUTTON_MINUS = 0x0004,
	VPAD_BUTTON_HOME = 0x0002,
	VPAD_BUTTON_SYNC = 0x0001,
	
	VPAD_BUTTON_STICK_R = 0x00020000,
	VPAD_BUTTON_STICK_L = 0x00040000,
	VPAD_BUTTON_TV = 0x00010000
};

struct VPADVec2D {
	float x;
	float y;
};

struct VPADVec3D {
	float x;
	float y;
	float z;
};

struct VPADDirection {
	VPADVec3D x;
	VPADVec3D y;
	VPADVec3D z;
};

struct VPADTouchData {
	uint16_t x;
	uint16_t y;
	uint16_t touched;
	uint16_t validity;
};

struct VPADAccStatus {
	VPADVec3D acc;
	float magnitude;
	float variation;
	VPADVec2D vertical;
};

struct VPADStatus {
	uint32_t hold;
	uint32_t pressed;
	uint32_t released;
	VPADVec2D leftStick;
	VPADVec2D rightStick;
	VPADAccStatus accelorometer;
	VPADVec3D gyro;
	VPADVec3D angle;
	uint8_t error;
	uint8_t _51;

	VPADTouchData tpNormal;
	VPADTouchData tpFiltered1;
	VPADTouchData tpFiltered2;
	uint16_t _6A;
	
	VPADDirection direction;
	bool headphones;
	VPADVec3D mag;
	uint8_t volume;
	uint8_t battery;
	uint8_t micStatus;
	uint8_t volumeEx;
	char _A4[8];
};

extern void (*VPADRead)(int chan, VPADStatus *buffers, uint32_t count, int *error);

void vpadInitialize();
