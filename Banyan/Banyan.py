import json
from pathlib import Path
from threading import Thread

if __name__ is not None and "." in __name__:
    from .Peer import Peer
    from .PeerConnection import PeerConnection
else:
    from Peer import Peer
    from PeerConnection import PeerConnection

INSERTPEER = "PONG"
QUERYFILELIST = "QFLL"
REPLYFILELIST = "RFLL"
GETFILE = "GETF"
PING = "PING"
PONG = "PONG"

REPLY = "REPL"
ERROR = "ERRR"


class Banyan:
    def __init__(self, max_peers, bcast_ip="255.255.255.255"):
        self.peer = Peer("BitBot", bcast_ip)
        self.max_peers = max_peers
        Thread(target=self.peer.get_packet).start()
        Thread(target=self.peer.receive_bcast).start()
        self.handlers = {
            INSERTPEER: self.handle_insert_peer,
            QUERYFILELIST: self.handle_query_file_list,
            REPLYFILELIST: self.handle_reply_file_list,
            GETFILE: self.handle_get_file,
            PING: self.handle_ping
        }

        for message_type in self.handlers:
            self.peer.add_handlers(message_type, self.handlers[message_type])

        self.files_available = {}
        self.local_files = []

        self.home_path = Path.home()
        #if Path.is_dir(self.home_path / 'BanyanWatchDirectory'):
        Path.mkdir(self.home_path / 'BanyanWatchDirectory', exist_ok=True)
        self.watch_directory = self.home_path / 'BanyanWatchDirectory'

    def get_local_files(self):
        if Path.is_dir(self.watch_directory):
            self.local_files = [(child, Path(child).stat().st_size) for child in Path(self.watch_directory).iterdir() if Path.is_file(child)]
            return self.local_files

    def handle_insert_peer(self, peer_conn):
        if self.no_of_peers >= self.max_peers:
            return False

        self.peer.add_peer(peer_conn.peer_addr)
        return True

    def handle_query_file_list(self, peer_conn):
        files = self.get_local_files()
        peer_conn.send(REPLYFILELIST, json.dumps(files))

    def handle_reply_file_list(self, peer_conn, data):
        files = json.loads(data)
        self.files_available[peer_conn.peer_addr]  = [file for file in files]

    def handle_get_file(self, peer_conn, filename):
        if filename not in self.get_local_files():
            peer_conn.send(ERROR, "{} not found".format(filename))

        fd = open(filename, 'r')
        data = ''
        while True:
            segment = fd.read(2048)
            if not len(segment):
                break
            data += segment
        fd.close()

        peer_conn.send(REPLY, data)

    def handle_ping(self, peer_conn):
        peer_conn.send(PONG, '')

    def check_life(self, peer_conn):
        peer_conn.send(PING, '')
        message_type, data = peer_conn.receive()
        if message_type == 'PONG':
            return True
        del self.peer.peer_list[peer_conn.peer_addr]
        return False

    def update_peers(self):
        self.peer.discover()


if __name__ == '__main__':
    app = Banyan(5)
