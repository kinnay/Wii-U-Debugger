
#include "cafe/coreinit.h"
#include <cstdint>

int (*SAVEInit)();
int (*SAVEOpenFile)(FSClient *client, FSCmdBlock *block, uint8_t slot, const char *path, int *handle, uint32_t flags);
int (*SAVEGetSharedDataTitlePath)(uint64_t titleId, const char *path, char *outpath, uint32_t outlen);
void (*SAVEShutdown)();

void nnsaveInitialize() {
	uint32_t handle;
	OSDynLoad_Acquire("nn_save.rpl", &handle);
	
	OSDynLoad_FindExport(handle, false, "SAVEInit", &SAVEInit);
	OSDynLoad_FindExport(handle, false, "SAVEOpenFile", &SAVEOpenFile);
	OSDynLoad_FindExport(handle, false, "SAVEGetSharedDataTitlePath", &SAVEGetSharedDataTitlePath);
	OSDynLoad_FindExport(handle, false, "SAVEShutdown", &SAVEShutdown);
}
