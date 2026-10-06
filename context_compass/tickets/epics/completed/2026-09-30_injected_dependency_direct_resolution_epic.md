# Epic: Make an injected dependency directly resolvable from the same Melder scope

## Metadata
- Epic ID: EPIC-2026-09-30-injected_dependency_direct_resolution
- Status: done
- Owner: user; Melder lead melder_0 (owner-assigned in chat, 2026-09-30)
- Agent Name: melder_0 (Melder lead), command_0 (report author, working in MelderOps)
- Priority: p1
- Created: 2026-09-30T15:45:47Z
- Updated: 2026-09-30T21:18:29Z
- Completed: 2026-09-30T21:18:29Z
- Summary: A dependency bound after conjure and first built by a consumer melds directly afterwards and returns
  its scope's instance: Melder 0.2.8215 (option B) flags it at the consumer's target pass and runs its own full
  pass on its first direct meld, with no caller step. The unchanged diagnostic passes on the installed wheel in
  a MelderOps host (red on 0.2.8212); the wheel is in priv_commandops/.venv314.
- Target Window: next owner-selected Melder correctness iteration
- Origin: priv_commandops / MelderOps native Toolbox migration
- Tested distribution: Melder 0.2.8212, installed in MelderOps .venv314
- Evidence directory: artifacts/2026-09-30_injected_dependency_direct_resolution/
- Implementation status: repaired in Melder 0.2.8215 (work package C); the handoff itself claimed none

## Problem / Opportunity

In an existing dynamic Melder root, register a service with `unique_per_conduit` existence and a
consumer with a required annotation for that service. Create a lesser conduit and meld the consumer.
The consumer is returned with a valid service instance. A subsequent direct meld of the service
from that same lesser conduit fails before returning a value:

```text
RuntimeError: Cannot build CreationContext before spell_codegen_creation exists.
Run analyzer -> processor -> planner -> codegen creation first.
```

The smallest executed diagnostic reached both of these observations in order:

```python
consumer = scope.meld(spellframe="native_probe", binding_name="NativeConsumer")
assert consumer.service.value == 7  # passed
assert scope.meld(
    spellframe="native_probe", binding_name="NativeService",
) is consumer.service              # meld raised before the identity assertion
```

This is a failed direct-resolution operation after successful dependency injection. It is not an
observed failure to construct the consumer, an absent service attribute, a wrong returned instance,
or a failed equality comparison. The failing call produced no result to compare.

**Evidence boundary:** the diagnostic uses two ordinary classes and public native bind/meld APIs,
without calling Toolbox to register or construct either class. It still obtains its root from a
Spectrum fixture. A completely standalone Melder fixture has not yet been run. Do not shorten that
qualification into a claim that the entire MelderOps host/environment was eliminated.

## MRP Alignment

Melder's object graph is used both to construct dependent objects and to address their registered
providers directly. These operations need compatible readiness and identity contracts. A provider
that was successfully used as a dependency must not require a consuming framework to repair compiler
state before ordinary public resolution. Fix the native contract where evidence places the cause;
preserve the existing lifetime policy rather than changing it to make the example pass.

## Ticket Contract
- ENTRY_GATE: owner requested this epic and evidence handoff. The receiving lead first reproduces
  the observed distribution behavior and distinguishes it from the current source checkout.
- EXECUTION_BOUNDARY: direct resolution following injected creation; native resolution readiness,
  generated creation payload/context publication, selected lifetime stores, and related regression tests.
- DEPENDENCIES: copied evidence, a supported free-threaded Python runtime, current Melder policy and
  test fixtures, and the owner's implementation assignment before source work starts.
- EXIT_GATE: the unchanged native-operation diagnostic passes; same-scope identity and sibling-scope
  isolation hold; the real downstream lookup is revalidated; source/test/docs/release obligations are met.
- FAILURE_ESCALATION: if the current checkout differs, classify that difference before editing. If
  standalone Melder passes, retain the host configuration as part of the reproduction and investigate it.

## Goals
- Explain why a direct provider request reaches CreationContext construction with no codegen payload.
- Establish whether the payload was never emitted, was invalidated, or was unavailable through the
  particular readiness/cache path. These are different causes and remain unproven today.
- Preserve `unique_per_conduit`: the direct service result must be the service already injected in
  that scope; separate scopes must retain separate service instances.
- Add a deterministic native regression that protects the actual failed lookup.
- Revalidate the installed-wheel consumer path after the owner delivers a corrected build.

## Non-Goals
- Rewriting Toolbox, Spectrum, Iris, agent pools, or their ownership rules in this Melder epic.
- Replacing native calls with Python constructors, manual instance registration, or private-cache edits.
- Binding a Conduit or rebuilding a caller's Package to satisfy resolution.
- Declaring all DI, all lifetimes, or every platform broken based on this one observation.
- Removing the CreationContextBuilder guard merely to suppress its exception.
- Reopening previous completed epics without proving that their cause applies here.
- Installing, publishing, committing, or pushing a Melder release on the strength of this drafting request.

