# Story: Update Frame Configuration And Local Config Test Surfaces
- Completed: 2026-05-16T15:47:45Z
- Summary: Closed after explicit test rewrites removed the temporary compat layer and the full suite passed.


## Metadata
- Story ID: STORY-2026-05-16-update-frame-configuration-and-local-config-test-surfaces
- Epic: EPIC-2026-05-16-explicit-aetheric-frame-configuration-and-spellbook-local-config
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-16T08:07:52Z
- Updated: 2026-05-16T15:47:45Z

## User Narrative
As the project owner, I want the frame/local config split covered by focused
tests, so that explicit frame setup, bounded waits, and field ownership rules
do not regress under concurrent or multi-Spellbook use.

## Value / MRP Alignment
This story protects the real concurrency boundary. If the explicit frame setup
is not tested well, the runtime can fall back into hidden sharing or race
conditions even if the code looks cleaner on paper.

## Ticket Contract
- ENTRY_GATE: the investigation story has logged the exact test surfaces and
  the implementation story has the final runtime shape ready for validation.
- EXECUTION_BOUNDARY: tests only for the frame/local config split and explicit
  setup lifecycle.
- DEPENDENCIES:
  - STORY-2026-05-16-investigate-frame-configuration-ownership-and-race-surfaces
  - STORY-2026-05-16-implement-explicit-frame-configuration-and-local-config-split
  - `tests/unit/melder/aether/test_aetheric_frame_configuration.py`
  - `tests/unit/melder/spellbook/configuration/test_configuration.py`
  - `tests/unit/melder/spellbook/test_spellbook.py`
  - `tests/unit/melder/aether/conduit/**`
  - `tests/integration/melder/aether/**`
- EXIT_GATE: the new lifecycle, ownership split, and timeout/concurrency
  semantics are covered by focused passing tests.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the implementation shape
  requires a much broader test rewrite than currently scoped.

## Requirements (Functional)
- Cover explicit frame setup success path.
- Cover concurrent/second-Spellbook wait path.
- Cover timeout path when frame config remains pending.
- Cover conflict path when a later Spellbook proposes incompatible frame
  posture.
- Cover that local-only config values are not inherited from Aether.
- Cover that per-Spellbook hooks remain localized.
- Cover `overrides_enabled` local behavior across ownership stamping / transfer
  if the implementation keeps it local.

## Requirements (Non-Functional)
- Deterministic.
- No sleep-heavy flaky concurrency tests.
- Clear separation between unit/component/integration responsibilities.

## Scope Boundaries
- In scope:
  - config ownership tests
  - explicit setup lifecycle tests
  - bounded wait/timeout tests
  - multi-Spellbook same-frame tests
- Out of scope:
  - broad override/compiler-path tests unrelated to this ownership split
  - unrelated Nexus/descriptor validation expansion

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the test lane is staged with the exact high-risk behaviors
  it needs to cover once the implementation story lands.

## Dependencies / Related Work
- tickets/epics/2026-05-16_explicit_aetheric_frame_configuration_and_spellbook_local_config_epic.md
- tickets/stories/2026-05-16_investigate_frame_configuration_ownership_and_race_surfaces_story.md
- tickets/stories/2026-05-16_implement_explicit_frame_configuration_and_local_config_split_story.md

## Tasks (Implementation Checklist)
- [ ] Task: update unit tests around `AethericFrameConfiguration` and `Configuration`
- [ ] Task: add multi-Spellbook same-frame tests around explicit configure and local-only config
- [ ] Task: add bounded wait/timeout tests for `conjure()`
- [ ] Task: add compatibility/conflict tests for repeated frame configure attempts
- [ ] Task: verify hook localization remains per `spellbook_id`
- [ ] Enforce Ticket Microcycle across the test lane.
- [ ] Require meaningful-finding note updates during validation.

## Acceptance Criteria
- The explicit configure path is tested.
- The bounded wait and timeout behavior is tested.
- The local-only config non-inheritance behavior is tested.
- The frame-global posture compatibility/conflict behavior is tested.

## Validation / Test Plan
- Unit:
  - frame posture state/claim logic
  - config field ownership
  - hook localization
- Component:
  - multi-Spellbook same-frame configure/conjure behavior
- Integration:
  - explicit setup path around Aether/Nexus frame posture usage where needed

## UX / API / Data Notes
- Errors to cover:
  - frame not configured
  - frame configuration pending timeout
  - frame configuration conflict
  - frame configuration failed

## Risks / Mitigations
- Risk: concurrency tests become flaky.
  Mitigation: use deterministic gates/conditions and explicit signaling instead
  of timing-only assertions.
- Risk: test scope widens into unrelated runtime paths.
  Mitigation: keep focus on config ownership and setup lifecycle only.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No validation claims without direct test-result evidence.

## Open Questions
- Exact timeout test shape.
- Whether the implementation will expose retry/reset hooks that need explicit
  test coverage.

## Decision Log
- pending

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-05-16T08:07:52Z
  TYPE: PLAN
  CLAIM: The highest-risk regression surfaces are already visible from the
    design discussion: same-frame multi-Spellbook configure races, hidden
    inheritance of local rich config from Aether, hook-localization drift, and
    incorrect handling of local `overrides_enabled` behavior when spells move
    between owners.
  EVIDENCE:
  - user_instruction: "n number of spellbooks are being configured at the same time but we're using a single aetheric_frame"
  - user_instruction: "we need a threadsafe way to turn on a gate"
  - user_instruction: "we should really only be pulling down the frame configuration and letting the user setup the Configuration"
  - user_instruction: "overrides_enabled into the configuration ... when you transfer a spell to another conduit you'd need to check if overrides_enabled = true in the new spellbook"
  IMPACT: The test story needs to cover both ownership semantics and the
    cross-owner spell/runtime consequences, not only the initial configure
    happy path.
  NEXT: use the investigation inventory to translate these risks into concrete
    unit/component/integration tests after the implementation story lands.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T08:07:52Z
  TYPE: FACT
  CLAIM: The initial test surface is already clear enough to stage. The most
    obvious unit anchors are `test_configuration.py`,
    `test_aetheric_frame_configuration.py`, and `test_spellbook.py`; the
    likely runtime-behavior and ownership follow-ons are under Aether/conduit
    and Aether integration tests; and the new cases needed are configure claim
    success, concurrent second-Spellbook wait, timeout, conflicting frame
    posture, local-only config non-inheritance, hook localization, and local
    `overrides_enabled` behavior when spells change owners.
  EVIDENCE:
  - tests/unit/melder/spellbook/configuration/test_configuration.py:1-402
  - tests/unit/melder/aether/test_aetheric_frame_configuration.py:1-200
  - src/melder/spellbook/spellbook.py:2887-2908
  - src/melder/spellbook/spellbook_creation_system.py:222-225
  - src/melder/aether/aether.py:794-867
  IMPACT: The later test work can stay tight and high-signal instead of
    rediscovering the obvious validation surfaces from scratch.
  NEXT: translate these anchors into exact test edits once the implementation
    story settles the final API/state shape.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when test scope, timeout semantics, or owner-transfer behavior changes.
- Reference implementation/investigation evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story stages the validation lane for the explicit frame configure and
local Spellbook config ownership change.

