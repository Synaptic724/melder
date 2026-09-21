# Task: Systematic sliced audit of src_components vs architecture and source

## Metadata
- Task ID: TASK-2026-09-21-components-audit
- Story: UNKNOWN
- Status: ready
- Owner: user
- Agent Name: muse
- Priority: p1
- Created: 2026-09-21T00:16:57Z
- Updated: 2026-09-21T00:16:57Z

## Objective
Walk `src_components.md` top-down through its 139-row index, slicing one
component at a time, and record every contradiction against
`src_architecture.md` and source with evidence. No doc edits in this lane
without a separate approval.

## Ticket Contract
- ENTRY_GATE: owner approved option 1 (systematic sliced audit); board row
  routes here with `muse` checked in.
- EXECUTION_BOUNDARY: read-only audit. Allowed reads: both system-docs
  indexes, verified slices of `src_components.md` / `src_architecture.md`,
  `src_graph_index.md` plus sliced `src_graph.md` sections, and the source
  files those slices name. Never read indexed documents whole. No edits to
  `system_docs/`, `src/`, or indexes in this lane.
- DEPENDENCIES: `attention_board.md` active row; `src_components_index.md`;
  `src_architecture_index.md`; mediator lane findings as method reference.
- EXIT_GATE: each audited component carries a ticket note (clean or
  contradiction with evidence); a closing summary lists all contradictions
  with `path:start-end` pointers and proposed dispositions.
- FAILURE_ESCALATION: record BLOCKER if an index goes stale and refuses to
  slice, or if a claim cannot be resolved to either document or source.

## Scope Boundaries
- In scope:
  - Front matter plus C3 Components Catalog in index order (24 components).
  - C2 subcomponents and C1 call flows only when a C3 claim depends on them.
  - Spot source reads for ownership, lifecycle, and wiring claims.
- Out of scope:
  - Bulk-reading any indexed document whole.
  - Editing docs, regenerating indexes, or touching source.
  - C2/C1 exhaustive pass (follow-up lane if the C3 pass warrants it).

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: owner-approved systematic audit lane opened with
  slice-only read discipline and per-finding note cadence.

## Steps / Checklist
- [ ] Confirm both indexes current before the first slice.
- [ ] Slice front matter (Metadata, Scope, Indexing, Unknowns) and record baseline.
- [ ] Slice each C3 component in index order; compare with architecture + source.
- [ ] Append one `## Notes` entry per component before slicing the next one.
- [ ] Keep a running contradiction list with evidence and dispositions.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Per-component audit notes with FACT/UNKNOWN claims and evidence.
- Closing contradiction list with proposed dispositions (doc fix, source
  check, or follow-up lane).

## Files / Paths Impacted
- context_compass/system_docs/src_components_index.md
- context_compass/system_docs/src_components.md
- context_compass/system_docs/src_architecture_index.md
- context_compass/system_docs/src_architecture.md
- context_compass/system_docs/src_graph_index.md
- context_compass/system_docs/src_graph.md
- src/melder/

## Validation
- Not run.
- Recommended commands:
  - python context_compass/tools/system_documents/index_document.py --doc
    context_compass/system_docs/src_components.md --check
  - python context_compass/tools/system_documents/index_document.py --doc
    context_compass/system_docs/src_architecture.md --check

## Risks / Rollback Notes
- Risk: 8,702-line doc tempts bulk reads; mitigated by slice-only boundary
  plus per-component note gates.
- Risk: audit sprawls into C2/C1 exhaustively; mitigated by C3-first scope
  with explicit follow-up trigger.
- Rollback: read-only lane, nothing to revert.

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
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: on ticket close

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - component-by-component audit against architecture and source
- IF_UNKNOWN: ask user before implementation

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-21T00:16:57Z
  TYPE: PLAN
  CLAIM: Sliced audit lane opened per owner option-1 approval; C3-first order.
  EVIDENCE:
  - context_compass/system_docs/src_components_index.md:28-36
  IMPACT: Bounds the pass to verifiable slices with per-component notes
    instead of a bulk whole-doc load.
  NEXT: Verify both indexes, then slice front matter plus first component.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-21T00:20:00Z
  TYPE: FACT
  CLAIM: Component 1 (Public API and Runtime Guardrails) is clean against
    source; ordering, warnings, and guard-absence claims all hold.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:208-271
  - src/melder/__init__.py:163-196
  - src/melder/__init__.py:200-200
  IMPACT: Audit method proven on first slice; no contradiction to file for
    this component.
  NEXT: Slice component 2 (Packaged Hardcopy Documents) and compare.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-09-21T00:28:00Z
  TYPE: CONFLICT
  CLAIM: Component 2 says hardcopy payloads are placeholders, but the live
    package renders the full current architecture text (2,444 lines).
  EVIDENCE:
  - context_compass/system_docs/src_components.md:272-338
  - src/melder/__architecture__.py:1-44
  IMPACT: Either the component section or the packaging pipeline description
    is stale; the runtime behavior is live snapshot, not placeholder.
  NEXT: Owner decides disposition: fix component prose or confirm placeholder
    refers to a different carrier stage.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-21T00:35:00Z
  TYPE: FACT
  CLAIM: Design skills applied to the mediator rewrite: code-first claims,
    preservation baseline captured before the detail edit, index regenerated
    same pass with zero lost line-groups.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:3426-3429
  IMPACT: Added only the FRAME_CREATE responsibility bullet; entry contract
    fields intact and portability hits are pre-existing, not introduced.
  NEXT: Continue C3 audit at component 3; component-2 fix still awaits owner
    disposition and is not applied.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Audit lane opened after owner rejected bulk-read and approved systematic
slicing. Mediator lane stays open (no checkout requested). Next: verify
indexes, slice front matter, then C3 components in order.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