## Scope Boundaries

The known failing body has one root, one child scope, two new class bindings, one successful consumer
meld and one failed service meld. There is no explicit link, contract import, purge, cleanup, notch,
structural refresh, or concurrent worker in that body between those two melds. The surrounding host
contains ordinary framework definitions and configuration; its influence has not been eliminated.

The final traceback comes from the installed Melder package in `.venv314/Lib/site-packages/melder`.
Current `melder_private/src/melder` has not been executed for this finding. Equal version labels alone
do not prove byte equivalence. The attached provenance records hashes of the inspected installed files.

## Exact Environment and Provenance

| Item | Captured value |
| --- | --- |
| Origin repository | `C:\Users\Mark\PycharmProjects\priv_commandops` |
| Interpreter | `.venv314\Scripts\python.exe` |
| Python | `3.14.7 free-threading build (main, Sep 1 2026, 14:18:33) [MSC v.1944 64 bit (AMD64)]` |
| Build free-threading flag | `Py_GIL_DISABLED = 1` |
| Runtime GIL | `sys._is_gil_enabled() == False` |
| Platform | `Windows-11-10.0.26200-SP0` |
| Melder distribution | `0.2.8212` |
| pytest | `9.0.3` |
| Imported Melder origin | `priv_commandops\.venv314\Lib\site-packages\melder\__init__.py` |
| Origin HEAD at provenance capture | `45c9ff67d2e6ffaea02f72c846da3c1acf6fe66d` |
| Worktree qualification | Uncommitted Spectrum/Toolbox migration changes were present; HEAD alone is insufficient. |
| Provenance capture | `2026-09-30T15:45:47.127401+00:00` |

`runtime_provenance.json` records the full values and SHA-256 hashes. The snapshot folder carries the
three relevant MelderOps runtime files, the Toolbox test module and the existing fixture sources.
These copies are diagnostic evidence, not a patch to apply to Melder.

## Discovery History: What Was Done and Why

### 1. Establish the preceding Spectrum baseline

The earlier Spectrum migration replaced manual service publication with native unique construction
for its four access services. Nine shared managers were already native-created. Actual configurations
remained named unique inputs, and Spectrum retained explicit references and cleanup responsibility.
The affected Spectrum/Iris selection passed 1,726 tests before the Toolbox slice. That is background
evidence for the starting host, not evidence that direct resolution of every injected provider worked.

### 2. Investigate deeper construction, then apply the owner's boundary

The owner requested a search for direct constructor sites that could use Melder. The investigation
traced center/group internals, pool ledgers/jobs, Toolbox, Actions, Interchange, Iris helpers and the
agent tier. The owner clarified the governing choice: private helpers consumed within their subsystem
can remain directly constructed and owned; shared infrastructure and objects crossing areas should
participate in Melder.

Following actual references narrowed the implementation to Toolbox. The center/group tracker and
pool-private Records/Job/counter construction were left direct. Toolbox and AgentBuilder already had
unique manager definitions. The change therefore concerned tool definitions and tool construction,
not making the managers unique or introducing another root/scope layer.

### 3. Implement the bounded Toolbox construction path

The current, uncommitted MelderOps changes are:

- `Toolbox.__init__(logger, *, root_conduit)` borrows the existing framework root.
- Its private helper is the existing `RootDefinitionRegistry`, used by the other builders.
- `register_tool` validates a concrete BaseTool class, admits its native definition, then publishes
  the alias. Existing compatible definitions are borrowed; incompatible definitions are refused.
- Tool products use the existing many/untracked builder policy. They remain caller-owned; Toolbox
  explicitly cleans its own registry/helper/logger, not the products.
- Replacing/removing the last alias retires only a definition introduced by that Toolbox.
- `build_tool(name, *, conduit, **kwargs)` melds by definition ID through the requested conduit,
  supplies the original kwargs as overrides, and preserves the previous output/error contract.
- Spectrum passes `root_conduit` as a meld override when it commissions Toolbox.
- CommandGroup passes its existing conduit. Pool/activity/mission/agent convenience paths continue
  delegating through the group; callers do not need to manage a new scope.

No RootDefinitionRegistry algorithm, Melder source, binding guards, frame layout, agent execution,
greenlet ownership, or native package installation was changed to achieve this.

### 4. Add real native tests for the proposed behavior

The new Toolbox component module exercises a real Spectrum and installed Melder. It covers unique
manager versus fresh tool identity, exact override identity, native dependency injection, requested
scope selection, caller-owned cleanup, aliases, borrowed definitions, incompatible definitions,
abstract refusal, constructor errors and CommandGroup forwarding.

