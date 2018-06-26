CYAN-msg server-side specification
==================================

Overview
--------

Server-side is a indispensable part of CYAN-msg. It provides a solid backbone for the platform, serving every user. The frontend is served by CYAN protocol, implementing a resourse model. This specification leaves room for developers to choose how they want thir data processed and in which formats it should be shared.

Formats
-------

The resourses model does not in any way specify any file restrictions, however, for stable operation a standartized system is necessary. Firstly, all text files should be encoded in utf-8 format, to ensure worldwide compatability. Also, such resourses as `/events`, `/users/` and `/settings` have to have a proper structure to be used. We strongly recommend using a text-based serialization format like JSON.

Handling errors
---------------

In order to be clear, server-side should always give a response to each request. If a normal response cannot be formed, server should always return an `ERR`-type response. As its base, it uses http status codes, covering a wide range of situations.
