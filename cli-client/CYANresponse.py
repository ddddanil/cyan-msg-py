import re
from argparse import FileType

ALLOWED_CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-/'
CURRENT_VERSION = '0.1'
first_line_re = r'CYAN ([0-9](?:\.[0-9])+)'
# Group 1 - version
second_line_re = r'(BIN|ACK|ERR) (u[0-9]{6})\s?((?:/[a-zA-Z0-9_]+)(/[a-zA-Z0-9_]+)?)?'
# Group 1 - type
# Group 2 - user
# Group 3 - resource
header_re = r'([a-zA-Z0-9\-/])\:([a-zA-Z0-9\-/])'
# Group 1 - key
# Group 2 - value

class MalformedResponse(Exception):
    def __init__(self, message=None):
        super().__init__()
        self.message = message

    def __str__(self):
        transform = "Malformed Response"
        if self.message:
            transform += f" {self.message}"
        return transform

class Response():
    def __init__(self, raw_data:bytes):
        self.raw_bytes = raw_data
        self.response = {}
        self.raw_head = ''
        self.file = b''

        self.parse()

    def parse(self):
        parts = self.raw_bytes.split('::', 1)
        self.raw_head = lines = parts[0].decode('ascii').split('\n')
        self.file = parts[1]

        for i, line in enumerate(lines):
            if i == 0:
                match = re.search(first_line_re, line) 
                if not match:
                    raise MalformedResponse
                elif match.group(1) != CURRENT_VERSION:
                    raise NotImplementedError
            elif i == 1:
                match = re.search(second_line_re, line)
                if not match:
                    raise MalformedResponse
                self.response["RESP-TYPE"] = match.group(1)
                self.response["USER"] = match.group(2)
                if self.response["RESP-TYPE"] in ["BIN", "ACK"]:
                    self.response["RESOURCE"] = match.group(3)
            elif i == len(lines) - 1:
                if self.response["RESP-TYPE"] == "BIN" and line.strip() != "BIN":
                    raise MalformedResponse
            else:
                match = re.search(header_re, line)
                if not match:
                    raise MalformedResponse
                self.response[match.group(1)] = match.group(2)

    def save_file(self, file:FileType('wb')):
        if self.file:
            file.write(self.file)
            file.close()