The original dependency test bound a `ScopeService` at `tool_dependencies` with
`existence="unique_per_conduit"`, registered `AssistedTool(service: ScopeService, payload: object)`,
created two lesser scopes, and successfully built one assisted tool in each scope. It then used
a direct service meld to compare each injected service with its scope's canonical service.

The first of those direct service melds raised the CreationContext error. The later comparison for
the second scope was not reached. The original ScopeService was an empty class; the independent
diagnostic below deliberately uses an explicit constructor and observable state to remove that concern.

### 5. Record and repeat the first failure

The first focused selection completed with **113 passed, 1 failed, 2 skipped** (116 total). The failure
was `test_tool_dependencies_resolve_from_each_requested_scope`. An isolated rerun of that same test
failed at the same direct dependency lookup. These are separate recorded XML files; the original red
receipt was not overwritten by later passing results.

The ordinary sandbox initially could not launch the uv Python trampoline (`permission denied`, OS
error 5). The real tests were then run in the same approved `.venv314` through the permitted execution
path. That launch error is an environment/tool boundary, not the native resolver failure.

### 6. Remove the Toolbox operation from the failing sequence

The diagnostic in `test_native_dependency_lookup.py` defines plain `NativeService` and `NativeConsumer`
classes. It registers both directly with `root.bind` and resolves them directly with `scope.meld`.
There is no Toolbox registration/build call and no BaseTool inheritance in the body. The service has
an explicit constructor that sets `value = 7`; the consumer stores its typed service argument.

This diagnostic failed with the same error after `consumer.service.value == 7` passed. It establishes
that the Toolbox facade is not required in the operation sequence that triggers the failure.
It does not establish an application-free root: the fixture still configures Spectrum first.

### 7. Separate the two contracts instead of claiming the error was fixed

The Toolbox scope test now uses repeated tool construction to verify its own contract:

- two tool builds in the same scope receive the same injected service;
- a tool built in a different scope receives a different service;
- explicit payload objects keep their original identity.

All **14 cases** in the Toolbox native component module then passed. This was a change to how that
test verifies scope routing; it is **not a repair of the direct-provider lookup**. The original red
XML and the dedicated failing native-operation diagnostic remain preserved. The receiving Melder
regression must keep the direct provider meld and must not accept injection alone as success.

### 8. Capture source boundary and wider validation status

The installed traceback and three relevant installed method bodies were inspected. They establish
the immediate guard and call path described below, not the upstream reason for the missing payload.
Version/import origin/runtime mode and file hashes were recorded after the failure.

The subsequent affected MelderOps regression completed with **1,794 passed, 1 failed, 2 skipped**
(1,797 total). Its failure was a separate test fixture that directly constructed Toolbox without the
new required `root_conduit` argument:
`test_failed_consumer_construction_cleans_its_pending_logger[toolbox]`. That is a MelderOps fixture
adaptation item, not another observation of the CreationContext failure. Do not report this wider
run as fully green. Its result is included so this handoff describes the work state honestly.

## Executed Reduced Reproduction

The exact diagnostic file is copied into the evidence directory. Its relevant body is:

```python
class NativeService:
    def __init__(self) -> None:
        self.value = 7


class NativeConsumer:
    def __init__(self, service: NativeService) -> None:
        self.service = service


def test_native_dependency_can_be_melded_directly_after_injection(host) -> None:
    root = host.get_conduit()
    root.bind(
        spell=NativeService, existence="unique_per_conduit",
        spellframe="native_probe", binding_name="NativeService",
        disposal_method_names=[],
    )
    root.bind(
        spell=NativeConsumer, existence="many",
        spellframe="native_probe", binding_name="NativeConsumer",
        disposal_method_names=[],
    )
    scope = root.create_lesser_conduit(name="native-provider-probe")
    consumer = scope.meld(spellframe="native_probe", binding_name="NativeConsumer")
    assert consumer.service.value == 7
    assert scope.meld(
        spellframe="native_probe", binding_name="NativeService",
    ) is consumer.service
```

Both bindings are class references. No existing service instance is bound, no Conduit is bound, no
Package is involved, and no override is used in this reduced sequence. The ordinary classes have no
cleanup method; empty disposal declarations here do not bypass an application cleanup contract.

### Host fixture and isolation that remain part of the executed setup

The diagnostic imports `host` from the new Toolbox test module, and `spectrum` plus
`reset_spectrum_and_melder` from the existing Spectrum component conftest. `host` calls:

```python
spectrum.configure(SpectrumConfig().with_iris_logger_options(
    include_stream_mirror=False, include_system_stream_mirror=False,
))
return spectrum
```

The `spectrum` fixture calls the live implementation module's `Spectrum.get_instance()`.
First host construction initializes the normal framework Melder setup. No custom frame policy,
cache-disable setting, or manual native validation call is added by this host fixture.

