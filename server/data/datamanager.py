import asyncio
import uvloop
import logging
import socket
import logging


logger = logging.getLogger('data.DataServer')


class DataServer:
    def __init__(self, host='0.0.0.0', port=12347):
        self.host = host
        self.port = port
        # Create tcp socket for accept
        # typical socket set up commands
        self.master_socket = socket.socket()
        self.master_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.master_socket.setblocking(False)
        self.master_socket.bind((host, port))
        self.master_socket.listen(socket.SOMAXCONN)
        self.loop = asyncio.get_event_loop()
        logger.info(f'Start DataServer on {host}:{port}')

    async def serv(self):
        while True:
            sock, _ = await self.loop.sock_accept(self.master_socket)
            logger.info('new connection')
            sock.setblocking(False)
            asyncio.ensure_future(self.handle_connection(sock))

    async def recv_request(self, sock, n=-1):
        # get size of new request
        request = b''
        if n == 0:
            return request
        elif n > 0:
            request = await self.loop.sock_recv(sock, n)
            if not request and n != 0:
                return None, None
        else:
            chunk = b''
            while chunk.find(b';') == -1:
                chunk = await self.loop.sock_recv(sock, 128)
                # connection was closed
                if not chunk:
                    return None, None
                request += chunk

        return request.split(b';', maxsplit=1)

    async def handle_connection(self, sock):
        next_req = b''
        cur_req = b''
        while True:
            cur_req += next_req
            cur_req, next_req = await self.recv_request(sock)
            if not cur_req:
                return
            reqest = cur_req.decode().split()
            # FILE META ID
            # USER META ID
            # USER POST ID
            if reqest[1] == 'POST':
                # recv last request data
                reqest.append(next_req + await self.recv_request(sock, max(0, int(reqest[-1]) - len(next_req))))
            await self.loop.sock_sendall(sock, str(reqest).encode())
            logger.debug(reqest)