# Task: Add Codex and GPT Context Compass reminder language

## Metadata
- Task ID: TASK-2026-07-01-add-codex-gpt-context-compass-reminder-language
- Story: none
- Status: closed (orphan sweep 2026-07-11, melder_0, owner-directed:
  codex_0 does not exist; DELIVERED-VERIFIED - the Codex/GPT
  ReminderDirective sections exist in AGENTS.MD, attention_board.md,
  artifact_board.md AND mailbox_board.md, all read in full this
  session; nothing remains)
- Owner: codex
- Agent Name: codex_0 (closed by melder_0)
- Priority: p2
- Created: 2026-07-01T23:02:12Z
- Updated: 2026-07-01T23:02:12Z

## Objective
Add Codex/GPT-specific reminder language to the existing Context Compass
tracking directives so the repository explicitly covers OpenAI/Codex runtime
nudges in the same way it already covers Claude/Anthropic ones.

## Ticket Contract
- ENTRY_GATE: current reminder locations are read and the wording change stays
  additive.
- EXECUTION_BOUNDARY: `codex/context_compass/AGENTS.MD`,
  `codex/context_compass/attention_board.md`, and
  `codex/context_compass/artifact_board.md` only.
- DEPENDENCIES: none.
- EXIT_GATE: all three reminder locations include a Codex/GPT companion
  section below the existing Claude-targeted text and no unrelated content is
  changed.
- FAILURE_ESCALATION: raise `BLOCKER` if the three files cannot be updated
  safely.

## Scope Boundaries
- In scope:
  - additive reminder language for Codex / GPT / OpenAI agent runtimes
  - preserving the existing Claude / Anthropic text
- Out of scope:
  - changing broader execution policy
  - changing unrelated board rows, artifacts, or tickets

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: user explicitly requested Codex/GPT-inclusive reminder
  language in the three Context Compass reminder locations.

## Steps / Checklist
- [ ] Update `AGENTS.MD` with additive Codex/GPT applicability language.
- [ ] Update `attention_board.md` with a Codex/GPT reminder section below the
      existing Claude-targeted reminder.
- [ ] Update `artifact_board.md` with the same Codex/GPT reminder section.
- [ ] Record outcome and keep the change scope additive only.

## Deliverables
- Codex/GPT-inclusive reminder language in the three requested files.

## Files / Paths Impacted
- `codex/context_compass/AGENTS.MD`
- `codex/context_compass/attention_board.md`
- `codex/context_compass/artifact_board.md`

## Validation
- Not run.
- Recommended commands:
  - `git diff -- codex/context_compass/AGENTS.MD codex/context_compass/attention_board.md codex/context_compass/artifact_board.md`

## Risks / Rollback Notes
- Keep the wording additive so the existing Claude/Anthropic guidance remains
  intact and readable.

## Applicable Anti-Patterns
- [ ] No unrelated reminder rewrites.
- [ ] No non-additive policy changes.
- [ ] No edits outside the three requested files.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Validation status recorded
- [ ] Applicable anti-pattern checks are clear
- [ ] Acceptance criteria reviewed with user and confirmed

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: exact reminder locations changed and why.

## Notes
- DATETIME: 2026-07-01T23:02:12Z
  TYPE: FACT
  CLAIM: The existing reminder language explicitly targets Claude /
    Anthropic runtimes; the user asked for an additive Codex/GPT companion
    section in `AGENTS.MD`, `attention_board.md`, and `artifact_board.md`.
  EVIDENCE:
  - `codex/context_compass/AGENTS.MD`
  - `codex/context_compass/attention_board.md`
  - `codex/context_compass/artifact_board.md`
  IMPACT: Makes the reminder text explicitly inclusive of Codex/GPT runtime
    nudges without changing the underlying Context Compass policy.
  NEXT: Patch the three reminder locations additively.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Additive documentation task only: extend the existing Context Compass reminder
language so it explicitly covers Codex/GPT/OpenAI runtime nudges alongside the
existing Claude/Anthropic wording.