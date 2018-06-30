from hashlib import sha1
from pprint import pprint
import re


ALLOWED_CHARACTERS = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-/'
ALLOWED_CYAN_VERSION = '0.1'

REQUIRED_GET_HEADERS = ['CYAN', 'REQ_TYPE', 'USER', 'RESOURCE', 'USER-TOKEN']
ACCEPTABLE_GET_HEADER = ['ACCEPT_TYPE', 'LAST_UPDATE']

REQUIRED_POST_HEADERS = ['CYAN', 'REQ_TYPE', 'USER', 'USER-TOKEN', 'TYPE', 'CHECKSUM', 'TIME-SENT', 'LENGTH', 'TARGET']


class ParseError(Exception):
    def __init__(self, description='', code=400):
        self.code = code
        self.description = 'BAD REQUEST\n' + description

    def __str__(self):
        return f"CODE: {self.code}\nDESC: {self.description}"


class Request():

    def __init__(self):
        self.headers = {}
        self.file_name = ''
        self.last_part = b''
        self.headers_part = b''
        self.file_path = b''
        self.file_hash = sha1()

    def add(self, data: bytes):
        if b'::' in data:
            headers_part, file_part = data.split(b'::', 1)
            self.headers_part += headers_part
            self.parse()
        else:
            self.headers_part += data

    def parse(self):
        lines = self.headers_part.split(b'\n')[:-1]
        # check characters
        for num, line in enumerate(lines):
            if num > 1 and line.count(b':') != 1:
                raise ParseError('more than one ":" in {}'.format(line))

            for ch in line:
                if ch not in (ALLOWED_CHARACTERS + b' .' if num < 2 else ALLOWED_CHARACTERS + b':'):
                    raise ParseError(f'invalid character {chr(ch)} in {num} {line.decode()}')

        for num, line in enumerate(lines):

            # Parse string like [CYAN 0.1]
            if num == 0:
                try:
                    name, version = line.split()
                except ValueError:
                    raise ParseError('INVALID FIRST LINE')
                if name != b'CYAN':
                    raise ParseError('INVALID PROTOCOL NAME')

                # Check version for type like [0.1 or 0.2.1 and etc]
                if not re.match(r"[0-9](\.[0-9])+", version.decode('ascii')):
                    raise ParseError('INVALID PROTOCOL VERSION')
                else:
                    self.headers['CYAN'] = version.decode('ascii')

            # Parse string like [GET u000001 /resources/id]
            elif num == 1:
                try:
                    request_type, user, resource = line.split()
                except ValueError:
                    raise ParseError('INVALID SECOND LINE')

                if request_type != b'POST' and request_type != b'GET':
                    raise ParseError('INVALID REQUEST TYPE')

                self.headers['REQ_TYPE'] = request_type.decode('ascii')
                self.headers['USER'] = user.decode('ascii')
                self.headers['RESOURCE'] = resource.decode('ascii')

            # Parse string like [KEY:VALUE]
            else:
                key, value = line.split(b':')
                self.headers[key.decode('ascii')] = value.decode('ascii')

        self.check_headers()

        pprint(self.headers)

    def check_headers(self):
        if self.headers['REQ_TYPE'] == 'GET':
            for required_header in REQUIRED_GET_HEADERS:
                if required_header not in self.headers:
                    raise ParseError(f"THERE ISN'T REQUIRED METHOD {required_header}")

            for key, _ in self.headers.items():
                if key not in REQUIRED_GET_HEADERS + ACCEPTABLE_GET_HEADER:
                    raise ParseError('METHOD NOT ALLOWED', 405)

        else:
            for required_header in REQUIRED_POST_HEADERS:
                if required_header not in self.headers:
                    raise ParseError(f"THERE ISN'T REQUIRED METHOD {required_header}")


if __name__ == '__main__':
    r = Request()
    r.add(
        b"CYAN 0.1\n" +
        b"GET u0001 /resources/0000001\n" +
        b"USER-TOKEN:ADDEFFFFAA0\n" +
        b"ACCEPT-TYPE:text\n" +
        b"::"
    )
