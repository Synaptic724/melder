

# Task: Design override execution and caller-supplied inputs as one contract (alternative to joint alpha)

## Metadata
- Task ID: TASK-2026-09-26-design-override-and-caller-input-execution
- Epic: EPIC-2026-09-24-override-execution-performance
- Story: none (epic-level design task)
- Status: review
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-26T00:14:30Z
- Updated: 2026-09-26T00:22:28Z

## Objective
Produce a source-grounded design that (1) lets a constructor declare parameters the caller always
supplies (Package, Conduit, greenlet, Spectrum) so conjure accepts them and meld requires them, and
(2) makes supplied overrides remove construction work instead of substituting values afterwards.
Compare it against joint_alpha_proposal.md and recommend one path with tradeoffs.

## Ticket Contract
- ENTRY_GATE: Owner direction 2026-09-26 ("go back to the original issue ... we can probably do better").
- EXECUTION_BOUNDARY: Read src/, tests/ and existing artifacts. Write only this ticket and
  artifacts/melder_override_design_20260926/. No src/, tests/, canonical doc, version or asset edits.
- DEPENDENCIES: joint_alpha_proposal.md, compact_structure_proposal.md, native_runtime_boundary.md,
  required_caller_inputs findings.md, melder_1's regression matrix, the completed slot-guard fix.
- EXIT_GATE: Design artifact with evidence-backed current-behavior claims, a comparison with joint
  alpha, decisions the owner must make, and an implementation sequence; task in review.
- FAILURE_ESCALATION: DECISION_REQUEST for semantic policy choices; CONFLICT where source contradicts
  a proposal; no behavior claim from documents or search hits alone.

## Scope Boundaries
- In scope: Phase 1/3 parameter classification, Phases 8-11 occurrence/injection/targeting/planning/
  emission, CreationContext dispatch, ConduitMeld/SpellSpaceMeld doors, override semantics, caller inputs.
- Out of scope: Production edits, hook standardization, existing-object ownership redesign, the
  comptime IR epic, cache-format changes beyond what the design must name.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner directed melder_0 to design a better alternative, 2026-09-26T00:14:30Z.
- from_state: in_progress
- to_state: review
- transition_reason: Design artifact written; D1-D4 raised, 2026-09-26T00:22:28Z.

## Steps / Checklist
- [x] Read joint_alpha_proposal.md, structural_plan.md, compact_structure_proposal.md,
      native_runtime_boundary.md, semantics_findings.md and the caller-input findings.
- [x] Read the current physical-graph producers (Phase 9 instance/injection rows) and targeting.
- [x] Read the ordinary and override emitters' step order and reuse handling.
- [x] Read Phase 1/3 classification for caller inputs and OVERRIDE_REQUIRED (via probe and findings).
- [x] Write the design artifact and the joint-alpha comparison.
- [x] Record owner decisions as DECISION_REQUEST notes.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- artifacts/melder_override_design_20260926/design.md

## Files / Paths Impacted
- None in src/ or tests/. This ticket and its artifact directory only.

## Validation
- Not run.

