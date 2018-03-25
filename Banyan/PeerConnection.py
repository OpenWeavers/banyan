import socket
import struct

if __name__ is not None and "." in __name__:
    from .Config import BANYAN_VERSION, CONN_PORT
else:
    from Config import BANYAN_VERSION, CONN_PORT

class PeerConnection:
    def __init__(self, peer_addr):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((peer_addr, CONN_PORT))
        self.sock_file = self.sock.makefile("rw", 0)

    def pack(self, message_type, data):
        data_len = len(data)
        stuff = struct.pack("!I4sL{0}s".format(data_len), BANYAN_VERSION, message_type, data_len, data)
        return stuff

    def send(self, message_type, data):
        stuff = self.pack(message_type, data)
        self.sock_file.write(stuff)
        self.sock_file.flush()

    def __del__(self):
        self.sock_file.close()
