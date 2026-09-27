# Melder Roadmap

**Status:** Expanded discussion draft — established direction plus labeled proposals  
**Planning horizon:** Approximately two years from adoption, covering the full path to 2.0.

## North star: governed runtime evolution of software

Melder's intention is to make software evolvable through its running runtime.
Humans and agents should be able to understand a live system, propose and research
changes, obtain the required authority, introduce new capabilities, verify the
outcome, and preserve or recover the resulting system through supported mechanisms.

The intended product is not merely object construction, dependency injection, or
an agent wrapper. It is a runtime foundation for the ongoing evolution of software,
with service-management practices, operational evidence, change controls, and
frame-owned governance built into that foundation.

The 1.0 direction includes an agent-usable, ITIL-compatible service-management
capability, the MutationResearch mechanics needed to support governed evolution,
and additional frame-local systems. Full compatibility is a target to define and
substantiate, not a claim that the current release is accredited or complete.

The roadmap has three connected stages: stabilize the public API, complete the
capabilities required by the runtime strategy, and progressively migrate the
implementation to Mojo while retaining a supported Python interface.

**API stability at 0.5 is not a feature freeze. Feature completion for the 1.0
scope and completion of the Mojo migration at 2.0 are separate milestones.**

The two-year horizon is a development target for the whole roadmap, not two years
per stage. Individual release dates will be assigned as scope and dependencies
are established. Releases must meet their acceptance criteria rather than ship
solely to satisfy a date.

## Milestones

| Target | Focus | Intended outcome |
| --- | --- | --- |
| **0.4** | API consolidation and stabilization | Review and settle public contracts across all systems and subsystems; resolve known inconsistencies and planned breaking redesigns. |
| **0.5** | Stable API baseline and alpha exit | Establish compatibility-protected public APIs, supported extension points, and an explicit deprecation process. |
| **0.5–1.0** | Feature development, integration, and performance | Add the features and implementation work required to fulfill Melder's declared 1.0 strategy and capability claims, alongside verification and optimization. |
| **1.0** | Complete supported runtime and dual licensing | Deliver the agreed 1.0 capabilities, supported tooling, documented contracts, and performance evidence. Make dual licensing available. |
| **1.2** | Mojo: compiler and resolution surfaces | Migrate compiler and resolution implementations behind the supported interfaces. |
| **1.4** | Mojo: backend | Migrate backend systems while preserving their documented behavior and interactions with other subsystems. |
| **1.6** | Mojo: Nexus | Migrate Nexus and its supported operator-facing and agent-facing surfaces. |
| **1.8** | Mojo: Crystallizer | Migrate Crystallizer and its persistence, checkpoint, and restoration responsibilities. |
| **2.0** | Complete Mojo migration | Complete migration of all Melder runtime systems and subsystems to Mojo, retaining a supported Python interface over the completed core. |

These are milestone targets, not a claim that the work has already shipped.
Intermediate releases can deliver compatible features, fixes, and incremental
migration work.

## Through 0.5: stabilize the contracts

By 0.4, the public APIs across Melder's systems and subsystems should be
consolidated into a coherent design. By 0.5, that work should establish the
compatibility baseline required to leave alpha.

The protected surface includes documented behavior, not only method names.
Configuration, inputs and outputs, errors, lifecycle and ownership rules,
structured inspection results, operator commands, extension points, and
persistence interfaces must have clear contracts appropriate to their role.

Internal implementation details can continue to change. Existing public contracts
must not become disposable merely because a subsystem is being expanded or
rewritten.

New features remain welcome after 0.5. Additions should extend established
contracts compatibly. Genuinely experimental additions must be explicitly
identified, with a clear process for becoming supported.

## 0.5–1.0: build out the intended runtime

This is an active feature-development phase, not merely a validation or
maintenance phase.

Melder will add the capabilities, integrations between subsystems, and
implementation work necessary to fulfill the strategy defined for 1.0. The work
includes closing architectural gaps, extending existing systems, completing
operator workflows, and making the supported tooling effective in practice.

