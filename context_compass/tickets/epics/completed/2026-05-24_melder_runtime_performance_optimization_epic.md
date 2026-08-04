# Epic: Melder Runtime Performance Optimization

## Metadata
- Epic ID: EPIC-2026-05-24-melder-runtime-performance-optimization
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p1
- Created: 2026-05-24T17:50:24Z
- Updated: 2026-06-01T11:05:49Z
- Target Window: 2026-Q2
- Related Program/Initiative: Melder runtime competitiveness and scope-first performance hardening

## Problem / Opportunity
Melder has already recovered substantial time by removing obvious churn, but
the remaining gap is still large enough to matter in scope-heavy and
transaction-heavy workloads. The current evidence points to five primary
families:
- warm-path descend-through-runtime overhead
- repeated spellspace access and creation-store probing
- post-pooling reset and return cost
- lock churn on creation-hit and executor paths
- over-broad transaction locality on mutation-changing operations

This is no longer a "something is slow somewhere" problem. The remaining work
is concrete enough to rank and attack in a deliberate order.

## MRP Alignment (Most Reasonable Product)
The right foundation is not micro-optimizing random methods. The right
foundation is:
- flatten the warm path
- keep scope churn cheap
- keep transaction semantics precise instead of broad
- preserve correctness and lifecycle truth while doing it

That gives Melder a coherent runtime that is fast in the common path and still
worthy of the structural capability it exposes.

## Ticket Contract
- ENTRY_GATE: the top performance claims are audited against current source and
  the active benchmark findings are reopened from ticket memory before any
  implementation starts.
- EXECUTION_BOUNDARY:
  - `src/melder/**` runtime performance surfaces directly implicated by the
    ranked opportunities
  - focused benchmark and experimentation helpers needed to measure those
    exact surfaces
  - architecture/component docs only when runtime ownership or documented
    wiring changes
- DEPENDENCIES:
  - `tickets/tasks/2026-05-24_investigate_performance_roadmap_claims_task.md`
  - `tickets/tasks/2026-05-23_investigate_single_meld_lock_and_check_cleaned_paths_task.md`
  - `tickets/tasks/2026-05-24_investigate_transaction_mediator_runtime_overhead_task.md`
- EXIT_GATE: the top-ranked stories are implemented or explicitly superseded,
  their validation is accepted, and board/ticket state is synchronized.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a top-ranked optimization
  conflicts with runtime correctness, invalidation safety, or transaction
  semantics.

## Goals (Outcomes)
- Rank 1: add a real warm-hit seal at the meld front door.
- Rank 2: hoist `get_active_spellspace()` and stop re-reading it throughout one executor run.
- Rank 3: optimize pooled lesser-conduit and spellspace reset/return paths.
- Rank 4: collapse repeated executor-side lock regions into fewer hot-path critical sections.
- Rank 5: trim creations-hit-path churn where locking or wrapper traffic is unnecessary.
- Rank 6: reduce first-build Phase 11 IR/signature churn.
- Rank 7: split spell lookup caching from resolved live-hit caching.
- Rank 8: narrow `LINK` transaction locality to real local-edge semantics.
- Rank 9: optimize mediator-era transaction-changing paths without blaming conduit creation on mediator.
- Rank 10: add a spellspace-first benchmark posture distinct from structural conduit churn.
- Rank 11: evaluate a bare-object fast path for non-disposable `Creation` entries.
- Rank 12: reduce `creation.value` indirection in hot reuse paths.
- Rank 13: remove inner-layer `check_cleaned()` calls where an outer live-contract already proved liveness.
- Rank 14: share inherited hook maps instead of copying them through lesser runtime churn.
- Rank 15: make `ConduitWard` lighter for lesser conduits.
- Rank 16: reduce repeated `SpellIndex.current` reads in compile/planning paths.
- Rank 17: reduce repeated storage probing in generated spellspace routes.
- Rank 18: revisit cluster/share runtime hot paths after the warm path is flatter.
- Rank 19: re-evaluate `DevopsIdentity` and registry overhead after the core hot path is flatter.
- Rank 20: re-rank conjure-time work after runtime hot-path fixes land.

