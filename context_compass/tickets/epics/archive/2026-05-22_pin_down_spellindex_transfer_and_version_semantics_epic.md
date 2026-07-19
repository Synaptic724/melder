# Epic: Pin Down SpellIndex, Transfer, and Version Semantics

## Metadata
- Epic ID: EPIC-2026-05-22-pin-down-spellindex-transfer-and-version-semantics
- Status: in_progress
- Owner: codex
- Agent Name: mutres_0
- Priority: p0
- Created: 2026-05-22T10:17:21Z
- Updated: 2026-05-22T10:17:21Z
- Target Window: 2026-Q2
- Related Program/Initiative: MutationResearch + spell ownership semantic cleanup

## Problem / Opportunity
Current runtime semantics around `SpellIndex`, spell registration, runtime
stewardship, transfer-of-ownership, and mutation/version concerns have drifted
together into one overloaded surface.

Right now the code shows:
- `SpellIndex` owns a mutable `current` pointer and historical `_versions`
- `SpellIndex` also stores `_owner_spellbook`, `_owner_spell`,
  `_owner_conduit_id`, and contracted spellbook attachments
- `Spell` separately stores conduit ownership state
- `Spellbook` separately owns owned and contracted spell-id registries
- `TransferOfOwnership` updates all of those layers together during a transfer

That is semantically muddy. We need to investigate and pin down what these
things are actually supposed to mean before more mutation/version work lands.

## MRP Alignment (Most Reasonable Product)
The MRP is not an immediate refactor.

The MRP is:
- an evidence-backed semantic model
- a clean separation between identification, registration, runtime
  stewardship, and mutation/version semantics
- a bounded follow-up task set that can implement the cleanup without
  rediscovering the model from chat

## Ticket Contract
- ENTRY_GATE: the user explicitly redirected focus to `SpellIndex`,
  transfer-of-ownership, and version-control semantics and wants an
  investigation-first epic.
- EXECUTION_BOUNDARY: investigation and semantic definition first; no runtime
  semantic rewrite until the investigation task and definition story settle the
  model.
- DEPENDENCIES:
  - `src/melder/aether/spellbook/bind/spell_index.py`
  - `src/melder/aether/spellbook/spell.py`
  - `src/melder/aether/spellbook/spellbook.py`
  - `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`
  - `codex/context_compass/tickets/tasks/2026-05-10_investigate_spell_index_runtime_grouping_semantics_task.md`
  - `codex/context_compass/artifacts/2026-05-09_mutation_research_philosophy.md`
- EXIT_GATE: the current semantic drift is mapped, the target semantic split is
  explicit, and bounded implementation tasks exist for the actual cleanup.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if current runtime behavior
  proves incompatible with the user's stated rule that `SpellIndex` is index
  only and not a lineage/version/ownership object.

## Goals (Outcomes)
- Determine the exact current runtime semantics of `SpellIndex`.
- Separate identification semantics from spellbook registration semantics.
- Separate identification semantics from conduit/runtime stewardship semantics.
- Separate transfer-of-ownership semantics from mutation/version semantics.
- Define where mutation/version relationships should live if not on
  `SpellIndex`.

## Non-Goals (Explicit Exclusions)
- Immediate runtime refactor in this epic note.
- Broad MutationResearch API redesign in the first investigation slice.
- Changing conduit behavior before the semantic model is pinned down.
- Solving every historical naming/doc drift issue before current semantics are
  clear.

## Scope Boundaries
- In scope:
  - current source semantics
  - target semantic split
  - epic/story/task decomposition for the cleanup
- Out of scope:
  - code edits that implement the cleanup
  - unrelated mutation socket work
  - unrelated Crystallizer runtime work

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a new epic and an
  investigation-first lane for SpellIndex, transfer, and version semantics.

## Success Metrics
- Investigation task records the exact semantic drift in source-backed terms.
- Definition story states the target semantic split with no hidden ownership
  assumptions.
- Follow-up tasks isolate the runtime cleanup into reviewable slices.

## Requirements (Functional + Non-Functional)
- Functional:
  - map current `SpellIndex` fields and behaviors
  - map current `Spellbook` registration semantics
  - map current `Spell` runtime stewardship semantics
  - map current transfer-of-ownership update path
  - define target placement for mutation/version semantics
