# Task: Reframe SpellIndex as index (not lineage/projection) in crystallizer + mutation_research philosophy artifacts

- Completed: 2026-07-11T21:35:00Z
- Summary: Closed superseded by melder_0 (owner-directed adjudication:
  crystal_0 departed, owner-confirmed only melder_0 + mutation_0
  exist; "crystal_0 might not need their philosophy done if its
  aged"). The delivered part (IMPORTANT_CONSIDERATION reframe, 3
  spots) stands. The PARKED remainder (merge/lane/head model rewrite,
  pending an owner decision) is MOOT: its target artifact
  (2026-05-09 mutation philosophy) was archived superseded by the
  canonical V3 (artifact board, owner-directed salvage read done
  2026-07-11), and V3's lanes/join model IS the answer the parked
  question was waiting for - mutation_0 shipped lane TYPEs from V3's
  Open Directions. No remaining work exists that any live document
  needs.

## Metadata
- Task ID: TASK-2026-07-01-reframe-spellindex-in-crystallizer-mutation-philosophy-artifacts
- Story: none (standalone task)
- Status: closed (superseded by philosophy V3; adjudicated on owner
  directive 2026-07-11)
- Owner: cowork
- Agent Name: crystal_0
- Priority: p2
- Created: 2026-07-01T10:53:36Z
- Updated: 2026-07-02T15:36:06Z

## Objective
Reconcile the crystallizer + mutation_research philosophy artifacts with the
corrected SpellIndex model already applied to the canonical source docs:
SpellIndex is a stable index (ULID) that categorizes/targets spells and holds one
active selected spell; version history is owned by MutationResearch. Strip the
pre-reframe framing of SpellIndex as a lineage identity or as a runtime
projection of a selected lane/head.

## Ticket Contract
- ENTRY_GATE: user directed "update the philosophy" after crystal_0 flagged that
  the April-May philosophy artifacts predate the SpellIndex reframe and still
  carry SpellIndex=lineage/projection framing.
- EXECUTION_BOUNDARY: prose edits only in
  `artifacts/2026-05-09_mutation_research_philosophy.md` and
  `artifacts/IMPORTANT_CONSIDERATION.md`. `2026-04-26_crystallizer_philosophy.md`
  already attributes lineage/version to MutationResearch and needs no edit.
- DEPENDENCIES: none blocking. Parallels the completed source-doc reframe
  (`tickets/tasks/2026-06-20_reframe_spellindex_as_index_not_lineage_in_source_docs_task.md`).
  Related general_0 SpellIndex work is runtime code, not these artifacts.
- EXIT_GATE: the two philosophy artifacts carry no SpellIndex=lineage or
  SpellIndex-as-version-projection framing (grep-clean at the SpellIndex spots);
  user confirms the merge/lane/head model decision and accepts the reframe.
- FAILURE_ESCALATION: raise DECISION_REQUEST for the MutationResearch merge model
  (lane/head/merge-node/rebase vs additive time-based union) - NOT rewritten here
  because it exists only in untrusted pre-compaction memory. Raise CONFLICT if an
  agent reports concurrent edits to these two artifacts.

## Scope Boundaries
- In scope:
  - `mutation_research_philosophy.md`: the "SpellIndex Is Runtime Projection"
    section.
  - `IMPORTANT_CONSIDERATION.md`: Core Concern list + the "Lineage and concrete
    version are separate" section + the coupling-list `SpellIndex.current` ref.
- Out of scope:
  - The MutationResearch merge/lane/head model rewrite (parked; DECISION_REQUEST).
  - `crystallizer_philosophy.md` (already aligned).
  - `2026-05-22_spellindex_multi_spell_transfer_blast_radius.md` (superseded
    multi-spell-per-index design; general_0 runtime lane, not philosophy).
  - Any code under `src/melder/`.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: user gave an explicit directive to update the philosophy;
  the SpellIndex reframe is evidenced by the corrected source docs re-read this
  session, so it proceeds; the merge model stays parked as UNKNOWN.

