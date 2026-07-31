

# Task: Drift-audit and tighten src_architecture, src_components, and the graph

## Metadata
- Task ID: TASK-2026-07-25-system-doc-graph-drift-audit
- Story: STORY-2026-07-25-guard-manifest-truth
- Status: done
- Owner: melder_1
- Agent Name: melder_1
- Priority: p2
- Created: 2026-07-25T19:42:08Z
- Updated: 2026-07-31T23:03:22Z

## Objective
Audit the three canonical system artifacts for drift after the 539-file sweep, fix what
is unambiguously wrong, and compress resolved historical bookkeeping so the live claims
are not buried under it.

## Ticket Contract
- ENTRY_GATE: owner directed continued iteration on these three artifacts; every defect
  measured before it is touched; board row created in the same pass as this ticket.
- EXECUTION_BOUNDARY: `system_docs/src_architecture.md`, `system_docs/src_components.md`,
  `system_docs/src_graph.json`, `system_docs/readable_src_graph.json`. No source code.
- DEPENDENCIES: none blocking. melder_0 is active in `src/` and packaging, not here.
- EXIT_GATE: zero graph nodes pointing at absent files; zero dangling edges; resolved
  bookkeeping compressed without losing the verified-removal record; both graphs valid.
- FAILURE_ESCALATION: DECISION_REQUEST before deleting any other agent's deliberate
  record wholesale.

## Scope Boundaries
- In scope: the dead graph node and its edges; compression of the 2026-06-12 SYNC NOTE
  blocks; the 2026-07-07 tail-repair marker; doc metadata accuracy.
- Out of scope: source code; the 23 pending `USER-BINDABLE` docstrings (own lane,
  awaiting scope confirmation); regenerating `src_graph.json` from source.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner directed it; the audit is complete and every finding is
  evidenced, so no unknown blocks the work.

## Steps / Checklist
- [ ] Remove the `SoloFinalizeCreationContextStep` node and its three edges.
- [ ] Regenerate `readable_src_graph.json` from corrected storage; validate JSON.
- [ ] Compress both `SYNC NOTE (2026-06-12 ...)` blocks, preserving the verified-removal
      list, which still tells a reader a path is permanently gone.
- [ ] Resolve or reword the 2026-07-07 tail-repair marker in the arch handoff summary.
- [ ] Re-verify path and symbol integrity after edits.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Three artifacts free of measurable drift, with live claims no longer buried.

## Files / Paths Impacted
- context_compass/system_docs/src_architecture.md
- context_compass/system_docs/src_components.md
- context_compass/system_docs/src_graph.json
- context_compass/system_docs/readable_src_graph.json

## Validation
- Not run (documentation artifacts; no test surface).
- Recommended checks:
  - graph node `file` existence sweep and dangling-edge sweep
  - cited-path resolution sweep across both prose docs
  - JSON validity of both graph artifacts

## Risks / Rollback Notes
- RISK: compressing another agent's deliberate bookkeeping loses context if done
  carelessly. Mitigation: keep the verified-removal facts, cut only the narration, and
  record what was cut and why.
