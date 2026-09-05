# Task: Document ordered disposal and regenerate derived assets

## Metadata
- Task ID: TASK-2026-09-04-ordered-disposal-docs-assets
- Story: STORY-2026-09-04-ordered-disposal-persistence
- Story Ticket: `tickets/stories/2026-09-04_ordered_disposal_persistence_story.md`
- Epic Ticket: `tickets/epics/2026-09-02_ordered_live_spell_disposal_epic.md`
- Status: ready
- Owner: codex
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-04T21:17:27Z
- Updated: 2026-09-04T22:06:16Z

## Objective
Make public/source documentation and generated repository assets describe the verified
ordered-disposal behavior, preserving existing documentation work and generation rules.

## Ticket Contract
- ENTRY_GATE: Producer/runtime/replay tasks verified; board routes here; read current
  working-tree changes and documentation ownership before editing shared surfaces.
- EXECUTION_BOUNDARY: Relevant disposal docs/examples, changed source descriptors/indexes,
  source build assets, LLM corpora, and patch promotion records.
- DEPENDENCIES: `tickets/tasks/2026-09-04_ordered_disposal_crystal_replay_task.md`.
- EXIT_GATE: Public examples and canonical docs match source; required generated assets are
  current and reproducible; artifact disposition is recorded for final accepted closure.
- FAILURE_ESCALATION: Record a real generator/overlap problem; do not rewrite unrelated docs,
  repair the entire stale graph, hand-edit generated output, or bypass asset checks.

## Scope Boundaries
- In scope: changed disposal contract and derived representations.
- Out of scope: new documentation platform, unrelated diagrams, version bumps, commits/pushes/releases.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Owner requested a completion task for documentation and derived assets.

## Required Reading and Evidence
- Current implementation task notes and their successful tests, not only the design.
- `agent_onboarding/default/engineer/skills/system_document_build.md`
- `agent_onboarding/default/engineer/skills/src_graph_generation.md`
- Relevant architecture/component authoring instructions before changing authored maps.
- Component index routes: configuration, binding, Creations, compiler, Crystallizer.
- `UX_and_AIX_experiences/AGENTS.md` before entering that example tree.
- Current `README.md`, relevant existing disposal examples, and architecture_and_design pages.
- Inspect source build runner/LLM builder instructions before executing them.
- Original user-facing plan: discovery task's current Phase 1 Design and Configuration Change Map.

## Steps / Checklist
- [ ] Inspect mailbox/attention and dirty files; codex_2 has separate Read the Docs work.
- [ ] Explain both contributing lists, flag default False, priority True, missing names,
      overlap handling, and creation-time resolution in the relevant public examples.
- [ ] Preserve current configuration setter lifecycle in examples; name defaults are set-once.
- [ ] Update authored component/architecture deltas only where the implementation changed.
- [ ] Rebuild each edited document's index in the same pass.
- [ ] Update changed source descriptors and assemble graph+index through the documented tools.
      Preserve unrelated authored semantics and report pre-existing staleness separately.
- [ ] Regenerate source assets first, then repository/LLM assets which include those source outputs.
- [ ] Run both freshness checks, inspect generated diffs, and verify only relevant inputs changed.
- [ ] Record patch promotion and pending disposition; apply deletion only at accepted closure.

## Deliverables
Accurate public examples, updated canonical deltas, current generated assets, and reviewable diffs.

## Files / Paths Impacted
- Relevant sections of `README.md`, `UX_and_AIX_experiences/`, and `architecture_and_design/`.
- `context_compass/system_docs/src_components.md` and index; architecture only if its contract changes.
- Changed source descriptors plus generated graph/index through the normal pipeline.
- Actual patch artifacts produced by the contract task and their association rows.
- Generated outputs from the existing source and repository asset builders.

## Validation
- Not run; ticket only. Use a verified supported interpreter and documented generator invocation.
- Source build command: `python src/melder/_build_assets/_build_asset_runner.py`.
- Source check: `python src/melder/_build_assets/_build_asset_runner.py --check`.
- Repository build: `python llm_support/_builder.py`.
- Repository check: `python llm_support/_builder.py --check`.
- Replace python with the verified 3.14 executable when PATH still points to 3.13.
- Check links/examples and generated diff hygiene; do not rerun unrelated generators for polish.

