

# user_approved_certification

Purpose
- Define the user-side approval gate for agent certification.
- Ensure certification is only granted after evidence-backed onboarding + (post-compaction) measured competence.

Canonical references
- `context_compass/AGENTS.MD`
- `context_compass/agent_onboarding/default/general/skills/self_certification.md`
- `context_compass/agent_onboarding/default/general/skills/compaction_requirements.md`
- `context_compass/skill_check/skill_check_policy.md`

---

## Approval token (non-negotiable)

Certification is granted only when the user provides the exact token:

`CERTIFY: APPROVED`

No near-matches. No paraphrases.

---

## Minimum evidence required from the agent (always)

Before the user should approve certification, the agent must provide:

- `ROLE_SKILLS_READ`
- `FILES_REREAD`
- `READ_INTEGRITY_PROOF`
- `NO_ACTION_TAKEN_YET: true`

If any are missing: do not approve.

---

## Additional post-compaction gate (mandatory)

If the session follows a compaction/handoff/reset event, the user should only
approve when `SKILL_GATE_REPORT` is present:

### `SKILL_GATE_REPORT`
Must include:
- `knowledge_score`
- `p0_miss_count`
- `critical_p0_miss_count`
- `policy_gate_miss_count`
- `rank`
- `ANTI_CHEAT: PASSED`

Default approval rule (strict)
- Do NOT approve if:
  - `policy_gate_miss_count > 0`, OR
  - any critical P0 miss, OR
  - `knowledge_score < knowledge_gate.global_pass_threshold`

---

## User override policy
- The user may override, but must do so explicitly and intentionally.
- Absent explicit override, the default is deny until gates pass.
