# Epic: Explore Top-Down Compiler Strategy Harness

## Metadata
- Epic ID: EPIC-2026-06-02-explore-topdown-compiler-strategy-harness
- Status: in_progress
- Owner: codex
- Agent Name: compiler_0
- Priority: p0
- Created: 2026-06-03T00:05:00Z
- Updated: 2026-06-03T00:05:00Z
- Target Window: 2026-Q3
- Related Program/Initiative: top-down compiler convergence and strategy exploration

## Problem / Opportunity
Melder is not trying to win as a slightly slower bottom-up DI resolver. The
point of the compiler is to convert top-down global knowledge into durable,
reusable spell-static artifacts so the runtime can amortize the expensive
reasoning pass instead of paying that tax on every meld.

Current state:
- the compiler facade is mostly ported
- phases 1-11 are explicit and routed through compiler-owned surfaces
- the rooted system layer, analyzer, processor, planner, and codegen creation
  layers all exist
- runtime now consumes `_spell_codegen_creation` through
  `CreationContextBuilder`

But the system is still a hybrid:
- discovery in phase 11 still selects the raw internal generalized strategy
  chain instead of selecting a real creation strategy family
- codegen creation still contains large monolithic compiler surfaces and bridge
  logic from the old runtime shape
- runtime still has to rehydrate and specialize too much of the creation
  contract after compiler work is supposedly complete
- there is no proper exploration harness yet for shape-aware strategy work

That means we cannot yet do the real optimization pass:
- throw many object graph shapes at the compiler
- measure cold and warm behavior separately
- compare wide vs narrow, solo vs deep, shared vs transient, override-free vs
  override-heavy, contract-heavy vs simple graphs
- let discovery choose genuinely different strategy families from rich model
  truth

## MRP Alignment (Most Reasonable Product)
The MRP is not a one-off micro-optimization. It is a coherent exploration and
convergence lane that gets Melder to the point where top-down compiler work
can be amortized and exploited intentionally.

The correct foundation is:
- converge the compiler and runtime boundary so `_spell_codegen_creation` is a
  real spell-static handoff
- build an exploration harness that can generate and execute many graph shapes
- classify graph shapes and runtime postures in ways the discovery systems can
  reason about
- spend a bounded exploration window testing alternative strategy families
- then lock in the first serious optimization wave

