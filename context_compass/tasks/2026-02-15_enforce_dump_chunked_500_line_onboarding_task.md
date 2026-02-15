# Task: Enforce Dump-First 500-Line Chunked Onboarding (Non-Performative)

## Metadata
- Task ID: TASK-2026-02-15-enforce-dump-chunked-500-line-onboarding
- Story: standalone
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-02-15
- Updated: 2026-02-15

## Objective
Make onboarding/re-onboarding dump consumption deterministic and non-performative by generating parallel chunk files in `context_compass/agent_onboarding/parallel_read_onboarding_dump/` named `onboarding_read_01`, `onboarding_read_02`, etc, and requiring full sequential `500`-line coverage before attestation.

## Scope Boundaries
- In scope:
- Add build tooling for `parallel_read_onboarding_dump` chunk artifacts at `500` lines per file.
- Add manifest-based integrity/coverage validation without Python dependency.
- Add/read tooling helpers to consume chunk files by ordinal (`onboarding_read_01`, `onboarding_read_02`, ...).
- Update policy language to reference the new parallel dump path/naming.
- Out of scope:
- Runtime/library behavior outside onboarding policy/scripts.
- Non-onboarding workflow redesign.

## Steps / Checklist
- [x] Create active task and route `attention_board.md`.
- [x] Add parallel dump build script(s) that output `onboarding_read_XX` chunk files under `agent_onboarding/parallel_read_onboarding_dump/`.
- [x] Add non-Python manifest validation script(s) for freshness/hash compliance.
- [x] Add chunk-read helper script(s) over `onboarding_read_XX` files.
- [x] Update onboarding/re-onboarding policy docs to reference the new path/naming.
- [x] Validate helper commands and policy references.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Parallel dump chunk artifact set under `context_compass/agent_onboarding/parallel_read_onboarding_dump/` with naming `onboarding_read_XX`.
- Manifest metadata including build timestamp and source/chunk hashes.
- Non-Python validation + chunk-read helper scripts and updated policy references.

## Files / Paths Impacted
- `context_compass/attention_board.md`
- `context_compass/tasks/2026-02-15_enforce_dump_chunked_500_line_onboarding_task.md`
- `context_compass/AGENTS.MD`
- `context_compass/agent_onboarding/agent/general/SKILLS.md`
- `context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md`
- `context_compass/agent_onboarding/agent/general/skills/self_certification.md`
- `context_compass/agent_onboarding/agent/general/skills/build_parallel_read_onboarding_dump.ps1`
- `context_compass/agent_onboarding/agent/general/skills/build_parallel_read_onboarding_dump.cmd`
- `context_compass/agent_onboarding/agent/general/skills/build_parallel_read_onboarding_dump.sh`
- `context_compass/agent_onboarding/agent/general/skills/validate_parallel_read_onboarding_dump.ps1`
- `context_compass/agent_onboarding/agent/general/skills/validate_parallel_read_onboarding_dump.cmd`
- `context_compass/agent_onboarding/agent/general/skills/validate_parallel_read_onboarding_dump.sh`
- `context_compass/agent_onboarding/agent/general/skills/read_parallel_read_onboarding_chunk.ps1`
- `context_compass/agent_onboarding/agent/general/skills/read_parallel_read_onboarding_chunk.cmd`
- `context_compass/agent_onboarding/agent/general/skills/read_parallel_read_onboarding_chunk.sh`
- `context_compass/agent_onboarding/parallel_read_onboarding_dump/`
- `context_compass/artifacts/2026-02-15_dump_chunked_onboarding_validation.txt`
- `context_compass/artifacts/2026-02-15_parallel_read_onboarding_validation.txt`

## Validation
- Completed:
  - built parallel dump artifacts with `build_parallel_read_onboarding_dump.cmd`
  - validated manifest/source/chunk hashes and freshness with `validate_parallel_read_onboarding_dump.cmd`
  - verified sequential chunk coverage via chunk summaries (`onboarding_read_01` and `onboarding_read_18`)
  - Linux/Bash validation command attempted and host-restricted (`E_ACCESSDENIED`)
  - evidence: `context_compass/artifacts/2026-02-15_parallel_read_onboarding_validation.txt`

