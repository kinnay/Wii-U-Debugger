
#pragma once

#include <cstdint>
#include <cstddef>

// Timers
#define OSTimerClockSpeed ((OSGetSystemInfo()->busClockSpeed) / 4)

#define OSSecondsToTicks(val) ((uint64_t)(val) * (uint64_t)OSTimerClockSpeed)
#define OSMillisecondsToTicks(val) (((uint64_t)(val) * (uint64_t)OSTimerClockSpeed) / 1000ull)

#define OSTicksToSeconds(val) ((uint64_t)(val) / (uint64_t)OSTimerClockSpeed)
#define OSTicksToMilliseconds(val) (((uint64_t)(val) * 1000ull) / (uint64_t)OSTimerClockSpeed)

// Memory
enum OSMemoryType {
	MEM1 = 1,
	MEM2 = 2
};

// System
enum KernelInfoType {
	TITLE_INFO = 0,
	SYSTEM_INFO = 1,
	PLATFORM_INFO = 2,
	
	KERNEL_STATISTICS = 4,
	PERFORMANCE_NUMBERS = 5,
	
	PROCESS_INFO = 8,
	
	CRASH_INFO = 11,
	APP_CRASH_CONTROL = 12,
	COS_REPORT_MASKS = 13,
	CRASH_RECOVERY = 14,
	CRASH_DETAIL_LEVEL = 15,
	CRASH_DUMP_TYPE = 16,
	SHUTDOWN_REASON = 17,
	WRITE_GATHER_REGS = 18,
	PROC_DATA_BOUNDS = 19
};

struct OSSystemInfo {
	uint32_t busClockSpeed;
	uint32_t coreClockSpeed;
	int64_t baseTime;
	char _10[0x10];
};

struct OSTitleInfo {
	char _0[0xC];
	uint32_t ramStart;
	uint32_t ramEnd;
	char _14[0x20];
	uint32_t systemHeapSize;
	char _38[0x40];
	uint32_t textStart;
	uint32_t _7C;
	uint32_t textSize;
	uint32_t dataStart;
	uint32_t _88;
	uint32_t dataSize;
	uint32_t loadStart;
	uint32_t _94;
	uint32_t loadSize;
	char _9C[0xC];
};

struct OSTitleInfoEx {
	OSTitleInfo info;
	uint64_t osVersionId;
};

// OSDynLoad
struct OSDynLoad_NotifyData {
	const char *path;
	uint32_t textAddr;
	uint32_t textOffset;
	uint32_t textSize;
	uint32_t dataAddr;
	uint32_t dataOffset;
	uint32_t dataSize;
	uint32_t readAddr;
	uint32_t readOffset;
	uint32_t readSize;
};

struct OSDynLoad_RPLInfo {
	uint32_t handle;
	uint32_t _4;
	const char *name;
	char _C[0x1C];
	OSDynLoad_NotifyData *notifyData;
	void *entryPoint;
	char _30[0x24];
	OSDynLoad_RPLInfo *next;
	char _58[0x3C];
};

// Thread / mutex / context
struct OSThread;
struct OSMutex;
struct OSAlarm;

struct OSContext {
	uint64_t tag;
	
	uint32_t gpr[32];

	uint32_t cr;
	uint32_t lr;
	uint32_t ctr;
	uint32_t xer;
	
	uint32_t srr0;
	uint32_t srr1;
	
	uint32_t dsisr;
	uint32_t dar;
	
	char _A8[0xC];
	
	uint32_t fpscr;
	double fpr[32];
	
	uint16_t spinLockCount;
	uint16_t state;
	
	uint32_t gqr[8];
	
	uint32_t _1DC;
	
	double psf[32];
	
	uint64_t coretime[3];
	uint64_t starttime;
	
	uint32_t error;
	
	uint32_t _304;
	
	uint32_t pmc1;
	uint32_t pmc2;
	uint32_t pmc3;
	uint32_t pmc4;
	uint32_t mmcr0;
	uint32_t mmcr1;
};

struct OSThreadQueue {
	OSThread *head;
	OSThread *tail;
	void *parent;
	uint32_t _C;
};

struct OSThreadLink {
	OSThread *next;
	OSThread *prev;
};

struct OSMutexLink {
	OSMutex *next;
	OSMutex *prev;
};

struct OSMutexQueue {
	OSMutex *head;
	OSMutex *tail;
	void *parent;
	uint32_t _C;
};

struct OSMutex {
	uint32_t tag;
	const char *name;
	uint32_t _8;
	
	OSThreadQueue queue;
	OSThread *thread;
	int count;
	OSMutexLink link;
};

