
#pragma once

#include <cstdint>

#define AF_INET 2

#define SOCK_STREAM 1
#define SOCK_DGRAM 2

#define IPPROTO_TCP 6
#define IPPROTO_UDP 17

#define SOL_SOCKET -1
#define SO_REUSEADDR 4

struct sockaddr {
	uint16_t family;
	uint16_t port;
	uint32_t addr;
	char zero[8];
};

extern int (*socket_lib_init)();
extern int (*inet_aton)(const char *ip, uint32_t *addr);
extern int (*socket)(int domain, int type, int protocol);
extern int (*setsockopt)(int socket, int level, int optname, void *optval, int optlen);
extern int (*connect)(int socket, sockaddr *addr, int addrlen);
extern int (*bind)(int socket, sockaddr *addr, int addrlen);
extern int (*listen)(int socket, int backlog);
extern int (*accept)(int socket, sockaddr *addr, int *addrlen);
extern int (*send)(int socket, const void *buffer, int size, int flags);
extern int (*recv)(int socket, void *buffer, int size, int flags);
extern int (*socketclose)(int socket);
extern int (*socket_lib_finish)();

void nsysnetInitialize();
