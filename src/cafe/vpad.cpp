
#include "cafe/vpad.h"
#include "cafe/coreinit.h"

void (*VPADRead)(int chan, VPADStatus *buffers, uint32_t count, int *error);

void vpadInitialize() {
	uint32_t handle;
	OSDynLoad_Acquire("vpad.rpl", &handle);
	
	OSDynLoad_FindExport(handle, false, "VPADRead", &VPADRead);
}
