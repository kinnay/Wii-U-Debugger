
#include "cafe/coreinit.h"

#include <cstdint>

#define KERN_SYSCALL_TBL1 0xFFE84C70 //Unknown
#define KERN_SYSCALL_TBL2 0xFFE85070 //Games
#define KERN_SYSCALL_TBL3 0xFFE85470 //Loader
#define KERN_SYSCALL_TBL4 0xFFEAAA60 //Home menu
#define KERN_SYSCALL_TBL5 0xFFEAAE60 //Browser

extern "C" void SCKernelCopyData(uint32_t dst, uint32_t src, uint32_t len);
extern "C" void KernelCopyData(uint32_t dst, uint32_t src, uint32_t len);

void KernelWrite(uint32_t addr, const void *data, uint32_t length) {
	uint32_t dst = OSEffectiveToPhysical(addr);
	uint32_t src = OSEffectiveToPhysical((uint32_t)data);
	KernelCopyData(dst, src, length);
	DCFlushRange((void *)addr, length);
	ICInvalidateRange((void *)addr, length);
}

void KernelWriteU32(uint32_t addr, uint32_t value) {
	uint32_t dst = OSEffectiveToPhysical(addr);
	uint32_t src = OSEffectiveToPhysical((uint32_t)&value);
	KernelCopyData(dst, src, 4);
	DCFlushRange((void *)addr, 4);
	ICInvalidateRange((void *)addr, 4);
}

/* Write a 32-bit word with kernel permissions */
void __attribute__ ((noinline)) kern_write(uint32_t addr, uint32_t value)
{
	asm volatile (
		"li 3,1\n"
		"li 4,0\n"
		"mr 5,%1\n"
		"li 6,0\n"
		"li 7,0\n"
		"lis 8,1\n"
		"mr 9,%0\n"
		"mr %1,1\n"
		"li 0,0x3500\n"
		"sc\n"
		"nop\n"
		"mr 1,%1\n"
		:
		:	"r"(addr), "r"(value)
		:	"memory", "ctr", "lr", "0", "3", "4", "5", "6", "7", "8", "9", "10",
			"11", "12"
		);
}

void PatchSyscall(int index, uint32_t addr) {
	kern_write(KERN_SYSCALL_TBL1 + index * 4, addr);
	kern_write(KERN_SYSCALL_TBL2 + index * 4, addr);
	kern_write(KERN_SYSCALL_TBL3 + index * 4, addr);
	kern_write(KERN_SYSCALL_TBL4 + index * 4, addr);
	kern_write(KERN_SYSCALL_TBL5 + index * 4, addr);
}

void kernelInitialize() {
	PatchSyscall(0x25, (uint32_t)SCKernelCopyData);
}
