import aioredis
from .config import redis_address
from .resources.resources import ResourcesClass, WrongMethodError
from .resources import *
from logging import getLogger

logger = getLogger("RModel.ResourceManager")

class ResourceManager:

    def __init__(self):
        self.db = None
        self.redis = None
        self.resource = None
        self.resources = ResourcesClass()

    async def redis_connect(self):
        self.redis: aioredis = await aioredis.create_redis(redis_address)
        # db = await bla bla
               
    def new_request(self, request_type, resource):
        self.resource = self.resources[(request_type, resource)]
        logger.debug(f"Resource {request_type} {resource} resolved to {self.resource}")

    def require(self):
        if self.resource is None:
            raise AttributeError
        return self.resource[1]

    async def process(self, *args, **kwargs):
        if self.resource is None:
            raise AttributeError
        await self.resource[0](self.redis, *args, **kwargs)
