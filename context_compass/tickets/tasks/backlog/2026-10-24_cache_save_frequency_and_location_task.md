# Task: Fewer meld-time cache saves and a cache root outside the package

## Metadata
- Task ID: TASK-2026-10-24-cache_save_frequency_and_location
- Story: none (standalone backlog task; directions 3 and 4 of TASK-2026-10-24-cache_file_write_failure_fails_meld)
- Status: draft
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p3
- Created: 2026-10-24T21:32:03Z
- Updated: 2026-10-24T21:32:03Z

## Objective
Two follow-ups of the best-effort cache save (0.2.8266), each the owner's call (directions 3 and 4 of the fix's
DECISION_REQUEST, Note 10 of TASK-2026-10-24-cache_file_write_failure_fails_meld):
- Fewer saves: a meld that stages new plans rewrites the whole bundle before it returns - the failing MelderOps
  configure wrote one bundle twice within 1 ms. Save at conjure end, then at most once per short interval or at the
  Book's teardown, so most melds never touch the disk.
- Location and growth: the cache root is a fragment under the package root, so every process of an install
  writes into site-packages (read-only in a system install, watched by scanners on Windows), and frame folders
  are never pruned (55 per-trial folders, 5.9 MB, in the MelderOps venv). Allow an absolute or per-user root,
  and prune the folders a run will not reuse.
Both are recorded with source evidence in the fix ticket (Notes 3, 4 and 10); re-read the source at pickup.

## Ticket Contract
- ENTRY_GATE: the owner picks either, both or neither, and the shape (an interval or the Book's teardown; the
  root's form; the pruning rule); an active board row; the patch gate (the save points and the cache location are
  boundary changes).
- EXECUTION_BOUNDARY: `CachingSystem` and its caller's save seam (`Spellbook._emit_cache_file_if_required`,
  `_emit_cache_file`), the cache-root option of the frame configuration and its resolution; their tests; the
  system documents; the release note; one notch per src change; the rebuild last.
- DEPENDENCIES: TASK-2026-10-24-cache_file_write_failure_fails_meld (completed, 0.2.8266: a refused save is
  harmless, so neither follow-up is a correctness fix).
- EXIT_GATE: the chosen behaviour with red-then-green tests, the GIL off and on; documents, release note, notch
  and rebuild done.
- FAILURE_ESCALATION: DECISION_REQUEST for any change to when a bundle is on disk (a crash between coalesced saves
  loses only accelerator state, but another process reads an older bundle for longer).

## Scope Boundaries
- In scope: when the creation cache is saved; where it lives; pruning frame folders.
- Out of scope: the cache format and its admission rules; the bind-guard and agent-documentation asset caches;
  the Crystallizer's cache.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: created as a parked follow-up at the fix's closure; the owner's go took directions 1 and 2
  and left 3 and 4 as follow-ups (Notes 19-21 of TASK-2026-10-24-cache_file_write_failure_fails_meld);
  no lane is opened.

## Steps / Checklist
- [ ] The owner's calls (ENTRY_GATE); a board row; the patch gate.
- [ ] Red tests for the chosen behaviour (a meld after the conjure-end save writes nothing until the interval or
      the teardown; a root outside the package is written and read back; a pruned folder is one no run reuses).
- [ ] The change; green with the GIL off and on; the fix lane's probe re-run.
- [ ] Documents, release note, notch, NOTICEs; closure; the rebuild last.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- The chosen save points and cache location, with tests, documents and the release note.

## Files / Paths Impacted
- src/melder/utilities/caching_system/caching_system.py
- src/melder/aether/spellbook/spellbook.py (the save seam)
- src/melder/aether/aetheric_frame/aetheric_frame_configuration.py (the cache root)
- their tests; context_compass/system_docs/src_architecture.md, src_components.md; release_docs/next_version_release.md

## Validation
- Not run.
- Recommended commands:
  - VM, against a copy of the tree:
    `python -X gil=0 -m pytest -q tests/unit/melder/utilities tests/component/melder/spellbook`

## Risks / Rollback Notes
- Coalescing changes when another process sees a new bundle; a moved root makes every existing bundle cold once.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; this ticket, at the closure of
  TASK-2026-10-24-cache_file_write_failure_fails_meld; 2026-10-24.
- Published By: UNKNOWN (local repository; not published)
- Independent Review: none requested

## Notes
- DATETIME: 2026-10-24T21:32:03Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The fix's DECISION_REQUEST (its Note 10) offered four directions; the owner's go took 1 and 2 (its
    Note 21), so 3 (fewer meld-time saves) and 4 (the cache root and pruning) stand as follow-ups. Notes 3
    and 4 there carry the source evidence: the root is a fragment under the package root, and the failing
    configure wrote one bundle twice within 1 ms.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-10-24_cache_file_write_failure_fails_meld_task.md:256-274
  - context_compass/tickets/tasks/completed/2026-10-24_cache_file_write_failure_fails_meld_task.md:276-302
  - context_compass/tickets/tasks/completed/2026-10-24_cache_file_write_failure_fails_meld_task.md:400-429
  - context_compass/tickets/tasks/completed/2026-10-24_cache_file_write_failure_fails_meld_task.md:693-711
  IMPACT: Neither is a correctness fix since 0.2.8266; both cut disk writes and site-packages growth.
  NEXT: The owner's calls in the ENTRY_GATE.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Draft, parked: directions 3 and 4 of the cache-save fix (Objective), each waiting for the owner's call. Evidence:
the FACT note above and Notes 3, 4 and 10 of the fix ticket.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
