import asyncio
import uvloop
import socket
from .Request import Request
from pprint import pprint


class ConnectionServer:

    def __init__(self, host='0.0.0.0', port=12345):
        self.host = host
        self.port = port
        self.connections = []
        # Create tcp socket for accept
        # typical socket set up commands
        print((host, port))
        self.master_socket = socket.socket()
        self.master_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.master_socket.setblocking(False)
        self.master_socket.bind((host, port))
        self.master_socket.listen(socket.SOMAXCONN)
        self.loop = asyncio.get_event_loop()
        print(f'Start server on {host}:{port}')

    async def serv(self):
        while True:
            sock, addr = await self.loop.sock_accept(self.master_socket)
            sock.setblocking(False)
            solver = CyanSolver(sock, addr)
            self.connections.append(solver)
            print(f'new connection from {addr}')
            self.loop.create_task(solver.serv())


class CyanSolver:

    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.alive = True
        self.request = Request()
        self.requests_queue = asyncio.Queue()
        self.ack_queue = asyncio.Queue()
        self.session = None
        self.session_addr = ('127.0.0.1', 123456)
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.send_to_session())
        self.data = b''

    async def serv(self):
        while True:
            print(self.data)
            data = self.data + await self.loop.sock_recv(self.sock, 1024)

            # I'm not sure about this place
            # Connection was close
            if not data:
                self.sock.close()
                self.alive = False
                return

            self.data = self.request.add(data)
            if self.request.done:
                self.requests_queue.put(self.request)
                self.request = Request()

    async def send_to_session(self):
        while True:
            if not self.session:
                self.session = socket.socket()
                self.session.setblocking(False)
                await self.loop.sock_connect(self.session_addr)
            request = await self.requests_queue.get()
            print(f'new request from {self.addr}')
            pprint(request.headers)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    server = ConnectionServer()
    loop.create_task(server.serv())
    loop.run_forever()
    loop.close()