The scope is the complete runtime, not only IoC or object resolution. Runtime
operation, ownership and lifecycle management, inspection, agent-facing tooling,
structural change, persistence, and recovery all belong in the release's
capability planning.

Correctness, usability, and performance will develop alongside the features.
A capability is not complete merely because an API exists: it must be accessible
through supported interfaces, work in the intended workflows, interact correctly
with other systems, and have documented limits.

Before 1.0, each capability claimed for that release must be connected to its
implementation, documentation, working examples or tooling, and appropriate
correctness and performance evidence. Significant unfinished work needed to
support a 1.0 claim remains release work; it is not automatically deferred to the
Mojo migration.

**1.0 is the target for delivering Melder's declared runtime capabilities, not
simply declaring the existing implementation stable.** It does not imply that
every possible future feature has been invented or delivered.

## 1.0 capability direction: an operational environment for evolution

### Direction established for this roadmap

The 0.5–1.0 phase includes active feature development across the runtime. It aims
to make the declared 1.0 strategy usable and performant, not simply to stabilize
or test the present implementation.

Agents should be able to participate in a complete governed-change workflow:
understand a service, investigate a problem or opportunity, propose a change,
assemble evidence, obtain authorization, stage and enact the change, evaluate the
outcome, and preserve the result or execute an approved recovery plan.

New service-management and governance systems should have frame-local ownership,
configuration, authority, and lifecycle. Separate frames must be able to adopt
separate policies without accidentally sharing mutable approvals, change state,
or operator authority.

The following workstreams are **proposed elaborations of that direction**. They
are not claims that these capabilities have already shipped. Names are functional
working labels, not decisions about public class names, exact module boundaries,
or guaranteed minor-release assignments. More systems may be introduced where
needed to meet the north star.

### Proposed workstream: frame-local service management and change enablement

Provide a machine-readable service-management model that supports change requests,
change models, authorization, scheduling, progress, verification, closure, and
links to incidents, problems, configuration items, releases, and improvement work.

Support a range of policy-driven change paths: pre-authorized repeatable changes,
assessed normal changes, and expedited emergency changes with explicit authority
and follow-up review. Not every operation should need a committee or synchronous
human intervention. Equally, an agent should not gain authority merely by labeling
its own request an emergency or assigning itself a low risk score.

Record which policy revision and principal authorized a particular plan, the
scope and limits of that authorization, and the evidence on which it depended.
Policy changes and delegation changes must themselves follow controlled paths.

Keep the long-running service-management workflow separate from short-lived
structural transaction admission. Do not hold runtime locks while waiting for
reviews, external systems, experiments, or an agent's next response. Revalidate
approved preconditions when the operation actually enters the mutation path.

### Proposed workstream: MutationResearch as the evidence foundation

Extend MutationResearch and its associated systems to support the complete
research side of runtime evolution. Connect candidate identities, source and
structural diffs, composition changes, dependency impact, baselines, experiments,
policy assessments, and observed outcomes through stable references.

The research record should be able to explain what was proposed, why it was
proposed, what alternatives were evaluated, which assumptions were used, what
was measured, and which implemented outcome followed the decision.

Preserve the distinction between a read-only candidate preview and actual
execution. Add a separately controlled rehearsal mechanism for tests and
benchmarks rather than making a preview secretly execute code. Record uncertainty
and untested conditions explicitly; a structural diff is not proof of arbitrary
runtime behavior or external side effects.

Bind evidence to the exact candidate, target frame, affected baseline revisions,
policy version, relevant configuration, and workload. If an affected dependency,
approval, or policy changes, re-evaluate the affected evidence before promotion.
An unrelated change elsewhere need not invalidate all work.

Give each concurrent operation explicit principal, frame, campaign, and change
identities. Ensure those identities survive retries and handoffs without leaking
through a shared ambient default into another agent's work.

Research should supply evidence to authorization, not automatically authorize its
own conclusions. Preserve the separate ownership of research, policy decisions,
runtime execution, and persistence custody.

### Proposed workstream: service catalog, configuration, and desired state

Add a frame-local service and configuration model that relates named services,
capabilities, ownership, dependency contracts, and explicitly managed external
resources to the live runtime graph.