## Non-Goals (Explicit Exclusions)
- Blind micro-optimization without measured or source-backed need.
- Broad runtime rewrites before the top-ranked items are classified or measured.
- Treating `TransactionMediator` as the culprit for lesser-conduit creation cost without evidence.
- Reintroducing removed lifecycle guards just to improve benchmark numbers.

## Scope Boundaries
- In scope:
  - top 20 runtime opportunities listed in this epic
  - focused benchmark, cProfile, and one-meld investigations needed to validate them
  - runtime changes that directly support those ranked items
- Out of scope:
  - unrelated API redesign
  - broad test churn not tied to runtime-performance work
  - speculative architecture rewrites with no direct performance evidence

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the ranked opportunity list is now explicit enough to justify a durable epic umbrella.

## Success Metrics
- Melder median and throughput improve materially on the current real-world gauntlet shapes.
- The remaining warm-path overhead is measurably flatter on focused single-meld benches.
- Scope churn stays bounded after pooling rather than shifting all cost into reset/return.
- Transaction-changing paths have narrower locality and lower avoidable overhead.

## Requirements (Functional + Non-Functional)
- Every optimization story must preserve runtime correctness and invalidation semantics.
- Every optimization story must include focused validation or measurement.
- Hot-path claims must be source-backed or measurement-backed.
- Lower-level lifecycle and ownership contracts must stay truthful after optimization.

## Constraints / Assumptions
- The current source is authoritative over pasted roadmap wording.
- cProfile is useful for call counts and relative ranking, not absolute wall time.
- Scope-heavy gauntlet numbers and transaction-path microbenches are measuring different costs and must stay separated.

## Dependencies / External References
- `benchmarks/testing_other_di/test_real_world_gauntlet.py`
- `benchmarks/testing_other_di/test_real_world_gauntlet_cprofile.py`
- `benchmarks/testing_other_di/test_melder_gauntlet.py`
- `benchmarks/testing_other_di/test_melder_single_meld_lock_and_check_cleaned.py`

## Milestones (Track Progress)
- [ ] Milestone 1: Warm-path flattening
  Success criteria: seal, spellspace-hoist, and creations-hit-path work are landed and benchmarked.
- [ ] Milestone 2: Scope-churn stabilization
  Success criteria: pooled reset/return costs are reduced and remeasured.
- [ ] Milestone 3: Transaction locality narrowing
  Success criteria: link and related transaction paths are classified and narrowed where appropriate.
- [ ] Milestone 4: Conjure/build-path cleanup
  Success criteria: first-build churn items are re-ranked after warm-path changes.

## Stories (Required to Complete)
- [ ] Story: seal the meld warm-hit path with safe invalidation.
- [ ] Story: hoist spellspace-active lookups and collapse repeated spellspace probing.
- [ ] Story: optimize lesser-conduit/spellspace pool reset and return paths.
- [ ] Story: narrow creations/executor lock churn on hot routes.
- [ ] Story: classify and narrow transaction locality for link-style operations.
- [ ] Story: reduce first-build planning churn after warm-path fixes.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task 1: Implement Rank 1 warm-hit seal.
- [ ] Task 2: Implement Rank 2 spellspace active lookup hoist.
- [ ] Task 3: Implement Rank 3 pool reset/return optimization.
- [ ] Task 4: Implement Rank 4 executor-side lock consolidation.
- [ ] Task 5: Implement Rank 5 creations-hit-path cleanup.
- [ ] Task 6: Revisit Rank 6 first-build Phase 11 churn.
- [ ] Task 7: Revisit Rank 7 cache split between lookup and live-hit.
- [ ] Task 8: Revisit Rank 8 local-edge transaction locality.
- [ ] Task 9: Revisit Rank 9 mediator transaction-path overhead.
- [ ] Task 10: Add Rank 10 spellspace-first benchmark posture.
- [ ] Task 11: Revisit Rank 11 no-wrapper `Creation` fast path.
- [ ] Task 12: Revisit Rank 12 `creation.value` indirection.
- [ ] Task 13: Revisit Rank 13 inner `check_cleaned()` trimming.
- [ ] Task 14: Revisit Rank 14 inherited hook-map sharing.
- [ ] Task 15: Revisit Rank 15 lighter lesser `ConduitWard`.
- [ ] Task 16: Revisit Rank 16 `SpellIndex.current` compile/planning churn.
- [ ] Task 17: Revisit Rank 17 generated spellspace storage probing.
- [ ] Task 18: Revisit Rank 18 cluster/share hot paths.
- [ ] Task 19: Revisit Rank 19 `DevopsIdentity` and registry overhead after hot-path flattening.
- [ ] Task 20: Revisit Rank 20 conjure/build-path ranking after runtime improvements.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The top-ranked opportunities are turned into concrete child stories/tasks.
- The first execution slice is accepted and measured.
- The list remains evidence-backed and updated when measurements invalidate earlier assumptions.

