import socket
import re

logger = None
ip_regex = re.compile(r"((?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}):(\d+)")
# Group 0 - Whole
# Group 1 - ip
# Group 2 - port 

def str_to_ip(address:str):
    match = ip_regex.search(address)
    return (match.group(1), int(match.group(2)))

class Connection():
    def __init__(self, server):
        self.server_address_full = server
        self.server_addr = str_to_ip(server)
        self.server_ip, self.server_port = self.server_addr
        self.socket = socket.socket()

    def try_send(self, data:bytes):
        logger.debug("Sending to server")
        while True:
            try:
                bytes_sent = self.socket.send(data)
            except OSError:
                logger.debug("Reconnecting...")
                self.socket.connect(self.server_addr)
            else:
                if bytes_sent != len(data):
                    raise ConnectionError
                else:
                    break

    def try_recieve(self):
        logger.debug("Receiving from server")
        while True:
            data = b''
            try:
                bytes_recv = self.socket.recv(1024)
                if not bytes_recv: break
                data += bytes_recv
            except OSError:
                logger.debug("Reconnecting...")
                self.socket.connect(self.server_addr)
        return data

    def exchange(self, request:bytes):
        self.try_send(request)
        bytes_recv = self.try_recieve()
        return bytes_recv