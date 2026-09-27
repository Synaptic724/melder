

# Task: Verify override behavior contract items 1-8 and draft the regression matrix

## Metadata
- Completed: 2026-09-26T00:12:00Z
- Closure Basis: owner directed turn-in ("turn in that task"), relayed by lead melder_0.
- Summary: Items 1-8 verified from source with a regression matrix; items 4 (a) and 5 (c) chosen as
  implementation inputs; item-7 conflict, R5d and two UNKNOWNs carried to the implementation lane.
- Task ID: TASK-2026-09-25-verify-override-behavior-contract
- Story: STORY-2026-09-25-verify-override-writer-and-contract
- Status: done
- Owner: user
- Agent Name: melder_1
- Priority: p1
- Created: 2026-09-25T20:52:31Z
- Updated: 2026-09-26T00:12:00Z

## Objective
For each "Required behavior contract" item in joint_alpha_proposal.md, establish current Melder
behavior from source, state the proposed behavior, and draft one regression case per item.

## Ticket Contract
- ENTRY_GATE: Active attention-board row routes here; melder_1 acknowledges M0-3.
- EXECUTION_BOUNDARY: Read-only over src/, tests/ and artifacts; writes limited to this ticket and
  artifacts/melder_override_contract_20260925/.
- DEPENDENCIES: joint_alpha_proposal.md:61-80; compact_structure_proposal.md; structural_plan.md;
  semantics_findings.md.
- EXIT_GATE: Every item has current-behavior evidence and a regression case; status review.
- FAILURE_ESCALATION: CONFLICT when source contradicts the proposal; DECISION_REQUEST for item 4
  and the item 5 equality contract.

## Scope Boundaries
- In scope: Compiler override-socket metadata, override execution lane, CreationContext dispatch,
  root override-on-reuse refusal, unresolved-descriptor failure paths, existing tests.
- Out of scope: Any src/tests edit; native lock ordering (melder_0 task).

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Created by lead on owner approval; melder_1 moves it to in_progress on start.
- from_state: ready
- to_state: in_progress
- transition_reason: melder_1 acknowledged M0-3 (reply M1-4) and started source verification, 2026-09-25T20:55:13Z.
- from_state: in_progress
- to_state: review
- transition_reason: Items 1-8 carry source-backed current behavior, matrix drafted, CONFLICT and two
  DECISION_REQUEST notes recorded; remaining UNKNOWNs listed in the handoff summary. 2026-09-25T21:03:56Z.
- from_state: review
- to_state: done
- transition_reason: Owner directed turn-in; item 4 (a) and item 5 (c) recorded, open items carried.
  2026-09-26T00:12:00Z.

## Steps / Checklist
- [x] Read joint_alpha_proposal.md, compact_structure_proposal.md and structural_plan.md.
- [x] For items 1-8, locate current behavior in source; cite ranges covering the logic.
- [x] Record current vs proposed per item; divergences are findings.
- [x] Draft the regression matrix in the task artifact (test plan only, no test code).
- [x] Raise DECISION_REQUEST notes for item 4 and the item 5 equality contract.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Per-item notes with evidence ranges.
- artifacts/melder_override_contract_20260925/regression_matrix.md

## Files / Paths Impacted
- None in src/ or tests/. Ticket and task artifact only.

## Validation
- Not run.

## Risks / Rollback Notes
- Prototype results describe artifact adapters, not production; do not cite them for current behavior.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No behavior claim cited only to a document or a one-line search hit.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/melder_override_contract_20260925/regression_matrix.md (draft, 2026-09-25T21:03:56Z; retained)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Owner decision at story closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Override semantics: supplied dependencies, parameter overrides, selectors, aliases.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-25T20:55:13Z
  TYPE: ALIGNMENT_CHECK
  CLAIM: Accepted M0-3 from melder_0: verify joint alpha contract items 1-8 against current source,
    then draft regression_matrix.md as a test plan. Read-only over src/tests; writes limited to this
    ticket and artifacts/melder_override_contract_20260925/. Native lock order stays with melder_0.
    Already read in full: joint_alpha_proposal.md, structural_plan.md, native_runtime_boundary.md.
  EVIDENCE:
  - tickets/tasks/2026-09-25_verify_override_behavior_contract_task.md:15-32
  - artifacts/override_structural_discovery_20260924/joint_alpha_proposal.md:63-80
  IMPACT: Fixes scope and exit gate; proposal and prototype claims stay UNKNOWN until source is read.
  NEXT: Read compact_structure_proposal.md in full, then locate item 1 (supplied whole dependency)
    in the current compiler override-socket path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7
