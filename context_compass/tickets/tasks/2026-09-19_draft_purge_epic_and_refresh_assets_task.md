# Task: Record the purge epic and refresh existing Melder build assets

## Metadata
- Task ID: TASK-2026-09-19-draft-purge-epic-and-refresh-assets
- Epic: EPIC-2026-09-19-scope-aware-creation-purge
- Story: none; planning/build-only operation
- Status: review
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-20T00:53:18Z
- Updated: 2026-09-20T00:56:30Z

## Objective
Create the requested purge epic first, then regenerate and verify the existing Melder build assets.

## Ticket Contract
- ENTRY_GATE: Owner explicitly requested the epic and build regeneration; existing onboarding and
  certification remain valid, and the attention board routes this task.
- EXECUTION_BOUNDARY: New epic, coordination records, source/repository build-runner outputs and logs.
- DEPENDENCIES: Existing source asset runner and LLM bundle builder, already read in this session.
- EXIT_GATE: Epic records the scope rules and no-implementation boundary; both build/check paths succeed.
- FAILURE_ESCALATION: No purge code, API, feature tests, package version bump, release or unrelated changes.

## Scope Boundaries
- In scope: the requested planning record followed by deterministic existing-asset regeneration.
- Out of scope: implementing or deeply investigating purge, resolving its open design choices.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Epic created first; source/repository builders and all freshness checks passed.

## Steps / Checklist
- [x] Read the epic template and scoped creation/component vocabulary.
- [x] Create the purge epic with all five supplied rules and explicit unresolved lineage/root details.
- [x] Regenerate source assets, then repository LLM bundles through their existing runners.
- [x] Verify freshness, record results and leave implementation unstarted.

## Deliverables
- tickets/epics/2026-09-19_scope_aware_creation_purge_epic.md
- Build logs and matching generated assets for the unchanged current package version.

## Files / Paths Impacted
- The new epic/task, attention_board.md, artifact_board.md and mailbox_board.md.
- Existing outputs owned by src/melder/_build_assets/_build_asset_runner.py and llm_support/_builder.py.

## Validation
- Source runner regenerated agent documentation (452 entries), bind guard (629), and system documents (4).
- Repository builder verified src/tests/other fingerprints and outputs; all were already current.
- Both freshness check commands passed with exit 0 for the existing package version 0.2.43.
- Runtime tests: Not run; this pass changed planning records and regenerated existing assets only.

## Risks / Rollback Notes
- Preserve unrelated working-tree changes and never hand-edit generated assets.
- Existing no-implementation direction remains in force after the build completes.

## Applicable Anti-Patterns
- [x] No purge implementation or feature-completion claim.
- [x] No stale generated outputs or unexecuted check claim.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/purge_epic_assets_20260919/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: accepted task closure; preserve build evidence.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Noting Behavior
Record build outcomes and constraints here; feature decisions belong in the draft epic.

## Notes
- DATETIME: 2026-09-20T00:53:18Z
  TYPE: DECISION
  CLAIM: The epic is created before running the builders. It records the owner's five rules and
    additional unresolved lineage/root/multiplicity details without implementing any of them.
    Regenerate existing source assets and src/tests/other bundles at version 0.2.43.
  EVIDENCE:
  - tickets/epics/2026-09-19_scope_aware_creation_purge_epic.md:14-23
  - src/melder/__version__.py:12-12
  IMPACT: This task satisfies the requested sequence while leaving purge as a draft idea.
  NEXT: Run source asset regeneration, then the repository builder and both freshness checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T00:56:30Z
  TYPE: MEASURE
  CLAIM: Epic creation preceded asset regeneration. Source runner regenerated all three assets;
    repository runner found src/tests/other and its manifest already current. All source/repository
    checks passed at unchanged version 0.2.43. No purge implementation or runtime test changes.
  EVIDENCE:
  - artifacts/purge_epic_assets_20260919/build_source.log:1-3
  - artifacts/purge_epic_assets_20260919/build_llm.log:1-4
  - artifacts/purge_epic_assets_20260919/check_source.log:1-3
  - artifacts/purge_epic_assets_20260919/check_llm.log:1-3
  IMPACT: The requested planning/build pass is complete; the feature itself remains a draft idea.
  NEXT: Owner reviews the epic and directs any subsequent discovery or implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Purge epic drafted; no implementation. Both builders ran and all freshness checks passed using uv
--no-sync --offline in .venv_new. Existing package version is 0.2.43. The epic remains draft for owner
review; no purge runtime code, feature tests, release, commit or version change was introduced.
