# Component Patch: Finishing Documentation Skills

## Component Purpose and Boundary in Current Architecture
This slice defines the documentation-family skills for the new role. Its focus
is not generic prose quality. It is system-aware public-library documentation:
docstrings, comments, and documentation/test alignment.

## Before/After Behavior Summary
Before:
- current synaptic docs cover docstrings/comments well, but they are still a
  broader Python-engineering overlay
- there is no dedicated finishing role that treats system-context reads as a
  prerequisite for writing library docstrings

After:
- the new role has a dedicated documentation family
- docstrings are explicitly system-aware
- comments are explicitly contract-preserving
- documentation and tests are explicitly aligned

## Interface Deltas (Inputs, Outputs, Error Semantics)
- Inputs:
  - code under edit
  - `src_architecture.md`
  - `src_components.md`
  - `graph_details_document.md`
  - `readable_src_graph.json`
- Outputs:
  - deeper docstring/comment skill guidance
- Error semantics:
  - role should stop and investigate when system context is missing or stale

## State and Lifecycle Deltas
- add new role-local documentation skill docs under
  `skills/documentation/`

## Dependency and Ordering Constraints
- the role must read mandatory system docs before using these skills
- documentation skills should reference testing expectations where contracts
  imply test obligations

## Validation Expectations
- documentation skills explicitly mention:
  - system role / collaborator boundaries
  - lifecycle / cleanup
  - threading / locking
  - failure modes
  - contract-to-test alignment

## Unknowns and Open Decisions
- UNKNOWN: whether future examples should live beside these docs or continue to
  reference the existing synaptic example files
