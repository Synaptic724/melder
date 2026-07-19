# Component Patch: Builder Interfaces

## Purpose
Expand the interface layer so the builder family can borrow collaborators and
borrowed typed configurations through protocols instead of concrete imports.

## Expected Additions
- richer typed ACL configuration protocols
- fuller `IFrameACLContainer` surface for builder usage
- builder protocol for family-specific builder collaboration

## Invariants
- protocol layer mirrors real runtime contracts
- no hidden widening to unrelated ACL subsystems
