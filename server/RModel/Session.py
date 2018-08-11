import asyncio
import logging
import os
import socket
import time
import aioredis
import uvloop
from pickle import loads, dumps
from RModel.ResourceManager import ResourceManager
from RModel.config import redis_address
# 24 hours
TIMEOUT_SECONDS = 86400
logger = logging.getLogger('RModel.Session')


class BaseSession:

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.resource_manager = ResourceManager()
        self.redis = None
        self.db = None

    async def recv_request(self, sock, addr):
        raw_request = b''
        # get size of new request
        raw_size = await self.loop.sock_recv(sock, 4)
        # connection close
        if not raw_size:
            return None
        size = int.from_bytes(raw_size, 'big')
        logger.debug(f'New request\'s size = {size}')
        # get this request
        while len(raw_request) < size:
            needed_size = min(size - len(raw_request), 1024)
            raw_request += await self.loop.sock_recv(sock, needed_size)
        request: dict = loads(raw_request)
        request['ORIGIN'] = (sock, addr)
        if request.get('TARGET'):
            request['RESOURCE'] = request['TARGET']
        logger.info(f"New request from {addr}")
        logger.debug(f"{request}")
        return request

    async def process_request(self, request):
        func, require = self.resource_manager[(request['REQ-TYPE'], request['RESOURCE'])]
        try:
            headers = {}
            for key in require:
                if key in ('DB', 'REDIS'):
                    continue
                headers[key] = request[key]
        except KeyError:
            await self.respond(request['ORIGIN'], {'RESP-TYPE': 'ERR', 'CODE': 400, 'TEXT': 'NOT ALL HEADERS'})
            return

        if 'REDIS' in require and not self.redis:
            self.redis = await aioredis.create_redis(redis_address)
        if 'DB' in require and not self.db:
            pass
            # TODO DataServer
            # self.db = await self.loop.sock_connect()
        result = await func(headers, redis=self.redis, db=self.db)
        logger.debug(result)
        if request['REQ-TYPE'] == 'POST':
            result.update({
                'RESP-TYPE': 'ACK',
                'RESOURCE': request['RESOURCE'],
            })

        elif request['REQ-TYPE'] == 'GET':
            result.update({
                'RESP-TYPE': 'BIN',
                'USER': request['USER'],
                'TYPE': request['ACCEPT-TYPE'],
                'RESOURCE': request['RESOURCE'],
                'CHECKSUM': 'CorgiOneLove',
                'SENDER': result.get('SENDER', request['USER']),
                'TIME-SENT': int(time.time()),
                'LENGTH': len(result['BIN'])
            })
        else:
            result = {
                'RESP-TYPE': 'ERR',
                'CODE': 405,
                'TEXT': 'METHOD NOT ALLOWED'
            }
        await self.respond(request['ORIGIN'], result)

    async def respond(self, origin, headers):
        if not headers['RESP-TYPE']:
            raise ValueError

        logger.info(f"Pushing response")
        # logger.debug(f"Response is {headers}")

        header_bytes = dumps(headers)
        header_length = len(header_bytes)
        header_result = header_length.to_bytes(4, 'big') + header_bytes
        sock, addr = origin
        await self.loop.sock_sendall(sock, header_result)
        logger.debug('Response was send')


############################################


class OneTimeSession(BaseSession):

    def __init__(self, sock: socket.socket, addr):
        super().__init__()
        self.sock = sock
        self.addr = addr
        logger.info(f'one time session to {addr}')
        asyncio.ensure_future(self.handle_client())

    async def handle_client(self):
        request = await self.recv_request(self.sock, self.addr)
        if not request:
            logger.info('lose connection')
            return
        logger.debug('new request from solver')
        await self.process_request(request)
        self.sock.close()
        logger.info('one time session died')


#############################################


class TokenSession(BaseSession):

    def __init__(self, sock: socket.socket, addr, token):
        super().__init__()
        self.requests_queue = asyncio.Queue()
        self.token = token
        self.process_request_lock = asyncio.Lock()
        self.connection_list = [(sock, addr)]
        logger.info(f'new connection to session({self.token}) from {addr}')
        self.tasks = [
            asyncio.ensure_future(self.handle_connection(sock, addr)),
            asyncio.ensure_future(self.process_requests()),
            asyncio.ensure_future(self.die()),
        ]

    async def receive_connection(self, sock, addr):
        logger.info(f'new connection to session({self.token}) from {addr}')
        self.connection_list.append((sock, addr))
        self.tasks.append(asyncio.ensure_future(self.handle_connection(sock, addr)))

    async def handle_connection(self, sock, addr):
        while True:
            request = await self.recv_request(sock, addr)
            if not request:
                logger.info('lose connection')
                sock.close()
                return
            request['ORIGIN'] = (sock, addr)
            logger.info(f'new request for ({self.token}) from {addr}')
            await self.requests_queue.put(request)

    async def process_requests(self):
        logger.debug('process requests start...')
        while True:
            logger.debug('wait request from queue')
            request = await self.requests_queue.get()
            logger.debug('new request')
            await self.process_request_lock.acquire()
            logger.debug('processing request...')
            await self.process_request(request)
            self.process_request_lock.release()
            logger.debug('successfully send send request')

    async def die(self):
        logger.debug(f'die ({self.token}) start')
        # sleep 24 hours
        await asyncio.sleep(TIMEOUT_SECONDS)
        await self.process_request_lock.acquire()
        logger.info(f'This session({self.token}) is going to die')
        while not self.requests_queue.empty():
            request = await self.requests_queue.get()
            await self.respond(request['ORIGIN'],
                               {'RESP-TYPE': 'ERR', 'CODE': 304, 'TEXT': "Repeat request due to timeout"})

        # cancel all running tasks
        for task in self.tasks:
            task.canсel()

        for sock, addr in self.connection_list:
            sock.close()


if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    # server = Session("0.0.0.0", 12347, NAMED)
    # asyncio.ensure_future(server.recieve_connection())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()
    loop.close()
