# Epic: Harden ACL Builder Protocol Typing And Docstrings
- Completed: 2026-04-26T09:56:44Z
- Summary: Closed after the ACL builder family hardening program landed green
  and the bounded task/story/epic stack was fully turned in.

## Metadata
- Epic ID: EPIC-2026-04-25-harden-acl-builder-protocol-typing-and-docstrings
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T20:08:57Z
- Updated: 2026-04-26T09:56:44Z

## Problem / Opportunity
The ACL builder family landed functionally, but the builder files do not yet
meet the repo's public-library quality bar:
- borrowed collaborators are still typed against concrete classes instead of
  protocols
- the existing interface layer is incomplete for the actual builder contract
- several builder methods have weak or missing docstrings
- the class docstrings are not rich enough for a public API surface

## MRP Alignment (Most Reasonable Product)
The MRP is a hardening pass, not another feature lane:
- complete the protocol surface needed by the builder family
- update the builders to use borrowed protocols instead of concrete imports
- rewrite the builder docstrings to real contract docstrings
- keep behavior unchanged unless the existing validator/protocol contract
  requires a bounded fix

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a full hardening pass across the
  ACL builder family and asked for an epic first.
- EXECUTION_BOUNDARY: builder typing/docstring hardening only.
- DEPENDENCIES:
  - `src/melder/utilities/interfaces/interfaces.py`
  - `src/melder/aether/nexus/acl/builder/`
- EXIT_GATE: the builder family uses protocols for borrowed collaborators and
  borrowed typed configs, docstrings are upgraded across the family, and the
  focused builder ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a proper protocol boundary
  would require a wider ACL architecture change.

## Notes
- DATETIME: 2026-04-25T20:08:57Z
  TYPE: DECISION
  CLAIM: The next builder lane is not new authoring surface. It is quality
    hardening: protocol-first typing and public-library docstrings across the
    ACL builder family.
  EVIDENCE:
  - user_instruction: "this should be a protocol"
  - user_instruction: "your docstrings are fucken garbage"
  IMPACT: The builder lane should now be treated as a bounded quality pass
    instead of another feature rollout.
  NEXT: stage the task and patch docs, then harden `interfaces.py` plus the
    builder files together.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T20:19:53Z
  TYPE: MEASURE
  CLAIM: The builder-family hardening slice is implemented and green. The lane
    completed the missing protocol boundaries and fixed the builder-family
    docstring quality without widening into another feature program.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-04-25_harden_acl_builder_protocol_typing_and_docstrings_task.md:1-116
  - src/melder/utilities/interfaces/interfaces.py:2790-3077
  - src/melder/aether/nexus/acl/builder/frame_acl_builder.py:1-604
  IMPACT: This epic can move to review while the user inspects the code.
  NEXT: wait for user review feedback or a follow-on hardening cut.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T20:28:38Z
  TYPE: FACT
  CLAIM: The epic now includes the full protocol-first correction, not just the
    first partial hardening pass. The builder-family contract is now expressed
    through configuration and family-builder protocols across the builder
    surface.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:2870-3103
  - src/melder/aether/nexus/acl/builder/frame_acl_builder.py:1-604
  IMPACT: The epic is ready for code review on the full requested correction.
  NEXT: wait for user review feedback.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
