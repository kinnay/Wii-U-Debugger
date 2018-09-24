
#include "cafe/coreinit.h"

void DumpContext(OSContext *context, const char *excType) {
	char buffer[1000];
	snprintf(buffer, 1000,
		"%s exception occurred!\n"
		"r0 :%08X r1 :%08X r2 :%08X r3 :%08X r4 :%08X\n"
		"r5 :%08X r6 :%08X r7 :%08X r8 :%08X r9 :%08X\n"
		"r10:%08X r11:%08X r12:%08X r13:%08X r14:%08X\n"
		"r15:%08X r16:%08X r17:%08X r18:%08X r19:%08X\n"
		"r20:%08X r21:%08X r22:%08X r23:%08X r24:%08X\n"
		"r25:%08X r26:%08X r27:%08X r28:%08X r29:%08X\n"
		"r30:%08X r31:%08X LR :%08X CTR:%08X XER:%08X\n"
		"\n"
		"SRR0:%08X SRR1:%08X DSISR:%08X DAR:%08X",
		excType,
		context->gpr[0], context->gpr[1], context->gpr[2], context->gpr[3],
		context->gpr[4], context->gpr[5], context->gpr[6], context->gpr[7],
		context->gpr[8], context->gpr[9], context->gpr[10], context->gpr[11],
		context->gpr[12], context->gpr[13], context->gpr[14], context->gpr[15],
		context->gpr[16], context->gpr[17], context->gpr[18], context->gpr[19],
		context->gpr[20], context->gpr[21], context->gpr[22], context->gpr[23],
		context->gpr[24], context->gpr[25], context->gpr[26], context->gpr[27],
		context->gpr[28], context->gpr[29], context->gpr[30], context->gpr[31],
		context->lr, context->ctr, context->xer, context->srr0, context->srr1,
		context->dsisr, context->dar
	);
	OSFatal(buffer);
}

bool DSIHandler(OSContext *context) {
	DumpContext(context, "A DSI");
	return false;
}

bool ISIHandler(OSContext *context) {
	DumpContext(context, "An ISI");
	return false;
}

bool ProgramHandler(OSContext *context) {
	DumpContext(context, "A program");
	return false;
}

void InstallExceptionHandlers() {
	OSSetExceptionCallbackEx(OS_EXCEPTION_MODE_GLOBAL_ALL_CORES, OS_EXCEPTION_TYPE_DSI, DSIHandler);
	OSSetExceptionCallbackEx(OS_EXCEPTION_MODE_GLOBAL_ALL_CORES, OS_EXCEPTION_TYPE_ISI, ISIHandler);
	OSSetExceptionCallbackEx(OS_EXCEPTION_MODE_GLOBAL_ALL_CORES, OS_EXCEPTION_TYPE_PROGRAM, ProgramHandler);
}
