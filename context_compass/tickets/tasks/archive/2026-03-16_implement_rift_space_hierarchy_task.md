# Task: Implement RiftSpace Hierarchy

## Metadata
- Task ID: TASK-2026-03-16-implement-rift-space-hierarchy
- Story: STORY-2026-03-16-aethericrift-system-bootstrap
- Status: ready
- Owner: codex
- Priority: p0
- Created: 2026-03-16T00:31:16Z
- Updated: 2026-03-16T00:31:16Z

## Objective
Add a class-based `RiftSpace` hierarchy with `StaticRiftSpace` and
`DynamicRiftSpace` subclasses, using ULID identity and a secondary name -> ULID
lookup path that keeps the structure customizable and extendable. Include a
configuration seam for action/memory event enrichment rather than a literal
hook class.

## Ticket Contract
- ENTRY_GATE: `AethericRift` and `AethericRiftState` skeletons exist and the
  system registry is in place.
- EXECUTION_BOUNDARY: space hierarchy and identity/lookup scaffolding only.
- DEPENDENCIES:
  - TASK-2026-03-16-implement-aethericrift-and-state-skeletons
  - src/melder/utilities/helpers/id_builder.py
  - current AR space docs
- EXIT_GATE: a base `RiftSpace` class exists, `StaticRiftSpace` and
  `DynamicRiftSpace` inherit from it, and the hierarchy explicitly supports
  ULID identity plus a secondary name -> ULID lookup path.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the secondary lookup belongs
  somewhere other than the initial hierarchy/registry boundary.

## Scope Boundaries
- In scope:
  - `src/melder/aether/aetheric_rift_system/rift_space/`
  - base class and two subclasses
  - ULID identity
  - secondary name -> ULID lookup plan/scaffold
  - `RiftEventConfiguration` / interaction-configuration seam
- Out of scope:
  - validation semantics
  - full dynamic room behavior
  - profile-driven population

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the requested space hierarchy is a distinct implementation
  slice with its own identity/lookup concerns.

## Steps / Checklist
- [ ] Create the `rift_space/` package.
- [ ] Add a base `RiftSpace` class designed for extension.
- [ ] Add `StaticRiftSpace` and `DynamicRiftSpace` subclasses.
- [ ] Use ULID identity for spaces.
- [ ] Add or plan the secondary name -> ULID lookup dictionary operation.
- [ ] Add `RiftEventConfiguration` (or equivalent) as the extension point for
      action/memory event enrichment and observers.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `RiftSpace` base class
- `StaticRiftSpace` subclass
- `DynamicRiftSpace` subclass
- ULID identity and secondary name lookup scaffold
- `RiftEventConfiguration` scaffold

## Files / Paths Impacted
- src/melder/aether/aetheric_rift_system/rift_space/__init__.py
- src/melder/aether/aetheric_rift_system/rift_space/rift_space.py
- src/melder/aether/aetheric_rift_system/rift_space/static_rift_space.py
- src/melder/aether/aetheric_rift_system/rift_space/dynamic_rift_space.py
- src/melder/aether/aetheric_rift_system/rift_space/rift_event_configuration.py
- tests/unit/melder/aether/

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/unit/melder/aether -k rift_space -v`

## Risks / Rollback Notes
- Risk: the first hierarchy hardcodes behavior that should stay extendable.
  Rollback: keep subclasses thin and the base contract explicit.

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
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-03-16T00:31:16Z
  TYPE: PLAN
  CLAIM: The `RiftSpace` hierarchy should be its own task because identity,
    extensibility, and the secondary name -> ULID lookup path are design
    concerns that can be settled without mixing them into system-registry or
    Aether-facade work.
  EVIDENCE:
  - src/melder/utilities/helpers/id_builder.py:1-16
  - codex/context_compass/tickets/artifacts/aethericrift_v1_object_model_and_build_direction.md:52-67
  IMPACT: Separating the hierarchy task keeps the first code slice class-based
    and extendable rather than turning `RiftSpace` into a one-off data holder.
  NEXT: implement the space hierarchy after the model skeleton task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-21T00:00:00Z
  TYPE: FACT
  CLAIM: The `SpellSpace` implementation provides the closest current precedent
    for the first `RiftSpace` scaffold: ULID identity via `IDBuilder`,
    `Cleanable` lifecycle, internal sentinel tagging, and a deliberately narrow
    ownership boundary around a room-like object.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space.py:1-118
  - src/melder/utilities/helpers/id_builder.py:1-16
  IMPACT: The first `RiftSpace` scaffold can stay minimal and extensible while
    still feeling native to the current Melder object model.
  NEXT: use `SpellSpace` style as the baseline when scaffolding `RiftSpace`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task isolates the class hierarchy and space identity/lookup design from
the rest of the bootstrap so it can evolve cleanly.
