import asyncio
import functools
import pickle


class CyanProtocol(asyncio.Protocol):

    def __init__(self):
        super().__init__()
        self.transport = None
        self.peername = None

        self.session_msg = asyncio.Future()
        self.session_msg.add_done_callback(functools.partial(self.session_msg_cb))
        self.session = SessionProtocol(self)
        coro = loop.create_connection(lambda: self.session, '0.0.0.0', 12346)
        asyncio.ensure_future(coro)
        self.loop = asyncio.get_event_loop()

    def connection_made(self, transport):
        self.transport = transport
        self.peername = transport.get_extra_info('peername')
        print(f'new connection from {self.peername}')

    def data_received(self, data):
        print(f'received proto: {data}')
        if not self.session:
            self.session = SessionProtocol(self)
            coro = loop.create_connection(lambda: self.session, '0.0.0.0', 12346)
            asyncio.ensure_future(coro)
        self.session.transport.write(data)

    def connection_lost(self, exc):
        if exc:
            print(exc)
        print('close connection')

    def session_msg_cb(self, fut):
        print(f'new message from Session {self.session_msg.result()} \neq: {fut is self.session_msg}')
        # clear future
        self.session_msg = asyncio.Future()
        self.session_msg.add_done_callback(functools.partial(self.session_msg_cb))


class SessionProtocol(asyncio.Protocol):

    def __init__(self, cyan_proto: CyanProtocol):
        super().__init__()
        self.cyan_proto = cyan_proto
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        print('new connection with session ', type(transport))

    def data_received(self, data):
        self.cyan_proto.session_msg.set_result(data)

    def connection_lost(self, exc):
        if exc:
            print(exc)
        print('lost connection with session')
        self.cyan_proto.session = None


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coro = loop.create_server(CyanProtocol, '0.0.0.0', 12345)
    server = loop.run_until_complete(coro)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    server.close()
    loop.run_until_complete(server.wait_close())
    loop.close()