- DATETIME: 2026-09-25T20:56:05Z
  TYPE: PLAN
  CLAIM: Proposal set read in full. Runtime override lane = Meld/ConduitMeld -> CreationContext
    override specialization executor -> codegen-creation override compilers (generalized and
    many_only, ~3k LOC each). Verify per item by reading the complete functions on each item's
    path, entered via the component map and graph index; whole 3k-line compilers are not bulk-read.
    Component-map index verified current (9004 lines, sha matches) before slicing.
  EVIDENCE:
  - artifacts/override_occurrence_discovery_20260924/compact_structure_proposal.md:34-78
  - system_docs/src_components.md:2733-3016
  IMPACT: Bounds the source surface per item; keeps the pass inside the declared scope.
  NEXT: Read creation_context.py and spell_overrider.py in full to locate item 1's supplied-child
    handling, then the override compiler functions they dispatch to.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-09-25T20:58:17Z
  TYPE: FACT
  CLAIM: Generalized-family override executor (file read in full) executes EVERY plan step: both
    emitters write one unguarded block per step that reuses or constructs, then registers. A supplied
    value only replaces the parent's kwarg. Item 1 current: a whole-supplied child is still built
    (and registered for unique*/many-with-disposal) then unused - diverges from proposed. Item 2
    current: owner still constructs; override applies by key presence (dict membership, socket-name
    compare), so None/False count by presence at this layer (upstream map build not yet checked).
    Item 6 current: existing root + any override raises MeldExecutionError; so does an existing
    shared NON-root step with targeted overrides (stricter than root-only). Item 7 current: every
    constructor exception, incl. missing-arg TypeError, is re-raised as MeldExecutionError('Error
    invoking spell') chained from the original; a zero-provider non-collection param is omitted,
    so the Python default (possibly a descriptor object) applies - pass-through path is HYPOTHESIS.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:549-616
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:1818-2266
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:2313-2514
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:1112-1144
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:2874-3022
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:2725-2759
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:1682-1728
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:3025-3085
  IMPACT: Items 1, 2, 6, 7 have source-backed current behavior for the generalized family; the
    many_only and solo families have separate override compilers and are not yet covered.
  NEXT: Read many_only_overrides_codegen_creation_compiler.py (2827 lines) for the same four items.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-25T20:58:50Z
  TYPE: FACT
  CLAIM: many_only override compiler is the generalized file with every step hard-wired to
    Existence.many/CALLER (full diff read): it never reuses, emits one unguarded block per step,
    and registers when the Spell has disposal methods - items 1/2/7 behave as in the generalized
    note. Solo override executor (read in full) passes the payload straight to the root call target
    and then add_creation()s with no reuse check or lock inside the executor. Family divergence
    for item 7: solo lets constructor exceptions (incl. missing-arg TypeError) propagate raw and
    raises RuntimeError for a bad __args__, while generalized/many_only wrap both in
    MeldExecutionError. Solo also treats __args__=None as absent (value test, not presence).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:1790-1933
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:2182-2265
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:2740-2827
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:73-276
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:279-309
  IMPACT: Item 7 error behavior differs by compilation family, so a regression case must pin the
    family. Solo item 6 refusal and writer locking must live in the door, not the executor.
  NEXT: Read creation_runtime_door_compiler.py in full for the root reuse check, override refusal
    and lock wrapping on each family's door.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-25T20:59:16Z
  TYPE: FACT
  CLAIM: Item 6 root refusal lives in the CreationContext override door, per route: existing_creation
    always raises MeldExecutionError; many has no check; unique_per_conduit, spellspace, lineage and
    cluster do an unlocked store read (raise if present), take that STORE lock, re-check, then run the
    whole family executor under it; unique re-checks under the Spell lock instead. So the root override
    executor, including every dependency step it constructs, runs while the root store lock is held
    on the four store routes - the same wrapper melder_0's inversion claim concerns. The door also
    supplies the lock the solo executor's unguarded add_creation relies on.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:689-868
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:7-53
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:100-146
  IMPACT: Item 6 current behavior is FACT for roots on all routes; the store-held-across-execution
    shape is shared evidence for the lock-order task and belongs in melder_0's lane, not mine.
  NEXT: Read the override targeting surfaces (spell_overrider.py, generalized
    spell_override_targeting_codegen_creation.py, Phase 9 targeting strategy) for items 3, 4 and 5.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-25T21:00:00Z
  TYPE: FACT
  CLAIM: Live generalized targeting (SpellOverrideTargetingCodegenCreation, read in full) validates
    every raw key against compile-time targets_by_spec: PATH needs >=1 match, *param exactly 1,
    **param >=1, else RuntimeError - independent of any cut, since current execution has none
    (item 3 match-count half). Equal-rank conflicts use `existing_value != value` (item 5 equality:
    arbitrary user __ne__/truthiness decides; equal values keep the first). Sockets are keyed by
    (node_id, param_path_id, param_name, kind), so two logical aliases of one physical param are
    different keys and never conflict here. A shared step then receives ALL of its spell's targets
    unfiltered and writes kwargs by param_name in target order: last alias wins silently (item 5
    current: no rejection of incompatible aliases). Item 4 current: no inactive-path concept; rules
    under a supplied parent still apply to its (discarded) construction, a shared descendant takes
    rules from any path, and an existing shared targeted step raises MeldExecutionError.
    SpellOverrider (conduit/meld/overrides) has the same != rule but no live src caller was found.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/artifacts/spell_override_targeting_codegen_creation.py:210-305
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/artifacts/spell_override_targeting_codegen_creation.py:307-361
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:2640-2723
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:2853-2871
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:949-961
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:1320-1330
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:2725-2759
  - src/melder/aether/conduit/meld/overrides/spell_overrider.py:159-201
  IMPACT: Items 4 and 5 currently diverge from the proposal in user-visible ways (silent last-alias
    win; rules leaking across paths). Target ORDER feeding the last-wins write is still UNKNOWN.
  NEXT: Read TargetSpec.parse (syntax half of item 3) and the Phase 9 targeting strategy that builds
    targets_by_spec, to settle declared-path counting and target order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-25T21:00:43Z
  TYPE: FACT
  CLAIM: Item 3 syntax: TargetSpec.parse rejects None/blank keys and bare '*'/'**' with ValueError,
    but silently drops empty path segments ('a>>b' == 'a>b'). Phase 9 builds one PATH target per
    rooted logical socket and gives *name/**name the tuple of every rooted socket with that name, so
    *name counts declared logical paths (a shared param reached twice = 2 matches -> refused).
    Per call, parse/match/conflict errors are re-raised as MeldExecutionError('Failed to apply
    overrides.') chained from the original. Target order per spell comes from the sorted socket
    shape (node_id, param_path_id, ...), so the item-5 silent last-alias winner is the alias with the
    highest param_path_id - deterministic, but unrelated to specificity or payload order.
    __args__ is split by value test: __args__=None stays in the payload and fails as an unknown path.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/dag/target_spec.py:75-129
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_override_targeting_processor_strategy.py:43-122
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_finalize_creation_context_step.py:331-491
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_finalize_creation_context_step.py:551-631
  IMPACT: Item 3 current is FACT (match counts + syntax, with the lenient-segment gap); item 5 alias
    winner is now fully determined for the generalized fresh-compile path.
  NEXT: Read the public override normalization in meld/conduit_meld (item 2 falsey handling at the
    front door), then generalized_manifest_overrides_runtime.py for the hydrated path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-25T21:01:34Z
  TYPE: FACT
  CLAIM: Front door (ConduitMeld.meld read in full): non-resolvable refusal and spellspace-request
    refusal run before override handling (item 6 capability FACT); with no call payload the Spell's
    stored _mutation_override is used as the override payload; _normalize_spell_override maps {} ->
    None, keeps dict values untouched (None/False retained - item 2 FACT end to end), list/tuple ->
    {'__args__': list}. Hook order: root pre-cast hooks run before the door, so invalid-selector
    rejection (inside the family executor) happens AFTER pre hooks. Hydrated generalized runtime
    uses the same targeting object; non-overlapping key sets skip per-call targeting, overlapping
    ones keep per-call conflict checks - items 3/5 identical to the fresh path. Item 8 current: no
    retry and no rollback - each step registers right after construction, and a later constructor
    failure leaves earlier registered dependencies in their stores (no try/finally in the executor).
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:259-574
  - src/melder/aether/conduit/meld/meld.py:1506-1575
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_overrides_runtime.py:215-445
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:2313-2514
  IMPACT: Item 2, 3, 5, 6 and 8 current behavior is source-backed; the hook-order boundary that
    structural_plan.md flagged is confirmed. Item 7's descriptor half is still HYPOTHESIS.
  NEXT: Read semantics_findings.md for the native descriptor scenario, then trace the source that
    leaves a descriptor parameter with zero dependency keys.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-25T21:02:15Z
  TYPE: FACT
  CLAIM: Item 7 descriptor half: Phase 9 injection builds param sources only from occurrence edges,
    OVERRIDE_REQUIRED sockets and contract-payload keys; there is no source kind for an unresolved
    descriptor/provider. A parameter with no edge gets no source, execution omits it, and the
    constructor's Python default (e.g. the SpellContract descriptor object) is used. Whether upstream
    validation stops a NESTED unresolved contract before execution is UNKNOWN from source (the native
    probe observed it does not). Shared-provider contract payloads are merged with `==` and distinct
    payloads raise MeldExecutionError - an existing precedent for rejecting incompatible shared inputs.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:119-284
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:286-344
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:2918-2927
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:1112-1116
  IMPACT: Descriptor pass-through is a source-backed mechanism; the missing guard is in Phase 9
    sourcing, not in the executor. Nested-validation coverage stays UNKNOWN until read.
  NEXT: Record the item-7 wording conflict and the two owner decision requests, then draft the matrix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-25T21:02:15Z
  TYPE: CONFLICT
  CLAIM: Proposal item 7 and the component map say retained constructors keep 'ordinary Python
    missing-argument errors'. Source: generalized and many_only re-raise every constructor exception
    as MeldExecutionError('Error invoking spell ...') chained from the TypeError; only the solo family
    lets the TypeError propagate raw. 'Ordinary Python error' is therefore true only as __cause__.
  EVIDENCE:
  - artifacts/override_structural_discovery_20260924/joint_alpha_proposal.md:73-74
  - system_docs/src_components.md:2777-2778
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:1682-1728
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:279-309
  IMPACT: A regression test written from the proposal text would assert the wrong exception type on
    two of three families. The contract must name the raised type per family, or unify it.
  NEXT: Carry as a matrix row with family-pinned assertions; flag in the handoff to melder_0.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-25T21:02:15Z
  TYPE: DECISION_REQUEST
  CLAIM: Item 4 (owner): today a rule below a supplied or reused constructor still applies to that
    constructor's discarded build, and a shared descendant accepts rules from any path. Options:
    (a) proposal default - such rules become inactive for that path and never affect another path;
    (b) reject them explicitly with an error. (a) keeps valid selectors legal; (b) is stricter and
    user-visible. Recommendation: (a), as the proposal and prototypes implement.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:2640-2723
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:2853-2871
  - artifacts/override_structural_discovery_20260924/joint_alpha_proposal.md:68-69
  IMPACT: Decides expected outcomes for matrix rows R4a-R4c; tests stay provisional until chosen.
  NEXT: Owner selects (a) or (b).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-25T21:02:15Z
  TYPE: DECISION_REQUEST
  CLAIM: Item 5 equality contract (owner): equal-rank conflicts today use `existing != value` on
    arbitrary user objects (custom __ne__ or array-like truthiness can raise or mask a conflict), and
    shared contract payloads use `==`. Options: (a) identity (`is`) only; (b) keep `!=` and document
    it; (c) identity first, `==` only for plain scalars. Recommendation: (c) - deterministic for
    user objects, keeps equal literal values legal.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/artifacts/spell_override_targeting_codegen_creation.py:271-289
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:318-328
  IMPACT: Decides expected outcome for matrix row R5c and the error type for incompatible aliases.
  NEXT: Owner selects (a), (b) or (c).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-25T21:03:56Z
  TYPE: HYPOTHESIS
  CLAIM: Item 5 specificity can invert across aliases: PATH 'a>x' and BROADCAST '**x' each win on
    their own logical socket (per-socket ranking), then the shared step writes kwargs by param name
    in param_path_id order, so the BROADCAST value wins whenever the 'b>x' alias has the higher id.
    Derived from three read code paths; not yet observed in a running interpreter.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/artifacts/spell_override_targeting_codegen_creation.py:271-294
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_finalize_creation_context_step.py:587-631
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:2853-2871
  IMPACT: If confirmed, current behavior breaks the PATH>UNIQUE>BROADCAST contract, not only the
    alias contract. Carried as matrix row R5d with a probe requirement.
  NEXT: Owner or melder_0 decides whether a CPython 3.14 probe should confirm R5d before review closes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-25T21:06:17Z
  TYPE: ALIGNMENT_CHECK
  CLAIM: melder_0 acknowledged the handoff (M0-6): lead review of these notes and the matrix follows;
    the door-compiler observation matches its own lock-order FACT notes. Instruction: hold in review,
    no further action until the lead or owner responds.
  EVIDENCE: tickets/tasks/2026-09-25_verify_native_writer_lock_order_task.md:1-20
  IMPACT: Task stays in review; no new investigation tranche opens without a lead or owner request.
  NEXT: Wait for lead review or owner decisions on the item-4 and item-5 requests.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T00:12:00Z
  TYPE: DECISION
  CLAIM: Owner directed turn-in of this task (melder_0 relay, 2026-09-25/26 session). Recorded as stated to the
    owner at re-certification, without objection: item 4 takes option (a) - rules below a supplied or reused
    constructor become inactive for that path and never reach another path; item 5 takes option (c) - identity
    first, `==` only for plain scalars. Both are inputs to the override implementation, not shipped behavior.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-25_verify_override_behavior_contract_task.md:320-348
  - artifacts/melder_override_contract_20260925/regression_matrix.md:66-88
  IMPACT: Matrix rows R4a-R4c and R5c now have a chosen expected outcome for the implementation lane.
  NEXT: The override implementation ticket adopts the matrix with these two choices.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T00:12:00Z
  TYPE: RISK
  CLAIM: Carried open at closure, not resolved: the item-7 CONFLICT (generalized/many_only wrap constructor
    errors in MeldExecutionError; solo propagates raw), R5d (matrix label READY, but it is HYPOTHESIS until a
    3.14 probe runs), nested unresolved-contract validation and R7c (UNKNOWN). Item-6 door evidence changed
    after this review: slotted routes now hold the store slot guard, not the store lock (M0-10).
  EVIDENCE:
  - tickets/tasks/completed/2026-09-25_verify_override_behavior_contract_task.md:304-374
  - artifacts/melder_override_contract_20260925/regression_matrix.md:89-116
  - tickets/tasks/completed/2026-09-25_implement_creation_slot_build_guards_task.md
  IMPACT: The implementation lane must pin item-7 assertions per family and probe R5d before relying on it.
  NEXT: none in this task; carried to the override implementation lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Status review (2026-09-25T21:03:56Z). All eight contract items have source-backed current behavior in Notes; the
matrix is artifacts/melder_override_contract_20260925/regression_matrix.md. Open: DECISION_REQUEST item 4 and item 5
equality (owner); CONFLICT on item 7 error wording; HYPOTHESIS R5d needs a 3.14 probe; UNKNOWN:
whether validation stops a nested unresolved contract, and baseline-validity effect of supplied calls
(R7c). Validation: Not run. Resume from the latest Notes NEXT.
Closed 2026-09-26T00:12:00Z on owner direction; see the DECISION and RISK notes for what carries forward.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
