# context_gold

Purpose
- Treat durable context as the highest priority for this repo.
- Prevent policy drift by forcing state into repository files, not chat memory.

Re-entry ritual (required)
- After context compaction OR a fresh session:
  1) Re-open `attention_board.md`.
  2) Re-open the active ticket(s) referenced there.
  3) Re-onboard/Onboard per `agent_onboarding/default/general/skills/compaction_requirements.md`
     (includes Diff-Onboarding).
  4) Read system-context docs ONLY when the active ticket or next step requires
     architecture/components/tests claims.
     - If triggered, read the relevant `system_docs/*` and the matching instruction docs.
     - If not triggered, DO NOT force-read `system_docs/*` as a box-check.

Behavior
- Update "Context / Handoff Summary" and `## Notes` in active tickets as you learn things.
- Keep documentation grounded in source evidence.
- Do not handwave; record UNKNOWNs and the next verification step.
- Do NOT claim you retained full context/documents after compaction.
  - Only rely on repo artifacts and verified compaction-cache retention claims.
  - Re-open the source file when making new claims.

References
- `agent_onboarding/default/general/skills/context_compaction.md`
- `agent_onboarding/default/general/skills/compaction_requirements.md`
- `agent_onboarding/default/general/skills/compaction_diff_onboarding.md`