The existing isolation fixture cleans an existing Spectrum, uses Melder's test-only Aether reset,
rebinds the imported Spellbook/Conduit test references to the fresh Aether, and reloads the public
MelderOps package. It repeats cleanup/reset after the test. Those private assignments are established
test-harness isolation, not repair steps between the successful and failing melds. The reproduction
body itself uses public operations only. The copied fixture source preserves this distinction.

### Exact run command used from the origin checkout

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
& '.venv314\Scripts\python.exe' -m pytest `
  context_compass/artifacts/2026-09-30_toolbox_native_dispense/test_native_dependency_lookup.py `
  -q --tb=short `
  --junitxml=context_compass/artifacts/2026-09-30_toolbox_native_dispense/native_dependency_lookup.xml
```

Run from the MelderOps checkout, with its tests package available. Copying this diagnostic into
Melder does not make its Spectrum fixtures native Melder fixtures. `reproduce_from_melderops.ps1`
in the evidence bundle runs the copied diagnostic against a caller-selected origin checkout without
installing or modifying packages. The receiving lead should also port the body to Melder's existing
isolated dynamic-root fixture as the first native reduction step.

## Evidence Ledger

| Receipt | Scope | Result | What it establishes |
| --- | --- | --- | --- |
| `focused.xml` | Toolbox unit/caller/group/native selection | 113 passed, 1 failed, 2 skipped | First failure is the direct injected-service lookup. |
| `dependency_lookup.xml` | Original failing Toolbox scope test alone | 1 failed | Repeated outside the broader selection. |
| `native_dependency_lookup.xml` | Two plain classes, direct bind/meld body | 1 failed | No Toolbox operation is required; host fixture still participates. |
| `native_contracts.xml` | Revised Toolbox native contract module | 14 passed | Scope dependency reuse/isolation and Toolbox behavior pass; direct-provider defect remains. |
| `regression.xml` | Wider affected MelderOps selection | 1794 passed, 1 failed, 2 skipped | Separate missing-root_conduit fixture adaptation remains. |
| `runtime_provenance.json` | Runtime/import/version/file-hash capture | Recorded | Identifies the tested installed distribution and relevant worktree bytes. |

No line-coverage percentage, performance result, clean-cache result, automatic-mode result, Linux/macOS
result, or current-Melder-source result is claimed by this ledger.

## Installed Failure Path: Confirmed Boundary

The installed traceback records this chain (line numbers belong to 0.2.8212 as captured):

1. `Conduit.meld`, `aether/conduit/conduit.py:4845`.
2. Dynamic meld delegation, `aether/conduit/meld/conduit_meld.py:593`.
3. `Meld._execute_admitted`, `aether/conduit/meld/meld.py:882`.
4. `Spell._get_or_build_creation_context`, `aether/spellbook/spell.py:847`.
5. `CreationContextFactory.get_or_build_for_spell`,
   `aether/conduit/meld/creation_context/creation_context_factory.py:361`.
6. `CreationContextBuilder.build`,
   `aether/conduit/meld/creation_context/creation_context_builder.py:121`.

The inspected `_execute_admitted` enters the creation gate and rechecks `resolution_required`.
It then selects an already-published context or asks the spell to build one. Only after obtaining
that context does it invoke the context's selected executor. The failing provider request takes the
context-building path and raises there, before returning an instance.

The inspected builder reads `spell._compiler_artifact._spell_codegen_creation`. Existing-creation
spells have a separate executor path; constructed class spells reject a None payload. The diagnostic
binds classes and reaches that rejection. This identifies the missing input at the guard. It does not
identify which earlier operation failed to create or preserve it.

Do not infer that the existing service instance disappeared, was cleaned, or was rebuilt. The
identity-return assertion was never reached. Do not infer a race merely because the runtime contains
gates. The diagnostic body is serial and has no user-created thread between the two calls.

## Hypotheses and Falsifiers — Not Root-Cause Findings

| Hypothesis | Investigation needed |
| --- | --- |
| Dependency occurrence planning builds an injectable service but does not establish its standalone creation payload. | Compare the service's planning/publication state before and after consumer resolution; establish the native invariant. |
| A readiness/cache flag reports enough progress for direct resolution while the required codegen payload is absent. | Capture readiness generation, context switch/publication and artifact availability at the direct request, without mutating them. |
| A later operation invalidates provider artifacts without requiring a coherent direct rebuild. | Add read-only boundary observations around the exact sequence; locate the first transition rather than assuming Phase 5 is responsible. |
| Spectrum configuration or a warm persisted cache is required. | Port to bare Melder fixtures; vary cache policy and cold/warm starts separately, retaining the original host case. |
| The behavior is specific to lesser-conduit or unique_per_conduit execution. | Compare root versus lesser and selected supported lifetimes, preserving each lifetime's expected identity semantics. |

