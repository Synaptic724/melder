# self_certification

Purpose
- Ensure onboarding is complete before any tool usage or edits.

Required flow
- Read every skill listed in `agent_onboarding/agent/SKILLS.md` and `agent_onboarding/agent/general/SKILLS.md` (parallel reading allowed).
- Optional single-command bootstrap for onboarding docs:
  - Windows/PowerShell:
    `powershell -NoProfile -ExecutionPolicy Bypass -File context_compass/agent_onboarding/agent/general/skills/run_onboarding_read.ps1`
  - Windows wrapper (no execution-policy friction):
    `context_compass/agent_onboarding/agent/general/skills/run_onboarding_read.cmd`
  - Linux/Bash:
    `bash context_compass/agent_onboarding/agent/general/skills/run_onboarding_read.sh`
  - Build dump once (Windows):
    `context_compass/agent_onboarding/agent/general/skills/build_onboarding_dump.cmd`
  - Build dump once (Linux):
    `bash context_compass/agent_onboarding/agent/general/skills/build_onboarding_dump.sh`
  using readset `context_compass/agent_onboarding/agent/general/skills/onboarding_read_paths.txt`.
  - Optional no-script path: read
    `context_compass/agent_onboarding/agent/general/skills/onboarding_read_dump.txt`.
- Performative onboarding is forbidden: marker-only reread logs do not satisfy the read requirement.
- Before requesting certification, provide concise read-integrity proof (concrete rule callouts from reread docs).
- For re-onboarding attestation, keep `FILES_REREAD` compact (active ticket paths)
  and reference onboarding docs via `ONBOARDING_READSET` when the readset script is used.
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
