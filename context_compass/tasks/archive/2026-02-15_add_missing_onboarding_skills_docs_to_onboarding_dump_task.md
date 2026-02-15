# Task: Add Missing Onboarding/Skills Docs to Onboarding Dump

- Completed: 2026-02-15
- Summary: Expanded onboarding readset manifest from 61 to 81 paths by adding the 20 previously missing onboarding/skills Markdown docs.
- Summary: Rebuilt onboarding dump and validated clean parity (`81/81`, no missing/extra, `20/20` previously missing now present).

## Metadata
- Task ID: TASK-2026-02-15-add-missing-onboarding-skills-docs-to-onboarding-dump
- Story: standalone
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-15
- Updated: 2026-02-15

## Objective
Ensure all currently missing onboarding/skills Markdown documents are included in the canonical onboarding dump via the readset manifest.

## Scope Boundaries
- In scope:
- Add missing onboarding/skills Markdown doc paths to `onboarding_read_paths.txt`.
- Rebuild `onboarding_read_dump.txt`.
- Validate manifest and dump path parity with zero missing/extra entries.
- Out of scope:
- Broad onboarding-policy rewrites.
- Non-onboarding repository docs.

## Steps / Checklist
- [x] Create task routing and board routing for this work item.
- [x] Capture pre-change dump coverage audit artifact.
- [x] Add missing Markdown document paths to onboarding manifest.
- [x] Rebuild onboarding dump from updated manifest.
- [x] Capture post-change dump coverage audit artifact and confirm parity.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Updated onboarding manifest including missing onboarding/skills Markdown docs.
- Rebuilt onboarding dump aligned with updated manifest.
- Coverage audit evidence showing no missing entries.

## Files / Paths Impacted
- `context_compass/agent_onboarding/agent/general/skills/onboarding_read_paths.txt`
- `context_compass/agent_onboarding/agent/general/skills/onboarding_read_dump.txt`
- `context_compass/attention_board.md`
- `context_compass/tasks/2026-02-15_add_missing_onboarding_skills_docs_to_onboarding_dump_task.md`
- `context_compass/artifacts/2026-02-15_onboarding_dump_coverage_audit_pre.txt`
- `context_compass/artifacts/2026-02-15_onboarding_dump_coverage_audit_post.txt`

## Validation
- Ran:
  - `context_compass/agent_onboarding/agent/general/skills/build_onboarding_dump.cmd`
  - coverage parity audit script writing `context_compass/artifacts/2026-02-15_onboarding_dump_coverage_audit_post.txt`
- Results:
  - Dump rebuild succeeded with `ONBOARDING_DUMP_FILES: 81`.
  - Post-audit confirms `MANIFEST_COUNT=81`, `DUMP_BEGIN_COUNT=81`, `MISSING_FROM_DUMP_COUNT=0`, `EXTRA_IN_DUMP_COUNT=0`, `MISSING_MD_IN_DUMP_COUNT=0`.
  - Recheck against the exact prior-missing list confirms `PREVIOUSLY_MISSING_COUNT=20`, `NOW_PRESENT_COUNT=20`, `STILL_MISSING_COUNT=0`.

## Risks / Rollback Notes
- Risk: adding recursive/self-reference files could bloat or destabilize dump generation.
- Mitigation: include only missing Markdown docs from onboarding/skills audit list.

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
  TYPE: PLAN
  CLAIM: Execute focused manifest expansion for missing onboarding/skills Markdown docs, rebuild dump, and prove parity with explicit counts and file-list evidence.
  EVIDENCE: context_compass/attention_board.md:16-24, context_compass/agent_onboarding/agent/general/skills/onboarding_read_paths.txt:1-64
  IMPACT: Keeps dump coverage deterministic and prevents policy/readset drift for onboarding.
  NEXT: Capture pre-change coverage artifact and append findings before editing manifest.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Pre-change audit confirms canonical manifest and dump are in parity (61/61), but 20 Markdown docs under onboarding/skills are missing from dump coverage and must be added to the manifest.
  EVIDENCE: context_compass/artifacts/2026-02-15_onboarding_dump_coverage_audit_pre.txt:1-27
  IMPACT: Onboarding dump currently omits onboarding/skills docs that user expects to be part of canonical read coverage.
  NEXT: Append the 20 missing Markdown paths to onboarding manifest and rebuild dump.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Added all 20 previously missing onboarding/skills Markdown paths to the canonical manifest, increasing manifest entries from 61 to 81.
  EVIDENCE: context_compass/agent_onboarding/agent/general/skills/onboarding_read_paths.txt:12-79, context_compass/artifacts/2026-02-15_onboarding_dump_coverage_audit_pre.txt:2-7
  IMPACT: The readset now includes the previously omitted onboarding and skills documents requested by the user.
  NEXT: Rebuild onboarding dump and verify manifest-to-dump parity and Markdown coverage.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Post-change rebuild and parity audit pass with zero manifest/dump drift and zero missing onboarding/skills Markdown docs.
  EVIDENCE: context_compass/agent_onboarding/agent/general/skills/onboarding_read_dump.txt:1-8, context_compass/artifacts/2026-02-15_onboarding_dump_coverage_audit_post.txt:1-10
  IMPACT: The onboarding dump now fully covers the audited onboarding/skills Markdown document set.
  NEXT: Move task to review and ask user to confirm acceptance criteria.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Task completed and user-approved for closure. Manifest expansion and dump rebuild are complete, with post-audit showing no missing onboarding/skills Markdown docs.