typedef int (*OSThreadFunc)(int argc, void *argv);

struct OSThread {
	OSContext context;
	
	uint32_t tag;

	uint8_t state;
	uint8_t attr;
	uint16_t id;
	uint32_t suspendCounter;
	
	int priority;
	int basePriority;

	int exitValue;
	
	char _338[0x24];
	
	OSThreadQueue *queue;
	OSThreadLink link;
	
	OSThreadQueue joinQueue;
	
	OSMutex *mutex;
	OSMutexQueue mutexQueue;
	
	OSThreadLink activeLink;
	
	void *stackBase;
	void *stackEnd;
	
	OSThreadFunc entryPoint;
	
	char _3A0[0x57C - 0x3A0];
	
	void *specific[0x10];
	
	int type;
	
	const char *name;
	
	char _5C4[0x6A0 - 0x5C4];
	
};

// Messages
enum OSMessageFlags {
	OS_MESSAGE_FLAGS_NONE = 0,
	OS_MESSAGE_FLAGS_BLOCKING = 1
};

struct OSMessage {
	uint32_t message;
	uint32_t args[3];
};

struct OSMessageQueue {
	uint32_t tag;
	const char *name;
	uint32_t _8;
	OSThreadQueue sendQueue;
	OSThreadQueue recvQueue;
	OSMessage *messages;
	uint32_t size;
	uint32_t first;
	uint32_t used;
};

// Alarms
struct OSAlarmQueue {
	uint32_t tag;
	const char *name;
	uint32_t _8;
	
	OSThreadQueue threadQueue;
	OSAlarm *head;
	OSAlarm *tail;
};

struct OSAlarmLink {
	OSAlarm *prev;
	OSAlarm *next;
};

typedef void (*OSAlarmCallback)(OSAlarm *alarm, OSContext *context);

struct OSAlarm {
	uint32_t tag;
	const char *name;
	uint32_t _8;
	OSAlarmCallback callback;
	uint32_t group;
	uint32_t _14;
	uint64_t nextFire;
	OSAlarmLink link;
	uint64_t period;
	uint64_t start;
	void *userData;
	uint32_t state;
	OSThreadQueue threadQueue;
	OSAlarmQueue *alarmQueue;
	OSContext *context;
};

// PPC disassembly
typedef void (*DisassemblyPrintFn)(const char *fmt, ...);
typedef uint32_t (*DisassemblyFindSymbolFn)(uint32_t addr, char *buffer, size_t bufsize);

enum DisassemblyFlags {
	DISASSEMBLY_FLAGS_NONE = 0,
	DISASSEMBLY_FLAGS_SIMPLIFY = 1,
	DISASSEMBLY_FLAGS_SPACE = 0x20,
	DISASSEMBLY_FLAGS_PLAIN = 0x40,
	DISASSEMBLY_FLAGS_NO_OPCODE = 0x80,
	DISASSEMBLY_FLAGS_PRINT_SYMBOLS = 0x100
};

// Exceptions
enum OSExceptionMode {
	OS_EXCEPTION_MODE_THREAD = 1,
	OS_EXCEPTION_MODE_GLOBAL = 2,
	OS_EXCEPTION_MODE_THREAD_ALL_CORES = 3,
	OS_EXCEPTION_MODE_GLOBAL_ALL_CORES = 4
};

enum OSExceptionType {
	OS_EXCEPTION_TYPE_DSI = 2,
	OS_EXCEPTION_TYPE_ISI = 3,
	OS_EXCEPTION_TYPE_PROGRAM = 6
};

typedef bool (*OSExceptionCallback)(OSContext *context);

// File system
enum FSMode {
	FS_MODE_READ_OWNER = 0x400,
	FS_MODE_WRITE_OWNER = 0x200,
	FS_MODE_EXEC_OWNER = 0x100,
	
	FS_MODE_READ_GROUP = 0x040,
	FS_MODE_WRITE_GROUP = 0x020,
	FS_MODE_EXEC_GROUP = 0x010,
	
	FS_MODE_READ_OTHER = 0x004,
	FS_MODE_WRITE_OTHER = 0x002,
	FS_MODE_EXEC_OTHER = 0x001
};

enum FSStatFlags {
	FS_STAT_DIRECTORY = 0x80000000
};

enum FSMountSourceType {
	FS_MOUNT_SOURCE_SD = 0
};

struct FSClient {
	char data[0x1700];
};

struct FSCmdBlock {
	char data[0xA80];
};

struct FSMountSource {
	char data[0x300];
};

struct __attribute__((packed)) FSStat {
	FSStatFlags flags;
	FSMode mode;
	uint32_t owner;
	uint32_t group;
	uint32_t size;
	char _14[0xC];
	uint32_t entryId;
	int64_t created;
	int64_t modified;
	char _34[0x30];
};

