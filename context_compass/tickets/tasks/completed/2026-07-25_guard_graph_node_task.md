

# Task: Correct the guard node in src_graph.json and regenerate the readable graph

## Metadata
- Task ID: TASK-2026-07-25-guard-graph-node
- Story: STORY-2026-07-25-guard-manifest-truth
- Status: done
- Owner: melder_1
- Agent Name: melder_1
- Priority: p2
- Created: 2026-07-25T18:19:28Z
- Updated: 2026-07-31T23:03:22Z

## Objective
Make the `MelderRegistrationGuard` graph node state manifest truth in canonical
storage, then regenerate the readable consumption artifact from it.

## Ticket Contract
- ENTRY_GATE: story routed on `attention_board.md`; the storage-first correction
  recorded as an ASSUMPTION_CHALLENGE in the parent story and accepted.
- EXECUTION_BOUNDARY: the single guard node in `system_docs/src_graph.json`, plus a
  full regeneration write of `system_docs/readable_src_graph.json`. No other node.
- DEPENDENCIES: TASK-2026-07-25-guard-doc-truth should land first so node wording and
  doc wording agree.
- EXIT_GATE: node names the manifest; `owns_state` no longer claims `_sentinel`;
  regenerated readable graph validates as JSON; max line length reported.
- FAILURE_ESCALATION: BLOCKER if `src_graph.json` proves stale beyond the guard node in
  ways this lane cannot honestly repair.

## Scope Boundaries
- In scope: `role`, `responsibilities`, and `owns_state` of the guard node; the
  delimiter-only regeneration of the readable artifact.
- Out of scope: regenerating `src_graph.json` itself from source; auditing other nodes
  for drift; the `creates`/`uses` edges, which remain accurate.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Storage-first sequencing resolved the contradiction in the
  owner's chosen approach; the edit target is a single evidenced node.

## Steps / Checklist
- [ ] Edit the guard node in `src_graph.json`: `role` and `responsibilities` describe
      exact-match manifest lookup; `owns_state` drops `_sentinel`.
- [ ] Confirm the `creates` edge to `InternalRegistrationError` and the `uses` edges
      from `Aether` and `ProtocolCrafter` remain accurate; leave them untouched.
- [ ] Regenerate `readable_src_graph.json` using the Bash recipe in
      `graph_details_readable_generation.md`, width 220, safe delimiters only.
- [ ] Validate the regenerated file parses as JSON and report max line length.
- [ ] Report source file used, output written, max line length, and validation result
      per the skill's Handoff Rule.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Corrected guard node in canonical storage.
- Regenerated, JSON-valid `readable_src_graph.json`.

## Files / Paths Impacted
- context_compass/system_docs/src_graph.json
- context_compass/system_docs/readable_src_graph.json

## Validation
- Not run.
- Recommended commands:
  - JSON parse check of both files
  - max-line-length report on the regenerated readable artifact
  - `rg -n "sentinel" context_compass/system_docs/src_graph.json`

## Risks / Rollback Notes
- RISK: a full-file regeneration write can truncate on failure. Mitigation: validate
  JSON before accepting the output; both files are git-tracked for revert.
- The regeneration recipe is explicitly Markdown-only; no script file may be committed.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No semantic reshaping of JSON during regeneration; line breaks only.
- [ ] No committed `.ps1`/`.sh` regeneration script.

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
  CLAIM: Both graph artifacts carry identical stale guard text, so the readable file is
    a faithful reflow of a wrong source. The node's edges are unaffected: the `creates`
    edge to `InternalRegistrationError` and the `uses` edges from `Aether` and
    `ProtocolCrafter` all remain true under the manifest mechanism.
  EVIDENCE:
  - context_compass/system_docs/readable_src_graph.json:15-16
  - context_compass/system_docs/src_graph.json (grep: `sentinel tag`)
  IMPACT: Scopes the edit to three fields on one node and spares a broader graph audit.
  NEXT: Edit `role`, `responsibilities`, and `owns_state` on the guard node in storage.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-25T18:19:28Z
  TYPE: MEASURE
  CLAIM: Storage corrected and readable regenerated. Guard node `role` now names the
    build-time manifest, `responsibilities` names EXACT `(module, qualname)` lookup
    that does not inherit, and `owns_state` is `[]`. Both artifacts JSON-validate.
    Blast radius is surgical: 7 changed lines in `readable_src_graph.json` and 1 in
    `src_graph.json`, line count unchanged at 4284.
  EVIDENCE:
  - context_compass/system_docs/src_graph.json
  - context_compass/system_docs/readable_src_graph.json:15-16
  IMPACT: The fast structural surface agents consult first no longer teaches a retired
    mechanism, and it now agrees with both canonical system docs.
  NEXT: Await owner acceptance.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-25T18:19:28Z
  TYPE: DECISION
  CLAIM: `owns_state` is `[]` rather than `["INTERNAL_MANIFEST"]`. The manifest is a
    module-level frozenset owned by `manifest_loader`, which the guard imports and
    borrows; it is not guard-owned state. The vestigial `_sentinel` field was not
    carried forward either, since a dead unused field is not important owned state.
  EVIDENCE:
  - src/melder/__melder_cache__/__init_cache__/manifest_loader.py:69-69
  - context_compass/agent_onboarding/default/engineer/skills/graph_details_usage.md:44-56
  IMPACT: Keeps the graph's ownership vocabulary honest, and the value stays correct
    once TASK-2026-07-25-sentinel-deadcode-strip removes the dead field.
  NEXT: None.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-07-25T18:19:28Z
  TYPE: FACT
  CLAIM: Regeneration used CRLF, not the Bash recipe's LF. The skill's two variants
    disagree - PowerShell emits CRLF, Bash emits LF - and the existing artifact was
    CRLF across all 4284 lines. Following the Bash variant literally would have
    rewritten every line as a whitespace-only change on top of the semantic fix.
    The transform contract (delimiter-only breaks at width 220, no reshaping) was
    followed exactly. Max line length is 479, down from 480 at HEAD, so the
    documented >220 overrun from long string literals is pre-existing.
  EVIDENCE:
  - context_compass/agent_onboarding/default/engineer/skills/graph_details_readable_generation.md:41-97
  - context_compass/agent_onboarding/default/engineer/skills/graph_details_readable_generation.md:172-179
  IMPACT: Reviewers see a 7-line diff instead of a 4284-line one; the skill's
    line-ending inconsistency is worth resolving so the next regeneration is
    deterministic regardless of which variant an agent picks.
  NEXT: Raise the recipe's LF/CRLF inconsistency to the owner at story walkthrough.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-31T23:03:22Z
  TYPE: DECISION
  CLAIM: CLOSED at owner turn-in 2026-07-31. Dead graph node removed and re-verified at closure: src_graph.json holds 535 nodes and
    SoloFinalizeCreationContextStep is absent. Validation section had read 'Not run'; the check
    was executed at turn-in rather than closed on claim.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-07-25_guard_graph_node_task.md
  IMPACT: Ticket moved to completed/; board row removed and replaced by one anchor.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Storage-first, then regenerate. Only three fields on one node change; the guard's edges
are already correct. The regeneration recipe is delimiter-only reflow at width 220 and
must be run inline, never committed as a script.
