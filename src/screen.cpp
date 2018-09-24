
#include "cafe/coreinit.h"
#include "screen.h"
#include "memory.h"

Screen::Screen() : screenBuffer(0) {}
Screen::~Screen() {
	if (screenBuffer) {
		operator delete(screenBuffer);
	}
}

void Screen::init() {
	OSScreenInit();
	
	uint32_t bufferSize0 = OSScreenGetBufferSizeEx(0);
	uint32_t bufferSize1 = OSScreenGetBufferSizeEx(1);
	screenBuffer = operator new(bufferSize0 + bufferSize1, 0x40);
	OSScreenSetBufferEx(0, screenBuffer);
	OSScreenSetBufferEx(1, (char *)screenBuffer + bufferSize0);

	OSScreenEnableEx(0, 1);
	OSScreenEnableEx(1, 1);
	OSScreenClearBufferEx(0, 0);
	OSScreenClearBufferEx(1, 0);
	OSScreenFlipBuffersEx(0);
	OSScreenFlipBuffersEx(1);
}

void Screen::clear(Display screen, uint32_t color) {
	OSScreenClearBufferEx(screen, color);
}

void Screen::drawRect(Display screen, int x1, int y1, int x2, int y2, uint32_t color) {
	for (int x = x1; x < x2; x++) {
		OSScreenPutPixelEx(screen, x, y1, color);
		OSScreenPutPixelEx(screen, x, y2, color);
	}
	for (int y = y1; y < y2; y++) {
		OSScreenPutPixelEx(screen, x1, y, color);
		OSScreenPutPixelEx(screen, x2, y, color);
	}
}

void Screen::fillRect(Display screen, int x1, int y1, int x2, int y2, uint32_t color) {
	for (int x = x1; x < x2; x++) {
		for (int y = y1; y < y2; y++) {
			OSScreenPutPixelEx(screen, x, y, color);
		}
	}
}

void Screen::drawText(Display screen, int x, int y, const char *text) {
	OSScreenPutFontEx(screen, x, y, text);
}

void Screen::flip(Display screen) {
	OSScreenFlipBuffersEx(screen);
}

int Screen::convx(int x) { return x * 854 / 1280; }
int Screen::convy(int y) { return y * 480 / 720; }

void Screen::clear(uint32_t color) {
	clear(TV, color);
	clear(DRC, color);
}

void Screen::drawRect(int x1, int y1, int x2, int y2, uint32_t color) {
	drawRect(TV, x1, y1, x2, y2, color);
	drawRect(DRC, convx(x1), convy(y1), convx(x2), convy(y2), color);
}

void Screen::fillRect(int x1, int y1, int x2, int y2, uint32_t color) {
	fillRect(TV, x1, y1, x2, y2, color);
	fillRect(DRC, convx(x1), convy(y1), convx(x2), convy(y2), color);
}

void Screen::drawText(int x, int y, const char *text) {
	drawText(TV, x, y, text);
	drawText(DRC, x, y, text);
}

void Screen::flip() {
	flip(TV);
	flip(DRC);
}
