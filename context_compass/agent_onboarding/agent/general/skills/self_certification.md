# self_certification

Purpose
- Ensure onboarding is complete before any tool usage or edits.

Required flow
- Read every skill listed in `agent_onboarding/agent/SKILLS.md` and `agent_onboarding/agent/general/SKILLS.md` (parallel reading allowed).
- Complete the canonical onboarding readset from:
  `context_compass/agent_onboarding/agent/general/skills/onboarding_read_paths.txt`.
- Manual source-document reading from the readset is required; onboarding dump files are non-compliant.
- Performative onboarding is forbidden: marker-only reread logs do not satisfy the read requirement.
- Before requesting certification, provide concise read-integrity proof (concrete rule callouts from reread docs).
- For re-onboarding attestation, keep `FILES_REREAD` compact (active ticket paths)
  and reference onboarding docs via `ONBOARDING_READSET`.
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
