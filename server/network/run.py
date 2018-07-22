import connserv
import cyanrequest
import cyanresponse
import logging
import configparser
import uvloop
from os import environ
import asyncio

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

    connserv.logger = master_logger


def setup_config():
    global DEBUG

    config = configparser.ConfigParser()
    config.read('server.conf')

    DEBUG = config['DEFAULT'].getboolean('debug')
    connserv.address['self'] = (
        config['ConnServer']['address'],
        config['ConnServer'].getint('port')
    )
    connserv.address['session'] = (
        config['ConnServer']['session_address'],
        config['ConnServer'].getint('session_port')
    )
    cyanrequest.ALLOWED_CYAN_VERSION = config["Protocol"]['version'].encode('ascii')
    cyanresponse.ALLOWED_CYAN_VERSION = config["Protocol"]['version']


def run():
    setup_logger()
    setup_config()

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    environ['PYTHONASYNCIODEBUG'] = '1' if DEBUG else '0'
    server = connserv.ConnectionServer()

    asyncio.ensure_future(server.serv())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()
    loop.close()


if __name__ == '__main__':
    run()