import asyncio
import os
import socket
import uvloop
from pickle import loads, dumps
from functools import wraps
from async_timeout import timeout

UNNAMED = 0
NAMED = 1

TIMEOUT_SECONDS = 86400

def run_while_alive(func):
        @wraps(func)
        async def new_function(self, *args, **kwargs):
            async with timeout(TIMEOUT_SECONDS):
                while True:
                    await self.check_death()
                    if not self.alive:
                        return
                    self.loop.call_soon(func(self, *args, **kwargs))
        return new_function


class Session:

    def __init__(self, sock, addr, death_type=UNNAMED, *args, **kwargs):
        self.type = death_type

        self.response_counter = 0
        self.alive = True
        self.connection_list = [(sock, addr)]
        self.request_queue = asyncio.Queue()
        self.loop = asyncio.get_event_loop()

        asyncio.ensure_future(self.handle_connection(sock, addr))
    
    async def recieve_connection(self, sock, addr):
        self.connection_list.append((sock, addr))
        asyncio.ensure_future(self.handle_connection(sock, addr))

    @run_while_alive
    async def handle_connection(self, sock, addr):
        raw_request = b''
        # get size of new request
        size = int.from_bytes(await self.loop.sock_recv(sock, 4), 'big')
        # get this request
        while len(raw_request) < size:
            needed_size = min(size - len(raw_request), 1024)
            raw_request += await self.loop.sock_recv(sock, needed_size)
        request = loads(raw_request)
        request['ORIGIN'] = (sock, addr)
        await self.request_queue.put(request)

    @run_while_alive
    async def process_requests(self):
        request = await self.request_queue.get()
        # TODO Process request
        response = None
        if request['REQ-TYPE'] is 'POST':
            response = {
                'RESP-TYPE': 'ACK',
                'USER': request['USER'],
                'RESOURCE': request['RESOURCE'],
                'TYPE': request['TYPE'],
                'CHECKSUM': request['CHECKSUM'],
                'LENGTH': request['LENGTH'],
                'CODE': 200
            }
        elif request['REQ-TYPE'] is 'GET':
            response = {
                'RESP-TYPE': 'BIN',
                'USER': request['USER'],
                'RESOURCE': request['RESOURCE'],
                'TYPE': request['TYPE'],
                'CHECKSUM': 'IloveCats',
                'LENGTH': 19,
                'CODE': 200,
                'SENDER': 'u000000',
                'TIME-SENT': 88008800,
                'BIN': b'You did a great job'
            }
        if not response:
            raise ValueError
        await self.respond(request['ORIGIN'], response)
        self.response_counter += 1

    async def check_death(self):
        if self.type is UNNAMED:
            if self.response_counter != 0:
                await self.die()
                return
        elif self.type is NAMED:
            pass # TODO timeouts

    async def die(self):
        try:
            while True:
                request = self.request_queue.get_nowait()
                await self.respond(request['ORIGIN'], {'RESP-TYPE': 'ERR', 'CODE': 304, 'TEXT': "Repeat request due to timeout"})
        except asyncio.QueueEmpty:
            pass
        
        for sock, addr in self.connection_list:
            sock.close()
        
        self.alive = False
        return

    async def respond(self, origin, headers):
        if not headers['RESP-TYPE']:
            raise ValueError

        header_bytes = dumps(headers)
        header_length = len(header_bytes)
        header_result = header_length.to_bytes(4, 'big') + header_bytes
        sock, addr = origin
        await self.loop.sock_sendall(sock, header_result)


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
