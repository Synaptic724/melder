# user_approved_certification

Purpose
- Enforce a strict approval handshake and keep the agent blocked until approved.

Canonical Contract (verbatim from context_compass/onboarding/AGENTS.md)
Certification gate (mandatory)
- Complete onboarding/agent/general/skills/self_certification.md and wait for approval.
- Request approval using onboarding/agent/general/skills/user_approved_certification.md.
- Do not use tools or edit files until the user replies exactly: CERTIFY: APPROVED.
- After approval, run: python context_compass/onboarding/system/certification/python_certified.py --repo-root . --agent-id <agent_id> --approval-token "CERTIFY: APPROVED"
- Tools that mutate repo state must refuse to run unless the agent profile certification_state is CERTIFIED.

Approval request (strict)
- Ask the user to reply exactly: CERTIFY: APPROVED
- If changes are needed, ask for: CERTIFY: CHANGES plus edits.

Blocking rules
- Only request approval after the self-certification explicitly lists all skills read from context_compass/onboarding/agent/SKILLS.md.
- If the approval token is not exactly CERTIFY: APPROVED, do not proceed.
- Only revise the self-certification and re-request approval.
- No tool calls, file edits, or implementation steps until approved.
- Approval must be explicit; "looks good" is not sufficient.

Post-approval requirement
- After approval, run:
  python context_compass/onboarding/system/certification/python_certified.py --repo-root . --agent-id <agent_id> --approval-token "CERTIFY: APPROVED"
- Do not proceed with any other action until the script succeeds.

References
- SQLite user.db table: agent_profile (with certification in agent_profile_certification)