## Historical Leads

- `tickets/epics/completed/2026-09-05_shared_context_rebuild_publication_epic.md` describes the same
  missing-payload guard under concurrent shared-context rebuilding. Its header says it was closed
  `cancelled_deferred`, with repair unimplemented/unqualified at that closure. Read its later history
  and relevant subsequent work before interpreting that status. The new diagnostic is a different,
  serial operation sequence; no common cause has been established.
- `tickets/epics/completed/2026-09-13_provider_artifact_ownership_and_existing_instance_planning_epic.md`
  records delivered provider-artifact and existing-instance planning repairs. Its older provider proof
  involved a borrower link/contract and structural revalidation on installed 0.2.40. The new diagnostic
  uses installed 0.2.8212 and has no explicit cross-root link. Do not label this a regression of that
  repair until the implementation and tests demonstrate it.

These are navigation aids for the receiving lead, not evidence that an old patch should be reapplied.

## Proposed Work Packages

These are proposed story scopes within this epic; separate story files have not been created or
assigned. Instantiate them through normal Melder workflow when the owner selects the implementation.

### A. Reproduce and reduce the current public sequence
- Reproduce the copied diagnostic in the recorded installed environment.
- Run the equivalent body against current `melder_private` source using native test isolation.
- Reduce away Spectrum while retaining dynamic mode, named bindings and the original lifetimes.
- Record precise policy/version/source/cache differences when a variation changes the outcome.
- Exit: a reliable native regression, or an explicit minimal host-configuration dependency.

### B. Establish the violated readiness/publication invariant
- Follow the source architecture/component/graph routing to the native owners named in the traceback.
- Read the whole relevant call path and capture state at the operation boundaries.
- Distinguish compiler payload ownership, CreationContext publication and application-instance storage.
- Determine whether the service ever had a standalone payload, and which public operation is required
  to establish or rebuild it before direct execution.
- Exit: evidence-backed cause and smallest repair boundary; no speculative catch-and-retry workaround.

### C. Repair the native contract and protect related lifetimes
- Implement the owner-approved native repair with deterministic teardown and error propagation.
- Preserve the successful identity policy and valid refusal paths.
- Keep the direct-provider assertion enabled; no xfail or expected-error conversion for acceptance.
- Add the targeted regression and related variants justified by the actual cause.
- Exit: native red-to-green evidence plus appropriate existing resolution/cache/publication checks.

### D. Revalidate the consumer and deliver the build
- Have the owner provide/install the corrected wheel through the established release workflow.
- Verify actual import origin and artifact hashes, not just a matching version string.
- Run the unchanged direct diagnostic and the original direct-provider comparison in the Toolbox case.
- Run the relevant consumer regression set; distinguish unrelated fixture failures explicitly.
- Complete Melder source docs, graph, version/release note and generated assets when a source fix lands,
  per `special_instructions/agent_contribution_guide.md`. This draft-only handoff takes no version notch.

## Validation Matrix

Begin with the original sequence; broaden only when a difference is relevant to the isolated cause.

| Axis | Required starting case | Useful controlled variation |
| --- | --- | --- |
| Creation order | Consumer first, provider directly second | Provider first; repeated consumer; repeated direct provider |
| Scope | One lesser conduit from a dynamic root | Root request; sibling lessers |
| Lifetime | Service unique_per_conduit; consumer many | unique or many with their own correct identity expectations |
| Registration | Late root.bind after root exists | Bind before conjure |
| Inputs | Required concrete service annotation; no override | Explicit service override as a separate bypass characterization |
| Cache | Original host's actual policy | Explicit disabled cache; fresh cache; warm cache |
| Host | Spectrum-prepared root | Native-only equivalent fixture |
| State changes | None between the two melds | Validation/purge/notch only if source evidence links their invariants |
| Concurrency | Serial test body | Concurrent checks only after the serial cause is understood |

## Acceptance Criteria
- [x] Both plain class binds succeed using supported public APIs.
- [x] Consumer meld succeeds with a usable injected service.
- [x] Subsequent direct service meld succeeds in the same scope and returns that exact instance.
- [x] Repeated same-scope requests preserve the selected lifetime; sibling scopes remain isolated.
- [x] The test observes the real result, not just absence of the previous error string.
- [x] No application-side compiler-cache mutation, fake instance binding or forced warm-up is required.
- [x] The original failing diagnostic is green against the delivered installed build.
- [x] Cause and supported configuration boundary are recorded; untested variants stay identified.
- [x] Any source repair completes the normal Melder validation/documentation/release obligations.

## Risks / Mitigations
- Same error text can arise through multiple paths. Preserve the exact call sequence and installed bytes.
- Cached contexts can legitimately exist separately from a compiler payload. Repair the invariant,
  not a superficial condition whose purpose has not been established.
