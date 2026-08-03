# Epic: Move compiler phases 1-10 onto a value-only IR and make phase 11 the sole hydration boundary

## Metadata
- Epic ID: EPIC-2026-08-03-comptime-ir-phase-pipeline
- Status: ready
- Owner: cowork
- Agent Name: UNASSIGNED
- Priority: p1
- Created: 2026-08-03T01:45:00Z
- Updated: 2026-08-03T01:45:00Z
- Target Window: unscheduled - open for claim
- Related Program/Initiative: SpellCompiler / Crystallizer / MutationResearch

## Problem / Opportunity

The conjure pipeline is a compiler. It runs requirements finding, symbolic graph
construction, local frame resolution, validation, root blueprints, system
validation, change control, occurrence analysis, injection processing, patch
maps and execution planning, and then EMITS an executor at phase 11 which the
runtime dispatches into. One file per phase exists on disk.

EVIDENCE:
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_1.py
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py
- context_compass/system_docs/src_architecture.md:628-640
- context_compass/system_docs/src_architecture.md:641-651

The compiler's intermediate state is carried in LIVE RUNTIME OBJECTS rather than
in a symbolic representation. Owner statement, 2026-08-03: phases 1-7 use "real
objects" where an IR of strings/values would represent the same structure and be
managed through explicit hydration targets instead of intrinsic object identity.
Owner refined the boundary in the same exchange: **phases 1-10 could use the IR
entirely, and phase 11 computes the rest.**

Four consequences follow from having no IR, and only the first is the one
usually noticed:

1. **The compiler cannot run without the runtime.** Compile-time state and
   runtime state are the same objects, so the phases cannot be exercised,
   tested, or reasoned about in isolation from a live world.
2. **The plan is not an artifact.** It exists only as object graph and
   evaporates. The Crystallizer records source and structure; MutationResearch
   diffs source and structure; NEITHER can see the compiled plan, because there
   is nothing to record.
3. **Restore recompiles from scratch.** A restored world re-runs the phase
   pipeline rather than rehydrating a plan it already computed once. Bulk graph
   construction is the one path where Melder's per-object cost is user-visible
   (see Constraints).
4. **Incremental recompile is hard to make correct.** Change control marks roots
   dirty and triggers revalidation; without a hashable plan there is no cheap
   way to decide what actually needs rebuilding.

## MRP Alignment (Most Reasonable Product)

This is foundational, not additive. `mrp_policy.md` defines MRP as the smallest
product coherent and durable enough that shipping it does not create a trap, and
says explicitly: if the core would need rework immediately after release to
become trustworthy, it is not MRP yet.

The phase pipeline is the core. Every capability layered above it - crystallizer
restore, MutationResearch diffing, codegen, agent-driven structural evolution -
reads or rebuilds compiler state. Doing this after those consumers harden means
retrofitting an IR under live dependents. Doing it now means they are built
against the IR from the start.

There is also an existing standard this lands on rather than inventing: the
project's own dataclass rule already describes an IR node. `init_and_ownership.md`
and `banned_patterns.md` restrict dataclasses to value types - `None`, `bool`,
`int`, `float`, `str` - and forbid storing object instances or resources in
them. An IR built from those dataclasses is compliant by construction, and any
node that cannot be expressed that way is a node still holding a live object.

## Ticket Contract

- ENTRY_GATE: this epic is routed from `attention_board.md`; STORY-1 (phase
  survey) is complete and its findings are recorded before any other story
  opens. No design work proceeds on architecture-doc evidence alone.
- EXECUTION_BOUNDARY: `src/melder/aether/spellbook/spell_compiler/**` and the
  Spellbook conjure call sites that drive it. Crystallizer and MutationResearch
  integration are SEPARATE downstream stories and are out of the first tranche.
- DEPENDENCIES:
  - `agent_onboarding/default/engineer/skills/patch_framework_gating.md`
    (system-impacting: patch docs required before implementation)
  - `system_docs/src_architecture.md`, `system_docs/src_components.md`
  - `agent_onboarding/user_defined/synaptic_python_developer/skills/python/init_and_ownership.md`
- EXIT_GATE: every required story accepted by the owner; both canonical system
  documents updated with the IR boundary and their `*_index.md` regenerated in
  the same pass; gauntlet regression gate green (see Validation).
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the IR cannot express a phase
  without holding an object reference. Raise `CONFLICT` if any IR symbol is
  found reachable from the meld hot path. Raise `BLOCKER` if a phase's current
  behavior cannot be established from source.

