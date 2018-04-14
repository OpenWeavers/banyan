import pickle
import json
from pathlib import Path
from threading import Thread

if __name__ is not None and "." in __name__:
    from .Peer import Peer
    from .PeerConnection import PeerConnection
    from .BanyanLogger import BanyanLogger
else:
    from Peer import Peer
    from PeerConnection import PeerConnection
    from BanyanLogger import BanyanLogger

INSERTPEER = "PONG"
QUERYFILELIST = "QFLL"
REPLYFILELIST = "RFLL"
GETFILE = "GETF"
PING = "PING"
PONG = "PONG"

REPLY = "REPL"
ERROR = "ERRR"

logger = BanyanLogger.get_logger("Banyan", stdout=False)


class Banyan:
    def __init__(self, max_peers: int, name: str, bcast_ip: str = "255.255.255.255"):
        self.peer = Peer(name, bcast_ip)
        self.max_peers = int(max_peers)
        self.threads = []
        self.threads += [Thread(target=self.peer.peer_listen)]
        self.threads += [Thread(target=self.peer.receive_bcast)]
        for thread in self.threads:
            thread.daemon = True
            thread.start()
        self.handlers = {
            PONG: self.handle_insert_peer,
            QUERYFILELIST: self.handle_query_file_list,
            REPLYFILELIST: self.handle_reply_file_list,
            GETFILE: self.handle_get_file,
            PING: self.handle_ping,
            ERROR: self.handle_error,
            REPLY: self.handle_reply
        }

        for message_type in self.handlers:
            self.peer.add_handlers(message_type, self.handlers[message_type])

        self.files_available = {}
        self.local_files = []
        self.no_of_peers = 0

        self.home_path = Path.home()
        # if Path.is_dir(self.home_path / 'BanyanWatchDirectory'):
        self.watch_directory = self.home_path / 'BanyanWatchDirectory'
        self.download_directory = self.home_path / 'BanyanDownloads'
        Path.mkdir(self.watch_directory, exist_ok=True)
        Path.mkdir(self.download_directory, exist_ok=True)

    def get_local_files(self):
        if Path.is_dir(self.watch_directory):
            self.local_files = [(child.name, Path(child).stat().st_size) for child in
                                Path(self.watch_directory).iterdir() if Path.is_file(child)]
            return self.local_files

    def handle_insert_peer(self, peer_conn: PeerConnection, data: str):
        """
        Handler to Insert Peer
        :param peer_conn: Recieved connection from another Peer
        :param data: Name of another Peer
        :return: Success Value
        """
        if self.no_of_peers >= self.max_peers:
            return False
        peer_name = json.loads(data)['name']
        self.peer.add_peer(peer_conn.peer_addr, peer_name)
        self.no_of_peers += 1
        return True

    def handle_query_file_list(self, peer_conn: PeerConnection, data: str = None):
        file_list = self.get_local_files()
        peer_conn.send(REPLYFILELIST, json.dumps(file_list))

    def handle_reply_file_list(self, peer_conn: PeerConnection, data: str):
        # print("Entered Handle")
        file_list = json.loads(data)
        # print("Data", data)
        self.files_available[peer_conn.peer_addr] = file_list

    def handle_get_file(self, peer_conn: PeerConnection, filename: str):
        local_files = [ele[0] for ele in self.get_local_files()]
        if filename not in local_files:
            peer_conn.send(ERROR, "{} not found".format(filename))
            return

        fd = open(self.watch_directory / filename, 'rb')
        data = fd.read()
        # while True:
        #    segment = fd.read(2048)
        #    if not len(segment):
        #        break
        #    data += segment
        fd.close()
        peer_conn.send(REPLY, data)

    def handle_ping(self, peer_conn: PeerConnection, data: str = None):
        logger.debug('Received Ping from {0}'.format(peer_conn.peer_addr))
        peer_conn.send(PONG, '')

    def handle_error(self, peer_conn: PeerConnection, data: str):
        logger.debug("Error from {0} : {1}".format(peer_conn.peer_addr, data))

    def handle_reply(self, peer_conn: PeerConnection, data: bytes):
        # content = pickle.loads(data)
        content = data
        filename = peer_conn.temp_info
        logger.debug("Recieved File {0} from {1}".format(filename, peer_conn.peer_addr))

        with open(self.download_directory / filename, 'wb') as f:
            f.write(data)

    def check_life(self, peer_addr: str):
        """
        Checks whether a peer is alive or not
        :param peer_addr: IP address of peer
        :return: True if peer is alive else False
        """
        peer_conn = PeerConnection(peer_addr)
        peer_conn.send(PING, '')
        message_type, data = peer_conn.receive()
        if message_type == PONG:
            return True
        del self.peer.peer_list[peer_conn.peer_addr]
        self.no_of_peers -= 1
        return False

    def update_peers(self):
        self.peer.peer_list = {}
        self.no_of_peers = 0
        self.peer.discover()

    def __del__(self):
        #print('jello')
        for thread in self.threads:
            if thread.is_alive:
                #thread.stop()
                pass
        del self.peer


'''
if __name__ == '__main__':
    app = Banyan(5, "BitBot")
    app.update_peers()
    while True:
        # app.update_peers()
        input("again")
        files = app.get_local_files()
        print(files)
        print(app.peer.peer_list)
        print(app.files_available)
        for peer in app.peer.get_peer_list():
            app.peer.send_to_peer(peer, QUERYFILELIST, '')
        print(app.files_available)
        print(app.peer.peer_list)
        app.peer.send_to_peer('192.168.0.104', GETFILE, "twenty.mp4")
'''
