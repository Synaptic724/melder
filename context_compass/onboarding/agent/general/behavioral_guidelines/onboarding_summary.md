# onboarding_summary

Purpose
- Provide a concise, general onboarding checklist for agents.

Checklist (short form)
1) Confirm context_compass root + policy sources
   - Read `AGENTS.override.md` (if present) and `context_compass/onboarding/AGENTS.md`.
2) Preflight (user-initiated, optional)
   - Run the preflight wrapper in `context_compass/onboarding/system/`.
   - If python is missing, stop and request installation before proceeding.
3) Install/seed (if needed)
   - Use the OS onboarding installer under `context_compass/onboarding/system/`.
   - Run `context_compass/system/installation/build_runner.py` if config tables are missing.
4) Read config + report
   - Load `config_context_compass_*` tables; report feature flags and `work_mode`.
5) Select career, then read skills
   - Follow `context_compass/onboarding/agent/SKILLS.md` in order.
   - Read career-specific skills from `context_compass/onboarding/agent/careers/<career>/SKILLS.md`.
6) Establish agent identity
   - Use a user-provided `agent_id` only; do not invent one.
7) Certification gate
   - Complete self-certification and request approval.
   - After `CERTIFY: APPROVED`, run `context_compass/onboarding/system/certification/python_certified.py`.
   - No tool usage or file edits before certification except preflight or onboarding bundle collection.
8) Initialize runtime + check in
   - Branch init/switch, repo_state assess, agent profile creation (if missing), checkin, and environment record.
9) Post-cert work execution
   - Use `context_compass/workspace/tools/` facades for discovery and execution.
   - Follow context-first rules (dir ctx -> file ctx -> code), use locks + atomic writes, rescan after edits, and check out when done.

References
- `context_compass/onboarding/AGENTS.md`
- `context_compass/onboarding/agent/general/behavioral_guidelines/onboarding_and_certification.md`
- `context_compass/onboarding/agent/SKILLS.md`
- `context_compass/onboarding/user/getting_started.md`
