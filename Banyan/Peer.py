import socket
from threading import Thread

CONN_PORT = 5000
BCAST_PORT = 5001
BCAST_RECV = 5002


class Peer:
    def __init__(self):
        self.bcast_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bcast_soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.bcast_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn_soc.bind(('', CONN_PORT))
        self.conn_soc.listen(5)
        self.bcast_recv_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bcast_recv_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bcast_recv_soc.bind(('', BCAST_RECV))

    def discover(self):
        self.bcast_soc.sendto(b'this is a broadcast', ('255.255.255.255', BCAST_RECV))

    # Should handle case where broadcast by itself should not be catched!
    def recieve_bcast(self):
        msg, addr = self.bcast_recv_soc.recvfrom(1024)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((addr[0], 5000))
        s.sendall(b'ALIVE:Hey this is a bot!')
        data = s.recv(1024)
        s.close()
        print(msg, addr)

    def get_packet(self):
        conn, addr = self.conn_soc.accept()
        print("Got message from {0} ".format(addr))
        msg = conn.recv(1024)
        print(msg)

    def __del__(self):
        self.bcast_soc.close()
        self.conn_soc.close()


if __name__ == '__main__':
    p = Peer()
    Thread(target=p.get_packet).start()
    Thread(target=p.recieve_bcast).start()
    del p
