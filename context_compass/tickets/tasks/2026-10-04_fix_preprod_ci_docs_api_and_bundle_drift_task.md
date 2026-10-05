# Task: Make the dev-to-preprod CI green: docs API selection and llm_support bundle drift

## Metadata
- Task ID: TASK-2026-10-04-fix_preprod_ci_docs_api_and_bundle_drift
- Story: none (standalone task; owner request)
- Status: review
- Owner: claude
- Agent Name: melder_1
- Priority: p1
- Created: 2026-10-04T18:55:59Z
- Updated: 2026-10-04T20:09:37Z

## Objective
Fix the two checks that failed on the owner's dev-to-preprod push: the docs tests (public API selection
drift on SpellframeKind) and `llm_support/_builder.py --check` (STALE other).

## Ticket Contract
- ENTRY_GATE: the owner's chat directive of 2026-10-04 ("go fix all that"). Active board row:
  preprod_ci_docs_and_bundles.
- EXECUTION_BOUNDARY: docs/api.toml, release_docs/next_version_release.md, src/melder/__init__.py and
  __version__.py (owner redirect, Note 5), two tests, regenerated assets, graph and llm_support bundles.
  No commit, push or PR; the owner commits.
- DEPENDENCIES: the owner must commit the four uncommitted ignore-file changes (Note 2).
- EXIT_GATE: docs tests and build_docs.py check pass here; llm_support --check prints only OK as the
  last step; the owner pushes and accepts.
- FAILURE_ESCALATION: Record BLOCKER if the docs tests cannot run here.

## Scope Boundaries
- In scope: the two failing checks.
- Out of scope: Python version policy for CI (discussed with the owner next), other workflow changes.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: (2026-10-04T20:09:37Z) redirect applied and validated (Notes 6-7); owner commits and pushes.

## Steps / Checklist
- [x] Diagnose both failures (Notes 1-2).
- [x] Add SpellframeKind to docs/api.toml and the release-note bullet.
- [x] Run the docs tests and build_docs.py check.
- [x] Owner redirect (Note 5): take SpellframeKind off the root; revert the api.toml entry and the bullet;
      guard it in the curated-exclusions test; notch 0.2.8225.
- [x] Rebuild assets, graph and llm_support last and run every --check (llm_support result in chat).

## Deliverables
- docs/api.toml with SpellframeKind selected; release-note bullet; rebuilt llm_support bundles.

## Files / Paths Impacted
- docs/api.toml
- release_docs/next_version_release.md
- llm_support/ (regenerated)

## Validation
- Unit tier, docs tests, docs check, asset check: Note 7. llm_support rebuild and --check: last step, reported in chat.

## Risks / Rollback Notes
- Risk: the bundles go stale again if anything is edited after the rebuild. Mitigation: the rebuild is
  the last write of this pass and its result is reported in chat, not written back here.