## Risks / Rollback Notes
- Prototype results describe artifact adapters, not production; cite source for current behavior.
- updater_0/updater_1 own the epic's discovery tasks; this task reads their artifacts and does not edit them.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No behavior claim cited only to a document or a one-line search hit.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/melder_override_design_20260926/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Owner decision at task closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Override execution semantics; caller-supplied constructor inputs.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T00:14:30Z
  TYPE: PLAN
  CLAIM: Joint alpha's native claim protocol (non-blocking claims, release-before-wait, retry, claim
    records) exists to break the store/Spell inversion, which the shipped slot guards already remove with
    an acyclic consumer-first lock order. Its runtime alias activation makes operand choice depend on live
    store state. Test the hypothesis that a static per-input-shape plan executed top-down under slot guards
    gives deterministic semantics with far less machinery. Caller inputs join as unprovided sockets.
  EVIDENCE:
  - artifacts/override_structural_discovery_20260924/joint_alpha_proposal.md:61-106
  - artifacts/override_structural_discovery_20260924/native_runtime_boundary.md:72-104
  - artifacts/required_caller_inputs_20260924/findings.md:99-135
  IMPACT: If source supports it, the design drops the claim subsystem and the conditional alias program.
  NEXT: Read Phase 9 instance/injection rows and the override targeting strategy in full.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T00:17:13Z
  TYPE: FACT
  CLAIM: The physical construction graph already exists upstream: the occurrence analyzer collapses each
    shared spell to one expansion and the instance processor keys shared sites (spell_id, None) and many
    sites per path. The Phase-5 socket overlay does not collapse: it walks every logical path, and override
    targeting then builds exact-path keys for every socket ref. This runs at conjure with or without
    overrides. Probe (3.14.7t, caching off): a binary unique chain of 15 sites yields 32,766 root socket
    refs and 0.31 s conjure (0.08 s at 13 sites): cost grows ~4x per two levels while work stays linear.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:719-785
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_instance_processor_strategy.py:127-215
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_root_blueprint_builder.py:435-500
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_override_targeting_processor_strategy.py:51-110
  - artifacts/melder_override_design_20260926/current_behavior_results_314t.json
  IMPACT: The design can reuse the existing physical graph and must remove path enumeration from Phase 5
    and targeting; selectors can be resolved by walking named edges, never by enumerating paths.
  NEXT: Record the probe's ordinary-reuse, supplied-dependency and caller-input results.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T00:17:13Z
  TYPE: MEASURE
  CLAIM: Same probe, current source: (1) ordinary meld of Root(many)->Middle(unique)->Leaf(many) twice
    builds Leaf twice though Middle is reused (eager bottom-up plan, no override involved); (2) supplying
    a and b to Consumer(a, b, c) still constructs A and B, then passes the supplied objects (identity kept);
    (3) Task(work: Package) with Package unbound fails conjure in Phase 3 ("no DI candidate").
  EVIDENCE:
  - artifacts/melder_override_design_20260926/current_behavior_probe.py:60-140
  - artifacts/melder_override_design_20260926/current_behavior_results_314t.json
  IMPACT: Wasted construction is a property of the bottom-up step order, not only of overrides, so the
    fix belongs in the shared lowering; caller inputs are blocked before any meld-time path can help.
  NEXT: Read the ordinary emitter's step order and reuse block to confirm the bottom-up cause in source.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T00:19:24Z
  TYPE: FACT
  CLAIM: The generalized plan emits steps in Kahn topological order (providers first, spell-id tie-break),
    one step per instance key, so every shared step is checked for reuse only after its dependencies were
    already built. That is the source-level cause of the ordinary Leaf waste. A top-down (consumer-first)
    lowering cannot simply nest `with guard:` blocks inline: CPython 3.14.7 compiles 21 nested `with`
    blocks but rejects 40 ("too many statically nested blocks"), so shared-site miss branches must be
    separate emitted functions while hit paths stay inline.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_order_processor_strategy.py:103-171
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1500-1600
  IMPACT: The design lowers each shared site as inline hit + out-of-line miss function; many sites stay
    inline under their physical parent. Nesting depth no longer tracks graph depth.
  NEXT: Write design.md: static per-shape plan, top-down lowering under slot guards, caller-input sockets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T00:22:28Z
  TYPE: DECISION
  CLAIM: Design written. Recommend: static plan per override key shape over the existing physical graph,
    lowered top-down (inline hit, out-of-line miss under the shipped slot guards); the empty shape is the
    ordinary meld. Caller inputs become a provider-less socket declared per binding. Drops joint alpha's
    claim protocol, live-state operand selection and selector-state machine; removes Phase-5 path
    enumeration so conjure is linear. Sequence S1 caller inputs -> S2 rows/selectors -> S3 ordinary
    lowering (parity gate) -> S4 shapes -> S5 qualification.
  EVIDENCE: artifacts/melder_override_design_20260926/design.md:1-204
  IMPACT: One lowering replaces the separate override compilers; no new concurrency protocol is needed.
  NEXT: Owner decides D1-D4 (next note); S1 can start independently once D1 is chosen.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T00:22:28Z
  TYPE: DECISION_REQUEST
  CLAIM: D1 caller-input declaration surface (per-binding keyword recommended; optional auto-classification
    of unbindable kernel types). D2 reuse never changes operands (revises item-4 (a) for runtime reuse;
    static cuts keep (a)). D3 two live PATH rules on one physical input are a shape error (replaces item-5
    (c)). D4 accept depth-first constructor order and fewer throwaway constructions in ordinary melds.
  EVIDENCE: artifacts/melder_override_design_20260926/design.md:166-179
  IMPACT: D1 gates S1; D2-D4 gate S3/S4 and the regression matrix rows R4b, R4c, R5c, R5d.
  NEXT: Owner answers D1-D4.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Design in review: artifacts/melder_override_design_20260926/design.md (probe and results beside it).
Waiting on owner decisions D1-D4. S1 (caller inputs) is independent and needs only D1. Validation: Not run
beyond the read-only current-behavior probe (3.14.7t).

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
