

# Context Compaction Policy (Fidelity-First)

## Purpose
- Preserve **system/skills/policy state** across compaction with high semantic fidelity.
- Keep operational routing pointers secondary (tickets + `attention_board.md` already handle routing).

## Objective and weighting
- **Primary:** maximize semantic parity of system/skills/policy state across compaction.
- **Secondary:** preserve minimal operational pointers.
- Default compaction summary mix:
  - **~90%** system/skills/policy
  - **~10%** operational pointers

## Compaction summary rule
- The compaction summary is a **system-state mirror**, not a ticket recap.
- Use structured, checkable statements (MUST/DO NOT gates, ordering constraints, definitions).
- Semantic parity is the objective; verbatim copying is not required.

## Required schema (system-first)
1) Role + skills routing (short)
2) System/skills/policy mirror (dominant)
3) Diff feedback loop state (cycle_id + top misses/hints)
4) Operational pointers (short)

See `CONTEXT_COMPACTION.md` for the canonical schema.

## Required review set (before compaction/handoff)
System/skills/policy (PRIMARY):
- `AGENTS.MD`
- `agent_onboarding/default/general/skills/execution_contract.md`
- `agent_onboarding/default/general/skills/compaction_requirements.md`
- `agent_onboarding/default/general/skills/compaction_diff_onboarding.md`
- `config/context_compass_config.yaml`
- `SKILLS.MD` + resolved role `SKILLS.MD` chain (SKILLS files)
- every required baseline skill doc referenced by the resolved chain
- certification + policy docs:
  - `agent_onboarding/default/general/policies/policy_skills.md`
  - `agent_onboarding/default/general/skills/self_certification.md`
  - `agent_onboarding/default/general/skills/user_approved_certification.md`

Operational (SECONDARY):
- `attention_board.md`
- active tickets referenced by `attention_board.md`
- artifacts docs when active

## Post-compaction re-entry
- Re-entry after compaction/handoff MUST run REONBOARD + **Diff-Onboarding**:
  `agent_onboarding/default/general/skills/compaction_requirements.md`.