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
    def __init__(self, name: str, bcast_ip: str):
        self.name = name
        self.bcast_ip = bcast_ip
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

    def add_handlers(self, message_type: str, handler):
        self.handlers[message_type] = handler

    def add_peer(self, addr: str, data: str):
        """
        Adds a peer to internal dictionary
        :param addr: IP adress of the peer
        :param data: Short name of the peer
        :return: Nothing
        """
        if addr not in self.peer_list.keys():
            self.peer_list[addr] = data
            logger.info("Added {} to peer list".format(data))

    def get_peer_list(self):
        return self.peer_list

    def discover(self):
        self.bcast_soc.sendto(b'PING', (self.bcast_ip, BCAST_PORT))

    def receive_bcast(self):
        try:
            while True:
                msg, addr = self.bcast_soc.recvfrom(1024)
                if addr[0] != get_host_ip():
                    logger.debug("Broadcast from " + addr[0] + "Message :" + msg.decode())
                    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    # s.connect((addr[0], CONN_PORT))
                    # s.sendall(b'PONG')
                    # data = s.recv(1024)
                    # s.close()
                    peer = PeerConnection(addr[0])
                    peer.send("PONG", json.dumps({'name': self.name}))
        except KeyboardInterrupt:
            return

    def peer_listen(self):
        def handle_connection(addr,conn):
            peer = PeerConnection(addr[0], sock=conn)
            (message_type, data_1) = peer.receive()
            logger.debug("Recieved {0} message from {1}:{2} Data: {3}".format(message_type, *addr, data_1))
            # print(message_type + " : " + data_1)
            # del peer
            # Execute the associated Handle
            self.handlers[message_type](peer, data_1)
        try:
            while True:
                conn, addr = self.conn_soc.accept()
                Thread(target=lambda : handle_connection(addr,conn)).start()
        except KeyboardInterrupt:
            return

    def send_to_peer(self, peer_addr: str, message_type: str, data: str):
        peer = PeerConnection(peer_addr)
        if message_type == "GETF":
            peer.temp_info = data
        peer.send(message_type, data)
        received_message_type, reply = peer.receive()
        self.handlers[received_message_type](peer, reply)
        # print(reply)
        # return received_message_type, reply

    def __del__(self):
        self.bcast_soc.close()
        self.conn_soc.close()


'''
if __name__ == '__main__':
    p = Peer("BitBot", "255.255.255.255")
    Thread(target=p.get_packet).start()
    Thread(target=p.receive_bcast).start()
    while True:
        s = input("discover again")
        p.discover()
'''