Distinguish desired state, an approved baseline, currently observed live state,
and recorded historical state. Do not treat a stale checkpoint as proof of what
is running now. Provide stable identities and reconciliation rules for updates,
restores, external records, and frame replacement.

Use runtime topology as evidence for a service-management configuration view;
augment it with service meaning and explicit external-resource links rather than
assuming every Python object is automatically a complete configuration item.

### Proposed workstream: release, rollout, and state-transition coordination

Provide controlled staging and promotion of versions and compositions. Define
how rollout cohorts, compatibility checks, lifecycle hooks, health checks,
quiescence, and policy decisions compose with existing mutation mechanisms.

Specify what happens to in-flight calls, existing references, stateful instances,
shared resources, and cleanup when an implementation changes. Support explicit
state transfer or reconstruction where required. Do not imply that selecting a
new implementation automatically rewrites every previously returned Python
reference or preserves arbitrary state.

Separate structural reversion, object-state recovery, and compensation for
external actions. Recovery must state what it can restore and what remains
irreversible. Returning to an older implementation is a new forward-recorded
event, not deletion of the failed change's history.

Canary and shadow execution are candidate techniques, not blanket guarantees of
safe duplication: isolate or stub side effects before replaying a workload.

### Proposed workstream: incidents, problems, service health, and improvement

Extend the existing descriptive incident model with the supported operator
workflows needed for triage, ownership, impact, problem investigation, known
errors, remediation proposals, and verified resolution.

Connect incidents and health evidence to MutationResearch campaigns and governed
changes. Closing a record should not itself be presented as proof that the
service recovered. Conversely, merely recording a suspected incident must not
implicitly mutate the running graph.

Add explicit monitoring/event integration, service objectives, and performance
budgets so rollout decisions can use measured outcomes. Treat behavioral and
performance risk as additional evidence; do not confuse it with the existing
structural/resolution-validity risk signal.

The improvement loop should connect the original operational need to the proposed
change and its measured result. Telemetry collection must have declared overhead,
privacy, retention, and failure behavior rather than imposing uncontrolled work on
steady-state resolution.

### Proposed workstream: durable agent operations and delegated authority

Expose supported, discoverable, schema-versioned operations through the mediated
agent-facing interfaces. Agents should not need internal manager references or
undocumented object traversal to participate in service management.

Provide operation identities, progress, cancellation, idempotent retry semantics,
authorization expiry, and explicit recovery after interruption. A replacement
agent should be able to inspect the current operation state and continue only
within its own current authority. Restoring a record must not silently restore
expired privileges.

Support separate proposing, evaluating, approving, and executing roles where
policy requires it. Pre-authorized automation remains possible within bounded
models. Add structured refusal and escalation responses so agents can distinguish
an invalid candidate, stale evidence, missing authority, contention, and a failed
postcondition.

### Proposed workstream: extensible frame-owned subsystem hosting

Introduce or extend a stable hosting contract for new frame-local systems:
capability discovery, configuration schemas, dependencies, construction order,
activation, cleanup, version compatibility, observation, and persistence/restore
participation.

A system should be independently configurable without hidden process-global
state. Optional systems should be disabled or lazy where appropriate, so the
runtime does not require every application to pay for the entire governance stack.
This is a performance design target to measure, not a promise of zero overhead.

Agent and integration adapters should use these contracts rather than bypassing
the frame's permissions or taking ownership of internal kernel managers.

### Additional candidate: coordinated evolution across frame boundaries

Support explicit protocols for changes that affect multiple independently governed
frames. Each affected frame retains its own authority, policy, and local admission
checks. A coordinator may exchange proposals and evidence but must not silently
borrow another frame's authority.

Define partial failure, cancellation, and compensation. Local structural
transactions must not be described as global atomicity over multiple frames,
processes, databases, or external systems without an implemented and verified
protocol that actually provides it.

The mechanism can begin as an integration or federation layer; it does not require
removing the existing frame boundary or enabling arbitrary direct cross-frame
references.

### ITIL compatibility: make the goal testable

