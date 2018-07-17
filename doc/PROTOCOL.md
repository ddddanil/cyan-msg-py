CYAN protocol v0.1
==================

Overview
--------

This protocol is made to work with CYAN-msg messaging app. It uses the 'everything is a file' ideolodgy, enabling users to share any information they want. Also, this protocol is text based, however, it also can transport binary information.

Basic information
-----------------

The protocol itself consists of a number of lines of ASCII characters, divided by newline characters. A packet has two parts

1. Head
   - Protocol confirmation line `CYAN <version number>`
   - Main header `<TYPE> <user link> [resource]`
   - Other headers `KEY:VALUE`
2. Ending. Either
   - Standart marker `::`
   - Binary marker `BIN::`
3. Binary information (optional)

In order to transport binary information safely, its length sould be present in headers (see details later). Recipient will wait until timeout for that amount of bytes to be recieved. Any excess will be interpreted as a new request.

All conversations between client and server can be basically broken down to client requests and consequent server responses. Client can either use `GET` or `POST` request, to which there are `BIN`, `ACK` and `ERR` responses, all of which are discussed in detail later. Each type has a list of required and acceptable headers and may or may not have a body. Any missing headers from the required list will result in an `ERR` response, all unmentioned headers will be ignored.

Requests and responses
----------------------

### `GET` request

- Requires resource
   - TRUE
- Has body
   - FALSE
- Required headers
   - `USER-TOKEN`
- Acceptable headers
   - `ACCEPT-TYPE`
   - `LAST-UPDATE`

#### Example

```s
CYAN 0.1
GET u0001 /resources/_unique_file_id_
USER-TOKEN:requesters_token
ACCEPT-TYPE:text
::
```

____________________

This is a typical `/events` request.

```s
CYAN 0.1
GET u0001 /events
USER-TOKEN:deadbeefcafe
LAST-UPDATE:880880456
::
```

### `POST` request

- Requires resource
  - FALSE
- Has body
  - TRUE
- Required headers
  - `USER-TOKEN`
  - `TYPE`
  - `CHECKSUM`
  - `TIME-SENT`
  - `LENGTH`
  - `TARGET`
- Acceptable headers
  - None

#### Example

```s
CYAN 0.1
POST u0001
USER-TOKEN:requesters_token
TARGET:u0002
TYPE:img
CHECKSUM:hash_of_binary
TIME-SENT:6782357087
LENGTH:14000
BIN::
binary file here
```

### `BIN` response

- Requires resource
   - TRUE
- Has body
   - TRUE
- Required headers
   - `TYPE`
   - `CHECKSUM`
   - `SENDER`
   - `TIME-SENT`
   - `LENGTH`
- Acceptable headers
   - `READ-STATUS`
   - `CODE`

#### Example

```s
CYAN 0.1
BIN u0001 /resources/_id_of_file_
TYPE:text
CHECKSUM:hash_of_binary
SENDER:u0002
TIME-SENT:880888421 //utc time
LENGTH:145
READ-STATUS:0
BIN::
binary file starts here
```

### `ACK` response

- Requires resource
   - TRUE
- Has body
   - FALSE
- Acceptable headers
   - `TYPE`
   - `CHECKSUM`
   - `TIME-SENT`
   - `LENGTH`
   - `CODE`
   - `USER-TOKEN`

#### Example

```s
CYAN 0.1
ACK u0001 /resources/_ID_of_new_file_
TYPE:video
CHECKSUM:hash_of_binary
LENGTH:543210
TIME-SENT:880880654
::
```

____________________

This is a responce to a successful `/login` request

```s
CYAN 0.1
ACK u0003 /user/0003
TYPE:text
CHECKSUM:1234567890abcdef
LENGTH:254
TIME-SENT:880880987
USER-TOKEN:deadbeebcafe
::
```

### `ERR` response

- Requires resource
   - FALSE
- Has body
   - FALSE
- Required headers
   - `CODE`
- Acceptable headers
   - `TEXT`

#### Example

```s
CYAN 0.1
ERR u0001
CODE:403
TEXT:Forbidden
::
```

Header specification
--------------------

#### `USER-TOKEN`

A token string authorising the user. In requests, this signifies a session token, however, in an `ACK` responce it stands for a one time token used to finish the login sequence.

#### `TARGET`

A user link or a specific resource.

#### `ACCEPT-TYPE` and `TYPE`

Specify a type of media wanted or presented.
Following types of media are currently supported

- `text`
- `img`
- `video`
- `audio`
- `other`

#### `CHECKSUM`

A hexadecimal digest of the following binary file

#### `TIME-SENT`

Time the message was originally sent. This value should be a UTC time stamp.

#### `LENGTH`

Length of the following binary file in bytes.

#### `SENDER`

User originally sending the message.

#### `READ-STATUS`

This applies only to messages sent by the requestor. Can be one of the following

- `0` Not read by the recipient
- `1` Read by the recipient

#### `CODE`

A http-like response status code

#### `TEXT`

Textual description of the status code.

#### `LAST-UPDATE`

A UTC time stamp representing the last time a resource had beed accessed by a client.

**Warning!**
This header is required when accessing `/events` resource

User links
----------

User link is a shorthand for a resource string. A link starting in 'u' expands into `/user/<id>`. Similarly, a link starting with a 'g' expands into `/group/<id>`.

#### Example

`u0001` -> `/user/0001`
`g8567` -> `/group/8567`
