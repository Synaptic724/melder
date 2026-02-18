# Context Compaction Policy

## Purpose
Preserve decision-critical context with high fidelity across compactions/handoffs
and keep execution resumable with minimal drift.

## Core Principle
- Repository artifacts are the durable source of truth.
- The compaction summary is a volatile cache used to carry P0/P1 operational
  truths across a reset.
- The cache is write-only before compaction: you influence it only by writing the
  compaction summary at compaction time.
- The cache is useful but **not authoritative** until verified via
  Diff-Onboarding.

## Compaction Summary Contract (Non-negotiable)
Empty compaction summaries are forbidden.

The compaction summary MUST contain:

1) Resume pointers
- Active role/profile.
- Active ticket path(s).
- Next immediate actions (1-3 concrete steps).

2) P0/P1 retention set
- Atomic claims with stable IDs (`C-P0-001`, `C-P1-004`, ...).
- One line per claim (no paragraphs).
- Include `SOURCE: path:start-end` evidence pointer(s).
- Prioritize P0 first, then P1. Omit P2 when budget is tight.

3) Diff-Onboarding hook
- `cycle_id` (unique id for this compaction/re-entry cycle).
- Pointer to `compacting_differential_board.md`.

Required structure (use this shape)
```text
COMPACTION_CACHE:
ROLE: <role>
ACTIVE_TICKETS:
- <path>
NEXT_ACTIONS:
- <one line>
RETENTION_SET_P0:
- C-P0-001: <operational truth> | SOURCE: <path>:<start-end>
RETENTION_SET_P1:
- C-P1-001: <operational truth> | SOURCE: <path>:<start-end>
DIFF_ONBOARDING:
- cycle_id: <id>
- board: compacting_differential_board.md
```

Budget discipline (non-negotiable)
- Target <= 450 tokens to avoid truncation.
- Trim order when budget is tight: resume pointers > P0 > P1 > P2.
- Never drop P0 policy-gate claims (certification, onboarding, tool restrictions).
- Keep each claim to one line; no prose; no lists inside claims.
- Prefer `ID: truth | SOURCE: path:start-end` over sentences.

Safety rules (non-negotiable)
- Do NOT include secrets, credentials, tokens, private keys, or sensitive
  identifiers in the compaction summary.
- If a claim depends on a secret value, write a redacted placeholder and a secure
  pointer.

## Retention Set Inputs
Retention claims are derived from:
- Active ticket state (`## Notes`, `Decision Log`, `Context / Handoff Summary`).
- Open items in `compacting_differential_board.md`.
- Policy gates that must not drift (onboarding, certification, unknowns gate).

## Diff-Onboarding Compaction Loop (Required)
After every compaction/handoff re-entry:
- Run REONBOARD per `agent_onboarding/default/general/skills/compaction_requirements.md`.
- Run Diff-Onboarding per `agent_onboarding/default/general/skills/compaction_diff_onboarding.md`.
- Measure P0/P1 retention, record misses, and adapt the next compaction summary
  from measured misses.

Default gates (healthy loop)
- `P0_retention_rate >= 0.98`
- `P0_critical_loss_count == 0`
- achieved for `2` consecutive cycles
- Override knobs (optional): `config/context_compass_config.yaml` -> `compaction_diff_onboarding.gates.*`

## Required Review Set
Before initiating compaction/handoff:
- You MUST ensure the durable state is up to date:
  - `attention_board.md` reflects current routing, status, blockers, and next actions.
  - Active tickets linked from `attention_board.md` have current checklists and `## Notes`.

Core review set (ALWAYS required) — review these files in order:
- `AGENTS.MD`
- `CONTEXT_COMPACTION.md`
- `agent_onboarding/default/general/skills/execution_contract.md`
- `config/context_compass_config.yaml`
- `SKILLS.MD`
- resolved role `SKILLS.MD` chain (parent-first; the SKILLS files themselves)
- `agent_onboarding/default/general/skills/compaction_requirements.md`
- `agent_onboarding/default/general/skills/compaction_diff_onboarding.md`
- `agent_onboarding/default/general/skills/workflow.md`
- `attention_board.md`
- Active epic/story/task tickets in `tickets/epics/`, `tickets/stories/`, `tickets/tasks/`
- `compacting_differential_board.md` (review open rows only)

Conditional review set (ONLY when triggered):
- `artifact_board.md` (when active tickets include artifacts or artifact disposition changes)
- `artifacts/README.md` (when artifact lifecycle protocol is active)
- System-context / architecture docs are **ON-DEMAND**:
  - Do NOT force-read `system_docs/*` as a box-check.
  - You MUST read the relevant system-context docs only when:
    - the active ticket requires architecture/components/tests documentation work, OR
    - this session modified `system_docs/*`, OR
    - the next immediate action requires architecture/components/tests claims.
  If triggered, review:
  - `agent_onboarding/default/engineer/skills/src_architecture_instructions.md`
  - `system_docs/src_architecture.md`
  - `agent_onboarding/default/engineer/skills/tests_architecture_instructions.md`
  - `system_docs/tests_architecture.md`
  - `agent_onboarding/default/engineer/skills/src_components_instructions.md`
  - `system_docs/src_components.md`
  - `agent_onboarding/default/engineer/skills/tests_components_instructions.md`
  - `system_docs/tests_components.md`

Read discipline (non-negotiable)
- Review-set document reads must be manual per file path.
- Loop-based/batch document-reading commands are forbidden (for/foreach/while
  loops, xargs-style runners, or piped file-list iterators).
- For files over 500 LOC, read in explicit 500-line chunks in sequential order.

## Required Updates
- Update `attention_board.md` during work so active items, status, blockers, and
  next actions stay current.
- Update `artifact_board.md` when active tickets have artifacts or artifact
  disposition changes.
- Before compaction/handoff, verify `attention_board.md` is current and matches
  active ticket status.
- Update the `## Notes` section of all active tickets with latest findings and
  `path:start_line-end_line` evidence pointers (use `start=end` for single-line
  evidence).
- Ensure each meaningful finding was written as a note before the next
  investigation tranche (no end-of-pass batching).
- Ensure UNKNOWN-first discipline was followed (unverified claims remain `UNKNOWN`).
- Ensure tickets carry enough state so the compaction cache summary can stay
  compact and strictly structured while preserving P0/P1 operational truth.

## Handoff Summary Checklist
- Current state and progress (what is done vs remaining).
- Key decisions and rationale.
- Known risks and active blockers.
- Immediate next steps (1-3 concrete actions).
- References to any critical files or paths.
