# Epic: Static Rift Integration Testbench
- Completed: 2026-04-13T11:31:28Z
- Summary: Completed the static-room integration testbench epic after the reusable harness, JSON request matrix, and multistep turn-script extension all landed.

## Metadata
- Epic ID: EPIC-2026-04-12-static-rift-integration-testbench
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-12T17:45:00Z
- Updated: 2026-04-13T11:31:28Z
- Target Window: 2026-Q2
- Related Program/Initiative: Rift room-mode validation depth

## Problem / Opportunity
Static room behavior is now implemented and green on the focused unit/runtime
ring, but there is still no large reusable integration harness that exercises:
- real Spellbook + Conduit runtime setup
- real Nexus + Rift + StaticRiftSpace targeting
- real static viewer/query behavior
- real static command behavior
- JSON-like request driving as if an LLM were constructing API calls

Without that, static is still mostly proven by unit-focused seams rather than
one reusable integration testbench that can keep catching drift later.

## MRP Alignment (Most Reasonable Product)
The MRP here is not 100 handwritten tests.

It is:
- one reusable real-runtime harness
- one JSON-like action driver
- one large meaningful scenario matrix

That gives us depth without filling the suite with low-value repetition.

## Ticket Contract
- ENTRY_GATE: static runtime behavior is implemented and the user explicitly
  requested a large reusable testbench driven by JSON-like requests.
- EXECUTION_BOUNDARY: integration testbench design + implementation for static
  room behavior only.
- DEPENDENCIES:
  - tests/integration/melder/aether/
  - src/melder/aether/nexus/rift/
  - src/melder/aether/conduit/
  - src/melder/spellbook/
- EXIT_GATE: one reusable static-room integration testbench exists with a
  JSON-like request driver and a large scenario matrix.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the requested coverage
  requires capability/dynamic behavior in the same lane.

## Goals (Outcomes)
- Build one reusable static-room integration harness.
- Drive it with JSON-like request payloads.
- Reuse the same object system with controlled variations.
- Prove static viewer, static command, workstation interaction, and conduit
  discovery together through one matrix lane.

## Non-Goals (Explicit Exclusions)
- Capability-mode behavior.
- Dynamic/codegen behavior.
- Cross-room comparative testing beyond what static needs.

## Scope Boundaries
- In scope:
  - static room integration harness
  - JSON-like request driver
  - scenario matrix
  - focused static integration validation
- Out of scope:
  - capability harness
  - dynamic harness
  - performance benchmarking

## Success Metrics
- A reusable harness exists under `tests/integration/melder/aether/rift/`.
- The harness is driven by JSON-like requests, not ad hoc direct calls only.
- The scenario matrix is large enough to stress static behavior meaningfully.

## Stories (Required to Complete)
- [x] Story: design and implement the static Rift testbench harness
- [x] Story: validate the large static scenario matrix

## Notes
- DATETIME: 2026-04-12T17:45:00Z
  TYPE: PLAN
  CLAIM: The integration work should follow the repo’s existing real-runtime
    matrix style, not invent a new testing philosophy. The nearest patterns are
    the existing Nexus/Rift integration matrix files and the reusable
    descriptor/viewer support helpers. The new lane should adapt that pattern
    into a static-room-specific harness plus a JSON-like request driver.
  EVIDENCE:
  - tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py:1-166
  - tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py:1-385
  - tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py:1-196
  - tests/_nexus_viewer_matrix_support.py:1-330
  IMPACT: We can build this testbench quickly and coherently by reusing the
    repo’s current integration style instead of starting from zero.
  NEXT: create the story/task route and then implement the harness under
    `tests/integration/melder/aether/rift/`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:31:28Z
  TYPE: DECISION
  CLAIM: This epic is complete. The reusable static-room harness exists under
    `tests/integration/melder/aether/rift/`, the JSON-like request matrix is
    landed, and the multistep turn-script extension is landed. Later static
    room work now consumes the bench as stable infrastructure instead of as a
    pending epic lane.
  EVIDENCE:
  - tickets/stories/completed/2026-04-12_build_static_rift_json_testbench_story.md:1-45
  - tickets/tasks/completed/2026-04-12_implement_static_rift_json_testbench_task.md:1-126
  - tickets/tasks/completed/2026-04-12_add_multistep_turn_scripts_to_static_rift_testbench_task.md:1-176
  IMPACT: The static testbench epic no longer belongs in the active epic lane.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This epic owned the static-room integration testbench lane: real runtime
setup, JSON-like request driving, and a large reusable scenario matrix. That
lane is now complete and archived as settled static-room infrastructure.
