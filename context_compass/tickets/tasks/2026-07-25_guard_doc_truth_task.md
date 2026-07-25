

# Task: Correct every guard claim in src_architecture.md and src_components.md

## Metadata
- Task ID: TASK-2026-07-25-guard-doc-truth
- Story: STORY-2026-07-25-guard-manifest-truth
- Status: ready
- Owner: melder_1
- Agent Name: melder_1
- Priority: p2
- Created: 2026-07-25T18:19:28Z
- Updated: 2026-07-25T18:19:28Z

## Objective
Replace the retired-sentinel description with the shipped build-time manifest model in
both canonical system docs, including the accepted subclass behavior flip.

## Ticket Contract
- ENTRY_GATE: story routed on `attention_board.md`; mechanism evidenced in source.
- EXECUTION_BOUNDARY: `system_docs/src_architecture.md` and
  `system_docs/src_components.md` only. No code, no graph, no other docs.
- DEPENDENCIES: STORY-2026-07-25-guard-manifest-truth Notes FACT entry.
- EXIT_GATE: all five drift sites corrected; no live sentinel mechanism claim remains;
  doc metadata `Updated:` refreshed.
- FAILURE_ESCALATION: DECISION_REQUEST if a correction would require asserting the
  cold-boot fallback as an evidenced runtime guarantee.

## Scope Boundaries
- In scope: the guard/guardrail prose, the C1 one-line descriptor, the subcomponent
  entry, and the failure-mode sentence.
- Out of scope: the C1 Code Map rebuild (own task), graph, code.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Mechanism is evidenced and the drift sites are enumerated with
  line numbers; no unknowns block the edit.

## Steps / Checklist
- [ ] `src_architecture.md:612-615` - rewrite the two guardrail bullets to describe the
      manifest, exact-match lookup, and no-MRO semantics.
- [ ] `src_architecture.md:1503` - C1 descriptor: "registration guard sentinel" ->
      manifest-backed guard.
- [ ] `src_architecture.md:1369` - boot-sequence line: keep the import-time singleton
      fact, drop any sentinel implication.
- [ ] `src_components.md:207` - failure mode: refusal is manifest membership, not a tag.
- [ ] `src_components.md:2142-2153` - retitle the subcomponent and replace `_SENTINEL`
      data-structure claim with `INTERNAL_MANIFEST` frozenset.
- [ ] `src_components.md:190-194,3412` - guard-instance claims reviewed for accuracy.
- [ ] Record the accepted behavior flip (user subclasses bindable) in both docs.
- [ ] Refresh `Updated:` in both Metadata blocks.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Both canonical system docs describing the manifest mechanism accurately.

## Files / Paths Impacted
- context_compass/system_docs/src_architecture.md
- context_compass/system_docs/src_components.md

## Validation
- Not run.
- Recommended commands:
  - `rg -n "sentinel" context_compass/system_docs/src_architecture.md context_compass/system_docs/src_components.md`
  - manual read-back of each edited section against the guard module source

## Risks / Rollback Notes
- Low risk: documentation-only, no runtime behavior. Rollback is a git revert of the
  two files.

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
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 7)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
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
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-07-25T18:19:28Z
  TYPE: FACT
  CLAIM: Five drift sites enumerated by grep across both docs; no other guard claims
    exist in either file, and `tests_architecture.md`, `tests_components.md`, and
    `graph_details_document.md` contain zero guard/sentinel references.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:612-615
  - context_compass/system_docs/src_components.md:2142-2153
  IMPACT: Bounds the doc blast radius to exactly two files, keeping the edit inside
    the expansion gate without a scope-confirmation round trip.
  NEXT: Rewrite `src_architecture.md:612-615` first, as it is the mechanism anchor the
    other sites refer back to.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-25T18:19:28Z
  TYPE: FACT
  CLAIM: All drift sites corrected in both docs. Remaining `sentinel` matches are
    exactly the intended ones: historical/superseded framing explaining WHY the
    manifest exists, the vestigial-surface note pointing at the strip task, and one
    unrelated crystallizer binding marker (`"user_source_retained"`), which is a
    different concept and was not touched.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:622-622
  - context_compass/system_docs/src_components.md:2180-2194
  IMPACT: Acceptance criterion "no live sentinel mechanism claim remains" is met
    without erasing the historical rationale a future reader needs.
  NEXT: Await owner acceptance; proceed to TASK-2026-07-25-c1-code-map-restore.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-25T18:19:28Z
  TYPE: MEASURE
  CLAIM: Formatting and encoding verified. Zero lines authored in this task exceed the
    120-char hard cap; the over-cap lines that exist in both files are pre-existing and
    untouched. Line endings preserved: 2120/2120 CRLF in `src_architecture.md` and
    4190/4190 in `src_components.md`, with zero LF-only lines in the edited zones.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:1510-1510
  - context_compass/agent_onboarding/default/general/skills/configuration_standards.md:22-30
  IMPACT: Repo has a documented history of encoding faults on board/doc writes; mixed
    line endings would have been a silent regression.
  NEXT: None for this task.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Five enumerated drift sites across two files. Mechanism truth is recorded in the parent
story's FACT note. The cold-boot fallback must be attributed to the loader contract
rather than asserted as an evidenced runtime guarantee, per the story's RISK note.
