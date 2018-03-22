#include "Socket.h"
#include <string>
#include <fcntl.h>
#include <cstring>
#include <iostream>

Socket::Socket() {
    sockfd = -1;
}

bool Socket::create() {
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (!is_valid())
        return false;
    int on = 1;
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, (const char *) &on, sizeof(on)) == -1)
        return false;

    return true;
}

bool Socket::bind(const int port) {
    if (is_valid())
        return false;

    host_addr.sin_family = AF_INET;
    host_addr.sin_addr.s_addr = INADDR_ANY;
    host_addr.sin_port = htons(port);

    int bind_return = ::bind(sockfd, (struct sockaddr *) &host_addr, sizeof(host_addr));

    return bind_return != -1;
}

bool Socket::listen() {
    if (!is_valid()) {
        return false;
    }
    int listen_return = ::listen(sockfd, MAXCONNECTIONS);

    return listen_return != -1;

}

bool Socket::accept(Socket &new_socket) {
    int addr_length = sizeof(host_addr);
    new_socket.sockfd = ::accept(sockfd, (sockaddr *) &host_addr, (socklen_t *) &addr_length);

    if (new_socket.sockfd <= 0)
        return false;
    else
        return true;
}


bool Socket::send(const std::string s) const {
    int status = ::send(sockfd, s.c_str(), s.size(), MSG_NOSIGNAL);
    return status != -1;
}


int Socket::recv(std::string &s) const {
    char buf[MAXRECV + 1];

    s = "";

    memset(buf, 0, MAXRECV + 1);

    int status = ::recv(sockfd, buf, MAXRECV, 0);

    if (status == -1) {
        std::cout << "status == -1   errno == " << errno << "  in Socket::recv\n";
        return 0;
    } else if (status == 0) {
        return 0;
    } else {
        s = buf;
        return status;
    }
}


bool Socket::connect(const std::string host, const int port) {
    if (!is_valid()) return false;

    host_addr.sin_family = AF_INET;
    host_addr.sin_port = htons(port);

    int status = inet_pton(AF_INET, host.c_str(), &host_addr.sin_addr);

    if (errno == EAFNOSUPPORT) return false;

    status = ::connect(sockfd, (sockaddr *) &host_addr, sizeof(host_addr));

    return status == 0;
}

void Socket::set_non_blocking(const bool b) {

    int opts;

    opts = fcntl(sockfd, F_GETFL);

    if (opts < 0)
        return;

    if (b)
        opts = (opts | O_NONBLOCK);
    else
        opts = (opts & ~O_NONBLOCK);

    fcntl(sockfd,
          F_SETFL, opts);

}
