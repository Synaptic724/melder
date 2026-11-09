# DevOps Control Plane contract
<!-- BEGIN ENTRY: "SpellValidity terminal name" -->
## Purpose and boundary
SpellValidity plus exact member references in SpellSystemStates and RiskManager.
## Before and after
Rename only cleaned to CLEANED. unknown, valid, gated, invalid and disabled stay lowercase.
## Interface and errors
Keep ordinary Enum, auto values1-6, order and all validity decisions; no lowercase Python alias.
## State and lifecycle
No gate, ownership, lock, registration, notification or cleanup ordering changes.
## Failure delta
Terminal-refusal and risk retirement use the same member under its canonical name.
## Dependencies and order
Read whole implementations before exact reference edits. Land with the declaration and tests.
## Validation and unknowns
Run complete validity, state-retirement, risk and related impacted modules; prove ordinal6.
Direct-consumer full reads remain pending and block those edits.
<!-- END ENTRY: "SpellValidity terminal name" -->