## Risks / Mitigations
- Risk: a high-ranked item is directionally right but numerically stale.
  Mitigation: measure before widening implementation.
- Risk: a speed win breaks invalidation or cleanup truth.
  Mitigation: keep correctness and lifecycle checks in every child story.
- Risk: benchmark shapes are conflated.
  Mitigation: keep warm-path, scope-churn, and transaction-path benches separated.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Use focused benches for:
  - one-meld hot path
  - scope churn/reset
  - transaction-changing paths
- Reuse real-world gauntlet and cProfile harnesses as comparative backstops.
- Treat cProfile as ranking/count evidence, not absolute wall-clock truth.

## Rollout / Adoption Plan
- Start with one narrow execution slice around the warm-hit seal.
- Re-profile after the first slice lands.
- Re-rank the rest before widening into lower-confidence work.

## Open Questions
- How much of the remaining warm gap can the seal absorb by itself?
- Which remaining `Creations` lock paths are still necessary after a seal?
- Does local-edge transaction locality require new explicit scope primitives or only strategy rewrites?

## Decision Log
- Decision: make the roadmap durable as one epic instead of leaving it only in chat.
- Decision: rank by payoff x confidence, not by novelty.
- Decision: do not keep `TransactionMediator` ranked as a top conduit-creation issue because current evidence does not support that.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: ticket closure

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
- DATETIME: 2026-05-24T17:50:24Z
  TYPE: FACT
  CLAIM: The top five items are the most credible near-term moves because they
    are directly supported by current source and measurements:
    1. warm-hit seal
    2. spellspace active lookup hoist
    3. pool reset/return optimization
    4. executor-side lock consolidation
    5. creations-hit-path cleanup
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:334-369
  - src/melder/aether/conduit/meld/meld.py:494-529
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:568-569
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:758-805
  - src/melder/aether/conduit/creations/creations.py:550-624
  - src/melder/aether/conduit/conduit.py:1552-1653
  - tickets/tasks/2026-05-24_investigate_performance_roadmap_claims_task.md:101-151
  IMPACT: These items should be the first execution tranche rather than spreading effort across lower-confidence ideas.
  NEXT: use this epic to launch the first child slice around the warm-hit seal.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T17:50:24Z
  TYPE: FACT
  CLAIM: The old claim that `TransactionMediator` is a top gauntlet-path scope
    create/cleanup culprit is not supported by current code or focused
    measurement. `Conduit.create_lesser_conduit(...)` does not enter the
    mediator path at all, while the focused dynamic microbench showed mediator
    cost on bind/link transaction roundtrips only.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1552-1653
  - src/melder/aether/conduit/conduit.py:1946-2183
  - src/melder/aether/spellbook/spellbook.py:2139-2302
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:630-742
  - tickets/tasks/2026-05-24_investigate_transaction_mediator_runtime_overhead_task.md:86-118
  IMPACT: Mediator work should be optimized as a transaction-path concern, not blamed for lesser-conduit creation cost.
  NEXT: keep mediator work lower in the ranking than the warm-path and scope-reset items.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T17:50:24Z
  TYPE: MEASURE
  CLAIM: The latest 3-thread real-world gauntlet cProfile dataset strengthens
    the warm-path and spellspace claims directly. The run still shows:
    - `spell_space_thread_state.get_active` and `creations.get_active_spellspace`
      at `17,916` calls each
    - `conduit_pool.return_lesser_conduit` and
      `creations.reset_non_spellspace_for_pool` as visible hot functions
    - hot-path dominance from `_get_existing_creation`, `creation.value`, and
      `cleanable.check_cleaned`
  EVIDENCE:
  - user_provided_profile_dataset
  - tickets/tasks/2026-05-24_investigate_performance_roadmap_claims_task.md:76-99
  IMPACT: The roadmap ranking should stay centered on warm-hit flattening,
    spellspace hoisting, and reset-path cleanup.
  NEXT: launch the seal story first and re-rank after it lands.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T19:06:30Z
  TYPE: FACT
  CLAIM: The stale singleton-typing route that was still sitting in active
    board state has been repaired. The original active task file was missing,
    so the route was removed from `## Active Items`, its matching active
    attention-detail block was removed, and a reconstructed completed record
    now preserves that slice outside the live `mutres_0` lane. That leaves
    this epic as the live umbrella for current Melder optimization work again.
  EVIDENCE:
  - codex/context_compass/attention_board.md:501-508
  - codex/context_compass/tickets/tasks/completed/2026-05-21_fix_nexus_and_mutation_research_singleton_optional_typing_task.md:1-21
  IMPACT: Current `mutres_0` routing is cleaner and the optimization epic is
    once again the correct top-level lane to continue from.
  NEXT: continue from the epic and choose the first execution slice from the
    current ranked set rather than reviving stale singleton-typing work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-24T19:06:30Z
  TYPE: FACT
  CLAIM: The current meld stack already caches two of the three lookup layers:
    `Meld` caches request identity to resolved `Spell`, and `Spell` caches
    `Spell` to `CreationContext` via the spell-owned counter-switch/factory
    path. The missing optimization layer is not another lookup cache. It is a
    cached hit-only execution lane attached to the spell/context that can probe
    the live creation store and return immediately before the existing
    no-hooks/no-overrides executor path is entered.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:334-381
  - src/melder/aether/spellbook/spell.py:665-692
  - src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:221-259
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:24-98
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:123-239
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:536-618
  - src/melder/aether/spellbook/spell_compiler/blueprints/phase12_no_overrides_executor.py:1341-1379
  IMPACT: The first fast-path slice should be designed as one compiled
    `try_hit(...)` lane per exact route shape, not as `binding -> context`
    caching and not as object caching. That keeps invalidation aligned to the
    existing spell/context rebuild contract while skipping the Phase 12 reuse
    machinery on warm hits.
  NEXT: design the first exact fast lane as
    `no_overrides + no_hooks + unique_per_conduit`, then decide whether to
    attach it to `CreationContext` or a sibling spell-owned plan object.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T19:06:30Z
  TYPE: FACT
  CLAIM: The override path is already doing real specialization caching inside
    `CreationContext`. It seeds a baseline override executor, caches compiled
    executors by `(plan_signature, socket_shape, root_positional_arity)`, keeps
    a hot `last_executor` reuse slot, and separately caches override socket
    shapes. That means the first new flattening work should not try to reinvent
    override caching. The actual gap is the no-override warm-hit path, which
    still goes through the general compiled executor stack on every hit.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:560-737
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:799-861
  IMPACT: The first fast-path slice should stay on the no-hooks/no-overrides
    path and add a hit-only lane there, while leaving the existing override
    specialization machinery alone for now.
  NEXT: keep the first experiment scoped to `unique_per_conduit` no-hook,
    no-override hits instead of broadening into override-path redesign.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic is the durable umbrella for the current Melder performance ranking.
The first intended execution slice is the warm-hit seal, followed by
spellspace-hoist and reset-path work, with mediator work kept scoped to actual
transaction-changing paths rather than conduit creation.

