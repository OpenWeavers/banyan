import socket
from threading import Thread

from .Logger import logger
from .Config import BCAST_PORT, CONN_PORT
from .PeerConnection import PeerConnection


def get_host_ip():
    return [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]


class Peer:
    def __init__(self):
        logger.info('Initializing Banyan in your local network...')
        self.bcast_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bcast_soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.bcast_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bcast_soc.bind(('', BCAST_PORT))
        self.conn_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn_soc.bind(('', CONN_PORT))
        self.conn_soc.listen(5)
        #self.bcast_recv_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.bcast_recv_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self.bcast_recv_soc.bind(('', BCAST_RECV))
        logger.info("Started at " + get_host_ip() + ":" + str(CONN_PORT))

    def discover(self):
        self.bcast_soc.sendto(b'PING', ('255.255.255.255', BCAST_PORT))

    def recieve_bcast(self):
        while True:
            msg, addr = self.bcast_soc.recvfrom(1024)
            if addr[0] != get_host_ip():
                logger.info("Broadcast from " + addr[0])
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((addr[0], CONN_PORT))
                s.sendall(b'PONG')
                #data = s.recv(1024)
                s.close()
                print(msg, addr)

    def get_packet(self):
        conn, addr = self.conn_soc.accept()
        print("Got message from {0} ".format(addr))
        msg = conn.recv(1024)
        conn.close()
        print(msg)

    def send_to_peer(self, peer_addr, message_type, data):
        p = PeerConnection(peer_addr)
        p.send(message_type, data)
        reply = p.recieve()

    def __del__(self):
        self.bcast_soc.close()
        self.conn_soc.close()


if __name__ == '__main__':
    p = Peer()
    Thread(target=p.get_packet).start()
    Thread(target=p.recieve_bcast).start()
    p.discover()
    del p
