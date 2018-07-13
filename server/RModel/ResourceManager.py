import json
import random
import SessionManager
import time
import aioredis

ALLOWED_TOKEN_CHARACTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


class ResourceManager:

    def __init__(self):
        self.db = None
        self.redis = None

    async def redis_connect(self):
        self.redis: aioredis = await aioredis.create_redis(('localhost', 6379))
        # db = await bla bla

    async def check(self, req_type, user, res) -> tuple:
        """
        :return demands for this request
        :param req_type:
        :param user:
        :param res:
        :return:
        """
        if req_type == 'POST':
            if res == '/login':
                return (
                    'USER', 'BIN',
                )

        elif req_type == 'GET':
            if res == '/login':
                return (
                    'USER-TOKEN',
                )

    async def solve(self, headers):
        if not self.redis:
            await self.redis_connect()
        if headers['REQ-TYPE'] == 'POST':
            if headers['RESOURCE'][0] == 'g':
                pass # TODO check that user in group

            elif headers['RESOURCE'] == '/login':
                # TODO check login and password, get id of this user
                data = json.loads(headers['BIN'].decode())
                # one time token for GET /login
                token = self.gen_token()
                await self.redis.set(f'token:{token}', 0)
                return {
                    'USER': 'u000001',
                    'USER-TOKEN': token,
                }
        else:
            if headers['RESOURCE'] == '/login':
                token = self.gen_token()
                # 24 hours token
                print(token)
                await self.redis.set(f'token:{token}', 1, expire=86400)
                token_json = json.dumps({'TOKEN': token}).encode()
                return {
                    'BIN': token_json
                }

    @staticmethod
    def gen_token(length=64):
        token = ''
        for i in range(length):
            token += random.choice(ALLOWED_TOKEN_CHARACTERS)
        return token