## Steps / Checklist
- [ ] Reframe the SpellIndex section in `mutation_research_philosophy.md`.
- [ ] Reframe the 3 SpellIndex spots in `IMPORTANT_CONSIDERATION.md`.
- [ ] Re-grep both artifacts; confirm no SpellIndex=lineage/projection framing.
- [ ] Record result in Notes; raise the merge-model DECISION_REQUEST to the user.

## Deliverables
- Reframed SpellIndex descriptions in the two philosophy artifacts.

## Files / Paths Impacted
- `artifacts/2026-05-09_mutation_research_philosophy.md`
- `artifacts/IMPORTANT_CONSIDERATION.md`

## Validation
- Not run yet.
- Recommended:
  - `grep -niE "spellindex[^\\n]*lineage|spellindex\\.current|projection of a selected" artifacts/2026-05-09_mutation_research_philosophy.md artifacts/IMPORTANT_CONSIDERATION.md`

## Risks / Rollback Notes
- Risk: concurrent edit on these artifacts. Mitigation: prose-only; re-read+retry.
- Rollback: revert the two artifacts; no code or graph touched.

## Applicable Anti-Patterns
- [ ] No implementation from UNKNOWN/HYPOTHESIS (merge model stays parked).
- [ ] No status transition without an evidence-backed transition reason.
- [ ] No closure without user acceptance + merge-model decision + board sync.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Validation status recorded
- [ ] Merge-model decision obtained
- [ ] Acceptance confirmed with user
- [ ] Board sync completed for closure anchor update

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- DISPOSITION: retain_as_reference