## Goals (Outcomes)

- Phases 1-10 operate exclusively on a value-only, serializable IR.
- Phase 11 is the ONLY hydration boundary: it consumes IR and emits the executor.
- The compiled plan becomes a durable, hashable, diffable artifact.
- Compile-time and runtime state are separable, so the phases can be tested
  without a live world.

## Non-Goals (Explicit Exclusions)

- **Meld throughput is not a goal.** Per-object cost is CPython's object model,
  not resolution overhead; the 3.15 JIT result measured +0.22% on this workload,
  which rules out interpreter dispatch as the constraint. Expect no meld speedup
  and do not justify this epic on one.
- No public API change to `Spellbook`, `Conduit`, or `Existence`.
- No change to the emitted executor's runtime semantics.
- Crystallizer plan persistence and MutationResearch plan-grain diffing are
  DOWNSTREAM: enabled by this epic, delivered by their own tickets.

## Scope Boundaries

- In scope: phase modules 1-10, the artifacts they exchange, the phase-11
  hydration boundary, the IR schema and its versioning.
- Out of scope: `meld` and the runtime lane, `Creations`, `ConduitWard`,
  persistence formats, MR diff strategies.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Owner directed the epic be authored and placed on the board
  unclaimed (2026-08-03). Scope boundary is owner-ruled (1-10 IR, 11 computes
  the rest). No agent has claimed it; STORY-1 is the entry point.

## Success Metrics

- 100% of phase 1-10 exchanged artifacts pass a value-only assertion walk.
- IR round-trip (build -> serialize -> deserialize -> hydrate) produces
  behaviorally identical resolution on the full existing test suite.
- Zero symbol lookups reachable from `meld`, demonstrated by benchmark parity
  rather than asserted.
- Recompile of an unchanged Spellbook becomes an IR-hash hit rather than a
  full phase run.

## Requirements (Functional + Non-Functional)

Functional
- IR nodes are value-only dataclasses per `init_and_ownership.md`; containers of
  value types are permitted, object references are not.
- Every IR node carries a stable symbolic id. Hydration resolves symbol -> real
  type exactly once, at phase 11.
- IR is serializable to plain JSON-compatible structures with no custom encoder.
- IR carries a version stamp consistent with the existing `RecordVersion`
  discipline for durable artifacts (`src_architecture.md:1084-1089`).
- IR is content-hashable so an unchanged plan can short-circuit recompilation.

Non-Functional
- Conjure wall time must not regress materially; if it does, the IR is being
  rebuilt where it should be memoized.
- No `getattr`/`hasattr` probing over IR nodes; the schema is owned and visible
  (`banned_patterns.md`).
- Type hints mandatory throughout; `Optional`/`Union`, never PEP 604
  (`typing.md`).

## Constraints / Assumptions

- **UNKNOWN, and this is the epic's largest risk:** the description of phases
  1-11 above is drawn from `src_architecture.md` and from the module layout on
  disk. It is evidence of INTENT and STRUCTURE, not of BEHAVIOR. No phase
  implementation has been read. `unknowns_gate_reference.md` forbids treating
  documents as evidence of behavior; STORY-1 exists to close this and nothing
  else may start first.
- Assumption to test, not to build on: each phase's inter-phase payload is
  already close to value-shaped, and the object references are incidental rather
  than load-bearing. If a phase genuinely needs identity (not just a name), the
  IR needs an explicit identity concept and that is a design decision, not an
  implementation detail.
- Where restore cost is user-visible: reconstructing large worlds. A 10M-object
  world costs seconds in Python; caching the plan removes the recompile half of
  that, not the construction half.

## Dependencies / External References

- `system_docs/src_architecture.md` - Boot and Configuration Sequence, phases
  1-11 and the conjure sequence
- `system_docs/src_components.md` - `Component: SpellCompiler and Validation
  Pipeline`, `Subcomponent: SpellCompiler Phase Artifacts` (slice via
  `src_components_index.md`)
- `agent_onboarding/default/engineer/skills/patch_framework_gating.md`

## Milestones (Track Progress)

- [ ] Milestone 1: Ground truth - every phase's real inputs and outputs
      established from source, object-bound points named with file:line.
- [ ] Milestone 2: IR schema ratified by the owner, with the identity question
      answered explicitly.
