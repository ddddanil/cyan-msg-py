import asyncio
from async_timeout import timeout
import socket
from cyanrequest import Request, ParseError
from cyanresponse import *
from pickle import dumps, loads
from pprint import pprint

logger = None
address = {
    'self': None,
    'session': None
}

class ConnectionServer:

    def __init__(self, host=None, port=None):
        if host is None or port is None:
            host, port = address['self']
        self.host = host
        self.port = port
        self.connections = []
        # Create tcp socket for accept
        # typical socket set up commands
        logger.debug((host, port))
        self.master_socket = socket.socket()
        self.master_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.master_socket.setblocking(False)
        self.master_socket.bind((host, port))
        self.master_socket.listen(socket.SOMAXCONN)
        self.loop = asyncio.get_event_loop()
        logger.info(f'Start server on {host}:{port}')

    async def serv(self):
        while True:
            sock, addr = await self.loop.sock_accept(self.master_socket)
            sock.setblocking(False)
            solver = CyanSolver(sock, addr)
            self.connections.append(solver)
            logger.info(f'new connection from {addr}')
            asyncio.ensure_future(solver.recv_from_user())


class CyanSolver:

    def __init__(self, sock, addr, s_addr=None, s_port=None):
        if s_addr is None or s_port is None:
            s_addr, s_port = address['session']
        self.sock = sock
        self.addr = addr
        self.alive = True
        self.request = Request()
        self.requests_queue = asyncio.Queue()
        self.response_queue = asyncio.Queue()
        self.session = None
        self.tasks = []
        self.session_addr = (s_addr, s_port)
        self.loop = asyncio.get_event_loop()
        self.data = b''

    async def recv_from_user(self):
        self.tasks.append(asyncio.ensure_future(self.send_to_session()))
        self.tasks.append(asyncio.ensure_future(self.send_to_user()))
        while True:
            data = b''
            try:
                # 5 minutes for send data
                with timeout(300):
                    data = self.data + await self.loop.sock_recv(self.sock, 1024)
                if not data:
                    logger.info(f'close connection with {self.addr}')
                    await self.stop()
                    return

            except asyncio.TimeoutError:
                self.request = Request()

            # I'm not sure about this place
            # Connection was close

            try:
                self.data = self.request.add(data)
            except ParseError as err:
                logger.debug(err)
                await self.response_queue.put(ErrResponse({'CODE':err.code, 'TEXT':err.desc}))
                logger.debug('err put')
                self.request = Request()
                
            if self.request.done:
                logger.debug('request done')
                await self.requests_queue.put(self.request)
                logger.debug('request put')
                self.request = Request()
    
    async def send_to_user(self):
        while True:
            logger.debug(f'wait for response from queue....')
            resp = await self.response_queue.get()
            logger.debug('new response from queue')
            await self.loop.sock_sendall(self.sock, bytes(resp))

    async def send_to_session(self):
        logger.debug('start send_to_session')
        while True:
            logger.debug('waiting for request from  queue....')
            request = await self.requests_queue.get()
            logger.info(f'new request from {self.addr}')
            # Connect to Session Manager
            if not self.session:
                self.session = socket.socket()
                self.session.setblocking(False)
                await self.loop.sock_connect(self.session, self.session_addr)
                logger.debug('connected to session')
                # Send user and token to session
                data = dumps({
                        'USER': request.headers['USER'],
                        'USER-TOKEN': request.headers['USER-TOKEN']
                    })
                await self.loop.sock_sendall(
                    self.session,
                    len(data).to_bytes(4, 'big') + data
                )
                self.tasks.append(asyncio.ensure_future(self.recv_from_session()))
            await self.loop.sock_sendall(self.session, bytes(request))
            logger.debug('send request to session')
            pprint(request.headers)

    async def recv_from_session(self):
        print('start recv_from_session')
        while True:
            raw_response = b''
            # get size of new request
            raw_size = await self.loop.sock_recv(self.session, 4)
            if not raw_size:
                self.session = None
                logger.debug('close connection with session')
                return

            size = int.from_bytes(raw_size, 'big')
            # get this request
            while len(raw_response) < size:
                needed_size = min(size - len(raw_response), 1024)
                raw_response += await self.loop.sock_recv(self.session, needed_size)
            headers: dict = loads(raw_response)
            if headers['RESP-TYPE'] == 'ERR':
                response = ErrResponse(headers)
            elif headers['RESP-TYPE'] == 'BIN':
                response = BinResponse(headers)
            elif headers['RESP-TYPE'] == 'ACK':
                response = AckResponse(headers)
            else:
                raise ValueError
            await self.response_queue.put(response)

    async def stop(self):
        for task in self.tasks:
            task.cancel()

        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        if self.session:
            self.session.shutdown(socket.SHUT_RDWR)
            self.session.close()