Full ITIL compatibility remains the target. Before describing it as achieved,
publish the targeted ITIL version and a practice-to-capability matrix identifying
native runtime support, supported integration responsibilities, organizational
roles, evidence, and any remaining gaps.

A small collection of change-related features is not by itself proof of full
compatibility. Practices outside direct runtime operation must be accounted for
through explicit supported boundaries rather than silently omitted or declared
satisfied by a ticket record. Select the precise baseline during scope definition;
this draft does not silently choose between ITIL editions.

Distinguish technical interoperability with selected ITSM products from alignment
with ITIL practices. Versioned adapters, authentication, correlation, retries, and
conflict reconciliation are implementation work, not automatic consequences of
using common terminology. Vendor integrations remain candidates until supported
products and versions are explicitly selected.

Do not describe this roadmap as an accreditation. Formal PeopleCert tool-vendor
accreditation would be a separate decision and assessment, not an outcome granted
by publishing a compatibility matrix.

### Architectural placement and boundaries

The uploaded source already has frame-local DevOps ownership and separate
incident, change-control, and risk managers. It also has an Aether-owned
MutationResearch singleton with named research sets and a persistence emission
boundary. These are foundations to extend, not absent systems to reinvent.

The proposed frame-owned governance services do not require inventing a separate
MutationResearch singleton inside every frame. One candidate design is to retain
the shared research root while exposing properly partitioned frame-scoped research
contexts. This requires explicit identity, authorization, publication, cleanup,
retention, and restore rules; a frame name or filter alone is not isolation.
Changing the root ownership model instead would be a deliberate architectural
migration, not a description of the current implementation.

Maintain four distinct responsibilities: research explains; governance authorizes;
transactional runtime mechanisms enact; persistence preserves the declared record.
Incident description and monitoring inform those decisions rather than becoming
implicit mutation channels.

Frame separation and in-process code checks should not be advertised as an
operating-system sandbox for hostile code. Rehearsal of untrusted code requires
appropriately isolated execution and explicitly controlled external effects.

### Proposed 1.0 acceptance scenario

Demonstrate an agent completing a governed runtime change through supported APIs:
identify a service issue, open a correlated investigation, produce a candidate,
attach static and executable evidence, receive the required authorization, stage
and promote under current preconditions, and evaluate the resulting service.

Demonstrate a refusal when the relevant baseline changed after approval; an
interrupted agent handing off without duplicating the mutation; a separate frame
remaining unaffected; and a controlled recovery whose limits are explicit.
Preserve the complete causal record of success, refusal, and recovery.

This scenario complements, rather than replaces, the full capability/ITIL coverage
matrix, subsystem tests, supported-platform qualification, and performance gates.

### Fit with the 0.5 contract baseline and the 2.0 migration

Specify common operation, evidence, policy, frame-hosting, and persistence seams
during the 0.4–0.5 API work. Their supported implementations and compatible
extensions can continue to grow through 1.0. Do not represent the entire future
feature set as frozen merely because the shared contracts are stable.

Every runtime subsystem introduced for 1.0 is included in the 2.0 migration goal.
MutationResearch and the new governance systems need explicit entries in the
migration inventory; their intermediate release allocation remains to be decided.
This does not change the owner's stated 1.2 compiler/resolution, 1.4 backend,
1.6 Nexus, and 1.8 Crystallizer sequence.

## Dual licensing at 1.0

Dual licensing is planned to become available with the 1.0 release.

The available license options and their exact terms will be published as part of
that release. This roadmap does not itself change the current license or grant
an alternative license before it is available.

## 1.0–2.0: progressively migrate the core to Mojo

After establishing the 1.0 runtime, Melder will use a strangler fig approach to
replace its Python implementation subsystem by subsystem.

Existing and migrated implementations will coexist during the transition.
Supported interfaces and explicit internal boundaries will route work to the
appropriate implementation. Each migrated subsystem must demonstrate the
required behavior and performance before replacing its predecessor.

Python access will remain available throughout the migration. The target at 2.0
is a completed Mojo runtime behind a supported Python interface—not a period
without Python access followed by its reintroduction at the end.

