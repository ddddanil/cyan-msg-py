import asyncio
from async_timeout import timeout
import uvloop
import socket
from request import Request, ParseError
from response import *
from pickle import dumps, loads
from pprint import pprint
import logging


logger: logging.Logger = None


class ConnectionServer:

    def __init__(self, host='0.0.0.0', port=12345):
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
            data = b''
            try:
                # 5 minutes for send data
                with timeout(300):
                    data = self.data + await self.loop.sock_recv(self.sock, 1024)
            except asyncio.TimeoutError:
                self.request = Request()

            # I'm not sure about this place
            # Connection was close
            if not data:
                logger.info(f'close connection with {self.addr}')
                self.sock.close()
                self.alive = False
                return

            try:
                self.data = self.request.add(data)
            except ParseError as err:
                logger.debug(err)
                await self.response_queue.put(ErrResponse(code=err.code, desc=err.desc))
                logger.debug('err put')
                self.request = Request()
                
            if self.request.done:
                logger.debug('request done')
                await self.requests_queue.put(self.request)
                logger.debug('request put')
                self.request = Request()
    
    async def send_to_user(self):
        while True:
            logger.debug(f'wait for response from queue (len={self.response_queue.qsize()})....')
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
            
                # Send user and token to session
                await self.loop.sock_sendall(
                    self.session,
                    dumps({
                        'USER': request.headers['USER'],
                        'USER-TOKEN': request.headers['USER-TOKEN']
                    })
                )
            await self.loop.sock_sendall(self.session, bytes(request))
            pprint(request.headers)

    async def recv_from_session(self):
        while True:
            raw_response = b''
            # get size of new request
            size = int.from_bytes(await self.loop.sock_recv(self.session, 4), 'big')
            # get this request
            while len(raw_response) < size:
                needed_size = min(size - len(raw_response), 1024)
                raw_response += await self.loop.sock_recv(self.session, needed_size)
            headers = loads(raw_response)
            if headers['RESP_TYPE'] == 'ERR':
                response = ErrResponse(headers)
            elif headers['RESP_TYPE'] == 'BIN':
                response = BinResponse(headers)
            elif headers['RESP_TYPE'] == 'ACK':
                response = AckResponse(headers)
            else:
                raise ValueError
            await self.loop.sock_sendall(self.sock, bytes(response))


def setup_logger():  # TODO external init through file
    global logger

    simple_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s\n\t-= %(message)s =-')
    debuglog = logging.StreamHandler()
    debuglog.setLevel(logging.DEBUG)
    debuglog.setFormatter(simple_formatter)

    master_logger = logging.getLogger('network')
    master_logger.setLevel(logging.DEBUG)

    master_logger.addHandler(debuglog)

    logger = master_logger


if __name__ == '__main__':
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    setup_logger()

    server = ConnectionServer()
    asyncio.ensure_future(server.serv())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()
    loop.close()
