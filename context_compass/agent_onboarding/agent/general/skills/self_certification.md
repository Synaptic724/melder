# self_certification

Purpose
- Ensure onboarding is complete before any tool usage or edits.

Required flow
- Read every skill listed in `agent_onboarding/agent/SKILLS.md` and `agent_onboarding/agent/general/SKILLS.md` (parallel reading allowed).
- Optional parallel-dump bootstrap for onboarding docs:
  - Build chunked dump (Windows):
    `context_compass/agent_onboarding/agent/general/skills/build_parallel_read_onboarding_dump.cmd`
  - Build chunked dump (Linux/Bash):
    `bash context_compass/agent_onboarding/agent/general/skills/build_parallel_read_onboarding_dump.sh`
  - Validate dump manifest/chunks (Windows):
    `context_compass/agent_onboarding/agent/general/skills/validate_parallel_read_onboarding_dump.cmd`
  - Validate dump manifest/chunks (Linux/Bash):
    `bash context_compass/agent_onboarding/agent/general/skills/validate_parallel_read_onboarding_dump.sh`
  - Read chunk by ordinal (Windows):
    `context_compass/agent_onboarding/agent/general/skills/read_parallel_read_onboarding_chunk.cmd -ChunkNumber <N> -ValidateFirst`
  - Read chunk by ordinal (Linux/Bash):
    `bash context_compass/agent_onboarding/agent/general/skills/read_parallel_read_onboarding_chunk.sh --chunk-number <N> --validate-first`
  - Parallel dump artifacts:
    `context_compass/agent_onboarding/parallel_read_onboarding_dump/manifest.txt`
    and `context_compass/agent_onboarding/parallel_read_onboarding_dump/onboarding_read_XX`.
  - Source readset manifest used by the builder:
    `context_compass/agent_onboarding/agent/general/skills/onboarding_read_paths.txt`.
  - Validation enforces timestamp freshness (`--max-age-minutes`) and SHA256 checks
    for the source manifest, source files, and chunk files.
  - If validation fails, rebuild and re-validate before certification.
  - When dump bootstrap is used, consume `onboarding_read_XX` sequentially
    from chunk number `1` through final chunk before requesting certification.
  - Windows/PowerShell direct readset fallback:
    `powershell -NoProfile -ExecutionPolicy Bypass -File context_compass/agent_onboarding/agent/general/skills/run_onboarding_read.ps1`
  - Windows wrapper direct readset fallback:
    `context_compass/agent_onboarding/agent/general/skills/run_onboarding_read.cmd`
  - Linux/Bash direct readset fallback:
    `bash context_compass/agent_onboarding/agent/general/skills/run_onboarding_read.sh`
- Performative onboarding is forbidden: marker-only reread logs do not satisfy the read requirement.
- Before requesting certification, provide concise read-integrity proof (concrete rule callouts from reread docs).
- For dump bootstrap paths, include chunk coverage proof (`chunk_size=500`, total chunk count, and consumed chunk-number range).
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
