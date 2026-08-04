# Task: Implement Rift Single Space Invariant
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-18-implement-rift-single-space-invariant
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T12:12:27Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Replace the live multi-space `Rift` model with one immutable primary space
created from configuration at Rift construction time, with no runtime surface
for registering or switching spaces afterward.

## Ticket Contract
- ENTRY_GATE: the investigation task mapped the live multi-space blast radius
  and the user approved continuing into implementation with no backward
  compatibility.
- EXECUTION_BOUNDARY: `Rift` single-space runtime surface, the directly
  affected `IRift`/`INexus` contract shapes, the direct `Nexus` consumer path,
  the direct unit tests, the two Rift integration benches, and minimal source
  docs that would otherwise become stale.
- DEPENDENCIES:
  - tickets/tasks/2026-04-18_investigate_rift_single_space_invariant_task.md
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/nexus.py
  - src/melder/utilities/interfaces/interfaces.py
  - tests/unit/melder/aether/test_rift_runtime_contracts.py
  - tests/unit/melder/aether/test_nexus.py
  - tests/integration/melder/aether/rift/static_rift_json_testbench_support.py
  - tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py
  - codex/context_compass/system_docs/src_architecture.md
  - codex/context_compass/system_docs/src_components.md
- EXIT_GATE: `Rift` exposes one immutable space only, no multi-space API or
  compatibility shim remains, and the focused validation ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the single-space invariant
  needs a broader AR redesign than the bounded runtime/doc/test surface above.

## Scope Boundaries
- In scope:
  - `Rift` one-space runtime storage/model
  - singular viewer helper surface
  - `IRift` and `INexus.create_rift(...)` signature changes required by the invariant
  - direct tests and integration benches
  - minimal C4/C3 source-doc updates for the changed owner model
- Out of scope:
  - event-system replacement
  - one-contract-per-frame changes
  - broader `RiftSpace` ownership refactors

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the single-space plan is accepted and the user explicitly
  approved implementation with no backward compatibility.

## Steps / Checklist
- [ ] Remove multi-space storage and APIs from `Rift`.
- [ ] Replace them with one owned `space` surface and singular viewer helpers.
- [ ] Update `IRift` and `INexus.create_rift(...)` for the new surface.
- [ ] Update the direct `Nexus` consumer path.
- [ ] Rewrite the directly affected unit tests and integration benches.
- [ ] Refresh the minimal source-doc sections that describe `Rift` as a
      multi-space owner.
- [ ] Run focused validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- one immutable primary-space `Rift` model
- removed multi-space runtime surface
- focused validation evidence

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py`

## Risks / Rollback Notes
- Risk: removing `active_space_id` and the registry-style API breaks a wider
  set of call sites than the investigation exposed.
- Rollback: keep the change bounded and fail fast instead of slipping in a
  compatibility alias.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-18T12:12:27Z
  TYPE: PLAN
  CLAIM: The implementation will remove the registry model instead of faking a
    single-space invariant on top of it. `Rift` will own one `_space`, the old
    multi-space methods/properties will die, `Nexus` will refresh exactly one
    attached space viewer per Rift, and the tests/benches will move to the
    singular `rift.space` surface.
  EVIDENCE:
  - tickets/tasks/2026-04-18_investigate_rift_single_space_invariant_task.md:96-126
  - user_instruction: "go ahead and continue"
  - user_instruction: "no backward compat"
  IMPACT: The refactor can stay structural and honest instead of preserving
    dead registry vocabulary.
  NEXT: patch `Rift`, then `Nexus`/interfaces, then the direct tests/benches,
    then the minimal source docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T12:26:47Z
  TYPE: FACT
  CLAIM: The runtime refactor is implemented with no compatibility layer.
    `Rift` now owns one `_space`, the registry-style multi-space fields and
    APIs are gone, the singular surface is `rift.space`, and the viewer host
    helpers are now `attach_frame_viewer(...)` and `get_frame_viewer()`.
    `Nexus.create_rift(...)` now takes `space_id` instead of `active_space_id`,
    the one direct `Nexus` multi-space consumer now refreshes a single owned
    space viewer, and the direct unit/integration consumers were rewritten to
    the singular space surface.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:76-95
  - src/melder/aether/nexus/rift/rift.py:108-212
  - src/melder/aether/nexus/rift/rift.py:560-777
  - src/melder/aether/nexus/rift/rift.py:920-1011
  - src/melder/aether/nexus/nexus.py:631-709
  - src/melder/aether/nexus/nexus.py:2012-2030
  - src/melder/utilities/interfaces/interfaces.py:7507-7661
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:378-609
  - tests/unit/melder/aether/test_nexus.py:534-541
  - tests/unit/melder/aether/test_nexus.py:803-812
  - tests/unit/melder/aether/test_nexus.py:2716-2720
  - tests/unit/melder/aether/test_nexus.py:3741-3850
  - tests/integration/melder/aether/rift/static_rift_json_testbench_support.py:183-190
  - tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py:119-126
  - codex/context_compass/system_docs/src_architecture.md:314-314
  - codex/context_compass/system_docs/src_architecture.md:393-393
  - codex/context_compass/system_docs/src_architecture.md:458-462
  - codex/context_compass/system_docs/src_components.md:505-505
  - codex/context_compass/system_docs/src_components.md:531-533
  - codex/context_compass/system_docs/src_components.md:1890-1899
  IMPACT: The live `Rift` owner model now matches the intended architecture
    instead of pretending to support multiple spaces.
  NEXT: record the focused validation result and return the task for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T12:26:47Z
  TYPE: MEASURE
  CLAIM: The focused single-space validation ring is green.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift.py src/melder/aether/nexus/nexus.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py tests/integration/melder/aether/rift/static_rift_json_testbench_support.py tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py` -> 344 passed
  IMPACT: The refactor is stable enough to hand back for acceptance before we
    continue into the event-system replacement.
  NEXT: return the task in review and ask whether to close it or continue
    directly into the next Rift lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the actual runtime/test/doc refactor for collapsing `Rift` to
one immutable primary space.