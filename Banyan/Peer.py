import json
import socket
from threading import Thread

if __name__ is not None and "." in __name__:
    from .BanyanLogger import BanyanLogger
    from .Config import BCAST_PORT, CONN_PORT
    from .PeerConnection import PeerConnection
else:
    from BanyanLogger import BanyanLogger
    from Config import BCAST_PORT, CONN_PORT
    from PeerConnection import PeerConnection

logger = BanyanLogger.get_logger("Banyan.Peer", stdout=True)


def get_host_ip():
    return [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in
            [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]


class Peer:
    def __init__(self, name):
        self.name = name
        logger.info('Initializing Banyan in your local network...')
        self.bcast_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bcast_soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.bcast_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bcast_soc.bind(('', BCAST_PORT))
        self.conn_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn_soc.bind(('', CONN_PORT))
        self.conn_soc.listen(5)

        self.handlers = {}
        self.peer_list = {}

        # self.bcast_recv_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.bcast_recv_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.bcast_recv_soc.bind(('', BCAST_RECV))
        logger.info("Started at " + get_host_ip() + ":" + str(CONN_PORT))

    def add_peer(self, addr, data):
        if addr[0] not in self.peer_list.keys():
            json_data = json.loads(data)
            self.peer_list[addr[0]] = json_data['name']
            logger.info("Added {} to peer list".format(json_data['name']))

    def discover(self):
        self.bcast_soc.sendto(b'PING', ('255.255.255.255', BCAST_PORT))

    def receive_bcast(self):
        while True:
            msg, addr = self.bcast_soc.recvfrom(1024)
            if addr[0] != get_host_ip():
                logger.info("Broadcast from " + addr[0])
                # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # s.connect((addr[0], CONN_PORT))
                # s.sendall(b'PONG')
                # data = s.recv(1024)
                # s.close()
                peer = PeerConnection(addr[0])
                peer.send("PONG", json.dumps({'name': self.name}))

                print(msg, addr)

    def get_packet(self):
        while True:
            conn, addr = self.conn_soc.accept()
            print("Got message from {0} ".format(addr))
            # msg = conn.recv(1024)
            # conn.close()
            # print(msg)
            peer = PeerConnection(addr[0], sock=conn)
            message_type, data = peer.receive()
            print(message_type + " : " + data)
            del peer
            if message_type == 'PONG':
                self.add_peer(addr, data)

    def send_to_peer(self, peer_addr, message_type, data):
        p = PeerConnection(peer_addr)
        p.send(message_type, data)
        reply = p.receive()

    def __del__(self):
        self.bcast_soc.close()
        self.conn_soc.close()


if __name__ == '__main__':
    p = Peer("BitBot")
    Thread(target=p.get_packet).start()
    Thread(target=p.receive_bcast).start()
    while True:
        s = input("discover again")
        p.discover()
