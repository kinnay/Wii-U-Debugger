
#pragma once

#include <cstddef>

void *operator new(size_t size, int alignment);
void *operator new[](size_t size, int alignment);
