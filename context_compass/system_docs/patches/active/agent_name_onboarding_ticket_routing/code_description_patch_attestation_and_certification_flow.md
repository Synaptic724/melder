# Code Description Patch: Attestation And Certification Flow

## Control Flow Commitments
- Every ONBOARD and REONBOARD cycle asks the user for an `AGENT_NAME`.
- The attestation includes `AGENT_NAME`.
- The approval ask requests both `AGENT_NAME` and `CERTIFY: APPROVED`.

## Edge and Error Semantics
- Missing `AGENT_NAME` means the cycle is not fully complete.
- Missing `CERTIFY: APPROVED` still blocks tool use and edits.

## Invariants and Non-Goals
- Keep `CERTIFY: APPROVED` exact.
- Do not turn the naming field into a separate approval token.
- Keep the feature additive to current workflow.

## Implementation Mapping
- general docs implement the prompt and attestation requirements
- templates implement ticket metadata
- attention board implements the live routing field
