# component_patch_interfaces

## Component purpose and boundary in current architecture
`interfaces.py` defines the Protocol contracts used across subsystem
boundaries.

## Before/after behavior summary
- Before:
  - no descriptor payload Protocol family exists
  - record typing still leans on concrete record classes
- After:
  - add descriptor payload Protocols
  - add spell/conduit/frame record Protocols
  - move descriptor aggregate typing toward those Protocols where it only needs
    contracts

## Validation expectations
- payload and record Protocols exist
- descriptor-facing code can type against interfaces instead of concrete record
  classes where appropriate
