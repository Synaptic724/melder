

# Task: Finish the probe and system-document portability follow-ups

## Metadata
- Task ID: TASK-2026-09-28-finish-probe-and-doc-portability-followups
- Story: none
- Status: done
- Owner: user
- Agent Name: melder_0
- Priority: p3
- Created: 2026-09-28T01:08:20Z
- Updated: 2026-09-28T08:39:36Z
- Completed: 2026-09-28T08:39:36Z
- Closure Basis: owner direction in chat (2026-09-28): "just keep iterating anything you got left", then "ok continue"
  after the remaining steps were named as this turn-in.

## Objective
Close the two follow-ups melder_0's last two lanes left open, on the owner's direction (chat, 2026-09-28): "keep
iterating ... you don't have to regen assets right now ... just keep iterating anything you got left".
(1) `ConduitMeld._describe_spell_live_creation_status`'s contract says broad-lived existences read
`owner_creations`, while its code reads the lineage root and the elected leader for those two lifetimes.
(2) The `## Indexing` sections of src_architecture and src_components paste the index tool's commands and a
skill citation, which a reader of the packaged copy cannot resolve; a few handoff lines name patch-lane paths.

## Ticket Contract
- ENTRY_GATE: this board row; the owner's direction and asset waiver recorded; findings noted before edits;
  sole-writer NOTICE for conduit_meld.py sent before its edit.
- EXECUTION_BOUNDARY: conduit_meld.py docstrings only (no behaviour); src_architecture.md and
  src_components.md (the Indexing sections and the lines the portability check flags) with their indexes;
  the ConduitMeld graph node; `__version__`; the release note. No asset or bundle rebuild (owner waiver).
- DEPENDENCIES:
  - tickets/tasks/completed/2026-09-28_count_space_held_many_in_spellspace_live_creation_probe_task.md
- EXIT_GATE: the docstring matches the code it describes; both portability checks from the authoring
  instructions return nothing on both documents; indexes current; preservation accounted for; ConduitMeld
  read against its prose and accepted; notch and release note current; stale assets recorded as waived.
- FAILURE_ESCALATION: DECISION_REQUEST if removing a path loses information a reader needs and no logical
  name can carry it; BLOCKER if the docs cannot be indexed.

## Scope Boundaries
- In scope: the two follow-ups above.
- Out of scope: behaviour, other docstrings, fable_0's Meld and Spellbook graph nodes (fable_0's lane),
  rewording document filenames that are not paths into the tooling, asset and bundle rebuilds.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner direction in chat (2026-09-28) to keep iterating on what is left, with the asset
  rebuild waived for now; both follow-ups are recorded with evidence in the closed probe task.
- from_state: in_progress
- to_state: done
- transition_reason: Docstrings and portability landed at 0.2.8205 with docs, graph and the release note; the
  waived rebuild is covered by workflows_0's 0.2.8206 rebuild, checks OK; closed on the owner's direction
  (DECISION note 2026-09-28T08:38:55Z).

## Steps / Checklist
- [x] ConduitMeld: read conduit_meld.py whole, fix the probe contract, NOTICE first.
- [x] Portability: baselines, rewrite both Indexing sections without tool paths, fix flagged handoff lines,
      rebuild indexes, run both portability checks.
