# Story: Verify the complete documentation experience and launch it with a maintenance contract

## Metadata
- Story ID: STORY-2026-09-04-rtd-quality-and-launch
- Epic: EPIC-2026-09-04-readthedocs-documentation
- Epic Path: ../epics/2026-09-04_readthedocs_documentation_epic.md
- Status: draft
- Owner: codex
- Agent Name: codex_2
- Priority: p1
- Created: 2026-09-04T21:36:46Z
- Updated: 2026-09-04T21:36:46Z

## User Narrative
As a reader and maintainer, I can trust that the released site is complete, navigable, accessible, and
aligned with the package/examples it documents, and that future updates preserve those properties.

## Value / MRP Alignment
Close the program on demonstrated reader outcomes and maintainability, not merely a successful HTML build.

## Ticket Contract
- ENTRY_GATE: S1-S8 deliverables and evidence available; quality/launch task routed to this story.
- EXECUTION_BOUNDARY: documentation quality checks, browser/download review, publication verification,
  maintenance guide, and scoped corrections routed back to owning stories.
- DEPENDENCIES: All eight implementation stories; current example-run evidence and actual RTD preview.
- EXIT_GATE: All launch criteria resolved, owner accepts the published/reviewable result, boards synchronized.
- FAILURE_ESCALATION: Return defects to the owning story; record unresolved failures instead of suppressing them.

## Requirements (Functional)
- Audit exactly four learning levels, homepage example prominence, full contents, and all navigation routes.
- Reconcile every numbered lesson and public API item against the catalog/reference inventory.
- Verify actual lesson outcomes on the documented revision; check that published code matches source.
- Check internal links/anchors, source links, images, downloads, canonical URLs, sitemap, and redirects.
- Review search by both common tasks and API names, version switching, and wrong/empty search cases.
- Review keyboard, focus, narrow-screen, zoom, diagram, long-code, and offline reading behavior.
- Launch only with an identified build/revision and a usable rollback/rebuild procedure.
- Provide maintenance instructions and a feedback loop for search gaps, source drift, and broken links.

## Requirements (Non-Functional)
- Do not silently omit failing lessons or suppress warnings globally to satisfy a gate.
- Separate deterministic checks from network-dependent link/service checks and report each honestly.
- Keep review evidence concise, reproducible, and traceable to the relevant story/task.

## Scope Boundaries
- In scope: quality/launch evidence, focused documentation checks, maintenance runbook, and accepted rollout.
- Out of scope: unrequested runtime rewrites, new learning-level taxonomy, and broad unrelated cleanup.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Quality and launch scope defined; no implementation or release executed.

## Dependencies / Related Work
Use S1-S8 ownership to route defects. The parent epic remains open until this story and all others are accepted.

## Tasks (Implementation Checklist)
- [ ] Open an audit task and produce the complete requirements-to-evidence matrix.
- [ ] Run content/navigation/source/example checks and review representative reader journeys.
- [ ] Resolve issues with the owning stories; repeat only affected checks when warranted.
- [ ] Review the launch candidate, publish within authorized scope, and verify the live outcome/runbook.

## Acceptance Criteria
- [ ] Every gate in blueprint section 15 has current evidence or an explicit owner ruling.
- [ ] All four levels, all saved lessons, and selected public references have complete usable routes.
- [ ] No unexplained missing content, duplicate IDs, broken local links, or false run claims remain.
- [ ] Browser/mobile/keyboard/zoom and download reviews demonstrate usable content.
- [ ] Hosted search, version identity, canonical/source links, and redirects are verified.
- [ ] A maintainer can add a lesson/page/API and rebuild/release using the documented procedure.
- [ ] Owner walkthrough/acceptance and all child/epic closure synchronization are recorded.

## Validation / Test Plan
Not run. Plan combines Sphinx build checks, catalog/API reconciliation, actual example suite/probes,
rendered-browser review, download inspection, and real hosted checks. Record command/revision/outcome.

## UX / API / Data Notes
Reader journeys: first useful result, arbitrary topic jump, browse/run an example, resolve an error,
look up an API, compare versions, and use downloaded documentation.

## Risks / Mitigations
Green builds can hide poor navigation or weak examples. The final review includes actual reader tasks
and meaningful assertions. Time/resource limits are measured, not used to reduce promised scope silently.

## Open Questions
Any remaining defects/hosting limitations must have an owner and disposition before launch acceptance.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS: artifacts/2026-09-04_readthedocs_site_blueprint.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Parent epic closure after all stories are accepted.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: full-site evidence, reader journeys, launch, maintenance
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-04T21:36:46Z
  TYPE: PLAN
  CLAIM: S9 closes the program on verified reader outcomes, complete coverage, real example evidence,
    hosted behavior, and a maintenance procedure. It cannot pass from HTML generation alone.
  EVIDENCE:
  - artifacts/2026-09-04_readthedocs_site_blueprint.md:326-356
  - UX_and_AIX_experiences/pytest_examples/test_example_contract.py:1-121
  IMPACT: The finished site preserves the owner's curriculum and stays trustworthy as Melder changes.
  NEXT: Assemble the final evidence matrix after S1-S8 are ready for integrated review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Applicable Anti-Patterns
- [ ] No launch with silent omissions, fabricated results, or unresolved ownership.
- [ ] No premature epic closure while a required story remains unaccepted.

## Closure Confirmation
- [ ] Final walkthrough, explicit acceptance, and all required board/artifact synchronization completed.

## Noting Behavior
Record integrated evidence, unresolved defects and owners, acceptance decisions, and maintenance obligations.

## Context / Handoff Summary
Defined, not implemented. S9 is the final integrated verification and launch/maintenance story for the epic.
