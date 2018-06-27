CYAN-msg Python server
======================

[Networker]: ./NETWORKER.md
[RModel]: ./RMODEL.md
[DataManager]: DATAMANAGER.md

Overview
--------

This is the first server-side application to use CYAN-msg specifications, including its protocol and resource model. This application is mainly a prototype that could be set up on any machine for testing purposes.

Inner workings
--------------

In order to comply with CYAN-msg specifications, this package includes three modules, which when combined produce a fully working server. These modules are Networker, RModel and DataManager.

### [Networker]

This module is made to ensure connectivity with all clients. The main goal of this module is to serve CYAN-msg protocol. It checks the integrity of incoming packages and immediately discards malformed ones. Moreover, it handles proper formation of server responses.

In order to communicate with the outer world, it uses stream socket technology.

### [RModel]

This module implements the CYAN-msg resource model including all additional resources. It is also in charge of managing sessions and permissions.

#### Resource model

In order to maximize efficiency, all resources are implemented in one of these ways

1. Abstraction

   These resources do not contain any stored data, but rather get resolved on the fly by the module. These are `/login` and `/register`.

2. Data

   These resources only contain metadata, so they are stored in a database. These are `/users/`, `/groups/`, `/settings` and `/events`.

3. Storage

   These resources have some binary data that is stored as a file on a machine. This currently is only `/resources/`.

#### Session managing

In this implementation, all packets exchanged within one system socket represent a session. From a user perspective, a session is a valid user token. The server always closes any session in 24 hours since opening it, or after 1 hour of inactivity. In order to start a new session, a user has to access the `/login` resource either with a one time token given them after authorising, or with a token from a previous session. Please note, only one attemt at restoring a session with a previous token is given, requiring the user to login again in case of a failure. When logging in the first time, there is a special user "u000000" (subject to change) that has permissions only to `/register` and `/login` resources.

#### Permission managing

As every non-personalized resource has a sender and a reciever metadata, in order to grant access permissions server should only check whether the requesting user is either of them. Please note, that if reciever happens to be a group, every member of that group counts as a reciever.

### [DataManager]

For all different storage needs, this server needs a complex database system. So in order for RModel to seamlessly fetch informantion, it needs a database manager. Such a manager would also be in control of managing files in the actual storage.

### Module communication

This server-side implementation uses an idea of microservices. Each module works asynchronously to one another, communicating through system sockets.
