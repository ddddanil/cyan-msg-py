import json
import random
import SessionManager
import time

ALLOWED_TOKEN_CHARACTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


class ResourceManager:

    def __init__(self):
        self.db_connection = None

    async def process_request(self, request):
        if request['REQ-TYPE'] == 'POST':
            if request['TARGET'][0] == 'g':
                pass # TODO check that user in group
            elif request['TARGET'] == '/login':
                # TODO check login and password, get id of this user
                data = json.loads(request['BIN'].decode())
                print(data)
                # one time token for GET /login
                token = self.gen_token()
                SessionManager.TOKENS[token] = 0
                return {
                    'RESP-TYPE': 'ACK',
                    'USER': 'u000001',
                    'RESOURCE': '/user/u000001',
                    'USER-TOKEN': token,
                    'TIME-SENT': 880880654,
                    'TYPE': request['TYPE'],
                    'CHECKSUM': request['CHECKSUM'],
                    'LENGTH': request['LENGTH'],
                    'CODE': 200
                }
        else:
            token = self.gen_token()
            # 24 hours token
            SessionManager.TOKENS[token] = 1
            token_json = json.dumps({'TOKEN': token}).encode()
            if request['RESOURCE'] == '/login':
                return {
                    'RESP-TYPE': 'BIN',
                    'USER': request['USER'],
                    'RESOURCE': '/login',
                    'TIME-SENT': int(time.time()),
                    'TYPE': 'text',
                    'CHECKSUM': 'Corgi',
                    'SENDER': 'u000000',
                    'LENGTH': len(token_json),
                    'BIN': token_json
                }
            pass

    @staticmethod
    def gen_token():
        token = ''
        for i in range(64):
            token += random.choice(ALLOWED_TOKEN_CHARACTERS)
        return token
