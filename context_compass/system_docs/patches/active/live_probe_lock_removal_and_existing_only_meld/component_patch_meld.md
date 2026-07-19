# Component Patch: Meld

## Before
- live probe path takes extra explicit read-side locks
- `meld(...)` has no explicit reuse-or-fail mode

## After
- live probe path is observational and lock-light
- `meld(existing_only=True)` returns an existing object or fails without
  creating a new one

## Interface Deltas
- `Meld.meld(...)` gains `existing_only`

## State / Failure Deltas
- read-only live checks stop taking extra explicit locks
- unsupported or non-live `existing_only` cases fail fast instead of falling
  into creation
