import socket
import struct

if __name__ is not None and "." in __name__:
    from .Config import BANYAN_VERSION, CONN_PORT
    from .BanyanLogger import BanyanLogger
else:
    from Config import BANYAN_VERSION, CONN_PORT
    from BanyanLogger import BanyanLogger

logger = BanyanLogger.get_logger("Banyan.PeerConnection", stdout=True)


class PeerConnection:
    def __init__(self, peer_addr: str, sock: socket.socket = None):
        self.peer_addr = peer_addr
        logger.debug("Connecting peer {}".format(peer_addr))
        if not sock:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((peer_addr, CONN_PORT))
        else:
            self.sock = sock

        logger.debug("Connected peer {}".format(peer_addr))
        self.sock_file = self.sock.makefile("rwb", 0)
        self.peer_addr = peer_addr
        self.temp_info = ''

    def pack(self, message_type: str, data: str):
        data_len = len(data)
        if message_type != "REPL":
            bytes_data = str.encode(data)
        else:
            bytes_data = data
        bytes_message_type = str.encode(message_type)
        stuff = struct.pack("!I4sL{0}s".format(data_len), BANYAN_VERSION, bytes_message_type, data_len, bytes_data)
        return stuff

    def send(self, message_type: str, data: str):
        stuff = self.pack(message_type, data)
        self.sock_file.write(stuff)
        self.sock_file.flush()

    def receive(self):
        banyan_version = self.sock_file.read(4)
        banyan_version = int(struct.unpack("!I", banyan_version)[0])
        logger.debug("Banyan version : " + str(banyan_version))
        if banyan_version == BANYAN_VERSION:
            message_type = self.sock_file.read(4)
            logger.debug(message_type.decode() + " received from {0}:{1}".format(self.peer_addr, CONN_PORT))
            data_len = self.sock_file.read(4)
            data_len = int(struct.unpack("!L", data_len)[0])
            # print(data_len)
            data = b''

            while len(data) != data_len:
                segment = self.sock_file.read(min(2048, data_len - len(data)))
                if not len(segment):
                    break
                data += segment
            if len(data) != data_len:
                return None, None
            message_type = message_type.decode()
            if message_type != "REPL":
                data = data.decode()
            return message_type, data
        else:
            logger.warning("Invalid message received from {0}:{1}".format(self.peer_addr, CONN_PORT))
            return None, None

    def __del__(self):
        if self.sock_file:
            self.sock_file.close()
        if self.sock:
            self.sock.close()
