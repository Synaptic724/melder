

# Task: Author special_instructions/agent_contribution_guide.md (0.0001 notch, release and asset rules)

## Metadata
- Task ID: TASK-2026-09-27-author-agent-contribution-guide
- Story: none (owner-directed policy document)
- Status: done
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-27T19:24:24Z
- Updated: 2026-09-27T19:24:24Z
- Completed: 2026-09-27T19:24:24Z
- Summary: `context_compass/special_instructions/agent_contribution_guide.md` written (92 lines): the per-ticket
  0.0001 notch in the owner's decimal reading (`0.2.82` -> `0.2.8201`; releases at `xx00`), the running release
  note and how it is cut, generated assets rebuilt as the last step, and the turn-in order. No notch taken:
  the 0.2.82 release is in its frozen window (cut, not yet committed or published).

## Objective
Owner directive (2026-09-27T19:24:24Z): pen the versioning change (0.0001 per epic, story or task instead of
0.01), define
the release rules, and put it in `special_instructions/` as `agent_contribution_guide.md`. The owner answered
the one open question in chat: the notch is literal decimal digits in the third segment (`0.2.8201`), not a
fourth segment.

## Ticket Contract
- ENTRY_GATE: owner directive; the survey of the existing surfaces (no policy document covered versioning).
- EXECUTION_BOUNDARY: one new file under `context_compass/special_instructions/`; this ticket; the boards.
- DEPENDENCIES: `context_compass/AGENTS.MD` (special instructions outrank role defaults); `docs/maintaining.md`
  (asset commands); the version-format test `tests/unit/melder/test_package_version_metadata.py:20`.
- EXIT_GATE: the document exists, lines within the 120-char cap, relative paths only; owner reads it.
- FAILURE_ESCALATION: none.

## Scope Boundaries
- In scope: the guide.
- Out of scope: a notch (frozen window), renumbering history, changing tools or tests.

## State Transition Event
- from_state: draft
- to_state: done
- transition_reason: Written and closed in one pass on the owner's directive (2026-09-27T19:24:24Z); closure
  pre-approved.

## Steps / Checklist
- [x] Survey: no policy, skill, special instruction or repo doc defined notching or the release note.
- [x] Owner's ruling on the notch shape taken in chat (literal decimal digits).
- [x] Guide written; line cap checked.
- [x] Run Ticket Microcycle during execution.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- context_compass/special_instructions/agent_contribution_guide.md

## Files / Paths Impacted
- context_compass/special_instructions/agent_contribution_guide.md (new)

## Validation
- Not run (a Markdown policy document). `tests/unit/melder/test_package_version_metadata.py:20` accepts the
  four-digit third segment (`\d+\.\d+\.\d+`), checked by reading the regex.

## Risks / Rollback Notes
- Delete the file to roll back; nothing else references it.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No closure without acceptance confirmation and board-sync completion (owner pre-approved closure).

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed (owner directive; closure pre-approved)
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: versioning; release process; generated assets.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-27T19:24:24Z
  TYPE: DECISION
  CLAIM: Owner rulings recorded in the guide: 0.0001 per ticket (epic, story, task alike) as literal decimal
    digits of the third segment (`0.2.82` reads `0.2.8200`, next notch `0.2.8201`; a release is the next
    hundredth `xx00`, so `0.2.8300`; a rollover to `0.2.8300` before a cut makes the release `0.2.8400`);
    the running note is `release_docs/next_version_release.md`, header follows `__version__`, cut files are
    never edited; releases are cut only on the owner's word with the assets rebuilt last; a frozen window
    between cut and publish where nobody notches. Survey basis: grep of AGENTS.MD, SKILLS.MD, the three role
    folders, special_instructions, CONTRIBUTING.md, README.md and docs/maintaining.md found no versioning or
    release-note rule; the only prior instruction was the owner's 2026-09-26 board note.
  EVIDENCE:
  - special_instructions/agent_contribution_guide.md:1-92
  - attention_board.md (search `### Versioning (owner, 2026-09-26)`)
  - tests/unit/melder/test_package_version_metadata.py:20-20
  IMPACT: The 0.01 board note is superseded by the guide; the board note should be retired or pointed at it.
  NEXT: none (owner reads the guide; the board note is updated in this pass to point at it).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
STATE 2026-09-27T19:24:24Z: DONE. Guide written and closed in one pass; no notch (frozen window for the 0.2.82 release).

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
