# Named conduits, ownership transfer, and severing

Prerequisite: [links and permissions](permissions.md). Names make dynamic conduits
discoverable through their frame's cloud. They also make a useful application
vocabulary: `platform`, `services`, and `workflows` can identify independently
owned parts of a system.

## Find the owner

The cloud lessons show lookup of already-created named conduits. Choose a distinct
name for each root in the same frame. A fresh root still comes from a fresh book;
lookup does not create a second root for an existing book.

## Transfer stewardship

`transfer_spell_ownership(...)` moves stewardship to the target conduit and returns
a report. By default (`move_creations=True`, since 0.2.8239) the objects the old
owner's creations hold for the spell move with it: a `unique` stays one object,
served by the new owner and disposed when the new owner is cleaned up. The
`many` dependencies a moved object was built with do not move: they belong to
the conduit or spell space that built them and are disposed when it ends. With
`move_creations=False` those objects leave the old owner's
creations without being moved or disposed, and the new owner builds its own. A
transfer disposes nothing. The saved lesson requests `move_creations=True`,
inspects the report, and resolves from the new home. Read that report when
diagnosing a transfer; sharing and moving ownership have different lifecycle
consequences.

A transfer hands over stewardship, not a working setup. The spells the
transferred spell depends on stay with the old owner unless
`include_dependencies=True` moves the direct ones, so expect the new owner to
start out broken once the old owner tears down: its moved objects can hold
dependencies that were just disposed. That is normal in a runtime agents
iterate in. The new owner purges what it does not want, binds the dependencies
it needs (a meld without them raises `UnresolvedInputError` naming each
missing input) and builds its own version, while the old owner cleans up
after itself.

## End the relationship

`sever_link(...)` removes the relationship and the contracts carried by it. The
sever lesson attempts another borrower meld, then checks the owner's live object.
This distinguishes the borrower's resolution rights from the owner's retained
creation. Application references you already hold still need their own lifecycle policy.

Finish with the [connected-subsystem walkthrough](connected-subsystems.md).
