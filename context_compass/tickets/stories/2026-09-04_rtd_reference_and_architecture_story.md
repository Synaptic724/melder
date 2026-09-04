# Story: Complete the architecture, public API, and lookup references

## Metadata
- Story ID: STORY-2026-09-04-rtd-reference-and-architecture
- Epic: EPIC-2026-09-04-readthedocs-documentation
- Epic Path: ../epics/2026-09-04_readthedocs_documentation_epic.md
- Status: draft
- Owner: codex
- Agent Name: codex_2
- Priority: p1
- Created: 2026-09-04T21:36:46Z
- Updated: 2026-09-04T21:36:46Z

## User Narrative
As a reader following a guide or solving a problem, I can move directly to the relevant architectural
explanation, public API contract, glossary term, or troubleshooting answer.

## Value / MRP Alignment
Make the four learning levels connect to durable, current reference material without duplicating source truth.

## Ticket Contract
- ENTRY_GATE: S1/S2 contracts and curriculum link map exist; current selected source is read; task routed.
- EXECUTION_BOUNDARY: docs/reference/, API selectors, glossary/troubleshooting/release guides, existing
  architecture inclusion, source links, and directly relevant documentation corrections.
- DEPENDENCIES: S1/S2; S3-S6 topic links; architecture_and_design manifest; current public export inventory.
- EXIT_GATE: Reference coverage is reconciled, APIs/diagrams render correctly, and links resolve.
- FAILURE_ESCALATION: Record unclear public/internal status, stale source claims, or unsupported imports.

## Requirements (Functional)
- Publish existing architecture prose and drawings from canonical files with captions and full-size access.
- Inventory public exports and documented returned surfaces; document or explicitly classify every entry.
- Group APIs by user activity: bind/configure, resolve/scope, connect, inspect, persist, evolve, handle errors.
- Render contracts from actual docstrings with signatures, parameters, errors, ownership, and threading notes.
- Preserve public-name aliases and avoid duplicate object anchors; link source at the built revision.
- Add glossary terms and aliases, symptom-based troubleshooting, release/migration guidance, and examples.
- Define agent reference routes to existing packaged documents and audited public machine-readable content.

## Requirements (Non-Functional)
- No parallel prose/code truth or automatic internal-module dump as the primary reader experience.
- Diagrams remain accessible and legible on narrow screens and in downloads.
- Searchable titles/descriptions use both ordinary task words and canonical Melder symbols.

## Scope Boundaries
- In scope: reference content, source selectors, existing diagrams, relevant cross-references and checks.
- Out of scope: re-exporting new runtime APIs, unrelated source changes, or publishing internal work records.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Reference delivery scope defined; no implementation started.

## Dependencies / Related Work
S3-S6 supply reader questions and lesson connections. S8 supplies version/hosting context; S9 audits completeness.

## Tasks (Implementation Checklist)
- [ ] Map public API/document coverage and reconcile inclusions/exclusions explicitly.
- [ ] Integrate architecture pages/SVGs and resolve local links to source/site destinations.
- [ ] Build public API, glossary, troubleshooting, migration, and agent reference pages.
- [ ] Verify signatures, type annotations, aliases, diagrams, and bidirectional lesson/reference links.

## Acceptance Criteria
- [ ] No unexplained public API omissions or duplicate anchors remain.
- [ ] Public names, signatures, and source revision links are correct.
- [ ] Existing architecture prose/diagrams have one canonical source and working site routes.
- [ ] Each major topic has meaningful guide/example/API connections.
- [ ] Glossary separates spellframe, conduit, and aetheric frame; troubleshooting gives corrective actions.
- [ ] Public machine-readable downloads, if included, pass an explicit content audit.
- [ ] Rendering and reference validation succeed without blanket warning suppression.

## Validation / Test Plan
Not run. Future checks: export/selector reconciliation, Sphinx object inventory and anchor checks,
representative import/type rendering, SVG/link validation, source-revision links, and mobile reading.

## UX / API / Data Notes
References support the four levels and free browsing; they do not introduce another curriculum hierarchy.

## Risks / Mitigations
Melder import effects and deferred typing require real build verification. Existing diagram hash checks
can be affected by Windows line endings; establish a consistent contract before regenerating assets.

## Open Questions
Exact current API inventory and the public eligibility of existing machine-readable bundles require inspection.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS: artifacts/2026-09-04_readthedocs_site_blueprint.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Parent epic closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: public API, architecture, glossary, troubleshooting, source links
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-04T21:36:46Z
  TYPE: PLAN
  CLAIM: S7 connects the learning levels and examples to complete, source-backed public references
    while preserving canonical architecture material and explicit public-content boundaries.
  EVIDENCE:
  - artifacts/2026-09-04_readthedocs_site_blueprint.md:196-212
  - artifacts/2026-09-04_readthedocs_site_blueprint.md:226-254
  - src/melder/__init__.py:203-269
  IMPACT: Reference lookup becomes useful and traceable instead of a disconnected generated appendix.
  NEXT: Inventory current public surfaces and their intended reference pages when S7 opens.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Applicable Anti-Patterns
- [ ] No unexplained API exclusions, stale diagrams, or private-record publication.
- [ ] No runtime contract changes just to satisfy the documentation builder.

## Closure Confirmation
- [ ] Reference walkthrough accepted; linked task/board state synchronized.

## Noting Behavior
Record coverage decisions, source freshness, import/typing findings, and cross-curriculum relationships.

## Context / Handoff Summary
Defined, not implemented. Complete the reference layer after the foundation/catalog and curriculum map exist.
