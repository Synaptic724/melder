# Story: Deliver indexed whole-repository LLM support assets

## Metadata
- Story ID: STORY-2026-08-30-llm-support-compilation-pipeline
- Epic: none
- Status: review
- Owner: cowork
- Agent Name: codex_1
- Priority: p0
- Created: 2026-08-30T22:07:25Z
- Updated: 2026-08-30T22:32:04Z

## User Narrative
As a repository user or external agent, I want deterministic indexed source,
test, and other bundles so that whole-repository material is portable without
replacing ContextCompass as the canonical navigation and work-state system.

## Value / MRP Alignment
Provides one trustworthy bulk-export surface with explicit authority,
staleness, encoding, exclusion, and incremental rebuild contracts.

## Ticket Contract
- ENTRY_GATE: Owner accepted the discovery design and check-only CI policy.
- EXECUTION_BOUNDARY: The approved llm_support tree, its unit tests,
  `.gitattributes`, and two repository-asset GitHub workflows.
- DEPENDENCIES: Accepted discovery task/artifact and existing source build-asset workflow.
- EXIT_GATE: Child task is in review; generated outputs are current,
  deterministic, indexed, and CI-checkable.
- FAILURE_ESCALATION: Stop on corpus-count drift outside documented exclusions,
  nondeterministic output, unsupported text, or workflow write permission.

## Requirements (Functional)
- Generate src, tests, and other text bundles plus one Markdown index each.
- Maintain one deterministic manifest and regenerate only stale corpora.
- Provide build, check, list, corpus, and slice commands.
- Rename build-assets workflow/file to build-src-assets.
- Add the generic check-only build-repo-assets workflow.

## Requirements (Non-Functional)
- Stdlib-only, no melder import, UTF-8/LF output, atomic writes, fail-loud behavior.
- ContextCompass-first README and zero recursive llm_support input.

## Scope Boundaries
- In scope: approved implementation file plan and generated outputs.
- Out of scope: GitHub bot commits, pre-commit installation, runtime behavior.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Linked implementation task meets every generated-asset,
  workflow, documentation, and validation acceptance criterion.

## Dependencies / Related Work
- `tickets/tasks/2026-08-30_implement_llm_support_compilation_pipeline_task.md`
- `artifacts/2026-08-30_llm_support_compilation_pipeline_discovery.md`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-08-30-implement-llm-support-compilation-pipeline.
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- All three bundles/indexes and manifest are generated and pass check mode.
- Unchanged corpora are not rewritten.
- Corpus counts match the accepted policy.
- Both renamed/new workflows are read-only and structurally valid.
- Focused tests and diff/EOL hygiene pass.

## Validation / Test Plan
- Builder unit/contract tests, two-pass deterministic build, stale/tamper tests,
  repository census, workflow semantic checks, and existing build-asset check.

## UX / API / Data Notes
- README directs capable agents to ContextCompass first and warns that bundles are derived.

## Risks / Mitigations
- Large committed outputs: regenerate only changed corpus; keep input/output hashes.
- Historical other content: explicit authority warning and indexed access.

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- None.

## Decision Log
- 2026-08-30T22:07:25Z: Check-only CI accepted; workflow names are build-src-assets and build-repo-assets.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - `artifacts/2026-08-30_llm_support_compilation_pipeline_discovery.md`
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: story acceptance

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - indexed repository bundles
  - manifest-driven incremental generation
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-08-30T22:32:04Z
  TYPE: MEASURE
  CLAIM: The accepted three-corpus system and separated source/repository asset
    workflows are implemented and fully validated by the linked task.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-08-30_implement_llm_support_compilation_pipeline_task.md`
  IMPACT: Story technical acceptance is complete and ready for owner review.
  NEXT: Close only after explicit owner acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T22:07:25Z
  TYPE: DECISION
  CLAIM: Implement the accepted discovery design with check-only CI, rename the
    existing source workflow, and add a generic repository-assets workflow.
  EVIDENCE:
  - `context_compass/artifacts/2026-08-30_llm_support_compilation_pipeline_discovery.md`
  IMPACT: Implementation has one accepted file/behavior boundary.
  NEXT: Execute the linked task from builder core through generated outputs and workflows.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: task evidence, dependency flow, and acceptance state.

## Context / Handoff Summary
Implementation is in review. Source, tests, and stable non-ContextCompass text
have committed generated bundles/indexes and a deterministic manifest;
build-src-assets and build-repo-assets are separate read-only gates.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
