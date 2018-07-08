import fleep
from time import time
from hashlib import sha1

logger = None
CURRENT_VERSION = b'0.1'

def get_cyan_type(magic_bytes: bytes):
    info = fleep.get(magic_bytes)
    file_type = ''

    if 'raster-image' in info.type or \
        'raw-image' in info.type or \
        'vector-image' in info.type:
        file_type = 'img'
    elif 'video' in info.type:
        file_type = 'video'
    elif 'audio' in info.type:
        file_type = 'audio'
    else:
        file_type = 'other'

    return file_type

class Request():
    def __init__(self, req_config: dict):
        self.request = self.make_request(req_config)
        self.bytes = b''

    def __bytes__(self):
        if not self.bytes:
            self.bytes = self.compile_request(self.request)

        return self.bytes

    def compile_request(self, request):
        byte_lines = []

        # 1st line
        byte_lines.append(b'CYAN ' + CURRENT_VERSION)
        # 2nd line
        byte_lines.append(f'{request["REQ-TYPE"]} {request["USER"]} {request["RESOURCE"]}'.encode('ascii'))

        # Headers
        for key, val in request.items():
            if key in ['REQ-TYPE', 'RESOURCE', 'USER', 'BIN']: continue
            byte_lines.append(f'{key}:{val}'.encode('ascii'))
        
        # Last line
        if 'BIN' in request:
            byte_lines.append(b'BIN::')
            byte_lines.append(request['BIN'])
        else:
            byte_lines.append(b'::')

        request_bytes = b''
        for line in byte_lines:
            request_bytes += line + b'\n'

        logger.debug(request_bytes)

        return request_bytes

    def make_request(self, conf):
        request = {}
        if conf["CMD"] == "u":
            file_bytes = conf["FILE"].read()
            request["REQ-TYPE"] = "POST"
            request["USER"] = conf['USER']
            request["RESOURCE"] = ''
            request["USER-TOKEN"] = 'deadbeefcafe' # IMPORTANT! TODO automatic login
            request["TYPE"] = get_cyan_type(file_bytes[:129])
            request["CHECKSUM"] = sha1(file_bytes).hexdigest()
            request["TIME-SENT"] = int(time())
            request["LENGTH"] = len(file_bytes)
            request["TARGET"] = conf["TARGET"]
            request["BIN"] = file_bytes
        elif conf["CMD"] == "d":
            request["REQ-TYPE"] = "GET"
            request["USER"] = conf['USER']
            request["USER-TOKEN"] = 'deadbeefcafe' # IMPORTANT! TODO automatic login
            request["RESOURCE"] = conf["RESOURCE"]
        else:
            raise ValueError("Invalid request type")

        conf["FILE"].close()

        logger.debug(request)

        return request