This is the right long-term foundation because Melder's advantage is not
"faster initial lookup." It is:
- richer validation
- richer diagnostics
- deeper override semantics
- stronger agent-facing manipulation surfaces
- global top-down knowledge that can become specialized compiled execution

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a new epic and deep artifact for
  compiler convergence, strategy exploration, and harness design.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell_compiler/`
  - `src/melder/aether/conduit/meld/`
  - `src/melder/aether/conduit/creations/`
  - `codex/context_compass/tickets/epics/`
  - `codex/context_compass/artifacts/`
  - `codex/context_compass/attention_board.md`
  - `codex/context_compass/artifact_board.md`
- DEPENDENCIES:
  - `tickets/epics/2026-06-01_group_codegen_creation_into_family_strategies_epic.md`
  - `artifacts/2026-05-30_execution_strategy_compiler_direction.md`
  - `artifacts/2026-05-30_phase12_north_star_runtime_model.md`
  - `system_docs/src_architecture.md`
  - `system_docs/src_components.md`
  - `system_docs/readable_src_graph.json`
- EXIT_GATE:
  - the compiler convergence target is explicit
  - the exploratory harness goal is explicit
  - the shape taxonomy is explicit
  - the story breakdown for the 2-month exploration window is explicit
  - the new artifact is linked and routed from board and artifact state
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the lane is pushed into
  implementation before the harness and exploration taxonomy are pinned down.

## Goals (Outcomes)
- Define the real compiler convergence target for top-down specialization.
- Separate compiler-owned spell-static artifacts from runtime-only
  specialization responsibilities.
- Define the exploration harness needed to test many graph configurations.
- Define the object-shape taxonomy discovery systems should eventually use.
- Establish a 2-month exploration program before deeper optimization lock-in.
- Preserve a clear benchmark story against bottom-up DI systems like Dishka.

## Non-Goals (Explicit Exclusions)
- No immediate code change to "beat Dishka" in this epic.
- No flattening of Melder into a bottom-up resolver model.
- No premature hard-coding of one permanent strategy family.
- No benchmark theater without a proper harness.
- No collapsing compiler and runtime boundaries to get a short-term speed win.

## Scope Boundaries
- In scope:
  - compiler architecture and convergence target
  - phase-11 discovery and creation-system role
  - runtime-consumer boundary through `CreationContext*`, `Meld`, and
    `Creations`
  - harness requirements
  - graph-shape taxonomy
  - metrics and exploration program
- Out of scope:
  - immediate full implementation of the harness
  - immediate rollout of all strategy families
  - final benchmark claims
  - unrelated runtime redesign outside compiler and creation-boundary needs

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a new compiler exploration
  epic and a linked deep strategy artifact.

## Success Metrics
- One explicit architecture artifact explains the current compiler/runtime
  shape, the convergence target, and the exploration program.
- The shape taxonomy covers width, depth, existence, override posture, and
  contract or mutation complexity.
- The exploration harness requirements are concrete enough to build without
  guesswork.
- The epic defines the story sequence for the next 2 months of compiler
  exploration work.

## Requirements (Functional + Non-Functional)
- Discovery must eventually reason over meaningful object-graph and runtime
  shape, not only generic planner strategy ids.
- Harness scenarios must include:
  - wide graphs
  - narrow graphs
  - solo graphs
  - deep graphs
  - mixed depth and width DAGs
  - shared vs transient existences
  - spellspace, conduit, and broader shared scopes
  - override-free and override-heavy routes
  - contract and mutation-aware routes
- Benchmarking must split:
  - cold compile cost
  - warm cached execution
  - no-overrides path
  - override-heavy path
  - validation-on path
- The runtime boundary must preserve:
  - compiler-owned spell-static packaging
  - runtime-owned per-call specialization
  - clear responsibility for admission, reuse, and storage routing

## Constraints / Assumptions
- All tested structures are still DAGs over Python objects.
- Top-down global reasoning is more expensive than bottom-up local lookup on
  the cold path.
- That cost is acceptable only if we turn it into durable compiled leverage.
- Rich validation and override surfaces are part of the product advantage, not
  incidental overhead to be discarded.
- Discovery and strategy exploration will be iterative and benchmark-driven.

## Dependencies / External References
- Dishka and similar bottom-up DI systems are comparison points, not design
  templates.
- Existing compiler direction artifact:
  `artifacts/2026-05-30_execution_strategy_compiler_direction.md`
- Existing phase-12 runtime artifact:
  `artifacts/2026-05-30_phase12_north_star_runtime_model.md`

## Milestones (Track Progress)
- [ ] Milestone 1: Compiler boundary convergence defined.
- [ ] Milestone 2: Exploration harness architecture defined.
- [ ] Milestone 3: Object-shape taxonomy defined.
- [ ] Milestone 4: Story plan for the 2-month exploration window defined.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-06-02-compiler-boundary-convergence
  Compiler-owned spell-static handoff vs runtime specialization boundary.
- [ ] Story: STORY-2026-06-02-compiler-exploration-harness
  Harness architecture, scenario execution model, and metrics collection.
- [ ] Story: STORY-2026-06-02-object-shape-taxonomy
  Width, depth, existence, override, and contract or mutation taxonomy.
- [ ] Story: STORY-2026-06-02-strategy-discovery-exploration
  Candidate discovery heuristics and strategy-family evaluation rules.
- [ ] Story: STORY-2026-06-02-benchmark-discipline
  Cold/warm path separation and comparison protocol against bottom-up systems.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Keep the compiler direction artifact and this epic aligned.
- [ ] Task: Prevent premature implementation drift before harness design is
  explicit.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The architecture artifact clearly explains the current shape and the
  convergence target.
- The harness design is concrete enough to implement directly.
- The shape taxonomy is concrete enough to generate scenario matrices.
- The story sequence for the exploration window is explicit and reviewable.

## Risks / Mitigations
- Risk: optimizing the wrong path.
  - Mitigation: separate cold compile cost from warm execution cost.
- Risk: pushing old compiler/runtime leakage deeper into runtime.
  - Mitigation: keep `_spell_codegen_creation` as the spell-static handoff and
    document the runtime boundary clearly.
- Risk: benchmark theater with unrepresentative graphs.
  - Mitigation: define a scenario taxonomy before benchmarking.
- Risk: imitating bottom-up systems and losing Melder's real advantage.
  - Mitigation: keep validation, diagnostics, and override power as first-class
    success criteria.

## Applicable Anti-Patterns
- [ ] No benchmark claims without a harness.
- [ ] No compiler/runtime boundary blur justified only by short-term speed.
- [ ] No strategy discovery locked to raw implementation plumbing forever.
- [ ] No reduction of Melder's top-down leverage into bottom-up imitation.

## Validation / Test Approach
- Not run.
- This epic is architecture and planning work only.
- Validation here is source-backed coherence and durable planning quality.

## Rollout / Adoption Plan
- Start with architecture convergence and harness definition.
- Build scenario generators and benchmark harness next.
- Spend the planned exploration window testing strategy families.
- Promote winning strategies into the live discovery systems afterward.

## Open Questions
- Which shape signals should be compile-time only vs runtime-fed back into
  discovery evolution?
- How much of the fast-path array shape should remain planner-owned vs move
  into a dedicated build-state object?
- Which metrics matter most for AI-heavy iterative usage beyond raw throughput?

## Decision Log
- The compiler is treated as the leverage point for amortizing top-down
  reasoning cost.
- Dishka-speed parity is not the primary architecture target; durable compiled
  leverage is.
- Harness-first exploration is required before serious optimization claims.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-06-02_topdown_compiler_exploration_strategy.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: when the exploratory program is complete and durable docs
  replace the active strategy artifact.

## Notes
- DATETIME: 2026-06-03T00:05:00Z
  TYPE: FACT
  CLAIM: The compiler facade is mostly ported, but phase 11 discovery still
    selects the raw internal generalized chain, and runtime still has to
    rehydrate too much spell-static packaging after `_spell_codegen_creation`.
    That means Melder has not yet cashed in the top-down leverage it pays for.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/codegen_creation_discovery_system.py:1-66
  - src/melder/aether/spellbook/spell_compiler/codegen_creation/codegen_creation_system.py:1-120
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:1-195
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1-1290
  IMPACT: The next serious optimization work should be organized as compiler
    convergence plus exploration, not just phase-11 local cleanup.
  NEXT: use the linked artifact as the strategy anchor and break out the first
    story on compiler/runtime boundary convergence.
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
This epic reframes the compiler lane from a narrow phase-11 cleanup into the
broader top-down compiler convergence and exploration program. The immediate
next step is to use the linked artifact as the design anchor, then break out
the first story on boundary convergence before any harness implementation
starts.
