# Story: Publish the complete saved-example catalog from canonical source

## Metadata
- Story ID: STORY-2026-09-04-rtd-example-catalog
- Epic: EPIC-2026-09-04-readthedocs-documentation
- Epic Path: ../epics/2026-09-04_readthedocs_documentation_epic.md
- Status: draft
- Owner: codex
- Agent Name: codex_2
- Priority: p1
- Created: 2026-09-04T21:36:46Z
- Updated: 2026-09-04T21:36:46Z

## User Narrative
As a reader, I can find a runnable lesson by level or topic and read its actual code, setup, and
expected outcome on the documentation site.

## Value / MRP Alignment
Make the existing example investment a central maintained product surface, with coverage that cannot
quietly shrink when new scripts are added.

## Ticket Contract
- ENTRY_GATE: S1 local build/page contracts are available and a catalog implementation task is routed.
- EXECUTION_BOUNDARY: example discovery, editorial catalog, source inclusion, lesson template,
  level/topic indexes, helper/download handling, and catalog consistency checks.
- DEPENDENCIES: S1; saved example corpus and local AGENTS.md; blueprint section 8.
- EXIT_GATE: Every numbered lesson is reconciled, canonical code is displayed, and catalog UX is verified.
- FAILURE_ESCALATION: Record missing metadata, unsupported helpers, or lesson/source drift explicitly.

## Requirements (Functional)
- Discover all numbered .py lessons in the four existing directories; baseline inventory 41/37/19/36.
- Produce one stable page per lesson and include every page in complete contents and its level index.
- Support topic/name filtering, static browse lists, numeric learning order, and featured examples.
- Extract metadata without importing/executing lessons; supplement it with authored explanations.
- Embed actual source and provide exact run commands, prerequisites, expected outcomes, and API links.
- Keep source links at the built revision and package needed helper files in any promised download.
- Distinguish real run evidence from authored VERIFY text; no blanket verified status.

## Requirements (Non-Functional)
- Deterministic ordering/URLs, no duplicated executable code, keyboard-usable filters, static fallback.
- Missing/duplicate mappings, dropped lessons, broken helpers, and stale code inclusions fail checks.

## Scope Boundaries
- In scope: docs/catalog.toml, docs/examples/, catalog portion of docs/tools/, related navigation and checks.
- Read canonical inputs from UX_and_AIX_experiences; curriculum stories own substantive lesson corrections.
- Out of scope: changing lesson numbering/tier placement, runtime changes, or executing all lessons in RTD.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Catalog delivery contract defined; execution has not started.

## Dependencies / Related Work
- Depends on S1. Supplies generated pages and editorial slots to S3-S6 and links to S7.

## Tasks (Implementation Checklist)
- [ ] Open a scoped task and define lesson identity/schema from the actual corpus.
- [ ] Implement discovery, source inclusion, static catalog, and topic/level access.
- [ ] Add helper-aware run/download handling and revision-specific source links.
- [ ] Reconcile all 133 initial lessons, review representative pages, and hand off editorial gaps.

## Acceptance Criteria
- [ ] All numbered scripts map exactly once; additions cause an explicit metadata/publication decision.
- [ ] Every lesson page contains actual source, usable run instructions, and its level/goal.
- [ ] Full Contents, level catalogs, and topic routes reach the same stable pages.
- [ ] Copy controls copy executable commands/code cleanly.
- [ ] Required helper files are available through the documented run/download route.
- [ ] Verification labels never claim more than the recorded run evidence.
- [ ] Static and filtered catalogs work on desktop/mobile and by keyboard.

## Validation / Test Plan
Not run. Future checks: filesystem-to-catalog equality, duplicate IDs, source hash/content comparison,
helper packaging, changed/new/deleted lesson cases, navigation links, and representative browser flows.

## UX / API / Data Notes
Lesson metadata: stable ID, source path, level, title, goal, topics, prerequisites, relevant APIs,
run instructions, helper requirements, and optional revision-bound execution evidence.

## Risks / Mitigations
Some concept maps contain old counts/history; source discovery is authoritative for inventory.
Individual scripts may depend on local helpers; do not advertise unsupported standalone downloads.

## Open Questions
Resolve metadata gaps during the inventory task; never infer a missing lesson contract from its name.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS: artifacts/2026-09-04_readthedocs_site_blueprint.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Shared blueprint follows parent epic closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: lesson catalog, canonical source, helpers, discovery
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-04T21:36:46Z
  TYPE: PLAN
  CLAIM: S2 publishes the complete saved corpus as first-class pages and supplies the common lesson
    presentation/metadata contract to all four curriculum stories.
  EVIDENCE:
  - artifacts/2026-09-04_readthedocs_site_blueprint.md:163-195
  - UX_and_AIX_experiences/pytest_examples/test_example_contract.py:1-121
  IMPACT: Example visibility and code fidelity become explicit build invariants.
  NEXT: Open the catalog implementation task after S1's local foundation is available.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Applicable Anti-Patterns
- [ ] No hand-copied code or silent omitted lessons.
- [ ] No inferred run status from historic metadata.

## Closure Confirmation
- [ ] Catalog walkthrough accepted and linked task/board state synchronized.

## Noting Behavior
Record catalog schema changes, missing metadata, helper contracts, and per-level handoff needs.

## Context / Handoff Summary
Defined, not implemented. S2 builds the common example system; S3-S6 complete the content around it.
