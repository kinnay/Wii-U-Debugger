
#include "cafe/coreinit.h"
#include "cafe/sysapp.h"
#include "cafe/nsysnet.h"
#include "cafe/vpad.h"
#include "cafe/nn_save.h"
#include "cafe/nn_act.h"
#include "kernel.h"
#include "hbl.h"

#include "patches.h"
#include "debugger.h"
#include "exceptions.h"
#include "screen.h"
#include "menu.h"


bool GetTitleIdOnDisk(uint64_t *titleId) {
	MCPTitleListType title;
	uint32_t count = 0;
	
	int handle = MCP_Open();
	MCP_TitleListByDevice(handle, "odd", &count, &title, sizeof(title));
	MCP_Close(handle);
	
	if (count > 0) {
		*titleId = title.titleId;
		return true;
	}
	return false;
}

int MenuMain() {
	Screen screen;
	screen.init();
	
	Menu menu(&screen);
	
	Menu::Option result = menu.show();
	if (result == Menu::Exit) return EXIT_SUCCESS;
	else if (result == Menu::LaunchDisk) {
		uint64_t titleId;
		if (GetTitleIdOnDisk(&titleId)) {
			SYSLaunchTitle(titleId);
		}
		else {
			menu.setMessage("Please insert a valid disk");
		}
	}
	else if (result == Menu::ReturnToMenu) {
		SYSLaunchMenu();
	}
	return EXIT_RELAUNCH_ON_LOAD;
}

int DebuggerMain() {
	ApplyPatches();
	debugger = new Debugger();
	debugger->start();
	return EXIT_RELAUNCH_ON_LOAD;
}


bool firstRun = true;
int start() {
	coreinitInitialize();
	kernelInitialize();
	vpadInitialize();
	sysappInitialize();
	nsysnetInitialize();
	nnsaveInitialize();
	nnactInitialize();
	
	InstallExceptionHandlers();
	
	int result;
	if (firstRun) {
		result = MenuMain();
	}
	else {
		result = DebuggerMain();
	}
	firstRun = false;
	
	return result;
}

extern "C" int entryPoint() {
	return start();
}
