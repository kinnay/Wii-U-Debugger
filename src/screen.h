
#pragma once

#include <cstdint>

class Screen {
	public:
	enum Display {
		TV,
		DRC
	};
	
	Screen();
	~Screen();
	
	void init();
	void clear(uint32_t color);
	void drawRect(int x1, int y1, int x2, int y2, uint32_t color);
	void fillRect(int x1, int y1, int x2, int y2, uint32_t color);
	void drawText(int x, int y, const char *text);
	void flip();
	
	void clear(Display screen, uint32_t color);
	void drawRect(Display screen, int x1, int y1, int x2, int y2, uint32_t color);
	void fillRect(Display screen, int x1, int y1, int x2, int y2, uint32_t color);
	void drawText(Display screen, int x, int y, const char *text);
	void flip(Display screen);

	private:
	void *screenBuffer;
	
	int convx(int x);
	int convy(int y);
};
