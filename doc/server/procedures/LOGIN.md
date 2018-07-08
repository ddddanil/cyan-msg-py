CYAN-msg Python server LOGIN procedure
======================================

Overview
--------

Login is a crucial part of using a messenger, so this procedure should be both easy and secure. This implementation uses both a special user and a one-time login token in order to do this procedure.

Login sequence
--------------

**Please note that protocol in this listings does not comply with the standarts and is presented only as an example.**

### First request

```s
POST u000000
USER-TOKEN:any_random_string
TARGET:/login
BIN::
{
    'email':'abc@mail.gov',
    'password':'I<3cats!'
}
```

Just after recieving this request, session manager spawns a unnamed session. As u000000 has permissions only to `POST` to `/login` and `/register`, any other request should be declined.

Under the hood, this abstraction is interpreted by the Resource manager as a request to check given password against one stored in a database. Depending on whether they match or not, session returns an `ERR` or `ACK` response.

### First response

```s
ACK u0001 /user/0001
USER-TOKEN:a_one_time_token
```

In the event of a successful login, a one time token is generated. Such a token can only give access to reading the `/login` resource and nothing else. Furthermore, only one attempt is given, and in a case of failure, this token is deemed invalid.

### Second request

```s
GET u0001 /login
USER-TOKEN:a_one_time_token
```

At this moment a temporary session is made, giving the user access to their token. It is at this point, when session manager checks whether a named session connected with the user token is alive, and starts one if it is not.

### Second response

```s
BIN u0001 /login
BIN::
{
    'token':'8467912deadbeefcafe'
}
```

Now the user has successfully logged in, and any further requests would be routed to the names session responsible for that token.
