# user_approved_certification

Purpose
- Define the explicit approval step that unlocks tool usage and edits.

Approval script
- Ask the user to reply with a message that includes the exact token `CERTIFY: APPROVED` and states the execution environment (`active` or `inactive`).
- Do not proceed with any tool use or file edits before approval.
- Do not run git commands unless the environment is explicitly `active`.

Rules
- Only request approval after listing the skills read from:
  - `context_compass/config/context_compass_config.yaml`
  - `context_compass/SKILLS.md`
  - `context_compass/agent_onboarding/default/general/SKILLS.MD`
  - `context_compass/agent_onboarding/default/engineer/SKILLS.MD`
- Before requesting approval, complete role-driven onboarding reads from:
  - `context_compass/config/context_compass_config.yaml`
  - `context_compass/SKILLS.md`
  - resolved role `SKILLS.MD` chain for the active profile
  - include read-integrity proof in the re-onboarding attestation.
- Do not request approval based on onboarding dump artifacts; approval requires source-document read completion.
- After compaction/handoff/fresh-session re-entry, the same full-readset requirement applies again before requesting approval.