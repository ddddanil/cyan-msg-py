import asyncio
import uvloop
import logging
import socket
import logging


logger = logging.getLogger('data.DataServer')


class DataServer:
    def __init__(self, host='0.0.0.0', port=12346):
        self.host = host
        self.port = port
        # Create tcp socket for accept
        # typical socket set up commands
        logger.debug((host, port))
        self.master_socket = socket.socket()
        self.master_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.master_socket.setblocking(False)
        self.master_socket.bind((host, port))
        self.master_socket.listen(socket.SOMAXCONN)
        self.loop = asyncio.get_event_loop()
        logger.info('Start DataServer on {host}:{port}')

    async def serv(self):
        while True:
            sock, _ = await self.loop.sock_accept(self.master_socket)
            sock.setblocking(False)
            asyncio.ensure_future(self.handle_connection(sock))

    async def recv_request(self, sock):
        raw_request = b''
        # get size of new request
        raw_size = await self.loop.sock_recv(sock, 1)
        # connection close
        if not raw_size:
            return None
        size = int.from_bytes(raw_size, 'big')
        logger.debug(f'New request\'s size = {size}')
        # get this request
        request = (await self.loop.sock_recv(sock, size)).decode()
        logger.debug(f"request: {request}")
        return request


    async def handle_connection(self, sock):
        while True:
            await self.read_msg(sock)
