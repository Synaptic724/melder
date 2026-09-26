

# Task: Trace the change that made conjure reject caller-supplied constructor inputs

## Metadata
- Task ID: TASK-2026-09-26-trace-caller-input-conjure-strictness-regression
- Epic: EPIC-2026-09-24-override-execution-performance
- Story: none
- Status: review
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-26T00:25:27Z
- Updated: 2026-09-26T00:42:21Z

## Objective
Find the commit(s) that turned a missing provider for a caller-supplied parameter (Task.work_callable:
Package) from an override-satisfiable input into a conjure failure, prove before/after behavior by
running both versions, and state what reverting the strictness would change.

## Ticket Contract
- ENTRY_GATE: Owner direction 2026-09-26: "in August we added restrictions ... the fault here is we're
  being too strict"; look up the epics and changes.
- EXECUTION_BOUNDARY: Read git history, tickets, src/ and tests/; run old and current source from
  read-only extracts in the VM. Write only this ticket and artifacts/melder_caller_input_regression_20260926/.
- DEPENDENCIES: workflows_0 findings (artifacts/required_caller_inputs_20260924/findings.md).
- EXIT_GATE: The responsible change identified with before/after runs; fix options stated; review.
- FAILURE_ESCALATION: CONFLICT where history contradicts workflows_0's May-20 attribution.

## Scope Boundaries
- In scope: Phase 1/3 classification, phase error handling at conjure, conjure gates, related epics.
- Out of scope: Production edits until the owner picks the fix.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner redirected caller inputs from "declare" to "regression: too strict", 2026-09-26T00:25:27Z.

- from_state: in_progress
- to_state: review
- transition_reason: Cause and timeline established across Melder and CommandOps, 2026-09-26T00:42:21Z.

## Steps / Checklist
- [x] Find where Phase-3 errors abort conjure and when that started (runs on dated extracts).
- [x] Run the caller-input probe on an old release and on current source.
- [x] Bisect by date: Phase-3 strictness predates 06-15; the guard change lands between 07-15 and 08-01.
- [x] Record fix options: missing-dependency socket agreed in owner discussion (ALIGNMENT_CHECK).
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Notes with commit ids, before/after runs and fix options.

## Files / Paths Impacted
- None in src/ or tests/.

## Validation
- Not run.

