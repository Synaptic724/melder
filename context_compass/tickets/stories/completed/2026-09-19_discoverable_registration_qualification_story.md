# Story: Qualify and document the complete discovery-only registration feature

## Completion
- Completed: 2026-09-20T00:25:59Z
- Summary: Qualified the integrated feature, repaired both owner-reported failures, and synchronized documentation and generated assets.
- Acceptance: Owner requested turn-in, then required two repairs first; both are verified.

## Metadata
- Story ID: STORY-2026-09-19-discoverable-registration-qualification
- Epic: EPIC-2026-09-19-discoverable-non-resolvable-registrations
- Sequence: S7
- Status: done
- Owner: codex
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-19T17:25:45Z
- Updated: 2026-09-20T00:25:59Z

## User Narrative
As a user, I can rely on one documented end-to-end workflow for registering, inspecting, versioning,
and restoring definitions that Melder does not resolve, with compatible normal bindings.

## Value / MRP Alignment
Qualify the whole contract across subsystem boundaries and ship documentation/assets that describe it honestly.

## Ticket Contract
- ENTRY_GATE: S1-S6 deliver their contracts and evidence; final qualification task and patch mappings exist.
- EXECUTION_BOUNDARY: End-to-end regressions, examples, public/system docs, generated assets and final review.
- DEPENDENCIES: All preceding stories. No feature release is implied by this story.
- EXIT_GATE: Epic acceptance matrix is proven, docs/assets match implementation, and owner accepts closure.
- FAILURE_ESCALATION: Route real failures to the owning story; do not hide them with xfails or weaker assertions.

## Requirements (Functional)
- Prove one full flow: register False base/helper, publish connected Nexus graph, inspect/revise history,
  construct a consumer with a supplied input, reject missing supply/direct resolution, and restore.
- Prove normal omitted/True binding and existing default precedence remain intact.
- Qualify pre/post-conjure, active/parked, named/typed, nested, scoped and cache paths as applicable.
- Document exact flag/category semantics, naming constraints, failure messages and supported target families.
- Explain signature declarations, supplied/provider/default outcomes and graph-versus-execution relationships.
- Include versioning and restore limits, including legacy records and unavailable source/live values.
- Document the retained version rules: same-identity body-only edits do not automatically mint versions.
- Update authored architecture/components with measured source references and regenerate their indexes.
- Refresh graph descriptors/assembly and package/build-runner assets through their owning tools.
- Keep examples runnable against the final API and consistent with actual default values.

## Requirements (Non-Functional)
- Report only executed checks and supported behavior; distinguish targeted evidence from full-suite results.
- Prefer behavior/contract tests over internal shape assertions and coverage filler.
- No manual edits to generated graph/index/payload outputs and no unrelated formatting sweep.
- No wheel publication, git release, version bump or external messaging unless separately requested.

## Scope Boundaries
- In scope: integration evidence and documentation/build correctness of this feature.
- Out of scope: unrelated CI repair, blanket repository cleanup or deferred feature implementation.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner-authorized turn-in after delivered scope and reported failure repairs passed.

## Dependencies / Related Work
- Parent: `tickets/epics/completed/2026-09-19_discoverable_non_resolvable_registrations_epic.md`
- S2: `tickets/stories/completed/2026-09-19_discoverable_registration_modifier_story.md`
- S3: `tickets/stories/completed/2026-09-19_caller_supplied_socket_compiler_story.md`
- S4: `tickets/stories/completed/2026-09-19_discoverable_resolution_runtime_story.md`
- S5: `tickets/stories/completed/2026-09-19_discoverable_nexus_graph_and_history_story.md`
- S6: `tickets/stories/completed/2026-09-19_discoverable_registration_persistence_story.md`

## Required Reading Before Work
1. Parent acceptance matrix, accepted S1 decisions, all S2-S6 result notes, and retained validation artifacts.
2. Read current test-system orientation and appropriate indexed component sections:
   - `system_docs/tests_architecture.md`
   - `system_docs/tests_architecture_index.md`
   - `system_docs/tests_components.md`
   - `system_docs/tests_components_index.md`
3. Read source architecture and component sections for final changed behavior and graph-index slices
   for changed owners. Follow the actual implementation when documentation disagrees.
4. Read current test fixtures and project runner configuration:
   - `pyproject.toml`
   - `tests/integration/melder/spellbook/test_spellbook_integration_default_precedence.py`
   - `tests/integration/melder/spellbook/test_spellbook_integration_overrides.py`
   - `tests/integration/melder/mutation_research/test_research_room_commands_integration.py`
   - `tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py`
   - `tests/unit/melder/build_assets/test_build_asset_runner.py`
   Reopen feature regressions written by S2-S6 and their shared fixtures before extending them.
5. Read the build/qualification entry points before running generation or checks:
   - `src/melder/_build_assets/_build_asset_runner.py`
   - `src/melder/_build_assets/_system_documents/_builder.py`
   - `src/melder/_build_assets/_agent_documentation/_builder.py`
   - `src/melder/_build_assets/_bind_guard/_builder.py`
   - `.github/workflows/build-src-assets.yml`
   - `.github/workflows/build-repo-assets.yml`
   - `.github/scripts/ci_qualification.py`
   Follow those current entry points to repository bundle tools; do not assume their command lines.
6. Reopen the engineering generation/patch-consumption skills when their work starts:
   - `agent_onboarding/default/engineer/skills/system_document_build.md`
   - `agent_onboarding/default/engineer/skills/src_graph_generation.md`
   - `agent_onboarding/default/engineer/skills/patch_artifact_consumption.md`
   Read system-document authoring instructions for every authored document being changed.

