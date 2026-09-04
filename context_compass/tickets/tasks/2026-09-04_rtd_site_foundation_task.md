# Task: Implement the four-level site foundation and local Sphinx build

## Metadata
- Task ID: TASK-2026-09-04-rtd-site-foundation
- Epic: EPIC-2026-09-04-readthedocs-documentation
- Story: STORY-2026-09-04-rtd-navigation-and-site-shell
- Story Path: ../stories/2026-09-04_rtd_navigation_and_site_shell_story.md
- Status: review
- Owner: codex
- Agent Name: codex_2
- Priority: p1
- Created: 2026-09-04T22:07:46Z
- Updated: 2026-09-04T22:07:46Z

## Objective
Create the working documentation source assembly, homepage, four level landings, complete contents, navigation, visual theme, and a representative real API/example/diagram build.

## Ticket Contract
- ENTRY_GATE: Parent story/blueprint read, dependency milestone available, and this task actively routed.
- EXECUTION_BOUNDARY: docs/conf.py, docs/requirements.txt, docs/navigation.toml, docs/index.md, docs/contents.rst, docs/tools/, docs/_static/, level landing pages, docs-focused checks, and this task's patch artifacts.
- DEPENDENCIES: Approved blueprint; required patch contracts; isolated Python 3.14 environment.
- EXIT_GATE: Acceptance checks have evidence; delivery state and parent story are synchronized.
- FAILURE_ESCALATION: Record concrete failures and preserve unaffected progress; do not infer success.

## Scope Boundaries
- In scope: the declared documentation task and necessary focused validation.
- Out of scope: unrelated runtime changes, other agents' assignments, and unrequested account actions.
- User authorization: implementation requested on 2026-09-04; ordinary scoped edits/checks may proceed.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: User authorized implementation; this is the first active delivery task.

## Steps / Checklist
- [ ] Read the exact inputs and record one bounded implementation decision.
- [ ] Complete required patch contracts when the change is system-impacting.
- [ ] Implement the scoped deliverable with notes before the next tranche.
- [ ] Validate meaningful behavior/content and record actual outcomes.
- [ ] Synchronize parent story and hand off or close after acceptance.

## Acceptance Criteria
- [ ] Local build runs with a recorded compatible dependency set.
- [ ] Exactly Beginner, Intermediate, Advanced, Expert appear as first-depth learning routes.
- [ ] Examples and Full Contents are prominent and all generated page IDs have one parent.
- [ ] A real saved example, public API signature, and architecture SVG render correctly.
- [ ] Keyboard/mobile/zoom navigation and source inclusion are inspected.

## Validation
- Not run. Implementation task just created.
- Use the parent story's validation plan and report local/hosted/execution results separately.

## Risks / Mitigations
- Canonical source and existing lessons can change concurrently; verify relevant inputs before edits.
- Hosting/dependency availability is an external-state check, not permission to invent completion.
- Keep the four owner-defined learning levels and prominent examples invariant.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/rtd_site_2026_09_04/architecture_patch.md
  - system_docs/patches/active/rtd_site_2026_09_04/component_patch_documentation_pipeline.md
  - system_docs/patches/active/rtd_site_2026_09_04/code_description_patch_documentation_pipeline.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Promote the durable contract into docs/maintaining.md at accepted pipeline closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Implement the four-level site foundation and local Sphinx build
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
  NEXT: Prepare the docs pipeline patch contract and the isolated build environment.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Applicable Anti-Patterns
- [ ] No silently omitted content or invented validation.
- [ ] No unrecorded scope changes or interference with another agent's work.