## Risks / Rollback Notes
- Old extracts run in the VM only; the repository and its .git are read, never written.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

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
  - artifacts/melder_caller_input_regression_20260926/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Owner decision at task closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Conjure strictness for parameters satisfied only by meld overrides.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T00:25:27Z
  TYPE: HYPOTHESIS
  CLAIM: Owner states conjure used to tolerate a missing provider for an override-supplied parameter and
    an August change made it fatal. workflows_0 dated the Phase-3 raise itself to May 20, which does not
    exclude a later change in whether that raise aborts conjure (phase error handling or a gate).
  EVIDENCE: artifacts/required_caller_inputs_20260924/findings.md:37-49
  IMPACT: Decides whether the fix is removing strictness (owner's view) or adding a declaration.
  NEXT: Locate the "Resolution pipeline aborted" path and its history, then run an old release.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T00:28:02Z
  TYPE: MEASURE
  CLAIM: Ran one portable probe (Task(work: LocalPackage), Package unbound, meld with override) on source
    extracts from 2026-06-15, 07-01, 07-15, 08-01, 08-15, release 0.2.3 and current, all on 3.14.7t. Every
    version fails conjure in Phase 3 with "no DI candidate". Binding Melder's own Package class succeeds on
    06-15..07-15 (conjure then fails because Package itself is a broken spell) and is refused from 08-01 by
    the internal-registration guard. The guard's July change is what made Package impossible to register.
  EVIDENCE:
  - artifacts/melder_caller_input_regression_20260926/bisect_results_314t.txt:1-19
  - artifacts/melder_caller_input_regression_20260926/probe.py:1-40
  - artifacts/melder_caller_input_regression_20260926/probe2.py:1-60
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:435-513
  IMPACT: The Phase-3 rejection of an unbound parameter is old; the July guard closed the registration route.
    How CommandOps satisfied the parameter before the guard is UNKNOWN (its repo is not mounted here).
  NEXT: Owner discussion: compile an unprovided parameter as a missing-dependency socket and raise a named
    error at meld only when it is neither provided nor supplied (owner's stated contract, 2026-09-26).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T00:28:02Z
  TYPE: ALIGNMENT_CHECK
  CLAIM: Owner contract (2026-09-26): do not reject early because a dependency is unregistered; let overrides
    supply it; if the caller does not, raise an error naming the missing dependency. Overrides must also stop
    building supplied objects (the 20% throughput gap). Both map onto design.md: an unprovided socket plus the
    per-shape plan that either binds an operand or lowers a named error into that object's build branch.
  EVIDENCE: artifacts/melder_override_design_20260926/design.md:120-133
  IMPACT: D1 resolves to no declaration: any unresolvable parameter becomes a missing-dependency socket.
  NEXT: Confirm with the owner which failures stay at conjure (ambiguous providers, cycles) before S1 scope.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T00:37:39Z
  TYPE: FACT
  CLAIM: The internal-registration guard is blanket: the builder AST-scans every .py under melder (skipping
    __pycache__, __melder_cache__, _build_assets) and records every class as (module, qualname). bind refuses
    an exact match for a class or an instance's type; subclasses are not covered. The exclusion seam is
    BindGuardBuildPolicy.EXCLUDED and is empty by owner ruling. The committed manifest holds 631 entries
    (stamped 0.2.51), 64 under melder.utilities, including helpers.package.Package; src_architecture still
    says 582 (stale).
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:33-111
  - src/melder/_build_assets/_bind_guard/_builder.py:40-90
  - src/melder/_build_assets/_bind_guard/_builder.py:169-251
  - src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py:17-19
  IMPACT: Package stays unbindable by design; the missing-dependency socket is the route for Package inputs.
  NEXT: Owner decides whether any class should move to EXCLUDED; no change is required for Package.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T00:39:00Z
  TYPE: FACT
  CLAIM: Of the 64 guarded utilities, the package root exports 13 classes: ProtocolCrafter, ULID_Factory,
    Cleanable, Package (Pack is an alias) and nine exceptions (DeadReferenceError, HookExecutionError,
    InternalRegistrationError, MeldExecutionError, PhaseExecutionError, PhaseSchedulerError,
    PhaseTimeoutError, SpellSpaceScopeError, SpellbookValidationError); new_ulid is a function, outside the
    guard. Every other guarded utility is internal-only. melder/utilities has no __init__.py re-exports.
  EVIDENCE:
  - src/melder/__init__.py:136-160
  - src/melder/__init__.py:200-269
  - src/melder/utilities/helpers/package.py:997-997
  IMPACT: Exported-and-guarded is intentional (the guard restricts registration, not use); a user-facing
    parameter typed with an exported class (Package, Cleanable) is the case the missing-dependency socket covers.
  NEXT: Owner decides whether any exported class should be registrable (EXCLUDED); default is none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T00:41:16Z
  TYPE: MEASURE
  CLAIM: No Melder version tested satisfies a Package-typed parameter at conjure. Registering a Package
    INSTANCE as an existing object fails bind on 2026-07-15 (TypeError "sequence item 11: expected str
    instance, function found") and is refused by the guard from 08-01; registering the class passes bind
    but breaks conjure at Phase 4. On 07-15 neither Package nor Cleanable carries the old sentinel. So the
    guard closed a route that was already broken; Phase 3 rejects the unregistered case in every version.
  EVIDENCE:
  - artifacts/melder_caller_input_regression_20260926/probe3.py:1-45
  - artifacts/melder_caller_input_regression_20260926/probe3_results_314t.txt:1-6
  - artifacts/melder_caller_input_regression_20260926/bisect_results_314t.txt:1-19
  IMPACT: The Melder side shows no version where this worked. How CommandOps previously built Task (annotation,
    default or construction path) is UNKNOWN and lives in the priv_commandops history.
  NEXT: With owner approval, read priv_commandops git history for Task.work_callable and its construction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T00:42:21Z
  TYPE: FACT
  CLAIM: priv_commandops history (read-only, owner-granted) gives the timeline. Task.work_callable has been
    typed Pack since 2025-08-19. On 2026-08-08 CommandOps replaced its own Package/Cleanable shims with direct
    melder imports (task.py now `from melder import Package as Pack`), so the annotation became Melder's
    guarded Package. The area bootstraps that bind Task/Job/etc. into a Melder Spellbook were added 2026-09-13
    and expanded 09-19; before that Melder never compiled Task. Conjure then applies Phase 3's long-standing
    "registered provider required" rule to a type the guard (blanket since 2026-07-24/25) forbids registering.
  EVIDENCE:
  - ../priv_commandops/src/command_ops/command_center/agent_pools/task/task.py:12-12
  - ../priv_commandops/src/command_ops/command_center/agent_pools/task/task.py:79-86
  - ../priv_commandops/src/command_ops/command_center/spectrum/bootstraps/agent_pools_bootstrap.py:46-76
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:486-497
  IMPACT: Root cause is Phase 3 requiring a registered provider for every typed parameter. The August import
    switch plus the guard removed any way to satisfy that rule for Package; neither is itself the defect.
  NEXT: Owner review; the fix is the missing-dependency socket (lenient conjure, named error at meld).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Phase-3 no-candidate failure predates 2026-06-15; the internal-registration guard (07-15..08-01) blocked
registering Package. Owner's target contract is recorded (ALIGNMENT_CHECK). Resume from the latest NEXT.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
