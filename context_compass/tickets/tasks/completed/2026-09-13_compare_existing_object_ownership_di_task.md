# Task: Compare existing-object identity and ownership across DI systems

- Completed: 2026-09-19T14:51:36Z
- Closure Basis: explicit owner request to turn in all delivered updater_0 work.
- Summary: Delivered cited framework comparison. Exact duplicate-reference/alias cleanup questions remain explicitly unverified and are parked with the user-created-object design.
- Deferred work: tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md.
  Historical unchecked redesign/downstream items are deferred, not an implementation claim.


## Metadata
- Task ID: TASK-2026-09-13-compare-existing-object-ownership-di
- Epic: EPIC-2026-09-13-existing-object-lifecycle-ownership
- Status: done
- Owner: codex
- Agent Name: updater_0
- Priority: p2
- Created: 2026-09-13T22:27:10Z
- Updated: 2026-09-19T14:51:36Z

## Objective
Explain how Dishka, Dependency Injector and Autofac handle objects created outside the container:
identity/reuse, multiple instances of one type, scope visibility, registration keys and cleanup ownership.
Use the comparison to inform Melder's deferred existing-object model without selecting or coding a patch.

## Current Owner Focus
Follow an actual user-created instance through registration, reuse and release in the three external
frameworks. Verify same-instance duplicate registration, same/different keys, whether registrations
merge or remain independent, and who owns cleanup. Do not substitute factory/class lifetime tutorials
or Melder implementation audits for this question. The existing general comparison is background.

## Ticket Contract
- ENTRY_GATE: owner requests research; this task is routed and linked to the deferred ownership epic.
- EXECUTION_BOUNDARY: primary documentation/source research, local evidence and ticket updates only.
- DEPENDENCIES: existing-object lifecycle epic and its construction/validation/ownership distinction.
- EXIT_GATE: cited comparison answers uniqueness, multiplicity and disposal, with limitations explicit.
- FAILURE_ESCALATION: label undocumented behavior UNKNOWN; do not generalize one framework's policy to another.

## Scope Boundaries
- In scope: existing instances, per-registration/per-scope reuse, type/key multiplicity, aliasing and cleanup.
- Owner clarification: the comparison is about the three external DI systems; stop the Melder implementation trace.
- Out of scope: Melder runtime changes, dependency installation, benchmarks or asserting unexecuted runtime tests.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: owner accepts turn-in of delivered scope and explicitly backlogs unperformed user-created-object work.

## Steps
- [x] Read official instance/context/resource and registration/scope documentation for each framework.
- [x] Resolve distinctions between one object, one registration, one key, one scope and one type.
- [x] Verify multiple-instance and cleanup ownership rules, including explicit ownership wrappers.
- [x] Publish cited findings and update the parent epic with implications and unresolved choices.

## Deliverables
- A durable cited comparison and a clear conversational explanation.
- Source links and concrete examples sufficient to revisit the lifecycle design after compaction.

## Files / Paths Impacted
- This task and its parent epic, plus routing/artifact/mailbox boards.
- artifacts/existing_object_di_comparison_20260913/comparison.md (created after research).

## Validation
- Primary-source verification. No external-framework runtime tests or installations.
- A native Melder probe ran outside the intended comparative scope: seven controls passed, two
  assumed alias-admission cases failed. Retain as historical evidence; no follow-up investigation here.

## Risks / Rollback Notes
- Do not equate singleton reuse with a global one-instance-per-type restriction.
- Distinguish registration replacement from retaining multiple addressable providers.
- Do not equate cached context values with automatically owned disposable resources.
- Autofac Owned<T> is a named framework feature; distinguish it from ordinary instance registration.

## Applicable Anti-Patterns
- [ ] No unsupported cross-framework equivalence or performance claims.
- [ ] No implementation decision hidden inside a research summary.
- [ ] No test execution claims for examples read only in documentation.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/existing_object_di_comparison_20260913/comparison.md
  - artifacts/existing_object_di_comparison_20260913/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: retain the cited design research for the existing-object epic.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: preserve unresolved semantics with exact next primary-source lookup.

