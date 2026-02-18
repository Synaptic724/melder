

# context_gold

Purpose
- Treat durable context as the highest priority for this repo.
- Prevent policy drift by forcing state into canonical sources and verifying retention after compaction.

Re-entry ritual (required)

After context compaction OR a fresh session:
1) Re-open `attention_board.md`.
2) Re-open the active ticket(s) referenced there.
3) Re-onboard/Onboard per `agent_onboarding/default/general/skills/compaction_requirements.md`.
4) After compaction/handoff specifically:
   - Run **Diff-Onboarding** (semantic parity measurement) per:
     `agent_onboarding/default/general/skills/compaction_diff_onboarding.md`.

System-context docs remain ON-DEMAND
- Read system-context docs ONLY when the active ticket or next step requires
  architecture/components/tests claims.
- If triggered, read the relevant `system_docs/*` and the matching instruction docs.
- If not triggered, DO NOT force-read `system_docs/*` as a box-check.

Behavior
- Update "Context / Handoff Summary" and `## Notes` in active tickets as you learn things.
- Keep documentation grounded in source evidence.
- Do not handwave; record UNKNOWNs and the next verification step.

Retention discipline (important)
- Do NOT claim you "retained" full documents after compaction.
- Instead:
  - Treat compaction summary state as **hypothesis** until verified by Diff-Onboarding.
  - Use `compacting_differential_board.md` to measure what survived, what distorted, and what dropped.
  - Improve the next compaction summary using board-driven `next_compaction_hint` corrections.

References
- `agent_onboarding/default/general/skills/context_compaction.md`
- `agent_onboarding/default/general/skills/compaction_requirements.md`
- `agent_onboarding/default/general/skills/compaction_diff_onboarding.md`
- `compacting_differential_board.md`
- `skill_check/skill_check_policy.md`