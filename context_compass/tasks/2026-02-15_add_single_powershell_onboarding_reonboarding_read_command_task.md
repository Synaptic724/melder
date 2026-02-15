# Task: Add Single-Command PowerShell Onboarding/Re-Onboarding Read Pattern

## Metadata
- Task ID: TASK-2026-02-15-add-single-powershell-onboarding-reonboarding-read-command
- Story: standalone
- Status: review
- Owner: codex
- Priority: p1
- Created: 2026-02-15
- Updated: 2026-02-15

## Objective
Add a manifest-driven single PowerShell onboarding/re-onboarding read command and update attestation policy so re-onboarding reports ticket paths plus readset reference instead of enumerating every onboarding file path.

## Scope Boundaries
- In scope:
- `context_compass/AGENTS.MD` onboarding/re-onboarding language.
- onboarding skill docs that govern compaction re-entry and certification read requirements.
- one manifest file of onboarding paths and single-command scripts for PowerShell and Linux Bash.
- Out of scope:
- Runtime/library implementation code.
- JIT/AOT feature behavior and tests.

## Steps / Checklist
- [x] Add one canonical manifest-driven single-command PowerShell read pattern to onboarding policy docs.
- [x] Add onboarding readset manifest file and reader scripts (`.ps1` and `.sh`).
- [x] Update attestation format to list active ticket paths + readset reference instead of full onboarding file enumeration.
- [x] Keep anti-performative and substantive-read requirements explicit.
- [x] Update task notes with evidence-backed findings as edits proceed.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Updated onboarding policy text with one concrete single-command PowerShell read pattern.
- Onboarding readset manifest and cross-platform reader scripts.
- Compact attestation format policy update (ticket paths + readset reference).

## Files / Paths Impacted
- `context_compass/AGENTS.MD`
- `context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md`
- `context_compass/agent_onboarding/agent/general/SKILLS.md`
- `context_compass/agent_onboarding/agent/general/skills/self_certification.md`
- `context_compass/agent_onboarding/agent/general/skills/onboarding_read_paths.txt`
- `context_compass/agent_onboarding/agent/general/skills/run_onboarding_read.ps1`
- `context_compass/agent_onboarding/agent/general/skills/run_onboarding_read.sh`

## Validation
- Ran:
  - `rg -n "run_onboarding_read.sh|Linux/Bash|ONBOARDING_READSET|run_onboarding_read.ps1" context_compass/AGENTS.MD context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md context_compass/agent_onboarding/agent/general/SKILLS.md context_compass/agent_onboarding/agent/general/skills/self_certification.md`
  - `powershell -NoProfile -ExecutionPolicy Bypass -File context_compass/agent_onboarding/agent/general/skills/run_onboarding_read.ps1`
  - `bash context_compass/agent_onboarding/agent/general/skills/run_onboarding_read.sh` (failed in this Windows environment due `Bash/Service/CreateInstance/E_ACCESSDENIED`)
- Artifact:
  - `context_compass/artifacts/2026-02-15_onboarding_readset_script_validation.txt`

## Risks / Rollback Notes
- Risk: introducing wording that implies command execution alone satisfies onboarding.
- Mitigation: keep explicit language that command execution is only a read bootstrap and does not replace substantive reading + attestation proof.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Current onboarding/re-onboarding policy already bans marker-only compliance loops and allows parallel/bulk reads only when substantive read evidence is provided.
  EVIDENCE: context_compass/AGENTS.MD:20-24, context_compass/AGENTS.MD:68-68, context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md:10-10, context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md:56-56, context_compass/agent_onboarding/agent/general/skills/self_certification.md:8-9
  IMPACT: A single-command onboarding shortcut is compatible only if it remains a bootstrap step and preserves substantive-read + read-integrity proof requirements.
  NEXT: Add a canonical single-command PowerShell pattern to the in-scope onboarding docs without weakening current enforcement language.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Current re-onboarding attestation contract explicitly requires listing files re-read in the attestation body, which drives large token output during compliance reporting.
  EVIDENCE: context_compass/AGENTS.MD:17-20, context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md:39-43
  IMPACT: To reduce token usage while preserving proof, policy needs a compact attestation mode that references a deterministic onboarding readset.
  NEXT: Patch AGENTS and compaction requirements to support ticket-only `FILES_REREAD` plus readset reference, then add manifest + script.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: The current single-command bootstrap wording is PowerShell-only, so Linux shells still lack an equivalent canonical onboarding readset command.
  EVIDENCE: context_compass/AGENTS.MD:71-72, context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md:31-34, context_compass/agent_onboarding/agent/general/SKILLS.md:49-53, context_compass/agent_onboarding/agent/general/skills/self_certification.md:8-10
  IMPACT: Cross-platform onboarding consistency is incomplete.
  NEXT: Add a Bash/Linux readset script and update all affected docs to include both commands.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Onboarding policy now supports compact re-onboarding attestation (`FILES_REREAD` focused on active tickets + `ONBOARDING_READSET` reference) and cross-platform single-command bootstrap commands (PowerShell and Bash), backed by a canonical readset manifest and two scripts.
  EVIDENCE: context_compass/AGENTS.MD:20-20, context_compass/AGENTS.MD:72-74, context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md:32-35, context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md:53-55, context_compass/agent_onboarding/agent/general/SKILLS.md:49-58, context_compass/agent_onboarding/agent/general/skills/self_certification.md:9-17, context_compass/agent_onboarding/agent/general/skills/onboarding_read_paths.txt:5-65, context_compass/agent_onboarding/agent/general/skills/run_onboarding_read.ps1:2-75, context_compass/agent_onboarding/agent/general/skills/run_onboarding_read.sh:1-121
  IMPACT: Re-onboarding overhead is reduced without weakening anti-performative read requirements, and onboarding bootstrap is now cross-platform.
  NEXT: Run validation commands and record execution status (including Linux script environment constraints, if any).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: PowerShell readset script executes successfully (`READSET_COMPLETE: 61 files processed`), while Bash script execution is blocked in this Windows environment by `Bash/Service/CreateInstance/E_ACCESSDENIED`.
  EVIDENCE: context_compass/artifacts/2026-02-15_onboarding_readset_script_validation.txt:3-6
  IMPACT: Windows-path validation is complete; Linux script behavior is implemented but not executable in this host runtime.
  NEXT: Ask user to confirm acceptance criteria for this policy/tooling update.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Implementation is complete and review-ready. The change adds compact attestation guidance and cross-platform onboarding readset scripts (`.ps1` + `.sh`) with a shared manifest; PowerShell script was validated, Bash execution is environment-blocked on this host.
