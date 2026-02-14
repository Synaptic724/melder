# self_certification

Purpose
- Ensure onboarding is complete before any tool usage or edits.

Required flow
- Read every skill listed in `agent_onboarding/agent/SKILLS.md` and `agent_onboarding/agent/general/SKILLS.md` (parallel reading allowed).
- Summarize that onboarding is complete and request approval.
- Require the approval message to include the exact token `CERTIFY: APPROVED` **and** the execution environment (`active` or `inactive`).
- Do not use tools or edit files until the user provides both the approval token and the environment.
- Do not run git commands unless the environment is explicitly `active`.

Certification record
- Track certification in the session narrative and update `attention_board.md`
  routing when certification state affects execution.
- `00_overview.md` may be updated optionally for high-level summaries only.

References
- `agent_onboarding/agent/SKILLS.md`
- `agent_onboarding/agent/general/SKILLS.md`
