
#include "cafe/coreinit.h"
#include "hbl.h"
#include <cstdint>
#include <cstddef>
	
int (*OSDynLoad_Acquire)(const char *name, uint32_t *handle);
int (*OSDynLoad_FindExport)(uint32_t handle, bool isData, const char *name, void *ptr);
int (*OSDynLoad_GetModuleName)(uint32_t handle, char *name, int *size);
OSMutex *OSDynLoad_gLoaderLock;

bool (*OSIsDebuggerInitialized)();

void (*exit)(int result);
void (*_Exit)(int result);

void (*OSFatal)(const char *msg);

uint32_t (*OSGetSymbolName)(uint32_t addr, char *buffer, size_t bufsize);
void (*DisassemblePPCRange)(uint32_t start, uint32_t end, DisassemblyPrintFn printFunc, DisassemblyFindSymbolFn symFunc, DisassemblyFlags flags);
void (*DisassemblePPCOpcode)(uint32_t addr, void *buffer, size_t bufsize, DisassemblyFindSymbolFn symFunc, DisassemblyFlags flags);

int (*OSSetExceptionCallback)(OSExceptionType type, OSExceptionCallback callback);
int (*OSSetExceptionCallbackEx)(OSExceptionMode mode, OSExceptionType type, OSExceptionCallback callback);
void (*OSLoadContext)(OSContext *context);

int (*OSDisableInterrupts)();
void (*OSRestoreInterrupts)(int state);

void (*__OSLockScheduler)(void *);
void (*__OSUnlockScheduler)(void *);

void (*OSInitMutex)(OSMutex *mutex);
void (*OSLockMutex)(OSMutex *mutex);
void (*OSUnlockMutex)(OSMutex *mutex);

void (*OSInitMessageQueue)(OSMessageQueue *queue, OSMessage *messages, int count);
bool (*OSSendMessage)(OSMessageQueue *queue, OSMessage *message, OSMessageFlags flags);
bool (*OSReceiveMessage)(OSMessageQueue *queue, OSMessage *message, OSMessageFlags flags);

void (*OSCreateAlarm)(OSAlarm *alarm);
bool (*OSSetAlarm)(OSAlarm *alarm, uint64_t timeout, OSAlarmCallback callback);
void (*OSCancelAlarm)(OSAlarm *alarm);
bool (*OSWaitAlarm)(OSAlarm *alarm);

OSThread *(*OSGetCurrentThread)();
OSThread *(*OSGetDefaultThread)(int core);
bool (*OSCreateThread)(OSThread *thread, OSThreadFunc func, int argc, void *argv, void *stack, uint32_t stackSize, int priority, int attr);
int (*OSResumeThread)(OSThread *thread);
bool (*OSJoinThread)(OSThread *thread, int *result);
void (*OSExitThread)(int result);
const char *(*OSGetThreadName)(OSThread *thread);
void (*OSSetThreadName)(OSThread *thread, const char *name);
uint32_t (*OSGetThreadAffinity)(OSThread *thread);
int (*OSGetThreadPriority)(OSThread *thread);

OSSystemInfo *(*OSGetSystemInfo)();
void (*OSSleepTicks)(uint64_t ticks);

uint64_t (*OSGetTitleID)();

int (*OSGetMemBound)(OSMemoryType type, uint32_t *startPtr, uint32_t *sizePtr);
uint32_t (*OSEffectiveToPhysical)(uint32_t addr);

void (*OSScreenInit)();
uint32_t (*OSScreenGetBufferSizeEx)(int screen);
void (*OSScreenSetBufferEx)(int screen, void *buffer);
void (*OSScreenEnableEx)(int screen, bool enabled);
void (*OSScreenClearBufferEx)(int screen, uint32_t color);
void (*OSScreenFlipBuffersEx)(int screen);
void (*OSScreenPutPixelEx)(int screen, int x, int y, uint32_t color);
void (*OSScreenPutFontEx)(int screen, int x, int y, const char *text);

void (*DCFlushRange)(const void *buffer, uint32_t length);
void (*DCInvalidateRange)(const void *buffer, uint32_t length);
void (*ICInvalidateRange)(const void *buffer, uint32_t length);

int (*IOS_Open)(const char *path, int mode);
int (*IOS_Ioctl)(int fd, uint32_t request, const void *inptr, uint32_t inlen, void *outptr, uint32_t outlen);
int (*IOS_Close)(int fd);

