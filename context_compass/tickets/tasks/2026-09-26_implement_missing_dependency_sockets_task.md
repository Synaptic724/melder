

# Task: Compile unprovided constructor dependencies as missing-dependency sockets instead of refusing conjure

## Metadata
- Task ID: TASK-2026-09-26-implement-missing-dependency-sockets
- Epic: EPIC-2026-09-24-override-execution-performance
- Story: none (step S1 of artifacts/melder_override_design_20260926/design.md)
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-26T00:44:21Z
- Updated: 2026-09-26T00:52:30Z

## Objective
A typed constructor parameter with no registered provider no longer fails conjure. It compiles as a
caller-supplied input; a meld that supplies it by override uses the supplied object; a meld that does not
raises a named MeldExecutionError that identifies the missing dependency and how to supply it.

## Ticket Contract
- ENTRY_GATE: Owner direction 2026-09-26 ("go ahead lets start looking into this") after agreeing the
  contract: no early rejection, named error at meld when not supplied. Cause trace in review.
- EXECUTION_BOUNDARY: Investigation now: read src/, tests/. Implementation only after patch docs exist and
  the owner confirms the file/symbol list. Writes now: this ticket, its patch lane and artifacts.
- DEPENDENCIES: tickets/tasks/2026-09-26_trace_caller_input_conjure_strictness_regression_task.md;
  completed 2026-09-19 caller-supplied socket contract (OVERRIDE_REQUIRED).
- EXIT_GATE: Behavior implemented with regression tests on 3.14t and GIL, docs promoted, owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST for multiple-candidate policy, late-provider recompile policy and
  error wording; BLOCKER if a consumer assumes OVERRIDE_REQUIRED always carries references.

## Scope Boundaries
- In scope: Phase-3 single-annotation resolution and socket classification, Phase-4/6 validation of the new
  socket, Phase-5/9 consumers of OVERRIDE_REQUIRED, the meld-time missing-input error on every executor
  family and the no-override lane, Nexus publication of reference-less sockets.
- Out of scope: the override build-order rewrite (S2-S5), multi-candidate ambiguity (stays an error),
  the internal-registration guard, a per-binding declaration keyword.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner approved starting the investigation, 2026-09-26T00:44:21Z.

## Steps / Checklist
- [x] Trace Phase 3: where the zero-candidate raise sits and how socket kinds are assigned.
- [x] Trace every OVERRIDE_REQUIRED consumer for assumptions about non-empty references.
- [x] Trace how a missing required input fails today in each executor family and the no-override lane.
- [x] Late-provider behavior: existing OVERRIDE_REQUIRED frame-key watcher recompiles the consumer.
- [ ] Write patch docs and the file/symbol list; owner confirmation before any src/ edit.
- [ ] Implement, test, promote docs.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Patch lane system_docs/patches/active/missing_dependency_sockets_2026_09_26/ (after investigation).
- Source and tests (after confirmation).

## Files / Paths Impacted
- UNKNOWN until the trace completes; recorded before implementation.

## Validation
- Not run.

