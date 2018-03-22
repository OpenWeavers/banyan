#ifndef BANYAN_SOCKET_H
#define BANYAN_SOCKET_H

#include <string>
#include <netinet/in.h>
#include <arpa/inet.h>

const int MAXHOSTNAME = 200;
const int MAXCONNECTIONS = 5;
const int MAXRECV = 500;


class Socket    {
private:
    int sockfd;
    sockaddr_in host_addr;
public:
    Socket();
    virtual ~Socket();

    bool create();
    bool bind(const int port);
    bool listen();
    bool accept (Socket&);
    bool connect(const std::string host, const int port);
    bool send(const std::string ) const;
    int recv(std::string&) const;


    void set_non_blocking ( const bool );
    bool is_valid() const { return sockfd != -1; }

};

#endif //BANYAN_SOCKET_H