int (*FSInit)();
int (*FSAddClient)(FSClient *client, uint32_t flags);
int (*FSInitCmdBlock)(FSCmdBlock *block);
int (*FSGetMountSource)(FSClient *client, FSCmdBlock *block, FSMountSourceType type, FSMountSource *source, uint32_t flags);
int (*FSMount)(FSClient *client, FSCmdBlock *block, FSMountSource *source, char *path, uint32_t bytes, uint32_t flags);
int (*FSMakeDir)(FSClient *client, FSCmdBlock *block, const char *path, uint32_t flags);
int (*FSChangeDir)(FSClient *client, FSCmdBlock *block, const char *path, uint32_t flags);
int (*FSGetCwd)(FSClient *client, FSCmdBlock *block, char *path, int length, uint32_t flags);
int (*FSOpenDir)(FSClient *client, FSCmdBlock *block, const char *path, int *handle, uint32_t flags);
int (*FSReadDir)(FSClient *client, FSCmdBlock *block, int handle, FSDirectoryEntry *entry, uint32_t flags);
int (*FSCloseDir)(FSClient *client, FSCmdBlock *block, int handle, uint32_t flags);
int (*FSOpenFile)(FSClient *client, FSCmdBlock *block, const char *path, const char *mode, int *handle, uint32_t flags);
int (*FSGetStatFile)(FSClient *client, FSCmdBlock *block, int handle, FSStat *stat, uint32_t flags);
int (*FSReadFile)(FSClient *client, FSCmdBlock *block, void *buffer, int size, int count, int handle, int flag, uint32_t flags);
int (*FSWriteFile)(FSClient *client, FSCmdBlock *block, const void *buffer, int size, int count, int handle, int flag, uint32_t flags);
int (*FSCloseFile)(FSClient *client, FSCmdBlock *block, int handle, uint32_t flags);
int (*FSGetStat)(FSClient *client, FSCmdBlock *block, const char *path, FSStat *stat, uint32_t flags);
int (*FSRename)(FSClient *client, FSCmdBlock *block, const char *oldPath, const char *newPath, uint32_t flags);
int (*FSRemove)(FSClient *client, FSCmdBlock *block, const char *path, uint32_t flags);
int (*FSDelClient)(FSClient *client, uint32_t flags);
void (*FSShutdown)();

int (*MCP_Open)();
int (*MCP_GetDeviceId)(int handle, uint32_t *deviceId);
int (*MCP_TitleList)(int handle, uint32_t *count, MCPTitleListType *list, uint32_t size);
int (*MCP_TitleListByAppType)(int handle, uint32_t appType, uint32_t *count, MCPTitleListType *list, uint32_t size);
int (*MCP_TitleListByDevice)(int handle, const char *device, uint32_t *count, MCPTitleListType *list, uint32_t size);
void (*MCP_Close)(int handle);

void (*__KernelGetInfo)(KernelInfoType type, void *buffer, uint32_t size, uint32_t unk);

int (*snprintf)(char *str, size_t size, const char *format, ...);

void *(*MEMGetBaseHeapHandle)(int type);
uint32_t (*MEMGetAllocatableSizeForExpHeapEx)(void *handle, int alignment);

void *(**pMEMAllocFromDefaultHeap)(uint32_t size);
void *(**pMEMAllocFromDefaultHeapEx)(uint32_t size, int alignment);
void  (**pMEMFreeToDefaultHeap)(void *ptr);

OSDynLoad_RPLInfo **pMainRPL;
OSDynLoad_RPLInfo **pFirstRPL;
OSThread **pThreadList;

