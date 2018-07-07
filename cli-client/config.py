import os
import re
from getpass import getpass

logger = None
base_dir = my_dir = os.path.expanduser("~/.cyan-cli/")
config_files = {  # config-key : filename
    "SERVER": 'default_server',
    "USER": 'user',
    "EMAIL": 'email',
    "PASSWD": '.password',
    "USER-TOKEN": '.token'
}

def add_subparser(subparser):
    parse_conf = subparser.add_parser("config")
    parse_conf.add_argument("--server", "-s", type=str, metavar="srv", help="Your default server to store in your config")
    parse_conf.add_argument("--user", "-u", type=str, metavar="USER", help="Your username")

def check_path_security(path):
    if re.match(r'\.\.', path):
        raise ValueError(path)

def touch_conf_dir(dir):
    new_path = base_dir + dir
    check_path_security(new_path)
    if not os.path.isdir(new_path):
        os.mkdir(new_path)

def touch_conf_file(file):
    new_path = base_dir + file
    check_path_security(new_path)
    with open(new_path, 'a'): pass

def read_conf_file(file):
    try:
        with open(base_dir + file, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.warning(f"Trying to access non-existent config file {file}")
        return None

def write_conf_file(file, value):
    if not value is None:
        touch_conf_file(file)
        with open(base_dir + file, "w") as f:
            f.write(value)
    else:
        raise ValueError

def get_config():
    config = {}
    
    for key, val in config_files.items():
        config[key] = read_conf_file(val)
    return config

def save_config(conf):
    touch_conf_dir('.')

    for key, val in conf.items():
        if key in config_files and not val is None:
            write_conf_file(config_files[key], val)

def ask_confirm(prompt):
    confirm = input(prompt)
    if not confirm.startswith("Y"):
        return False
    else:
        return True

def ask_value(prompt, valid_re, is_hidden=False):
    while True:
        value = None
        if is_hidden:
            value = getpass(prompt)
        else:
            value = input(prompt)
        valid = re.search(valid_re, value)
        print(valid)
        if valid:
            return valid.group(1)
        else:
            if not ask_confirm("Invalid input. Retry? (Y/n) "):
                return None

def full_config():
    if not ask_confirm("Do you want to redo your configuration? (Y/n) "):
        return
    new_config = {}
    logger.info("Inputting new configuration")

    new_config['EMAIL'] = ask_value("Your email: ", r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
    new_config['USER'] = ask_value("Your username: ", r"(u[0-9]{6})")
    new_config['PASSWD'] = ask_value("Your password: ", r"([a-zA-Z0-9_#$^+=!*()@%&\-]{5,})", True)
    new_config['SERVER'] = ask_value("Your default server: ", r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}:(\d+))")

    save_config(new_config)

def process_args(args):
    if args.server is None and args.user is None:
        full_config()
    else:
        new_config = {
            'USER': args.user,
            'SERVER': args.server
        }
        save_config(new_config)
