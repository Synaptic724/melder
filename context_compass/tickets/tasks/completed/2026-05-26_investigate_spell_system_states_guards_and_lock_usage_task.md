# Task: Investigate SpellSystemStates Guards And Lock Usage

## Metadata
- Task ID: TASK-2026-05-26-investigate-spell-system-states-guards-and-lock-usage
- Story: none
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p1
- Created: 2026-05-26T16:28:41Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Map every meaningful guard, `check_cleaned()` use, and lock boundary across
`SpellSystemStates` and its immediate owned state surfaces so we can decide
which internal guards are protecting real invariants and which ones are just
costly internal-public-surface baggage.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a source-backed guard/lock audit of
  `SpellSystemStates` before any trimming discussion.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py`
  - `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_state.py`
  - `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/conduit_resolution_state.py`
  - `src/melder/aether/spellbook/spell_compiler/system/spell_system_adjacency_builder.py`
  - directly implicated callsites only when needed to explain observed lock/guard use
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - `tickets/tasks/2026-05-24_investigate_performance_roadmap_claims_task.md`
  - `tickets/tasks/2026-05-24_investigate_phase_scheduler_and_spell_compiler_pipeline_task.md`
- EXIT_GATE: the guard types, lock boundaries, nested-lock paths, and plausible
  trim candidates are summarized with direct evidence and one bounded next
  implementation recommendation.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if separating removable guards
  from invariant-preserving guards requires widening into a larger dev-ops or
  validation redesign.

## Scope Boundaries
- In scope:
  - `check_cleaned()` usage
  - cleaned-state / `None` / empty-input / required-collaborator guards
  - coarse vs nested lock usage
  - read-path vs write-path lock patterns
  - adjacency-builder lock reach-through into `SpellSystemStates`
- Out of scope:
  - runtime guard removal implementation
  - broad change-control redesign
  - unrelated performance claims outside this object family

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a bounded audit of
  `SpellSystemStates` guards and lock usage.

## Steps / Checklist
- [ ] Inventory guard types in `SpellSystemStates`.
- [ ] Inventory lock entry/exit paths in `SpellSystemStates`.
- [ ] Inventory nested lock interactions with `SpellSystemState`,
      `ConduitResolutionState`, and `SpellSystemAdjacencyBuilder`.
- [ ] Classify guards into invariant-preserving vs trim-candidate buckets.
- [ ] Summarize a bounded next optimization cut.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- one evidence-backed guard inventory
- one evidence-backed lock-usage map
- one bounded recommendation for the first guard/lock trimming slice

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-26_investigate_spell_system_states_guards_and_lock_usage_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "check_cleaned|with self\\._lock|raise ValueError|raise RuntimeError|if not |if .* is None" src\\melder\\aether\\aetheric_frame\\dev_ops\\spell_system_states\\*.py`

## Risks / Rollback Notes
- Risk: some guards that look redundant at this layer may still be preserving
  multi-map coherence or teardown safety for external callers.
  Rollback: keep the audit source-first and separate “expensive” from
  “removable” instead of assuming they are the same.

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
- CLEANUP_TRIGGER: ticket closure