void coreinitInitialize() {
	*(uint32_t *)&OSDynLoad_Acquire = OS_SPECIFICS->OSDynLoad_Acquire;
	*(uint32_t *)&OSDynLoad_FindExport = OS_SPECIFICS->OSDynLoad_FindExport;
	
	uint32_t handle;
	OSDynLoad_Acquire("coreinit.rpl", &handle);
	
	OSDynLoad_FindExport(handle, false, "OSDynLoad_GetModuleName", &OSDynLoad_GetModuleName);
	OSDynLoad_FindExport(handle, true, "OSDynLoad_gLoaderLock", &OSDynLoad_gLoaderLock);
	
	OSDynLoad_FindExport(handle, false, "OSIsDebuggerInitialized", &OSIsDebuggerInitialized);
	
	OSDynLoad_FindExport(handle, false, "exit", &exit);
	OSDynLoad_FindExport(handle, false, "_Exit", &_Exit);

	OSDynLoad_FindExport(handle, false, "OSFatal", &OSFatal);
	
	OSDynLoad_FindExport(handle, false, "OSGetSymbolName", &OSGetSymbolName);
	OSDynLoad_FindExport(handle, false, "DisassemblePPCRange", &DisassemblePPCRange);
	OSDynLoad_FindExport(handle, false, "DisassemblePPCOpcode", &DisassemblePPCOpcode);
	
	OSDynLoad_FindExport(handle, false, "OSSetExceptionCallback", &OSSetExceptionCallback);
	OSDynLoad_FindExport(handle, false, "OSSetExceptionCallbackEx", &OSSetExceptionCallbackEx);
	OSDynLoad_FindExport(handle, false, "OSLoadContext", &OSLoadContext);
	
	OSDynLoad_FindExport(handle, false, "OSDisableInterrupts", &OSDisableInterrupts);
	OSDynLoad_FindExport(handle, false, "OSRestoreInterrupts", &OSRestoreInterrupts);
	
	OSDynLoad_FindExport(handle, false, "__OSLockScheduler", &__OSLockScheduler);
	OSDynLoad_FindExport(handle, false, "__OSUnlockScheduler", &__OSUnlockScheduler);
	
	OSDynLoad_FindExport(handle, false, "OSInitMutex", &OSInitMutex);
	OSDynLoad_FindExport(handle, false, "OSLockMutex", &OSLockMutex);
	OSDynLoad_FindExport(handle, false, "OSUnlockMutex", &OSUnlockMutex);
	
	OSDynLoad_FindExport(handle, false, "OSInitMessageQueue", &OSInitMessageQueue);
	OSDynLoad_FindExport(handle, false, "OSSendMessage", &OSSendMessage);
	OSDynLoad_FindExport(handle, false, "OSReceiveMessage", &OSReceiveMessage);

	OSDynLoad_FindExport(handle, false, "OSCreateAlarm", &OSCreateAlarm);
	OSDynLoad_FindExport(handle, false, "OSSetAlarm", &OSSetAlarm);
	OSDynLoad_FindExport(handle, false, "OSCancelAlarm", &OSCancelAlarm);
	OSDynLoad_FindExport(handle, false, "OSWaitAlarm", &OSWaitAlarm);

	OSDynLoad_FindExport(handle, false, "OSGetCurrentThread", &OSGetCurrentThread);
	OSDynLoad_FindExport(handle, false, "OSGetDefaultThread", &OSGetDefaultThread);
	OSDynLoad_FindExport(handle, false, "OSCreateThread", &OSCreateThread);
	OSDynLoad_FindExport(handle, false, "OSResumeThread", &OSResumeThread);
	OSDynLoad_FindExport(handle, false, "OSJoinThread", &OSJoinThread);
	OSDynLoad_FindExport(handle, false, "OSExitThread", &OSExitThread);
	OSDynLoad_FindExport(handle, false, "OSGetThreadName", &OSGetThreadName);
	OSDynLoad_FindExport(handle, false, "OSSetThreadName", &OSSetThreadName);
	OSDynLoad_FindExport(handle, false, "OSGetThreadAffinity", &OSGetThreadAffinity);
	OSDynLoad_FindExport(handle, false, "OSGetThreadPriority", &OSGetThreadPriority);
	
	OSDynLoad_FindExport(handle, false, "OSGetSystemInfo", &OSGetSystemInfo);
	OSDynLoad_FindExport(handle, false, "OSSleepTicks", &OSSleepTicks);
	
	OSDynLoad_FindExport(handle, false, "OSGetTitleID", &OSGetTitleID);
	
	OSDynLoad_FindExport(handle, false, "OSGetMemBound", &OSGetMemBound);
	OSDynLoad_FindExport(handle, false, "OSEffectiveToPhysical", &OSEffectiveToPhysical);
	
	OSDynLoad_FindExport(handle, false, "OSScreenInit", &OSScreenInit);
	OSDynLoad_FindExport(handle, false, "OSScreenGetBufferSizeEx", &OSScreenGetBufferSizeEx);
	OSDynLoad_FindExport(handle, false, "OSScreenSetBufferEx", &OSScreenSetBufferEx);
	OSDynLoad_FindExport(handle, false, "OSScreenEnableEx", &OSScreenEnableEx);
	OSDynLoad_FindExport(handle, false, "OSScreenClearBufferEx", &OSScreenClearBufferEx);
	OSDynLoad_FindExport(handle, false, "OSScreenFlipBuffersEx", &OSScreenFlipBuffersEx);
	OSDynLoad_FindExport(handle, false, "OSScreenPutPixelEx", &OSScreenPutPixelEx);
	OSDynLoad_FindExport(handle, false, "OSScreenPutFontEx", &OSScreenPutFontEx);
	
	OSDynLoad_FindExport(handle, false, "DCFlushRange", &DCFlushRange);
	OSDynLoad_FindExport(handle, false, "DCInvalidateRange", &DCInvalidateRange);
	OSDynLoad_FindExport(handle, false, "ICInvalidateRange", &ICInvalidateRange);
	OSDynLoad_FindExport(handle, false, "IOS_Open", &IOS_Open);
	OSDynLoad_FindExport(handle, false, "IOS_Ioctl", &IOS_Ioctl);
	OSDynLoad_FindExport(handle, false, "IOS_Close", &IOS_Close);
	
	OSDynLoad_FindExport(handle, false, "FSInit", &FSInit);
	OSDynLoad_FindExport(handle, false, "FSAddClient", &FSAddClient);
	OSDynLoad_FindExport(handle, false, "FSInitCmdBlock", &FSInitCmdBlock);
	OSDynLoad_FindExport(handle, false, "FSGetMountSource", &FSGetMountSource);
	OSDynLoad_FindExport(handle, false, "FSMount", &FSMount);
	OSDynLoad_FindExport(handle, false, "FSMakeDir", &FSMakeDir);
	OSDynLoad_FindExport(handle, false, "FSChangeDir", &FSChangeDir);
	OSDynLoad_FindExport(handle, false, "FSGetCwd", &FSGetCwd);
	OSDynLoad_FindExport(handle, false, "FSOpenDir", &FSOpenDir);
	OSDynLoad_FindExport(handle, false, "FSReadDir", &FSReadDir);
	OSDynLoad_FindExport(handle, false, "FSCloseDir", &FSCloseDir);
	OSDynLoad_FindExport(handle, false, "FSOpenFile", &FSOpenFile);
	OSDynLoad_FindExport(handle, false, "FSGetStatFile", &FSGetStatFile);
	OSDynLoad_FindExport(handle, false, "FSReadFile", &FSReadFile);
	OSDynLoad_FindExport(handle, false, "FSWriteFile", &FSWriteFile);
	OSDynLoad_FindExport(handle, false, "FSCloseFile", &FSCloseFile);
	OSDynLoad_FindExport(handle, false, "FSGetStat", &FSGetStat);
	OSDynLoad_FindExport(handle, false, "FSRename", &FSRename);
	OSDynLoad_FindExport(handle, false, "FSRemove", &FSRemove);
	OSDynLoad_FindExport(handle, false, "FSDelClient", &FSDelClient);
	OSDynLoad_FindExport(handle, false, "FSShutdown", &FSShutdown);
	
	OSDynLoad_FindExport(handle, false, "MCP_Open", &MCP_Open);
	OSDynLoad_FindExport(handle, false, "MCP_GetDeviceId", &MCP_GetDeviceId);
	OSDynLoad_FindExport(handle, false, "MCP_TitleList", &MCP_TitleList);
	OSDynLoad_FindExport(handle, false, "MCP_TitleListByAppType", &MCP_TitleListByAppType);
	OSDynLoad_FindExport(handle, false, "MCP_TitleListByDevice", &MCP_TitleListByDevice);
	OSDynLoad_FindExport(handle, false, "MCP_Close", &MCP_Close);
	
	OSDynLoad_FindExport(handle, false, "__KernelGetInfo", &__KernelGetInfo);
	
	OSDynLoad_FindExport(handle, false, "__os_snprintf", &snprintf);
	
	OSDynLoad_FindExport(handle, false, "MEMGetBaseHeapHandle", &MEMGetBaseHeapHandle);
	OSDynLoad_FindExport(handle, false, "MEMGetAllocatableSizeForExpHeapEx", &MEMGetAllocatableSizeForExpHeapEx);
	
	OSDynLoad_FindExport(handle, true, "MEMAllocFromDefaultHeap", &pMEMAllocFromDefaultHeap);
	OSDynLoad_FindExport(handle, true, "MEMAllocFromDefaultHeapEx", &pMEMAllocFromDefaultHeapEx);
	OSDynLoad_FindExport(handle, true, "MEMFreeToDefaultHeap", &pMEMFreeToDefaultHeap);
	
	pMainRPL = (OSDynLoad_RPLInfo **)0x10081014;
	pFirstRPL = (OSDynLoad_RPLInfo **)0x10081018;
	pThreadList = (OSThread **)0x100567F8;
}
