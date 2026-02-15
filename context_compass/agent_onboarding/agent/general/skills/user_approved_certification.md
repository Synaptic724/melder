# user_approved_certification

Purpose
- Define the explicit approval step that unlocks tool usage and edits.

Approval script
- Ask the user to reply with a message that includes the exact token `CERTIFY: APPROVED` and states the execution environment (`active` or `inactive`).
- Do not proceed with any tool use or file edits before approval.
- Do not run git commands unless the environment is explicitly `active`.

Rules
- Only request approval after listing the skills read from:
  - `agent_onboarding/agent/SKILLS.md`
  - `agent_onboarding/agent/general/SKILLS.md`
- Before requesting approval, complete canonical onboarding readset consumption from:
  - `context_compass/agent_onboarding/agent/general/skills/onboarding_read_paths.txt`
  - include read-integrity proof in the re-onboarding attestation.
- After compaction/handoff/fresh-session re-entry, the same full-readset requirement applies again before requesting approval.

References
- `agent_onboarding/agent/general/skills/self_certification.md`
