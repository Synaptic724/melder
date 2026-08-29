# Task: Add compact documentation routes to the root README

## Metadata
- Task ID: TASK-2026-08-29-root-readme-documentation-routes
- Status: review
- Owner: cowork
- Agent Name: codex_1
- Priority: p1
- Created: 2026-08-29T16:38:36Z
- Updated: 2026-08-29T16:43:25Z

## Objective
Enrich the root README with a compact routing layer that points readers to the
architecture-and-design journey and the repository examples without duplicating
their content.

## Ticket Contract
- ENTRY_GATE: Owner explicitly requested a basic pointer-first README enrichment.
- EXECUTION_BOUNDARY: `README.md` plus ContextCompass task/board state only; no
  architecture-page, example, runtime, package, or dependency changes.
- DEPENDENCIES: Existing `architecture_and_design/` and `examples/` navigation.
- EXIT_GATE: Compact links are placed in the existing reading flow, every target
  resolves, documentation checks pass, and the README remains a front door.
- FAILURE_ESCALATION: Stop if examples lack a stable landing target or if the
  existing README structure requires broader reorganization.

## Scope Boundaries
- In scope:
  - Inspect the current README reading/navigation sections.
  - Inspect top-level example folders and their landing documentation.
  - Add concise links and one-sentence routing guidance.
  - Validate local links, documentation checks, and diff hygiene.
- Out of scope:
  - Copying architecture or example content into the README.
  - Adding a full generated table of contents.
  - Rewriting the existing Part I / Part II tutorial.
  - Editing files under `architecture_and_design/` or `examples/`.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: Owner authorized the focused pointer-first README change.

## State Transition Event (Review)
- from_state: in_progress
- to_state: review
- transition_reason: Compact README routes are implemented and passed target,
  documentation, focused-test, and diff validation.

## Steps / Checklist
- [x] Identify the least disruptive insertion points.
- [x] Verify stable architecture and example destinations.
- [x] Add compact README routing links.
- [x] Validate links, documentation checks, and diff hygiene.

## Deliverables
- One focused root README navigation enrichment.

## Files / Paths Impacted
- `README.md`
- `context_compass/tickets/tasks/2026-08-29_root_readme_documentation_routes_task.md`
- `context_compass/attention_board.md`
- `context_compass/mailbox_board.md`

## Validation
- Local target existence check.
- `architecture_and_design/tools/architecture_docs.py check`.
- Focused architecture-documentation tests when relevant.
- `git diff --check`.

## Risks / Rollback Notes
- Too many links would recreate a table of contents; keep destinations few and
  purpose-based.
- Rollback removes only the new README routing block.

## Applicable Anti-Patterns
- [x] No content duplication from deeper docs.
- [x] No complete API/reference catalogue in the root README.
- [x] No unrelated README restructuring.
- [x] No broken or unstable example-folder link.

## Done Checklist
- [x] Routing copy added
- [x] Link targets verified
- [x] Validation passed
- [ ] Owner acceptance confirmed

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: none
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS:
  - root README routing
  - architecture-and-design landing
  - examples landing paths
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: insertion point, destination stability, and link validation.

## Notes
- DATETIME: 2026-08-29T16:38:36Z
  TYPE: PLAN
  CLAIM: Keep the 1,051-line README's existing narrative and add only a compact
    purpose-based route to deeper architecture/design and runnable examples.
  EVIDENCE:
  - README.md:1-1051
  - architecture_and_design/README.md
  IMPACT: Readers gain clear depth choices without turning the README into a copy
    of the new documentation system.
  NEXT: Inspect the existing `How to Read This` / `Documentation` sections and
    top-level example destinations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T16:40:57Z
  TYPE: FACT
  CLAIM: The README already has the right insertion surfaces: a four-level `How to
    Read This` table and a compact `Documentation` destination table. There is no
    root `examples/` directory; the stable runnable curriculum is tiered under
    `UX_and_AIX_experiences/01_beginner` through `04_expert`, and
    `UX_and_AIX_experiences/pytest_examples` is its verification harness.
  EVIDENCE:
  - README.md:220-244
  - README.md:1010-1020
  - UX_and_AIX_experiences/AGENTS.md:1-38
  - UX_and_AIX_experiences/01_beginner/
  - UX_and_AIX_experiences/02_intermediate/
  - UX_and_AIX_experiences/03_advanced/
  - UX_and_AIX_experiences/04_expert/
  - UX_and_AIX_experiences/pytest_examples/
  IMPACT: The least disruptive enrichment is to add example-folder links directly
    to each existing level row, then add engineering-drawing, runnable-example, and
    verification destinations to the bottom routing table.
  NEXT: Edit only `README.md` with the compact routing links.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T16:41:58Z
  TYPE: FACT
  CLAIM: The root README now routes without duplicating deeper content. Each level
    row links its matching runnable example folder; the reading-flow paragraph links
    architecture/design, engineering drawings, and the pytest example harness; and
    the bottom Documentation table exposes the same destinations as compact choices.
  EVIDENCE:
  - README.md:220-247
  - README.md:1013-1027
  IMPACT: Readers can choose narrative, architecture, pictures, runnable scripts, or
    verification directly while the existing Part I / Part II tour stays intact.
  NEXT: Verify every new local target, run documentation checks and focused tests,
    and inspect diff hygiene.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T16:43:25Z
  TYPE: MEASURE
  CLAIM: Focused README routing validation passed. All seven new local destinations
    exist and appear in the README; the architecture documentation checker passed;
    18 focused tests passed; `git diff --check` exited zero; and the verified pytest
    temp directory was removed. The only diff output is the pre-existing root README
    LF-to-CRLF warning.
  EVIDENCE:
  - README.md:220-247
  - README.md:1013-1027
  - architecture_and_design/tools/architecture_docs.py:1-416
  - tests/unit/architecture_and_design/test_architecture_docs_tool.py
  IMPACT: The root README now acts as a stronger routing front door without copying
    or restructuring the deeper documentation and examples.
  NEXT: Present the focused enrichment for owner acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
README routing is implemented and validated; awaiting owner acceptance.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
