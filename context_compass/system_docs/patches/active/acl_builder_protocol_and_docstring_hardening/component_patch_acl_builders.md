# Component Patch: ACL Builders

## Purpose
Bring the builder family to the public-library standard.

## Required Changes
- borrowed collaborator/config typing through protocols
- no borrowed concrete builder/config imports where the file does not own creation
- class docstrings rewritten to rich contract docstrings
- method docstrings completed for the public builder surface

## Invariants
- keep the existing builder lifecycle
- keep family-specific helper vocabularies intact
