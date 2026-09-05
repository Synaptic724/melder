# Task: Implement the complete saved-example catalog and lesson pages

## Metadata
- Task ID: TASK-2026-09-04-rtd-example-catalog
- Epic: EPIC-2026-09-04-readthedocs-documentation
- Story: STORY-2026-09-04-rtd-example-catalog
- Story Path: ../stories/2026-09-04_rtd_example_catalog_story.md
- Status: review
- Owner: codex
- Agent Name: codex_2
- Priority: p1
- Created: 2026-09-04T22:07:46Z
- Updated: 2026-09-04T22:07:46Z

## Objective
Publish all numbered source lessons with stable pages, source-included code, metadata, run instructions, and level/topic discovery.

## Ticket Contract
- ENTRY_GATE: Parent story/blueprint read, dependency milestone available, and this task actively routed.
- EXECUTION_BOUNDARY: docs/catalog.toml, docs/examples/, catalog/source-inclusion modules in docs/tools/, styles/scripts for catalog interaction, and docs-focused tests.
- DEPENDENCIES: S1 foundation and navigation schema; actual saved corpus; local example policy.
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
- [ ] All numbered scripts are reconciled exactly once; initial floor is 133.
- [ ] No generated page duplicates executable source as authored truth.
- [ ] Run/source/helper routes are accurate and revision-aware.
- [ ] Static and filtered catalogs remain usable by keyboard/mobile.
- [ ] New, missing, or duplicate metadata has explicit validation behavior.

## Validation
- Not run. Implementation task just created.
- Use the parent story's validation plan and report local/hosted/execution results separately.

## Risks / Mitigations
- Canonical source and existing lessons can change concurrently; verify relevant inputs before edits.
- Hosting/dependency availability is an external-state check, not permission to invent completion.
- Keep the four owner-defined learning levels and prominent examples invariant.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false until this task produces or owns a supporting artifact.
- ARTIFACT_PATHS: none; the parent story links the shared blueprint.
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Record task-owned artifact disposition before accepted closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Implement the complete saved-example catalog and lesson pages
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

## Applicable Anti-Patterns
- [ ] No silently omitted content or invented validation.
- [ ] No unrecorded scope changes or interference with another agent's work.

- DATETIME: 2026-09-04T22:43:42Z
  TYPE: DECISION
  CLAIM: Build a catalog from explicit per-level source inventories and AST-read module metadata.
    Validate discovered files against that inventory before staging. Merge generated lesson/index
    pages into the same navigation graph, preserve the authored Hello Melder route, and add static
    catalogs with progressive level/topic/text filtering. Source files and helper bundles are copied
    only into generated public downloads; examples are not executed during rendering.
  EVIDENCE:
  - artifacts/2026-09-04_readthedocs_site_blueprint.md:163-195
  - docs/tools/build_docs.py
  - UX_and_AIX_experiences/pytest_examples/test_example_contract.py:35-105
  IMPACT: The full saved corpus can become visible without duplicating authored code or silently
    dropping new/deleted lessons. Metadata defects must be corrected from actual source evidence.
  NEXT: Implement inventory reconciliation, lesson rendering, and complete catalog navigation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T22:43:42Z
  TYPE: FACT
  CLAIM: Consumed workflows_1's coordination notice: that lane owns edits to the three existing
    workflows, new ci/test-runtime/build-distributions workflows and .github/scripts, and PyYAML in
    the pyproject test group. It will regenerate LLM repository assets after its validation and is
    not editing docs files. Our later CI task must read that settled contract before integrating.
  EVIDENCE:
  - tickets/tasks/2026-09-04_implement_branch_ci_release_validation_task.md
  IMPACT: Continue documentation/catalog files without overlapping workflow ownership or regenerating
    shared LLM assets concurrently. No acknowledgment was requested.
  NEXT: Implement the complete example catalog within docs/.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T22:53:30Z
  TYPE: FACT
  CLAIM: Catalog validation rejected Beginner lesson 07 because its module header lacks SURFACE
    EXERCISED. The complete 35-line source was read: it constructs Spellbook, binds with string and
    Existence.many forms, conjures, and melds both classes. Add only the missing descriptive header;
    the executable lesson remains unchanged.
  EVIDENCE:
  - UX_and_AIX_experiences/01_beginner/07_strings_as_vocabulary.py:1-35
  IMPACT: The catalog gate found the same missing metadata category enforced by the existing example
    contract test. Correcting it preserves source truth instead of silently inventing a fallback field.
  NEXT: Add the source-backed header and run catalog/strict-build validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T23:08:54Z
  TYPE: MEASURE
  CLAIM: The 146-page strict build and 14 regression checks pass. Browser filtering narrowed the
    catalog to four Expert checkpoint examples, but visual inspection exposed a separate rendering
    defect: multiline goal text retained blank lines inside a raw HTML data attribute, which ended
    MyST's HTML block early and displayed escaped metadata. Normalize attribute whitespace and add
    a real MyST/Sphinx rendering regression before calling the catalog complete.
  EVIDENCE:
  - docs/tools/example_catalog.py:_cards
  - docs/_build/html/examples/index.html
  - Browser inspection of the Expert/checkpoint filtered catalog.
  IMPACT: Build success alone was insufficient; visual inspection found an output corruption that
    must be corrected before expanding the curriculum.
  NEXT: Flatten search attributes and verify a multi-paragraph fixture through Sphinx.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T23:14:37Z
  TYPE: MEASURE
  CLAIM: Catalog delivery now builds 146 source pages including all 133 lessons. Fifteen regression
    checks pass, including a real Sphinx/MyST rendering case for multiline metadata and a helper-aware
    source-snapshot ZIP test. Browser review confirms corrected cards, nine Expert/checkpoint matches,
    and Clear filters restoring all 133 with an empty query string. The old four-match observation
    came from the malformed HTML and is superseded. No example runtime execution is claimed yet.
  EVIDENCE:
  - docs/tools/example_catalog.py
  - docs/catalog.toml
  - docs/tests/test_example_catalog.py
  - docs/_build/html/examples/index.html
  - Strict build, unittest, and browser results on 2026-09-04T23:14:37Z
  IMPACT: The complete source-backed catalog is available for curriculum linking. Runtime verification
    and final offline format checks remain explicit downstream work.
  NEXT: Build the Beginner guide chapters from the README and saved lesson sources.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Defined task awaiting its dependency milestone.
Publish all numbered source lessons with stable pages, source-included code, metadata, run instructions, and level/topic discovery.
