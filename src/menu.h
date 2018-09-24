
#pragma once

#include "screen.h"

class Menu {
	public:
	enum Option {
		LaunchDisk,
		ReturnToMenu,
		Exit
	};
	
	Menu(Screen *screen);
	Option show();
	void setMessage(const char *message);
	void redraw();
	
	private:
	Screen *screen;
	int currentOption;
	
	const char *message;
};
