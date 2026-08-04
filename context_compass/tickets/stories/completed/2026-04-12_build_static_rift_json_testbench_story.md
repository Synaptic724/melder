# Story: Build Static Rift JSON Testbench
- Completed: 2026-04-13T11:31:28Z
- Summary: Completed the reusable static-room integration harness story and archived it after the static JSON bench and multistep extension both landed.

## Metadata
- Story ID: STORY-2026-04-12-build-static-rift-json-testbench
- Epic: EPIC-2026-04-12-static-rift-integration-testbench
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-12T17:45:00Z
- Updated: 2026-04-13T11:31:28Z

## User Narrative
As the Rift runtime designer, I want one reusable static-room integration
testbench driven by JSON-like requests so I can validate real end-to-end static
behavior instead of relying only on focused unit seams.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a large static-room testbench and
  approved reusing one object system with variations.
- EXECUTION_BOUNDARY: test harness design + implementation only.
- DEPENDENCIES:
  - tickets/epics/2026-04-12_static_rift_integration_testbench_epic.md
  - tests/integration/melder/aether/
- EXIT_GATE: a reusable harness plus JSON-like driver exists and can support a
  large scenario matrix.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the harness needs capability
  or dynamic behavior to stay meaningful.

## Acceptance Criteria
- One reusable static-room harness exists.
- One JSON-like request driver exists.
- The scenario matrix is large and meaningful.
- Focused static integration tests are green.

## Notes
- DATETIME: 2026-04-12T17:45:00Z
  TYPE: PLAN
  CLAIM: The harness should create real Spellbook/Conduit/Nexus/Rift static
    setups and drive them through a JSON-like request envelope with:
    - `surface`
    - `method`
    - `args`
    - `kwargs`
    plus placeholder resolution for known manifest/object symbols.
  EVIDENCE:
  - user_direction: "pretend the json string is a LLM json string"
  - user_direction: "it just calls methods via the API after its setup"
  IMPACT: The testbench can model realistic agent usage instead of only direct
    Python test calls.
  NEXT: create the task and implement the harness under
    `tests/integration/melder/aether/rift/`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:31:28Z
  TYPE: DECISION
  CLAIM: This story is complete. The static-room harness exists, the JSON-like
    request driver exists, and the multistep turn-script extension is landed.
    Later static-room work now treats the bench as settled infrastructure
    rather than pending review work.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-12_implement_static_rift_json_testbench_task.md:1-126
  - tickets/tasks/completed/2026-04-12_add_multistep_turn_scripts_to_static_rift_testbench_task.md:1-176
  IMPACT: The story can move to the completed lane and stop occupying active
    planning state.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This story owned the harness/driver implementation tranche for the static-room
integration testbench. The harness is now part of the settled static-room
validation foundation.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
