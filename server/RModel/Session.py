import asyncio


class Session(asyncio.Protocol):

    def __init__(self):
        super().__init__()
        self.transport = None
        self.peername = None

    def connection_made(self, transport: asyncio.Transport):
        self.transport = transport
        self.peername = transport.get_extra_info('peername')
        print(self.peername)

    def data_received(self, data):
        print(f'received session: {data}')
        self.transport.write(data)

    def connection_lost(self, exc):
        if exc:
            print(exc)
        print('close connection')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coro = loop.create_server(Session, '0.0.0.0', 12346)
    server = loop.run_until_complete(coro)
    lp = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    server.close()
    loop.close()