- Non-functional:
  - keep claims source-backed
  - no premature semantic rewrite
  - no fake certainty where the target model still needs a decision

## Constraints / Assumptions
- The user has already rejected treating `SpellIndex` as lineage owner or
  version owner.
- Current runtime still uses `SpellIndex.current` and `_versions`.
- MutationResearch and Crystallizer remain combined support context, but this
  epic is focused on the spell/index/transfer semantic layer itself.

## Dependencies / External References
- `src/melder/aether/spellbook/bind/spell_index.py`
- `src/melder/aether/spellbook/spell.py`
- `src/melder/aether/spellbook/spellbook.py`
- `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`
- `codex/context_compass/tickets/tasks/2026-05-10_investigate_spell_index_runtime_grouping_semantics_task.md`
- `codex/context_compass/artifacts/2026-05-09_mutation_research_philosophy.md`

## Milestones (Track Progress)
- [ ] Milestone 1: investigate current semantic drift across SpellIndex,
      Spellbook, Spell, and transfer code
- [ ] Milestone 2: define target semantic split and unresolved decision points
- [ ] Milestone 3: open bounded implementation tasks for the runtime cleanup

## Stories (Required to Complete)
- [ ] Story: STORY-2026-05-22-define-spellindex-transfer-and-registration-semantics - investigate and define the semantic split
- [ ] Story: STORY-2026-05-22-stage-spellindex-semantics-runtime-cleanup - cut the implementation slices after the model is accepted

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-2026-05-22-define-spellindex-transfer-and-registration-semantics
- [ ] Task: Open the runtime cleanup tasks only after the semantic model is accepted
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The source-backed semantic drift is documented.
- The target semantic model is explicit and accepted.
- Bounded runtime cleanup tasks exist and map cleanly to the accepted model.

## Risks / Mitigations
- Risk: current runtime semantics force a larger mutation/version redesign than
  expected.
  Mitigation: keep the first story investigation-only and escalate decisions
  explicitly.
- Risk: `SpellIndex` identity, registration, and runtime stewardship remain
  mixed because the cleanup tries to do everything at once.
  Mitigation: separate the actual refactor into bounded post-investigation
  tasks.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Investigation and semantic definition first.
- Runtime tests only after the semantic cleanup tasks are opened and
  implemented.

## Rollout / Adoption Plan
- First: investigate exact current semantics.
- Second: define target semantic split.
- Third: cut implementation tasks for runtime cleanup.
- Fourth: land the cleanup in bounded slices.

## Open Questions
- If `SpellIndex` is pure identification, what object owns version-selection
  semantics today and what should own them after cleanup?
- Should transfer operate only on current concrete spell stewardship, with no
  semantic relationship to mutation/version selection?
- What is the clean runtime lookup shape once `SpellIndex` no longer carries
  attachment state?

## Decision Log
- 2026-05-22T10:17:21Z: Epic opened as an investigation-first lane after the
  user explicitly rejected the current lineage/ownership reading of
  `SpellIndex`.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-05-22T10:17:21Z
  TYPE: FACT
  CLAIM: Current source mixes four separate concerns into the `SpellIndex`
    surface: stable identity, mutable version-selection state, spellbook
    attachment state, and conduit ownership/contract attachment state. Transfer
    code then updates both the concrete `Spell` ownership fields and the
    `SpellIndex` ownership fields during the same move.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/spell_index.py:32-41
  - src/melder/aether/spellbook/bind/spell_index.py:72-77
  - src/melder/aether/spellbook/bind/spell_index.py:113-173
  - src/melder/aether/spellbook/bind/spell_index.py:174-257
  - src/melder/aether/spellbook/spell.py:847-857
  - src/melder/aether/spellbook/spell.py:1007-1054
  - src/melder/aether/spellbook/spellbook.py:573-830
  - src/melder/aether/spellbook/spellbook.py:1362-1417
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:747-803
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1223-1342
  IMPACT: We cannot safely reason about transfer, mutation, or version control
    semantics until these concerns are separated conceptually.
  NEXT: create the first story/task lane that maps the current semantics and
    defines the target split before any runtime cleanup is attempted.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic exists because current runtime semantics around `SpellIndex`,
spellbook registration, runtime stewardship, transfer, and mutation/version
work have drifted together. The first job is to investigate and define the
split correctly before touching runtime code.
