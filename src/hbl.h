
#pragma once

#include <cstdint>

#define MEM_BASE 0x800000

struct OsSpecifics {
	uint32_t OSDynLoad_Acquire;
	uint32_t OSDynLoad_FindExport;
};
#define OS_SPECIFICS ((OsSpecifics *)(MEM_BASE + 0x1500))

#define EXIT_SUCCESS 0
#define EXIT_RELAUNCH_ON_LOAD -3