## Noting Behavior
- Note focus: concrete guard classes, concrete lock scopes, and one-step
  continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-01T11:05:49Z
  TYPE: DECISION
  CLAIM: The user explicitly accepted this lane as complete and requested that
    it be turned in and moved out of active routing.
  EVIDENCE:
  - user_instruction
  IMPACT: This ticket is now closed and should no longer appear in active
    board routing.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-26T16:28:41Z
  TYPE: PLAN
  CLAIM: The user wants a deep-object audit, not another generic
    `check_cleaned()` complaint. The right cut is to inventory guard types and
    lock boundaries across `SpellSystemStates`, `SpellSystemState`,
    `ConduitResolutionState`, and the adjacency builder that reaches into them.
  EVIDENCE:
  - user_instruction
  IMPACT: The next step is a method-level guard/lock map, not runtime edits.
  NEXT: read the three state objects and the adjacency builder in bounded
    chunks, then record the first concrete guard/lock classification.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-26T16:28:41Z
  TYPE: FACT
  CLAIM: The `SpellSystemStates` object family uses four different guard
    classes today:
    1. lifecycle guards via `check_cleaned()`,
    2. cleanup double-check guards (`if self._cleaned` before and under lock),
    3. input guards (`if not ...` / `is None` with `ValueError` or no-op),
    4. post-cleanup container-availability guards (`_states_by_* is None`,
       `_resolution_by_conduit_id is None`, `_flags is None`) inside locked
       bodies.
    The lock topology also splits clearly:
    - `SpellSystemStates` owns one coarse registry `RLock`,
    - `SpellSystemState` owns one per-lineage `RLock`,
    - `ConduitResolutionState` owns one per-conduit `RLock`,
    - `SpellSystemAdjacencyBuilder.build(...)` nests the coarse registry lock
      with per-lineage state locks.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:45-132
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:453-556
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:697-830
  - src/melder/aether\aetheric_frame\dev_ops\spell_system_states\spell_system_states.py:930-1029
  - src/melder\aether\aetheric_frame\dev_ops\spell_system_states\spell_system_states.py:1159-1303
  - src/melder\aether\aetheric_frame\dev_ops\spell_system_states\spell_system_state.py:64-154
  - src/melder\aether\aetheric_frame\dev_ops\spell_system_states\spell_system_state.py:160-510
  - src/melder\aether\aetheric_frame\dev_ops\spell_system_states\conduit_resolution_state.py:95-180
  - src/melder\aether\aetheric_frame\dev_ops\spell_system_states\conduit_resolution_state.py:223-332
  - src/melder\aether\aetheric_frame\dev_ops\spell_system_states\conduit_resolution_state.py:374-522
  - src/melder\aether\aetheric_frame\dev_ops\spell_system_states\conduit_resolution_state.py:581-664
  - src/melder\aether\spellbook\spell_compiler\system\spell_system_adjacency_builder.py:33-97
  IMPACT: We now have enough structure to separate “coarse lock protecting
    multi-map coherence” from “defensive internal-public-surface guards that
    may be trim candidates.”
  NEXT: classify which methods truly need the coarse lock and which getter /
    post-cleanup guard surfaces look redundant enough to trim first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-26T16:28:41Z
  TYPE: FACT
  CLAIM: The lifecycle-guard surface is broad enough to matter. Current
    `check_cleaned()` counts are:
    - `SpellSystemStates`: `29`
    - `SpellSystemState`: `21`
    - `ConduitResolutionState`: `18`
    The broad pattern is “public-ish method/property -> `check_cleaned()` ->
    maybe input guard -> maybe lock -> maybe extra post-cleanup field guard.”
    That is coherent for a public API, but it is expensive for an internal
    runtime state family that is already tightly owned and frequently called by
    compiler/runtime internals.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_state.py
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/conduit_resolution_state.py
  - measurement_result: `rg -c "check_cleaned\\(" ...` -> `29 / 21 / 18`
  IMPACT: There is enough surface here that trimming guard cost can be a real
    optimization target, but only if we avoid cutting the guards that are
    standing in for multi-map invariant protection.
  NEXT: separate trim candidates into read-only accessor guards, post-cleanup
    redundancy guards, and true multi-map mutation guards.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-26T16:36:12Z
  TYPE: FACT
  CLAIM: The caller map makes the hot paths pretty clear. The methods sitting
    on real compiler/runtime traffic are:
    - `register_index(...)`: `Spellbook.bind(...)`, transfer ownership
    - `update_dependencies(...)` and `register_local_topology(...)`: Phase 3 only
    - `get_local_topology_by_id(...)`: Phase 6 and validation strategies
    - `get_conduit_resolution_state(...)`: `Meld`, `SpellbookCreationSystem`,
      `RiskManager`, and `Conduit`
    - `get_or_create_conduit_resolution_state(...)`: conduit upgrade and all
      conduit-resolution publish helpers
    - `bulk_set_conduit_spell_validity(...)`,
      `bulk_set_conduit_root_validity(...)`,
      `record_conduit_diagnostics(...)`: Phase 6 and local visibility-failure paths
    - `mark_collection_dependents_dirty(...)`: `Spellbook` and `ChangeControlManager`
    - `mark_contract_dependents_dirty(...)`: `ConduitWard` and `ChangeControlManager`
    The strongest internal-lock smell is the adjacency builder: it bypasses the
    public accessors, takes `SpellSystemStates._lock`, and then takes every
    child `SpellSystemState._lock` while building the frame-wide snapshot.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:998-998
  - src/melder/aether/spellbook/spellbook.py:399-399
  - src/melder/aether/spellbook/spellbook.py:2617-2617
  - src/melder/aether/spellbook/spellbook.py:2751-2751
  - src/melder/aether/spellbook/spellbook_creation_system.py:1417-1417
  - src/melder/aether/spellbook/spellbook_creation_system.py:1776-1786
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:664-668
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_6.py:199-199
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_6.py:458-468
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_validation_system.py:245-258
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_adjacency_builder.py:67-97
  - src/melder/aether/conduit/meld/meld.py:1150-1181
  - src/melder/aether/conduit/meld/meld.py:1321-1321
  - src/melder/aether/conduit/conduit.py:596-596
  - src/melder/aether/conduit/conduit.py:1510-1559
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1829-1829
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:576-615
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:788-799
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:461-461
  IMPACT: The first trimming slice should target internal read accessors on
    `SpellSystemState` / `ConduitResolutionState` and redundant registry
    post-cleanup guards, not the coarse multi-map mutation methods. The biggest
    potential lock bottleneck is the frame-wide adjacency snapshot path, not a
    random single getter.
  NEXT: summarize the trim candidates as
    (1) internal read accessors,
    (2) redundant post-cleaned container checks,
    (3) adjacency snapshot locking,
    while explicitly leaving multi-map writers alone for now.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-26T16:39:03Z
  TYPE: DECISION
  CLAIM: The user direction is now explicit: leave the lock model alone for
    this slice, but aggressively trace and then remove internal guard baggage
    (`check_cleaned()`, redundant `None`/empty checks, and similar
    internal-safety ceremony) from the `SpellSystemStates` family where the
    callers are already internal runtime/compiler surfaces. That means the next
    investigation step is no longer “should we trim guards?” but “which
    specific guards can be removed without breaking the actual internal call
    contracts?”.
  EVIDENCE:
  - user_instruction
  IMPACT: The remaining discovery work should classify each hot-path method by
    actual caller contract so the first implementation cut is a direct guard
    removal slice, not another abstract discussion.
  NEXT: split the methods into read-accessor, scalar write, multi-map write,
    and adjacency-scan buckets, then mark exactly which guards in each bucket
    are removable under the internal-only contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-26T16:49:16Z
  TYPE: MEASURE
  CLAIM: The current guard-removal edit changed two different things. First, it
    removed boundary-style input/lifecycle guards from `SpellSystemStates`
    methods like `register_index(...)`, `update_dependencies(...)`,
    `get_by_index_id(...)`, and `get_or_create_conduit_resolution_state(...)`.
    Second, because cleanup deletes `_lock`, removing those lifecycle guards
    means post-cleanup calls now degrade into `AttributeError` on missing
    `_lock` instead of failing through a deliberate runtime error. Focused
    validation of `SpellSystemStates` plus `RiskManager` currently shows 4
    failures: two stale boundary-expectation failures (`None` input now blows
    up deeper), and two real cleaned-object failure-mode changes.
  EVIDENCE:
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\dev_ops\spell_system_states\test_spell_system_states.py tests\unit\melder\aether\dev_ops\risk_manager\test_risk_manager.py` -> `4 failed, 47 passed, 2 warnings`
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:307-344
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:697-737
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:137-241
  IMPACT: Not every removed guard is equal. Internal input guards may be fair
    game if the caller contract is strong enough, but cleaned-object guards on
    high-fanout registry entry methods are currently the only thing preventing
    torn-object `AttributeError` crashes after cleanup.
  NEXT: summarize the review as:
    - staged `RiskManager` wiring is intentional,
    - internal read-path guards are the best trim target,
    - cleaned-object stops on high-fanout registry entry methods should be an
      explicit decision, not accidental fallout from deleting `check_cleaned()`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-26T16:57:38Z
  TYPE: FACT
  CLAIM: The `RiskManager` late-wiring is almost entirely an ownership/order
    artifact. `AethericFrame` creates `SpellSystemStates` first, then creates
    `DevOpsManager`; `DevOpsManager` creates `RiskManager` and immediately
    injects it back with `spell_system_states.set_risk_manager(...)`. New
    `SpellSystemState` and `ConduitResolutionState` children also inherit the
    current risk manager on creation. There are no real runtime callers
    depending on `set_risk_manager(...)` beyond this ownership boot path; the
    rest are tests. So the nullable `_risk_manager` surface is not a deep
    semantic requirement of steady-state runtime, it is the result of “DevOps
    owns RiskManager” plus current boot order.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame.py:135-145
  - src/melder/aether/aetheric_frame/dev_ops/dev_ops_manager.py:73-76
  - src/melder/aether/aetheric_frame/dev_ops/dev_ops_manager.py:107-116
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:132-132
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:276-277
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:700-701
  - validation_result: `rg -n "SpellSystemStates\\(|set_risk_manager\\(|_set_risk_manager\\(|_risk_manager = None" src tests -g "*.py"`
  IMPACT: If we want this object family to “just have” a risk manager, the
    clean fix is ownership inversion or co-construction, not more guards. As
    long as `DevOpsManager` owns `RiskManager`, `SpellSystemStates` has to be
    born before the thing it wants to point at.
  NEXT: tell the user plainly that, yes, we can redesign this so
    `SpellSystemStates` owns or is constructed with `RiskManager`, but that is
    an ownership change, not just a reorder.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to define the real guard and lock surfaces around
`SpellSystemStates` before any trimming discussion starts.

