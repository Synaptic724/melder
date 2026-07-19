# Component Patch: Onboarding Identity Flow

## Component Purpose and Boundary in Current Architecture
This slice adds mandatory name capture to onboarding/re-onboarding
certification and attestation flow.

## Before/After Behavior Summary
Before:
- certification asks only for `CERTIFY: APPROVED`
- attestation formats do not carry agent naming

After:
- certification asks for `AGENT_NAME` plus `CERTIFY: APPROVED`
- ONBOARD/REONBOARD attestations carry `AGENT_NAME`
- the name request happens every onboarding cycle

## Interface Deltas (Inputs, Outputs, Error Semantics)
- Inputs:
  - user-supplied `AGENT_NAME`
  - user-supplied `CERTIFY: APPROVED`
- Outputs:
  - attestation carrying the chosen name

## Dependency and Ordering Constraints
- `AGENT_NAME` request must happen before or with certification ask
- attestation format must mention the chosen name explicitly

## Validation Expectations
- general docs reread cleanly and consistently use `AGENT_NAME`

## Unknowns and Open Decisions
- UNKNOWN: whether a future persistence surface should remember names across
  sessions or keep them cycle-local
