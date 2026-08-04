# Task: Populate Src Graph For Crystallizer First Tranche

## Metadata
- Task ID: TASK-2026-04-19-populate-src-graph-for-crystallizer-first-tranche
- Story: STORY-2026-04-19-populate-src-graph-for-crystallizer-directory
- Status: review
- Owner: codex
- Priority: p1
- Created: 2026-04-19T21:30:41Z
- Updated: 2026-04-19T21:30:41Z

## Objective
Decide the minimal honest `crystallizer` graph outcome:
either add the small number of system-significant crystallizer objects that
exist, or explicitly record that the subtree is still too thin to justify
graph nodes.

## Ticket Contract
- ENTRY_GATE: the `utilities` story is coherent enough to pause and the
  remaining top-level source directory is `crystallizer`.
- EXECUTION_BOUNDARY:
  - `src/melder/crystallizer/**`
  - `codex/context_compass/system_docs/src_graph.json`
  - the active expanded graph working copy
- DEPENDENCIES:
  - `tickets/tasks/2026-04-19_populate_src_graph_for_utilities_first_tranche_task.md`
  - `codex/context_compass/system_docs/src_architecture.md`
  - `codex/context_compass/system_docs/src_components.md`
  - `codex/context_compass/system_docs/graph_details_document.md`
- EXIT_GATE: the subtree is either represented honestly in the graph or
  explicitly documented as too small/low-signal for node inclusion, with JSON
  validation still green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if crystallizer has hidden
  implementation surfaces not visible from the current subtree inventory.

## Scope Boundaries
- In scope:
  - actual crystallizer source/runtime objects if they exist
  - explicit low-signal closure if they do not
- Out of scope:
  - `tests/**`
  - speculative future crystallizer design
  - non-code directional notes promoted into fake graph structure without evidence

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the final top-level repo graph lane is `crystallizer`,
  and the subtree appears small enough to resolve quickly.

## Steps / Checklist
- [ ] Inventory and read the crystallizer subtree in compliant chunks.
- [ ] Record the first meaningful crystallizer finding in `## Notes`.
- [ ] Decide whether graph nodes are warranted or the subtree should close as low-signal.
- [ ] Patch the active expanded graph working copy only if warranted.
- [ ] Recompress and validate the canonical graph if the graph changed.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- crystallizer graph decision
- updated `src_graph.json` only if needed
- validation record and tranche notes

## Files / Paths Impacted
- src/melder/crystallizer/
- codex/context_compass/system_docs/src_graph.json
- codex/context_compass/system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json
- codex/context_compass/tickets/tasks/2026-04-19_populate_src_graph_for_crystallizer_first_tranche_task.md
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Not run.
- Recommended commands:
  - `Get-Content codex/context_compass/system_docs/src_graph.json -Raw | ConvertFrom-Json | Out-Null`

## Risks / Rollback Notes
- Risk: directional crystallizer notes get promoted into fake implementation nodes.
  Rollback: keep the story as an explicit low-signal closure with no graph additions.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/populate_src_graph_aether_first_tranche/src_graph.expanded.json
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the active repo-graph lane changes to a new working copy.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-19T21:30:41Z
  TYPE: PLAN
  CLAIM: `crystallizer` appears small enough that the honest outcome may be
    "no graph nodes yet." The task should prove that from source evidence
    rather than force graph additions.
  EVIDENCE:
  - tickets/stories/2026-04-19_populate-src-graph-for-crystallizer-directory_story.md: current scope
  - src/melder/crystallizer: current subtree inventory
  IMPACT: This lane can close quickly if the subtree is still only directional
    context instead of implemented runtime structure.
  NEXT: inventory and read the crystallizer subtree fully.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-19T21:30:41Z
  TYPE: FACT
  CLAIM: The current `crystallizer` subtree does not yet contain implemented
    runtime objects worth graphing. It contains:
    - an empty `__init__.py`, which is explicitly excluded from graph nodes
    - one plain `info` file containing directional prose, not an implementation
      contract and not a runtime object/module surface
    So the honest current outcome is an explicit low-signal closure with no
    graph additions.
  EVIDENCE:
  - src/melder/crystallizer/__init__.py: empty file
  - src/melder/crystallizer/info:1-10
  - src/melder/crystallizer/info: "This file is directional project context, not an implementation contract."
  IMPACT: The repo graph lane can finish the `crystallizer` story without
    inventing fake nodes from directional notes.
  NEXT: move the crystallizer task to review as a no-node closure and sync the
    story/epic state.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the first active `crystallizer` graph-population tranche.
