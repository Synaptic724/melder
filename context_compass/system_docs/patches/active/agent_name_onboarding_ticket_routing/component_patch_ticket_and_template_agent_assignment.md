# Component Patch: Ticket And Template Agent Assignment

## Component Purpose and Boundary in Current Architecture
This slice adds assigned agent names to ticket metadata and ticketing guidance.

## Before/After Behavior Summary
Before:
- tickets track `Owner` but not assigned user-facing agent names

After:
- tickets track `Agent Name`
- the field supports one or more assigned names
- templates and ticketing docs describe the field explicitly

## Interface Deltas
- New metadata field:
  - `Agent Name: <name>` or `Agent Name: <name_a>, <name_b>`

## Dependency and Ordering Constraints
- ticket templates and ticketing docs must agree on the field name and
  multi-agent representation

## Validation Expectations
- templates reread cleanly with the new field

## Unknowns and Open Decisions
- UNKNOWN: whether future ticket parsers should upgrade comma-separated names
  into a structured list format
