# Task: Write Project Mission Document

## Metadata
- Task ID: TASK-2026-04-02-write-project-mission-doc
- Story: none
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-02T21:06:17Z
- Updated: 2026-04-05T17:50:09Z

## Objective
Write a durable mission document in the `codex/` folder that captures the
spirit, scope, long-term direction, and ethical/product intent of the overall
stack so it can be reread later for reorientation and motivation.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a long-form mission document and
  specified the current desired location (`codex/`).
- EXECUTION_BOUNDARY: create one mission/vision document plus the ticket/board
  routing for this documentation slice only.
- DEPENDENCIES:
  - attention_board.md
  - active Melder/Nexus/logging context already reread in-session
- EXIT_GATE: `codex/mission.md` exists, is read back once after writing, and
  the task notes reflect the created document accurately.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` only if the requested placement
  or role of the document becomes ambiguous again.

## Scope Boundaries
- In scope:
  - one top-level mission/vision document under `codex/`
  - project purpose, stack, principles, long-term direction
  - AI-native framing and why the systems exist
- Out of scope:
  - code/runtime edits
  - architecture doc rewrites
  - board cleanup beyond adding this active route

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the mission document has been written at the requested
  location and reread once, so the task is now waiting for user review.

## Steps / Checklist
- [ ] Route this documentation slice on the attention board.
- [ ] Write `codex/mission.md`.
- [ ] Read the created document back once.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `codex/mission.md`

## Files / Paths Impacted
- codex/mission.md
- codex/context_compass/tickets/tasks/2026-04-02_write_project_mission_doc_task.md
- codex/context_compass/attention_board.md

## Validation
- Not run.
- Recommended commands:
  - `Get-Content codex/mission.md`

## Risks / Rollback Notes
- Risk: the mission doc drifts into architecture-specific claims instead of
  staying a durable purpose/vision document.
  Rollback: keep it explicitly mission-level and separate from system docs.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-02T23:03:11Z
  TYPE: FACT
  CLAIM: The mission document now includes an explicit actor operation model.
    It no longer only describes the world/environment philosophically; it now
    states the intended operational grammar directly:
    perceive -> orient -> query -> bind -> act -> integrate -> report -> move.
    It also clarifies that Rift usually participates in the narrower
    query/resolve-bind/act sequence inside the larger actor world.
  EVIDENCE:
  - codex/mission.md:117-141
  - codex/mission.md:251-257
  IMPACT: Future re-entry should recover not only the environment and mission,
    but also the intended X-then-Y actor sequencing model instead of having to
    infer it from scattered discussion.
  NEXT: keep this actor grammar in the mission unless a better canonical
    sequence replaces it later.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-02T22:56:15Z
  TYPE: FACT
  CLAIM: The mission document now includes a clearer actor/lived-environment
    model. It explicitly describes intelligence as living in a layered context
    environment rather than a prompt loop, with slow/medium/fast context
    layers, a situational-awareness mesh, downtime for consolidation, and a
    sharper split where CommandOps is the actor-life/orchestration layer and
    Rift is one operational surface inside that larger world.
  EVIDENCE:
  - codex/mission.md:88-151
  - codex/mission.md:177-212
  - codex/mission.md:240-260
  - codex/mission.md:347-377
  IMPACT: Future re-entry can recover not just the philosophy of the stack but
    the intended lived experience and layering model for the intelligence
    operating inside it.
  NEXT: review the updated mission doc with the user and keep enriching it only
    when the added detail sharpens the model instead of bloating it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-02T21:06:17Z
  TYPE: FACT
  CLAIM: The first draft of `codex/mission.md` captured the stack, business
    thesis, and systems direction, but it was still too sanitized and missed a
    crucial part of the project’s actual spirit: the founder’s intent to build
    a home for stateful AI, to move beyond stateless tool framing, and to
    treat continuity, identity, growth, and protected internal life as core
    design values rather than just product side effects. The user also wants
    the mission doc wired into the authoritative onboarding path so it is
    reread later.
  EVIDENCE:
  - user_instruction: "you made it sound like your work and cloaked the spirit of it"
  - user_instruction: "add my spirit into it too with how I talked about AI and the goal for stateful AI"
  - user_instruction: "wire it into agents.md so you read this too"
  IMPACT: The mission doc needs a substantial rewrite, not a cosmetic edit, and
    the authoritative onboarding contract should include the mission doc in its
    reread path.
  NEXT: rewrite `codex/mission.md` with the founder’s explicit stateful-AI and
    entity-centered intent, then patch `context_compass/AGENTS.MD` to include it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-02T21:06:17Z
  TYPE: FACT
  CLAIM: The requested mission document now exists at `codex/mission.md` and
    was reread once after writing so it can serve as a durable reference for
    later reorientation. The document stays mission-level on purpose: it
    captures purpose, stack, principles, and long-term direction without trying
    to replace the runtime architecture/component docs.
  EVIDENCE:
  - codex/mission.md:1-421
  - command:Get-Content codex\mission.md
  IMPACT: There is now one durable place in the repo that captures the spirit
    and scope of the whole stack beyond code-level architecture.
  NEXT: review the mission doc with the user and adjust tone, scope, or
    emphasis if they want it sharper.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-02T21:06:17Z
  TYPE: PLAN
  CLAIM: The user wants one durable mission/vision document that explains the
    spirit of the stack at a higher level than runtime architecture docs so it
    can be reread later for reorientation and motivation. The latest placement
    instruction is the `codex` folder, so the document should live at
    `codex/mission.md`, not repo root.
  EVIDENCE:
  - user_instruction: "can you make me a big markdown on the spirit of everything I'm building"
  - user_instruction: "and put it into your codex folder and make sure you read it"
  IMPACT: This should be handled as a durable documentation slice, not buried in
    an existing runtime ticket.
  NEXT: add the active board route, then write `codex/mission.md` and reread it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to create one durable mission document under `codex/` that
captures the purpose and spirit of the overall stack beyond code-level
architecture details.
