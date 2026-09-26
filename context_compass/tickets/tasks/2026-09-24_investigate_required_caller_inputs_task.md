# Task: Investigate required caller-supplied constructor inputs

## Metadata
- Task ID: TASK-2026-09-24-investigate-required-caller-inputs
- Story: none; standalone investigation
- Status: review
- Owner: codex
- Agent Name: workflows_0
- Priority: p1
- Created: 2026-09-24T11:36:32Z
- Updated: 2026-09-24T11:53:24Z

## Objective
Explain why bootstrap validation rejects constructors requiring caller-provided Package/Conduit
objects, establish existing native capabilities, and recommend a bounded supported remedy.

## Problem / Context
The owner forwards command_0's report: Task.work_callable: Package, StackContext.entry and
CommandCenter.conduit are supplied through meld overrides, but conjure rejects the missing inferred
providers first. The desired contract accepts a definition with explicitly required caller inputs
and rejects construction if those inputs are absent. The inherited-cleanup correction is complete.

## Ticket Contract
- ENTRY_GATE: Existing role onboarding/certification remains valid; check-in and active route restored.
- EXECUTION_BOUNDARY: Required parameter classification, validation/compiler representation and
  runtime override admission; relevant CommandOps classes/tests and prior caller-socket contracts.
- DEPENDENCIES: command_0's exact consumer evidence and existing OVERRIDE_REQUIRED capabilities.
- EXIT_GATE: Source-backed diagnosis, local reproduction, existing-API assessment and a concrete
  correction/design recommendation with scope and remaining decisions.
- FAILURE_ESCALATION: Keep missing evidence explicit. Do not bind kernel objects, invent dummy
  providers, weaken required annotations/defaults or skip tests to conceal a missing capability.

## Scope Boundaries
- In scope: explicit required runtime inputs, missing-provider validation and missing-override failure.
- Out of scope: production changes, public API implementation, inherited-cleanup changes, release work,
  broad override graph pruning and the separate CommandCenter registration defect.
- Other agents are investigating effective-graph override semantics; this task addresses declaration
  of required supplied inputs before the graph can validate, and will preserve their active work.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Consumer failures, existing native capability and epic/history boundaries are
  verified; a bounded parameter-declaration recommendation is recorded without production edits.

## Steps / Checklist
- [x] Obtain exact consumer failures and declaration attempts from command_0.
- [x] Read prior required-input contracts and trace current classification through validation.
- [x] Reproduce bootstrap refusal and prove current required-override behavior at runtime.
- [x] Identify whether a supported API already expresses the required contract.
- [x] Deliver the smallest compatible remedy with evidence and unresolved decisions.

## Deliverables / Acceptance
- Pinpoint the phase that refuses each reported input and its source-level reason.
- Distinguish ordinary non-resolvable application definitions from guarded Melder kernel types.
- Explain how a declaration should reach existing runtime override execution without constructing
  caller-owned objects or changing their ownership.
- Evidence and recommendation are recorded in this task; production source stays unchanged.

## Validation
- Verified local Melder 0.2.52 with the application interpreter: 5 failures and 1 passing identity
  control, matching the original consumer report. This investigation does not fix those failures.
- Existing native controls: 32 runtime cases and 6 compiler cases pass; 36 compiler cases deselected.
- Phase-1-only inspection records all three real constructor input shapes without domain construction.
- Historical blame, commands and receipts are retained with findings.md in the linked artifact directory.

## Risks / Rollback Notes
- Constructor injection and overrides share compilation metadata; identify gates before proposing changes.
- Do not conflate required input authoring with the other agents' effective-DAG optimization work.
- Investigation writes are limited to this ticket, its route, peer messages and supporting artifacts.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/required_caller_inputs_20260924/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: retain source-backed diagnosis and reproducible evidence on accepted turn-in.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: required caller-input declaration, native type guard and validation timing
- IF_UNKNOWN: none

## Noting Behavior
- Record a coherent trace before the next investigation/validation tranche.
- Use PowerShell Start-Sleep -Seconds 30 between peer-message checks, as directed by the owner.

