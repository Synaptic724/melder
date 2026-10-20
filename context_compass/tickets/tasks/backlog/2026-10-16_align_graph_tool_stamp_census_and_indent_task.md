# Task: align_graph_tool_stamp_census_and_indent - the extractor's census and indent disagree with the walker

## Metadata
- Task ID: TASK-2026-10-16-align_graph_tool_stamp_census_and_indent
- Story: none (standalone backlog task; found during EPIC-2026-10-14-managed_spell_quantity S7)
- Status: ready
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p3
- Created: 2026-10-16T00:52:02Z
- Updated: 2026-10-16T00:52:02Z

## Objective
`extract_graph.py` counts a node accepted with an empty stamp (module nodes) as unverified because it tests the stamp
for truthiness, while `graph_walker.py` tests for the key and counts it AUTHORED, so the extractor's census line
overstates stale nodes. The extractor also writes descriptors with `indent=1` while the walker's `--accept` writes
`indent=2`, so every accept rewrites whole descriptor files. Make the extractor test the key and both write one indent.

## Ticket Contract
- ENTRY_GATE: an active board row; the owner's go-ahead to change the shipped package tools locally.
- EXECUTION_BOUNDARY: `context_compass/tools/system_documents/python/extract_graph.py` and `graph_walker.py`, their
  tests.
- DEPENDENCIES: none.
- EXIT_GATE: one stamp rule and one indent in both tools, tests for both, a re-extraction that leaves accepted
  descriptors byte-identical.
- FAILURE_ESCALATION: DECISION_REQUEST if the fix belongs upstream in the package rather than in this install.

## Scope Boundaries
- In scope: the two graph tools.
- Out of scope: the descriptors' content.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: found in EPIC-2026-10-14-managed_spell_quantity S7 and evidenced below; parked in the backlog at
  the owner's direction ("if you found more bugs just add tickets", 2026-10-16).

## Steps / Checklist
- [ ] Make the extractor's census test the stamp key, as the walker's `state_of` does.
- [ ] Pick one indent for both writers; re-extract once to normalize.
- [ ] Test both rules.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- Tools that agree on what a verified node is and write descriptors one way.

## Files / Paths Impacted
- context_compass/tools/system_documents/python/extract_graph.py
- context_compass/tools/system_documents/python/graph_walker.py

## Validation
- Not run.
- Recommended commands:
  - `python context_compass/tools/system_documents/python/extract_graph.py --src src --out context_compass/system_docs/graph --check`

## Risks / Rollback Notes
- Re-indenting rewrites every descriptor once; do it in its own change.

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
  CLAIM: The extractor's census uses `if not stamp` where the walker's `state_of` tests `STAMP not in node` (its comment
    explains why); the extractor writes `indent=1`, the walker's accept writes `indent=2`.
  EVIDENCE:
  - context_compass/tools/system_documents/python/extract_graph.py:497-517
  - context_compass/tools/system_documents/python/extract_graph.py:654-662
  - context_compass/tools/system_documents/python/graph_walker.py:91-117
  - context_compass/tools/system_documents/python/graph_walker.py:268-268
  - context_compass/tools/system_documents/python/graph_walker.py:347-347
  IMPACT: The census overstated stale nodes (238 against the walker's 166 on 2026-10-15), and every accept churns
    whole descriptor files.
  NEXT: Ask the owner whether to change the shipped tools here or upstream.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
- Scope: align two graph tools. State: ready, unassigned, parked in the backlog.
- Next: the owner says where the tool fix belongs; then an agent opens a board row.

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
