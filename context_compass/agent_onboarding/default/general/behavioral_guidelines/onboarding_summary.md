# onboarding_summary

Purpose
- Provide a concise, general onboarding checklist for agents.

Checklist (short form)
1) Confirm repo root + policy sources
   - Read `AGENTS.MD` and any directory-local `AGENTS.MD` in scope.
2) Read onboarding entrypoints
   - `config/context_compass_config.yaml`
   - `router.md`
   - `agent_onboarding/default/new/skills/first_time_profile_setup.md`
   - `agent_onboarding/default/new/README.md` (allowed only for `new` profile)
3) Select career (engineer)
   - Read `agent_onboarding/default/general/SKILLS.MD` first.
   - Read `agent_onboarding/default/engineer/SKILLS.MD` after the baseline.
4) Certification gate
   - Request approval before any tool usage or edits.
   - Approval must include the exact token `CERTIFY: APPROVED` and the execution environment (`active` or `inactive`).
   - Do not run git commands unless the environment is explicitly `active`.
5) Post-cert work execution
   - Use `tickets/epics/`, `tickets/stories/`, and `tickets/tasks/` for all work.
   - Route from `attention_board.md` and resume from linked ticket notes.
   - Re-read architecture/components docs before major work.
   - Keep `attention_board.md` current for routing and ticket notes current for durable findings.

References
- `AGENTS.MD`
- `config/context_compass_config.yaml`
- `router.md`