## Risks / Rollback Notes
- Risk: over-prescriptive policy could conflict with future tool limits.
- Mitigation: keep `500` as required default with explicit fallback only when truncation is evidenced.

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
  TYPE: ALIGNMENT_CHECK
  CLAIM: User requested onboarding enforcement for dump-first sequential iteration in `500`-line chunks and explicitly called out performative compliance risk after compaction.
  EVIDENCE: context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md:8-11, context_compass/AGENTS.MD:20-24
  IMPACT: Policy and tooling need deterministic chunk-coverage rules, not just generic anti-performative wording.
  NEXT: Add active routing, then patch scripts/docs to codify sequential `500`-line chunk coverage plus attestation proof.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Existing dump tooling validates dump freshness/integrity and then emits entire content, which can exceed tool output limits and force manual chunking.
  EVIDENCE: context_compass/agent_onboarding/agent/general/skills/read_onboarding_dump.ps1:244-256, context_compass/agent_onboarding/agent/general/skills/read_onboarding_dump.sh:249-254
  IMPACT: A dedicated chunk-reader command is required for reliable, repeatable dump-first onboarding.
  NEXT: Implement chunk-reader helper scripts with default chunk size `500` and chunk index controls.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Implemented dump chunk-reader helpers (`.ps1`, `.cmd`, `.sh`) and codified mandatory sequential `500`-line dump consumption with attestation chunk-coverage proof across onboarding policy docs.
  EVIDENCE: context_compass/agent_onboarding/agent/general/skills/read_onboarding_dump_chunk.ps1:1-87, context_compass/agent_onboarding/agent/general/skills/read_onboarding_dump_chunk.cmd:1-5, context_compass/agent_onboarding/agent/general/skills/read_onboarding_dump_chunk.sh:1-147, context_compass/AGENTS.MD:21-28, context_compass/AGENTS.MD:76-87, context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md:31-60, context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md:79-95, context_compass/agent_onboarding/agent/general/skills/self_certification.md:13-36, context_compass/agent_onboarding/agent/general/SKILLS.md:54-79
  IMPACT: Re-onboarding now has deterministic dump-first chunking behavior and explicit anti-performative enforcement after compaction.
  NEXT: Run validation commands, capture outputs in artifact, and request user acceptance for closure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Validation confirms dump validation succeeds and sequential chunk iteration covers the full dump range at `chunk_size=500` (`chunk indexes 0..17`, lines `1..8779`); Windows chunk reads succeed while Bash execution is host-blocked.
  EVIDENCE: context_compass/artifacts/2026-02-15_dump_chunked_onboarding_validation.txt:1-177
  IMPACT: Enforcement workflow is operational in this environment and explicitly documents Linux runtime limitation.
  NEXT: Ask user to confirm acceptance criteria and whether to close/move the task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: DECISION
  CLAIM: User directed a new canonical structure: move to `context_compass/agent_onboarding/parallel_read_onboarding_dump/`, name chunks `onboarding_read_01`, `onboarding_read_02`, etc, and skip Python validator to avoid Python dependency.
  EVIDENCE: context_compass/tasks/2026-02-15_enforce_dump_chunked_500_line_onboarding_task.md:1-108
  IMPACT: Prior single-dump chunk helper approach is superseded; task scope is expanded to implement path/naming and non-Python validation.
  NEXT: Implement parallel-dump build/validate/read scripts and patch policy docs accordingly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Non-Python parallel-dump scripts validate successfully and chunk reads resolve correctly end-to-end (`manifest`, chunk `01`, chunk `18`) against `parallel_read_onboarding_dump`.
  EVIDENCE: context_compass/artifacts/2026-02-15_parallel_read_onboarding_validation.txt:1-31
  IMPACT: Earlier manifest-resolution failure is not reproducible in the current workspace; remaining work is policy/doc reference alignment.
  NEXT: Replace legacy `read_onboarding_dump*` / `build_onboarding_dump*` canonical references with the parallel dump build/validate/read command set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Canonical onboarding policy docs now reference `parallel_read_onboarding_dump` with `onboarding_read_XX` chunk sequencing and non-Python build/validate/read commands as the dump bootstrap path.
  EVIDENCE: context_compass/AGENTS.MD:24-88, context_compass/agent_onboarding/agent/general/SKILLS.md:48-80, context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md:32-59, context_compass/agent_onboarding/agent/general/skills/self_certification.md:9-34
  IMPACT: Onboarding guidance is aligned with user-directed architecture and no longer relies on Python validator assumptions.
  NEXT: Rebuild dump artifacts and capture final validation evidence after doc changes in readset files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Final post-doc-change validation passes with chunk size `500`, total chunks `18`, total lines `8690`, and sequential chunk boundaries confirmed at chunk `1` and chunk `18`.
  EVIDENCE: context_compass/artifacts/2026-02-15_parallel_read_onboarding_validation.txt:1-40
  IMPACT: The parallel-dump onboarding flow is currently consistent and executable in this workspace.
  NEXT: Request user acceptance on this task and then perform ticket-closure flow if approved.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: MEASURE
  CLAIM: Linux/Bash validation path is currently blocked in this environment (`Bash/Service/CreateInstance/E_ACCESSDENIED`), so only Windows command paths were runtime-validated here.
  EVIDENCE: context_compass/artifacts/2026-02-15_parallel_read_onboarding_validation.txt:42-46
  IMPACT: Cross-platform script syntax remains unverified in this host despite implementation parity.
  NEXT: Ask user to run the Bash command in a Linux-capable environment if cross-platform runtime confirmation is required.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active: implementation and validation are complete for user-directed parallel-dump onboarding (`onboarding_read_XX`, non-Python validation); pending user acceptance/closure decision.
