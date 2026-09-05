# Task: Implement public API and architecture reference integration

## Metadata
- Task ID: TASK-2026-09-04-rtd-reference-content
- Epic: EPIC-2026-09-04-readthedocs-documentation
- Story: STORY-2026-09-04-rtd-reference-and-architecture
- Story Path: ../stories/2026-09-04_rtd_reference_and_architecture_story.md
- Status: review
- Owner: codex
- Agent Name: codex_2
- Priority: p1
- Created: 2026-09-04T22:07:46Z
- Updated: 2026-09-04T22:07:46Z

## Objective
Publish curated public API, canonical architecture/drawings, glossary, troubleshooting, migration, and audited agent-reference routes.

## Ticket Contract
- ENTRY_GATE: Parent story/blueprint read, dependency milestone available, and this task actively routed.
- EXECUTION_BOUNDARY: docs/reference/, API selector/assembly code, architecture link adaptation, glossary and troubleshooting pages, and directly relevant docstring/prose corrections.
- DEPENDENCIES: S1/S2 and agreed curriculum topic/API target map; completed curriculum prose is not required to begin.
- EXIT_GATE: Acceptance checks have evidence; delivery state and parent story are synchronized.
- FAILURE_ESCALATION: Record concrete failures and preserve unaffected progress; do not infer success.

## Scope Boundaries
- In scope: the declared documentation task and necessary focused validation.
- Out of scope: unrelated runtime changes, other agents' assignments, and unrequested account actions.
- User authorization: implementation requested on 2026-09-04; ordinary scoped edits/checks may proceed.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Implementation task defined; prerequisite work remains ahead of activation.

## Steps / Checklist
- [ ] Read the exact inputs and record one bounded implementation decision.
- [ ] Complete required patch contracts when the change is system-impacting.
- [ ] Implement the scoped deliverable with notes before the next tranche.
- [ ] Validate meaningful behavior/content and record actual outcomes.
- [ ] Synchronize parent story and hand off or close after acceptance.

## Acceptance Criteria
- [ ] Public API inventory has no unexplained omissions or duplicate anchors.
- [ ] Current signatures and public-name aliases render correctly.
- [ ] Existing diagrams/prose retain canonical ownership and valid relative/source links.
- [ ] Glossary, troubleshooting, and example/API relationships are complete.
- [ ] Machine-readable content is explicitly selected and audited before inclusion.

## Validation
- Strict Sphinx HTML build: 292 pages. Documentation unit suite: 31 passed.
- Browser inspection confirmed formatted Spellbook signatures, parameter links, and source navigation.
- Use the parent story's validation plan and report local/hosted/execution results separately.

## Risks / Mitigations
- Canonical source and existing lessons can change concurrently; verify relevant inputs before edits.
- Hosting/dependency availability is an external-state check, not permission to invent completion.
- Keep the four owner-defined learning levels and prominent examples invariant.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS: artifacts/rtd_validation_20260904/reference_build.log
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Record task-owned artifact disposition before accepted closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Implement public API and architecture reference integration
- IF_UNKNOWN: none

## Noting Behavior
- Finish a coherent read/work unit and append evidence, impact, and one next action.
- Keep notes append-only; label unverified claims explicitly.

## Notes
- DATETIME: 2026-09-04T22:07:46Z
  TYPE: PLAN
  CLAIM: Implement this bounded part of the accepted documentation program under its existing story.
  EVIDENCE:
  - artifacts/2026-09-04_readthedocs_site_blueprint.md:293-344
  - Owner implementation instruction on 2026-09-04.
  IMPACT: The complete program now has explicit execution tasks and dependency boundaries.
  NEXT: Activate this task when its dependency milestone is available.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T00:07:14Z
  TYPE: DECISION
  CLAIM: The package root explicitly declares its public exports. Build an exhaustive disposition
    registry over those names, group reference pages by user activity, and render selected contracts
    from canonical source docstrings. Include documented returned command/document surfaces explicitly.
    Integrate architecture prose/assets through its existing manifest with contained relative links.
    The existing patch's validate-before-output and public-input-only invariants remain mandatory.
  EVIDENCE:
  - src/melder/__init__.py:46-166
  - src/melder/__init__.py:200-269
  - system_docs/patches/active/rtd_site_2026_09_04/architecture_patch.md:15-38
  IMPACT: References extend the same publisher and cannot silently expose all internal modules or work records.
  NEXT: Inspect the architecture manifest and expand the API proof beyond SpellMap.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T00:11:29Z
  TYPE: FACT
  CLAIM: Full Spellbook autodoc produces 11 docutils warnings/errors from malformed indentation
    and list boundaries. The class docstring contains a continuation at column zero, which breaks
    dedenting of the entire class contract. No annotation import failure appeared in this probe.
    Architecture manifest declares 18 public documents and 10 generated diagram pairs; its drawing
    document additionally references 17 authored SVG/Mermaid pairs. Preserve their original sources.
  EVIDENCE:
  - artifacts/rtd_validation_20260904/api_probe.log:1-15
  - src/melder/aether/spellbook/spellbook.py:67-170
  - architecture_and_design/manifest.json:1-361
  - architecture_and_design/05_engineering_drawings/README.md:1-449
  IMPACT: Correct demonstrated prose formatting; no blanket warning suppression or runtime rewrite.
  NEXT: Build exhaustive API selectors and canonical architecture/link assembly, then resolve strict warnings.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T00:50:29Z
  TYPE: MEASURE
  CLAIM: Integrated references build at 292 pages with 31 documentation tests passing. Every declared
    package export has a selected disposition, plus eight explicit returned surfaces. Architecture
    publication consumes 18 canonical documents and 27 drawing pairs. Normalized Mermaid source hashes
    and exact SVG hashes match the existing manifest. Fixed four isolated source-docstring formatting
    defects and adapted documented lists/code examples in the presentation layer; no warning suppression.
    Browser inspection shows correct Spellbook signatures and cross-linked type/source references.
  EVIDENCE:
  - docs/api.toml
  - docs/tools/api_reference.py
  - docs/tools/architecture_reference.py
  - docs/tests/test_references.py
  - artifacts/rtd_validation_20260904/reference_build.log
  IMPACT: Reference, glossary, troubleshooting, source navigation, and featured applications are ready
    for integrated quality checks. Current source changes require normal generated-asset verification.
  NEXT: Wire the shared build into CI/RTD and produce the defined offline handbook.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Applicable Anti-Patterns
- [x] No silently omitted content or invented validation.
- [x] No unrecorded scope changes or interference with another agent's work.

## Context / Handoff Summary
Reference implementation is in review. The latest complete build produced 292 pages; the subsequent
small link/fence-preservation changes pass the 31-test docs suite and need the final integrated rebuild.
Four source changes are docstring formatting only. API inventory, canonical architecture selection,
glossary, troubleshooting, migration, and feature cards are implemented. S8 owns build/host/offline;
S9 still owns final link, browser, source-fidelity, and launch checks.
