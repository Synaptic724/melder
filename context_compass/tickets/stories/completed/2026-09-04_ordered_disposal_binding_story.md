# Story: Establish ordered disposal when each Spell is created

## Metadata
- Story ID: STORY-2026-09-04-ordered-disposal-binding
- Epic: EPIC-2026-09-02-ordered-live-spell-disposal
- Epic Ticket: `tickets/epics/completed/2026-09-02_ordered_live_spell_disposal_epic.md`
- Status: done
- Completed: 2026-09-05T14:22:02Z
- Summary: Delivered creation-time configuration, ordered matching, stable identity, and configuration transport.
- Owner: codex
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-04T21:17:27Z
- Updated: 2026-09-05T14:22:02Z

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
- `enforce_priority_disposal_methods` defaults False: spell-only methods first, book block last.
- True promotes matching book methods to the front in configuration order.
- Shared names belong to the book block in both modes; each block preserves supplied order.
- Deduplicate each accepted name; missing profile names are skipped.
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
- from_state: in_progress
- to_state: done
- transition_reason: Owner accepted delivery and requested this closure; completed at 2026-09-05T14:22:02Z.

## Dependencies / Related Work
- Discovery: `tickets/tasks/completed/2026-09-02_ordered_spell_disposal_contract_discovery_task.md`
- Next story: `tickets/stories/completed/2026-09-04_ordered_disposal_runtime_story.md`

## Tasks (Implementation Checklist)
- [x] `tickets/tasks/completed/2026-09-04_ordered_disposal_patch_contract_task.md`
- [x] `tickets/tasks/completed/2026-09-04_disposal_priority_configuration_task.md`
- [x] `tickets/tasks/completed/2026-09-04_ordered_disposal_bind_and_spell_task.md`
- [x] `tickets/tasks/completed/2026-09-04_disposal_configuration_roundtrip_task.md`

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
- [x] No source changes before patch contracts and scoped source reads.
- [x] No old tuple/default-True/override-only proposal used as current direction.

## Open Questions
- None about the accepted composition rule. Technical findings belong in child notes.

## Decision Log
- Owner chose creation-time list composition and optional book priority, default False.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false (closed)
- ARTIFACT_PATHS: none active
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: owner-accepted closure 2026-09-05T14:22:02Z
- Durable contracts: source architecture/components, source docstrings, README, configuration guide,
  and committed regression tests. Temporary patches/probes/validation scratch are removed at closure.
- Historical artifact citations in Notes are retained; tracked patches are recoverable from Git history.

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
  - `context_compass/tickets/tasks/completed/2026-09-02_ordered_spell_disposal_contract_discovery_task.md:140-320`
  IMPACT: Each child has a bounded implementation or verification deliverable.
  NEXT: Execute the patch-contract task before configuration implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T14:22:02Z
  TYPE: DECISION
  CLAIM: Owner accepted this deliverable and requested closure of the ordered-disposal program.
    Delivered creation-time configuration, ordered matching, stable identity, and configuration transport.
  EVIDENCE: tickets/tasks/completed/2026-09-04_ordered_disposal_end_to_end_validation_task.md
  IMPACT: Ticket history is retained under completed. Registered temporary artifacts are disposed
    at accepted closure; durable behavior is in canonical docs, examples, source, and regression tests.
    Linux/hosted checks and unrelated recording/name-lookup findings retain their documented scope.
  NEXT: none; this work item is closed.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Child outcomes and evidence reviewed; owner accepts story closure.

## Noting Behavior
Record cross-task decisions here; detailed findings remain in the owning child task.

- DATETIME: 2026-09-04T22:39:54Z
  TYPE: MEASURE
  CLAIM: Configuration is implemented and in review, with 115 focused tests passing.
    The configuration-only patch gate is satisfied; other component contracts remain pending.
  EVIDENCE:
  - `context_compass/tickets/tasks/completed/2026-09-04_disposal_priority_configuration_task.md`
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
  - `context_compass/tickets/tasks/completed/2026-09-04_ordered_disposal_bind_and_spell_task.md`
  IMPACT: Configuration and producers are available for consumer work. Full transport,
    compiler/Creations propagation, and replay acceptance are not established by these results.
  NEXT: Review the producer slice, then consume the compiler propagation task's contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T11:08:48Z
  TYPE: MEASURE
  CLAIM: Configuration transport is verified by 59 focused tests, including six new real
    emission/profile/checkpoint/JSON/reload cases and Nexus defaults. No transport source changes.
  EVIDENCE:
  - `context_compass/tickets/tasks/completed/2026-09-04_disposal_configuration_roundtrip_task.md`
  IMPACT: Producer and configuration-transport prerequisites are satisfied. Runtime is also
    verified; persistence work now holds a reproduced differing-host graft policy decision.
  NEXT: Resolve the graft policy decision in the crystal/replay task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T11:37:10Z
  TYPE: MEASURE
  CLAIM: Owner's clarified overlap contract is implemented: book order owns shared names in
    both modes, while the flag chooses front/back placement. Updated producer/runtime tests
    pass 2,807 selected cases; 10 new cases cover overlap identity and repeated composition.
  EVIDENCE:
  - `context_compass/tickets/tasks/completed/2026-09-04_ordered_disposal_bind_and_spell_task.md`
  IMPACT: Producer prerequisite is back in review; the runtime still needs no extra policy calls.
  NEXT: Continue the crystal/replay slice using the clarified book block.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
CLOSED: 2026-09-05T14:22:02Z. Delivered creation-time configuration, ordered matching, stable identity, and configuration transport.
Program record: tickets/epics/completed/2026-09-02_ordered_live_spell_disposal_epic.md
No active work remains in this ticket. Prior handoff text below is historical.

### Historical handoff at closure
Configuration, Bind/Spell, and configuration transport are implemented/verified and in review.
Transport has 59 passing checks with no source correction. Runtime is also verified separately.
The crystal/replay task is blocked on an explicit receiving-host policy/live-ID decision.
The list/False-default/composition rule remains settled; no post-creation mutation support is added.
