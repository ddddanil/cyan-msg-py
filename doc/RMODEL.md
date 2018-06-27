CYAN-msg Python server RModel module
====================================

Overview
--------

This module provides and resolves the layer of abstraction that is resource model.

Classes
-------

### Session

This class is working with requests and responses from Networker module. It manages permissions and session timeouts.

### Resource manager

This class resolves a requests resource. It might or might not make a request for something from the DataManager module during its operation.
