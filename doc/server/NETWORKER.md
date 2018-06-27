CYAN-msg Python server Networker module
=======================================

Overview
--------

This module provides connectivity for Python server, handling sockets, requests, responses and working with the protocol.

Classes
-------

### ConnServer

This class is responsible for maintaining sockets. It uses stream sockets and TCP for establishing connections with all users.

### ProtocolSolver

This class envelopes CYAN-msg protocol and enables other modules to convert objects into byte streams and vice versa.

### Request

This class represents a finished request ready for further processing by other modules. This is the end product the Networker module.

### Response

This class is a gateway for other modules to the network, as it is the vessel for object information transferred into the Networker module.