## Notes
- DATETIME: 2026-09-13T22:27:10Z
  TYPE: PLAN
  CLAIM: Owner asks how Dishka, Dependency Injector and Autofac handle owned/existing objects,
    whether they are unique and whether multiple instances can coexist. Compare identity,
    registration keys, scope caches and cleanup custody independently.
  EVIDENCE:
  - Owner's cross-framework research request in this conversation.
  - tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md
  IMPACT: Research is authorized; the implementation epic remains deferred.
  NEXT: Read official instance/context registration and disposal documentation across the three frameworks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T22:31:00Z
  TYPE: FACT
  CLAIM: Official docs distinguish reuse from type-level multiplicity. Autofac accepts provided
    instances and owns disposal unless ExternallyOwned; multiple service registrations retain
    selection semantics. Dishka supports context inputs, components and collect; Dependency Injector
    Object supplies a retained value while List/Dict compose multiple providers.
  EVIDENCE:
  - https://docs.autofac.org/en/latest/register/registration.html
  - https://docs.autofac.org/en/latest/lifetime/disposal.html
  - https://dishka.readthedocs.io/en/stable/provider/from_context.html
  - https://dishka.readthedocs.io/en/stable/advanced/components.html
  - https://dishka.readthedocs.io/en/stable/advanced/collect.html
  - https://python-dependency-injector.ets-labs.org/providers/object.html
  - https://python-dependency-injector.ets-labs.org/providers/dict.html
  IMPACT: Do not interpret Melder's unique lifetime as proof that other systems forbid additional
    objects of the same class. Cleanup semantics for Python context/Object inputs still need verification.
  NEXT: Verify scope reuse and cleanup defaults, then compare duplicate keys and explicit ownership handles.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T22:34:01Z
  TYPE: FACT
  CLAIM: Primary sources separate cached identity from finalization. Dishka closes generator
    finalizers and maintains per-scope caches; context values are externally supplied and shared
    across components. DI Object retains its supplied reference (also through provider deepcopy);
    Resource supplies shutdown, while Singleton reset only clears a reference. Autofac RegisterInstance
    configures/enforces single-instance sharing, with ownership stored independently.
  EVIDENCE:
  - https://dishka.readthedocs.io/en/stable/container/index.html
  - https://dishka.readthedocs.io/en/stable/provider/provide.html
  - https://dishka.readthedocs.io/en/stable/advanced/context.html
  - https://python-dependency-injector.ets-labs.org/providers/resource.html
  - https://python-dependency-injector.ets-labs.org/providers/singleton.html
  - https://raw.githubusercontent.com/ets-labs/python-dependency-injector/master/src/dependency_injector/providers.pyx
  - https://raw.githubusercontent.com/autofac/Autofac/develop/src/Autofac/RegistrationExtensions.cs
  IMPACT: A supplied object need not be globally unique by class, and retaining it is not equivalent
    to installing cleanup. Source cross-checks use upstream branches, not a locally executed release.
    Discard the stale raw Dishka cache as current-version evidence; current docs/rendered source suffice.
  NEXT: Publish the comparison with scoped multiplicity examples and explicit Melder design implications.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T22:38:30Z
  TYPE: FACT
  CLAIM: Published the three-framework comparison with primary links, identity examples and
    framework-specific cleanup defaults. Includes Autofac Owned<T>, Dishka shared context versus
    components/collection, and Dependency Injector Object versus Singleton/Resource. No external
    framework runtime tests or package installations were performed.
  EVIDENCE:
  - artifacts/existing_object_di_comparison_20260913/comparison.md:1-167
  IMPACT: Melder design should specify service key, registration, value identity, scope/reuse and
    cleanup owner separately. This does not select transfer/rollback or runtime Protocol-validation
    semantics; those remain separate research/implementation boundaries in the deferred epic.
  NEXT: Discuss the ownership/identity model with the owner before choosing a Melder implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T22:55:09Z
  TYPE: PLAN
  CLAIM: Owner asks how existing-object resolution and singleton/transient semantics relate to
    Melder's registration uniqueness and its Aether-level switch. Trace the actual switch, collision
    domain, frame key claims and stored existing-reference return before explaining the combined model.
  EVIDENCE:
  - Owner's follow-up question about lifecycle and registration uniqueness.
  - src/melder/aether/aether_configuration.py:process_wide_unique_spell_ids
  IMPACT: Keep reuse/creation, object identity, key uniqueness and cleanup ownership separate.
    The requested source trace is research; it does not authorize changing Melder's uniqueness policy.
  NEXT: Read Aether collision lookup and frame claim logic, then compare identical and differently named registrations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T22:59:19Z
  TYPE: FACT
  CLAIM: Aether's switch changes spell-ID collision scope between process and frame. Frame-local
    active-key uniqueness remains in LookupContainer. Bind fingerprints include binding_name,
    spellframe and existence; existing-value executors return the stored reference directly.
    These checks do not constitute a process-wide reverse registry of Python object identities.
  EVIDENCE:
  - src/melder/aether/aether.py:2028-2092
  - src/melder/aether/aether.py:2263-2312
  - src/melder/aether/aetheric_frame/lookup_container.py:93-129
  - src/melder/aether/spellbook/bind/bind.py:573-672
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:155-201
  IMPACT: Verify same-reference/different-name bindings, same-key refusal, cross-frame flag behavior
    and class-singleton versus prebuilt-reference reuse with real Melder calls. Existing source tests
    also document a separate concurrent-conjure preflight race; do not claim atomic global uniqueness.
  NEXT: Run a native identity matrix under the public configuration API in isolated test worlds.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T23:03:24Z
  TYPE: DECISION
  CLAIM: Owner clarifies that the open lifetime question concerns Dishka, Dependency Injector and
    Autofac, not Melder implementation. Stop the native investigation and answer fixed-reference
    versus factory singleton/transient/scoped semantics and cleanup ownership for those systems.
  EVIDENCE:
  - Owner correction in this conversation.
  - artifacts/existing_object_di_comparison_20260913/melder_identity_probe.log
  - artifacts/existing_object_di_comparison_20260913/melder_identity_probe.xml
  IMPACT: The out-of-scope probe returned seven passes and two failures: distinct named registrations
    were rejected by DuplicateSpellNameStrategy, refuting the tentative alias-admission assumption.
    No source changes occurred; preserve evidence without continuing or presenting it as the answer.
  NEXT: Explain the external frameworks' fixed-instance reuse and separate cleanup policies.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T23:19:03Z
  TYPE: DECISION
  CLAIM: Owner again narrows the question to user-created instances registered and reused; generic
    factory/singleton explanations are not the requested comparison. Exact same-reference duplicate
    registration and cleanup ownership have not been established across all three frameworks.
  EVIDENCE:
  - Owner correction: user-created objects being registered and reused, not elementary DI.
  - artifacts/existing_object_di_comparison_20260913/comparison.md
  IMPACT: Do not present multiple same-type factory registrations as evidence for handling a
    repeatedly registered prebuilt reference. Autofac Disposer's stack has no identity deduplication,
    but that alone cannot prove the complete RegisterInstance lifecycle; activator source fetches
    were unavailable through browsing and the public HTTP fallback was refused. No new runtime tests.
  NEXT: Verify exact existing-reference registration and release cases from primary source/tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T14:51:36Z
  TYPE: DECISION
  CLAIM: Owner accepts turn-in of this delivered record. Delivered cited framework comparison. Exact duplicate-reference/alias cleanup questions remain explicitly unverified and are parked with the user-created-object design.
  EVIDENCE:
  - Owner instruction to backlog user-created-object ideas and turn in all work done.
  - artifacts/updater_0_turn_in_20260919/closure_manifest.json
  IMPACT: Record closed with its historical evidence retained. Deferred requirements remain visible
    in the backlog epic; no new runtime, test, installation or release result is implied.
  NEXT: Resume deferred work only on a new explicit owner request.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Noting Behavior
Record primary-source findings before each next research tranche; mark inferences separately.

## Context / Handoff Summary
CLOSED BY OWNER: delivered scope is turned in; see the completion summary at the top. Any earlier
review/resume instructions below are historical. Deferred user-created-object work is parked in the
backlog epic and does not request continued implementation.

Owner corrected scope: external DI semantics only; no further Melder investigation in this task.
Latest focus is specifically the identity and custody of user-created instances through repeat
registration and reuse. General class/factory lifetime material does not settle this; exact
duplicate-reference registration/disposal results remain unverified across all three systems.
Research complete for review; read comparison.md. All three admit multiple objects of one class,
with distinct provider/key/scope mechanisms and different cleanup defaults. No runtime tests,
installations or Melder source changes. Transfer/alias cleanup guarantees and Protocol-check parity
remain separate bounded investigations; the ownership epic's implementation remains deferred.
