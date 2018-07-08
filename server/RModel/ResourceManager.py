import json
import random
import SessionManager

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
                data = json.loads(request['BIN'])
                print(data)
                # one time token for GET /login
                token = self.gen_token()
                SessionManager.TOKENS[token] = 0
                return {
                    'USER': 'u000001',
                    'RESOURCE': '/user/u000001',
                    'USER-TOKEN': token,
                    'TYPE': request['TYPE'],
                    'CHECKSUM': request['CHECKSUM'],
                    'LENGTH': request['LENGTH'],
                }
        else:
            pass

    @staticmethod
    def gen_token():
        token = ''
        for i in range(64):
            token += random.choice(ALLOWED_TOKEN_CHARACTERS)
        return token
