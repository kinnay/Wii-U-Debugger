
#include "cafe/sysapp.h"
#include "cafe/coreinit.h"

bool (*SYSCheckTitleExists)(uint64_t titleId);
void (*SYSLaunchTitle)(uint64_t titleId);
void (*SYSLaunchMenu)();

void (*SYSLaunchTitleByPathFromLauncher)(const char *path, int len);

void sysappInitialize() {
	uint32_t handle;
	OSDynLoad_Acquire("sysapp.rpl", &handle);
	
	OSDynLoad_FindExport(handle, false, "SYSCheckTitleExists", &SYSCheckTitleExists);
	OSDynLoad_FindExport(handle, false, "SYSLaunchTitle", &SYSLaunchTitle);
	OSDynLoad_FindExport(handle, false, "SYSLaunchMenu", &SYSLaunchMenu);
	
	OSDynLoad_FindExport(handle, false, "_SYSLaunchTitleByPathFromLauncher", &SYSLaunchTitleByPathFromLauncher);
}
