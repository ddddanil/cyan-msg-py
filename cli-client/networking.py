import socket
import re

logger = None
ip_regex = r"((?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}):(\d+)"
# Group 0 - Whole
# Group 1 - ip
# Group 2 - port 

def str_to_ip(address:str):
    match = re.search(ip_regex, address)
    return (match.group(1), int(match.group(2)))

class Connection():
    def __init__(self, server):
        self.server_address_full = server
        self.server_addr = str_to_ip(server)
        self.server_ip, self.server_port = self.server_addr
        self.socket = socket.socket()

    def try_send(self, data:bytes):
        while True:
            try:
                bytes_sent = self.socket.send(data)
            except OSError:
                self.socket.connect(self.server_addr)
            else:
                if bytes_sent != len(data):
                    raise ConnectionError
                else:
                    break

    def try_recieve(self):
        while True:
            data = b''
            try:
                bytes_recv = self.socket.recv(1024)
                if not bytes_recv: break
                data += bytes_recv
            except OSError:
                self.socket.connect(self.server_addr)
        return data

    def exchange(self, request:bytes):
        self.try_send(request)
        bytes_recv = self.try_recieve()
        return bytes_recv