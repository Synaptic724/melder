# Epic: General Open Questions

## Metadata
- Epic ID: EPIC-2026-05-03-general-open-questions
- Status: in_progress
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-03T15:00:23Z
- Updated: 2026-05-09T10:31:56Z
- Target Window: 2026-Q2
- Related Program/Initiative: Durable holding lane for important unresolved design questions

## Problem / Opportunity
The system has a growing set of hard questions that are important enough to
keep durable, visible, and explicitly open instead of burying them in chat or
overloaded feature epics.

This epic exists as the general-purpose parking lane for:
- important unresolved design questions
- high-pressure semantic concerns
- ideas that should stay durable until they are reduced into concrete stories
  or implementation tranches

The first active occupant is mutation semantics, but this epic is intentionally
broader than mutation alone.
It now also owns the sandbox-architecture comparison lane between observed
Codex local sandboxing and the planned CommandOps container-first direction.

## MRP Alignment (Most Reasonable Product)
The MRP here is not "finish everything."
The MRP is:
- keep the hardest unresolved design questions explicit
- keep them tied to evidence and active artifacts
- prevent premature closure or false certainty
- preserve a clean place to collect future decisions and tranche work

## Ticket Contract
- ENTRY_GATE: the user explicitly asked for an epic that acts as a placeholder
  for important open questions and ideas, with the current `IMPORTANT_CONSIDERATION`
  artifact tied into it.
- EXECUTION_BOUNDARY: hold unresolved design questions and important ideas
  without forcing premature closure. Current focus: mutation semantics.
- DEPENDENCIES:
  - active artifacts assigned to this epic
  - the relevant source/doc anchors for whichever question is currently active
