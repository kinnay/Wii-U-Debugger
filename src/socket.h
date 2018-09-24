
#pragma once

#include <cstddef>

class Socket {
public:
	enum Type {
		TCP,
		UDP
	};
	
	Socket();
	~Socket();
	bool init(Type type);
	bool close();

	int sock;
};

class Client : public Socket {
public:
	bool sendall(const void *data, size_t length);
	bool recvall(void *data, size_t length);
};

class Server : public Socket {
public:
	bool bind(int port);
	bool accept(Client *client);
};
