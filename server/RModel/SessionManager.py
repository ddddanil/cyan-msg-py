import asyncio
import socket
import uvloop
from pickle import loads
import logging, logging.handlers
import Session


class SessionManager:

    def __init__(self, host='0.0.0.0', port=12346):
        self.host = host
        self.port = port

        self.session_list = {}
        self.tokens = {}
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
            logger.debug('serving....')
            sock, addr = await self.loop.sock_accept(self.master_socket)
            sock.setblocking(False)
            asyncio.ensure_future(self.handle_solver(sock, addr))
            logger.info(f'new connection to SessionManager from {addr}')

    async def handle_solver(self, sock, addr):
        data = await self.loop.sock_recv(sock, 1024)
        param = loads(data)
        logger.debug(param)
        if param['USER'] != 'u000000':
            logger.debug('user not u000000')
            current_session = None
            try:
                current_session = self.session_list[param['USER-TOKEN']]
            except KeyError:
                current_session = self.session_list[param['USER-TOKEN']] = Session.TokenSession(sock, addr, param['USER-TOKEN'])
                logger.info(f"New session on token {param['USER-TOKEN']}")
            else:
                await current_session.recieve_connection(sock, addr)
        else:
            logger.debug('One time session')
            Session.OneTimeSession(sock, addr)


def setup_logger(): # TODO external init through file
    global logger
    
    simple_formatter = logging.Formatter('%(levelname)-8s %(name)-24s: %(message)s')
    wide_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s\n\t-= %(message)s =-')
    debuglog = logging.StreamHandler()
    debuglog.setLevel(logging.DEBUG)
    debuglog.setFormatter(simple_formatter)

    master_logger = logging.getLogger('CYAN-msg')
    master_logger.setLevel(logging.DEBUG)
    
    master_logger.addHandler(debuglog)

    logger = logging.getLogger('CYAN-msg.SessionManager')
    Session.logger = logging.getLogger('CYAN-msg.Session')


if __name__ == '__main__':
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    setup_logger()

    server = SessionManager()
    asyncio.ensure_future(server.serv())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()
    loop.close()