- Rollback: remove the api.toml entry; rebuild the bundles.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

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
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: not applicable (no artifacts planned)

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
- DATETIME: 2026-10-04T18:55:59Z
  TYPE: FACT
  CLAIM: The docs build requires docs/api.toml groups to select every name in melder's `__all__`
    exactly once, and refuses otherwise. SpellframeKind is imported and listed in `__all__` (since
    0.2.8222) but no group selects it, so builder.load() raises "Public API selection drift:
    missing=['SpellframeKind']", which is the owner's two CI errors.
  EVIDENCE:
  - docs/tools/api_reference.py:36-40
  - src/melder/__init__.py:90-90
  - src/melder/__init__.py:249-249
  - docs/api.toml:4-8
  IMPACT: One selection entry fixes both docs errors; the binding group fits, since the kind is what
    a binding records.
  NEXT: Record the bundle finding.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T18:55:59Z
  TYPE: FACT
  CLAIM: `llm_support/_builder.py --check` prints OK for src, tests and other on the working tree,
    while CI reported other STALE on the pushed commit. Ignoring line endings, only four files differ
    from HEAD: the root .gitignore (the `.meldercache` lines and the persistent-gauntlet results line
    were never committed; its last commit is 2026-09-05) and three `.gitignore` files under
    context_compass/artifacts/ deleted on disk but still committed.
  EVIDENCE:
  - .gitignore:206-209
  - .gitignore:232-232
  IMPACT: The bundles describe the disk, CI describes the commit. Committing those four changes (with
    the rebuilt bundles) makes them agree; an agent cannot commit here, so it is owner-owed.
  NEXT: Record the decision and plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T18:55:59Z
  TYPE: PLAN
  CLAIM: The owner's directive is the confirmation. Add SpellframeKind after Spell in the binding
    group; add one Packaging-and-documentation bullet and align the release note with __version__
    0.2.8224; no src change, so no notch. Run the docs tests and build_docs.py check (their temp
    folders need delete permission in the repo), then mark this ticket for review, and LAST rebuild
    llm_support and run --check, reporting that result in chat so nothing is written after it.
  EVIDENCE:
  - docs/api.toml:4-8
  - .github/workflows/docs.yml:30-33
  IMPACT: After the owner commits everything and pushes, both failing checks should pass.
  NEXT: Edit docs/api.toml.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T19:44:11Z
  TYPE: MEASURE
  CLAIM: SpellframeKind is selected in the binding group; the release note names 0.2.8224 and lists the
    docs change. Device VM, CPython 3.14.7 (GIL build) with docs/requirements.txt: `python -m unittest
    discover -s docs/tests -q` ran 60 tests OK, and `python docs/tools/build_docs.py check` exited 0.
  EVIDENCE:
  - docs/api.toml:8-8
  - docs/tools/api_reference.py:36-40
  IMPACT: The two docs CI errors are fixed. The remaining step is the llm_support rebuild and --check,
    which runs after this note as the last write; its result is reported to the owner in chat.
  NEXT: Owner commits everything (including the four ignore-file changes) and pushes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T19:53:36Z
  TYPE: DECISION
  CLAIM: Owner redirect (chat, 2026-10-04): SpellframeKind was never meant to be public. Bind already sets
    it on every Spell from the spellframe it was given (string -> category, Protocol -> contract, none ->
    none) and no bind signature takes a kind; only the package-root export (commit 15ee1e692, 0.2.8222)
    was wrong. So: remove it from melder's import and `__all__`, revert the api.toml entry and the
    release-note bullet, guard it in the curated-exclusions test, notch 0.2.8225. The system docs never
    claimed a root export, so no system-doc edit or patch lane is needed (a public-surface curation like
    the 2026-08 SpellExaminer, Scan and ConduitCloud rulings).
  EVIDENCE:
  - src/melder/__init__.py:90-90
  - src/melder/__init__.py:249-249
  - src/melder/aether/spellbook/spellframe_kind/spellframe_kind.py:36-37
  - tests/unit/melder/test_package_public_surface.py:234-292
  IMPACT: The docs drift error disappears because the export is gone, not because it is documented.
  NEXT: Apply the edits, run the tests, rebuild last.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T19:53:36Z
  TYPE: FACT
  CLAIM: Applied: SpellframeKind is no longer imported into melder or listed in `__all__`; the api.toml
    entry and the release-note bullet are reverted and the 0.2.8222 paragraph no longer says it is
    exported; the enum's test now asserts it is not a root export and the curated-exclusions test lists
    it; version 0.2.8225 with a board notch notice.
  EVIDENCE:
  - tests/unit/melder/spellbook/spellframe_kind/test_spellframe_kind.py:21-27
  - tests/unit/melder/test_package_public_surface.py:290-294
  - src/melder/__version__.py:12-12
  IMPACT: Bind behaviour and `spell.spellframe_kind` are unchanged; only the public name is gone.
  NEXT: Run the unit tier and the docs tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T20:09:37Z
  TYPE: MEASURE
  CLAIM: Device VM, CPython 3.14.7t (tests) and 3.14.7 with docs/requirements.txt (docs). Graph refreshed
    (587 ranges verified); the asset runner wrote all three assets at v0.2.8225 and --check prints only
    OK. tests/unit outside melder/: 522 passed; tests/unit/melder in three shards: 1418, 4556 and 2425
    passed, 3 failed only because the VM reused Windows-compiled bytecode (their paths point at C:\),
    and that file passes 46/46 with a Linux-only bytecode cache. The export, spellframe, version, hosted
    accessor and restore tests: 33 passed. Docs: 60 tests OK, build_docs.py check OK (301 pages).
  EVIDENCE:
  - tests/unit/melder/test_package_public_surface.py:290-294
  - src/melder/__version__.py:12-12
  IMPACT: Ready for the owner's commit. The llm_support rebuild and --check run after this note as the
    last write; their result goes to the owner in chat.
  NEXT: Owner commits everything, including the four ignore-file changes, and pushes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
SpellframeKind is off the public surface (owner ruling) and the docs check passes again; version 0.2.8225;
assets, graph and bundles rebuilt last. Owner-owed: commit everything, including the root .gitignore and the
three deleted artifact .gitignore files, then push.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
