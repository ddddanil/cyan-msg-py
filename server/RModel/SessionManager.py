import asyncio
import aioredis
import socket
import uvloop
from pickle import loads
from json import JSONDecodeError
import logging, logging.handlers
from RModel import Session
from RModel.config import redis_address
# 0 one time token
# 1 24 hours token
TOKENS = {}

logger = None


class SessionManager:

    def __init__(self, host='0.0.0.0', port=12346):
        global logger
        logger = logging.getLogger('RModel.SessionManager')
        self.host = host
        self.port = port
        self.session_list = {}
        self.redis = None
        # Create tcp socket for accept
        # typical socket set up commands
        logger.debug((host, port))
        self.master_socket = socket.socket()
        self.master_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.master_socket.setblocking(False)
        self.master_socket.bind((host, port))
        self.master_socket.listen(socket.SOMAXCONN)
        self.loop = asyncio.get_event_loop()
        print(f'Start server on {host}:{port}')

    async def serv(self):
        self.redis = await aioredis.create_redis(redis_address)
        while True:
            logger.debug('serving....')
            sock, addr = await self.loop.sock_accept(self.master_socket)
            sock.setblocking(False)
            asyncio.ensure_future(self.handle_solver(sock, addr))
            logger.info(f'new connection to SessionManager from {addr}')

    async def handle_solver(self, sock, addr):
        len = int.from_bytes((await self.loop.sock_recv(sock, 4)), 'big')
        data = await self.loop.sock_recv(sock, len)
        param = loads(data)
        logger.debug(param)
        if param['USER'] != 'u000000':
            # session for /login
            redis_ans = await self.redis.get(f'token:{param["USER-TOKEN"]}')
            if redis_ans == b'0':
                self.redis.delete(f'token:{param["USER-TOKEN"]}')
                Session.OneTimeSession(sock, addr)
            # 24 hours session
            elif redis_ans == b'1':
                # session exist
                if self.session_list.get(param['USER-TOKEN']):
                    await self.session_list[param['USER-TOKEN']].receive_connection(sock, addr)
                # new session
                else:
                    self.session_list[param['USER-TOKEN']] = Session.TokenSession(sock, addr, param['USER-TOKEN'])
            else:
                logger.debug('invalid token')
                sock.close()
        else:
            Session.OneTimeSession(sock, addr)
            logger.debug(f'create OneTimeSession for u000000 {addr}')