## Risks / Rollback Notes
- Conjure-time detection of a forgotten binding moves to meld time; mitigate with a conjure warning.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No src/ edit before patch docs and owner confirmation.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/missing_dependency_sockets_20260926/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Owner decision at task closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Missing-dependency sockets; meld-time missing-input error.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T00:44:21Z
  TYPE: PLAN
  CLAIM: Reuse the existing caller-supplied socket (OVERRIDE_REQUIRED) for a parameter with zero candidates
    instead of raising, so Phase 5/9 and the executors already treat it as a supplied input. Verify every
    consumer tolerates empty references, then add a named missing-input error where today a Python
    missing-argument error (or a descriptor default) surfaces.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:486-497
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:733-747
  IMPACT: Keeps the change inside an existing category; no new socket kind unless a consumer forces one.
  NEXT: Read the Phase-3 loop that calls _resolve_single_by_annotation and builds socket targets/references.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T00:46:10Z
  TYPE: FACT
  CLAIM: Phase 3 raises only in _resolve_single_by_annotation; the loop already skips empty results, collections
    may be empty, and _build_local_topology marks OVERRIDE_REQUIRED only when references exist. Consumers of
    OVERRIDE_REQUIRED: injection keeps it as an "override_required" source (no edge); the frame-key watcher
    already watches OVERRIDE_REQUIRED sockets with a dependency_key, so a provider bound later invalidates and
    recompiles the consumer; cycle validation excludes it; Nexus publishes one relation per reference (none if
    empty). One consumer rejects empty references: SpellInjectionInstanceSpec._build_required_override_params.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:435-513
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:693-768
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:770-926
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:216-278
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_injection_analysis.py:125-150
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1362-1390
  - src/melder/nexus/frame_descriptor_manager.py:600-617
  IMPACT: Reusing OVERRIDE_REQUIRED needs two compiler edits (Phase 3 marking, the reference check); late
    provider binding already works through the existing watcher. Serialization sites still to read.
  NEXT: Record today's missing-input failure per family (probe), then read the constructor-call error paths.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T00:46:10Z
  TYPE: MEASURE
  CLAIM: With today's resolvable=False route (3.14.7t, many consumers): supplied root and nested inputs work by
    exact path and by broadcast; a missing root input on a dependency-free root raises a raw TypeError
    ("missing 1 required positional argument: 'work'"); on a root with dependencies, or nested, it raises
    MeldExecutionError "Error invoking spell 'X'" chained from that TypeError. Nothing names the missing
    dependency or how to supply it.
  EVIDENCE:
  - artifacts/missing_dependency_sockets_20260926/probe_required_today.py:1-75
  - artifacts/missing_dependency_sockets_20260926/probe_required_today_314t.json
  IMPACT: Execution already honors supplied inputs; S1 needs the named error on the failure path only.
  NEXT: Read each family's constructor-call exception path to place a failure-path-only missing-input check.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T00:48:04Z
  TYPE: PLAN
  CLAIM: Proposed change set for owner confirmation. (1) Phase 3: zero candidates for SINGLE_BY_ANNOTATION
    returns empty and the socket becomes OVERRIDE_REQUIRED with no references (ambiguity still raises).
    (2) Injection: accept reference-less required inputs. (3) Required-holes warning names a missing provider.
    (4) One failure-path helper raises MeldExecutionError naming the missing parameters, its type and the
    override key; every family's existing constructor except-branch calls it (generalized, many_only, manifest
    no-override/override); solo no-override emits it at compile time; solo override adds try/except TypeError
    only for spells with required inputs. Success paths gain no work. (5) Cache generation 11. (6) Update the
    7 existing "no DI candidate" assertions and add regressions per family, nested, reuse and late provider.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:1650-1735
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:603-617
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:40-190
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/required_holes_strategy.py:110-135
  IMPACT: Small compiler change plus one error helper wired into existing except-branches.
  NEXT: Owner confirms; then write patch docs under system_docs/patches/active/missing_dependency_sockets_2026_09_26/.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T00:52:30Z
  TYPE: TRADEOFF
  CLAIM: Maintainer assessment for the owner. The model (a constructor parameter is either a graph edge or an
    open input the call supplies) is durable and is the same concept the S2-S5 shape plan uses for cuts and
    operands. Two parts of the proposed change set are not durable as written: encoding "no provider" as
    OVERRIDE_REQUIRED with an empty reference tuple (meaning inferred from emptiness), and naming the error from
    ~20 per-family except-branches that S4 replaces. Refinement: an explicit input-origin field on the socket
    (registered non-resolvable definition vs no registered provider) and the error decided by plan data, with
    the except-branch helper recorded as interim until S4.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:733-747
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_injection_analysis.py:125-150
  - artifacts/melder_override_design_20260926/design.md:120-133
  IMPACT: Keeps S1 small without leaving an implicit encoding behind.
  NEXT: Owner decides whether S1 ships with the interim error wiring or waits for plan-level errors.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Investigation complete; change set proposed (PLAN note) and awaiting owner confirmation before patch docs
and any src/ edit. Resume from the latest Notes NEXT.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
