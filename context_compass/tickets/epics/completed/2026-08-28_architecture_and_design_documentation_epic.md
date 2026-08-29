# Epic: Publish Melder architecture and design documentation

- Completed: 2026-08-29T16:31:01Z
- Summary: Published the full architecture-and-design reader journey, deterministic
  documentation tooling, ten canonical rendered diagrams, and seventeen manually
  composed engineering-drawing pairs; the complete lane is validated and accepted.

## Metadata
- Epic ID: EPIC-2026-08-28-architecture-and-design-documentation
- Status: done
- Owner: cowork
- Agent Name: codex_1
- Priority: p1
- Created: 2026-08-29T00:44:49Z
- Updated: 2026-08-29T16:31:01Z
- Target Window: current implementation lane
- Related Program/Initiative: Public Melder documentation

## Problem / Opportunity
Melder has a strong README and deep internal maps but no repo-native journey combining
high-level orientation, mid-level architecture, utilization stories, and portable pictures.

## MRP Alignment (Most Reasonable Product)
Build the smallest coherent documentation system whose navigation, pictures, evidence,
tradeoffs, and freshness workflow can grow without being rewritten.

## Ticket Contract
- ENTRY_GATE: Accepted ten-step discovery, routed foundation task, and linked artifact.
- EXECUTION_BOUNDARY: `architecture_and_design/`, its tests, the root README link, and
  ContextCompass state; no runtime implementation changes.
- DEPENDENCIES: Discovery artifact and three required tranche stories.
- EXIT_GATE: All three stories implemented, validated, reviewed, and accepted.
- FAILURE_ESCALATION: Raise BLOCKER for unrenderable diagrams, unevidenced behavior claims,
  or expansion into runtime code.

## Goals (Outcomes)
- Publish a three-depth user journey.
- Publish ten accessible, source-controlled architecture pictures.
- Publish core and advanced utilization documentation with evidence-backed tradeoffs.
- Provide deterministic render/check tooling without runtime dependencies.

## Non-Goals (Explicit Exclusions)
- Runtime code changes.
- A weaknesses catalogue.
- Class-by-class duplication of source documentation.

## Scope Boundaries
- In scope: accepted discovery tree, tooling, prose, diagrams, tests, and README entry link.
- Out of scope: API redesign, runtime dependencies, and hosted documentation deployment.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: Owner explicitly authorized implementation of the accepted design.

## State Transition Event (Final Drawing Expansion Review)
- from_state: in_progress
- to_state: review
- transition_reason: The engineering-drawing extension reached sixteen validated
  pairs and no implementation work remains before owner acceptance.

## State Transition Event (Closure)
- from_state: review
- to_state: done
- transition_reason: Owner declared the documentation program complete and
  explicitly requested all documentation tickets be turned in.

## Success Metrics
- Ten canonical `.mmd` sources and ten matching accessible SVGs.
- All proposed prose pages exist and route between depths.
- Manifest, render/check tool, and focused tests pass.
- Internal links and source/test anchors resolve.

## Requirements (Functional + Non-Functional)
- Use C4 as modeling discipline and stable Mermaid flowchart/sequence syntax.
- Keep SVGs generated and Mermaid sources canonical.
- Keep AGPL-3.0-or-later as current license truth.
- Keep diagrams legible, scoped, labelled, and textually explained.

## Constraints / Assumptions
- Mermaid rendering is documentation tooling only.
- Source truth governs behavioral claims.
- Existing unrelated worktree changes remain untouched.

## Dependencies / External References
- `artifacts/2026-08-28_architecture_and_design_documentation_discovery.md`
- C4 model, GitHub Mermaid rendering, and Mermaid CLI documentation.

## Milestones (Track Progress)
- [x] Milestone 1: Foundation and one rendered proof diagram.
- [x] Milestone 2: Human-facing MRP documentation and seven-picture core set.
- [x] Milestone 3: Advanced ceiling and complete ten-picture set.

## Stories (Required to Complete)
- [x] Story: STORY-2026-08-28-architecture-docs-foundation
- [x] Story: STORY-2026-08-28-architecture-docs-human-mrp
- [x] Story: STORY-2026-08-28-architecture-docs-advanced-ceiling

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete TASK-2026-08-29-system-document-engineering-drawings.
- [x] Task: Complete TASK-2026-08-28-architecture-docs-foundation
- [x] Task: Complete TASK-2026-08-28-architecture-docs-human-mrp
- [x] Task: Complete TASK-2026-08-28-architecture-docs-advanced-ceiling
- [x] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- Complete folder tree, prose set, ten diagrams, tooling, tests, and root navigation link.
- All claims and tradeoffs meet the evidence contract.
- Owner accepts the complete documentation lane.