## Tasks (Implementation Checklist)
- [x] Qualification/evidence owner:
  `tickets/tasks/completed/2026-09-19_publish_and_replay_non_resolvable_definitions_task.md`.
- [x] Owner-reported failure repairs: 394 distinct passes and 25 fresh-process churn passes.
  `tickets/tasks/completed/2026-09-19_fix_feature_turn_in_failures_task.md`.
- [x] Record end-to-end qualification in the joint final implementation task.
- [x] Run the selected behavioral matrix and correct native fixture/version expectations.
- [x] Update public usage guides and architecture/component contracts.
- [x] Regenerate authored indexes, graph descriptors/assembly and package/repository assets.
- [x] Review capability/default/restore documentation against executed behavior.
- [x] Present final walkthrough, limits and acceptance evidence; perform closure synchronization after acceptance.

## Acceptance Criteria
- The full registered-definition-to-Nexus-to-consumer-to-restore flow passes meaningful tests.
- Default-resolvable and ordinary-default compatibility is demonstrated.
- Every promised execution, graph and persistence variant has evidence or an explicit supported-scope limit.
- Generated assets agree with current sources and authored docs; public examples use the real API.
- No outstanding required story is hidden by a completion claim.

## Validation / Test Plan
- 8055 distinct selected tests pass after targeted reruns; one pre-existing skip/four xfails remain.
- 39 docs tests, strict 294-page build and 35,513-link/source validation pass. Source/LLM assets rebuilt.
- Full repository suite and coverage: Not run. No measured runtime-speed claim.
- Run focused suites first, then the necessary integration/qualification checks for changed boundaries.
- If performance is claimed, measure the relevant bind/conjure/meld paths on the supported interpreter.
- Keep coverage reporting separate and follow repository policy; no percentage is inferred from test count.

## UX / API / Data Notes
Documentation must distinguish discovery-only registration, caller-supplied input, normal provider and default.
Use the chosen category name OVERRIDE_REQUIRED and the existing module/binding/version workflow.

## Risks / Mitigations
Partially updated generated bundles can advertise behavior the runtime lacks; verify generation after final edits.

## Applicable Anti-Patterns
- [x] No skipped failure disguised as expected behavior.
- [x] No manual generated-file patch or unverified test/coverage claim.
- [x] No release/publication inferred from story completion.

## Open Questions
Resolve remaining supported-scope decisions with S1-S6 before writing definitive public guidance.

## Decision Log
- Qualification covers the integrated contract; individual transport/compiler stories are not feature completion.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: final owner acceptance and per-artifact disposition.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: integrated contracts, compatibility, evidence, docs and generated build assets.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-19T17:25:45Z
  TYPE: PLAN
  CLAIM: Reserve a final end-to-end qualification step with explicit documentation/build reading requirements.
  EVIDENCE:
  - tickets/epics/completed/2026-09-19_discoverable_non_resolvable_registrations_epic.md:186-240
  IMPACT: Feature completion requires agreement across execution, graph history and persisted reconstruction.
  NEXT: After S1-S6 delivery, read their evidence and derive the final qualification task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-19T23:28:23Z
  TYPE: MEASURE
  CLAIM: Cross-story qualification is recorded in the joint task: 8055 distinct selected passes,
    one existing skip and four existing xfails; 39 docs tests, strict HTML and site checks pass.
    Public/system docs explain native capability, graph/source/history, replay, ordinary constructor
    errors and retained existing limits. Build assets and repository bundles are regenerated.
  EVIDENCE:
  - artifacts/non_resolvable_graph_replay_20260919/qualification_summary.json:1-12
  - artifacts/non_resolvable_graph_replay_20260919/validation.md
  IMPACT: Implementation is review-ready, without claiming full-suite coverage or publishing a release.
  NEXT: Verify final asset freshness and provide the owner the completed change summary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T00:25:59Z
  TYPE: DECISION
  CLAIM: Owner-authorized feature turn-in is complete for this record. Both later reported failures
    are repaired: crystal test-double capability and current-run local cancellation forwarding.
    This acceptance retains ordinary Python errors, existing version rules and documented limits.
  EVIDENCE:
  - artifacts/non_resolvable_graph_replay_20260919/validation.md:1-78
  - artifacts/non_resolvable_followup_20260919/validation.md:1-50
  IMPACT: Record is done; validation evidence is retained and promoted patch contracts are archived.
  NEXT: none; reopen only for a new owner-requested change or new failure evidence.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Integrated walkthrough and evidence shared.
- [x] Owner accepts required behavior and recorded limits.
- [x] Child tasks, artifacts, docs and boards synchronized.

## Noting Behavior
Keep final cross-story acceptance and build evidence here; retain tactical logs in associated tasks/artifacts.

## Context / Handoff Summary
CLOSED at 2026-09-20T00:25:59Z. Qualified the integrated feature, repaired both owner-reported failures, and synchronized documentation and generated assets.
Final evidence and limits are in the graph/replay and follow-up validation artifacts.
No next implementation step remains in this accepted record.

### Historical pre-closure handoff
S7 is review-ready. Read the joint task validation artifact and latest asset-check logs. Selected-scope
qualification has 8055 distinct passes, one existing skip/four xfails; docs tests/build/site checks pass.
Ordinary Python errors replace the abandoned input preflight. No release or coverage measurement.
