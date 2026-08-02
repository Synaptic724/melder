# Epic: Userland Ingest And Persistence Subsystem

## Metadata
- Epic ID: EPIC-2026-04-07-userland-ingest-and-persistence-subsystem
- Status: draft
- Owner: codex
- Priority: p0
- Created: 2026-04-07T23:04:26Z
- Updated: 2026-04-07T23:04:26Z
- Target Window: 2026-Q2
- Related Program/Initiative: Melder userland admission, persistence, and code bundle safety

## Problem / Opportunity
Melder can already expose a rich runtime world to agents through the viewer,
AST introspection, and top-level system-doc objects. The next missing major
subsystem is how user code actually enters that world safely and how saved
objects/code bundles are represented over time.

This is not a small helper feature. It is a first-class subsystem for:
- ingesting user-provided Python and JSON inputs
- discovering explicitly loadable objects
- analyzing dependency closure around those objects
- deciding whether a target is admissible into Melder
- rejecting incomplete or unsafe submissions with exact diagnostics
- persisting accepted code bundles plus structured metadata for later reload

Without this subsystem, Melder can inspect and reason about runtime objects,
but it does not yet have a durable, governed intake path for userland code.

## MRP Alignment (Most Reasonable Product)
The most reasonable product here is not naive save/load and not magical object
pickup. The subsystem should be honest and strict:
- if a target object/module/package has a complete enough dependency closure,
  accept it and persist it
- if it does not, reject it and tell the user exactly what files, symbols, or
  runtime assumptions are missing

The MRP is therefore an admissibility-first subsystem that protects Melder from
pretending it can safely ingest code when the dependency story is incomplete.

## Ticket Contract
- ENTRY_GATE: the viewer/runtime proving ground is useful enough that the next
  large architecture lane can shift to userland ingest and persistence.
- EXECUTION_BOUNDARY: design and later implementation planning for the full
  userland ingest/admission/persistence subsystem.
- DEPENDENCIES:
  - tickets/tasks/2026-04-06_implement_actionable_viewer_profile_tool_compositions.md
  - tickets/epics/2026-04-07_agent_tooling_frame_and_tool_organization_epic.md
  - src/melder/utilities/helpers/class_surface_ast_describer.py
  - src/melder/__architecture__.py
  - src/melder/__components__.py
  - src/melder/__graph_network__.py
  - src/melder/__graph_details__.py
  - tickets/artifacts/2026-04-07_userland_ingest_and_persistence_subsystem_design.md
- EXIT_GATE: the subsystem has an accepted architecture for intake,
  dependency-capture, admission policy, persistence bundles, and loader
  integration boundaries.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if persistence scope expands
  beyond object/module/package closure into unsupported generalized packaging.

## Goals (Outcomes)
- Define the admissibility contract for user-supplied code and JSON.
- Define how Melder discovers explicitly loadable userland objects.
- Define how dependency closure is computed and classified.
- Define acceptance/rejection diagnostics for incomplete submissions.
- Define the persisted bundle/manifests used for later reload.
- Define where decorators, loader contracts, and registry integration belong.

## Non-Goals (Explicit Exclusions)
- Immediate full implementation of the subsystem.
- Mutation/version-promotion mechanics.
- Replacing user source with a JSON-only behavioral representation.
- Becoming a general-purpose IDE.

## Scope Boundaries
- In scope:
  - userland Python/JSON intake contract
  - dependency closure discovery and capture levels
  - admissibility states and diagnostics
  - persistence bundle shape
  - load/reload registration boundaries
  - decorator or explicit marker requirements for loadable objects
- Out of scope:
  - live IDE/editor replacement
  - arbitrary package-manager emulation
  - mutation/change-control semantics
  - broad graph-runtime work beyond direct dependency representation

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: created as a future major subsystem lane so ingest and
  persistence architecture is not lost in chat-only discussion.

## Success Metrics
- One accepted admissibility model with explicit rejection states.
- One accepted dependency-capture model with clear escalation from object to
  module to package capture.
- One accepted persisted bundle/manifest contract for reload.
- One accepted subsystem decomposition for implementation work.

## Requirements (Functional + Non-Functional)
- Functional:
  - intake Python files and structured JSON requests
  - discover explicitly loadable targets
  - analyze dependency closure around selected targets
  - classify capture as object-safe, module-required, package-required, or rejected
  - emit exact missing-file, missing-symbol, and dynamic-unknown diagnostics
  - persist accepted bundles plus manifest metadata
  - support later reload/registration through a governed loader path