- EXIT_GATE: this epic should remain open until the user explicitly decides the
  open questions have been sufficiently reduced into concrete finished stories
  or implementation lanes.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` when a proposed solution would
  force premature closure or blur unresolved questions into fake
  certainty.

## Goals (Outcomes)
- Preserve one high-priority home for important open questions and ideas.
- Keep hard semantic concerns visible as first-class design problems.
- Tie future decisions back to durable artifacts instead of transient chat.
- Prevent these questions from being lost while other work proceeds.

## Non-Goals (Explicit Exclusions)
- Finalize every open question immediately.
- Pretend unresolved semantics are settled.
- Close this epic through normal "done" mechanics while it is still serving as
  a live holding place for unresolved important questions.

## Scope Boundaries
- In scope:
  - important unresolved design questions
  - future ideas worth keeping durable
- current mutation lineage/version concerns
- sandbox-backend philosophy and deployment-tier direction
- important open questions and future design ideas
- Out of scope:
  - pretending the current active question is the only future occupant
  - forcing final answers before mutation is ready

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a standing p0 epic that
  keeps important open questions and ideas durable and open, with mutation
  semantics as the current first occupant.

## Success Metrics
- Important open questions are no longer only in chat.
- `IMPORTANT_CONSIDERATION` has a dedicated owning epic.
- Future design notes can accumulate here without being mistaken for solved work.
- The epic remains open and visible as long as it is still serving as the
  durable home for unresolved important questions.

## Requirements (Functional + Non-Functional)
- Functional:
  - own the currently assigned important-question artifacts
  - keep important open questions explicit
  - collect future decisions/ideas without collapsing them into solved design
- Non-functional:
  - stay durable and easy to reread
  - remain high-priority
  - avoid false closure pressure

## Constraints / Assumptions
- MutationResearch is unfinished and is the first active question set here.
- Some of the hardest semantics in the system are still not proven in the live runtime.
- This epic is intentionally a placeholder/holding structure and should be
  treated differently from a normal finishable feature epic.

## Dependencies / External References
- `codex/context_compass/artifacts/IMPORTANT_CONSIDERATION.md`
- `codex/context_compass/artifacts/2026-05-09_mutation_research_philosophy.md`
- `codex/context_compass/artifacts/2026-05-06_codex_cli_native_sandbox_vs_commandops_container_sandbox_philosophy.md`
- `codex/context_compass/artifacts/2026-05-10_mutation_branch_type_enforcement.md`
- active source/doc anchors referenced by the current question set

## Milestones (Track Progress)
- [ ] Milestone 1: keep the active open-question set durable and current
- [ ] Milestone 2: reduce major questions into explicit future stories or design cuts without closing the holding epic

## Stories (Required to Complete)
- [ ] Story: define mutation fork semantics when the system is ready
- [ ] Story: define lane/head/index projection and merge semantics when the system is ready
- [ ] Story: define non-active spell link/meld rules when the system is ready
- [ ] Story: define conduit snapshot mutation-manifest reload semantics when the system is ready
- [ ] Story: stage future important questions here when they need a durable home
- [ ] Story: reduce the sandbox-backend philosophy into concrete CommandOps execution-backend tasks later

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: keep active important-question artifacts updated when discussions materially change
- [ ] Task: split proven questions into separate implementation-facing stories later
- [ ] Task: verify Ticket Microcycle enforcement across future story/task work spawned from this holding epic
- [ ] Task: keep the sandbox-design artifact current while the CommandOps backend direction stays open

## Acceptance Criteria (Epic Done)
- This epic is intentionally not a normal "done when feature shipped" epic.
- It should not be closed simply because some nearby work landed.
- It is only eligible for closure after explicit user confirmation that it is no
  longer needed as a placeholder for important mutation questions and ideas.

## Risks / Mitigations
- Risk: this becomes a junk drawer with no structure.
  Mitigation: keep notes focused on one active question cluster at a time.
- Risk: someone later closes it mechanically because it looks like a normal epic.
  Mitigation: state explicitly in multiple sections that it is a standing
  placeholder and should remain open.

## Applicable Anti-Patterns
- [ ] No epic-state transition without evidence-backed scope.
- [ ] No fake closure while important open questions are still active.
- [ ] No treating unresolved semantics as solved implementation rules.

## Validation / Test Approach
- Design-only placeholder epic.
- Validation is durability and clarity of the open-question record.

## Rollout / Adoption Plan
- Keep this open while important question clusters are still in flux.
- Spawn focused stories/tasks from it when questions become tractable.
- Preserve this as the durable parking lot for unresolved important issues.

## Open Questions
- Current active open questions:
  - When does a mutation branch remain within one lineage versus becoming a new lineage?
  - Can non-active spell versions be linked but intentionally not melded?
  - What exactly should happen when another conduit wants to "work on" a spell
    under active mutation?
  - When do cross-conduit semantics require `mutation_fork` rather than direct
    transfer or direct reuse?
  - Should MutationResearch optionally enforce shared branch-type
    classification across module and spell mutation branches, while still
    allowing freeform branch names?
  - Which parts of Codex local native sandboxing are worth reproducing
    semantically inside a container/pod-first CommandOps execution model, and
    which parts should remain intentionally different because our first hard
    boundary is the worker container rather than the host process?

## Decision Log
- 2026-05-03T15:00:23Z: Opened as a standing p0 epic to hold important
  unresolved design questions and ideas without pretending they are solved.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/IMPORTANT_CONSIDERATION.md
  - artifacts/2026-05-09_mutation_research_philosophy.md
  - artifacts/2026-05-06_codex_cli_native_sandbox_vs_commandops_container_sandbox_philosophy.md
  - artifacts/2026-05-10_mutation_branch_type_enforcement.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: explicit user-directed closure only

## Notes
- DATETIME: 2026-05-03T15:00:23Z
  TYPE: FACT
  CLAIM: This epic is intentionally a placeholder for important open questions
    and ideas in general, with mutation semantics as the current first active
    occupant. It should remain open as a priority lane until the user
    explicitly decides it is no longer needed as a holding epic.
  EVIDENCE:
  - user_instruction: "epic should be called open questions in general because we'll add more things to it"
  IMPACT: Later work should treat this as a durable holding structure, not a
    normal feature epic that gets closed as soon as adjacent implementation
    work lands.
  NEXT: keep the current mutation artifact and any future important-question
    artifacts tied to this epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-06T10:27:13Z
  TYPE: FACT
  CLAIM: This holding epic now also owns the sandbox-architecture comparison
    lane. The new artifact is not a product-copy summary; it is a source-backed
    comparison between Codex local native sandboxing and the planned
    CommandOps container/pod-first worker model. It keeps one durable answer to
    why the planned design should use Docker Compose for general users and
    K3s/Kubernetes for business and enterprise instead of copying Codex's
    host-native process sandbox primitive directly.
  EVIDENCE:
  - artifacts/2026-05-06_codex_cli_native_sandbox_vs_commandops_container_sandbox_philosophy.md:1-220
  - <local-path>/Downloads/codex-main/codex-rs/README.md
  - <local-path>/Downloads/codex-main/codex-rs/linux-sandbox/README.md
  - <local-path>/Downloads/codex-main/codex-rs/shell-escalation/README.md
  - <local-path>/Downloads/codex-main/codex-rs/windows-sandbox-rs/src/lib.rs
  IMPACT: The epic now has two distinct important-question occupants:
    mutation semantics and sandbox-backend philosophy. Future CommandOps
    sandbox tasks can point here instead of re-litigating the comparison in chat.
  NEXT: keep the sandbox artifact current until the execution-backend
    architecture hardens into concrete CommandOps implementation tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-09T10:31:56Z
  TYPE: FACT
  CLAIM: The open-questions lane now also has a broader MutationResearch
    philosophy artifact. `IMPORTANT_CONSIDERATION.md` remains the narrow
    pressure file for fork/meld/link semantics, while the new artifact captures
    the larger lane/head/index snapshot-merge structure, structural diffs,
    surgical mutation, prune/collapse, and runtime recomposition direction.
  EVIDENCE:
  - artifacts/2026-05-09_mutation_research_philosophy.md
  - artifacts/IMPORTANT_CONSIDERATION.md
  - artifacts/Archived/2026-03-15_aethericrift_engineer_context_bundle/MutationResearch/WORKING_MODEL.md
  IMPACT: Future mutation design work can now separate the broad forward model
    from the narrower unresolved pressure points instead of overloading one
    artifact or relying on archived docs only.
  NEXT: keep the broader mutation artifact current while the lane/head/index
    model remains an active open-question surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-10T09:19:43Z
  TYPE: FACT
  CLAIM: The open-questions lane now also has a narrow branch-labeling artifact
    for MutationResearch. It captures one optional policy surface:
    `branch_type_enforcement`, where branch names can stay flexible while
    module mutation and spell mutation share one enum-based branch-type
    vocabulary for grouped transaction labeling and validation.
  EVIDENCE:
  - artifacts/2026-05-10_mutation_branch_type_enforcement.md:1-186
  - user_instruction: "another mutation configuration item called branch_type_enforcement"
  - user_instruction: "we can use enum too"
  IMPACT: Future mutation work now has a separate durable reference for branch
    naming/classification policy instead of forcing that idea into the broader
    mutation philosophy artifact.
  NEXT: decide later whether this stays as an open-questions policy idea or
    reduces into one narrower MutationResearch configuration story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: important active question clusters, transfer concerns, branch/fork
  semantics, and future ideas that must stay visible.
- Add notes when the active question set materially changes or a new pressure point is identified.
- Keep notes append-only and preserve UNKNOWN-first discipline.

## Context / Handoff Summary
This epic is a standing p0 holding place for important open questions and ideas
in general. It is intentionally open and should not be closed through ordinary
epic completion habits while it is still serving as the durable home for
unresolved high-priority design concerns.
