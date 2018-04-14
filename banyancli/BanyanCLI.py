import cmd
import os
from pathlib import Path

if __name__ is not None and "." in __name__:
    from .Banyan import Banyan, QUERYFILELIST, GETFILE
else:
    from Banyan import Banyan, QUERYFILELIST, GETFILE


class BanyanShell(cmd.Cmd):
    intro = """
    Banyan Command Line Shell v1
    -------------------------------------
    Developed and Maintained By OpenWeavers
    
    Project: https://github.com/OpenWeavers/banyan
    
    Type "help" or "?" for list of commands
    
    Type "exit" to exit
    """
    prompt = '~> '
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
        print("{0:^16} {1:^16}".format("IP", "Name"))
        print("-" * 32)
        for peer in self.app.peer.peer_list:
            print("{0:16} {1:^15}".format(peer, self.app.peer.peer_list[peer]))
        print()

    def do_sync(self, args):
        """Retrieves the file list from each peer"""
        if not self.is_okay(args):
            return
        for peer in self.app.peer.peer_list:
            print("Syncing with {0}".format(peer))
            self.app.peer.send_to_peer(peer, QUERYFILELIST, '')
        print()

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
                print("Peer Name : {0}".format(self.app.peer.peer_list[ip]))
                print("{0:^15} \t {1:^10}".format("Name", "Size"))
                print("-" * 36)
                for (file, size) in file_list:
                    print("{0:15} \t {1:10}K".format(file, size // 1024))
        else:
            ip = [x for x in self.app.peer.peer_list if self.app.peer.peer_list[x] == args[0].strip()]
            try:
                print("{0:^15} \t {1:^10}".format("Name", "Size"))
                print("-" * 36)
                for (file, size) in self.app.files_available[ip[0]]:
                    print("{0:15} \t {1:10}K".format(file, size // 1024))
            except IndexError:
                print("{} not in Peer List".format(args[0]))
        print()

    def do_status(self, args):
        """View Current Status of Banyan Client"""
        if not self.is_okay(args, arglen=0):
            return
        print("Banyan Watch Directory : {}".format(self.app.watch_directory))
        print("Banyan Download Directory : {}".format(self.app.download_directory))
        print("\n")
        print("Local File List")
        print("{0:^15} \t {1:^10}".format("Name", "Size"))
        print("-" * 36)
        for child in Path(self.app.watch_directory).iterdir():
            if Path.is_file(child):
                print("{0:15} \t {1:10}K".format(child.name, Path(child).stat().st_size // 1024))
        print("\n")
        print("Downloads List")
        print("{0:^15} \t {1:^10}".format("Name", "Size"))
        print("-" * 36)
        for child in Path(self.app.download_directory).iterdir():
            if Path.is_file(child):
                print("{0:15} \t {1:10}K".format(child.name, Path(child).stat().st_size // 1024))
        print()

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
        print("Download Successful\n")

    def complete_download(self, text, line, begin_idx, end_idx):
        parts = line.split()
        partlen = len(parts) - 1
        peer_names = self.app.peer.peer_list.values()
        if partlen == 0 or (partlen == 1 and begin_idx != end_idx):
            return [x for x in peer_names if x.startswith(text)]
        elif (partlen == 1 and begin_idx == end_idx) or partlen == 2:
            ip = [x for x in self.app.peer.peer_list if self.app.peer.peer_list[x] == parts[1].strip()]
            if len(ip) == 0:
                return []
            return [x[0] for x in self.app.files_available[ip[0]] if x[0].startswith(text)]

    def emptyline(self):
        pass

    def do_search(self, args):
        """
        Searches a file from the available file list and prints its peers.

        Syntax:
        search filename

        Usage:
        search t.pdf
        """
        args = self.parse(args)
        if not self.is_okay(args, arglen=1):
            return
        results = []
        for peer in self.app.peer.peer_list.keys():
            [results.append([file[0], peer]) for file in self.app.files_available[peer] \
             if args[0] in file[0] or file[0] in args[0]]
        if len(results) == 0:
            print("0 search results found!")
        else:
            print("{} search results found!\n".format(len(results)))
            print("{:20} {:20}".format('Files', 'Peers'))
            print("-"*40)
            [print("{:20} {:20}".format(file[0], file[1])) for file in results]

    def complete_search(self, text, line, begin_idx, end_idx):
        files = []
        for peer in self.app.peer.peer_list:
            [files.append(file[0]) for file in self.app.files_available[peer] if text in file[0] or file[0] in text]
        return files

    def do_shell(self, s):
        """
        Execute shell commands. Also '!' Prefix can be used

        Syntax:
            shell cmd
            !cmd

        Example:
            shell ls
            !ls -l
        """
        os.system(s)

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

    def do_exit(self, s):
        """Exit from the Banyan Shell"""
        #raise KeyboardInterrupt
        copy = self.app
        del copy
        return True

    def do_run(self, args):
        """
        Runs specified script in interactive shell

        Syntax:
            run filename

        Example:
            run .banyanrc
        """
        args = self.parse(args)
        if not self.is_okay(args, check_app=False, arglen=2):
            return
        try:
            with open(args[0], 'r') as f:
                self.cmdqueue += [x for x in f.readlines()]
        except IOError:
            print("Error while opening {0}".format(args[0]))

    def complete_run(self, text, line, begin_idx, end_idx):
        return [x for x in os.listdir(os.getcwd()) if x.startswith(text)]

    do_EOF = do_exit


def main():
    BanyanShell().cmdloop()


if __name__ == '__main__':
    main()