- Non-functional:
  - never pretend an incomplete submission is safely ingestable
  - keep diagnostics deterministic and user-readable
  - preserve source-of-truth separation between code and metadata
  - stay explicit about dynamic/unknown dependency edges

## Constraints / Assumptions
- Melder is not trying to replace a user IDE.
- User code will likely mark loadable objects through explicit decorators or an
  equally explicit contract rather than loose heuristic discovery.
- Python source remains the canonical behavioral source.
- Structured metadata/manifests exist alongside source instead of replacing it.
- Dynamic dependency tricks must be surfaced honestly as unknowns, not hidden.

## Dependencies / External References
- Active viewer/runtime lane proving out agent-native inspection surfaces.
- Later tool-organization decisions may influence where admission/persistence
  tools are exposed, but should not block the subsystem design itself.

## Milestones (Track Progress)
- [ ] Milestone 1: Define intake and admissibility architecture
- [ ] Milestone 2: Define dependency-capture and diagnostics model
- [ ] Milestone 3: Define persistence bundle and reload contract
- [ ] Milestone 4: Stage implementation stories/tasks

## Stories (Required to Complete)
- [ ] Story: STORY-TBD - userland intake and admissibility design
- [ ] Story: STORY-TBD - dependency-closure and diagnostics design
- [ ] Story: STORY-TBD - persistence bundle and loader integration design

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: create the first design story when this lane is activated
- [ ] Task: stage bundle-schema and diagnostic-shape artifacts if implementation begins
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The subsystem architecture is explicit enough that implementation can begin
  without inventing the ingest/persistence model during coding.
- Admission, dependency-capture, and persistence boundaries are accepted.
- The persisted bundle/manifest shape has one accepted direction.

## Risks / Mitigations
- Risk: object-only persistence lies about dependency completeness.
  Mitigation: require capture-level classification and escalate to module or
  package capture when dependency closure demands it.
- Risk: dynamic Python edges are hidden and later explode during reload.
  Mitigation: surface unresolved dynamic edges explicitly and block or flag
  persistence based on policy.
- Risk: the subsystem grows into an accidental package manager or IDE.
  Mitigation: keep scope on admission, dependency closure, and governed
  persistence only.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Discovery validation only until implementation is activated.
- Later implementation should carry deep unit/component/integration coverage for:
  - file intake
  - dependency resolution
  - rejection diagnostics
  - manifest generation
  - reload validation

## Rollout / Adoption Plan
- Defer until the lane is explicitly activated.
- Start with explicit decorator-marked targets and conservative closure rules.
- Widen only after the first accepted closure and persistence model is stable.

## Open Questions
- What exact decorator/marker contract should userland objects use?
- When should the system escalate from object capture to module capture?
- What exact unresolved-dynamic policy should block persistence versus merely
  warn?
- How much package-level closure should be supported in the first real cut?
- What part of the subsystem belongs in Rift tooling versus deeper runtime
  services?

## Decision Log
- Created after the userland save/load discussion clarified that this is not a
  helper feature but a full subsystem covering intake, admissibility,
  dependency closure, and persisted bundles.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - tickets/artifacts/2026-04-07_userland_ingest_and_persistence_subsystem_design.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the subsystem is implemented and either promoted
  into canonical documentation or intentionally retired.

## Notes
- DATETIME: 2026-04-07T23:04:26Z
  TYPE: PLAN
  CLAIM: Melder needs a first-class subsystem for userland code intake,
    dependency-closure analysis, admissibility decisions, and persisted bundle
    creation. This epic exists so that architecture and later implementation
    work happen intentionally instead of being re-derived from memory.
  EVIDENCE:
  - user_instruction: "make an EPic for this too and describe it very well, and make an artifact for it date it to today"
  - user_instruction: "like we can map dependencies too"
  IMPACT: The ingest/persistence subsystem now has a durable planning home and
    one detailed companion artifact for later implementation discovery.
  NEXT: leave this epic dormant until you explicitly activate the subsystem
    design or implementation lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This is a future major subsystem lane. The current runtime already supports
viewer-based inspection and AST-guided understanding, but it still lacks the
governed path by which userland code is admitted, dependency-validated, and
persisted for later reload. This epic preserves that next architecture problem
as a first-class lane.
