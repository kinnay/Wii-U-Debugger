
#include "cafe/coreinit.h"
#include <cstdint>

namespace nn::act {
	uint32_t (*Initialize)();
	uint8_t (*GetSlotNo)();
	uint32_t (*GetPersistentIdEx)(uint8_t slot);
	uint32_t (*Finalize)();
}

void nnactInitialize() {
	uint32_t handle;
	OSDynLoad_Acquire("nn_act.rpl", &handle);
	
	OSDynLoad_FindExport(handle, false, "Initialize__Q2_2nn3actFv", &nn::act::Initialize);
	OSDynLoad_FindExport(handle, false, "GetSlotNo__Q2_2nn3actFv", &nn::act::GetSlotNo);
	OSDynLoad_FindExport(handle, false, "GetPersistentIdEx__Q2_2nn3actFUc", &nn::act::GetPersistentIdEx);
	OSDynLoad_FindExport(handle, false, "Finalize__Q2_2nn3actFv", &nn::act::Finalize);
}
