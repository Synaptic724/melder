

# Task: Organize the 0.2.82 release, close the IR epic, and rebuild the build assets and LLM bundles

## Metadata
- Task ID: TASK-2026-09-27-organize-release-0-2-82-and-rebuild-assets
- Story: none (owner-directed release and closure pass)
- Status: done
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-27T18:34:24Z
- Updated: 2026-09-27T18:43:57Z
- Completed: 2026-09-27T18:43:57Z
- Summary: 0.2.82 release note written fresh in release_docs/next_version_release.md (owner: "looks fine, it's a
  short release"); 0.2.77.md restored to its cut state; the comptime IR epic closed and synced. The build assets
  and LLM bundles are rebuilt as the owner-ordered final step after this closure; results are reported in chat
  and appended below as a post-closure record.

## Objective
Owner directive (2026-09-27T18:34:24Z): "rebuild the build assets in melder ... organize a new release for melder
... based on
the new epics that were completed today specifically ... close your epic close your tasks then rebuild the assets;
you do not need to ask me for approval to close your own tickets". Deliver: the running release note finalized as
the 0.2.82 release (the owner pre-notched `__version__` to 0.2.82 at 18:25Z), the comptime IR phase-pipeline epic
closed, the generated build assets and LLM bundles rebuilt and checked at 0.2.82, and this task closed.

## Ticket Contract
- ENTRY_GATE: this row on `attention_board.md`; the survey note below.
- EXECUTION_BOUNDARY: `release_docs/` (rename and finalize the running note), the generated assets under
  `src/melder/_build_assets/` and `llm_support/` through their builders only, the IR epic ticket and the boards.
  No hand edit of a generated manifest; no src code change; no `__version__` change (the owner set it).
- DEPENDENCIES: docs/maintaining.md (the two generated-asset checks); the five epics completed 2026-09-27;
  melder_0's 0.2.80/0.2.81 notes in release_docs (already in the running note).
- EXIT_GATE: release note at 0.2.82 with no "Unreleased" marker; epic in completed/; both `--check` commands OK
  at 0.2.82; asset-currency tests green on the VM's 3.14t against the device tree; boards synced.
- FAILURE_ESCALATION: BLOCKER if a builder fails or the VM interpreter cannot import melder; RAISE if the
  rebuild changes anything besides version stamps and fingerprints.

## Scope Boundaries
- In scope: release-note finalization, epic closure, asset and bundle rebuild, checks, board sync.
- Out of scope: new release content, code changes, publishing (tag, wheel, PyPI) - owner-owned.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner directive received and survey complete (2026-09-27T18:34:24Z).
- from_state: in_progress
- to_state: done
- transition_reason: Release note accepted by the owner in chat; epic closed; owner ordered the rebuild to be
  the last step, after the ticket turn-in (2026-09-27T18:43:57Z).

## Steps / Checklist
- [x] R1: survey - version state, release-note state, epic coverage, asset commands (notes below).
- [x] R2 (as corrected by the owner): brand-new `release_docs/next_version_release.md` for 0.2.82 built from the
  sections appended to 0.2.77.md after its cut; 0.2.77.md restored to its cut state; the rename undone.
- [x] R3: close tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md (summary, move, anchors, artifact row).
- [x] R5: close this task; board sync (ordered before R4 by the owner: "make sure rebuilding is the last step").
- [x] R4: rebuild build assets and LLM bundles; `--check` both; asset-currency tests on the VM 3.14t - ran after
  this closure as the final step; result recorded in the post-closure note below.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `release_docs/0.2.82.md`; rebuilt assets and bundles at 0.2.82; the IR epic in completed/.

## Files / Paths Impacted
- release_docs/next_version_release.md (new 0.2.82 note); release_docs/0.2.77.md (restored to commit 2fc783045)
- src/melder/_build_assets/** and llm_support/** (generated, through their builders)
- context_compass/tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md -> tickets/epics/completed/
- context_compass/attention_board.md, artifact_board.md, mailbox_board.md

## Validation
- At closure: Not run. The asset check on the pre-rebuild tree reported all three assets STALE (expected v0.2.82),
  which is the state the rebuild resolves.
- The rebuild, both `--check` commands and the asset-currency tests run after this closure as the owner-ordered
  final step (VM venv CPython 3.14.7t, `PYTHONPATH=src` against the device tree); results in the post-closure note.
- Commands:
  - `python src/melder/_build_assets/_build_asset_runner.py` then `--check`
  - `python llm_support/_builder.py` then `--check`
  - `pytest -q tests/unit/melder/build_assets tests/unit/melder/test_package_version_metadata.py
    tests/unit/llm_support/test_builder.py tests/unit/melder/test_system_documents.py`

## Risks / Rollback Notes
- The rebuild only restamps generated files; rollback is `git checkout` of the generated paths by the owner.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion (owner pre-approved closure).

## Done Checklist
- [x] Steps complete and checked off (R4 deliberately follows closure by owner order)
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed) - the release note
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed (release note accepted in chat; closure pre-approved)
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: release notes; generated build assets; LLM bundles.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-27T18:34:24Z
  TYPE: FACT
  CLAIM: Survey. `__version__` reads 0.2.82 on the tree (file modified 18:25Z; the only file under src/tests/
    release_docs/docs/llm_support/benchmarks changed since the 0.2.81 commit 332aabf98 at 14:54Z), so the owner
    set the release version himself. The running note `release_docs/0.2.77.md` (664 lines, equal to HEAD) is
    headed "Melder 0.2.81 / **Unreleased**" and already carries the two code epics completed today - the Aether
    lookup API (its own section) and the Sphinx publication work (Packaging and documentation) - plus every
    0.2.78-0.2.81 change; its last bullet says assets and bundles were rebuilt for 0.2.81. The three UX/AIX
    epics closed today add no release content: their lesson collections last changed in git on 2026-09-20 and
    2026-09-23, before the 0.2.50 cut. docs/maintaining.md names the two generated-asset checks; melder_0's
    0.2.80 task records that the bundle check needs `--include-untracked` on a tree with uncommitted files.
  EVIDENCE:
  - docs/maintaining.md:187-196
  - release_docs/0.2.77.md:1-3
  - release_docs/0.2.77.md:619-664
  - tickets/tasks/2026-09-27_aggregate_creations_disposal_method_failures_task.md:71-72
  IMPACT: The release is a finalization at 0.2.82, not new content; the rebuild restamps the assets to 0.2.82.
  NEXT: R2 - finalize the note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T18:34:24Z
  TYPE: FACT
  CLAIM: Mailbox M0-59 (melder_0, 2026-09-27T13:25:25Z) consumed, no ACK requested: Creations now runs every
    declared disposal method after one raises and reports one RuntimeError per failure inside the existing
    ExceptionGroup; landed at 0.2.80 with docs, assets and bundles. Nothing for this lane beyond the release note,
    which already carries its section ("Disposal runs every method and reports every failure").
  EVIDENCE:
  - tickets/tasks/2026-09-27_aggregate_creations_disposal_method_failures_task.md
  - release_docs/0.2.77.md:68-83
  IMPACT: No action; recorded for the durable trace.
  NEXT: R2.
  REREAD: OPTIONAL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-27T18:35:49Z
  TYPE: FACT
  CLAIM: R2 done. `release_docs/0.2.77.md` is now `release_docs/0.2.82.md` (mv -n); its header reads
    "# Melder 0.2.82" and the "**Unreleased**" marker is replaced by a seven-line introduction naming the
    headline changes and the two breaking renames, in the 0.2.50 style. The file is CRLF and was edited with
    its endings preserved. Slip recorded: the first edit script aborted on a CRLF guard while the rename in the
    same shell line still ran, so the file was briefly renamed with the old header; the header edit was redone
    on the renamed file. No other content changed; the last packaging bullet still says 0.2.81 until R4.
  EVIDENCE:
  - release_docs/0.2.82.md:1-9
  - release_docs/0.2.82.md:670-670
  IMPACT: The release note is final except for the rebuild stamp line.
  NEXT: R3 - close the IR epic.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T18:39:59Z
  TYPE: DECISION
  CLAIM: Owner correction ("you should be making a brand new release in release_docs/next_version_release.md not
    reusing the old 77"). Undone: the rename and header edit (0.2.82.md deleted with delete permission granted
    for it). Findings that settle the organization: git tags stop at 0.2.50; 0.2.77.md was created by the
    owner's commit 2fc783045 ("Bump version to 0.2.78", 601 lines, header "Melder 0.2.78 / Unreleased") and
    only two later commits (79eaef22a at 0.2.79, 332aabf98 at 0.2.81) appended to it: the Aether lookup section,
    the disposal-aggregation section, the README roadmap bullet, the lookup/disposal clauses of the packaged
    system-documents bullet and the rebuild stamp (diff: +60/-5 lines). Done: 0.2.77.md restored to the cut
    state (content of 2fc783045, CRLF); next_version_release.md written as the 0.2.82 note - intro, those two
    sections verbatim, a Packaging and documentation section with the README bullet, the regenerated packaged
    documents and the 0.2.82 rebuild line (true once R4 lands). The three UX/AIX epics still add no content.
  EVIDENCE:
  - release_docs/next_version_release.md:1-75
  - release_docs/0.2.77.md:1-3
  IMPACT: 0.2.77.md is the previous release as committed; the new release has its own note; no duplication.
  NEXT: R3 - move the closed IR epic and sync the boards.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T18:43:57Z
  TYPE: FACT
  CLAIM: R3 done and this task closed. The comptime IR epic is in tickets/epics/completed/ with a closure summary
    (M1, plan, T1, I-1 delivered; six IR-port stories retired unopened), a closed anchor on attention_board.md
    (oldest anchor dropped to hold the cap) and its gauntlet-baseline artifact row moved to cleared
    (retain_as_reference). Owner in chat: the release note "looks fine, it's a short release"; turn in the tickets
    and rebuild last. Rebuild environment verified: the VM venv (CPython 3.14.7t, GIL disabled) imports melder
    0.2.82 from the device tree with `PYTHONPATH=src`; the asset runner lists three builders and its `--check`
    reports all three STALE at v0.2.82; the bundle builder excludes context_compass (4518 files), so a note
    appended here after the rebuild cannot stale the bundles.
  EVIDENCE:
  - tickets/epics/completed/2026-08-03_comptime_ir_phase_pipeline_epic.md
  - artifact_board.md (search `ir_epic_gauntlet_baseline_20260925`)
  IMPACT: Everything but the rebuild is turned in; the rebuild is the final step.
  NEXT: R4 - rebuild, check, test; append the result below.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T18:47:25Z
  TYPE: MEASURE
  CLAIM: Post-closure record of the owner-ordered final step (the only write after the rebuild is this note; the
    bundles exclude context_compass). Build assets rebuilt on the device tree with the VM venv (CPython 3.14.7t,
    GIL disabled, `PYTHONPATH=src`): `_agent_documentation` 460 entries, `_bind_guard` 619 entries (unchanged
    count), `_system_documents` 4 entries, all v0.2.82; `--check` reports all three current (schema 2.0.0, key
    match). LLM bundles rebuilt: src 576 files, tests 1021, other 378, manifest.json; `--check` OK for all three
    corpora (no `--include-untracked` needed: the only tracked changes are `__version__.py` and release_docs).
    Tests on the rebuilt tree (`-X gil=0`, `-p no:cacheprovider`): tests/unit/melder/build_assets +
    test_package_version_metadata.py + test_system_documents.py 144 passed, 1 skipped; tests/unit/llm_support/
    test_builder.py + tests/unit/github_workflows/test_distributions.py 54 passed. Files written by the rebuild:
    the three manifests, graph_adjacency_manifest.py, system_documents_index.py and the three payload modules
    under src/melder/_build_assets/, plus the three bundles, their indexes and manifest.json under llm_support/.
  EVIDENCE:
  - src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py:1-20
  - llm_support/manifest.json
  IMPACT: The 0.2.82 tree is consistent: version, release note, assets and bundles agree; the owner commits.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
STATE 2026-09-27T18:34:24Z: IN_PROGRESS. Survey done; finalizing the release note at 0.2.82, then the IR epic
closure, then the asset and bundle rebuild, then closure of this task.
STATE 2026-09-27T18:43:57Z: DONE. Release note accepted, epic closed, boards synced; the rebuild follows as the
owner-ordered final step and its result is appended below.
STATE 2026-09-27T18:47:25Z: DONE (post-closure record). Assets and bundles rebuilt and checked at 0.2.82;
198 tests green.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
