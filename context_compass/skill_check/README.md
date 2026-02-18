

# skill_check (Knowledge Gate + Compaction Fidelity System)

Purpose
- Add a **measurable knowledge-gate** layer to the existing fidelity-first compaction + diff-onboarding loop.
- The Diff Board measures *semantic parity* (what survived compaction).
- The Skill Check measures *skill competence* (can the agent apply the rules correctly).
- Over repeated compaction cycles, the system must converge toward:
  - high-fidelity retention of system/skills/policy state, AND
  - consistent correct application of those rules.

Core intent (non-negotiable)
1) Compaction is not a â€œsmall cacheâ€ optimization.
2) Compaction summary should be as rich as platform limits allow.
3) Target mix in compaction summary is **~90% system/skills/policy** and **~10% operational pointers**.
4) The Diff Board is not the cache itself. It is the measurement ledger for cache fidelity.
5) The Skill Check is not the cache itself. It is the measurement ledger for skill competence.
6) The system must improve over cycles by measuring weaknesses, targeting them in the next compaction summary, then retesting.

Directory structure
- `context_compass/skill_check/tests/`
  - test prompts only (safe to read before answering)
- `context_compass/skill_check/test_answers/`
  - answer keys + grading rubrics (**locked until answer submission**)
- `context_compass/skill_check/historical_test_results/`
  - cycle summaries + deltas + remediation tracking
- `context_compass/skill_check/manifest/`
  - onboarding manifest derived from canonical docs

Canonical references
- `context_compass/AGENTS.MD`
- `context_compass/CONTEXT_COMPACTION.md`
- `context_compass/compacting_differential_board.md`
- `context_compass/agent_onboarding/default/general/skills/compaction_requirements.md`
- `context_compass/agent_onboarding/default/general/skills/compaction_diff_onboarding.md`
- `context_compass/config/context_compass_config.yaml`

Read next
- `context_compass/skill_check/skill_check_policy.md` (canonical operating policy)