# Task: Investigate SpellIndex Runtime Grouping Semantics

## Metadata
- Task ID: TASK-2026-05-10-investigate-spell-index-runtime-grouping-semantics
- Story:
- Epic:
- Status: review
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-10T12:28:58Z
- Updated: 2026-05-10T12:38:12Z

## Objective
Determine whether the current runtime behavior actually treats `SpellIndex` as
the kind of binding-signature grouping container we have been describing, or
whether the code still behaves as a one-spell / one-version-history object and
we only cleaned the wording around it.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked to verify the underlying runtime
  behavior after the rename work, not just the language we landed.
- EXECUTION_BOUNDARY:
  - `src/melder/spellbook/bind/spell_index.py`
  - `src/melder/spellbook/bind/bind.py`
  - `src/melder/spellbook/spellbook.py`
  - direct tests or supporting files only when needed as evidence
- DEPENDENCIES:
  - the completed SpellIndex rename/cleanup lane
- EXIT_GATE: we have an evidence-backed answer about whether the current code
  matches the new SpellIndex grouping assumption.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` only if the runtime behavior is
  too ambiguous to classify without widening into a larger design/code pass.

## Scope Boundaries
- In scope:
  - how `SpellIndex` is created
  - how `SpellIndex` is keyed and looked up
  - whether many spells can share one `SpellIndex`
  - what `current`, `_versions`, owner, and contracted attachments really mean
- Out of scope:
  - changing the runtime
  - reopening conduit lineage work
  - broad MutationResearch redesign

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the runtime-truth investigation is complete enough to
  answer the assumption question directly.

## Steps / Checklist
- [x] Re-read `spell_index.py`.
- [x] Re-read `bind.py` for SpellIndex creation behavior.
- [x] Re-read `spellbook.py` for lookup/ownership/grouping behavior.
- [x] Record whether the current code matches the grouping assumption or not.

## Deliverables
- evidence-backed answer about current SpellIndex runtime semantics

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-05-10_investigate_spell_index_runtime_grouping_semantics_task.md
- codex/context_compass/attention_board.md

## Validation
- Investigation only.

## Risks / Rollback Notes
- Risk: the cleaned language tempts us to overstate the runtime behavior.
  Rollback: keep UNKNOWN as the default until the creation and lookup paths are
  read directly.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No conflation of renamed vocabulary with actual runtime behavior.

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
- DATETIME: 2026-05-10T12:28:58Z
  TYPE: PLAN
  CLAIM: The right question now is not “what words did we change?” It is
    “what does the runtime actually do?” The answer has to come from the
    SpellIndex object, the bind path that creates it, and the Spellbook maps
    that own and resolve it.
  EVIDENCE:
  - user_instruction: "investigate to make sure our underlying assumption is true"
  - user_instruction: "I know right now we don't have the capabity to add spells to a spell_index"
  IMPACT: The lane needs a direct runtime-truth read, not more vocabulary
    cleanup.
  NEXT: inspect `spell_index.py`, `bind.py`, and `spellbook.py` directly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-10T12:38:12Z
  TYPE: FACT
  CLAIM: The current runtime does **not** yet implement `SpellIndex` as a
    true multi-spell grouping container under one binding signature. What the
    code actually does today is:
    - `Bind._bind_logic(...)` always creates a fresh `SpellIndex` for every new
      bind operation.
    - `Spellbook._assert_lookup_key_available(...)` rejects a second different
      `SpellIndex` on the same binding signature.
    - `Spellbook._lookup_spells[key]` maps one binding signature to one
      `SpellIndex`, and `Spellbook._spells[spell_index]` maps that one
      `SpellIndex` to one current spell object.
    - `SpellIndex` itself holds one mutable `current` version pointer, one
      version-id history set, one owner spellbook, one owner spell, and
      contracted attachments keyed by `(spellbook, conduit_id) -> spell`.
  EVIDENCE:
  - src/melder/spellbook/bind/bind.py:241-257
  - src/melder/spellbook/bind/bind.py:289-301
  - src/melder/spellbook/spellbook.py:1265-1292
  - src/melder/spellbook/spellbook.py:1316-1366
  - src/melder/spellbook/spellbook.py:2721-2734
  - src/melder/spellbook/bind/spell_index.py:17-31
  - src/melder/spellbook/bind/spell_index.py:167-249
  IMPACT: The rename work aligned the language toward the desired model, but
    the runtime behavior still matches a one-SpellIndex / one-current-spell /
    one-version-history object keyed by binding signature, not a bucket that
    can already hold many heterogeneous candidate spells under one binding slot.
  NEXT: tell the user the underlying assumption is not yet true in code and
    that bringing out the "many spells under one SpellIndex" capability will
    require actual runtime changes later.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-10T18:07:52Z
  TYPE: FACT
  CLAIM: Current placement and responsibility of `MutationResearch` are
    clear in code. `AethericFrame` **owns** one frame-local MutationResearch
    hub and cleans it during frame teardown; `Aether` only **retrieves** that
    hub by frame name; `Conduit` only **gates access** to it and refuses access
    unless the conduit is normal and dynamic. Inside the mutation subsystem,
    `MutationResearch` owns `Research` sessions keyed by `SpellIndex.id`,
    while each `Research` session borrows one target `SpellIndex`, snapshots
    its starting `current` version into `_root_version`, and owns both
    `ResearchSpell` and `ResearchCreation` lines for that target index. The
    graph surface matches that code: `AethericFrame -> MutationResearch ->
    Research -> (ResearchSpell, ResearchCreation)`, with `Research` borrowing
    `SpellIndex`. There is no graph edge making `Conduit` an owner of
    MutationResearch; conduit is only an access boundary.
  EVIDENCE:
  - src/melder/aether/aetheric_frame.py:20-30
  - src/melder/aether/aetheric_frame.py:90-90
  - src/melder/aether/aetheric_frame.py:195-197
  - src/melder/aether/aetheric_frame.py:281-293
  - src/melder/aether/aether.py:1934-1973
  - src/melder/aether/conduit/conduit.py:3971-4005
  - src/melder/spellbook/mutations/mutation_research.py:66-74
  - src/melder/spellbook/mutations/mutation_research.py:124-166
  - src/melder/spellbook/mutations/mutation_research.py:246-312
  - src/melder/spellbook/mutations/research/research.py:10-17
  - src/melder/spellbook/mutations/research/research.py:33-49
  - src/melder/spellbook/mutations/research/research.py:155-244
  - codex/context_compass/system_docs/readable_src_graph.json:890-896
  - codex/context_compass/system_docs/readable_src_graph.json:1465-1472
  - codex/context_compass/system_docs/readable_src_graph.json:1553-1554
  IMPACT: If we decide to move MutationResearch up a level, we are not moving
    a conduit-owned object. We are moving a frame-owned session manager whose
    present graph interactions are mostly with SpellIndex and its research-line
    children, not with the conduit runtime itself.
  NEXT: summarize this placement and graph-interaction model for the user and
    decide whether the next step is a design ticket for lifting ownership from
    `AethericFrame` toward `Aether`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task checks whether current SpellIndex runtime behavior actually matches
the new grouping/container assumption or whether the rename work only cleaned
the language around an older runtime model.
