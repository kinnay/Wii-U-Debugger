
#include "cafe/nsysnet.h"
#include "cafe/coreinit.h"
#include <cstdint>

int (*socket_lib_init)();
int (*inet_aton)(const char *ip, uint32_t *addr);
int (*socket)(int domain, int type, int protocol);
int (*setsockopt)(int socket, int level, int optname, void *optval, int optlen);
int (*connect)(int socket, sockaddr *addr, int addrlen);
int (*bind)(int socket, sockaddr *addr, int addrlen);
int (*listen)(int socket, int backlog);
int (*accept)(int socket, sockaddr *addr, int *addrlen);
int (*send)(int socket, const void *buffer, int size, int flags);
int (*recv)(int socket, void *buffer, int size, int flags);
int (*socketclose)(int socket);
int (*socket_lib_finish)();

void nsysnetInitialize() {
	uint32_t handle;
	OSDynLoad_Acquire("nsysnet.rpl", &handle);
	
	OSDynLoad_FindExport(handle, false, "socket_lib_init", &socket_lib_init);
	OSDynLoad_FindExport(handle, false, "inet_aton", &inet_aton);
	OSDynLoad_FindExport(handle, false, "socket", &socket);
	OSDynLoad_FindExport(handle, false, "setsockopt", &setsockopt);
	OSDynLoad_FindExport(handle, false, "connect", &connect);
	OSDynLoad_FindExport(handle, false, "bind", &bind);
	OSDynLoad_FindExport(handle, false, "listen", &listen);
	OSDynLoad_FindExport(handle, false, "accept", &accept);
	OSDynLoad_FindExport(handle, false, "send", &send);
	OSDynLoad_FindExport(handle, false, "recv", &recv);
	OSDynLoad_FindExport(handle, false, "socketclose", &socketclose);
	OSDynLoad_FindExport(handle, false, "socket_lib_finish", &socket_lib_finish);
}
