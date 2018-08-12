import asyncio
import uvloop
import RModel.logger_setup
import RModel.resources
from RModel.SessionManager import SessionManager


def run():
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    server = SessionManager()
    asyncio.ensure_future(server.serv())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()
    loop.close()
