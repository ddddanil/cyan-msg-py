from configparser import ConfigParser

config = ConfigParser()
config.read("server.conf")

# Variables accessible from other modules
session_timeout = config["SessionManager"].getint("session_timeout", 86400) # 24 hours

server_address = (
    config["SessionManager"].get("address", '0.0.0.0'),
    config["SessionManager"].getint("port", 12346)
)

redis_address = (
    config["Redis"].get("address", 'localhost'),
    config["Redis"].get("port", 6379)
)