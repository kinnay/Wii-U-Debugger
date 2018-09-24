
#pragma once

#include "cafe/coreinit.h"
#include <cstdint>

extern int (*SAVEInit)();
extern int (*SAVEOpenFile)(FSClient *client, FSCmdBlock *block, uint8_t slot, const char *path, int *handle, uint32_t flags);
extern int (*SAVEGetSharedDataTitlePath)(uint64_t titleId, const char *path, char *outpath, uint32_t outlen);
extern void (*SAVEShutdown)();

void nnsaveInitialize();