struct FSDirectoryEntry {
	FSStat info;
	char name[256];
};

// MCP
struct MCPTitleListType {
	uint64_t titleId;
	uint32_t _4;
	char path[56];
	uint32_t appType;
	char _48[0xC];
	uint8_t device;
	char _55;
	char indexedDevice[10];
	uint8_t _60;
};

// Function pointers
extern int (*OSDynLoad_Acquire)(const char *name, uint32_t *handle);
extern int (*OSDynLoad_FindExport)(uint32_t handle, bool isData, const char *name, void *ptr);
extern int (*OSDynLoad_GetModuleName)(uint32_t handle, char *name, int *size);
extern OSMutex *OSDynLoad_gLoaderLock;

extern bool (*OSIsDebuggerInitialized)();

extern void (*exit)(int result);
extern void (*_Exit)(int result);

extern void (*OSFatal)(const char *msg);

extern uint32_t (*OSGetSymbolName)(uint32_t addr, char *buffer, size_t bufsize);
extern void (*DisassemblePPCRange)(uint32_t start, uint32_t end, DisassemblyPrintFn printFunc, DisassemblyFindSymbolFn symFunc, DisassemblyFlags flags);
extern void (*DisassemblePPCOpcode)(uint32_t addr, void *buffer, size_t bufsize, DisassemblyFindSymbolFn symFunc, DisassemblyFlags flags);

extern int (*OSSetExceptionCallback)(OSExceptionType type, OSExceptionCallback callback);
extern int (*OSSetExceptionCallbackEx)(OSExceptionMode mode, OSExceptionType type, OSExceptionCallback callback);
extern void (*OSLoadContext)(OSContext *context);

extern int (*OSDisableInterrupts)();
extern void (*OSRestoreInterrupts)(int state);

extern void (*__OSLockScheduler)(void *);
extern void (*__OSUnlockScheduler)(void *);

extern void (*OSInitMutex)(OSMutex *mutex);
extern void (*OSLockMutex)(OSMutex *mutex);
extern void (*OSUnlockMutex)(OSMutex *mutex);

extern void (*OSInitMessageQueue)(OSMessageQueue *queue, OSMessage *messages, int count);
extern bool (*OSSendMessage)(OSMessageQueue *queue, OSMessage *message, OSMessageFlags flags);
extern bool (*OSReceiveMessage)(OSMessageQueue *queue, OSMessage *message, OSMessageFlags flags);

extern void (*OSCreateAlarm)(OSAlarm *alarm);
extern bool (*OSSetAlarm)(OSAlarm *alarm, uint64_t timeout, OSAlarmCallback callback);
extern void (*OSCancelAlarm)(OSAlarm *alarm);
extern bool (*OSWaitAlarm)(OSAlarm *alarm);

extern OSThread *(*OSGetCurrentThread)();
extern OSThread *(*OSGetDefaultThread)(int core);
extern bool (*OSCreateThread)(OSThread *thread, OSThreadFunc func, int argc, void *argv, void *stack, uint32_t stackSize, int priority, int attr);
extern int (*OSResumeThread)(OSThread *thread);
extern bool (*OSJoinThread)(OSThread *thread, int *result);
extern void (*OSExitThread)(int result);
extern const char *(*OSGetThreadName)(OSThread *thread);
extern void (*OSSetThreadName)(OSThread *thread, const char *name);
extern uint32_t (*OSGetThreadAffinity)(OSThread *thread);
extern int (*OSGetThreadPriority)(OSThread *thread);

extern OSSystemInfo *(*OSGetSystemInfo)();
extern void (*OSSleepTicks)(uint64_t ticks);

extern uint64_t (*OSGetTitleID)();

extern int (*OSGetMemBound)(OSMemoryType type, uint32_t *startPtr, uint32_t *sizePtr);
extern uint32_t (*OSEffectiveToPhysical)(uint32_t addr);

extern void (*OSScreenInit)();
extern uint32_t (*OSScreenGetBufferSizeEx)(int screen);
extern void (*OSScreenSetBufferEx)(int screen, void *buffer);
extern void (*OSScreenEnableEx)(int screen, bool enabled);
extern void (*OSScreenClearBufferEx)(int screen, uint32_t color);
extern void (*OSScreenFlipBuffersEx)(int screen);
extern void (*OSScreenPutPixelEx)(int screen, int x, int y, uint32_t color);
extern void (*OSScreenPutFontEx)(int screen, int x, int y, const char *text);

