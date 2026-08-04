

# Task: Reframe SpellIndex as an index (not a lineage) in canonical source docs

## Metadata
- Task ID: TASK-2026-06-20-reframe-spellindex-as-index-not-lineage-in-source-docs
- Story: none (standalone task)
- Status: review
- Owner: cowork
- Agent Name: crystal_0
- Priority: p2
- Created: 2026-06-20T17:07:33Z
- Updated: 2026-06-20T17:07:33Z

## Objective
Update the canonical prose source docs so SpellIndex is described as an index
(a stable key that categorizes and targets spells and holds the active selected
spell), not as a version lineage. Version history/lineage is owned by
MutationResearch, not SpellIndex.

## Ticket Contract
- ENTRY_GATE: active board row routes this task; user explicitly directed the
  reframe and over-rode the general_0-overlap concern ("just update the docs").
- EXECUTION_BOUNDARY: prose edits only in
  `system_docs/src_architecture.md` and `system_docs/src_components.md`.
- DEPENDENCIES: none blocking. Overlaps general_0 lanes
  (`spellindex_terminology_rename`, `spellindex_genuine_index_operations`);
  handled via a mailbox NOTICE, not a code dependency.
- EXIT_GATE: both prose docs carry no SpellIndex=lineage framing (grep-clean for
  the SpellIndex-tied spots) and the user confirms acceptance.
- FAILURE_ESCALATION: raise CONFLICT if general_0 reports a concurrent re-sync of
  the same two .md files; raise DECISION_REQUEST if the user wants the broader
  SpellSystemStates dev-ops "lineage" vocabulary changed too.

## Scope Boundaries
- In scope:
  - `src_architecture.md`: L341 glossary, L1098 invariant, L1295 code map.
  - `src_components.md`: L365 responsibility, L380 owned-state, the
    "SpellIndex Lineage Tracking" subcomponent (L2073-2084), L2465 mutation note.
- Out of scope:
  - `src_graph.json` / `readable_src_graph.json` (derived graph; general_0 regen lane).
  - `SpellSystemStates` dev-ops "lineage" vocabulary (separate concept; hope_0 lanes).
  - Any code change under `src/melder/`.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: user gave an explicit, repeated directive to update the docs
  now and confirmed the index framing and the proceed-despite-overlap decision.

## Steps / Checklist
- [ ] Reframe the 3 SpellIndex spots in `src_architecture.md`.
- [ ] Reframe the SpellIndex spots in `src_components.md` (incl. subcomponent heading).
- [ ] Post mailbox NOTICE to general_0 + attention-board alert line.
- [ ] Validate: re-grep both docs; confirm zero SpellIndex=lineage framing remains.
- [ ] Document the result in `## Notes`; request user acceptance before closure.

## Deliverables
- Reframed SpellIndex descriptions in the two canonical source docs.

## Files / Paths Impacted
- `codex/context_compass/system_docs/src_architecture.md`
- `codex/context_compass/system_docs/src_components.md`

## Validation
- Not run yet.
- Recommended check:
  - `grep -niE "spellindex.*lineage|create SpellIndex lineages|Lineage Tracking" system_docs/src_architecture.md system_docs/src_components.md`

## Risks / Rollback Notes
- Risk: concurrent edit clobber with general_0 on the same two .md files.
  Mitigation: mailbox NOTICE; prose-only; re-read+retry on write conflict.
- Rollback: revert the two .md files; no code or graph touched.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for closure anchor update

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Keep notes append-only; promote UNKNOWN to FACT only with evidence pointers.

## Notes
- DATETIME: 2026-06-20T17:07:33Z
  TYPE: DECISION
  CLAIM: Scope locked to a prose-only SpellIndex lineage->index reframe in the two
    canonical source docs. SpellIndex is an index (categorize/target spells, hold
    the active selected spell); versions/lineage are owned by MutationResearch.
    Graph artifacts and the dev-ops "lineage" vocabulary are explicitly excluded.
  EVIDENCE:
  - system_docs/src_architecture.md:341-341
  - system_docs/src_architecture.md:1098-1098
  - system_docs/src_components.md:365-365
  - system_docs/src_components.md:2073-2084
  IMPACT: Stops the canonical docs from contradicting the corrected runtime model
    (SpellIndex = one active spell; versions owned by MutationResearch).
  NEXT: apply the prose edits, then re-grep to confirm clean.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-06-20T17:07:33Z
  TYPE: MEASURE
  CLAIM: Prose reframe applied and validated. Re-grep of both docs shows the old
    SpellIndex=lineage framing is gone (no "Lineage Tracking", "create SpellIndex
    lineages", "selected-spell pointer", "version pointer", "set of versions", or
    "anchored to SpellIndex lineages"). The only remaining SpellIndex+lineage
    co-occurrences are deliberate "is an index, not a lineage" corrective clauses.
  EVIDENCE:
  - system_docs/src_architecture.md:341-342
  - system_docs/src_architecture.md:1100-1101
  - system_docs/src_components.md:380-380
  - system_docs/src_components.md:2076-2082
  IMPACT: Canonical docs now match the corrected model (SpellIndex = index;
    versions owned by MutationResearch). Exit-gate grep condition met.
  NEXT: confirm with user whether to keep the "not a lineage" negations or go
    purely positive; then close + board-sync on acceptance.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-06-20T17:07:33Z
  TYPE: FACT
  CLAIM: Per user directive, removed the word "lineage" entirely from every
    SpellIndex description (dropped the "not a lineage" hedges); SpellIndex is now
    stated purely positively as an index. Re-grep: zero SpellIndex<->lineage
    co-occurrences in either doc. Remaining "lineage" hits are unrelated concepts
    (ConduitWard lineage trees, the `unique_per_conduit_lineage` existence mode,
    SpellSystemStates dev-ops lineage) and were intentionally left.
  EVIDENCE:
  - system_docs/src_architecture.md:341-342
  - system_docs/src_components.md:380-380
  - system_docs/src_components.md:2076-2077
  IMPACT: SpellIndex framing in canonical docs is now fully index-based; exit-gate
    grep condition met.
  NEXT: await user acceptance to close + board-sync.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
User-directed doc reframe: SpellIndex is an index, not a lineage. Prose-only edits
in src_architecture.md + src_components.md; graph and dev-ops lineage vocab out of
scope. Coordinated with general_0 via mailbox NOTICE. Awaiting user acceptance to
close.
