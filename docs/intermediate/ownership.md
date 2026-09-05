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
a report. The saved lesson requests `move_creations=True`, inspects the report,
and resolves from the new home. Read that report when diagnosing a transfer;
sharing and moving ownership have different lifecycle consequences.

## End the relationship

`sever_link(...)` removes the relationship and the contracts carried by it. The
sever lesson attempts another borrower meld, then checks the owner's live object.
This distinguishes the borrower's resolution rights from the owner's retained
creation. Application references you already hold still need their own lifecycle policy.

Finish with the [connected-subsystem walkthrough](connected-subsystems.md).
