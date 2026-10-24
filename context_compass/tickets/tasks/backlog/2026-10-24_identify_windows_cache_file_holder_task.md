# Task: Name what held the bundle open in the owner's WinError 5 failure

## Metadata
- Task ID: TASK-2026-10-24-identify_windows_cache_file_holder
- Story: none (standalone backlog task; the open HYPOTHESIS of TASK-2026-10-24-cache_file_write_failure_fails_meld)
- Status: draft
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p3
- Created: 2026-10-24T21:32:03Z
- Updated: 2026-10-24T21:32:03Z

## Objective
Find what refused the rename of `melderops.meldercache` with PermissionError [WinError 5] in the owner's MelderOps
run on 0.2.8265 (chat 2026-10-24). The fix recorded the cause as a HYPOTHESIS (Note 5 of
TASK-2026-10-24-cache_file_write_failure_fails_meld): Windows refuses a rename onto a file another handle holds open
without FILE_SHARE_DELETE - an on-access scanner (Microsoft Defender), the Windows Search or an IDE indexer, a
reader in another process. Since 0.2.8266 the meld no longer fails and the rename is retried for about 100 ms;
this task names the holder and says whether that budget fits.

## Ticket Contract
- ENTRY_GATE: the owner runs it on his Windows machine (the VM cannot raise WinError 5); an active board row.
- EXECUTION_BOUNDARY: measurement only - the owner's MelderOps test with 0.2.8266 installed, and this ticket's
  Notes. A change the finding calls for gets a task of its own.
- DEPENDENCIES: TASK-2026-10-24-cache_file_write_failure_fails_meld (completed, 0.2.8266).
- EXIT_GATE: the holder named from a capture, or the refusal shown to stop with real-time scanning excluded; the
  rerun's WARNING count recorded.
- FAILURE_ESCALATION: DECISION_REQUEST when refusals outlast the retry budget often enough to matter.

## Scope Boundaries
- In scope: one or two reruns on the owner's machine and their record.
- Out of scope: changing the retry budget or the save frequency (TASK-2026-10-24-cache_save_frequency_and_location).

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: created as a parked follow-up at the fix's closure; the HYPOTHESIS of Note 5 of
  TASK-2026-10-24-cache_file_write_failure_fails_meld stays open; no lane is opened.

## Steps / Checklist
- [ ] With 0.2.8266 in priv_commandops/.venv314, from priv_commandops:
      `uv run pytest tests/benchmarks/postgres_row_transfer_v2/test_submission_batches.py -k list50 -x`;
      count the WARNING lines that start "Could not save the creation-cache bundle".
- [ ] Rerun under Process Monitor filtered on paths ending in .meldercache, to name the process holding the
      handle at the refused rename; or rerun with the venv excluded from real-time scanning.
- [ ] Record the MEASURE here; file a task when the budget or the save frequency should change.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- A MEASURE note naming the holder, or showing the refusal stops with scanning excluded.

## Files / Paths Impacted
- none in the repository (the owner's machine; this ticket's Notes)

## Validation
- Not run (the owner's machine).
- Recommended commands: the Steps above.

## Risks / Rollback Notes
- None in the repository; Process Monitor captures can be large - filter before recording.

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
  CLAIM: The holder behind WinError 5 is unmeasured: the fix ticket's Note 5 states it as a HYPOTHESIS with
    this verification, and its Note 4 records the evidence (two writes of one bundle 1 ms apart, inside one
    configure, in a frame unique to the trial; the orphaned temp file beside the bundle).
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-10-24_cache_file_write_failure_fails_meld_task.md:276-302
  - context_compass/tickets/tasks/completed/2026-10-24_cache_file_write_failure_fails_meld_task.md:304-322
  IMPACT: Without it the retry budget (about 100 ms) is a guess against the holder's hold time.
  NEXT: The owner's rerun (Steps).
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Draft, parked: the owner's rerun on Windows to name the holder behind WinError 5 (Objective); the fix makes the
refusal harmless either way. Evidence: the FACT note above and Notes 4-5 of the fix ticket.

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