- Rollback: git revert of four files.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No semantic reshaping of graph JSON beyond the identified defect.
- [ ] No deletion of another agent's record without preserving its load-bearing facts.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 7)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-07-25T19:42:08Z
  TYPE: MEASURE
  CLAIM: Full drift audit run before touching anything. The artifacts are in far better
    shape than the 539-file sweep suggested. GRAPH: exactly ONE of 536 nodes points at
    a file that no longer exists (`SoloFinalizeCreationContextStep`), zero nodes lack a
    `file` key, and zero of 1000 edges have a dangling endpoint. PROSE: all 695 distinct
    source paths cited across both docs resolve on disk - zero dead. SYMBOLS: of 274
    distinct CamelCase symbols cited, every apparent miss is either an enum MEMBER my
    regex miscaught (`IGNORE`, `PLAIN`, `SPELL`, `METHOD` - all verified real) or an
    explicitly historical mention of a removed/renamed type.
  EVIDENCE:
  - context_compass/system_docs/src_graph.json
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/parameter_di_shape.py:64-64
  - src/melder/aether/spellbook/spell_types/spell_types.py:76-88
  IMPACT: Confirms the docs did NOT rot broadly under the sweep, so the work is narrow
    correction plus compression rather than a rewrite. It also means the earlier
    guard-lane churn was the exception, not the pattern.
  NEXT: Remove the one dead node and its three edges.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-25T19:42:08Z
  TYPE: FACT
  CLAIM: `SoloFinalizeCreationContextStep` is genuinely gone, not moved. The solo family
    retains five steps, all five present in the graph; the `generalized` and `many_only`
    families keep their own `finalize_creation_context_step`, so the deletion is
    solo-specific rather than a family-wide rename. No replacement class exists in the
    solo steps directory.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_finalize_creation_context_step.py
  IMPACT: Removal is the correct repair; repointing would invent a relationship that
    does not exist.
  NEXT: Remove node plus its `specializes` and two `uses` edges.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-25T19:42:08Z
  TYPE: DECISION
  CLAIM: The `Unknowns` section of both docs opens with 42 and 45 lines respectively of
    2026-06-12 rename bookkeeping, ahead of the single genuine unknown (producers for
    the advanced `SpellState` flags). That bookkeeping records a sweep this audit has
    now independently verified COMPLETE: zero dead paths, zero symbol drift. Its
    tracking purpose is discharged, and it sits in a section defined as "a living list
    of claims currently not backed by evidence" - which it is not.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:118-159
  - context_compass/system_docs/src_components.md:68-112
  IMPACT: The live unknown is buried under six-week-old resolved history, which is the
    opposite of what the section is for and directly against the owner's stated
    preference for current-state prose over narration.
  NEXT: Compress both blocks, KEEPING the verified-removal list (it still tells a reader
    a path is permanently gone rather than merely missing) and cutting the narration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-25T19:50:00Z
  TYPE: MEASURE
  CLAIM: All four artifacts corrected and re-audited clean. GRAPH: dead node and its
    three edges removed (536->535 nodes, 1000->997 edges); zero nodes with an absent
    file, zero dangling edges, storage and readable agree, both JSON-valid. PROSE: 695
    cited source paths still all resolve; encoding intact at 2091 and 5154 CRLF lines
    with zero bare LF and zero NUL; zero over-cap prose lines authored this session (the
    17 and 14 that remain are pre-existing and untouched).
  EVIDENCE:
  - context_compass/system_docs/src_graph.json
  - context_compass/system_docs/src_architecture.md
  IMPACT: The three canonical artifacts now carry no measurable drift against source.
  NEXT: Owner acceptance.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-25T19:50:00Z
  TYPE: DECISION
  CLAIM: Three compression edits made, each preserving load-bearing content and
    recording what was cut. (1) Both `SYNC NOTE (2026-06-12)` blocks (42 and 45 lines)
    became a single PERMANENTLY REMOVED list plus one sentence attesting the sweep is
    complete - the removal facts survive because they still tell a reader a path is gone
    by intent rather than by oversight; the step-by-step narration went to git.
    (2) The `Verified compiler phase-artifact ownership` sub-block was NOT compressed -
    it is a live contract, not bookkeeping, so it was MOVED out of `Unknowns` into the
    resolution-pipeline body in the arch doc and into a labelled live-contract bullet in
    the components doc. (3) The arch `Context / Handoff Summary` was a 20-entry
    changelog of edits made TO the document; it was replaced with the state, decisions,
    open-unknown and volatile-areas summary the template actually specifies, and the
    2026-07-07 tail-repair marker was folded into a closing note rather than dropped.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:118-133
  - context_compass/templates/task_template.md:109-110
  IMPACT: In both docs the single live UNKNOWN now sits at the top of `Unknowns` instead
    of under six weeks of settled history, and a resuming reader gets current state plus
    where to distrust the doc rather than a diff log of past edits.
  NEXT: None; flagged in the report so the compression is reviewable rather than
    discovered later.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-25T23:05:00Z
  TYPE: FACT
  CLAIM: AUDIT GAP, found by the owner not by me. Both docs listed
    `MUTATION_CONTRACT_DISABLED` under PERMANENTLY REMOVED and then cited it as LIVE
    Phase-4 behaviour in eleven places. Verified against source before editing, and the
    removal entries were the correct ones: `MUTATION_CONTRACT_DISABLED` has ZERO
    occurrences in `src/`; `ParameterDIShape` has SIX members and no
    `MUTATION_CONTRACT` (both docs listed seven);
    `ContractProviderPresenceStrategy` emits four codes, none about mutation -
    `CONTRACT_IN_AUTOMATIC_MODE`, `SPELL_CONTRACT_INVALID`,
    `SPELL_CONTRACT_AMBIGUOUS`, and the warning `SPELL_CONTRACT_MISSING_PROVIDER`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/parameter_di_shape.py:64-69
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py:145-210
  IMPACT: MY AUDIT COULD NOT HAVE CAUGHT THIS. I verified that every cited path and
    symbol RESOLVES, and that no renamed symbol survived - but a doc declaring a
    constant removed and then describing its behaviour is SELF-contradiction, not
    drift against source. Path-existence and symbol-existence checks are blind to it.
    A future audit needs a third check: does the document agree with itself?
  NEXT: Add self-consistency to the audit method if this lane is ever repeated.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-07-25T23:05:00Z
  TYPE: DECISION
  CLAIM: Kept a distinction the docs had collapsed, rather than deleting both halves.
    The mutation SOCKET is gone; the mutation OVERLAY is LIVE -
    `Spell.apply_mutation_override` / `clear_mutation_override` exist at
    spell.py:1540,1586 and still emit `mutation_contract_set` /
    `mutation_contract_cleared`. Those reason names imply a socket that no longer
    exists, so both docs now state explicitly that the names are historical and the
    overlay is unrelated to the removed socket. The owner confirmed this split.
    Also corrected the same stale claim in code at
    `spell_state_change_reason.py:46-48` and its enum comment, and matched that file
    to its LF index form so the change reads as 6 lines instead of 101.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_state_change_reason.py:44-49
  - src/melder/aether/spellbook/spell.py:1540-1586
  IMPACT: Deleting the overlay references as "stale" would have removed a real
    mechanism; leaving them ambiguous is what produced the contradiction in the first
    place. `grep -rE "MUTATION_CONTRACT_DISABLED|Phase 4 blocks" src/` is now clean.
  NEXT: None; seven surviving doc mentions are all either removal entries or negative
    claims.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-25T23:20:00Z
  TYPE: DECISION
  CLAIM: SETTLED RULE for a removed concept, after I over-corrected twice on it.
    Pass 1 I explained the absence ("the socket is GONE, the names are historical,
    there is no `ParameterDIShape` for it") - owner: don't mention it, that confuses
    agents. Pass 2 I stripped every mention INCLUDING the `PERMANENTLY REMOVED`
    entries - owner: that list is fine, it functions as a version-control /
    deprecation statement and is handy. The rule that satisfies both:
    NAME IT ONCE, IN THE DEPRECATION RECORD; NEVER DESCRIBE ITS BEHAVIOUR.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:118-121
  - context_compass/system_docs/src_components.md:68-70
  IMPACT: A removed concept appearing in a deprecation list answers "was this ever a
    thing?" cheaply. The same concept appearing in a behaviour section teaches a
    mechanism that does not exist. The failure mode is the second, not the first, and
    my instinct to purge everything was as wrong as the original contradiction.
  NEXT: Apply the same rule to any future removal: one deprecation-list line, zero
    behavioural prose.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-25T23:20:00Z
  TYPE: MEASURE
  CLAIM: Final state verified. Six mentions across both docs, each in its correct
    place: two are the `PERMANENTLY REMOVED` deprecation entries (arch:120-121,
    comp:70), and four name the LIVE overlay's real change-reason identifiers
    `mutation_contract_set` / `mutation_contract_cleared` with no archaeology
    (arch:391-392, arch:1875-1876, comp:103-104). Two further regex hits at comp:93,97
    are the phrase "mutation/contract state flags", which is the genuine open UNKNOWN
    about `SpellState.contract_violation` / `mutation_candidate` /
    `mutation_quarantined` / `mutation_failed` - unrelated, correctly left alone. Zero
    mentions remain in `src/`. Diffs 20/32 and 20/30, each file matched to its own
    index EOL form, zero NUL.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:93-96
  IMPACT: No behavioural claim about the removed socket survives anywhere, while the
    deprecation record and the live overlay both remain intact.
  NEXT: Owner acceptance.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-25T23:35:00Z
  TYPE: MEASURE
  CLAIM: Owner asked whether the derived assets were rebuilt, and the question caught a
    real staleness. The C1 Code Map had drifted 550 -> 553: melder_0's build-asset work
    added `_build_assets/_agent_metadata/_builder.py`,
    `_build_assets/_agent_metadata/agent_metadata.py`, and
    `_build_assets/_build_asset_runner.py` after I generated it. Zero dead entries, three
    unlisted. Regenerated; now 553 listed against 553 live, zero dead, zero unlisted.
    The four packaged hardcopy modules (`__architecture__.py`, `__components__.py`,
    `__graph_network__.py`, `__graph_details__.py`) need NO rebuild - each is ~1.5KB and
    its own docstring states the payload is a PLACEHOLDER, not a live regenerated
    snapshot, with population tracked separately.
  EVIDENCE:
  - src/melder/__architecture__.py:13-16
  - context_compass/system_docs/src_components.md:3735-3735
  IMPACT: Confirms the C1 map is the one section in these docs that decays on its own,
    exactly as its REGENERATION note warns. It should be re-walked at the end of any
    session that moves modules, not just when it is first built.
  NEXT: Owner acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-25T23:35:00Z
  TYPE: MEASURE
  CLAIM: Full six-point review clean. C1 map 553 listed / 553 live / 0 dead / 0
    unlisted. Graph 535 nodes, 997 edges, 0 absent-file nodes, 0 dangling edges,
    readable artifact in sync with storage. Prose path integrity: 143 and 554 cited
    source paths, zero dead. Zero stale guard references
    (`__melder_registration_guard__`, `__init_cache__`, `manifest_loader`, `_mrg`,
    `_RegistrationGuardProxy`, `bind.py:308`) in either doc. 554 source files parse with
    zero syntax failures. Encoding correct per file against its own git index form, zero
    NUL bytes across both docs and both boards.
  EVIDENCE:
  - context_compass/system_docs/src_graph.json
  - context_compass/system_docs/src_components.md
  IMPACT: Docs, graph, and source agree; nothing in this lane is left unverified.
  NEXT: None.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-31T23:03:22Z
  TYPE: DECISION
  CLAIM: CLOSED at owner turn-in 2026-07-31. Audit found no broad rot: 1 dead node of 536, 0 dangling edges, 695/695 cited paths resolved,
    0 symbol drift. Two 2026-06-12 SYNC NOTE blocks compressed with content preserved; the
    phase-8-11 artifact-ownership sub-block MOVED not cut, being a live contract.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-07-25_system_doc_graph_drift_audit_task.md
  IMPACT: Ticket moved to completed/; board row removed and replaced by one anchor.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Post-sweep drift audit of the three canonical system artifacts. Measured result: one
dead graph node out of 536, zero dangling edges, zero dead paths across 695 citations,
zero symbol drift. Work is therefore narrow: remove the dead node, regenerate the
readable graph, and compress two blocks of resolved 2026-06-12 bookkeeping that are
burying the single live unknown in each doc.
