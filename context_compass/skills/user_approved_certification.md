# user_approved_certification

Purpose
- Enforce a strict approval handshake and keep the agent blocked until approved.

Canonical Contract (verbatim from context_compass/AGENTS.md)
Certification gate (mandatory)
- Complete skills/self_certification.md and wait for approval.
- Request approval using skills/user_approved_certification.md.
- Do not use tools or edit files until the user replies exactly: CERTIFY: APPROVED.
- After approval, run: python python_certified.py --approval-token "CERTIFY: APPROVED"
- Tools that mutate repo state must refuse to run unless certification_state.json is CERTIFIED.

Approval request (strict)
- Ask the user to reply exactly: CERTIFY: APPROVED
- If changes are needed, ask for: CERTIFY: CHANGES plus edits.

Blocking rules
- If the approval token is not exactly CERTIFY: APPROVED, do not proceed.
- Only revise the self-certification and re-request approval.
- No tool calls, file edits, or implementation steps until approved.
- Approval must be explicit; "looks good" is not sufficient.

Post-approval requirement
- After approval, run:
  python python_certified.py --approval-token "CERTIFY: APPROVED"
- Do not proceed with any other action until the script succeeds.

References
- context_compass/self_context/certification_state.json
