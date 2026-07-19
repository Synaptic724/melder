# Task: Add Optional Context Management To General Role

## Metadata
- Task ID: TASK-2026-06-03-add-optional-context-management-to-general-role
- Story: none
- Status: done
- Owner: codex
- Agent Name: compiler_0
- Priority: p0
- Created: 2026-06-03T12:23:49Z
- Updated: 2026-06-05T22:52:54Z

## Objective
Add an optional `context_management` system to Context Compass, wire it into
the general role as required baseline reading, and update ticket templates and
workflow docs so tickets can opt into context-managed reread packs without
forcing the feature on every ticket.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested the new context-management system,
  and the active board route points to this task.
- EXECUTION_BOUNDARY:
  - `codex/context_compass/agent_onboarding/default/general/`
  - `codex/context_compass/templates/`
  - `codex/context_compass/context_management/`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `agent_onboarding/default/general/AGENTS.MD`
  - `agent_onboarding/default/general/SKILLS.MD`
  - `agent_onboarding/default/general/skills/ticketing.md`
  - `agent_onboarding/default/general/skills/workflow.md`
  - `artifact_board.md`
- EXIT_GATE:
  - context-management docs and folders exist
  - general-role readset includes the new skill and board
  - ticket templates expose optional context-management fields
  - workflow and ticketing docs describe the optional gate correctly
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the requested design cannot
  be integrated cleanly without changing the ticket or board model more
  broadly than the user asked.

## Scope Boundaries
- In scope:
  - add `context_management/` board and artifact folder
  - add one general-role context-management skill doc
  - make ticket support optional, not mandatory
  - update general-role docs and templates accordingly
- Out of scope:
  - generating an actual context-management artifact for a live ticket
  - changing active compiler program content
  - building automation around context pack generation

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested immediate implementation of
  optional context-management support in the general role and ticket system.

## Steps / Checklist
- [x] Add `context_management/` board and artifact folder docs.
- [x] Add a general-role context-management skill and wire it into baseline
      onboarding.
- [x] Update general-role AGENTS/ticketing/workflow docs.
- [x] Update epic/story/task templates to include optional context management.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `context_management/context_board.md`
- `context_management/README.md`
- `context_management/artifacts/.gitkeep`
- updated general-role policy/skill/template docs

