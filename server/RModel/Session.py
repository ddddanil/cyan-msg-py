import asyncio
import os
import socket
import uvloop
from pickle import loads, dumps
from functools import wraps, partial
from async_timeout import timeout

# 24 hours
TIMEOUT_SECONDS = 86400
logger = None


class BaseSession:

    def __init__(self):
        self.loop = asyncio.get_event_loop()

    async def recv_request(self, sock, addr):
        raw_request = b''
        # get size of new request
        size = int.from_bytes(await self.loop.sock_recv(sock, 4), 'big')
        logger.debug(f'size = {size}')
        # get this request
        while len(raw_request) < size:
            needed_size = min(size - len(raw_request), 1024)
            raw_request += await self.loop.sock_recv(sock, needed_size)
        request = loads(raw_request)
        request['ORIGIN'] = (sock, addr)

        logger.info(f"New request from {addr}")
        logger.debug(f"{request}")
        return request

    async def process_request(self, request):
        # TODO Process request
        response = None
        if request['REQ-TYPE'] == 'POST':
            response = {
                'RESP-TYPE': 'ACK',
                'USER': request['USER'],
                'RESOURCE': request['RESOURCE'],
                'TYPE': request['TYPE'],
                'CHECKSUM': request['CHECKSUM'],
                'LENGTH': request['LENGTH'],
                'CODE': 200
            }
        elif request['REQ-TYPE'] == 'GET':
            response = {
                'RESP-TYPE': 'BIN',
                'USER': request['USER'],
                'RESOURCE': request['RESOURCE'],
                'TYPE': request['ACCEPT-TYPE'],
                'CHECKSUM': 'IloveCats',
                'LENGTH': 19,
                'CODE': 200,
                'SENDER': 'u000000',
                'TIME-SENT': 88008800,
                'BIN': b'You did a great job'
            }
        if not response:
            raise ValueError
        logger.debug(f"Processed\n{request}\nto\n{response}")
        await self.respond(request['ORIGIN'], response)

    async def respond(self, origin, headers):
        if not headers['RESP-TYPE']:
            raise ValueError

        logger.info(f"Pushing response")
        logger.debug(f"Response is {headers}")

        header_bytes = dumps(headers)
        header_length = len(header_bytes)
        header_result = header_length.to_bytes(4, 'big') + header_bytes
        sock, addr = origin
        await self.loop.sock_sendall(sock, header_result)
        logger.debug('Response was send')


class OneTimeSession(BaseSession):

    def __init__(self, sock: socket.socket, addr):
        super().__init__()
        self.sock = sock
        self.addr = addr
        logger.info(f'one time session to {addr}')
        asyncio.ensure_future(self.handle_client())

    async def handle_client(self):
        request = await self.recv_request(self.sock, self.addr)
        logger.debug('new request from solver')
        await self.process_request(request)


class TokenSession(BaseSession):

    def __init__(self, sock: socket.socket, addr, token):
        super().__init__()
        self.requests_queue = asyncio.Queue()
        self.token = token
        self.process_request_lock = asyncio.Lock()
        self.connection_list = [(sock, addr)]
        self.tasks = [
            asyncio.ensure_future(self.handle_connection(sock, addr)),
            asyncio.ensure_future(self.process_requests()),
            asyncio.ensure_future(self.die()),
        ]

    async def recieve_connection(self, sock, addr):
        logger.info(f'new connection to session({self.token}) from {addr}')
        self.connection_list.append((sock, addr))
        self.tasks.append(asyncio.ensure_future(self.handle_connection(sock, addr)))

    async def handle_connection(self, sock, addr):
        while True:
            request = await self.recv_request(sock, addr)
            request['ORIGIN'] = (sock, addr)
            await self.requests_queue.put(request)

    async def process_requests(self):
        while True:
            self.process_request_lock.acquire()
            request = await self.requests_queue.get()
            self.process_request(request)
            self.process_request_lock.release()

    async def die(self):
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
