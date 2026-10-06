

# Task: Audit the remaining system-document citations and stale counts

## Metadata
- Task ID: TASK-2026-10-01-audit-remaining-system-document-citations
- Story: none; follow-up of TASK-2026-09-29-promote-host-read-surface-into-system-docs
- Status: done
- Owner: user
- Agent Name: melder_0
- Priority: p3
- Created: 2026-10-01T10:46:11Z
- Updated: 2026-10-01T11:25:53Z

- Completed: 2026-10-01T11:25:53Z
- Summary: src_architecture and src_components: ten stale citations remapped, one range pair tightened in
  each, five suspects confirmed; the bind-guard count is 619 at 0.2.8215; the components' core set equals its
  Key Files union again (13 entries added). Assets rebuilt, both checks OK. No source change, no notch.

## Objective
The host read surface documentation pass (2026-10-01) remapped every numeric citation into aether.py and the 13 the
0.2.8208 insertions moved, and stopped there. Three known defects stay in src_architecture and src_components:
16 numeric citations into other files that a heuristic flags as suspect and nobody has read against source; the
src_components C1 core set no longer equals the union of its Key Files lists; and the bind-guard entry count the
documents quote (582) is not the manifest's (619 at 0.2.8215). This task reads each against source and fixes what
is wrong. Documentation only: no source change, no notch.

## Ticket Contract
- ENTRY_GATE: the owner schedules it; board row; preservation baselines of both documents and their indexes.
- EXECUTION_BOUNDARY: context_compass/system_docs src_architecture.md and src_components.md with their indexes;
  then build assets (rebuilt in the VM mirror and copied back, the device refuses deletes) and the LLM bundles.
- DEPENDENCIES: artifacts/host_read_surface_docs_20261001/citation_heuristic_audit.txt (the suspect list; its
  document line numbers are as of 2026-10-01T10:11Z and have moved since);
  tickets/tasks/completed/2026-09-29_promote_host_read_surface_into_system_docs_task.md (the pass that left these
  open).
- EXIT_GATE: each of the 16 citations read at its target and either confirmed or remapped to the symbol it names;
  the core-set drift resolved (entries added or Key Files corrected, each from source) or recorded with a reason;
  the bind-guard count matches the manifest or is restated without a number; indexes current; citation recipe,
  portability and preservation checks clean; assets and LLM bundles rebuilt with both checks OK.
- FAILURE_ESCALATION: CONFLICT when a document claim contradicts the source beyond its citation; DECISION_REQUEST
  before changing what a Key Files list names.

## Scope Boundaries
- In scope: the three defects above.
- Out of scope: source changes; citations outside these two documents; re-authoring sections.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: (2026-10-01T11:25:53Z) the owner turned it in (chat answer "Turn it in"), confirming the
  acceptance criteria.
- from_state: in_progress
- to_state: review
- transition_reason: (2026-10-01T11:10:12Z) the exit gate is met short of the owner's acceptance (MEASURE notes
  11:03Z-11:10Z): citations, core set and count fixed; indexes, assets and bundles current; both checks OK.
- from_state: draft
- to_state: in_progress
- transition_reason: (2026-10-01T10:54:10Z) the owner, told this task was the docs pass's follow-up, directed in chat
  "ok cool continue doing work and finish turning in your shit"; taken as scheduling it. Ticket out of the
  backlog and board row before any edit.
- from_state: draft
- to_state: draft
- transition_reason: Created parked (2026-10-01T10:46:11Z) from the host read surface documentation pass;
  awaits scheduling.

## Steps / Checklist
- [x] Re-capture preservation baselines.
- [x] Read the 16 suspect citations at their targets and remap or confirm each: mutation_research.py 220, 830-831,
      837-840, 845, 944-945, 3900 (`_emission_lock`, `on_mutation`); bind.py 404 (twice), 84-97, 946-956;
      spellbook.py 3686 (twice); spellbook_creation_system.py 1253-1292 and 616-723; crystallizer.py 1587-1594;
      spell_occurrence_graph_analyzer_strategy.py 1085-1127.
