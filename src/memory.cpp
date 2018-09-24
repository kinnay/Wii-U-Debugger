
#include "cafe/coreinit.h"

#include <cstddef>

void * operator new(size_t size) {
	return MEMAllocFromDefaultHeap(size);
}

void * operator new[](size_t size) {
	return MEMAllocFromDefaultHeap(size);
}

void * operator new(size_t size, int alignment) {
	return MEMAllocFromDefaultHeapEx(size, alignment);
}

void * operator new[](size_t size, int alignment) {
	return MEMAllocFromDefaultHeapEx(size, alignment);
}

void operator delete(void *ptr) {
	MEMFreeToDefaultHeap(ptr);
}

void operator delete(void *ptr, size_t size) {
	MEMFreeToDefaultHeap(ptr);
}
