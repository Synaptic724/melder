

# Context Compaction Policy (Fidelity-First)

## Objective
1) **Primary objective:** maximize semantic fidelity of **system/skills/policy state** across compaction.
2) **Secondary objective:** preserve minimal operational routing pointers so work can resume.
3) **Default target mix for the compaction summary:**
   - **~90%**: system/skills/policy state
   - **~10%**: operational pointers (routing + immediate next actions)

This is the opposite of a "tiny pointer summary" policy. Compactness is a constraint, not the objective.

## Canonical Definition: What the Compaction Summary Is
- The compaction summary is the *carried state* that survives a compaction event.
- It is **not** a ticket recap and **not** a narrative replay.
- It is a **high-fidelity mirror of onboarding/skills/policy state**, expressed as structured, checkable statements.

## Required Compaction Summary Schema (System-First)
The compaction summary MUST be structured with system/skills/policy first.

### 1) Active Profile + Role Resolution (operational; keep short)
- active profile / selected role
- resolved `SKILLS.MD` chain (parent-first) and any on-demand triggers currently active
- certification state requirement (must re-certify after compaction)
- **skill_check snapshot** (short): last cycle_id, last global_score, last rank, requires_retest count
- pointers: `attention_board.md`, active tickets, immediate next actions (13)

### 2) System / Skills / Policy State Mirror (dominant; ~90% of budget)
Provide a high-fidelity semantic mirror of the canonical docs:

- `AGENTS.MD` (prime gates + anti-theater + compaction rules)
- `agent_onboarding/default/general/skills/execution_contract.md`
- `agent_onboarding/default/general/skills/compaction_requirements.md`
- `agent_onboarding/default/general/skills/compaction_diff_onboarding.md`
- `skill_check/skill_check_policy.md`
- `skill_check/manifest/onboarding_manifest.yaml`
- `agent_onboarding/default/general/policies/policy_skills.md`
- certification docs:
  - `agent_onboarding/default/general/skills/self_certification.md`
  - `agent_onboarding/default/general/skills/user_approved_certification.md`
- the resolved role `SKILLS.MD` chain (the SKILLS files themselves)
- **every required baseline skill doc** referenced by that resolved chain

**Rule for mirroring:** semantic parity, not verbatim copy.
- Prefer structured bullets with explicit MUST/DO NOT constraints.
- Preserve definitions, gates, ordering constraints, and "what changes my behavior" implications.
- If you are unsure, mark `UNKNOWN` rather than invent.

### 3) Diff + Knowledge Feedback Loop State (system; short but mandatory)
- last `cycle_id` (if any)
- top unresolved misses from `compacting_differential_board.md` (both fidelity_diff and knowledge_test)
- the top 5 `next_compaction_hint` corrections to apply next compaction
  - prioritize policy-gate and sequence-order misses first

### 4) Operational Pointers (secondary; ~10% of budget)
- `attention_board.md` routing state (what is active and why)
- active ticket paths + one-line status each
- immediate next actions

## Budget and Trimming Rules
- Use as much compaction summary budget as the platform allows.
- Only trim when the platform forces a hard limit.

If trimming is required, the trimming order MUST protect system/skills/policy coverage first:

1) Trim operational narrative/details first.
2) Trim operational pointers beyond immediate routing.
3) Trim lowest-priority system/skills items (P2) next.
4) Trim medium-priority system/skills items (P1) next.
5) **Never trim policy-gate system items (P0 policy gates).**

## Pre-Compaction Checklist (Required)
Before initiating compaction/handoff:

1) Ensure durable operational state is current:
   - `attention_board.md` matches reality (routing, status, blockers, next actions).
   - active tickets have up-to-date checklists and `## Notes` with evidence pointers.
2) Ensure the semantic-parity loop has inputs:
   - Open `compacting_differential_board.md` and identify OPEN/HIGH items.
   - Apply the latest `next_compaction_hint` corrections in the compaction summary.
3) Generate the compaction summary using the required schema above.

## Required Review Set
To author a high-fidelity system mirror, you MUST review:

System/skills/policy review set (PRIMARY; system-first):
- `AGENTS.MD`
- `agent_onboarding/default/general/skills/execution_contract.md`
- `agent_onboarding/default/general/skills/compaction_requirements.md`
- `agent_onboarding/default/general/skills/compaction_diff_onboarding.md`
- `skill_check/skill_check_policy.md`
- `skill_check/manifest/onboarding_manifest.yaml`
- `config/context_compass_config.yaml`
- `SKILLS.MD`
- resolved role `SKILLS.MD` chain (parent-first; the SKILLS files themselves)
- `agent_onboarding/default/general/policies/policy_skills.md`
- `agent_onboarding/default/general/skills/self_certification.md`
- `agent_onboarding/default/general/skills/user_approved_certification.md`
- every required baseline skill doc referenced by the resolved chain

Operational review set (SECONDARY; keep short):
- `attention_board.md`
- active epic/story/task tickets referenced by `attention_board.md`
- `artifact_board.md` and `artifacts/README.md` when artifact lifecycle is active

System-context / architecture docs remain **ON-DEMAND** unless a role baseline explicitly requires them.

## Post-Compaction Verification (Re-Entry)
After compaction/handoff, before any action:

- Apply `agent_onboarding/default/general/skills/compaction_requirements.md` (REONBOARD).
- Produce a `DIFF_ONBOARDING_REPORT` (semantic parity metrics) before requesting certification.
- Produce a `SKILL_GATE_REPORT` (knowledge-gate test metrics + global score + rank) before requesting certification.
- Only after certification may you update `compacting_differential_board.md` with the new cycle rows.