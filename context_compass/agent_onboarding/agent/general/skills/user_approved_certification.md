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

References
- `agent_onboarding/agent/general/skills/self_certification.md`
