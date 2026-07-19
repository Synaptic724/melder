# Component Patch: Attention Board Agent Assignment

## Component Purpose and Boundary in Current Architecture
This slice adds `agent_name` to the attention board while preserving `owner`.

## Before/After Behavior Summary
Before:
- board rows only have `owner`

After:
- board rows have both `owner` and `agent_name`
- `owner` keeps executor identity
- `agent_name` carries one or more assigned user-facing names

## Interface Deltas
- New board column:
  - `agent_name`

## Dependency and Ordering Constraints
- board docs and live schema must agree
- live rows must be populated with a current value

## Validation Expectations
- attention board rereads cleanly with the new column in both active and closed
  routing tables

## Unknowns and Open Decisions
- UNKNOWN: whether live legacy rows should eventually be backfilled with
  user-provided names instead of executor placeholders
