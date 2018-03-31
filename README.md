# Banyan
Banyan is a simple P2P application protocol

# What can it do currently?
- File Sharing over LAN

# How it works?
The workflow is organized as follows
1. Initialization - Peer Starts up with a friendly name, which is visible on local network
2. Peer Discovery - Peer Sends a broadcast to all other hosts in local network. Other peers will respond to it.
3. Synchronization - Peer Receives file list from all other Peers
4. Transfer - Peer can receive file from any other Peer

# Requirements
- Python 3.6 or later
- Couple of machines to work with and test

# Documentation

Run as

    python BanyanInterface.py

It will open up an interactive shell

Command List


|Command     | Options | Description |
|------------|---------|-------------|
| `init`       | `name [max_conn=5] [bcast_ip=255.255.255.255]` | Starts the Peer |
| `discover`   | -       | Discovers other Peers in Current Network |
| `sync`       | -       | Gets the list of Publicly Available Files |
| `who`        | -       | View the list of Peers in the same network |
| `ls`         | `[name]`  | Lists the files of the Peer name. If not given, Lists all Peers files|
| `status`     | -       | View the status of current Peer |
| `download`   | `peername filename` | Downloads the file |
| `exit`       | -       | Go out of Banyan Shell |

# Future Work
- Efficient Peer Discovery Methods (other than Broadcast)
- Efficient File Transfer Approach (now the peek speed is around 1.6 Mbps over LAN)
- Extending the service to Internet


