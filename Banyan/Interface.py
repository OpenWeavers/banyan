import cmd
from pathlib import Path

if __name__ is not None and "." in __name__:
    from .Banyan import Banyan, QUERYFILELIST, GETFILE
else:
    from Banyan import Banyan, QUERYFILELIST, GETFILE


class BanyanShell(cmd.Cmd):
    intro = """
    Banyan Command Line Shell v0.1
    -------------------------------------
    Developed and Maintained By OpenWeavers
    
    Visit https://openweavers.github.io/banyan for details
    
    Type "help" or "?" for list of commands
    
    Type "exit" to exit
    """
    prompt = '(banyan) -> '
    name = None
    app = None
    ruler = '-'

    def do_init(self, arg):
        """
        Initializes the banyan client.

        Syntax:
            init name [max_conn=5] [broadcast_ip=255.255.255.255]

        Example :
            init BitBot
            init BitBot 4
            init BitBot 5 10.24.30.255
        """
        arg = self.parse(arg)
        if len(arg) < 1:
            print("Invalid Usage")
            return
        self.name = arg[0]
        max_conn = arg[1] if len(arg) == 2 else 5
        bcast_ip = arg[2] if len(arg) == 3 else "255.255.255.255"
        if self.app:
            print("An app is already running...Restart the client")
            return
        self.app = Banyan(max_conn, self.name, bcast_ip)
        self.app.get_local_files()

    def do_discover(self, args):
        """Discovers peers in current network"""
        if not self.is_okay(args):
            return
        self.app.update_peers()

    def do_who(self, args):
        """Prints peer list"""
        if not self.is_okay(args):
            return
        print("    IP     | Peer Name    ")
        print("--------------------------")
        for peer in self.app.peer.peer_list:
            print(peer, self.app.peer.peer_list[peer], sep='|')

    def do_sync(self, args):
        """Retrieves the file list from each peer"""
        if not self.is_okay(args):
            return
        for peer in self.app.peer.peer_list:
            self.app.peer.send_to_peer(peer, QUERYFILELIST, '')

    def do_ls(self, args):
        """Lists the files from given name.

        Syntax:
            ls [name]

        Examples:
            ls
            ls MotoBot
        """
        args = self.parse(args)
        if not self.is_okay(args, check_len=False):
            return
        if len(args) == 0:
            for ip, file_list in self.app.files_available.items():
                print("Peer IP : {0}".format(ip))
                for (file, size) in file_list:
                    print("{0} \t {1}".format(file, size))
                print()
        else:
            ip = [x for x in self.app.peer.peer_list if self.app.peer.peer_list[x] == args[0].strip()]
            try:
                print("Name \t Size")
                for (file, size) in self.app.files_available[ip[0]]:
                    print("{0} \t {1}".format(file, size))
            except IndexError:
                print("{} not in Peer List".format(args[0]))

    def do_status(self, args):
        """View Current Status of Banyan Client"""
        if not self.is_okay(args, arglen=0):
            return
        print("Banyan Watch Directory : {}".format(self.app.watch_directory))
        print("Banyan Download Directory : {}".format(self.app.download_directory))
        print("Local File List")
        print("Name \t Size")
        for (file, size) in self.app.local_files:
            print("{0} \t {1}".format(file, size))
        print("Downloads List")
        print("Name \t Size")
        for child in Path(self.app.download_directory).iterdir():
            if Path.is_file(child):
                print("{0} \t {1}".format(child, Path(child).stat().st_size))

    def complete_ls(self, text, line, begin_idx, end_idx):
        return [x for x in self.app.peer.peer_list.values() if x.startswith(text)]

    def do_download(self, args):
        """
        Download a file from specified peer

        Syntax:
            download peername filename

        Usage:
            download BitBot t.pdf
        """
        args = self.parse(args)
        if not self.is_okay(args, arglen=2):
            return
        if args[0] not in self.app.peer.peer_list.values():
            print("Invalid Peer {0}".format(args[0]))
            return
        ip = [x for x in self.app.peer.peer_list if self.app.peer.peer_list[x] == args[0]][0]
        if args[1] not in [x[0] for x in self.app.files_available[ip]]:
            print("Peer {0} does not have File {1}. Try sync again".format(*args))
            return
        print("Please wait while downloading...")
        self.app.peer.send_to_peer(ip, GETFILE, args[1])
        print("Download Successful")

    def emptyline(self):
        pass

    def parse(self, args):
        return [x.strip() for x in args.split()]

    def is_okay(self, args, check_app=True, check_len=True, arglen=0):
        if check_app and not self.app:
            print("App not initialized ... Run init")
            return False
        if check_len and len(args) != arglen:
            print('Invalid Usage')
            return False
        return True

    def can_exit(self):
        return True

    def onecmd(self, line):
        r = super(BanyanShell, self).onecmd(line)
        if r and (self.can_exit() or
                  input('exit anyway ? (yes/no):') == 'yes'):
            return True
        return False

    def do_exit(self, s):
        """Exit from the Banyan Shell"""
        return True

    do_EOF = do_exit


if __name__ == '__main__':
    BanyanShell().cmdloop()
