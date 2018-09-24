
#include <cstdint>

namespace nn::act {
	extern uint32_t (*Initialize)();
	extern uint8_t (*GetSlotNo)();
	extern uint32_t (*GetPersistentIdEx)(uint8_t slot);
	extern uint32_t (*Finalize)();
}

void nnactInitialize();