## Risks / Rollback Notes
Source graph hashes were stale for several inspected files before this feature. Fix only
changed-file semantics and keep the generated index accurate; do not claim a full graph audit.
Do not overwrite codex_2/user changes in shared docs or change asset formats incidentally.

## Applicable Anti-Patterns
- [ ] No hand-written generated payload/corpus/index changes.
- [ ] No unrelated README or hosted-docs redesign.

## Done Checklist
- [ ] Docs match source and exact examples; links validated.
- [ ] Build order and freshness results recorded; generated diffs inspected.
- [ ] Artifact associations/disposition and final validation handoff updated.
- [ ] Owner acceptance before final closure or artifact removal.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false at ticket creation
- ARTIFACT_PATHS: none yet; link actual contract-task artifacts for promotion
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: owner-accepted closure after final validation

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: public contract, canonical docs, generated assets
- IF_UNKNOWN: none

## Noting Behavior
Record actual documentation/generation outcomes with paths; retain source truth over old prose.

## Notes
- DATETIME: 2026-09-04T21:17:27Z
  TYPE: PLAN
  CLAIM: Documentation follows verified runtime/replay; source assets must precede LLM regeneration.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-09-02_ordered_spell_disposal_contract_discovery_task.md:140-320`
  IMPACT: Published descriptions and committed asset proofs will match the same ordered contract.
  NEXT: After replay verification, inspect current documentation changes and affected examples.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T22:04:01Z
  TYPE: FACT
  CLAIM: Both current asset workflows are check-only. The source runner discovers builders
    and verifies their committed version/schema/input fingerprints. The LLM builder hashes
    eligible tracked files per corpus and rebuilds only stale corpora. Its classifier excludes
    ContextCompass and generated source manifest/payload directories; raw packaged document
    payloads are NOT inputs to llm_full_src. Ordinary source builders/loaders remain eligible.
  EVIDENCE:
  - `.github/workflows/build-src-assets.yml:97-121`
  - `.github/workflows/build-repo-assets.yml:34-58`
  - `src/melder/_build_assets/_build_asset_runner.py:184-399`
  - `llm_support/_builder.py:63-100`
  - `llm_support/_builder.py:313-401`
  - `llm_support/_builder.py:653-766`
  IMPACT: Keep the source-build then repository-build completion sequence, but do not claim
    the LLM bundle includes every generated payload. Changes to eligible source, tests, and
    public docs invalidate their own corpora. ContextCompass-only findings need no corpus
    regeneration. Do not edit workflow behavior in this epic; workflows_1 owns that separate lane.
  NEXT: After feature verification, refresh relevant authored docs/descriptors and run both
    builders/checks against the final source/test/public-doc state, inspecting actual diffs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T11:37:10Z
  TYPE: PLAN
  CLAIM: Owner clarified overlaps: book order owns shared names in BOTH modes; False places
    the full book block last and True first. Bind and configuration setter docs now describe it.
    During canonical/public promotion, replace any earlier first-group-wins wording, including
    the active/inactive Spellbook argument docs, and refresh all derived representations.
  EVIDENCE:
  - `src/melder/aether/spellbook/bind/bind.py:258-278`
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py:1128-1158`
  - Navigation: Spellbook.bind/bind_inactive disposal argument descriptions near lines 4806/5077.
  IMPACT: The runtime prerequisite is verified (2,807 tests); final documentation/assets remain
    deferred until replay is complete, avoiding conflicting writes to other agents' corpora.
  NEXT: After replay, explain book-block placement and overlap ownership at every documented input route.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
No work executed yet. Use implemented behavior and task evidence, preserve the separate RTD lane,
and run source assets before LLM assets. Final task:
`tickets/tasks/2026-09-04_ordered_disposal_end_to_end_validation_task.md`.
