# Story: Harden ACL Builder Protocol Typing And Docstrings
- Completed: 2026-04-26T09:56:44Z
- Summary: Closed after the ACL builder-family public-library hardening slice
  landed green with protocol-backed collaborator typing and stronger docstrings.

## Metadata
- Story ID: STORY-2026-04-25-harden-acl-builder-protocol-typing-and-docstrings
- Epic: EPIC-2026-04-25-harden-acl-builder-protocol-typing-and-docstrings
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T20:08:57Z
- Updated: 2026-04-26T09:56:44Z

## User Narrative
As an engineer, I want the ACL builder family to use proper protocols and real
contract docstrings, so the builder API reads like a serious public library
instead of an internal scratch pass.

## Ticket Contract
- ENTRY_GATE: the user explicitly rejected the current builder typing/docstring
  quality and directed a full fix across the builder family.
- EXECUTION_BOUNDARY:
  - `src/melder/utilities/interfaces/interfaces.py`
  - `src/melder/aether/nexus/acl/builder/`
  - focused builder tests
- DEPENDENCIES:
  - `tickets/tasks/2026-04-25_harden_acl_builder_protocol_typing_and_docstrings_task.md`
- EXIT_GATE: the builder family uses protocols where collaborators/configs are
  borrowed and the docstrings are upgraded to the public-library bar.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a correct protocol boundary
  cannot be expressed without widening outside the builder family.

## Notes
- DATETIME: 2026-04-25T20:08:57Z
  TYPE: PLAN
  CLAIM: The story should harden all four builder files together, not file by
    file, because the typing problem crosses `interfaces.py`, the generic
    builder, and the three family-specific builders.
  EVIDENCE:
  - src/melder/aether/nexus/acl/builder/frame_acl_builder.py:1-583
  - src/melder/aether/nexus/acl/builder/frame_acl_codegen_builder.py:1-522
  - src/melder/aether/nexus/acl/builder/frame_acl_view_builder.py:1-420
  - src/melder/aether/nexus/acl/builder/frame_acl_command_builder.py:1-360
  IMPACT: One coherent pass is safer than patching the family asymmetrically.
  NEXT: harden the task across `interfaces.py` and all builder files together.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T20:19:53Z
  TYPE: FACT
  CLAIM: The story is now implemented and green. The fix was not just cosmetic:
    it completed the interface layer for the builder contract, migrated the
    builder family to borrowed protocols, and rewrote the builder prose to the
    public-library bar in the same pass.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:2790-3077
  - src/melder/aether/nexus/acl/builder/frame_acl_builder.py:1-604
  - src/melder/aether/nexus/acl/builder/frame_acl_codegen_builder.py:1-546
  - src/melder/aether/nexus/acl/builder/frame_acl_view_builder.py:1-590
  - src/melder/aether/nexus/acl/builder/frame_acl_command_builder.py:1-525
  IMPACT: The builder family is now materially closer to the repo's intended
    standards instead of only being functionally green.
  NEXT: return the story for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T20:28:38Z
  TYPE: FACT
  CLAIM: The second hardening pass closed the remaining shape-contract gap by
    adding family-builder protocols and switching the public builder signatures
    to those interfaces.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:2870-3103
  - src/melder/aether/nexus/acl/builder/frame_acl_builder.py:1-604
  IMPACT: The story now reflects the protocol-first boundary the user asked
    for instead of only the initial partial hardening pass.
  NEXT: keep the story in review while the user inspects the code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
