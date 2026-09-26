

# Task: Bump the version for unresolved inputs, rebuild the build assets and complete the release note

## Metadata
- Completed: 2026-09-26T08:53:38Z
- Closure Basis: owner direction ("finish off the last few steps and you can build asset runs update the version number and add details to the release").
- Summary: __version__ and the release header read 0.2.54; all three build assets and the LLM bundles regenerated
  and checked; release note carries the unresolved-input details, upgrading notes and packaging.
- Task ID: TASK-2026-09-26-bump-version-rebuild-assets-for-unresolved-inputs
- Story: STORY-2026-09-26-unresolved-input-sockets (step 6 of the patch rollout plus release hygiene)
- Status: done
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-26T08:43:05Z
- Updated: 2026-09-26T08:53:38Z

## Objective
Advance `__version__` one notch (0.2.53 -> 0.2.54) for the unresolved-input change, run the build-asset
runners so the internal-registration manifest, agent documentation and packaged system documents match
the source and docs, and make the next-release note name the version and carry the release details.

## Ticket Contract
- ENTRY_GATE: Owner direction 2026-09-26 ("finish off the last few steps and you can build asset runs
  update the version number and add details to the release").
- EXECUTION_BOUNDARY: `src/melder/__version__.py` (literal only), the files the build-asset runner and
  the LLM support builder generate, and `release_docs/next_version_release.md`. No hand edits to
  generated files, no other src/tests edits, no commit, tag or publish.
- DEPENDENCIES: tickets/tasks/2026-09-26_implement_missing_dependency_sockets_task.md (steps 1-5 done).
- EXIT_GATE: Version and header read 0.2.54; runner --check passes; asset and version tests recorded.
- FAILURE_ESCALATION: BLOCKER if a builder fails; DECISION_REQUEST if a concurrent lane's in-flight src
  change would be baked into the assets.

## Scope Boundaries
- In scope: the version literal, the three runner-owned assets, LLM support bundles, the release note.
- Out of scope: commits, tags, publication; unrelated lanes' source changes.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner directed the bump, the asset runs and the release details, 2026-09-26T08:43:05Z.
- from_state: in_progress
- to_state: done
- transition_reason: Version, assets and release note current with checks passing; owner directed completion (2026-09-26T08:53:38Z).

## Steps / Checklist
- [x] Notify melder_1 (active src lane) before regenerating assets.
- [x] Set `__version__ = "0.2.54"` (CRLF kept) and the release-note header.
- [x] Run the build-asset runner, then --check.
- [x] Run the LLM support builder, then --check.
- [x] Run asset, version and document tests on 3.14t.
- [x] Add release details (packaging and asset status).

## Deliverables
- `src/melder/__version__.py` at 0.2.54; regenerated assets; release note headed 0.2.54.

## Files / Paths Impacted
- src/melder/__version__.py
- src/melder/_build_assets/**/manifest/*, src/melder/_build_assets/_system_documents/payloads/*
- llm_support/llm_full_*.txt, llm_support/*_index.md, llm_support/manifest.json
- release_docs/next_version_release.md

## Validation
- 3.14t unit suite and both --check gates: see the MEASURE note.

## Risks / Rollback Notes
- Every persisted creation cache cold-resets once under the new release (by design).
- Rollback: restore the literal and rerun the runner.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No hand edit of a generated asset.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/missing_dependency_sockets_20260926/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Owner decision at closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - Version literal, build-asset stamps, release note.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.

## Notes
- DATETIME: 2026-09-26T08:43:05Z
  TYPE: FACT
  CLAIM: Starting state: `__version__` 0.2.53, release header 0.2.53 (Unreleased). The runner discovers three
    builders (_agent_documentation, _bind_guard, _system_documents) and --check reports all three STALE
    ("source key or version moved", expected v0.2.53). The owner committed the unresolved-input work in
    f1cd22a22; a later docstring correction in unresolved_input_error.py is uncommitted. melder_1 holds an
    active src lane (inspect.signature NameError) that may touch many modules.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - src/melder/_build_assets/_build_asset_runner.py:246-362
  - attention_board.md:111-111
  IMPACT: The assets capture current source; melder_1 must rerun the runner if their fix lands after this.
  NEXT: Notify melder_1, then bump the version.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T08:53:07Z
  TYPE: MEASURE
  CLAIM: Done. `__version__` and the release header read 0.2.54 (CRLF kept). The asset runner rewrote all three
    assets at 0.2.54 (agent documentation 453 entries, bind guard 632 incl. UnresolvedInputError, system
    documents 4 records incl. the promoted docs); --check: all three OK (key match). The system-documents
    builder deletes its payload files before rewriting, which the mount refused; the owner's device granted
    delete permission for this session and the rerun succeeded. The LLM builder hit one transient
    Permission denied on os.replace, succeeded on rerun, was rerun after the release-note edits, and --check
    passes for src/tests/other. Unit suite on 3.14t (VM copy synced from the repo): 8038 passed, 20 failed =
    18 architecture-docs-tool + 2 system-documents-builder baseline failures (those two need the repo's
    context_compass/ tree, absent from the VM copy); the asset-stamp test that failed at 0.2.53 now passes.
    Release claims probed: Optional[T] without default -> UnresolvedInputError, None supplies it; binding
    UnresolvedInputError raises InternalRegistrationError; version reads 0.2.54.
    Release note gained Defaults/collections, "every missing input is named", an Upgrading subsection and a
    Packaging and documentation section.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py:615-615
  - release_docs/next_version_release.md:1-67
  - artifacts/missing_dependency_sockets_20260926/probe_commandops_shapes.py:1-39
  IMPACT: Version, assets and release note are current; melder_1 was told to rerun the runner if their src
    fix lands later (M0-14).
  NEXT: Closure sync (owner directed completion).
  REREAD: HELPFUL
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T08:53:07Z
  TYPE: DECISION
  CLAIM: Owner directed completion ("finish off the last few steps and you can build asset runs update the
    version number and add details to the release"); this task closes with the implementation task and story.
  EVIDENCE: tickets/tasks/2026-09-26_implement_missing_dependency_sockets_task.md
  IMPACT: Move to completed and run board sync.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Owner-directed release hygiene after the unresolved-input work: version 0.2.54, asset rebuild, release note.
Done and closed; see the MEASURE note. If melder_1's inspect.signature fix changes src afterwards, rerun
`python src/melder/_build_assets/_build_asset_runner.py` and the LLM support builder.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
