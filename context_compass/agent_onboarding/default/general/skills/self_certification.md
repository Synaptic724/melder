# self_certification

Purpose
- Ensure onboarding is complete before any tool usage or edits.

Required flow
- Read routing authority from:
  - `context_compass/config/context_compass_config.yaml`
  - `context_compass/SKILLS.md`
  - `context_compass/agent_onboarding/default/general/SKILLS.MD`
  - `context_compass/agent_onboarding/default/engineer/SKILLS.MD`
- Complete role-driven onboarding reads from:
  - `context_compass/config/context_compass_config.yaml`
  - `context_compass/SKILLS.md`
  - resolved role `SKILLS.MD` chain for the active profile.
- For a given trigger event, complete the readset once; do not duplicate-read
  the same onboarding set before certification unless a new
  compaction/handoff/session-reset event occurs.
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