- A global recompilation workaround may hide the error while changing hot-path cost. Measure any
  repair that adds work to ordinary warm resolution, using existing benchmarks when applicable.
- Pytest teardown may make later object representations look cleaned. Capture original failure state
  before teardown if liveness becomes part of the diagnosis.
- Do not mix the separate Toolbox constructor-fixture failure into this native issue.

## Open Questions
- Does a native-only root reproduce this on the current checkout?
- Was the service codegen payload never emitted, invalidated, or only unavailable to this path?
- Which readiness/cache generation is authoritative for the direct request?
- Does cache posture or prior host setup affect reproducibility?
- Do other lifetimes or resolution doors exhibit the same transition?
- Is there a demonstrated relationship to either historical epic?

## Decision Log
- Owner requests a detailed Melder epic and evidence handoff, not a Melder source patch in this turn.
- Keep the known failing direct lookup as the native acceptance contract.
- Separate tested observations from root-cause hypotheses and from host-independent claims.
- Preserve MelderOps's explicit owner cleanup and its ongoing local/shared composition decision.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-09-30_injected_dependency_direct_resolution/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: retain original red receipts and provenance through native repair and downstream acceptance.
- `evidence_manifest.json` lists the copied files, their original paths and SHA-256 values.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- Required re-entry sources: this epic, evidence manifest, exact diagnostic, installed provenance,
  native red XML, and the source owners named in the failure path.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: (2026-09-30T21:18:29Z) the owner's directive in chat
  ("you can close that epic if its done"); C and D met every acceptance criterion. Earlier: review ->
  in_progress below.
