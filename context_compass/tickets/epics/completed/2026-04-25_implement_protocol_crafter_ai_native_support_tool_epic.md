# Epic: Implement Protocol Crafter AI-Native Support Tool
- Completed: 2026-04-26T09:56:44Z
- Summary: Closed after the first protocol-crafter utility lane landed and the
  task/story/epic stack all converged on a green bounded slice.

## Metadata
- Epic ID: EPIC-2026-04-25-implement-protocol-crafter-ai-native-support-tool
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T20:28:38Z
- Updated: 2026-04-26T09:56:44Z

## Problem / Opportunity
The repo uses protocols heavily, but there is no first-class support tool for
generating protocol mirrors from a target class/object and then updating an
interface file cleanly.

## MRP Alignment (Most Reasonable Product)
The MRP is one bounded support utility:
- `ProtocolCrafter`
- protocol code generation from class/object input
- add-to-interface-file helper
- remove-from-interface-file helper
- focused unit tests

## Ticket Contract
- ENTRY_GATE: the user explicitly requested this utility lane.
- EXECUTION_BOUNDARY: utility implementation, focused tests, and routing.
- DEPENDENCIES:
  - `src/melder/utilities/interfaces/interfaces.py`
  - `src/melder/utilities/`
- EXIT_GATE: `ProtocolCrafter` lands green with generation and interface-file
  update helpers.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the requested generation
  contract needs a different attribute-mirroring rule than the bounded
  best-effort default.

## Notes
- DATETIME: 2026-04-25T20:28:38Z
  TYPE: DECISION
  CLAIM: This belongs in a dedicated `ai_native_support_tools` package, not as
    ad hoc code in `interfaces.py` or another builder lane.
  EVIDENCE:
  - user_instruction: requested `utilities/ai_native_support_tools`
  IMPACT: The work is now a standalone utility lane.
  NEXT: implement the story and task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T20:46:36Z
  TYPE: MEASURE
  CLAIM: The first protocol-crafter utility slice is implemented and green. The
    epic now has a concrete utility object and focused tests instead of only a
    proposal.
  EVIDENCE:
  - src/melder/utilities/ai_native_support_tools/protocol_crafter.py:1-660
  - tests/unit/melder/utilities/test_protocol_crafter.py:1-176
  IMPACT: The epic can move to review while the user inspects the utility.
  NEXT: wait for review feedback or a follow-on feature request.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
