
#pragma once

#include <cstdint>

extern bool (*SYSCheckTitleExists)(uint64_t titleId);
extern void (*SYSLaunchTitle)(uint64_t titleId);
extern void (*SYSLaunchMenu)();

extern void (*SYSLaunchTitleByPathFromLauncher)(const char *path, int len);

void sysappInitialize();