The migration is of Melder's runtime implementation. It does not require
applications, user-defined Python objects, or agent tooling to be rewritten in
Mojo.

### 1.2: compiler and resolution surfaces

Begin with the compiler and resolution implementations. Establish and exercise
the Python/Mojo boundary, preserve the supported compilation and resolution
contracts, and measure performance through the actual Python-facing API.

This milestone must qualify the interoperability and packaging approach needed
by subsequent subsystem migrations, including the supported interpreter and
concurrency configurations.

### 1.4: backend

Extend the migration into the backend. Preserve the contracts for runtime state,
ownership, lifecycle behavior, coordination, and subsystem interaction wherever
those responsibilities belong to the migrated backend.

Mixed Python/Mojo operation must be verified before the remaining systems depend
on the replacement backend.

### 1.6: Nexus

Migrate Nexus while preserving its supported interfaces and behavior for
inspection, mediated operations, agent workspaces, and structured responses.

Permission decisions, refusal behavior, object identity, and supported operations
across migrated boundaries must remain consistent with the public contracts.

### 1.8: Crystallizer

Migrate Crystallizer, including its supported recording, checkpoint, and
restoration workflows.

Define and test the supported compatibility of persisted formats and restored
systems across the migration. Where conversion is required, provide an explicit
migration path rather than silently changing the meaning of existing data.

### 2.0: complete the migration

Complete migration of all Melder runtime systems and subsystems to Mojo and
retire superseded Python core implementations.

Python remains the supported interface and integration layer. The objective is
to preserve the public programming model while changing the machinery beneath
it; the 2.0 milestone is not an excuse for unrelated API churn.

Completion requires the whole runtime to work through that interface, not merely
a collection of individually ported subsystems.

## Migration acceptance criteria

A migration milestone is complete only when its replacement meets the supported
behavioral contracts, works with the rest of the runtime, and satisfies defined
performance and delivery criteria.

Use shared contract tests and equivalent isolated workloads to compare old and
new implementations. Verify outcomes, errors, identity and lifetime semantics,
concurrency behavior, and relevant persistence behavior. For operations with
side effects, comparisons must not execute the same real-world mutation twice.

Measure end-to-end workloads through the Python interface, including
interoperability overhead, memory use, and concurrency. Performance improvement
is an engineering objective to demonstrate, not an automatic claim attached to
a language change.

Keep a controlled return path to the previous implementation until a migration
stage is accepted, where state and persisted-format compatibility permit it.
Document limits to reversal and data conversion explicitly.

Mojo interoperability, the toolchain, supported platforms, and package delivery
must be qualified as part of the migration. A subsystem does not become ready
solely because its source has been translated.

## Proposed compatibility and deprecation policy

From 0.5 onward, documented public contracts are compatibility-protected.

During the remaining 0.x series, planned removals require at least one
minor-release series of advance notice. A deprecation introduced at 0.5.0, for
example, remains supported throughout 0.5.x and can be removed no earlier than
0.6.0. Planned deprecations should normally begin at minor-release boundaries;
a late patch must not be used to create an effectively immediate removal.

Each notice must identify the affected API, the version where deprecation begins,
the earliest removal version, and the replacement or migration instructions.
Deprecated behavior remains supported and tested during its notice period.

From 1.0 onward, compatible additions can ship in minor releases, while
incompatible public API removals or changes require a major release and must
also satisfy the published notice policy. The 1.x Mojo migration should preserve
the established public contracts.

API compatibility, supported runtime environments, and persisted-data formats
must each have explicit expectations; preserving function names alone is not
enough.

---

**Stable contracts by 0.5. Governed runtime evolution, agent-usable service
management, and the agreed capabilities and performance at 1.0, with dual licensing
available. A fully migrated Mojo core with a Python interface at 2.0. One
approximately two-year roadmap.**


## Editorial and evidence notes

This is a planning draft, not a statement that all proposed systems are currently
implemented. The source review was static; no runtime verification or ITIL
conformance assessment was performed. Companion file:
`melder-roadmap-source-notes.md`.

The original repository roadmap and the earlier draft have not been modified.