## Notes
- DATETIME: 2026-09-24T11:36:32Z
  TYPE: PLAN
  CLAIM: Open the owner's required-input investigation. CommandOps' existing task already distinguishes
    non-resolvable application parent definitions from Package/Conduit, which native admission blocks.
    Read the prior caller-socket contract and current source before concluding the capability is absent.
  EVIDENCE:
  - ../priv_commandops/context_compass/tickets/tasks/2026-09-24_reported_area_and_center_failures_task.md:73-88
  - context_compass/system_docs/src_components_index.md:76-84
  IMPACT: The likely gap is input declaration for guarded types; the exact mechanism remains unverified.
  NEXT: Read the existing required-input contract and the parameter-classification component slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-24T11:40:31Z
  TYPE: FACT
  CLAIM: The September 19 non-resolvable-registration epic introduced OVERRIDE_REQUIRED for known
    registered reference targets and retained ordinary Python missing-argument errors. Current Phase 1
    still infers SINGLE_BY_ANNOTATION for required custom types. Phase 3 raises on zero matches;
    OVERRIDE_REQUIRED is assigned only after a nonempty reference-ID set has been selected.
  EVIDENCE:
  - context_compass/tickets/epics/completed/2026-09-19_discoverable_non_resolvable_registrations_epic.md:20-45
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:1100-1226
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:435-513
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:693-768
  IMPACT: The internal input category exists, but its current producer depends on a registration.
    User also requests checking recent conjure/schema epics; investigate history before attributing
    the refusal to a recent strictness change.
  NEXT: Trace the zero-provider branch history and inspect the closest conjure/creation-schema epics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T11:41:11Z
  TYPE: FACT
  CLAIM: Git blame attributes the unchanged zero-candidate RuntimeError to May 20 (b9ec49dee7),
    while September 19 (63ef620e36) adds resolvable-provider preference and the reference-only path.
    RequiredHolesStrategy already emits warnings for PLAIN required inputs and OVERRIDE_REQUIRED.
    command_0 supplied current-source evidence: five bootstrap/late-bind failures and one passing
    actual Package identity control. No Package binding occurs in the failing paths.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:486-513
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/required_holes_strategy.py:64-133
  - ../priv_commandops/context_compass/artifacts/2026-09-24_reported_area_and_center_failures/native_required_inputs_handoff.md:1-162
  IMPACT: The immediate blocker is Phase-3 provider inference, not BindGuard executing at failure
    and not a newly added runtime missing-argument validator. Record package provenance afresh: the
    peer reports source version 0.2.52 after unrelated concurrent release work.
  NEXT: Read the exact consumer proof and reproduce current native caller-input contrasts locally.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T11:44:18Z
  TYPE: FACT
  CLAIM: Recent epic comparison separates three changes. September 19 adds a registered-definition
    input route; September 23 advances persisted creation-cache admission to schema 9 and explicitly
    preserves resolution semantics; August 3's whole-pipeline value-only IR epic is still ready and
    unassigned. The CommandOps minimal fixture disables disk caching, so its current refusal does
    not depend on the cache-schema change. Existing native tests cover supplied identity and ordinary
    missing-argument failure across all executor families after a False definition is registered.
  EVIDENCE:
  - context_compass/tickets/epics/completed/2026-09-19_discoverable_non_resolvable_registrations_epic.md:20-45
  - context_compass/tickets/epics/completed/2026-09-23_invalidate_creation_cache_on_melder_version_change_epic.md:37-71
  - context_compass/tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md:3-11
  - ../priv_commandops/tests/component/spectrum/test_manual_package_overrides.py:61-138
  - tests/component/melder/aether/conduit/test_conduit_component_non_resolvable_overrides.py:96-187
  IMPACT: Do not describe this as a newly introduced strict creation schema without contrary evidence.
    The actionable gap is a typed parameter-level supplied-input declaration that needs no target bind.
  NEXT: Run the original six consumer cases and existing native supplied-input controls.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T11:45:19Z
  TYPE: MEASURE
  CLAIM: Independent execution against verified local Melder 0.2.52 reproduces 5 failures and 1 pass
    in 2.87 seconds: Task initial/late registration and three area roots stop at Phase 3; the plain
    receiver retains the actual unregistered Package identity. Existing required-input runtime tests
    pass all 32 cases, and six compiler selection controls pass (36 deselected). Caching is disabled
    in the application proof and native runtime fixture.
  EVIDENCE:
  - context_compass/artifacts/required_caller_inputs_20260924/application.log:1-152
  - context_compass/artifacts/required_caller_inputs_20260924/native_runtime.log:1-2
  - context_compass/artifacts/required_caller_inputs_20260924/native_compiler.log:1-2
  IMPACT: Existing executor support and missing-input failure are operational after input policy is
    established. The missing authoring path must produce that policy without requiring a target bind.
  NEXT: Verify the consumer constructor boundaries and write the minimum explicit declaration design.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T11:49:47Z
  TYPE: FACT
  CLAIM: A later cold-build conjure gate does exist: _enforce_conduit_resolution_valid rejects
    ERROR-severity resolution verdicts. Its call site traces to June 28 (b823784f48). The current
    conjure implementation runs structural phases before cache classification and this later gate;
    all reported refusals occur in structural Phase 3. Phase-1-only inspection also reveals typed
    required StackContext.home (greenlet) and CommandCenter.spectrum (Spectrum), in addition to the
    first failing parameters. No domain constructor or greenlet was executed for that inspection.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:203-317
  - src/melder/aether/spellbook/spellbook_creation_system.py:349-409
  - context_compass/artifacts/required_caller_inputs_20260924/conjure_gate_history.log:1-9
  - context_compass/artifacts/required_caller_inputs_20260924/phase1_inputs.json:1-145
  IMPACT: Disabling the later conjure gate cannot reach the desired override path. A reusable input
    declaration must cover all caller-provided parameters, not special-case Package or Conduit only.
  NEXT: Record a parameter-scoped declaration recommendation and return it to command_0.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T11:53:24Z
  TYPE: DECISION
  CLAIM: Recommend a native per-binding declaration of required caller-input parameter names,
    producing OVERRIDE_REQUIRED without a registered reference target. Preserve truthful annotations,
    ordinary DI failures on undeclared parameters, existing Python missing-argument errors and
    supplied-object identity. Include binding identity/descriptions/replay and cache semantics in any
    implementation. Exact public naming is a future design decision, not an existing API claim.
  EVIDENCE:
  - context_compass/artifacts/required_caller_inputs_20260924/findings.md:99-135
  - context_compass/artifacts/required_caller_inputs_20260924/native_runtime.log:1-2
  - context_compass/artifacts/required_caller_inputs_20260924/native_compiler.log:1-2
  IMPACT: This extends the existing input category at its authoring/producer boundary. It does not
    require relaxing the kernel guard, changing constructors, disabling validation or adding preflight.
  NEXT: Owner selects the declaration design and implementation scope; coordinate shared compiler
    boundaries with the active override-graph lane before any production edit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T11:53:24Z
  TYPE: FACT
  CLAIM: command_0 acknowledged the findings and confirmed StackContext.home and CommandCenter.spectrum
    are exact caller-supplied identities; the prior question and alert were consumed after durable
    receipt. Its separate SpectrumContextConfig work does not overlap this native investigation.
  EVIDENCE:
  - ../priv_commandops/src/command_ops/command_center/agents/utilities/stack_context.py:77-115
  - ../priv_commandops/context_compass/tickets/tasks/2026-09-24_reported_area_and_center_failures_task.md
  IMPACT: The declaration must cover more than the three first failures and preserve application
    ownership/thread-affinity rules. No source workaround or implementation was selected.
  NEXT: Present the epic-history conclusion and recommended authoring boundary to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Investigation is complete and in review. Current source 0.2.52 reproduces five pre-meld failures
with a real passing Package identity control; 38 existing native input-policy controls pass.
The no-provider refusal predates the recent epics (present by May 20). The separate June 28 conjure
resolution gate occurs later, and schema 9 is cache compatibility. September 19 added
OVERRIDE_REQUIRED only for selected registered False definitions. Recommended next work is explicit
parameter-scoped caller-input authoring without a reference registration. Findings and commands:
artifacts/required_caller_inputs_20260924/findings.md. command_0 confirms additional caller-input
sites StackContext.home and CommandCenter.spectrum. No production/application source was changed.
