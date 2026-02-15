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
- Before requesting approval, complete canonical onboarding consumption through the parallel read-list workflow:
  - build + validate `context_compass/agent_onboarding/parallel_read_onboarding_dump/manifest.txt`
  - consume `onboarding_read_XX` sequentially (`1..N`, chunk size `500`)
  - include read-integrity + chunk-coverage proof in the re-onboarding attestation.
- After compaction/handoff/fresh-session re-entry, the same parallel read-list requirement applies again before requesting approval.
- Direct readset fallback is allowed only when the parallel dump path is unavailable, and still requires full readset completion.

References
- `agent_onboarding/agent/general/skills/self_certification.md`
