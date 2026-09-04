# Story: Build Melder's four-level documentation foundation and navigation

## Metadata
- Story ID: STORY-2026-09-04-rtd-navigation-and-site-shell
- Epic: EPIC-2026-09-04-readthedocs-documentation
- Epic Path: ../epics/2026-09-04_readthedocs_documentation_epic.md
- Status: draft
- Owner: codex
- Agent Name: codex_2
- Priority: p1
- Created: 2026-09-04T21:36:46Z
- Updated: 2026-09-04T21:36:46Z

## User Narrative
As a reader, I can start at my level, browse the whole site, or open an example immediately, so I can
learn in sequence or go directly to the answer I need.

## Value / MRP Alignment
Establish one coherent navigation and local-build foundation that all content and hosting work can use.

## Ticket Contract
- ENTRY_GATE: The blueprint and owner-selected four levels are read; an implementation task is routed.
- EXECUTION_BOUNDARY: docs foundation, navigation registry, homepage, level landing pages, styling,
  complete contents, and the minimum local Sphinx build command.
- DEPENDENCIES: Site blueprint; completed ThreadFactory discovery; current README.
- EXIT_GATE: Local build proves the navigation and representative real content; owner accepts the shell.
- FAILURE_ESCALATION: Record build/import incompatibility or a required runtime change separately.

## Requirements (Functional)
- Exactly Beginner, Intermediate, Advanced, Expert in that order, with the existing level identifiers.
- Homepage: purpose, three verbs, prerequisites, four level cards, prominent Examples and Full Contents.
- Persistent expandable sidebar, breadcrumbs, on-page contents, heading links, previous/next, and search.
- One navigation registry drives page parentage, order, complete contents, and stable URLs.
- Supporting entries: All Examples, Architecture & Drawings, API, Glossary, Troubleshooting, Releases.
- Real first build includes Hello Melder, one existing drawing, and one selected public API page.
- Establish Sphinx/MyST, RTD theme, source inclusion, docstring formatting, cards, and code copying.

## Requirements (Non-Functional)
- Essential navigation works without custom JavaScript and remains usable with keyboard, mobile, and zoom.
- Keep level names visible; color/icons supplement them. Avoid parallel navigation taxonomies.
- Use deterministic public-source assembly and isolated docs dependencies. No product behavior changes.

## Scope Boundaries
- In scope: docs/conf.py, docs/requirements.txt, docs/index.md, docs/contents.rst, docs/navigation.toml,
  four level index pages, docs/_static/, docs/tools/build_docs.py, and related focused checks.
- Out of scope: complete lesson catalog, full curricula, complete API coverage, and hosted setup.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Planning record created; implementation has not started.

## Dependencies / Related Work
- Provides the local build and page/navigation contracts to every other story.
- S2 supplies the complete example catalog; S8 adds CI/hosting after content is complete.

## Tasks (Implementation Checklist)
- [ ] Define and route an implementation task with exact paths and navigation schema.
- [ ] Build homepage/four level shells and complete contents from one registry.
- [ ] Configure the docs environment and prove imports/source inclusion with real content.
- [ ] Review navigation on desktop/mobile and keyboard, then record the handoff contract.

## Acceptance Criteria
- [ ] Four level names/order match the README; all four are first-depth navigation entries.
- [ ] Full Contents and Examples are visible from every representative page.
- [ ] Direct deep links and previous/next work; no duplicate/orphan shell pages exist.
- [ ] One local command builds the same inputs deterministically with selected dependencies recorded.
- [ ] Real API signatures, source code, and a rendered SVG appear correctly.
- [ ] Narrow-screen, keyboard, 200% zoom, and no-custom-JS navigation checks are recorded.

## Validation / Test Plan
Not run. Future checks: strict Sphinx HTML build, navigation graph integrity, internal anchors, example
source equality, API import/annotation rendering, and representative browser checks.

## UX / API / Data Notes
The navigation registry stores stable document IDs and order, not duplicated prose or executable code.

## Risks / Mitigations
Autodoc imports Melder and its root constructs Aether; verify this with actual Python 3.14 before
expanding. Resolve docs-tooling incompatibility without weakening Melder's runtime/type contracts.

## Open Questions
Exact compatible dependency pins and any narrow source-assembly requirements are build-time findings.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS: artifacts/2026-09-04_readthedocs_site_blueprint.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Parent epic closure; shared blueprint remains until all dependent work is complete.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: four levels, navigation, site shell, local build
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-04T21:36:46Z
  TYPE: PLAN
  CLAIM: S1 owns the navigation and local-build contract. It establishes the four levels and complete
    contents that all downstream stories use; it does not create a second learning partition.
  EVIDENCE:
  - artifacts/2026-09-04_readthedocs_site_blueprint.md:10-69
  - artifacts/2026-09-04_readthedocs_site_blueprint.md:213-254
  IMPACT: Downstream content can be assembled consistently and reviewed in real rendered pages.
  NEXT: Open the scoped S1 implementation task when execution begins.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Applicable Anti-Patterns
- [ ] No hidden curriculum or duplicate source/navigation truth.
- [ ] No claims of a working build before it runs.

## Closure Confirmation
- [ ] Owner walkthrough and acceptance recorded; tasks and board synchronized.

## Noting Behavior
Record navigation decisions, dependency pins, import findings, and downstream interface changes.

## Context / Handoff Summary
Defined, not implemented. Begin with the README's four levels and the blueprint's homepage/contents
contract, then establish a real local build for S2-S9.
