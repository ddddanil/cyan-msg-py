CYAN-msg Python server RModel module
====================================

Overview
--------

This module provides and resolves the layer of abstraction that is resource model.

Classes
-------

### Session manager

This class distributes all new connections among opened sessions and creates new ones. Sessions s[awned by this manager can be one of the following three types

1. Named, or long-term

   This session is working with authorised users and is named and accessed via their current user token.

2. Temporary

   This session serves users that had been given a one time token. This type is closed right after its first response.

3. Unnamed

   This session serves a special user (u000000 for this particular server). It is destroyed in the same manner as a temporary session, but it is not acessed by a token name.

Once a new connection is established, the following procedure is performed (see the procedure page for details)

1. Determining which session type to use
2. Spawning new session worker
3. Establishing a system socket connecting a Networker node and a new session

### Session

This class is working with requests and responses from Networker module. It manages permissions and session timeouts.

Once it has been spawned, it fetches requests one at a time, firstly checking for permissions and then asking the Resource manager for a requested resource.

Also, one session is not limited to serving one Networker node, but rather there is a list of nodes being serviced. Each of those nodes has successfully logged in as the same user, and was given the same user token. All requests from every node are put into a queue, so that one session would not get more that one request at a time.

Each session has closing conditions. Each session checks them before fetching a request and after giving a response. If this condition is met, session executes finishing instructions and dies.

### Resource manager

This class resolves a requests resource. It might or might not make a request for something from the DataManager module during its operation.
