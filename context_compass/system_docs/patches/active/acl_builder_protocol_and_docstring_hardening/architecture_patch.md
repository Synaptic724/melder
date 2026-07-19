# Architecture Patch: ACL Builder Protocol And Docstring Hardening

## Objective
Harden the ACL builder family so protocol boundaries match actual ownership and
the builder API docstrings meet the public-library contract bar.

## Non-Goals
- No new ACL behavior.
- No builder feature expansion.
- No compiler or validator redesign.

## Changed Components
- `interfaces.py`
- generic ACL builder
- view/command/codegen family builders

## Invariants
- Concrete ACL configuration/profile/container ownership stays unchanged.
- Family builders still layer over the generic builder lifecycle.
- This slice changes typing/docs, not runtime ACL semantics.
