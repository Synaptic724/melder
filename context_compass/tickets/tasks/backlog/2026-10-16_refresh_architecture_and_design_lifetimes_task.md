# Task: refresh_architecture_and_design_lifetimes - the design pages list six lifetimes; Melder has seven

## Metadata
- Task ID: TASK-2026-10-16-refresh_architecture_and_design_lifetimes
- Story: none (standalone backlog task; found during EPIC-2026-10-14-managed_spell_quantity S7)
- Status: ready
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p2
- Created: 2026-10-16T00:52:02Z
- Updated: 2026-10-16T00:52:02Z

## Objective
`architecture_and_design/02_architecture/ownership_and_lifetimes.md` and
`architecture_and_design/05_engineering_drawings/README.md` (with their drawings) list six Existence members, and
both are stamped "Verified against: Melder 0.1.2". Re-verify the set against the current source, add
`managed_spell_quantity`, and restamp only what was actually checked.

## Ticket Contract
- ENTRY_GATE: an active board row; the pages read whole with the source they describe.
- EXECUTION_BOUNDARY: `architecture_and_design/` (pages, mermaid and svg drawings).
- DEPENDENCIES: none.
- EXIT_GATE: every claim on the touched pages checked against the source, the stamp naming the version checked;
  the docs tests green; the rebuild last (the LLM bundles include these pages).
- FAILURE_ESCALATION: DECISION_REQUEST if re-verifying the whole set is larger than the owner wants; the owner may
  prefer a narrower stamp.

## Scope Boundaries
- In scope: the lifetime pages and drawings of `architecture_and_design/`.
- Out of scope: the rest of the set unless the stamp requires it.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: found in EPIC-2026-10-14-managed_spell_quantity S7 and evidenced below; parked in the backlog at
  the owner's direction ("if you found more bugs just add tickets", 2026-10-16).

## Steps / Checklist
- [ ] Read both pages and their drawings whole; list every claim and check it against the source.
- [ ] Add the seventh member and fix any claim that moved since 0.1.2; regenerate the drawings.
- [ ] Restamp with the version and commit actually checked; rebuild last.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- Pages that list all seven lifetimes and a stamp that is true.

## Files / Paths Impacted
- architecture_and_design/02_architecture/ownership_and_lifetimes.md
- architecture_and_design/05_engineering_drawings/README.md and its mermaid/svg drawings

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest docs/tests -q -p no:cacheprovider` (with Sphinx from docs/requirements.lock)
  - `python llm_support/_builder.py --check --include-untracked`

## Risks / Rollback Notes
- A stamp widened beyond what was read would make it false; restamp only what was checked.

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
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; created 2026-10-16T00:52:02Z; evidence in Notes.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-16T00:52:02Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Both pages are stamped as verified against Melder 0.1.2 and list six lifetimes; the seventh,
    `managed_spell_quantity`, landed in 0.2.8241-0.2.8246.
  EVIDENCE:
  - architecture_and_design/02_architecture/ownership_and_lifetimes.md:7-7
  - architecture_and_design/02_architecture/ownership_and_lifetimes.md:33-42
  - architecture_and_design/05_engineering_drawings/README.md:7-7
  - architecture_and_design/05_engineering_drawings/README.md:170-178
  IMPACT: Readers of the design set meet six lifetimes while the runtime has seven.
  NEXT: Read both pages and their drawings whole against the source.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
- Scope: re-verify the lifetime pages and add the seventh member. State: ready, unassigned, parked in the backlog.
- Next: an assigned agent opens a board row and reads both pages whole.

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
