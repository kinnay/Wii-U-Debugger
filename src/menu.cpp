
#include "cafe/vpad.h"
#include "menu.h"
#include "screen.h"
#include "input.h"
#include "color.h"

Menu::Menu(Screen *screen) : screen(screen) {
	currentOption = LaunchDisk;
	message = nullptr;
}

Menu::Option Menu::show() {
	while (true) {
		redraw();
		uint32_t buttons = WaitInput(VPAD_BUTTON_A | VPAD_BUTTON_DOWN | VPAD_BUTTON_UP);
		if (buttons & VPAD_BUTTON_A) return (Option)currentOption;
		else if (buttons & VPAD_BUTTON_DOWN) {
			if (currentOption < 2) currentOption++;
		}
		else if (buttons & VPAD_BUTTON_UP) {
			if (currentOption > 0) currentOption--;
		}
	}
}

void Menu::setMessage(const char *message) {
	this->message = message;
	redraw();
}

void Menu::redraw() {
	screen->clear(COLOR_BLUE);
	screen->drawText(5, 5, "Wii U Debugger");
	screen->drawText(5, 7, "Choose an option:");
	screen->drawText(8, 9, "Install and launch disc");
	screen->drawText(8, 10, "Install and return to system menu");
	screen->drawText(8, 11, "Exit without installing");
	screen->drawText(5, 9 + currentOption, ">");
	if (message) {
		screen->drawText(5, 13, message);
	}
	screen->flip();
}
