from .cyanrequest import Request
import pytest
import sys


class TestRequest:

    def test_GET_1(self):
        req = Request()
        data = \
            b"CYAN 0.1\n" + \
            b"GET u0001 /resources/43534535345\n" + \
            b"USER-TOKEN:000000\n" + \
            b"ACCEPT-TYPE:text\n" + \
            b"::"
        assert req.add(data) == b''
        assert req.done is True
        assert req.headers == {
            'CYAN': '0.1',
            'REQ-TYPE': 'GET',
            'USER': 'u0001',
            'RESOURCE': '/resources/43534535345',
            'USER-TOKEN': '000000',
            'ACCEPT-TYPE': 'text'
        }

    def test_POST_1(self):
        req = Request()
        data = \
            b"CYAN 0.1\n" + \
            b"POST u0001\n" + \
            b"USER-TOKEN:000000\n" + \
            b"TARGET:u0001\n" + \
            b"TYPE:img\n" + \
            b"CHECKSUM:000000\n" + \
            b"TIME-SENT:0001\n" + \
            b"LENGTH:16\n" + \
            b"BIN::\n" + \
            b"binary file here"
        assert req.add(data) == b''
        assert req.done is True
        assert req.headers == {
            'CYAN': '0.1',
            'REQ-TYPE': 'POST',
            'USER': 'u0001',
            'USER-TOKEN': '000000',
            'TARGET': 'u0001',
            'TYPE': 'img',
            'CHECKSUM': '000000',
            'TIME-SENT': '0001',
            'LENGTH': '16',
            'BIN': b'binary file here'
        }
