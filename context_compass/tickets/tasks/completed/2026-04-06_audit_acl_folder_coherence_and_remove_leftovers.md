# Task: Audit ACL Folder Coherence And Remove Leftovers
- Completed: 2026-04-06T12:17:44Z
- Summary: Accepted review slice moved out of the active lane during the 2026-04-06 board cleanup after the user advanced to later ACL/frame-surface work.


## Metadata
- Task ID: TASK-2026-04-06-audit-acl-folder-coherence-and-remove-leftovers
- Story: STORY-2026-04-02-profile-contracts-and-access-boundaries
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T02:15:00Z
- Updated: 2026-04-06T12:17:44Z

## Objective
Audit the full `src/melder/aether/nexus/acl/` folder for coherence after the
recent package split and remove any dead leftover modules or obviously invalid
boundaries.

## Ticket Contract
- ENTRY_GATE: the user explicitly called out duplicate ACL modules and
  requested a folder-wide sanity pass.
- EXECUTION_BOUNDARY: ACL-folder audit plus cleanup of clearly dead leftovers
  only.
- DEPENDENCIES:
  - src/melder/aether/nexus/acl/
  - src/melder/aether/nexus/frame_acl_manager.py
  - tests/unit/melder/aether/
- EXIT_GATE: the ACL folder has one clear source of truth per concept, dead
  leftovers are removed, and the affected ACL test surface still passes.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a suspicious duplicate turns
  out to be an intentional compatibility seam with real callers.

## Scope Boundaries
- In scope:
  - ACL-folder file inventory
  - duplicate/dead leftover detection
  - removal of clearly dead duplicate modules
  - smallest import/test updates required by the cleanup
- Out of scope:
  - new ACL features
  - frame-link folder cleanup
  - broad architectural redesign

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the task was turned in during the cleanup pass after the user advanced to later ACL/frame-surface work.
## Steps / Checklist
- [x] Inventory the ACL folder and identify duplicate or stale modules.
- [x] Prove whether each suspicious file has live imports or not.
- [x] Remove clearly dead leftovers.
- [x] Run focused ACL validation after cleanup.
- [x] Document findings, implementation, and validation in `## Notes`.

## Deliverables
- ACL folder audit findings
- removal of dead leftover ACL modules
- focused validation evidence

## Files / Paths Impacted
- src/melder/aether/nexus/acl/
- tests/unit/melder/aether/
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_profile.py tests/unit/melder/aether/test_frame_acl_profile_contract_matrix.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_configuration.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_nexus_frame_acl_profiles.py tests/unit/melder/aether/test_frame_acl_compiled_access_surface.py`

## Risks / Rollback Notes
- Risk: deleting a duplicate file that still has real callers would break
  imports.
  Rollback: only remove files once live-import checks show they are dead.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-06T02:15:00Z
  TYPE: PLAN
  CLAIM: The next bounded slice is an ACL-folder coherence audit. The user
    already found dead duplicates under `acl/profiles/` and another duplicate
    monolith at `acl/frame_acl_profile.py`. The correct next move is to inspect
    the whole ACL folder for split-brain leftovers, prove whether they have
    live callers, and then remove the dead ones instead of pretending they are
    compatibility layers.
  EVIDENCE:
  - user_instruction: "please go over all hte files there in the ACL folder and make sure that it all makes sense"
  - src/melder/aether/nexus/acl/profiles/frame_acl_profile.py:1-151
  - src/melder/aether/nexus/acl/frame_acl_profile.py:1-1968
  IMPACT: Cleanup should now target ACL folder coherence before further test
    expansion.
  NEXT: read the remaining ACL files and search for live imports of the
    suspicious duplicate modules.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T02:24:00Z
  TYPE: FACT
  CLAIM: The main ACL-folder coherence problem was dead refactor leftovers, not
    an active multi-implementation strategy. The canonical split is:
    - top-level ACL runtime objects for chain/container/config/builder/validator/compiler
    - reusable profile catalog under `acl/profiles/`
    The old duplicate top-level `safe_profile.py` / `hybrid_profile.py` /
    `permissive_profile.py` helpers and the old monolithic
    `acl/frame_acl_profile.py` file had no live import callers and were removed.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_configuration_chain.py:1-376
  - src/melder/aether/nexus/acl/frame_acl_container.py:1-271
  - src/melder/aether/nexus/acl/frame_acl_validator.py:1-378
  - src/melder/aether/nexus/acl/profiles/frame_acl_profile.py:1-151
  - src/melder/aether/nexus/acl/profiles/frame_acl_profile_builder.py:1-266
  - deleted:src/melder/aether/nexus/acl/profiles/safe_profile.py
  - deleted:src/melder/aether/nexus/acl/profiles/hybrid_profile.py
  - deleted:src/melder/aether/nexus/acl/profiles/permissive_profile.py
  - deleted:src/melder/aether/nexus/acl/frame_acl_profile.py
  IMPACT: The ACL folder now has one clear source of truth per profile concept
    instead of a split-brain package plus monolith.
  NEXT: run a focused ACL suite to prove the cleanup did not break imports or
    behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T02:26:00Z
  TYPE: MEASURE
  CLAIM: The ACL-folder cleanup is green on a focused ACL suite. After removing
    the dead top-level duplicate profile modules and the dead monolithic
    `acl/frame_acl_profile.py`, the focused ACL profile/config/builder/validator/
    compiled-surface unit surface still passed.
  EVIDENCE:
  - deleted:src/melder/aether/nexus/acl/profiles/safe_profile.py
  - deleted:src/melder/aether/nexus/acl/profiles/hybrid_profile.py
  - deleted:src/melder/aether/nexus/acl/profiles/permissive_profile.py
  - deleted:src/melder/aether/nexus/acl/frame_acl_profile.py
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_acl_profile.py tests/unit/melder/aether/test_frame_acl_profile_contract_matrix.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_configuration.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_nexus_frame_acl_profiles.py tests/unit/melder/aether/test_frame_acl_compiled_access_surface.py
  IMPACT: The ACL folder now has a cleaner single-source-of-truth layout and no
    immediate import fallout from the cleanup.
  NEXT: return to the broader ACL/frame-link test expansion lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to audit the ACL folder for dead leftovers and coherence
problems after the recent profile/config/compiler refactors.



