from configparser import ConfigParser

config = ConfigParser()
config.read('server.conf')

DEBUG = config['DEFAULT'].getboolean('debug')
server_address = (
    config['ConnServer'].get('address', '0.0.0.0'),
    config['ConnServer'].getint('port', 12345)
)
session_address = (
    config['SessionManager'].get('address', '0.0.0.0'),
    config['SessionManager'].getint('port', 12346)
)
version_b = config["Protocol"]['version'].encode('ascii')
version_s = config["Protocol"]['version']