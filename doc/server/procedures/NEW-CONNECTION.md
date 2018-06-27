CYAN-msg Python server NEW CONNECTION procedure
===============================================

Overview
--------

This procedure describes the precise order in which any new connection is handled.

Sequence
--------

1. Networker
   1. Server accepts new connection and creates new ProtocolSolver using this connection.
   2. ProtocolSolver collects data from the client and creates a raw request
   3. ProtocolSolver parses raw request data and forms a valid Request object
   4. Connect to Session
      1. ProtocolSolver connects to SessionManager and waiting for accept
      2. After connection  ProtocolSolver sends 2 fields: user id (`user:u00001`) and token (`token:user_token`) 
2. RModel
   1. SessionManager accepts new connection
   2. It reads 2 fields from this connection (user and token)
   3. Based in the information from these fields, session manager deduces which session type to create