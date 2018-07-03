import asyncio
import os
import socket
from pickle import loads
from functools import wraps


UNNAMED = 0
NAMED = 1


class Session:

    def __init__(self, path, death_type=UNNAMED, *args, **kwargs): # Is better to use system sockets?
        self.path = path
        self.type = death_type

        if not self.path:
            raise ValueError("Specify path")
        
        self.master_socket = socket.socket(socket.AF_UNIX)
        self.master_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.master_socket.setblocking(False)
        try:
            os.remove(self.path)
        except OSError:
            pass
        self.master_socket.bind(path)
        self.master_socket.listen(socket.SOMAXCONN)

        self.response_counter = 0
        self.alive = True

        self.connection_list = []
        self.request_queue = asyncio.Queue()
        self.loop = asyncio.get_event_loop()
    
    def run_while_alive(self, func):
        @wraps(func)
        async def new_function(*args, **kwargs):
            while True:
                self.check_death()
                if not self.alive:
                    return
                self.loop.call_soon(func(*args, **kwargs))
        return new_function

    @run_while_alive
    async def recieve_connection(self):
        sock, addr = await self.loop.sock_accept(self.master_socket)
        sock.setblocking(False)
        self.connection_list.append((sock, addr))
        asyncio.ensure_future(self.handle_(sock, addr))
    
    @run_while_alive
    async def handle_connection(self, sock, addr):
        request_p = await self.loop.sock_recv(sock, 1024)
        request = loads(request_p)
        self.request_queue.put(request)

    @run_while_alive
    async def process_requests(self):
        request = await self.request_queue.get()
        # Process request
        self.respond(request) # TODO respond
        self.response_counter += 1

    async def check_death(self):
        if self.type is UNNAMED:
            if self.response_counter != 0:
                return self.die()
        elif self.type in NAMED:
            pass # TODO timeouts

    def die(self):
        try:
            while True:
                request = self.request_queue.get_nowait()
                self.respond(request, 'ERR', 304, "Repeat request due to timeout")
        except QueueEmpty:
            pass
        
        for sock, addr in self.connection_list:
            sock.close()
        
        self.master_socket.close()
        try:
            os.remove(self.path)
        except OSError:
            pass
        
        self.alive = False
        return
