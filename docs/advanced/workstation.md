# Own the room's working objects

Prerequisite: [Rift setup](nexus.md). The workstation is the room's local binding
canvas. It holds objects, attributes, and methods you give it; it is not another
Spellbook or an implicit resolver.

The saved example binds the name `subject` in both the object and method stores.
The `store=` argument distinguishes them. It selects a method as the active target,
calls it, clears the target without deleting the binding, and releases the object.

## Be explicit about retention

`weak_ref=True` requests weak storage. The lesson proves a non-weak-referenceable
value is refused rather than silently stored strongly. A strong binding retains
the object for the binding's lifetime; a weak binding does not give it that lifetime.

Keep room storage and world access separate. Retrieve permitted world objects
through the room's command/view surfaces, then place the objects you need on the
canvas. [Expert rooms](../expert/agent-rooms.md) continue into operation and codegen.
