'''Network module for CYAN-msg Python server

This module handles all incoming requests, parses them and then passes them to a session.
'''

__all__ = ["cyanrequest", "cyanresponse"]
__author__ = "Danil Doroshin and Nikolay Rulov"
__credits__ = ["Danil Doroshin", "Nikolay Rulev"]
__version__ = '0.1'

from network.execute import run