FILE
----

   1) name
   2) creation utc
   3) creator
   4) receiver

USER
----

   1) display name
   2) id
   3) email
   4) password (hash(utc + passwd + id + salt))
   5) registration utc
   6) avatar (file name)
   7) description

GROUP
-----

   1) display name
   2) id
   3) users
   4) open/closed
   5) avatar
   6) description
   7) admins

EVENTS (user)
-------------

   1) res/action
   2) resource
   3) creation utc