- [x] Resolve the src_components core-set drift (12 Key Files without a C1 entry, 19 C1 entries named by no Key
      Files list; recorded in the document's handoff on 2026-10-01).
- [x] Bind-guard count: src_architecture "582 at the current build" and "582-entry manifest", src_components the
      same two phrases; the manifest's ENTRY_COUNT is 619 (BUILT_FOR_VERSION 0.2.8215).
- [x] Indexes, checks, rebuild last.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Both documents' citations and counts verified against source; indexes, assets and bundles current.

## Files / Paths Impacted
- context_compass/system_docs/src_architecture.md, src_architecture_index.md
- context_compass/system_docs/src_components.md, src_components_index.md
- src/melder/_build_assets (regenerated), llm_support (regenerated)

## Validation
- Asset --check OK (VM mirror and device), LLM --check --include-untracked OK (device), 2026-10-01.
- VM mirror, GIL off: package-root, build_assets, agent-text reader and multithreaded document-view tests:
  299 passed, 24 skipped. Full suite: Not run (no src or test change). Coverage: Not run.
- Recommended commands:
  - the citation recipe in each document's Indexing section
  - python src/melder/_build_assets/_build_asset_runner.py --check
  - python llm_support/_builder.py --check --include-untracked

## Risks / Rollback Notes
- Until this runs, up to 16 citations may point a reader at the wrong code, and the packaged documents quote a
  bind-guard count 37 entries short.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.
- [x] No remap from a search hit: open the target and confirm the symbol is there.

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
  - artifacts/host_read_surface_docs_20261001/citation_heuristic_audit.txt
  - artifacts/system_doc_citation_audit_20261001/
- DISPOSITION: retain_as_reference
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
- DATETIME: 2026-10-01T10:46:11Z
  TYPE: DECISION
  CLAIM: Parked, not worked, by the scope the documentation pass set itself (its PLAN note): the 16 suspects were
    flagged by a heuristic only, and the core-set drift and the stale bind-guard count were found while checking
    other things. The count is a measured fact: the documents say 582, the manifest says 619.
  EVIDENCE:
  - context_compass/artifacts/host_read_surface_docs_20261001/citation_heuristic_audit.txt:1-27
  - context_compass/system_docs/src_architecture.md:534-535
  - context_compass/system_docs/src_architecture.md:555-555
  - context_compass/system_docs/src_components.md:5155-5155
  - context_compass/system_docs/src_components.md:5161-5161
  - src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py:16-19
  IMPACT: The open defects are recorded where the next documentation pass will find them.
  NEXT: Wait for the owner to schedule it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-01T11:03:55Z
  TYPE: MEASURE
  CLAIM: Entry gate met (baselines of both documents and indexes captured; the two authoring instructions, the
    four examples and the patch contract skills read; patch lane not triggered - no behaviour or boundary
    changes). Each of the 16 suspect citations was read at its target. Five hold: spellbook.py:3686 (twice;
    the comment in `_notch_spell` saying the Conduit admits the transaction), spellbook_creation_system.py:
    1253-1292 (`check_system_state`, exact), spell_occurrence_graph_analyzer_strategy.py:1085-1127
    (`_iter_spell_contract_defaults`, exact) and bind.py:946-956 (the class branch of `sha256_profile`, the
    sorted annotation keys at 953); the heuristic flagged names the claims mention but the ranges need not hold.
    Ten are stale: the `assert_allowed(spell, context="bind")` call is bind.py:657 in `Bind._bind_logic`, not
    404 (twice); `assert_allowed` is bind.py:62-106, not 84-97; crystallizer.py:1587-1594 now lands in
    `_custody_key_for` (0.2.8214) and `emit` is 1619-1671; the six mutation_research.py citations moved 43-56
    lines (263, 886-887, 893-896, 901, 1000-1001, 3956), each re-read for its claim (emission lock before
    root, the on_mutation wiring, the emitter called under both, the re-entry). One overruns:
    spellbook_creation_system.py:616-723 spans `_build_conjure_cache_state` and `_resolve_conjure_cache_path`
    (616-721) plus the next method's decorator, and its sibling 242-260 stops inside the
    `_enforce_conduit_resolution_valid` call (242-263); both pairs appear in both documents.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:62-106
  - src/melder/aether/spellbook/bind/bind.py:656-657
  - src/melder/aether/spellbook/bind/bind.py:942-956
  - src/melder/aether/spellbook/spellbook.py:3650-3699
  - src/melder/aether/spellbook/spellbook_creation_system.py:242-263
  - src/melder/aether/spellbook/spellbook_creation_system.py:616-723
  - src/melder/aether/spellbook/spellbook_creation_system.py:1253-1292
  - src/melder/crystallizer/crystallizer.py:1581-1671
  - src/melder/mutation_research/mutation_research.py:258-266
  - src/melder/mutation_research/mutation_research.py:880-902
  - src/melder/mutation_research/mutation_research.py:994-1025
  - src/melder/mutation_research/mutation_research.py:3930-3960
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1084-1127
  - context_compass/artifacts/system_doc_citation_audit_20261001/baseline_manifest.txt:1-5
  IMPACT: Ten citations remap and one pair tightens in each document; no claim text changes but the call-site
    history line.
  NEXT: Measure the core set and the bind-guard count.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-01T11:03:55Z
  TYPE: MEASURE
  CLAIM: The core set drifted one way only, not two. Read as the document's own invariant states it - the union
    of every Key Files list, C3 and C2, the reading that measured 201 = 201 on 2026-08-02 - all 214 core
    entries are named by a component, and 13 named files have no entry (12 from C3 lists, general_helpers.py
    from a C2 list). The earlier "19 entries no Key Files list names" came from a parser that stopped the
    Crystallizer entry's Key Files list at the prose bullet inside it, missing the eleven crystal modules
    listed after it. So the fix is additive - 13 measured entries - and changes no Key Files list, which needs
    no decision. Bind-guard count: both documents say 582, twice each; the manifest holds 619 (ENTRY_COUNT,
    BUILT_FOR_VERSION 0.2.8215), which the loader re-exports as MANIFEST_ENTRY_COUNT. The neighbouring "seven
    sites" claim holds: test_bind.py patches `bind.assert_allowed` in its autouse fixture and six tests, all
    raising=True (the fixture's own comment says 577 - a test comment, outside this lane).
  EVIDENCE:
  - context_compass/artifacts/system_doc_citation_audit_20261001/runs/core_set_drift_before.log:1-14
  - context_compass/artifacts/system_doc_citation_audit_20261001/apply/core_set_drift.py:1-143
  - context_compass/system_docs/src_components.md:1645-1683
  - context_compass/system_docs/src_components.md:8164-8181
  - src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py:16-19
  - src/melder/_build_assets/_bind_guard/bind_guard.py:93-96
  - tests/unit/melder/spellbook/bind/test_bind.py:114-128
  IMPACT: Every defect the task named is measured and none needs the owner's decision.
  NEXT: PLAN note, then apply.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-01T11:03:55Z
  TYPE: PLAN
  CLAIM: One apply script per document (artifacts/system_doc_citation_audit_20261001/apply/); every anchor must
    match once and nothing is written otherwise; lines stay within 120. (1) src_architecture: bind.py:404 ->
    657; 242-260 -> 242-263 and 616-723 -> 616-721 in the conjure sequence; "582" -> 619 at 0.2.8215 (two
    places); Updated; a handoff paragraph. (2) src_components: bind.py:84-97 -> 62-106; bind.py:404 -> 657
    and its history parenthetical; crystallizer.py:1587-1594 -> 1619-1671; the six mutation_research.py
    citations and the ":830 then :831, and :944 then :945" prose; 242-260 -> 242-263 and 616-723 -> 616-721;
    "582" -> 619 (two places); 13 measured core entries appended before the full inventory; the 2026-10-01
    handoff sentence corrected (13 and 0); a handoff paragraph; Updated. (3) Indexes, the citation recipe,
    portability, preservation, the graph join and the core-set script (equal sets). (4) Assets rebuilt in the
    VM mirror and copied back, LLM bundles checked; both checks OK. (5) Review. Docs only, no notch.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-01_audit_remaining_system_document_citations_task.md:23-35
  - context_compass/artifacts/system_doc_citation_audit_20261001/runs/core_set_drift_before.log:1-14
  IMPACT: The pass is bounded to the 16 citations, their four sibling ranges, the core set and one count.
  NEXT: Apply src_architecture.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-01T11:08:05Z
  TYPE: MEASURE
  CLAIM: Applied (three scripts, every anchor matched once). src_architecture: the call site 657, the conjure
    evidence 242-263 and 616-721, the count 619 at 0.2.8215 (two places), the manifest's C1 extent 641 (it was
    the only stale extent of 149), a handoff paragraph. src_components: 62-106, 657 with its history line,
    1619-1671, the six MutationResearch citations and their prose, 242-263 and 616-721, 619 (two places), the
    manifest extent 641 (the only stale extent of 214), 13 measured core entries, the earlier handoff sentence
    corrected, a handoff paragraph. Checks on the files as written: the core set equals the Key Files union
    (227 = 227); the citation recipe finds nothing (a first run flagged my own bare `bind.py:657` and
    `spellbook.py:3686` in the new handoff lines - rewritten with full paths); no tooling or absolute path; 149
    and 227 cited source paths resolve in the graph index; every baseline line survives except the 9 and 20
    lines deliberately replaced; each new citation's first line is the code it names; both indexes current
    (3495 and 10548 lines). Rubric: not re-scored - it needs a whole re-read from disk and the pass added 16
    and 110 lines; the standing record is src_architecture 75 (B), src_components unscored.
  EVIDENCE:
  - context_compass/artifacts/system_doc_citation_audit_20261001/runs/checks.log:1-54
  - context_compass/artifacts/system_doc_citation_audit_20261001/runs/core_set_drift_after.log:1-1
  - context_compass/artifacts/system_doc_citation_audit_20261001/apply/apply_docs_architecture.py:1-79
  - context_compass/artifacts/system_doc_citation_audit_20261001/apply/apply_docs_components.py:1-160
  - context_compass/artifacts/system_doc_citation_audit_20261001/apply/apply_handoff_paths.py:1-76
  - context_compass/system_docs/src_architecture.md:3177-3183
  - context_compass/system_docs/src_components.md:10167-10175
  IMPACT: The three defects the task named are fixed in the documents; only the rebuild remains.
  NEXT: Copy the two documents and indexes into the VM mirror, rebuild assets there, copy back, both checks.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-01T11:10:12Z
  TYPE: MEASURE
  CLAIM: Rebuild, last. The two documents and indexes were the only asset inputs that differed; copied into the
    VM mirror, the runner wrote the three manifests at v0.2.8215 (bind guard 619 entries) and its --check is OK.
    The copy-back wrote 4 of 8 generated files to the device, CRLF (the system documents index and manifest, the
    architecture and components payloads); the other four were already the intended bytes. The device's asset
    --check is OK for all three, and each device payload embeds its document byte for byte (3495, 10548 and
    27573 lines). The LLM builder reports every corpus unchanged (context_compass is outside its corpora) and its
    --check is OK. No .git/index.lock, no temporary file. In the mirror the package-root, build_assets,
    agent-text reader and multithreaded document-view tests pass with the GIL off: 299 passed, 24 skipped.
    Coverage: Not run.
  EVIDENCE:
  - context_compass/artifacts/system_doc_citation_audit_20261001/runs/compare_asset_inputs_sync.log:1-10
  - context_compass/artifacts/system_doc_citation_audit_20261001/runs/rebuild_assets_vm.log:1-3
  - context_compass/artifacts/system_doc_citation_audit_20261001/runs/copy_back_assets.log:1-9
  - context_compass/artifacts/system_doc_citation_audit_20261001/runs/check_assets_device.log:1-3
  - context_compass/artifacts/system_doc_citation_audit_20261001/runs/device_payload_roundtrip.log:1-3
  - context_compass/artifacts/system_doc_citation_audit_20261001/runs/rebuild_llm_device.log:1-4
  - context_compass/artifacts/system_doc_citation_audit_20261001/runs/check_llm_device.log:1-3
  - context_compass/artifacts/system_doc_citation_audit_20261001/runs/post_rebuild_package_root_vm.log:1-6
  IMPACT: The exit gate is met short of the owner's acceptance.
  NEXT: Move to review and report to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-01T11:25:53Z
  TYPE: DECISION
  CLAIM: The owner turned the task in (chat, asked "Turn the audit in too?", answered "Turn it in"), confirming the
    acceptance criteria, and picked the MelderOps threading-findings task next. Closure: the ticket moves to
    completed, its board row becomes a closed anchor, both artifact rows move to cleared (retained), and melder_0
    releases its claims on src_architecture, src_components and their indexes.
  EVIDENCE:
  - context_compass/artifact_board.md:88-89
  IMPACT: This lane is closed; nothing of it stays open.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Turned in 2026-10-01T11:25:53Z (owner). Sixteen suspect citations read at their targets: ten stale ones remapped
(one in src_architecture, nine in src_components), one range pair tightened in each, five confirmed. The
bind-guard count is 619 at 0.2.8215 and the manifest's code-map extent 641; the core set equals the Key Files
union again (13 measured entries added; the earlier '19 unclaimed entries' was a parser artifact). Indexes,
assets and bundles current, both checks OK. No src change, no notch. Next: the owner's turn-in.
Scheduled 2026-10-01T10:54:10Z (owner direction; see the transition).
Parked 2026-10-01T10:46:11Z. Start with the baselines, then the 16 citations (read each target),
then the core set and the count.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