## Risks / Mitigations
- Diagram drift: manifest hashes and render/check tooling.
- Visual overload: one reader question per picture.
- Marketing drift: capability/mechanism/evidence structure.

## Applicable Anti-Patterns
- [x] No implementation outside declared documentation/tool/test surfaces.
- [x] No diagram-only architectural claims.
- [x] No Mermaid experimental C4 syntax.

## Validation / Test Approach
- Unit tests for the documentation tool.
- Deterministic rendering, manifest checks, link checks, and manual SVG review.
- `git diff --check`.

## Rollout / Adoption Plan
- Land foundation, then human MRP, then advanced ceiling.
- Add the root README link only after the human MRP validates.

## Open Questions
- None; implementation is owner-authorized.

## Decision Log
- 2026-08-29: Accepted prose-first, C4-disciplined, Mermaid-source/SVG-render design.
- 2026-08-29: AGPL v3 remains current; Apache 2.0 is only a future option.
- 2026-08-29: Owner reopened the lane to add packaged C4/C3/C2 engineering drawings
  and Mermaid companions through the system-document build-asset path.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-08-28_architecture_and_design_documentation_discovery.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Epic closure after accepted promotion.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: architecture-and-design documentation implementation
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-08-29T00:44:49Z
  TYPE: PLAN
  CLAIM: Execute foundation, human MRP, and advanced ceiling in order under one epic.
  EVIDENCE:
  - artifacts/2026-08-28_architecture_and_design_documentation_discovery.md:379-447
  IMPACT: Tooling and evidence contracts precede the full picture/document set.
  NEXT: Implement the foundation task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T01:06:59Z
  TYPE: MEASURE
  CLAIM: Milestone 1 passed its render, check, test, compile, diff, and visual gates.
  EVIDENCE:
  - tickets/tasks/2026-08-28_architecture_docs_foundation_task.md
  IMPACT: The human-facing MRP tranche is unblocked.
  NEXT: Implement the MRP prose and six remaining core diagrams.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T01:16:58Z
  TYPE: MEASURE
  CLAIM: Milestone 2 passed all prose, render, visual, test, link, and diff gates.
  EVIDENCE:
  - tickets/tasks/2026-08-28_architecture_docs_human_mrp_task.md
  IMPACT: The advanced ceiling is unblocked as an additive continuation.
  NEXT: Implement and validate the remaining pages and three diagrams.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T01:32:58Z
  TYPE: MEASURE
  CLAIM: All three milestones and tranche tasks are implemented and validated; the epic
    remains in review until the owner accepts the delivered reader journey.
  EVIDENCE:
  - tickets/tasks/2026-08-28_architecture_docs_foundation_task.md
  - tickets/tasks/2026-08-28_architecture_docs_human_mrp_task.md
  - tickets/tasks/2026-08-28_architecture_docs_advanced_ceiling_task.md
  IMPACT: No implementation work remains inside the accepted scope.
  NEXT: Request owner acceptance, then close/synchronize the epic, stories, tasks, and artifact.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T10:40:22Z
  TYPE: DECISION
  CLAIM: The owner reopened the documentation epic for a new build-asset tranche:
    plan and produce C4, C3, and C2 draw.io-style engineering pictures with Mermaid
    companions inside the packaged system-document lane.
  EVIDENCE:
  - tickets/epics/2026-08-28_architecture_and_design_documentation_epic.md:24-25
  - tickets/epics/2026-08-28_architecture_and_design_documentation_epic.md:166-172
  IMPACT: The prior execution boundary and review-state claim no longer cover the
    requested work; builder integration must be inspected before exact file scope is set.
  NEXT: Read the system-document builder, central build-asset runner, and visual tooling
    contract, then propose the exact drawing inventory and files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T10:44:35Z
  TYPE: FACT
  CLAIM: The central runner already discovers and invokes the system-document builder
    automatically. That builder currently fingerprints and packages only the authored
    Markdown/index pairs into lazy Python payloads; it has no diagram inventory or
    runtime diagram view, and it does not derive architecture pictures from src_graph.
  EVIDENCE:
  - src/melder/_build_assets/_build_asset_runner.py:189-264
  - src/melder/_build_assets/_system_documents/_builder.py:126-189
  - src/melder/_build_assets/_system_documents/_builder.py:471-631
  - src/melder/_build_assets/_system_documents/system_documents.py:1-78
  IMPACT: No runner registration change is needed. The clean extension point is the
    existing system-document builder: ingest authored SVG/Mermaid pairs, fingerprint
    them, emit lazy payload modules, and attach metadata to existing document views.
  NEXT: Route the static three-pair drawing task and request exact-scope confirmation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T11:13:15Z
  TYPE: MEASURE
  CLAIM: The reopened system-document drawing task delivered and validated the exact
    three-pair C4/C3/C2 static drawing inventory without expanding into code or runner changes.
  EVIDENCE:
  - tickets/tasks/2026-08-29_system_document_engineering_drawings_task.md
  IMPACT: The epic is ready for an updated owner walkthrough and acceptance decision.
  NEXT: Ask the owner to accept the drawing task and complete epic closure sync.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T12:20:28Z
  TYPE: MEASURE
  CLAIM: The owner-requested engineering drawings are now published inside
    `architecture_and_design` as a registered, navigable page with exact mirrored assets.
  EVIDENCE:
  - architecture_and_design/05_engineering_drawings/README.md:1-84
  - tickets/tasks/2026-08-29_system_document_engineering_drawings_task.md
  IMPACT: The reopened epic again has no remaining implementation or validation work.
  NEXT: Request updated owner acceptance and perform closure synchronization.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T12:49:34Z
  TYPE: MEASURE
  CLAIM: The engineering-drawings extension now publishes nine pairs, including three
    use-case views and detailed Nexus/Rift, Crystallizer, and MutationResearch flows.
  EVIDENCE:
  - architecture_and_design/05_engineering_drawings/README.md
  - tickets/tasks/2026-08-29_system_document_engineering_drawings_task.md
  IMPACT: The reopened epic again has no remaining implementation or validation work.
  NEXT: Request owner acceptance and perform closure synchronization.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T15:28:39Z
  TYPE: MEASURE
  CLAIM: The engineering-drawings extension now publishes sixteen pairs. The final
    seven add boot/ownership, free-threaded coordination, self-documentation,
    failure/recovery, scoped lifetimes, linked subsystems, and isolated worlds; the
    complete set passed documentation, render, visual, focused-test, and diff gates.
  EVIDENCE:
  - architecture_and_design/05_engineering_drawings/README.md:1-384
  - tickets/tasks/2026-08-29_system_document_engineering_drawings_task.md
  IMPACT: The reopened epic again has no remaining implementation or validation work.
  NEXT: Request owner acceptance and perform closure synchronization.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T15:47:17Z
  TYPE: MEASURE
  CLAIM: The engineering-drawings extension now publishes seventeen pairs and
    opens with a fair DI-container-versus-Melder comparison. The intro preserves
    DI's common baseline while showing Melder's broader runtime-world, governance,
    topology, access, and continuity responsibilities; the full validation gate passed.
  EVIDENCE:
  - architecture_and_design/05_engineering_drawings/README.md:1-409
  - tickets/tasks/2026-08-29_system_document_engineering_drawings_task.md
  IMPACT: The reopened epic again has no remaining implementation or validation work.
  NEXT: Request owner acceptance and perform closure synchronization.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T15:54:50Z
  TYPE: MEASURE
  CLAIM: Owner-requested copy review of the DI comparison is complete. Promotional,
    duplicated, vague, and overloaded phrases were replaced by direct responsibility
    language, and the revised picture passed its focused validation gate.
  EVIDENCE:
  - architecture_and_design/05_engineering_drawings/svg/di_container_vs_melder.svg
  - tickets/tasks/2026-08-29_system_document_engineering_drawings_task.md
  IMPACT: The seventeen-pair set remains complete and returns to owner review.
  NEXT: Request owner acceptance and perform closure synchronization.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: tranche order, cross-story synthesis, and program acceptance.

## Context / Handoff Summary
The public documentation and seventeen-pair engineering-drawing extension are
implemented, validated, owner-accepted, and ready in their completed lanes.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
