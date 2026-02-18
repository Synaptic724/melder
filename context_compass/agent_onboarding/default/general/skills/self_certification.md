

# self_certification

Purpose
- Define the mandatory evidence package an agent must publish before requesting certification.
- Prevent box-check compliance by requiring measured parity + measured competence after compaction.

Canonical references
- `context_compass/AGENTS.MD`
- `context_compass/agent_onboarding/default/general/skills/compaction_requirements.md`
- `context_compass/agent_onboarding/default/general/skills/compaction_diff_onboarding.md`
- `context_compass/skill_check/skill_check_policy.md`
- `context_compass/config/context_compass_config.yaml`

---

## Required for certification (always)

Before requesting any certification token, publish a certification attestation containing:

- `ROLE_SKILLS_READ` (resolved chain, parent-first)
- `FILES_REREAD` (minimum: `attention_board.md` + active tickets)
- `READ_INTEGRITY_PROOF` (concise comprehension proof; NOT tool logs)
- `NO_ACTION_TAKEN_YET: true`

Hard rule
- Never claim reads/tests/checks ran unless they actually ran.

---

## Additional post-compaction certification gates (mandatory)

When the session follows a compaction/handoff/reset event, certification requires BOTH:

### A) Fidelity evidence (Diff-Onboarding)
Publish `DIFF_ONBOARDING_REPORT` including at least:
- `system_skill_doc_coverage`
- `system_skill_parity_rate`
- `policy_gate_miss_count`
- top 3 misses + `next_compaction_hint` corrections

### B) Knowledge evidence (Skill Gate)
Publish `SKILL_GATE_REPORT` including at least:
- `knowledge_score`
- `knowledge_pass_rate`
- `p0_miss_count`
- `critical_p0_miss_count`
- `fidelity_score`
- `global_score`
- `rank`
- `ANTI_CHEAT: PASSED` (answers submitted before reading answer keys)

Certification gates (strict; default)
- `global_score >= knowledge_gate.global_pass_threshold`
- `policy_gate_miss_count == 0`
- `critical_p0_miss_count <= knowledge_gate.p0_critical_miss_max`
- consecutive pass cycles threshold respected
- no missing test artifacts for required manifest entries

Hard rules
- If any gate fails: certification is blocked.
- Do NOT request certification when blocked.

---

## Certification request (format)

When (and only when) all required gates pass:

1) State: `CERTIFY: REQUEST`
2) Include the full attestation package:
   - baseline reads evidence (always)
   - `DIFF_ONBOARDING_REPORT` (post-compaction only)
   - `SKILL_GATE_REPORT` (post-compaction only)
3) Request user approval using the exact token:
   - `CERTIFY: APPROVED`