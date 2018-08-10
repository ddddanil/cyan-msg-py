import asyncio
import uvloop
import logging
from SessionManager import SessionManager


def setup_logger(): # TODO external init through file
    simple_formatter = logging.Formatter('%(levelname)-8s %(name)-24s: %(message)s')
    wide_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s\n\t-= %(message)s =-')
    debuglog = logging.StreamHandler()
    debuglog.setLevel(logging.DEBUG)
    debuglog.setFormatter(simple_formatter)

    master_logger = logging.getLogger('CYAN-msg')
    master_logger.setLevel(logging.DEBUG)
    
    master_logger.addHandler(debuglog)


def run():
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
