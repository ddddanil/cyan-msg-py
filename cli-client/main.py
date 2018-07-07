import os
import sys
import fleep
import socket
import argparse
from time import time
from hashlib import sha1
from pprint import pprint

base_dir = my_dir = os.path.expanduser("~/.cyan-cli/")
DEBUG = 1

def get_cyan_type(magic_bytes:bytes):
    info = fleep.get(magic_bytes)
    file_type = ''

    if 'raster-image' in info.type or \
        'raw-image' in info.type or \
        'vector-image' in info.type:
        file_type = 'img'
    elif 'video' in info.type:
        file_type = 'video'
    elif 'audio' in info.type:
        file_type = 'audio'
    else:
        file_type = 'other'

    return file_type

def do_request(server, request):
    byte_lines = []

    # 1st line
    byte_lines.append(b'CYAN 0.1')
    # 2nd line
    byte_lines.append(f'{request["REQ-TYPE"]} {request["USER"]} {request["RESOURCE"]}'.encode('ascii'))

    # Headers
    for key, val in request.items():
        if key in ['REQ-TYPE', 'RESOURCE', 'USER', 'BIN']: continue
        byte_lines.append(f'{key}:{val}'.encode('ascii'))
    
    # Last line
    if 'BIN' in request:
        byte_lines.append(b'BIN::')
        byte_lines.append(request['BIN'])
    else:
        byte_lines.append(b'::')

    request_bytes = b''
    for line in byte_lines:
        request_bytes += line + b'\n'

    if DEBUG: pprint(request_bytes)

    server = server.split(':')
    addr = (server[0], int(server[1]))
    sock = socket.socket()
    sock.connect(addr)
    sock.sendall(request_bytes)
    resp_bytes = sock.recv(2048)
    return resp_bytes

def make_request(args, conf):
    request = {}
    if args.command == "u":
        file_bytes = args.input.read()
        request["REQ-TYPE"] = "POST"
        request["USER"] = conf['USER']
        request["RESOURCE"] = ''
        request["USER-TOKEN"] = 'deadbeefcafe' # IMPORTANT! TODO automatic login
        request["TYPE"] = get_cyan_type(file_bytes[:129])
        request["CHECKSUM"] = sha1(file_bytes).hexdigest()
        request["TIME-SENT"] = int(time())
        request["LENGTH"] = len(file_bytes)
        request["TARGET"] = args.target
        request["BIN"] = file_bytes
    elif args.command == "d":
        request["REQ-TYPE"] = "GET"
        request["USER"] = conf['USER']
        request["USER-TOKEN"] = 'deadbeefcafe' # IMPORTANT! TODO automatic login
        request["RESOURCE"] = args.resource
    else:
        raise ValueError("Invalid request type")

    if DEBUG: pprint(request)

    return do_request(conf["SERVER"], request)

def try_conf_file(file):
    try:
        with open(base_dir + file, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def get_config():
    info = {}
    
    info["USER"] = try_conf_file("user")
    info["SERVER"] = try_conf_file("default_server")
    info["PASSWD"] = try_conf_file(".password")
    return info

def save_config(args):
    if not os.path.isdir(base_dir):
        os.mkdir(base_dir)
    if not args.user is None:
        with open(base_dir + "user", "w") as f:
            f.write(args.user)
    if not args.server is None:
        with open(base_dir + "default_server", "w") as f:
            f.write(args.server)

def get_parser():
    arg_p = argparse.ArgumentParser(description="A utility to forward files using CYAN-msg")
    subparse = arg_p.add_subparsers(help='Available commands', dest='command')

    parse_up = subparse.add_parser("u")
    parse_up.add_argument("--server", "-s", type=str, metavar="srv", help="Override the default server stored in your config")
    parse_up.add_argument("--target", "-t", type=str, required=True, metavar="USER", help="A user to whom you want to send this file")
    parse_up.add_argument("--input", type=argparse.FileType("rb"), required=True, metavar="file", help="File to send")

    parse_down = subparse.add_parser("d")
    parse_down.add_argument("--server", "-s", type=str, metavar="srv", help="Override the default server stored in your config")
    parse_down.add_argument("--resource", "-r", type=str, required=True, metavar="RESOURCE", help="Which resource you want to download")
    parse_down.add_argument("--output", type=argparse.FileType("wb"), required=True, metavar="file", help="File to save")

    parse_conf = subparse.add_parser("config")
    parse_conf.add_argument("--server", "-s", type=str, metavar="srv", help="Your default server to store in your config")
    parse_conf.add_argument("--user", "-u", type=str, metavar="USER", help="Your username")

    return arg_p

def main():
    parser = get_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if DEBUG: print(args)

    if args.command == 'config':
        save_config(args)
        sys.exit(0)
    
    conf = get_config()
    if conf['USER'] is None:
        print("No user stored")
        sys.exit(2)
    
    if args.server:
        conf['SERVER'] = args.server

    print(make_request(args, conf))

if __name__ == '__main__':
    main()