## Notes
- DATETIME: 2026-07-01T10:53:36Z
  TYPE: DECISION
  CLAIM: Split the "update the philosophy" directive into (1) the evidenced
    SpellIndex reframe, applied now, and (2) the MutationResearch merge/lane/head
    model, parked as a DECISION_REQUEST because it exists only in untrusted
    pre-compaction memory (compaction_requirements forbids treating that as fact).
  EVIDENCE:
  - artifacts/2026-05-09_mutation_research_philosophy.md:487-506
  - artifacts/IMPORTANT_CONSIDERATION.md:69-96
  - system_docs/src_architecture.md:341
  IMPACT: Philosophy stops contradicting the corrected runtime model on SpellIndex
    without risking a wrong merge model written into canonical docs.
  NEXT: apply the edits, re-grep, then raise the merge-model DECISION_REQUEST.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-01T10:53:36Z
  TYPE: MEASURE
  CLAIM: SpellIndex reframe applied and validated clean. 5 spots in
    mutation_research_philosophy.md (section retitled to "A Runtime Index";
    MutationResearch/SpellIndex split rewritten to index-holds-active-selected-
    spell; "many projections"->"many entries"; summary "runtime projections"->
    "runtime index handles"; the "not a lineage" negation dropped for a positive
    statement) and 3 spots in IMPORTANT_CONSIDERATION.md (Core Concern list; the
    renamed "Index and concrete version are separate" section; the coupling
    list). crystallizer_philosophy.md needed no edit (already assigns
    version/lineage to MutationResearch). Grep for the old framing
    (spellindex.current, projection of a selected, stable lineage identity,
    runtime projection, spellindex<->lineage co-occurrence) returns exit 1 (no
    matches) on both files. Remaining "lineage" hits are mutation-lineage
    (MutationResearch's own concept) and left intentionally.
  EVIDENCE:
  - artifacts/2026-05-09_mutation_research_philosophy.md:487-506
  - artifacts/2026-05-09_mutation_research_philosophy.md:918
  - artifacts/IMPORTANT_CONSIDERATION.md:30
  - artifacts/IMPORTANT_CONSIDERATION.md:69-96
  IMPACT: Both philosophy artifacts now match the corrected SpellIndex model;
    exit-gate grep condition met. Held at review pending user acceptance and the
    parked merge-model DECISION_REQUEST.
  NEXT: raise the MutationResearch merge-model decision (lane/head/merge-node/
    rebase vs additive time-based union); on answer, rewrite that half or close.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-01T10:53:36Z
  TYPE: DECISION_REQUEST
  CLAIM: MutationResearch merge/lane/head model. The artifacts describe lanes,
    one head per lane, dominant lanes, merge-creates-a-new-node, rebase, prune,
    collapse. Pre-compaction memory suggests a simpler additive time-based union
    (versions accumulate as DB history, no conflicts). That memory is not
    trustworthy post-compaction, so the merge half is NOT rewritten. Need the
    user to confirm which model is current before touching it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7
- DATETIME: 2026-07-02T15:36:06Z
  TYPE: FACT
  CLAIM: Consumed mailbox NOTICE from melder_0 (2026-07-01T23:50:00Z). Canonical V2
    philosophy artifacts landed and supersede-where-conflicting the two docs this
    reframe lane touched; supersession headers were added under their Status lines.
    This lane's SpellIndex reframe content is reported untouched and consistent with
    V2. V2 deltas: MR = tool/internal-git model (SpellMutationNode / CreationMutationNode,
    MutationConduit-as-gate-orchestrator, MutationFrame retired); crystallizer gains
    universal crystal-at-bind, an AST blast-radius service, and MR composition
    persistence. The parked merge/lane/head DECISION_REQUEST remains open and is now
    also tracked as an open question inside MR philosophy V2.
  EVIDENCE:
  - artifacts/2026-07-01_mutation_research_philosophy_v2.md
  - artifacts/2026-07-01_crystallizer_philosophy_v2.md
  IMPACT: The review-held reframe stays valid under V2 (no rework needed); the still-open
    merge model is corroborated as unresolved, so this ticket stays in review pending the
    user's merge-model decision rather than closing.
  NEXT: Hold at review; on the user's merge-model decision, rewrite that half or close.
    Re-read the two V2 artifacts before any further philosophy edit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-02T16:43:38Z
  TYPE: FACT
  CLAIM: Read the full crystallizer + MR philosophy set in precedence order and
    confirmed the version hierarchy via explicit supersession headers. CANONICAL
    (2026-07-01 V2, updated 07-02): crystallizer_philosophy_v2 (Custody + Unfold)
    supersedes-where-conflicting 2026-04-26 crystallizer_philosophy;
    mutation_research_philosophy_v2 (Tool Model) supersedes-where-conflicting
    2026-05-09 mutation_research_philosophy. Both V2 docs state "this document wins
    on any disagreement." SUPPORTING docs carry no supersession and V2 keeps them:
    crystallizer_configuration (copy-mode; hot-swap boundary non-negotiable),
    file_to_memory_bridge_mechanic (bridge stands), branch_type_enforcement (now
    config policy on ResearchStream), IMPORTANT_CONSIDERATION (still governs world
    merge). Key V2 deltas over the older docs: crystal is MANDATORY at bind (source
    custody); blast-radius / change-judgment RELOCATED from crystallizer to MR's
    code-based impact engine; MR kill-list retires SpellMutationNode /
    CreationMutationNode, MutationConduit-as-gate-orchestrator, and MutationFrame
    (all still described in the older docs); versions are full objects (no
    diff-chain / node-ledger).
  EVIDENCE:
  - artifacts/2026-07-01_crystallizer_philosophy_v2.md:7-7
  - artifacts/2026-07-01_mutation_research_philosophy_v2.md:7-7
  - artifacts/2026-07-01_mutation_research_philosophy_v2.md:182-208
  - artifacts/2026-04-26_crystallizer_philosophy.md:7-8
  - artifacts/2026-05-09_mutation_research_philosophy.md:807-854
  IMPACT: Confirms this reframe lane's target framing is current under V2 and pins
    which older content is the weaker/superseded material. Directly corroborates
    this ticket's parked DECISION_REQUEST: MR V2 keeps world-merge / lane-head-merge
    semantics OPEN (defers to IMPORTANT_CONSIDERATION), so the merge-model half stays
    undecided; the May doc's full lane/head/merge/rebase/prune/collapse model is
    exactly the superseded-where-conflicting content and must not be treated as
    current.
  NEXT: Hold at review; await the user's merge-model decision before touching that
    half of the philosophy.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
crystal_0 reconciling the crystallizer/mutation philosophy artifacts with the
corrected SpellIndex model. SpellIndex reframe applied to two artifacts; the
MutationResearch merge/lane/head-vs-additive-union model is parked pending an
explicit user decision.
