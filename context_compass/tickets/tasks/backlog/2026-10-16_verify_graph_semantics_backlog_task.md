# Task: verify_graph_semantics_backlog - re-verify stale graph prose, author unsemantic nodes, settle retired ones

## Metadata
- Task ID: TASK-2026-10-16-verify_graph_semantics_backlog
- Story: none (standalone backlog task; found during EPIC-2026-10-14-managed_spell_quantity S7)
- Status: ready
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p3
- Created: 2026-10-16T00:52:02Z
- Updated: 2026-10-16T00:52:02Z

## Objective
The source graph carries 144 SEMANTICS_STALE nodes (prose not re-checked since its source moved, 8 of them in classes
the managed lane changed), 9 UNSEMANTIC nodes and 5 RETIRED ones. Read each node's source, update its prose, accept
what holds, author the unsemantic nodes and adjudicate the retired ones, then reassemble.

## Ticket Contract
- ENTRY_GATE: an active board row; the walker's report re-run on the current tree.
- EXECUTION_BOUNDARY: `context_compass/system_docs/graph/` descriptors and the assembled graph and index.
- DEPENDENCIES: none; may be split per package (graph_semantics_tickets.py dry run first).
- EXIT_GATE: the walker reports no SEMANTICS_STALE, UNSEMANTIC or RETIRED node, or each remaining one carries a
  recorded reason; the graph reassembled; the rebuild last (the graph ships in the system-document payloads).
- FAILURE_ESCALATION: DECISION_REQUEST for the split if the backlog is too large for one pass.

## Scope Boundaries
- In scope: the graph's authored tier.
- Out of scope: source changes.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: found in EPIC-2026-10-14-managed_spell_quantity S7 and evidenced below; parked in the backlog at
  the owner's direction ("if you found more bugs just add tickets", 2026-10-16).

## Steps / Checklist
- [ ] Re-run the walker's report; split per package if needed.
- [ ] For each node: read the source, update or confirm the prose, accept; author unsemantic nodes; adjudicate retired.
- [ ] Re-extract with --strict, assemble, rebuild last.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- A graph whose authored prose was checked against today's source.

## Files / Paths Impacted
- context_compass/system_docs/graph/
- context_compass/system_docs/src_graph.md and src_graph_index.md

## Validation
- Not run.
- Recommended commands:
  - `python context_compass/tools/system_documents/python/graph_walker.py --descriptors context_compass/system_docs/graph --src src --report`

## Risks / Rollback Notes
- Accepting without reading is how a graph becomes confidently wrong; read every node's source first.

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
  CLAIM: After the 2026-10-15 reassembly the walker reports AUTHORED 1074, SEMANTICS_STALE 144, UNSEMANTIC 9 and
    RETIRED 5 (the retired: dag_index and ManyOnlyCodegenPlanTargetKind); the managed lane added none of them.
  EVIDENCE:
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_graph_walker_after.txt:1-110
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_graph_census_after.txt:1-169
  IMPACT: Stale prose reads exactly like current prose; an agent slicing the graph cannot tell them apart.
  NEXT: Re-run the walker's report on the current tree and decide the split.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
- Scope: verify the graph's authored tier. State: ready, unassigned, parked in the backlog.
- Next: an assigned agent opens a board row and re-runs the walker's report.

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
