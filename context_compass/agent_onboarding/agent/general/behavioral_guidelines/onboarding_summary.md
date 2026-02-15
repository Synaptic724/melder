# onboarding_summary

Purpose
- Provide a concise, general onboarding checklist for agents.

Checklist (short form)
1) Confirm repo root + policy sources
   - Read `AGENTS.MD` and any directory-local `AGENTS.MD` in scope.
2) Read onboarding entrypoints
   - `agent_onboarding/agent/SKILLS.md`
   - `agent_onboarding/agent/general/README.md`
   - `agent_onboarding/agent/engineer/README.md`
3) Select career (engineer)
   - Read `agent_onboarding/agent/general/SKILLS.md` in order.
   - Read `agent_onboarding/agent/engineer/SKILLS.md` after the baseline.
4) Certification gate
   - Request approval before any tool usage or edits.
   - Approval must include the exact token `CERTIFY: APPROVED` and the execution environment (`active` or `inactive`).
   - Do not run git commands unless the environment is explicitly `active`.
5) Post-cert work execution
   - Use `epics/`, `stories/`, and `tasks/` for all work.
   - Route from `attention_board.md` and resume from linked ticket notes.
   - Re-read architecture/components docs before major work.
   - Keep `attention_board.md` current for routing and ticket notes current for durable findings.

References
- `AGENTS.MD`
- `agent_onboarding/agent/SKILLS.md`
- `agent_onboarding/agent/general/SKILLS.md`
- `agent_onboarding/agent/engineer/SKILLS.md`
