import logging
import uvloop
from os import environ
import asyncio
from data.datamanager import DataServer

DEBUG = True


def setup_logger():  # TODO external init through file
    simple_formatter = logging.Formatter('%(levelname)-8s %(name)-24s: %(message)s')
    wide_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s\n\t-= %(message)s =-')
    debuglog = logging.StreamHandler()
    debuglog.setLevel(logging.DEBUG)
    debuglog.setFormatter(simple_formatter)

    master_logger = logging.getLogger('network')
    master_logger.setLevel(logging.DEBUG)

    master_logger.addHandler(debuglog)


def run():
    setup_logger()

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    environ['PYTHONASYNCIODEBUG'] = '1' if DEBUG else '0'
    server = DataServer()

    asyncio.ensure_future(server.serv())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()
    loop.close()


if __name__ == '__main__':
    print("This module was not designed to run separately, please treat the package itself as an executable.")