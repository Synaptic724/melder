# Build a complete beginner application

Bring the level's ideas together in the saved beginner capstone: configuration,
a pooled resource, a request handler, classified addresses, mixed lifetimes,
and explicit cleanup.

## Read the application in three passes

First identify the ordinary application classes. Then read the registrations:
what address each binding receives and which lifetime is selected. Finally,
follow the resolutions and cleanup, checking the assertions and recorded
teardown output against the purpose of each object.

## Keep the bootstrap understandable

The bootstrap-pattern lesson places registration and conjure in one function.
The inventory-pattern lesson shows how a caller can inspect the vocabulary it
has been handed. Together they give you a small application boundary that is
easy to run, explain, and extend.

Once this feels comfortable, continue to Intermediate for configuration and
cooperation between independently owned subsystems.
