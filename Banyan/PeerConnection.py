import socket
import struct

if __name__ is not None and "." in __name__:
    from .Config import BANYAN_VERSION, CONN_PORT
    from .BanyanLogger import BanyanLogger
else:
    from Config import BANYAN_VERSION, CONN_PORT
    from BanyanLogger import BanyanLogger

logger = BanyanLogger.get_logger(__name__, stdout=True)


class PeerConnection:
    def __init__(self, peer_addr):
        logger.info("Connecting peer {}".format(peer_addr))
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((peer_addr, CONN_PORT))
        logger.info("Connected peer {}".format(peer_addr))
        self.sock_file = self.sock.makefile("rw", 0)

    def pack(self, message_type, data):
        data_len = len(data)
        stuff = struct.pack("!I4sL{0}s".format(data_len), BANYAN_VERSION, message_type, data_len, data)
        return stuff

    def send(self, message_type, data):
        stuff = self.pack(message_type, data)
        self.sock_file.write(stuff)
        self.sock_file.flush()

    def receive(self):
        banyan_version = self.sock_file.read(4)
        banyan_version = int(struct.unpack("!I", banyan_version)[0])
        logger.info("Banyan version : " + str(banyan_version))
        if banyan_version == BANYAN_VERSION:
            message_type = self.sock_file.read(4)
            logger.log(message_type + " recieved")
            data_len = self.sock_file.read(4)
            data_len = int(struct.unpack("!L", data_len)[0])
            data = ""

            while len(data) != data_len:
                segment = self.sock_file.read(min(2048, data_len - len(data)))
                if not len(data):
                    break
                data += segment

            if len(data) != data_len:
                return None, None

            return message_type, data

        return None, None


def __del__(self):
    self.sock_file.close()
