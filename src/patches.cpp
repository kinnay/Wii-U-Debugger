
#include "cafe/coreinit.h"
#include "kernel.h"

#include <cstdint>

int OSSetExceptionCallback_Patch() {
	return 0;
}

int OSSetExceptionCallbackEx_Patch() {
	return 0;
}

bool OSIsDebuggerInitialized_Patch() {
	return true;
}

void Patch(void *funcPtr, void *patchPtr) {
	OSDynLoad_NotifyData *sectionInfo = MainRPL->notifyData;
	
	uint32_t func = (uint32_t)funcPtr;
	uint32_t patch = (uint32_t)patchPtr;
	if (func < 0x01800000) { //OS function (with trampoline)
		for (uint32_t addr = sectionInfo->textAddr; addr < 0x10000000; addr += 4) {
			uint32_t *instrs = (uint32_t *)addr;
			if (instrs[0] == (0x3D600000 | (func >> 16)) &&     //lis   r11, func@h
			    instrs[1] == (0x616B0000 | (func & 0xFFFF)) &&  //ori   r11, r11, func@l
			    instrs[2] == 0x7D6903A6 &&                      //mtctr r11
			    instrs[3] == 0x4E800420)                        //bctr
			{
				KernelWriteU32(addr, 0x3D600000 | (patch >> 16));        //lis r11, patch@h
				KernelWriteU32(addr + 4, 0x616B0000 | (patch & 0xFFFF)); //ori r11, r11, patch@l
			}
		}
	}
	else { //Dynamic function
		for (uint32_t addr = sectionInfo->textAddr; addr < 0x10000000; addr += 4) {
			uint32_t instr = *(uint32_t *)addr;
			if ((instr & 0xFC000002) == 0x48000000) { //b or bl
				if ((instr & 0x03FFFFFC) == func - addr) {
					instr = instr & ~0x03FFFFFC;
					instr |= patch;
					instr |= 2; //Turn b/bl into ba/bla
					KernelWriteU32(addr, instr);
				}
			}
		}
	}
}

void ApplyPatches() {
	Patch((void *)OSSetExceptionCallback, (void *)OSSetExceptionCallback_Patch);
	Patch((void *)OSSetExceptionCallbackEx, (void *)OSSetExceptionCallbackEx_Patch);
	
	Patch((void *)OSIsDebuggerInitialized, (void *)OSIsDebuggerInitialized_Patch);
}
