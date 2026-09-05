# Story: Establish ordered disposal when each Spell is created

## Metadata
- Story ID: STORY-2026-09-04-ordered-disposal-binding
- Epic: EPIC-2026-09-02-ordered-live-spell-disposal
- Epic Ticket: `tickets/epics/2026-09-02_ordered_live_spell_disposal_epic.md`
- Status: in_progress
- Owner: codex
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-04T21:17:27Z
- Updated: 2026-09-05T09:40:08Z

## User Narrative
As a Melder user, I want book and spell disposal names resolved once in a predictable
order, so the Spell records exactly which cleanup operations its instances require.

## Value / MRP Alignment
Binding establishes one coherent input for identity, execution, and persistence.

## Ticket Contract
- ENTRY_GATE: Route a child task after REONBOARD/certification and read its prerequisites.
- EXECUTION_BOUNDARY: Configuration/fluent API, Spellbook bind forwarding, Bind matching,
  Spell metadata, and focused configuration transport/Nexus-default verification.
- DEPENDENCIES: The completed discovery map below; patch contracts precede source edits.
- EXIT_GATE: Four child tasks deliver the contract, configuration, ordered bindings, and
  configuration round-trip evidence. Runtime consumer work proceeds under story 2.
- FAILURE_ESCALATION: Record an actual conflict with the agreed order or configuration
  lifecycle; do not introduce private-mutation defenses or expand matching families.

## Requirements (Functional)
- Use LISTS. Both book and per-spell names contribute at creation.
- `enforce_priority_disposal_methods` defaults False: spell methods first, book methods last.
- True promotes matching book methods to the front in configuration order.
- Preserve first occurrence across both groups; missing profile names are skipped.
- The existing class-profile boundary remains; no factory/instance expansion.
- Bind hashes the resolved ordered list and Spell stores that list directly.
- No first-bind shared override may absorb later new Spells' explicit inputs.

## Requirements (Non-Functional)
- Follow Synaptic direct-access, typing, documentation, and cleanup rules.
- Complete matching once at Spell creation; no repeated disposal-time configuration reads.
- Property defaults must exist before bind, including supplied configurations without defaults.

## Scope Boundaries
- In scope: the four producer files and existing generic configuration transport.
- Out of scope: compiler/Creations implementation, resolved crystal replay, publication.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: Configuration and Bind/Spell implementation are verified and in review;
  configuration transport and later program phases remain pending.

## Dependencies / Related Work
- Discovery: `tickets/tasks/2026-09-02_ordered_spell_disposal_contract_discovery_task.md`
- Next story: `tickets/stories/2026-09-04_ordered_disposal_runtime_story.md`

## Tasks (Implementation Checklist)
- [ ] `tickets/tasks/2026-09-04_ordered_disposal_patch_contract_task.md`
- [ ] `tickets/tasks/2026-09-04_disposal_priority_configuration_task.md`
- [ ] `tickets/tasks/2026-09-04_ordered_disposal_bind_and_spell_task.md`
- [ ] `tickets/tasks/2026-09-04_disposal_configuration_roundtrip_task.md`

## Acceptance Criteria
- Both flag values produce the documented merged order on independently bound Spells.
- Duplicates run once; unmatched names contribute nothing; empty spell input keeps book names.
- Configuration defaults/opt-in, fluent assembly, reload, and Nexus defaults work coherently.
- Hash inputs and the stored Spell list describe the same order.

## Validation / Test Plan
Child tasks own focused tests. Use a verified Python 3.14 interpreter; default python is 3.13.
Configuration and Bind/Spell are implemented; the latest producer and surrounding verification
passes 753 selected tests. Full configuration transport and later runtime/replay work remain pending.

## UX / API / Data Notes
Proposed fluent setter: `with_enforce_priority_disposal_methods(enabled=True)`.
The configuration default is False; the setter's omitted argument opts in to True.
False changes priority only and does not disable book methods.

## Risks / Mitigations
- A seeded set-once default can prevent opting in: handle this in the configuration task.
- A supplied unvalidated config can lack the new flag: establish default availability at setup.

## Applicable Anti-Patterns
- [ ] No source changes before patch contracts and scoped source reads.
- [ ] No old tuple/default-True/override-only proposal used as current direction.

## Open Questions
- None about the accepted composition rule. Technical findings belong in child notes.

## Decision Log
- Owner chose creation-time list composition and optional book priority, default False.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none yet; the contract task owns future patch outputs.
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: after artifacts are created and the completed program is accepted

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: configuration, ordered matching, bind identity
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-04T21:17:27Z
  TYPE: PLAN
  CLAIM: Phase 1 is split into contract, configuration, binding, and configuration transport tasks.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-09-02_ordered_spell_disposal_contract_discovery_task.md:140-320`
  IMPACT: Each child has a bounded implementation or verification deliverable.
  NEXT: Execute the patch-contract task before configuration implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Child outcomes and evidence reviewed; owner accepts story closure.

## Noting Behavior
Record cross-task decisions here; detailed findings remain in the owning child task.

- DATETIME: 2026-09-04T22:39:54Z
  TYPE: MEASURE
  CLAIM: Configuration is implemented and in review, with 115 focused tests passing.
    The configuration-only patch gate is satisfied; other component contracts remain pending.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-09-04_disposal_priority_configuration_task.md`
  IMPACT: The priority setting exists but does not yet affect bound Spell metadata or disposal.
  NEXT: Review configuration, then prepare the separate Bind/Spell implementation contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T09:40:08Z
  TYPE: MEASURE
  CLAIM: The producer successor is implemented and in review: separate book/spell forwarding,
    ordered matching and SHA, direct Spell list storage, and no redundant conjure check.
    The producer and surrounding verification runs pass 753 selected cases on Windows 3.14t.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-09-04_ordered_disposal_bind_and_spell_task.md`
  IMPACT: Configuration and producers are available for consumer work. Full transport,
    compiler/Creations propagation, and replay acceptance are not established by these results.
  NEXT: Review the producer slice, then consume the compiler propagation task's contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Configuration and Bind/Spell source/tests are implemented and in review. The active producer
task records 753 selected passing tests. Full configuration transport remains pending; the
next runtime task owns compiler propagation. Ready tasks still require their entry gates.
The current list/False-default/composition rule supersedes historical tuple/override proposals.