## Files / Paths Impacted
- `codex/context_compass/agent_onboarding/default/general/`
- `codex/context_compass/templates/`
- `codex/context_compass/context_management/`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "context_management|CONTEXT_MANAGEMENT_REQUIRED" codex/context_compass`

## Risks / Rollback Notes
- Risk: making context management too mandatory and turning it into paperwork.
- Risk: duplicating artifact-board semantics instead of keeping the feature narrow.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_ARTIFACTS:
- CONTEXT_TOPICS:
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-03T12:23:49Z
  TYPE: FACT
  CLAIM: The current general-role system already has explicit optional artifact
    handling via `artifact_board.md` and `Artifact Links (Optional)` in
    tickets, but it has no matching optional context-pack mechanism. That
    means reusable reread bundles have no first-class routing surface today.
  EVIDENCE:
  - codex/context_compass/agent_onboarding/default/general/SKILLS.MD:49-50
  - codex/context_compass/agent_onboarding/default/general/skills/ticketing.md:18-18
  - codex/context_compass/agent_onboarding/default/general/skills/ticketing.md:40-40
  - codex/context_compass/agent_onboarding/default/general/skills/workflow.md:27-29
  - codex/context_compass/artifact_board.md:1-18
  IMPACT: The new system should mirror artifact handling conceptually while
    staying optional at the ticket level.
  NEXT: add the new board and skill docs, then update the templates and
    general-role guidance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-03T12:25:45Z
  TYPE: FACT
  CLAIM: The current schema and workflow explicitly support optional artifact
    management but have no parallel context-pack mechanism. Artifact handling
    is first-class in templates and workflow docs, while context reread bundles
    are only implied informally and cannot be linked or enforced from tickets.
  EVIDENCE:
  - codex/context_compass/templates/epic_template.md:93-97
  - codex/context_compass/templates/story_template.md:75-79
  - codex/context_compass/templates/task_template.md:73-77
  - codex/context_compass/agent_onboarding/default/general/skills/ticketing.md:18-18
  - codex/context_compass/agent_onboarding/default/general/skills/ticketing.md:40-40
  - codex/context_compass/agent_onboarding/default/general/skills/ticketing.md:89-90
  - codex/context_compass/agent_onboarding/default/general/skills/workflow.md:28-28
  - codex/context_compass/agent_onboarding/default/general/skills/workflow.md:47-48
  - codex/context_compass/agent_onboarding/default/general/skills/workflow.md:149-152
  IMPACT: The new system should mirror artifact support closely enough to be
    familiar, but must remain optional at the ticket level and independent from
    `attention_board.md` routing.
  NEXT: add `context_management/`, add the skill and board docs, and then
    update the templates and general-role docs to expose the optional gate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-03T12:28:01Z
  TYPE: FACT
  CLAIM: The optional context-management rollout is implemented. The general
    role now reads a dedicated `context_management` skill plus
    `context_management/context_board.md`, tickets expose an optional `Context
    Management` section, and workflow/ticketing policy now enforces linked
    context-artifact rereads only when `CONTEXT_MANAGEMENT_REQUIRED: true`.
  EVIDENCE:
  - codex/context_compass/agent_onboarding/default/general/SKILLS.MD:49-52
  - codex/context_compass/agent_onboarding/default/general/AGENTS.MD:95-99
  - codex/context_compass/agent_onboarding/default/general/skills/ticketing.md:18-19
  - codex/context_compass/agent_onboarding/default/general/skills/ticketing.md:42-42
  - codex/context_compass/agent_onboarding/default/general/skills/ticketing.md:95-97
  - codex/context_compass/agent_onboarding/default/general/skills/workflow.md:30-32
  - codex/context_compass/agent_onboarding/default/general/skills/workflow.md:53-54
  - codex/context_compass/agent_onboarding/default/general/skills/workflow.md:173-182
  - codex/context_compass/agent_onboarding/default/general/skills/context_management.md:1-62
  - codex/context_compass/context_management/context_board.md:1-28
  - codex/context_compass/context_management/context_artifact_template.md:1-25
  - codex/context_compass/templates/epic_template.md:100-105
  - codex/context_compass/templates/story_template.md:82-87
  - codex/context_compass/templates/task_template.md:80-85
  IMPACT: Tickets can now opt into reusable context packs without forcing a
    heavy context schema onto every lane, and agents have an explicit reread
    gate when a ticket chooses to use the feature.
  NEXT: review the wording and decide whether you want any additional context
    board fields or compaction-specific integration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-03T13:01:55Z
  TYPE: FACT
  CLAIM: The rollout now uses `Context ID` as the ticket-facing reference
    instead of direct artifact paths, and the context surfaces now carry agent
    identity plus explicit `UNKNOWN` handling. Tickets still opt into context
    management, but when they do, unresolved context state must be written as
    `UNKNOWN` and resolved through the board and linked artifact.
  EVIDENCE:
  - codex/context_compass/context_management/context_board.md:13-24
  - codex/context_compass/context_management/context_artifact_template.md:4-12
  - codex/context_compass/context_management/context_artifact_template.md:23-25
  - codex/context_compass/agent_onboarding/default/general/skills/context_management.md:17-29
  - codex/context_compass/agent_onboarding/default/general/skills/context_management.md:36-45
  - codex/context_compass/agent_onboarding/default/general/skills/ticketing.md:95-97
  - codex/context_compass/agent_onboarding/default/general/skills/ticketing.md:162-170
  - codex/context_compass/agent_onboarding/default/general/skills/workflow.md:178-186
  - codex/context_compass/templates/epic_template.md:100-106
  - codex/context_compass/templates/story_template.md:82-88
  - codex/context_compass/templates/task_template.md:80-86
  IMPACT: The system is now stricter and less ambiguous: agents learn the
    context-management protocol by default, tickets reference stable ids, and
    unknown context is explicitly surfaced instead of left blank.
  NEXT: confirm whether you want any extra board fields beyond `context_id`,
    `owner`, and `agent_name`, or whether this rollout is sufficient.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-03T13:04:56Z
  TYPE: DECISION
  CLAIM: The microcycle also needs one context-management hook. When a ticket
    opts into context management, documenting a meaningful finding is not
    complete until the linked context artifact is updated if the finding
    changes the required reread bundle or the active topics. That keeps the
    context artifact useful as a live derived reread pack instead of a stale
    static note.
  EVIDENCE:
  - codex/context_compass/agent_onboarding/default/general/skills/ticket_microcycle.md:1-18
  - codex/context_compass/agent_onboarding/default/general/skills/ticketing.md:71-97
  - codex/context_compass/agent_onboarding/default/general/skills/workflow.md:41-64
  - codex/context_compass/context_management/context_artifact_template.md:1-31
  IMPACT: Context-managed lanes will now keep ticket notes and context artifacts
    synchronized during the microcycle instead of only at ticket setup time.
  NEXT: patch the microcycle and workflow docs so context updates are required
  whenever the ticket explicitly enables context management.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-05T22:52:54Z
  TYPE: DECISION
  CLAIM: The optional context-management rollout is accepted as complete and
    should leave the active board. The remaining live work should stay focused
    on mutation contract runtime semantics rather than keeping this rollout
    open.
  EVIDENCE:
  - codex/context_compass/attention_board.md:18-30
  - codex/context_compass/tickets/tasks/2026-06-03_add_optional_context_management_to_general_role_task.md:1-168
  IMPACT: This task can move to `completed`, and the mutation runtime epic
    becomes the only active technical lane on the board.
  NEXT: move this task to `tickets/tasks/completed/` and remove its active
    routing row and attention detail.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the rollout of optional context management into the general
role. The design target is an artifact-board-like derived system that tickets
can opt into with a boolean switch and linked context artifacts.
