# Task: Harden Manual Onboarding Path and Eliminate Dump-Lookup Drift

Completed: 2026-02-15
Summary: Hardened onboarding so manual source-document reading is canonical from bootstrap through certification, with explicit non-canonical dump warnings and two validation artifacts proving no dump-workflow cues in entrypoint policy docs.

## Metadata
- Task ID: TASK-2026-02-15-harden-manual-onboarding-no-dump-path
- Story: none
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-15
- Updated: 2026-02-15

## Objective
Ensure onboarding from first bootstrap to certification clearly enforces manual document reading and no longer nudges agents toward dump/script-based onboarding paths.

## Scope Boundaries
- In scope:
  - Root bootstrap onboarding docs (`agents.md`, `context_compass/AGENTS.MD`).
  - Core onboarding policy docs under `context_compass/agent_onboarding/agent/general/`.
  - Read-order/readset wording that can cause dump lookup behavior.
- Out of scope:
  - Deleting dump artifacts/scripts from disk.
  - Runtime/library code changes outside onboarding policy docs.

## Steps / Checklist
- [x] Audit onboarding entrypoint docs for dump/script-oriented language that can misroute agents.
- [x] Rewrite onboarding instructions to make manual document reading the default and explicit path.
- [x] Ensure first-read ordering (`AGENTS.MD` then `SOCIAL_CONTRACT.md`) is consistent across entry docs.
- [x] Validate no active onboarding policy doc prescribes dump lookup/build/validate chunk workflows.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Updated onboarding docs with unambiguous manual-read onboarding path.
- Validation evidence that active policy docs no longer route to dump files.

## Files / Paths Impacted
- `context_compass/tasks/2026-02-15_harden_manual_onboarding_no_dump_path_task.md`
- `context_compass/attention_board.md`
- `agents.md`
- `context_compass/AGENTS.MD`
- `context_compass/agent_onboarding/agent/general/SKILLS.md`
- `context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md`
- `context_compass/agent_onboarding/agent/general/skills/self_certification.md`
- `context_compass/agent_onboarding/agent/general/skills/user_approved_certification.md`
- `context_compass/agent_onboarding/agent/general/policies/policy_router.md`
- `context_compass/agent_onboarding/agent/general/skills/onboarding_read_paths.txt`
- `context_compass/artifacts/2026-02-15_manual_onboarding_policy_sweep.txt`

## Validation
- Command checks run:
  - `rg` sweep over bootstrap/entrypoint docs returned no dump-command/script-path onboarding instructions.
  - Artifact recorded at `context_compass/artifacts/2026-02-15_manual_onboarding_policy_sweep.txt` with `RESULT=NO_MATCHES`.
  - Second-pass readset audit recorded at `context_compass/artifacts/2026-02-15_manual_onboarding_policy_sweep_pass2.txt` (`READSET_MISSING=FALSE`, `READSET_DUMP_TERMS=NONE`, and head order AGENTS -> SOCIAL_CONTRACT).

## Risks / Rollback Notes
- Inconsistent wording across bootstrap and policy layers can still produce drift in fresh sessions.
- Over-broad replacement can accidentally remove required certification/read-order constraints.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [x] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: `context_compass/AGENTS.MD` still contains script-forward onboarding wording (`manifest + script path`, `manifest-driven onboarding script runs`) that can steer agents toward scripted onboarding behavior.
  EVIDENCE: context_compass/AGENTS.MD:20-20, context_compass/AGENTS.MD:26-26
  IMPACT: Fresh-session agents can still interpret scripted onboarding as expected behavior instead of manual read-first behavior.
  NEXT: Patch AGENTS and related onboarding policy docs to make manual document reading explicit and canonical.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Bootstrap and onboarding policy docs now explicitly require manual source-document reads and explicitly classify dump artifacts as non-canonical for onboarding.
  EVIDENCE: agents.md:5-5, context_compass/AGENTS.MD:20-27, context_compass/AGENTS.MD:72-77, context_compass/agent_onboarding/agent/general/SKILLS.md:49-53, context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md:9-11, context_compass/agent_onboarding/agent/general/skills/self_certification.md:8-10, context_compass/agent_onboarding/agent/general/skills/user_approved_certification.md:15-18, context_compass/agent_onboarding/agent/general/policies/policy_router.md:26-30, context_compass/agent_onboarding/agent/general/skills/onboarding_read_paths.txt:4-7
  IMPACT: Fresh-session onboarding path is now explicitly manual-read-first from the beginning and no longer cues dump lookup.
  NEXT: Validate entrypoint docs for zero dump-command/script-path instructions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Entry-point policy sweep confirms no dump-command/script-path onboarding instructions remain in the bootstrap and onboarding entry docs.
  EVIDENCE: context_compass/artifacts/2026-02-15_manual_onboarding_policy_sweep.txt:1-4
  IMPACT: Another fresh agent should no longer start by searching for onboarding dumps from policy instructions.
  NEXT: Ask user to confirm acceptance criteria and either close this task or continue hardening if additional failure modes are observed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: A second onboarding pass confirms canonical readset integrity (81 files, no missing paths), first-two ordering (`AGENTS.MD` then `SOCIAL_CONTRACT.md`), and no dump-workflow terms across the full readset.
  EVIDENCE: context_compass/artifacts/2026-02-15_manual_onboarding_policy_sweep_pass2.txt:4-8
  IMPACT: Manual-read onboarding path is validated end-to-end in a repeat pass before closure.
  NEXT: Confirm with user whether to close the hardening task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Task executed to harden onboarding from first bootstrap to certification for manual document reading. Dump/script cues were removed from active onboarding entrypoint docs, explicit non-canonical dump warnings were added, and a second-pass readset audit confirmed AGENTS->SOCIAL ordering plus no dump terms across the full readset.
