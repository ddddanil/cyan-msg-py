import logging

simple_formatter = logging.Formatter('%(levelname)-8s %(name)-24s: %(message)s')
wide_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s\n\t-= %(message)s =-')
debuglog = logging.StreamHandler()
debuglog.setLevel(logging.DEBUG)
debuglog.setFormatter(simple_formatter)

master_logger = logging.getLogger('CYAN-msg')
master_logger.setLevel(logging.DEBUG)

master_logger.addHandler(debuglog)