- [ ] Milestone 3: Phases 1-10 ported, existing suite green, gauntlet parity.
- [ ] Milestone 4: Phase 11 is the sole hydration boundary, proven not asserted.
- [ ] Milestone 5: IR hashing and comptime memoization landed.

## Stories (Required to Complete)

- [ ] Story: STORY-2026-08-03-phase-pipeline-survey - read `compiler_phase_1.py`
      through `compiler_phase_11.py` and record, per phase, what it consumes,
      what it produces, and every point where it holds a live object rather than
      a value. **Gate: no other story starts until this is accepted.**
- [ ] Story: STORY-2026-08-03-ir-schema-design - define the node/edge schema,
      the symbolic id scheme, the version stamp, and the answer to the identity
      question. Owner ratification required.
- [ ] Story: STORY-2026-08-03-ir-port-phases-1-4 - requirements, symbolic graph,
      local frame, validation.
- [ ] Story: STORY-2026-08-03-ir-port-phases-5-7 - root blueprints, system
      validation, change control.
- [ ] Story: STORY-2026-08-03-ir-port-phases-8-10 - occurrence, injection,
      patch maps, execution plan.
- [ ] Story: STORY-2026-08-03-phase-11-hydration-boundary - phase 11 consumes IR
      and emits; add the test that fails if any symbol is reachable from meld.
- [ ] Story: STORY-2026-08-03-ir-hash-memoization - content-hash the IR and
      short-circuit recompile on an unchanged plan.

## Tasks (Cross-Cutting or Epic-Level)

- [ ] Task: Author the required patch docs before any implementation story opens
      (`patch_framework_gating.md` entry gate - this epic is system-impacting).
- [ ] Task: Capture a gauntlet baseline before the first port lands, so parity
      is measured rather than assumed.
- [ ] Task: Update `src_architecture.md` and `src_components.md` with the IR
      boundary; regenerate both `*_index.md` in the same pass.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories.

## Acceptance Criteria (Epic Done)

- A test walks every phase 1-10 artifact and FAILS on any non-value field.
- Round-trip test: IR serialized, deserialized, hydrated, and the resolved object
  graph is behaviorally identical to a non-round-tripped conjure.
- A test asserts no IR symbol type is reachable from the meld call path.
- Full existing test suite green on 3.14t, owner-run.
- Gauntlet parity: `test_melder_gauntlet.py` per-scope-cycle summary within run
  noise of the pre-port baseline. A regression here means IR reached the hot path.
- Recompiling an unchanged Spellbook is an IR-hash hit with no phase execution.
- Both canonical system docs updated and their indexes regenerated.

## Risks / Mitigations

- **RISK: IR leaks into the runtime lane.** Highest-severity failure mode; turns
  a maintainability win into a throughput regression.
  MITIGATION: the reachability test plus the gauntlet parity gate. Both are
  acceptance criteria, not follow-ups.
- **RISK: a phase needs object identity, not just a name.** Would force an
  identity concept into the IR mid-port.
  MITIGATION: STORY-1 surfaces it before any port begins; it is an explicit
  ratification item in STORY-2.
- **RISK: big-bang refactor of the most load-bearing code in the system.**
  MITIGATION: port in tranches (1-4, 5-7, 8-10), each keeping the existing suite
  green; `refactor_limits.md` scope discipline per story.
- **RISK: conjure gets slower because the IR is rebuilt where it should be
  cached.** MITIGATION: the memoization story, and conjure timing in the epic's
  success metrics.
- **RISK: the epic is justified on the wrong grounds.** It will be tempting to
  sell this as a performance fix. It is not one - see Non-Goals.

## Applicable Anti-Patterns

- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.
- [ ] No design decision taken from `src_architecture.md` alone - documents are
      evidence of intent, source is evidence of behavior.
- [ ] No implementation before the patch-framework entry gate is satisfied.

## Validation / Test Approach

- Value-only assertion walk over all phase 1-10 artifacts.
- IR round-trip behavioral equivalence test.
- Meld-path symbol reachability test (must fail loudly if violated).
- Existing spell_compiler unit/component suites, per tranche.
- Gauntlet regression gate:
  `python benchmarks/testing_other_di/test_melder_gauntlet.py`, baseline
  captured before the first port. Compare per-scope-cycle create/cleanup/total.
- All runs are OWNER-RUN. Agents report `"Not run."` until the owner reports
  output (`evidence_reporting.md`).