extern void (*DCFlushRange)(const void *buffer, uint32_t length);
extern void (*DCInvalidateRange)(const void *buffer, uint32_t length);
extern void (*ICInvalidateRange)(const void *buffer, uint32_t length);

extern int (*IOS_Open)(const char *path, int mode);
extern int (*IOS_Ioctl)(int fd, uint32_t request, const void *inptr, uint32_t inlen, void *outptr, uint32_t outlen);
extern int (*IOS_Close)(int fd);

extern int (*FSInit)();
extern int (*FSAddClient)(FSClient *client, uint32_t flags);
extern int (*FSInitCmdBlock)(FSCmdBlock *block);
extern int (*FSGetMountSource)(FSClient *client, FSCmdBlock *block, FSMountSourceType type, FSMountSource *source, uint32_t flags);
extern int (*FSMount)(FSClient *client, FSCmdBlock *block, FSMountSource *source, char *path, uint32_t bytes, uint32_t flags);
extern int (*FSMakeDir)(FSClient *client, FSCmdBlock *block, const char *path, uint32_t flags);
extern int (*FSChangeDir)(FSClient *client, FSCmdBlock *block, const char *path, uint32_t flags);
extern int (*FSGetCwd)(FSClient *client, FSCmdBlock *block, char *path, int length, uint32_t flags);
extern int (*FSOpenDir)(FSClient *client, FSCmdBlock *block, const char *path, int *handle, uint32_t flags);
extern int (*FSReadDir)(FSClient *client, FSCmdBlock *block, int handle, FSDirectoryEntry *entry, uint32_t flags);
extern int (*FSCloseDir)(FSClient *client, FSCmdBlock *block, int handle, uint32_t flags);
extern int (*FSOpenFile)(FSClient *client, FSCmdBlock *block, const char *path, const char *mode, int *handle, uint32_t flags);
extern int (*FSGetStatFile)(FSClient *client, FSCmdBlock *block, int handle, FSStat *stat, uint32_t flags);
extern int (*FSReadFile)(FSClient *client, FSCmdBlock *block, void *buffer, int size, int count, int handle, int flag, uint32_t flags);
extern int (*FSWriteFile)(FSClient *client, FSCmdBlock *block, const void *buffer, int size, int count, int handle, int flag, uint32_t flags);
extern int (*FSCloseFile)(FSClient *client, FSCmdBlock *block, int handle, uint32_t flags);
extern int (*FSGetStat)(FSClient *client, FSCmdBlock *block, const char *path, FSStat *stat, uint32_t flags);
extern int (*FSRename)(FSClient *client, FSCmdBlock *block, const char *oldPath, const char *newPath, uint32_t flags);
extern int (*FSRemove)(FSClient *client, FSCmdBlock *block, const char *path, uint32_t flags);
extern int (*FSDelClient)(FSClient *client, uint32_t flags);
extern void (*FSShutdown)();

extern int (*MCP_Open)();
extern int (*MCP_GetDeviceId)(int handle, uint32_t *deviceId);
extern int (*MCP_TitleList)(int handle, uint32_t *count, MCPTitleListType *list, uint32_t size);
extern int (*MCP_TitleListByAppType)(int handle, uint32_t appType, uint32_t *count, MCPTitleListType *list, uint32_t size);
extern int (*MCP_TitleListByDevice)(int handle, const char *device, uint32_t *count, MCPTitleListType *list, uint32_t size);
extern void (*MCP_Close)(int handle);

extern void (*__KernelGetInfo)(KernelInfoType type, void *buffer, uint32_t size, uint32_t unk);

extern int (*snprintf)(char *str, size_t size, const char *format, ...);

extern void *(*MEMGetBaseHeapHandle)(int type);
extern uint32_t (*MEMGetAllocatableSizeForExpHeapEx)(void *handle, int alignment);

extern void *(**pMEMAllocFromDefaultHeap)(uint32_t size);
extern void *(**pMEMAllocFromDefaultHeapEx)(uint32_t size, int alignment);
extern void  (**pMEMFreeToDefaultHeap)(void *ptr);
#define MEMAllocFromDefaultHeap (*pMEMAllocFromDefaultHeap)
#define MEMAllocFromDefaultHeapEx (*pMEMAllocFromDefaultHeapEx)
#define MEMFreeToDefaultHeap (*pMEMFreeToDefaultHeap)

// Internal
extern OSDynLoad_RPLInfo **pMainRPL;
extern OSDynLoad_RPLInfo **pFirstRPL;
extern OSThread **pThreadList;
#define MainRPL (*pMainRPL)
#define FirstRPL (*pFirstRPL)
#define ThreadList (*pThreadList)

void coreinitInitialize();