- [x] Graph, notch, release note; record the asset waiver.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- conduit_meld.py docstrings (six places) name the store each lifetime uses (`many` and `unique_per_conduit`:
  the conduit's store; `unique`: the Spell owner; lineage: the lineage root; cluster: the elected leader) and
  replace the stale active-spellspace claim with the released-space refusal; no code changed.
- src_architecture and src_components: `## Indexing` keeps its prose and heading rules without the tool
  commands or the tooling's specification; patch-lane and skill paths became logical names; conduit_meld.py
  remeasured in the C1 map; one handoff paragraph each; indexes rebuilt.
- Graph: ConduitMeld prose rewritten from the full read and accepted; `__version__` 0.2.8205 and a release-note
  packaging bullet.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/conduit_meld.py (docstrings only)
- src/melder/__version__.py (0.2.8204 -> 0.2.8205)
- release_docs/next_version_release.md (header, packaging bullet)
- context_compass/system_docs/src_architecture.md and src_architecture_index.md
- context_compass/system_docs/src_components.md and src_components_index.md
- context_compass/system_docs/graph/ (conduit_meld.json authored and accepted; the extraction re-hashed
  __version__, eight asset descriptors and duplicate_spell_name_strategy), src_graph.md and src_graph_index.md
- context_compass/artifacts/probe_and_portability_followups_20260928/

## Validation
- 0.2.8205, before the rebuild (assets stale by the owner's waiver): meld/conduit tests 1915 passed; the
  package/asset/system-document set 287 passed, 1 skipped, 1 failed - the stamped-assets test, expected while
  assets were stale (validation_0_2_8205_stale_assets.txt); 3.14t PYTHON_GIL=0.
- 0.2.8206, after workflows_0's rebuild: both portability checks 0 hits on both documents; index --check OK;
  asset --check OK; LLM --check --include-untracked OK; test_package_version_metadata.py 4 passed
  (validation_0_2_8206_after_rebuild.txt).
- Full suite, benchmarks: not run - docstring and document text only, nothing on the meld path.
- Coverage: Not run.

## Risks / Rollback Notes
- Docstring and document text only. Rollback is a revert of one change set.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.
- [x] No graph acceptance without reading the node's source against its prose.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/probe_and_portability_followups_20260928/
- DISPOSITION: retain_as_reference (apply and edit scripts, graph run logs and walker reports, preservation
  report, validation logs)
- CLEANUP_TRIGGER: task closure

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
- DATETIME: 2026-09-28T01:08:20Z
  TYPE: DECISION
  CLAIM: Lane opened on the owner's direction (chat, 2026-09-28): keep iterating on what is left; the asset and
    bundle rebuild is waived for this pass, so the asset --check will report stale after these edits and the
    release note's rebuild line stays at the last rebuilt version. Scope: the two follow-ups recorded in the
    probe task's DECISION note; fable_0's Meld and Spellbook graph nodes stay with fable_0.
  EVIDENCE: context_compass/tickets/tasks/completed/2026-09-28_count_space_held_many_in_spellspace_live_creation_probe_task.md:362-378
  IMPACT: Source changes stay docstring-only; one notch at landing; no rebuild.
  NEXT: Read conduit_meld.py whole and record what its docstrings and graph prose get wrong.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-28T01:09:08Z
  TYPE: FACT
  CLAIM: Read conduit_meld.py whole (1075 lines). Its code sends each lifetime to one store: `many` and
    `unique_per_conduit` to `_conduit_creations`; `unique` to `spell._owner_creations`; lineage to
    `_root_creations`; cluster to `_cluster_creations.resolved_store()` (purge, reuse-only and the probe alike;
    the emitted executors pick the same stores). Five docstring places say something else: the class contract
    and `meld` say broad-lived existences (cluster and lineage included) use spell-owned `owner_creations`;
    `meld_existing_spell` says "shared owner-creations"; `_describe_spell_live_creation_status` says broad-lived
    existences read `owner_creations`; the class System Context says SpellSpace "enforces that it is the ACTIVE
    spellspace for the conduit before melding" - no such check exists (a released space is refused; corrected
    in the system docs at 0.2.8203, this docstring was missed). `describe_live_creation_status` promises "its
    active spellspace" in the payload; this door always reports `active_spellspace_id` None. Graph: ConduitMeld
    is SEMANTICS_STALE since fable_0's 0.2.8201 mint of `_fast_input_doors`; its prose omits that mint and calls
    the probes "conduit-scoped" although they read the shared stores too; every other line matches the code.
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:13-78
  - src/melder/aether/conduit/meld/conduit_meld.py:204-257
  - src/melder/aether/conduit/meld/conduit_meld.py:259-706
  - src/melder/aether/conduit/meld/conduit_meld.py:708-863
  - src/melder/aether/conduit/meld/conduit_meld.py:865-928
  - src/melder/aether/conduit/meld/conduit_meld.py:960-1075
  - src/melder/aether/conduit/spell_space/spell_space.py:513-531
  IMPACT: Docstring-only fixes in six places; no behaviour. The ConduitMeld node can be accepted after its
    prose gains the mint and the store list.
  NEXT: PLAN note with exact edits and files, then the sole-writer NOTICE.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-28T01:10:06Z
  TYPE: PLAN
  CLAIM: melder_0 writes every file below. (1) conduit_meld.py, docstrings only, six places: the class contract
    and System Context, `meld`, `meld_existing_spell`, `describe_live_creation_status` and the probe contract
    name the store each lifetime uses (`unique` -> Spell owner, lineage -> lineage root, cluster -> elected
    leader); the System Context drops the active-spellspace claim for the released-space refusal; the probe
    says this door reports no spellspace. (2) src_architecture.md and src_components.md: each `## Indexing`
    keeps its prose and heading rules but loses the three tool commands and the skill citation (the authoring
    instructions already hold the commands, so they are relocated, not lost); src_architecture's index rules
    move above its citation-check subsection; the lines the portability check flags (patch-lane and skill
    paths in C1 notes, companion list and handoffs) and five bare skill-file names become logical names;
    conduit_meld.py remeasured in src_components C1; a handoff line per document. Indexes rebuilt, both
    portability checks from the authoring instructions must return nothing, preservation accounted for. (3)
    Graph: extract, ConduitMeld prose gains the name/class mint and the store list, read and accepted;
    assemble. (4) `__version__` notch at landing (expected 0.2.8205), release-note header and one packaging
    bullet; the rebuild line keeps the last rebuilt version. (5) No asset or bundle rebuild (owner waiver);
    run the meld and package tests to record what the stale assets fail.
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:13-78
  - context_compass/system_docs/src_architecture.md:33-115
  - context_compass/system_docs/src_components.md:22-107
  - context_compass/agent_onboarding/default/design_engineer/skills/src_architecture_instructions.md:134-175
  - context_compass/agent_onboarding/default/design_engineer/skills/src_components_instructions.md:132-173
  IMPACT: No behaviour changes; the packaged copies of the two documents change at the next rebuild.
  NEXT: NOTICE the conduit_meld.py claim to the active agents, then the docstring edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-28T01:11:24Z
  TYPE: FACT
  CLAIM: conduit_meld.py docstrings corrected in the six planned places (apply script in the lane's artifact dir;
    CRLF kept; the file parses; 1075 -> 1087 lines): the class contract, System Context, `meld`,
    `meld_existing_spell` and the probe name the store per lifetime; the System Context's active-spellspace
    claim is replaced by the released-space refusal with a dated correction; the public probe says this door
    reports no spellspace. No code changed. `__version__` read at landing (0.2.8204) and set to 0.2.8205 at
    01:10:58Z. The meld unit tests, the conduit facade and the spellspace creations component file pass on
    3.14t GIL 0 (280).
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:21-32
  - src/melder/aether/conduit/meld/conduit_meld.py:58-74
  - src/melder/aether/conduit/meld/conduit_meld.py:324-327
  - src/melder/aether/conduit/meld/conduit_meld.py:738-741
  - src/melder/aether/conduit/meld/conduit_meld.py:894-896
  - src/melder/aether/conduit/meld/conduit_meld.py:979-988
  - src/melder/__version__.py:12-12
  - context_compass/artifacts/probe_and_portability_followups_20260928/apply/apply_1_conduit_meld_docstrings.py:1-90
  IMPACT: The source half of the lane is on the tree; docs, graph and release note follow.
  NEXT: Capture the preservation baselines of both system documents, then rewrite the Indexing sections.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-28T01:13:18Z
  TYPE: FACT
  CLAIM: Portability pass landed in both documents (edit script in the lane's artifact dir). Each `## Indexing`
    keeps its prose, heading rules and citation-check recipe but no longer pastes the three index-tool
    commands (they already sit in the authoring instructions' Indexing Contract, so they are relocated, not
    lost) or cites the tooling's specification; src_architecture's index rules moved above its citation
    subsection. Patch-lane paths, the companion-list entry and five skill-file names became the patch id,
    "the documentation tooling's open patch lanes" and "authoring instructions"; conduit_meld.py is
    remeasured in src_components C1 (1087); one handoff paragraph per document. Both portability checks from
    the authoring instructions (package paths; absolute paths) return nothing on both documents; indexes
    rebuilt and --check OK (57 sections over 3220 lines; 147 over 10162). Preservation: 22 and 31 lost lines,
    all accounted for (report in the lane's artifact dir).
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:33-56
  - context_compass/system_docs/src_components.md:22-47
  - context_compass/artifacts/probe_and_portability_followups_20260928/doc_preservation/preservation_report.md:1-25
  - context_compass/agent_onboarding/default/design_engineer/skills/src_architecture_instructions.md:57-107
  IMPACT: The two packaged documents stop naming the tooling once assets are rebuilt; the source docs are clean now.
  NEXT: Extract the graph, rewrite and accept the ConduitMeld prose, assemble.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-28T01:17:04Z
  TYPE: FACT
  CLAIM: Graph refreshed. The first extraction failed writing duplicate_spell_name_strategy.json (EINVAL on open,
    a transient host-side lock; the file stayed intact and valid); the retry completed (--strict, skipped 0).
    It re-hashed conduit_meld, __version__, 8 asset descriptors and workflows_0's in-flight
    duplicate_spell_name_strategy (their DuplicateSpellNameStrategy node now reads SEMANTICS_STALE - their
    lane's to re-accept). ConduitMeld's prose was rewritten from the full read (the probes read the store
    each lifetime uses; it mints the name/class entries it never reads) and accepted; no other authored field
    changed. A third extraction to re-indent the walker's write hit the same lock after conduit_meld.json was
    rewritten, so no further runs. Assemble: src_graph.md 27544 lines, 584 ranges verified, no machine paths.
    Census 1060 -> 1061 AUTHORED, 142 -> 141 stale.
  EVIDENCE:
  - context_compass/artifacts/probe_and_portability_followups_20260928/docs/graph_extract_run1.txt:1-16
  - context_compass/artifacts/probe_and_portability_followups_20260928/docs/graph_extract_run2.txt:1-4
  - context_compass/artifacts/probe_and_portability_followups_20260928/docs/edit_graph_descriptors.py:1-36
  - context_compass/artifacts/probe_and_portability_followups_20260928/docs/graph_walker_report_after.txt:1-8
  IMPACT: The graph describes ConduitMeld as it is; only the release note remains before closure.
  NEXT: Release-note header 0.2.8205 and one packaging bullet.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-28T08:28:43Z
  TYPE: FACT
  CLAIM: Resumed after the device link dropped (01:18Z-08:28Z). State at resume: my edits are intact
    (conduit_meld.py unchanged since 01:10Z; the validation run recorded meld/conduit 1915 passed and the package
    set 287 passed with the one expected stale-asset failure, test_generated_build_assets_are_stamped_for_the_
    live_version; its asset --check step never ran). Mailbox: workflows_0 asked at 01:11Z (WF0-1, ACK requested)
    to be told when my pass on src_architecture/src_components and graph assembly was free, then at 08:22Z
    (WF0-2) proceeded because my ticket records the edits finished, and at 08:24Z (WF0-3) took 0.2.8206 for the
    qualified-name validation fix, with the asset rebuild following in their lane. Checked after their edits:
    the release note is at 0.2.8206 with my packaging bullet kept; both portability checks still return nothing
    on both documents and my handoff paragraphs remain. The asset rebuild my waiver deferred is now carried by
    workflows_0's lane.
  EVIDENCE:
  - context_compass/artifacts/probe_and_portability_followups_20260928/validation_0_2_8205_stale_assets.txt:1-7
  - context_compass/mailbox_board.md:454-464
  - context_compass/mailbox_board.md:495-513
  - release_docs/next_version_release.md:100-115
  - src/melder/__version__.py:12-12
  IMPACT: Nothing in this lane remains to edit; the shared documents and graph assembly are free for workflows_0.
  NEXT: ACK WF0-1 with the release of my claim, consume the three messages, then turn in.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-28T08:35:32Z
  TYPE: FACT
  CLAIM: After the 08:28:43Z note: ACK M0-91 went to workflows_0 at 08:28:59Z and they consumed it (no message to
    them remains); WF0-1/2/3 were consumed (no message to melder_0 remains); index --check was OK on both
    documents (57 sections over 3236 lines; 147 over 10185). A context compaction followed. REONBOARD completed
    at 08:34Z, self-certified as melder_0 under the owner's standing rule, with one disclosed lapse before it (a
    scratch note outside the repository and a read of this ticket); check-in written 08:34:49Z. This lane's board
    row is stale (it still names the conduit_meld.py read) and goes at turn-in. workflows_0 departed at 08:31:05Z
    and its closed anchor says its final asset checks follow its turn-in, so whether assets are current at
    0.2.8206 is UNKNOWN until checked.
  EVIDENCE:
  - context_compass/mailbox_board.md:84-90
  - context_compass/attention_board.md:124-124
  - context_compass/attention_board.md:131-131
  - context_compass/system_docs/src_architecture_index.md:11-19
  - context_compass/system_docs/src_components_index.md:11-19
  IMPACT: Nothing in the lane remains to edit; the closure needs current validation, and the asset state decides
    what the closing NOTICE says about the rebuild.
  NEXT: Run the closing checks read-only: portability grep and index --check on both documents, asset --check and
    LLM --check.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-28T08:37:41Z
  TYPE: MEASURE
  CLAIM: Closing checks at 0.2.8206 (read-only, 3.14t PYTHON_GIL=0, device tree): both portability checks
    (package paths; absolute paths) return 0 hits on src_architecture and src_components; index --check OK (57
    sections over 3236 lines; 147 over 10185); asset --check OK for all three assets at v0.2.8206; LLM --check
    --include-untracked OK for src, tests and other; test_package_version_metadata.py 4 passed, including the
    stamped-assets test that failed at 0.2.8205 while assets were stale. So workflows_0's lane rebuilt assets and
    bundles after my edits, and this lane's waived rebuild is covered. The release note carries my packaging
    bullet and a rebuild line naming 0.2.8206. Not run: the full suite, coverage, benchmarks.
  EVIDENCE:
  - context_compass/artifacts/probe_and_portability_followups_20260928/validation_0_2_8206_after_rebuild.txt:1-15
  - tests/unit/melder/test_package_version_metadata.py:23-86
  - release_docs/next_version_release.md:108-115
  IMPACT: Every exit-gate item is met; the lane can close with nothing owed on assets.
  NEXT: DECISION note for the turn-in, then the closure edits and the move to completed.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-28T08:38:55Z
  TYPE: DECISION
  CLAIM: Turned in on the owner's direction in chat (2026-09-28): "keep iterating ... anything you got left", then
    "ok continue" after my report named the turn-in as the remaining step. Acceptance is that direction, and the
    exit gate is met: the ConduitMeld docstrings match the code; both portability checks return nothing on both
    documents; indexes current; preservation accounted for; ConduitMeld read and accepted; notched 0.2.8205 with
    the release note's packaging bullet; the waived rebuild is covered by workflows_0's 0.2.8206 rebuild (asset
    and LLM checks OK). The walker now reads 1062 AUTHORED / 140 stale: workflows_0's DuplicateSpellNameStrategy
    node, which my 01:17Z extraction left stale, is no longer on the stale list. Left for fable_0, not done here:
    the Meld and Spellbook nodes (meld.py, spellbook.py) stay SEMANTICS_STALE in fable_0's lane.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-09-28_finish_probe_and_doc_portability_followups_task.md:19-24
  - context_compass/tickets/tasks/completed/2026-09-28_finish_probe_and_doc_portability_followups_task.md:34-36
  - context_compass/artifacts/probe_and_portability_followups_20260928/validation_0_2_8206_after_rebuild.txt:1-15
  - context_compass/artifacts/probe_and_portability_followups_20260928/docs/graph_walker_report_turn_in.txt:1-10
  IMPACT: The lane closes with nothing owed; my sole-writer claims on conduit_meld.py and the two system documents
    are released.
  NEXT: Close: metadata, transition, checklists, validation and handoff; move to completed; boards; closing NOTICE.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
State (2026-09-28): done. At 0.2.8205 the ConduitMeld docstrings name the store each lifetime uses and no longer
promise an active-spellspace check (no code changed), and src_architecture / src_components name no path into
the documentation tooling (both portability checks return nothing; indexes current). The graph's ConduitMeld
node is accepted against the source. The asset and bundle rebuild waived for this pass is covered by
workflows_0's 0.2.8206 rebuild; both checks OK. Follow-up for fable_0, not done here: the stale Meld and
Spellbook graph nodes.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
