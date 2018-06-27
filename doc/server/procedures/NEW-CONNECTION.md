CYAN-msg Python server NEW CONNECTION procedure
===============================================

Overview
--------

This procedure describes the precise order in which any new connection is handled.

Sequence
--------

1. Networker
   1. Designate a new socket
   2. Recieve data
   3. Parse data
   4. Form a request object
   5. Throw that abjetc at session manager
2. RModel
   1. Recieve an object
   2. Determine should this connection have a new session, or use an existing one. Determine type and name of that session
   3. Spawn and/or select a proper session
   4. Add the requested Networker node to the list of served nodes in that session
