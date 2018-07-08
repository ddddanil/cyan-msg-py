import sys
import config
import logging
import argparse
import networking
import CYANrequest
import CYANresponse
import logging.handlers

DEBUG = 1
logger = None

def get_parser():
    arg_parcer = argparse.ArgumentParser(description="A utility to forward files using CYAN-msg")
    subparser = arg_parcer.add_subparsers(help='Available commands', dest='command')

    parse_up = subparser.add_parser("u")
    parse_up.add_argument("--server", "-s", type=str, metavar="srv", help="Override the default server stored in your config")
    parse_up.add_argument("--target", "-t", type=str, required=True, metavar="USER", help="A user to whom you want to send this file")
    parse_up.add_argument("--input", type=argparse.FileType("rb"), default=sys.stdin, metavar="file", help="File to send")

    parse_down = subparser.add_parser("d")
    parse_down.add_argument("--server", "-s", type=str, metavar="srv", help="Override the default server stored in your config")
    parse_down.add_argument("--resource", "-r", type=str, required=True, metavar="RESOURCE", help="Which resource you want to download")
    parse_down.add_argument("--output", type=argparse.FileType("wb"), default=sys.stdout, metavar="file", help="File to save")

    return (arg_parcer, subparser)

def setup_logger():
    config.touch_conf_dir("log/")
    config.touch_conf_file('log/default.log')
    config.touch_conf_file('log/warning.log')

    logging.addLevelName(5, 'CHECK')

    simple_formatter = logging.Formatter('%(levelname)-8s %(name)-24s: %(message)s')
    wide_formatter = logging.Formatter('%(asctime)-10s - %(name)-24.24s - %(levelname)-8s -= %(message)s =-')
    very_wide_formatter = logging.Formatter('| %(asctime)-20s | - | %(name)-20.20s | - | %(levelname) -20s |\n| %(message)-77s |\n')

    console_log = logging.StreamHandler()
    if DEBUG:
        console_log.setLevel(logging.DEBUG)
    else:
        console_log.setLevel(logging.ERROR)
    console_log.setFormatter(simple_formatter)

    file_log = logging.handlers.RotatingFileHandler(config.base_dir + 'log/default.log', maxBytes=(5*1024*1024), backupCount=3, encoding='utf-8')
    file_log.setLevel(logging.INFO)
    file_log.setFormatter(wide_formatter)

    warn_log = logging.handlers.RotatingFileHandler(config.base_dir + 'log/warning.log', maxBytes=(5*1024*1024), backupCount=3, encoding='utf-8')
    warn_log.setLevel(logging.WARNING)
    warn_log.setFormatter(very_wide_formatter)

    master_logger = logging.getLogger('CYAN-cli')
    master_logger.setLevel(logging.NOTSET)
    
    master_logger.addHandler(console_log)
    master_logger.addHandler(file_log)
    master_logger.addHandler(warn_log)

    global logger
    logger = logging.getLogger('CYAN-cli.main')
    config.logger = logging.getLogger('CYAN-cli.config')
    CYANrequest.logger = logging.getLogger('CYAN-cli.request')
    CYANresponse.logger = logging.getLogger('CYAN-cli.response')
    networking.logger = logging.getLogger('CYAN-cli.network')

def merge_conf_arg(args, conf):
    if args.server:
        conf['SERVER'] = args.server

    conf['CMD'] = args.command
    try:
        conf['TARGET'] = args.target
    except AttributeError:
        conf["TARGET"] = ''
    try:
        conf['RESOURCE'] = args.resource
    except AttributeError:
        conf["RESOURCE"] = ''
    conf['FILE'] = args.input or args.output

    return conf

def main():
    setup_logger()
    parser, subparser = get_parser()
    config.add_subparser(subparser)
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    logger.debug(args)

    if args.command == 'config':
        config.process_args(args)
        sys.exit(0)
    
    conf = config.get_config()

    if conf['USER'] is None:
        logger.error("No user was stored in the config")
        print(f"No user stored.\nPlease run `{parser.prog} config` to set up necessary files.")
        sys.exit(2)
    
    conf = merge_conf_arg(args, conf)

    request = CYANrequest.Request(conf)
    connection = networking.Connection(conf['SERVER'])
    resp_bytes = connection.exchange(bytes(request))
    response = CYANresponse.Response(resp_bytes)
    
    response.present_result(conf['FILE'])

if __name__ == '__main__':
    main()
