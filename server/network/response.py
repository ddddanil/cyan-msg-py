from request import ALLOWED_CYAN_VERSION

ALLOWED_CYAN_VERSION = ALLOWED_CYAN_VERSION.decode('ascii')

class ErrResponse:

    def __init__(self, code, desc):
        self.code = code
        self.desc = desc

    def __bytes__(self):
        """
        :return: bytes like
         CYAN 0.1
         ERR u0001
         CODE:403
         TEXT:Forbidden
         ::
        """
        # CYAN {ALLOWED_CYAN_VERSION}
        # ERR
        # CODE:{self.code}
        # TEXT:{self.desc}
        # ::
        return f'CYAN {ALLOWED_CYAN_VERSION}\nERR\nCODE:{self.code}\nTEXT:{self.desc}\n::\n'.encode()


class AckResponse:

    def __init__(self, headers):
        self.headers = headers

    def __bytes__(self):
        # CYAN 0.1
        # ACK u0001 /resources/_ID_of_new_file_
        # TYPE:video
        # CHECKSUM:hash_of_binary
        # LENGTH:543210
        # TIME-SENT:880880654
        # CODE:200
        # USER-TOKEN:deadbeebcafe
        # ::
        return (
                f'CYAN {ALLOWED_CYAN_VERSION}\nACK {self.headers["USER"]} {self.headers["RESOURCE"]}\n'
                f'TYPE"{self.headers["TYPE"]}\nCHECKSUM:{self.headers["CHECKSUM"]}\nLENGTH:{self.headers["LENGTH"]}\n' +
                (f'CODE:{self.headers["CODE"]}\n' if self.headers.get("CODE") else '') +
                (f'USER-TOKEN:{self.headers["USER-TOKEN"]}' if self.headers.get("USER-TOKEN") else '') +
                '::\n'
        ).encode()


class BinResponse:

    def __init__(self, headers):
        self.headers = headers

    def __bytes__(self):
        # CYAN 0.1
        # BIN u0001 /resources/_ID_of_new_file_
        # TYPE:video
        # CHECKSUM:hash_of_binary
        # SENDER:u0002
        # TIME-SENT:880880654
        # LENGTH:543210
        # READ-STATUS:0
        # CODE:200
        # ::
        return (
                f'CYAN {ALLOWED_CYAN_VERSION}\nBIN {self.headers["USER"]} {self.headers["RESOURCE"]}\n'
                f'TYPE"{self.headers["TYPE"]}\nCHECKSUM:{self.headers["CHECKSUM"]}\nSENDER:{self.headers["SENDER"]}\n'
                f'TIME-SENT:{self.headers["TIME-SENT"]}\nLENGTH:{self.headers["LENGTH"]}\n' +
                (f'READ-STATUS:{self.headers["READ-STATUS"]}\n' if self.headers.get("READ-STATUS") else '') +
                (f'CODE:{self.headers["CODE"]}\n' if self.headers.get("CODE") else '') +
                f'BIN::\n'
        ).encode() + self.headers["BIN"]
