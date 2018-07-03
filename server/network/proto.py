import asyncio
import uvloop
import socket
from request import Request, ParseError
from response import ErrResponse
from pickle import dumps
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
            asyncio.ensure_future(solver.recv_from_user())


class CyanSolver:

    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.alive = True
        self.request = Request()
        self.requests_queue = asyncio.Queue()
        self.response_queue = asyncio.Queue()
        self.session = None
        self.session_addr = ('127.0.0.1', 12346)
        self.loop = asyncio.get_event_loop()
        self.data = b''

    async def recv_from_user(self):
        asyncio.ensure_future(self.send_to_session())
        asyncio.ensure_future(self.send_to_user())
        while True:
            self.response_queue.put(ErrResponse(code=400, desc=400))
            data = self.data + await self.loop.sock_recv(self.sock, 1024)

            # I'm not sure about this place
            # Connection was close
            if not data:
                print(f'close connection with {self.addr}')
                self.sock.close()
                self.alive = False
                return

            try:
                self.data = self.request.add(data)
            except ParseError as err:
                print(err)
                self.response_queue.put(ErrResponse(code=err.code, desc=err.desc))
                print('err put')
                self.request = Request()
                
            if self.request.done:
                print('request done')
                self.requests_queue.put(self.request)
                print('request put')
                self.request = Request()
    
    async def send_to_user(self):
        while True:
            print(f'wait for response from queue (len={self.response_queue.qsize()})....')
            resp = await self.response_queue.get()
            print('new response from queue')
            await self.loop.sock_sendall(self.sock, bytes(resp))

    async def send_to_session(self):
        print('start send_to_session')
        while True:
            print('waiting for request from  queue....')
            request = await self.requests_queue.get()
            print(f'new request from {self.addr}')
            # Connect to Session Manager
            if not self.session:
                self.session = socket.socket()
                self.session.setblocking(False)
                await self.loop.sock_connect(self.session, self.session_addr)
            
            # Send user and token to session
            await self.loop.sock_sendall(
                self.session,
                dumps({
                    'USER': request.headers['USER'],
                    'USER-TOKEN': request.headers['USER-TOKEN']
                })
            )
            pprint(request.headers)

    async def recv_from_session(self):
        while True:
            data = await self.loop.sock_recv(self.session, 1024)
            if not data:
                self.session = None
                return
            

if __name__ == '__main__':
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    server = ConnectionServer()
    asyncio.ensure_future(server.serv())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()
    loop.close()
