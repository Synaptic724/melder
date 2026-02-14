# Context Compaction Policy

## Purpose
Ensure continuity and minimize lost context when a session is compacted or handed off.

## External Memory Priority
- Repository artifacts are the source of truth for durable context.
- `attention_board.md` is the canonical active-attention state and is mandatory
  during active work.
- Prefer empty compaction summaries when allowed by platform/runtime.
- It is acceptable to save no compaction summary at all when allowed; rely on
  `attention_board.md` and active tickets as the durable state.
- If empty summaries are not allowed, write only minimal pointer summaries:
  - high-level code-change outcomes (no low-level replay)
  - policy/regulation anchor paths that must be re-read
  - active ticket path(s)
  - changed file path(s)
  - next immediate action
- Avoid narrative replay; keep state externalized to files.

## Required Review Set
Before compaction, review these files in order:
- `AGENTS.MD`
- `agent_onboarding/agent/general/skills/compaction_requirements.md`
- `SKILLS.MD`
- `WORKFLOW.md`
- `README.md`
- `architecture/README.md`
- `architecture/src_architecture.md`
- `architecture/tests_architecture.md`
- `components/README.md`
- `components/src_components.md`
- `components/tests_components.md`
- `attention_board.md`
- Active epic/story/task tickets in `epics/`, `stories/`, `tasks/`

## Required Updates
- Update `attention_board.md` during work so active items, status, blockers, and
  next actions stay current.
- Before compaction/handoff, verify `attention_board.md` is current and matches
  active ticket status.
- Update the `## Notes` section of all active tickets with latest findings and
  `path:line` evidence pointers.
- Ensure each meaningful finding was written as a note before the next
  investigation tranche (no end-of-pass batching).
- Ensure UNKNOWN-first discipline was followed (unverified claims remain
  `UNKNOWN`).
- Ensure note entries carry re-entry metadata:
  - `REREAD` (`REQUIRED` or `HELPFUL`)
  - `SCORE_0_TO_10` compaction usefulness score
- Update the "Context / Handoff Summary" section of all active tickets.
- Capture open questions, decisions, and next steps in the relevant ticket.
- Ensure status fields and checkboxes are accurate.
- Ensure tickets carry enough state so compaction summaries can stay empty or minimal.

## Handoff Summary Checklist
- Current state and progress (what is done vs remaining).
- Key decisions and rationale.
- Known risks and active blockers.
- Immediate next steps (1-3 concrete actions).
- References to any critical files or paths.

## Post-Compaction Verification
After compaction, re-open the required review set and confirm:
- `agent_onboarding/agent/general/skills/compaction_requirements.md` has been re-applied before any action.
- A `REONBOARD: COMPLETE` attestation was posted before any action.
- `attention_board.md` was re-opened and still matches active ticket state.
- The active tickets still represent the correct plan.
- The next steps are unambiguous.
