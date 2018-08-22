import asyncio
import asyncpg
import logging
import socket
import json
from sql import *

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
        self.pool = None
        logger.info(f'Start DataServer on {host}:{port}')

    async def serv(self):
        self.loop = await asyncpg.create_pool('postgresql://cyan:cyan@localhost:5432/cyan')
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
            if not request:
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

    async def solve(self, request):
        if request[0] == 'USER':
            return await self._solve_user(request[1:])

        elif request[0] == 'GROUP':
            return await self._solve_group(request[1:])

        elif request[0] == 'FILE':
            return await self._solve_file(request[1:])

    async def _solve_user(self, request):
        user = int(request[1][1:])
        if request[0] == 'POST':
            data = json.loads(request[-1].decode())
            if request[1] == 'u000000':  # CREATE NEW USER
                # (email, password, display_name, registration_utc)
                async with self.pool.acquire() as conn:
                    result = await conn.fetchrow(CREATE_NEW_USER,
                                                 data['email'],
                                                 data['password'],
                                                 data['display_name'],
                                                 data['registration_utc'])
                return json.dumps(dict(result))

            else:  # UPDATE USER INFO

                # get user meta from db
                async with self.pool.acquire() as conn:
                    meta = await conn.fetch(USER_META, data['USER'])

                # (id, email, password, display_name, registration_utc, avatar, description)
                async with self.pool.acquire() as conn:
                    result = await conn.fetch(UPDATE_USER,
                                              int(request[1][1:]),
                                              data.setdefault('email', meta['email']),
                                              data.setdefault('password', meta['password']),
                                              data.setdefault('display_name', meta['display_name']),
                                              data.setdefault('registration_utc', meta['registration_utc']),
                                              data.setdefault('avatar', meta['avatar']),
                                              data.setdefault('description', meta['description']))
        else:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow(USER_META, user)
            return json.dumps(dict(result))

    async def _solve_group(self, request):
        pass

    async def _solve_file(self, request):
        pass

    async def _user_post(self):
        pass

    async def handle_connection(self, sock):
        next_req = b''
        cur_req = b''
        while True:
            cur_req += next_req
            cur_req, next_req = await self.recv_request(sock)
            if cur_req is None:
                return
            request = cur_req.decode().split()
            # FILE META ID
            # USER META ID
            # USER POST ID
            if request[1] == 'POST':
                # recv last request data
                request.append(next_req + await self.recv_request(sock, max(0, int(request[-1]) - len(next_req))))
            logger.debug(request)