- DATETIME: 2026-09-04T22:14:08Z
  TYPE: DECISION
  CLAIM: Implement a documentation-only source assembly component with one navigation model and
    a strict public-input boundary. Patch architecture invariants map to path/source tests; component
    interfaces map to prepare/build/check CLI behavior; control-flow gates map to invalid-input and
    repeat-build checks. No Melder runtime behavior change is part of this task.
  EVIDENCE:
  - system_docs/patches/active/rtd_site_2026_09_04/architecture_patch.md
  - system_docs/patches/active/rtd_site_2026_09_04/component_patch_documentation_pipeline.md
  - system_docs/patches/active/rtd_site_2026_09_04/code_description_patch_documentation_pipeline.md
  IMPACT: Required patch scope and implementation/validation mapping are explicit before code edits.
  NEXT: Read the authored patch contracts and implement the navigation/build foundation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T22:14:08Z
  TYPE: MEASURE
  CLAIM: Isolated dependency installation succeeded after the authorized network escalation: Sphinx
    9.1.0, MyST 5.1.0, sphinx-rtd-theme 3.1.0, sphinx-design 0.7.0, and copybutton 0.5.2 are installed
    under the retained Python 3.14 docs environment. A Sphinx build has not yet run.
  EVIDENCE:
  - uv pip install output for context_compass/artifacts/rtd_probe_20260904/.venv on 2026-09-04T22:14:08Z
  IMPACT: The earlier network blocker no longer prevents local documentation implementation.
  NEXT: Build the first real site with those resolved versions and capture exact requirements.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T22:23:58Z
  TYPE: MEASURE
  CLAIM: Implemented the initial 10-page Sphinx site, four exact levels, complete contents generation,
    canonical example/SVG inclusion, theme, and validated prepare/check/build command. The first real
    HTML build rendered all pages and imported Melder successfully on Python 3.14, but strict status
    is failure because SpellMap's class docstring emitted six formatting warnings/errors. The expected
    GIL-mode UserWarning appeared separately; no runtime behavior was changed.
  EVIDENCE:
  - docs/tools/build_docs.py
  - docs/navigation.toml
  - docs/conf.py
  - docs/_build/html/index.html
  - Sphinx 9.1.0 first build output on 2026-09-04T22:23:58Z
  IMPACT: Actual rendering is available. Source docstring formatting is the first concrete strict-build
    defect to resolve before broadening API coverage or calling the foundation complete.
  NEXT: Read the SpellMap docstring and correct the narrow formatting mismatch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T22:26:50Z
  TYPE: DECISION
  CLAIM: SpellMap's class documentation contains a single-backtick python block, which native
    reStructuredText cannot parse. Add a docs-only autodoc formatter that translates known fenced
    code blocks before Napoleon runs, preserving text and code while leaving canonical runtime source
    untouched. Malformed unclosed blocks must fail explicitly rather than discard content.
  EVIDENCE:
  - src/melder/aether/conduit/meld/contracts/spell_map.py:35-58
  - docs/conf.py:27-37
  IMPACT: The publication layer handles the repository's existing docstring markup without a runtime
    edit or global warning suppression. Regression checks and the real strict build verify it.
  NEXT: Implement the format bridge and rerun the strict representative build.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T22:43:42Z
  TYPE: MEASURE
  CLAIM: The 10-page foundation passes the strict Sphinx build after adding the content-preserving
    docstring fence bridge. All nine docs regression checks pass. Browser inspection verified the
    four levels, cards, real full-contents links, and the 390px mobile layout without horizontal
    overflow. The native theme's icon-only menu was replaced by a real button; Enter toggled its
    expanded state. Direct mobile Contents/Examples links and per-page contents are present.
    Full zoom and corpus-wide checks remain part of the later quality task.
  EVIDENCE:
  - docs/tools/build_docs.py
  - docs/tools/docstring_format.py
  - docs/tests/test_build_docs.py
  - docs/_templates/layout.html
  - docs/_templates/page.html
  - Local Sphinx/unittest output and browser inspection at http://127.0.0.1:8765/
  IMPACT: The source/build/navigation contract is ready for the catalog task. Initial test fixture
    failures were a Windows temporary-directory ACL issue and were resolved using contained generated
    test workspaces; the passing test run is recorded above, not inferred.
  NEXT: Extend the foundation with all 133 saved lesson pages under the catalog task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Active first delivery task.
Create the working documentation source assembly, homepage, four level landings, complete contents, navigation, visual theme, and a representative real API/example/diagram build.
