# Task: Map MutationResearch Aether Migration

- Completed: 2026-07-11T19:30:00Z
- Summary: Closed done with its parent epic (owner directive). The
  ownership/collaborator map served its purpose: the Aether migration it
  mapped was executed (MR is the Aether-hosted root today) and the old
  frame-local surfaces it inventoried are gone.

## Metadata
- Task ID: TASK-2026-05-10-map-mutation-research-aether-migration
- Story:
- Epic: EPIC-2026-05-10-design-mutation-research-runtime-surfaces
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-10T22:36:02Z
- Updated: 2026-05-10T22:39:41Z

## Objective
Map the current `AethericFrame` ownership and collaborator surface of
`MutationResearch`, then define the cleanest move toward `Aether`-level
ownership and the responsibilities that object should keep there.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked to map `MutationResearch` in
  `AethericFrame`, what it touches, how it can migrate to `Aether`, and what
  its responsibilities should be.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/aetheric_frame.py`
  - `src/melder/aether/aether.py`
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/spellbook/mutations/mutation_research.py`
  - `src/melder/spellbook/mutations/research/research.py`
  - nearby direct mutation-research children only when needed as evidence
- DEPENDENCIES:
  - `tickets/epics/2026-05-10_design_mutation_research_runtime_surfaces_epic.md`
  - `artifacts/2026-05-09_mutation_research_philosophy.md`
- EXIT_GATE: the current ownership/collaborator map and the Aether-level
  migration responsibilities are explicit enough to guide later implementation
  work.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` only if the current code proves
  that moving ownership to `Aether` would break a deeper runtime contract than
  the design currently assumes.

## Scope Boundaries
- In scope:
  - current ownership location
  - current collaborator surface
  - Aether migration seams
  - role/responsibility definition
- Out of scope:
  - implementation of the move
  - MutationConduit implementation
  - MutationFrame implementation

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested this ownership/migration map.

## Steps / Checklist
- [ ] Re-read current `AethericFrame` ownership path.
- [ ] Re-read `Aether` and `Conduit` retrieval/gating path.
- [ ] Re-read `MutationResearch` and `Research` collaborators.
- [ ] Record the current collaborator map and migration responsibilities.

## Deliverables
- evidence-backed ownership/collaborator map
- Aether-level migration responsibility summary

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-05-10_map_mutation_research_aether_migration_task.md
- codex/context_compass/attention_board.md

## Validation
- Investigation only.

## Risks / Rollback Notes
- Risk: overstate how centralized MutationResearch should become before the
  runtime facade work is proven.
  Rollback: keep the migration summary limited to ownership and collaborator
  responsibilities, not final implementation shape.

## Applicable Anti-Patterns
- [ ] No implementation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No pretending the Aether-level move is already coded.
- [ ] No conflating MutationConduit / MutationFrame design with current ownership facts.

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
- DATETIME: 2026-05-10T22:36:02Z
  TYPE: PLAN
  CLAIM: The next investigation slice is purely architectural: map where
    `MutationResearch` is owned today, what objects it currently touches, and
    what responsibilities should move with it if ownership lifts toward
    `Aether`. The aim is to separate present facts from future facade design.
  EVIDENCE:
  - user_instruction: "map out mutation research in the aetheric_frame and what it touches and how we can migrate it to the Aether"
  - user_instruction: "we'll actually be managing mutation research first and moving it out of the frame context and up to the aether first"
  IMPACT: Later implementation work can move the ownership root cleanly before
    the broader runtime surfaces are built.
  NEXT: read the current ownership and collaborator code paths directly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-10T22:37:20Z
  TYPE: FACT
  CLAIM: Current ownership is shallow and well-bounded. `AethericFrame`
    constructs and cleans one `MutationResearch` instance as a frame-owned
    child service. `Aether` does not own mutation logic semantically; it only
    retrieves the frame-local object through `_get_mutation_research(...)`.
    `Conduit` is only the public dynamic-mode gate to that retrieval path.
    Inside the mutation subsystem, `MutationResearch` keeps:
    - one frame reference
    - a sessions map keyed by `SpellIndex.id`
    - convenience entrypoints for spell and creation mutation
    and each `Research` session keeps:
    - one borrowed `SpellIndex`
    - the starting concrete `current` version as `_root_version`
    - child `ResearchSpell` and `ResearchCreation` lines
    - a shallow promotion hook that can move `SpellIndex.current`
      but does not own the larger runtime adoption choreography
  EVIDENCE:
  - src/melder/aether/aetheric_frame.py:17-30
  - src/melder/aether/aetheric_frame.py:85-99
  - src/melder/aether/aetheric_frame.py:179-201
  - src/melder/aether/aetheric_frame.py:281-293
  - src/melder/aether/aether.py:1934-1973
  - src/melder/aether/conduit/conduit.py:3971-4005
  - src/melder/spellbook/mutations/mutation_research.py:66-74
  - src/melder/spellbook/mutations/mutation_research.py:82-166
  - src/melder/spellbook/mutations/mutation_research.py:246-312
  - src/melder/spellbook/mutations/research/research.py:12-20
  - src/melder/spellbook/mutations/research/research.py:35-49
  - src/melder/spellbook/mutations/research/research.py:155-343
  IMPACT: Moving ownership up toward `Aether` is mostly a root-placement and
    retrieval refactor, not a deep conduit/runtime surgery. The bigger design
    work is deciding which responsibilities stay on the Aether-level research
    authority versus moving into future mutation facades like
    `MutationConduit`.
  NEXT: map the intended Aether-level responsibilities explicitly and separate
    them from conduit/frame facade responsibilities.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-10T22:39:41Z
  TYPE: FACT
  CLAIM: `MutationResearch` currently has very few real dependencies and very
    few real dependents. Internally it depends on:
    - one `IAethericFrame` reference
    - `SpellIndex` identity/current state
    - `Research` child sessions
    - low-level utility bases (`Cleanable`, `IDBuilder`, `RLock`)
    It does **not** currently depend on a central mutation configuration system,
    and it does not currently talk directly to `SpellSystemStates`,
    `ChangeControlManager`, or creation gates itself. On the other side, the
    only production runtime dependents are:
    - `AethericFrame`, which constructs/owns it
    - `Aether`, which retrieves it
    - `Conduit`, which gates access to it
    There is no broader runtime subsystem currently depending on
    `MutationResearch` methods beyond that retrieval path.
  EVIDENCE:
  - src/melder/spellbook/mutations/mutation_research.py:1-312
  - src/melder/spellbook/mutations/research/research.py:1-343
  - src/melder/aether/aetheric_frame.py:11-12
  - src/melder/aether/aetheric_frame.py:90-90
  - src/melder/aether/aether.py:1934-1973
  - src/melder/aether/conduit/conduit.py:3971-4005
  - source_scan:
    `rg -n "MutationResearch|get_mutation_research|begin_spell_mutation|begin_creation_mutation|create_session|get_session_for_index|get_session_by_index_id|list_sessions|remove_session_for_index" src tests`
  IMPACT: This makes the Aether-level move low-risk from a dependency angle.
    MutationResearch is not deeply entangled yet, and there is no central
    mutation config surface to untangle before moving ownership.
  NEXT: define the narrow Aether-level responsibilities for the moved object
    and keep configuration assumptions local to the calling frame/conduit
    surfaces for now.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the current ownership/collaborator map and the Aether-level
migration summary for `MutationResearch`.