## Rollout / Adoption Plan

- Internal only; no public API surface changes, so no consumer migration.
- Land tranche by tranche behind a green suite; no flag, no dual path - a
  parallel legacy pipeline would double the surface and rot.
- Downstream tickets (crystallizer plan persistence, MR plan-grain diff) open
  only after Milestone 4.

## Open Questions

- Does the IR carry validation RESULTS, or only the structure that validation
  consumes? Results in the IR make the plan self-describing; they also make it
  stale-able independently of the structure.
- Version the IR under the existing `RecordVersion "1.0.0"` stamp, or a separate
  IR version line? Sharing the stamp couples plan format to record format.
- Is phase 11's existing codegen cache keyed on something that an IR hash could
  replace outright, or do they answer different questions?
  (`codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py`)
- Does `dynamic=True` change what the IR must carry, given link/sever/transfer
  mutate structure after conjure?

## Decision Log

- 2026-08-03 (owner): phases **1-10** move to the IR entirely; **phase 11
  computes the rest**. The hydration boundary is phase 11, not a phase-by-phase
  mix.
- 2026-08-03 (owner): the epic is placed on the board **unclaimed**.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - <patch docs to be authored under system_docs/patches/active/ at story start>
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: durable deltas merged into `src_architecture.md` and
  `src_components.md` at epic closure; patch lane removed per
  `patch_framework_gating.md` closure gate.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - UNKNOWN
- IF_UNKNOWN: none

## Notes

- DATETIME: 2026-08-03T01:45:00Z
  TYPE: DECISION
  CLAIM: Owner ruled the IR boundary at phases 1-10, with phase 11 as the sole
    hydration and codegen step. Epic authored and boarded unclaimed.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_1.py
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py
  IMPACT: Fixes the scope boundary before design starts, so the IR schema is
    built for ten consumers rather than being negotiated per phase.
  NEXT: Claim the epic and open STORY-2026-08-03-phase-pipeline-survey.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-03T01:45:00Z
  TYPE: UNKNOWN
  CLAIM: Everything this epic states about what phases 1-11 currently DO is
    drawn from `src_architecture.md` and the module layout on disk. No phase
    implementation has been read. Under the Unknowns Gate a document is evidence
    of intent and only source is evidence of behavior, so the current-state
    description is UNKNOWN, not FACT.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:628-640
  - context_compass/agent_onboarding/default/general/skills/unknowns_gate_reference.md:38-41
  IMPACT: A schema designed from the architecture doc would encode intent rather
    than behavior, and the mismatch would surface mid-port when it is expensive.
  NEXT: STORY-1 reads `compiler_phase_1.py` through `compiler_phase_11.py` and
    promotes this to FACT with file:line evidence per phase.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-03T01:45:00Z
  TYPE: RISK
  CLAIM: The tempting justification for this epic is performance, and that
    justification is false. Measured on the gauntlet, CPython 3.15.0b2t against
    3.14.0t moved this workload +0.22% - noise - which rules out interpreter
    dispatch as the constraint and points the residual at object allocation and
    refcounting. An IR changes neither.
  EVIDENCE:
  - benchmarks/testing_other_di/test_melder_gauntlet.py:316-325
  IMPACT: An epic sold on a speedup it cannot deliver gets judged against the
    wrong acceptance criteria and reads as a failure when it succeeds.
  NEXT: Keep the Non-Goals section intact through every status transition.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

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

Authored 2026-08-03 by `super_tester_0` on owner direction and left UNCLAIMED.
No agent owns it; no implementation has begun; nothing under `src/` was touched.

The idea came out of a benchmarking session, not a defect. Conjure is a compiler
and phase 11 already emits a compiled executor, which is why the 3.15 JIT gave
this workload +0.22%: the interpreter overhead was already removed at comptime.
What the compiler lacks is an IR, so its plan is object graph rather than
artifact - invisible to the crystallizer, undiffable by MutationResearch, and
recomputed from scratch on every restore.

Entry point is STORY-1, the phase survey, and it gates everything else for a
reason: this document describes what the phases are INTENDED to do, taken from
the architecture doc and the file layout. Nobody has read the phase source. Do
not design the schema until that is closed.

The two things most likely to go wrong: an IR symbol reaching the meld hot path
(there is an acceptance test for it, and a gauntlet baseline to catch it), and
this being pitched as a performance win when it is a durability and mutability
win.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