- from_state: review
- to_state: in_progress
- transition_reason: (2026-09-30T16:19:54Z) the owner assigned the Melder lead to melder_0 in chat ("take on
  this epic ... this is important"). Earlier: none -> review (2026-09-30T15:45:47Z), command_0's
  cross-repository finding handoff; no implementation assignment was inferred then.

## Notes
- DATETIME: 2026-09-30T15:45:47Z
  TYPE: FACT
  CLAIM: Installed Melder 0.2.8212 successfully injects NativeService into NativeConsumer, then
    direct same-scope service resolution raises at CreationContextBuilder's missing-payload guard.
    The public native-operation diagnostic still uses a Spectrum host fixture. No native repair
    or fully standalone reproduction has been performed.
  EVIDENCE:
  - artifacts/2026-09-30_injected_dependency_direct_resolution/test_native_dependency_lookup.py:11-35
  - artifacts/2026-09-30_injected_dependency_direct_resolution/native_dependency_lookup.xml:1-1
  - artifacts/2026-09-30_injected_dependency_direct_resolution/runtime_provenance.json
  IMPACT: A concrete native-resolution transition needs investigation; Toolbox changes alone
    cannot be assumed to explain or repair it.
  NEXT: Port the exact body to Melder's isolated dynamic-root fixture and compare installed/source behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-30T16:19:54Z
  TYPE: DECISION
  CLAIM: The owner assigned this epic to melder_0 as Melder lead (chat, 2026-09-30: "also please take on this epic
    too ... this is important"). Tranche order: work packages A and B run in one read-only task - reproduce on
    current source without the Spectrum host, vary the matrix, establish the cause - which ends in a
    DECISION_REQUEST with repair options. Work package C (the repair with its patch docs, red-to-green regression,
    notch, release note and rebuild) starts only on the owner's pick; D (installed-wheel revalidation in MelderOps)
    follows the owner's delivery. The three installed files at the failure boundary are byte-identical to current
    melder_private source, so the current tree is the right target.
  EVIDENCE:
  - tickets/tasks/2026-09-30_reproduce_injected_provider_direct_meld_task.md:115-134
  - artifacts/2026-09-30_injected_dependency_direct_resolution/evidence_manifest.json
  IMPACT: The epic moves from handoff to active Melder work; no source change is authorized before the owner's pick.
  NEXT: Run the bare-Melder probe of the diagnostic body (the task's NEXT).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-30T16:34:07Z
  TYPE: FACT
  CLAIM: Work packages A and B are done (read-only). The failure reproduces on bare Melder at current source without
    the Spectrum host, cache on or off, on the root or any lesser, for unique_per_conduit, unique and many providers:
    a provider bound after conjure and first built as a consumer's dependency cannot be melded directly afterwards.
    Cause: the consumer's target-local pass publishes only the consumer (the 2026-09-19 publication restriction),
    but local Phase 6 stamps the provider's conduit verdict valid; the Book's validation flag then clears and the
    direct meld never resolves the provider, so CreationContextBuilder's correct guard raises. Binds before conjure
    and a provider-first meld are unaffected. Repair options and the recommendation are in the task's
    DECISION_REQUEST.
  EVIDENCE:
  - tickets/tasks/2026-09-30_reproduce_injected_provider_direct_meld_task.md:188-227
  - tickets/tasks/2026-09-30_reproduce_injected_provider_direct_meld_task.md:245-279
  IMPACT: The epic's first two acceptance questions (native reproduction, cause) are answered; the repair waits on
    the owner's pick, and no historical epic's cause applies (serial sequence, no concurrency, no borrower link).
  NEXT: Owner picks A, B or C; then work package C as a patch lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T17:41:36Z
  TYPE: DECISION
  CLAIM: The owner's repair contract, relayed by command_0 (priv_commandops mailbox, 17:04:54Z; consumed here): late
    binding into resolution and meld must automate the validation and compilation it needs - no explicit
    validate_resolution call, no second conjure, no provider-first warm-up - and a manual validation workaround is
    not acceptance; post-conjure binds deliberately take the gated route, so resolution_required is not to be
    flipped blindly. The owner's suspected cause (the dependency is not left validation-required or gated) is the
    cause the task established: the consumer's local Phase 6 stamps the dependency's conduit verdict valid although
    that pass published no plan for it, and the Book's validation flag then clears. All three repair options meet
    the contract with no caller step: A keeps the gated route (the flag stays raised until each such dependency is
    melded directly); B sets resolution_required only on an owned dependency with no plan of its own and has the
    deferred lane run the full target pass, a reasoned departure from the gated-route rule stated in the
    DECISION_REQUEST; C compiles dependencies inside the consumer's pass. The repair still waits on the owner's
    pick; the lane stays parked behind the per-frame spell-id lane (owner, chat).
  EVIDENCE:
  - priv_commandops/context_compass/tickets/tasks/2026-09-30_toolbox_native_dispense_task.md:143-161
  - tickets/tasks/2026-09-30_reproduce_injected_provider_direct_meld_task.md:188-227
  - tickets/tasks/2026-09-30_reproduce_injected_provider_direct_meld_task.md:229-279
  - tickets/epics/2026-09-30_injected_dependency_direct_resolution_epic.md:419-428
  IMPACT: The contract is the acceptance criterion for work package C and matches this epic's own criterion that no
    forced warm-up or application-side workaround is required.
  NEXT: The owner's repair pick, after the per-frame spell-id lane lands.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T17:57:31Z
  TYPE: ALIGNMENT_CHECK
  CLAIM: Owner (chat, during the per-frame lane): the provider spell should be flagged as requiring validation when
    it is melded as a dependency, or a validation should be triggerable - "I think thats part of the problem"; to be
    talked through when this lane resumes. It matches the traced cause: the consumer's target pass leaves the
    provider stamped valid for the conduit with no plan of its own, so nothing marks it as needing work before its
    first direct meld. Option A keeps it validation-required (gated) until its own pass runs; option B flags it
    (resolution_required) so its first direct meld runs that pass; both set the flag the owner describes and need
    no caller step, as the relayed contract requires (note above). Open for the discussion: A or B, and whether
    "trigger a validation" means an internal trigger at meld or a public call (the contract rules out requiring one).
  EVIDENCE:
  - tickets/tasks/2026-09-30_reproduce_injected_provider_direct_meld_task.md:188-227
  - tickets/tasks/2026-09-30_reproduce_injected_provider_direct_meld_task.md:245-279
  - tickets/epics/2026-09-30_injected_dependency_direct_resolution_epic.md:527-550
  IMPACT: The owner's leaning narrows the repair to the flag-setting options (A or B); the pick between them and the
    public-trigger question are the discussion items.
  NEXT: After the per-frame lane lands, talk A vs B (and any public trigger) through with the owner, then open work
    package C.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T19:07:02Z
  TYPE: DECISION
  CLAIM: Owner pick for work package C (chat, 2026-09-30): option B - the consumer's target pass flags each owned
    dependency that has no plan of its own with resolution_required, and that dependency's first direct meld runs
    its own full resolution pass through the deferred lane, returning the instance its scope already holds. No
    caller step, no public trigger (the owner chose B alone), verdicts and the Book validation flag unchanged. The
    owner asked for regression tests first ("make a regression test then fix it", "or multiple tests"). The
    reproduce task is turned in; work package C runs in tickets/tasks/2026-09-30_resolve_injected_provider_on_first_direct_meld_task.md.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-30_reproduce_injected_provider_direct_meld_task.md:246-277
  - tickets/epics/2026-09-30_injected_dependency_direct_resolution_epic.md:552-571
  IMPACT: The repair is fixed to one option; the epic's exit gate now waits on C (red-to-green regressions, notch,
    docs) and D (the owner's wheel delivery to MelderOps).
  NEXT: Regression tests in tickets/tasks/2026-09-30_resolve_injected_provider_on_first_direct_meld_task.md, run red, then the fix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T20:22:19Z
  TYPE: MEASURE
  CLAIM: Work package C is done and in review: option B landed as 0.2.8215 - a successful target-local pass flags
    each owned dependency it compiled without a plan of its own (resolution_required), and the deferred lane runs
    the full target pass for a spell that is not its Phase 5 root - with 13 component regressions (red on 0.2.8214:
    11 failed, the 2 controls passed) and 14 unit tests red then green, the full suite green in the VM apart from
    the build-asset stamp the rebuild then refreshed, the system docs, graph, release note, patch archive and the
    asset and LLM rebuild (--check OK). The unchanged diagnostic body passes on source in every variant; the epic's
    installed-build criteria wait on work package D.
  EVIDENCE:
  - tickets/tasks/2026-09-30_resolve_injected_provider_on_first_direct_meld_task.md:188-209
  - tickets/tasks/2026-09-30_resolve_injected_provider_on_first_direct_meld_task.md:260-290
  - tickets/tasks/2026-09-30_resolve_injected_provider_on_first_direct_meld_task.md:420-441
  IMPACT: The Melder side of the epic is complete on the tree; acceptance against the delivered installed build
    (the diagnostic in MelderOps, the original Toolbox comparison) is D.
  NEXT: Owner turns in the task; D after the owner delivers the corrected wheel to MelderOps.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T21:18:29Z
  TYPE: DECISION
  CLAIM: Epic closed on the owner's directive (chat): "you can close that epic if its done". Acceptance: the two
    binds, the consumer meld and the direct meld returning the injected instance, lifetimes and sibling isolation
    (13 component regressions, 0.2.8215); no caller step; the unchanged diagnostic green on the installed wheel in
    a MelderOps host, red on 0.2.8212 in the same env; cause and boundary recorded in the reproduce task and C;
    release obligations met (notch, release note, docs, assets, bundles). Not run: the diagnostic under the
    Windows interpreter (the same RECORD-verified files are in .venv314).
  EVIDENCE:
  - context_compass/artifacts/wheel_0_2_8215_20260930/diagnostics_0_2_8215.log:1-14
  - context_compass/artifacts/wheel_0_2_8215_20260930/diagnostics_control_0_2_8212.log:1-15
  - context_compass/artifacts/wheel_0_2_8215_20260930/suite/summary.txt:1-67
  - tests/component/melder/aether/conduit/test_conduit_component_injected_provider_direct_meld.py:174-286
  - release_docs/next_version_release.md:282-306
  IMPACT: The injected-dependency defect is fixed and delivered; no work package remains open.
  NEXT: None.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-01T11:11:52Z
  TYPE: FACT
  CLAIM: Post-closure acceptance from the consumer (command_0's NOTICE in MelderOps' mailbox, consumed here): the
    owner-requested retest on the installed 0.2.8215 wheel in priv_commandops/.venv314 (Python 3.14.7t, GIL off)
    passes all four original probes - service-only, service-first, tool-first then direct service resolution,
    and plain consumer-first lookup - with the Toolbox and framework-manager modules: 65 passed, none failed or
    skipped, probe and source hashes unchanged before and after. This covers the Windows-interpreter run the
    closing note lists as not run. Not a full-suite result.
  EVIDENCE:
  - priv_commandops/context_compass/tickets/tasks/2026-09-30_toolbox_native_dispense_task.md:237-256
  - priv_commandops/context_compass/artifacts/2026-09-30_toolbox_native_dispense/2026-10-01_native_retest.xml:1-1
  IMPACT: The fix is confirmed by its consumer on the interpreter the closure could not run.
  NEXT: None.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary

Start with the copied 35-line diagnostic and its red XML, then read the fixture/provenance section.
Consumer construction and injection pass; the immediate direct provider meld raises before returning.
The original focused red case, isolated rerun, public-native-operation red case and 14 passing Toolbox
contracts are all retained. The wider 1,797-case run has one separate fixture adaptation failure.
No native source fix, package upgrade, native-only-host proof, or complete Toolbox delivery is claimed.
The next Melder lead should reduce the host and establish the missing-payload invariant before choosing
a repair. Source work, agent/greenlet changes and releases are not authorized by this drafting action.

2026-09-30 (melder_0): the owner assigned the Melder lead to melder_0. Work packages A and B run read-only in
tickets/tasks/2026-09-30_reproduce_injected_provider_direct_meld_task.md; no source change before the owner's pick.

2026-09-30 (melder_0): the owner picked repair option B; work package C runs in
tickets/tasks/2026-09-30_resolve_injected_provider_on_first_direct_meld_task.md (regression tests first, then the fix).

2026-09-30 (melder_0): work package C landed as 0.2.8215 and is in review; D (installed-wheel
revalidation in MelderOps) follows the owner's wheel delivery.

2026-09-30T21:18:29Z (melder_0): D done - 0.2.8215 installed in MelderOps' environments, the diagnostic green on it;
epic closed on the owner's directive.
