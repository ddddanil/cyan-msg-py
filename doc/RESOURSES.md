CYAN-msg server-side resources
==============================

Overview
--------

A CYAN-msg server provides a plethora of services to each user. Each resource can be accessed via a CYAN protocol request and is represented by a string. This string looks like a path, starting at root and navigating through directories.

Main resourses
--------------

#### `/events`

This resourse is crucial to the app. It has all events queued to be recieved by the user. Server-side should return only a part of this file that is earlier than the `LAST-UPDATE` timestamp.

#### `/resourses/<unique file id>`

This resourse provides access to any binary file by its ID. Before fetching, server-side should check requester's permissions.

#### `/user/<user id>`

This resourse provides all public information about a user by their ID.

Additional resourses
--------------------

#### `/settings`

An updatable file containing user's settings.
