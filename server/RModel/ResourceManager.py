import json
import random
import time
import aioredis
from .config import redis_address
from .resources.resources import Resources

ALLOWED_TOKEN_CHARACTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


class ResourceManager:

    def __init__(self):
        self.db = None
        self.redis = None

    async def redis_connect(self):
        self.redis: aioredis = await aioredis.create_redis(redis_address)
        # db = await bla bla
               
    def new_request(self, resource):
        self.process, self.require = Resources[(request_type, resource)]

    @staticmethod
    def gen_token(length=64):
        token = ''
        for _ in range(length):
            token += random.choice(ALLOWED_TOKEN_CHARACTERS)
        return token
