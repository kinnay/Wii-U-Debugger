
#pragma once

#include <cstdint>

void KernelWrite(uint32_t addr, const void *data, uint32_t length);
void KernelWriteU32(uint32_t addr, uint32_t value);

void PatchSyscall(int index, void *ptr);

void kernelInitialize();
