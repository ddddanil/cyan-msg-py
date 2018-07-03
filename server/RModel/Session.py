import asyncio
import os
import socket
import uvloop
from pickle import loads
from functools import wraps


UNNAMED = 0
NAMED = 1


def run_while_alive(func):
        @wraps(func)
        async def new_function(self, *args, **kwargs):
            while True:
                self.check_death()
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
        size = int.from_bytes(await self.loop.sock_recv(sock, 4), 'big')
        while len(raw_request) < size:
            needed_size = min(size - len(raw_request), 1024)
            raw_request += await self.loop.sock_recv(sock, needed_size)

        await self.request_queue.put(loads(raw_request))

    @run_while_alive
    async def process_requests(self):
        request = await self.request_queue.get()
        # Process request
        self.respond(request) # TODO respond
        self.response_counter += 1

    def check_death(self):
        if self.type is UNNAMED:
            if self.response_counter != 0:
                return self.die()
        elif self.type is NAMED:
            pass # TODO timeouts

    def die(self):
        try:
            while True:
                request = self.request_queue.get_nowait()
                self.respond(request, 'ERR', 304, "Repeat request due to timeout")
        except asyncio.QueueEmpty:
            pass
        
        for sock, addr in self.connection_list:
            sock.close()
        
        self.alive = False
        return

    def respond(self, request, type='ERR', code=500, msg=''):
        pass
        # raise NotImplementedError


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
