# Epic: Extend structural restore with application state and assisted recovery

## Metadata
- Epic ID: EPIC-2026-09-07-stateful_application_recovery
- Status: ready
- Owner: project owner; documentation executor codex
- Agent Name: unassigned
- Documentation Author: command_1, working from CommandOps; no Melder agent assignment.
- Priority: p1
- Created: 2026-09-07T19:15:12Z
- Updated: 2026-09-07T19:18:52Z
- Target Window: discussion and recovery design; implementation not selected
- Related Program/Initiative: Crystallizer recovery and CommandOps composition
- Authorization: preserve findings and opportunities; no runtime implementation or restore execution.

## Read This First

Crystallizer supplies a useful reconstruction layer: recorded native structure, replayable
definitions, selected configuration and relationships can be rebuilt in a new runtime. That gives
application recovery a world to reconstruct services into. It does not preserve the previous Python
heap, all live scopes, all workstation sessions, or suspended execution.

The owner's proposal is to build on that foundation: restore recoverable structure, run customized
application reconstruction and state-machine scripts, then potentially let an agent handle the
remaining declared gaps. Full recovery of every old object need not be the requirement. Recovering
enough of the intended application to continue meaningful work can be the requirement.

Evidence status: this epic consolidates the source inspection recorded in CommandOps on 2026-09-07.
This authoring pass did not execute a checkpoint or demonstrate a stateful recovery. Recheck relevant
source before implementation. Current findings and future opportunities are distinguished below.

Primary investigation record:
- ../priv_commandops/context_compass/tickets/tasks/2026-09-07_crystallizer_restore_object_lifetimes_task.md

Broader composition and actor discussion:
- ../priv_commandops/context_compass/tickets/epics/2026-09-07_commandops_melder_agent_execution_composition_epic.md
- ../priv_commandops/context_compass/tickets/tasks/2026-09-07_actor_execution_nexus_attachment_trace_task.md

## Problem / Opportunity

The discussion became stuck on whether saving structure has value when application instances and
their state do not automatically return. There are several different recovery subjects: definitions,
scope topology, constructed services, explicit value state and ongoing work. Crystallizer addresses
part of this problem; application recovery must declare what supplies the rest.

Without that contract, native restore completion can be mistaken for application readiness. Missing
instance bindings, callbacks, workspaces or interrupted requests may still matter when the native
stage chain finishes successfully. The opportunity is an honest composed recovery model:
- Melder reconstructs native structures it knows how to rebuild.
- Application procedures recreate necessary scopes, services, resources and relationships.
- Durable state tells replacements which identities and work they continue.
- Optional agent assistance handles declared unresolved recovery work.
- Application checks determine readiness, permitted degraded operation, or a blocked recovery.

## Owner Intent and Context

CommandOps should compose through Melder with a low floor and high ceiling. Spectrum, configuration
and bootstrap ownership are central. Spectrum may be registered after other infrastructure exists;
that does not remove the need for an explicit reconstruction strategy.

The current R&D leaning is one dynamic frame with rich features and AI enabled. Automatic mode,
multiple frames and spellframe organization remain discussion options. This epic does not freeze
topology or convert a leaning into a public API contract.

Different agents and pools remain valid, including ordinary producer/consumer applications. The
experimental actor model uses an owner thread, concurrent API work on an event loop, greenlet
residences, and graph locations that change the model context through ASE. Recovery should preserve
the selected model's logical identity and work without claiming its running stacks are checkpointed.

Nexus supplies mediated object/workstation access. A recovery agent may use it to inspect, construct,
test and repair real objects. That agent need not be mandatory in every application. Peak live
in-process modification remains a design goal; recovery control may live outside the mutable runtime.

## MRP Alignment (Most Reasonable Product)

The foundation is explicit identity, ownership, state compatibility and readiness. A small application
can use a bootstrap and a few recovery procedures; larger applications can add state owners, scopes
and migrations without changing those meanings. A small complete example should test this foundation,
not redefine CommandOps as a stateless service or force a particular agent/deployment architecture.

## Ticket Contract
- ENTRY_GATE: owner requested this epic; existing findings retained; board routes here.
- EXECUTION_BOUNDARY: document native coverage, recovery opportunities and discussion scenarios.
  Future source changes require their own concrete implementation scope.
- DEPENDENCIES: linked source investigation, composition discussion and native scope/identity work.
- EXIT_GATE: required design workstreams accepted, supported guarantees explicit, relevant evidence
  attached and owner acceptance recorded. Creating this capture does not complete the design program.
- FAILURE_ESCALATION: keep missing inputs, incompatible state and unsupported replay as explicit gaps;
  do not replace evidence with an agent's assertion of success.

## Current Findings: Capture and Replay Coverage

These findings describe the inspected checkpoint path. A replay stage can exist while rejecting a
particular input. Fresh-runtime reconstruction and loading into an existing world have different
admission/collision concerns; this table does not claim live load rewinds every active object.

| Surface | Recorded / reconstructed today | Limitation or remaining responsibility |
| --- | --- | --- |
| AethericFrame names/posture | Recorded dynamic frame posture rebuilt before books | Automatic frame emission excluded by the inspected gate |
| Spellbook configuration | Recorded properties reloaded | Rejected/backfilled properties become shortfalls; live hooks require code |
| Class/function bindings | Import or supported source reconstruction, then bind | Hydratable classification does not guarantee every target reconstructs |
| Prebuilt instances, bound methods, lambdas, callable objects | Classified replay_required | Automatic hydration skipped and shortfalls recorded |
| Normal/root conduits | Recorded roots re-conjured with structural identity translation | Old Python references do not survive replacement |
| SpellIndex members/selection | Active/staged members and selected versions replay | Required targets and anchors must exist |
| Root links and ordinary spell grants | Native link/contract verbs reconstruct relationships | Endpoint and admission requirements still apply |
| Index subscriptions | Recorded | Explicitly not replayed in the inspected path |
| Clusters | Cluster and member reconstruction exists | Leadership not replayed; auto-share does not prove exact share fidelity |
| Aether root configuration | Applied where supported | Already-configured Aether retains its configuration; callbacks need code |
| Crystallizer policy | Recorded and reported | Active recorder does not replace its policy during restore |
| MutationResearch | Configuration and supplied research composition reload | Missing, old and cleaned cases have explicit handling/shortfalls |
| Nexus root | Configuration and enabled/disabled lifecycle replay | Its crystal excludes the Rift registry |
| Rifts, rooms, workstations, active projections | No replay entity/path in the inspected chain | Reconstruct sessions, access policy and selected working bindings |
| Lesser conduit population | Live runtime relationships exist | No current checkpoint entities reconstruct that population |
| SpellSpaces, stacks, leases and versions | Runtime scope machinery exists | Prior population, membership, versions and contents not replayed |
| Scope pool helpers | Recreated with new conduit infrastructure | Old occupancy, active scopes and leases not restored |
| Creations contents | New live/disposal maps start empty | Resolve fresh instances under Existence rules; recover state separately |
| Threads, coroutines, greenlets and pending API calls | No live continuation representation | Restart/resume at declared application boundaries |
| Application state and runtime-only references | No generic state/continuation contract | Persist selected values and rebuild relationships explicitly |

Root-only recording is an explicit current boundary. SpellSpacePool can allocate spaces again, but
that does not recover an old request's space identity or contents. ConduitPool currently supplies
retention/reuse scaffolding; it does not itself construct new lesser conduits.

Creations.extract_spell_creations / restore_spell_creations is a different operation: it transfers
the same raw references between in-process stores. It does not serialize, clone or hydrate objects
from a previous process.

RestoreReport.status can be complete while shortfalls remain. Built counts describe native units
and registrations, not a recovered application-instance population. The application must decide
which omissions prevent useful operation.

## What Structural Recovery Already Buys Us

The record can preserve bindings, selected versions, roots and relationships that an application
assembled, subject to the coverage above. This matters when the graph evolves beyond its original
bootstrap, including agent-created components that were registered through supported paths.

After reconstruction, normal resolution builds the required dependency graph again. Application code
does not need handwritten construction for every dependency. It needs participation for unreplayable
targets, explicit state, runtime resources and relationships outside the recorded graph.

Useful outcomes include reconstructing a recorded world for inspection, rebuilding a selected
structural version, reproducing dynamic definitions in a candidate runtime, and reattaching durable
mission/agent state. Structure supplies a known starting point and visible gaps instead of forcing
the application to rediscover its composition after each failure.

## Missing Contracts for Stateful Recovery

### Logical inventory and identity
Record what should exist after recovery: applications, centers, missions, agents, sessions, scopes
and selected services/tools. Distinguish logical identity from newly allocated native runtime IDs.

An inventory entry could name its owner, parent, root/frame, construction recipe, state record and
essential/optional status. These are proposed fields, not existing APIs. Raw Python addresses and
borrowed references are not durable cross-process identities.

Logging each creation would help establish what existed. It would not automatically provide saved
fields, constructor inputs, resource handles or a valid continuation point. Decide whether to track
all creations or only declared recoverable participants; ephemeral objects may not justify records.

### Construction and explicit value state
Each required participant needs compatible definitions/configuration, a construction or resolution
recipe, selected value state, migration rules and postconditions. Some services are fully rebuilt by
construction. Others need mission progress, conversation state, memory, results or domain records.
Caches and transient helpers may deliberately start empty. Datastore and schema choices remain open.

### Relationships and live resources
Reconnect selected references using logical identities and native structural translation. Declare one
disposal owner and explicit borrowers. Sharing Iris or a provider does not make each consumer its owner.

Threads, loops, connections, windows and GPU resources need fresh creation or external reattachment.
Their actual affinity and lifecycle rules still apply. Saving an object name cannot recreate an open
connection or transfer ownership of a host's UI resource.

### Work continuation and external effects
Persist progress at meaningful application transitions. Resume a declared step rather than a guessed
instruction inside an old thread/greenlet stack. Rebuild ASE context from durable identity, work and
location state; saved Python execution alone would not recover provider context caches either.

A request may succeed externally before local completion is saved. Recovery needs correlation and a
choice among status lookup, safe retry, compensation, blocked uncertainty or human decision. Agent
assistance does not make an uncertain effect safe to repeat.

### Compatibility and readiness
Associate structural checkpoint identity, code/recipe versions and compatible state-store versions.
Every state update need not create a structural checkpoint, but the compatibility rule must be clear.
Independent snapshots do not automatically constitute one atomic recovery point.

Native completion is an input to application checks. Required dependencies, state invariants, missing
bindings and work-continuation rules determine whether normal admission can open.

## Proposed Recovery Composition

These are conceptual phases, not current Melder API names:

~~~mermaid
flowchart TD
    A[Minimal recovery bootstrap and compatible inputs] --> B[Native structural restore]
    B --> C[Classify report and application gaps]
    C --> D[Application reconstruction and state recovery]
    D --> E{Required checks pass?}
    E -->|yes| F[Publish permitted readiness]
    E -->|repairable work remains| G[Optional recovery agent]
    G --> D
    E -->|essential inputs unavailable| H[Blocked recovery with evidence]
~~~

1. Start enough logging, configuration, checkpoint/state access and control to perform recovery.
2. Select compatible inputs and apply prerequisites that native replay cannot replace live.
3. Restore native structure; retain its report, shortfalls and identity translations.
4. Classify the missing application work before opening normal admission.
5. Recreate required scopes, resolve services, supply unreplayable bindings and reconnect resources.
6. Load/migrate explicit state, rebuild relationships and reconcile interrupted operations.
7. If configured, let an agent perform declared repairs and record the resulting evidence.
8. Verify essential contracts and publish the application's permitted operating state.

This can serve a fresh process/container or a bounded application within an existing host. Whole-world
checkpoint load and scoped formation load are distinct native paths. A borrowed host does not become
application-owned because a recovery procedure can reach it.

## Customizable State-Machine Recovery Scripts

The owner's special restore scripts can initially be ordinary application code called by bootstrap.
A universal extension framework is not a prerequisite. Reusable library hooks can follow demonstrated
common needs. Each step should remain understandable if recovery itself stops halfway through.

| Step contract | Question answered |
| --- | --- |
| Stable identity and version | Which procedure ran, and which saved progress can it understand? |
| Preconditions | Which native structures, state records and external resources must already exist? |
| Inputs and owned outputs | What does it read, construct, adopt, borrow or replace? |
| Repeat behavior | Is retry safe, detectable as already completed, or dependent on reconciliation? |
| Completion evidence | Which observable postcondition proves the step succeeded? |
| Failure behavior | Retry, compensate, block or request assistance? |
| Durable transition | Which progress record changes, under what version/concurrency rule? |
| Cleanup | Who disposes temporary/replacement resources when a step fails? |
| Compatibility | Which code, structure and state-schema combinations are valid? |

An illustrative CommandOps recipe establishes logging/providers, restores definitions and roots,
constructs/configures Spectrum, rebuilds required centers/groups/scopes, loads mission/agent state,
reconnects workspaces and reconciles pending work before starting normal intake.

That order is provisional. Current constructors already create some descendants. Inventory replay
must not create them a second time or assign a second cleanup owner. Trace the chosen composition
before making its actual recovery recipe.

Late registration is compatible with this model. A prebuilt Spectrum binding is replay_required;
bootstrap must provide its replacement or a replayable construction definition and reconnect state.
Registration alone is not a state snapshot, but construction order need not be inverted solely to
make Spectrum participate in recovery.

## Partial Recovery Followed by Agent Assistance

Restoring a useful majority and letting an agent address remaining work is a reasonable design
option. Define a known operational subset rather than an invented percentage of objects restored.
One unavailable essential state record can block the application even if every other object rebuilds.

| Gap class | Example | Candidate handling |
| --- | --- | --- |
| Already rebuilt | Recorded root and class binding | Verify and use |
| Script-reconstructible | Live-instance binding or known callback | Run a declared recovery recipe |
| Rebuildable transient | Cache, scratch scope, reconnectable client | Construct fresh and record the intended loss |
| Agent-addressable | Missing optional adapter with retained source and testable contract | Permit repair and validate |
| Deliberately omitted | Abandoned experiment or disposable scratch | Record omission; continue if policy allows |
| Essential but unavailable | Lost business state or absent credentials | Obtain real inputs; block dependent work |
| External outcome unknown | A request may already have changed another system | Reconcile before retry or continuation |

A recovery agent needs a functioning starting environment: model access, evidence, permitted actions
and a work interface. It cannot be the only mechanism responsible for building every prerequisite of
its own first turn. A minimal recovered slice or an external controller can supply that starting point.

Useful agent work could include inspecting shortfalls, executing known procedures, reconstructing
reproducible tools, repairing compatible bindings, testing candidates and explaining unresolved
assumptions. Successful repairs can become repeatable reviewed recipes for future restarts.

The agent cannot restore data that was never retained, establish an unknown remote outcome by
assertion, or replace application invariants with its judgment. Readiness must be based on declared
checks. An optional missing feature may permit degraded operation; missing essential state may not.

Peak recovery can allow real in-process modifications. Its authority and acceptable failure domain
should match the intended application. A separate controller can retain restart and recovery access
if the editable runtime breaks itself. Frames alone do not supply process-memory containment or
independently protected recovery history.

## Improvement Opportunities

| Opportunity | Value | Design choice still needed |
| --- | --- | --- |
| Explicit coverage/shortfall policy | Know what native complete permits | Fatal, repairable, optional or informational omissions |
| Logical creation inventory | Know which meaningful objects should return | All creations versus declared participants |
| Lesser/SpellSpace structure records | Preserve more active scope topology | Parent, ownership, naming and lease meaning after restart |
| Application state participation | Recover selected values through an explicit seam | Melder hooks versus application bootstrap/datastore ownership |
| Relationship reconstruction | Avoid stale references and double ownership | Stable logical identities and adoption rules |
| Workspace/session recipes | Recover useful agent working context | Reproducible bindings versus disposable scratch |
| Restartable recovery steps | Recover recovery itself | Step versions, retry, completion and progress storage |
| Agent-assisted gap handling | Diagnose and repair cases beyond fixed recipes | Available inputs, authority and independently testable outcomes |
| Fresh-runtime rehearsal | Discover omissions before process loss | Isolated verification without repeating real effects |
| Semantic recovery comparison | Show what returned, changed or stayed absent | Application checks beyond native object counts |

Named lesser recovery already has related design work. Its epic calls for structural persistence
while excluding created-instance state. Coordinate with that work rather than designing competing
naming, ownership or lesser-replay semantics:
- context_compass/tickets/epics/2026-09-06_named_lesser_conduit_discovery_epic.md
- context_compass/tickets/tasks/2026-09-07_named_conduit_implementation_map_task.md

The existing parallel-restore/ULID epic is related to identity translation, journal order and scheduling.
Recheck its implementation state before touching those contracts; this capture does not take it over:
- context_compass/tickets/epics/2026-07-18_parallel_restore_ulid_identity_epic.md

## Scenarios for Discussion

### Mission after process loss
Restore its roots and required scope, construct a replacement mission, load durable logical identity
and progress, reconcile an in-flight request, then resume a declared transition. The old greenlet
stack is not an input. Decide which actor state and ASE location/context must return.

### Workshop with partially reproducible tools
Replay recorded definitions and create a new workspace. A missing callable object can be rebuilt by
code or an agent if its source, recipe and checks were retained. If no reproducible inputs exist,
report the loss. A prior in-memory object is not evidence that reconstruction is possible.

### Partial application with an optional missing feature
Core state/services recover while an experiment does not. Allow a declared degraded state if essential
checks pass. Repair may proceed concurrently where dependencies permit; operations requiring the
missing feature remain unavailable until its checks pass.

### Successor runtime and self-upgrade
An external controller constructs/tests a successor from structure, code and compatible state. The
agent can build the candidate. Cutover still requires admission, state compatibility and readiness
rules; selecting an old code version does not automatically reverse migrated state.

## Goals (Outcomes)
- Preserve current restore value, limitations and evidence without overclaiming completeness.
- Define understandable native restore, application state and recovery-script responsibilities.
- Support useful partial recovery and optional agent assistance.
- Preserve logical identity, ownership and application flexibility across replacement runtime objects.

## Non-Goals (Explicit Exclusions)
- Full Python heap, OS thread, coroutine or greenlet serialization.
- Automatic recovery of any object solely because its creation was logged.
- Selection of a database, public recovery API, agent type or final frame topology.
- Source changes, deployments, actual restore execution or runtime tests in this capture.
- Claims that structural checkpoints undo external effects or prove hostile-code containment.

## Scope Boundaries
- In scope: recovery coverage, state/identity contracts, script customization and assisted recovery design.
- Out of scope: unrelated fixes or taking ownership of linked active design programs.
- Future implementation: select one concrete scenario and its scoped contracts before runtime changes.

## Constraints / Assumptions
- Recorded inputs, compatible source and required application state must remain available.
- Native Existence and load/admission rules still govern reconstructed objects and structures.
- Application-defined logical identity must survive replacement of native runtime IDs.
- Agent assistance is optional and requires a functioning starting environment.
- This epic records prior source inspection; fresh-runtime recovery remains unverified.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: owner-requested discussion capture prepared; design and implementation remain open.

## Requirements (Functional + Non-Functional)
- Distinguish definitions, scope topology, instances, value state and execution progress.
- Respect native load/lifetime/identity contracts and one explicit disposal owner.
- Report gaps per meaningful participant and define repeated/interrupted recovery behavior.
- Check code/structure/state compatibility and external outcomes before dependent work resumes.
- Keep simple applications usable with a bootstrap and explicit procedures.
- Make agent repair depend on real inputs and checkable outcomes.
- Avoid unclaimed atomicity across independent checkpoint and state stores.

## Success Metrics
- One scenario specifies exactly what survives, what is rebuilt and what may be absent.
- Every essential participant has a recovery contract or a visible blocker.
- Readiness is independent of native stage completion.
- Interrupted recovery has a defined next action rather than blind repetition.
- Another session can resume this design from the epic and its evidence.

## Milestones (Track Progress)
- [x] Capture native coverage and the owner's partial-recovery proposal.
- [ ] Select the first stateful application scenario.
- [ ] Define identity, state, recovery steps and readiness contracts.
- [ ] Coordinate native scope/identity changes with related work.
- [ ] Evaluate optional agent repair with concrete inputs and checks.
- [ ] Verify selected guarantees in an authorized implementation/rehearsal lane.

## Stories (Required to Complete)
Proposed workstreams only; no child tickets or assignments are created by this capture.
- [ ] Coverage/report story: classify native outcomes and required shortfalls.
- [ ] State/identity story: define one recoverable participant and its compatible state.
- [ ] Recovery-script story: define restartable construction, migration, attachment and failure steps.
- [ ] Scope/session story: choose which lessers, SpellSpaces and workspaces need reconstruction.
- [ ] Assisted-recovery story: define the agent starting environment and permitted testable repairs.
- [ ] Rehearsal story: verify success, interruption, missing inputs and uncertain external effects.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Preserve the source investigation and discussion in Melder's recovery epic.
- [ ] Recheck relevant source and related design status before implementation.
- [ ] Turn illustrative steps into reviewed contracts for one selected application.
- [ ] Record owner decisions and link scoped work as responsibilities become concrete.

## Acceptance Criteria (Epic Done)
- [ ] Owner accepts selected recovery guarantees and exclusions.
- [ ] Scenario maps essential participants to native replay, scripts, reconstruction or missing inputs.
- [ ] Logical identity, state compatibility, ownership and continuation are specified.
- [ ] Shortfalls and readiness are connected by explicit application policy.
- [ ] Agent assistance, if selected, has a viable starting environment and verifiable outcomes.
- [ ] Runtime guarantees have relevant implementation/rehearsal evidence.
- [ ] Required workstreams are accepted; capture alone does not close the design epic.

## Risks / Mitigations
- Native complete mistaken for readiness: classify gaps and check essential application invariants.
- Topology saved without useful state: specify both structure and value-state participants.
- Repeated external effects: correlate requests and reconcile uncertain outcomes.
- Duplicate constructors/disposers: trace bootstrap side effects and adopt one owner.
- Agent depends on broken services: provide a minimal recovered or external starting environment.
- Repair damages recoverability: retain usable inputs and control of recovery attempts.
- Incompatible recipes/state: version procedures and rehearse valid combinations.

## Applicable Anti-Patterns
- [ ] No arbitrary-memory or execution-stack recovery claims.
- [ ] No essential loss hidden behind complete status or recovery percentages.
- [ ] No competing scope/identity design introduced without consulting related work.
- [ ] No proposal presented as owner-selected implementation.
- [ ] No closure while required workstreams remain unaccepted.

## Validation / Test Approach
This capture requires section, link, evidence-range, board-route and Markdown checks only.
Runtime tests, coverage and checkpoint replay: Not run.

Later authorized work should use a fresh runtime and prove semantic outcomes: expected roots and
bindings, required scope reconstruction, preserved logical identity/value state, replay_required
recipe participation, safe interrupted recovery, optional versus essential omissions, and rejected
incompatible state. An agent repair must meet the same application checks as a scripted recovery.

## Rollout / Adoption Plan
1. Choose one mission/service and list what must survive its process.
2. Map native replay and remaining application responsibilities to that list.
3. Implement the selected scope after authorization.
4. Rehearse reconstruction and failures.
5. Extract reusable library support from demonstrated common needs.

## Open Questions
- What is the first meaningful application state machine to recover?
- Which scopes/workspaces persist logically, and which are recreated on demand?
- Should Melder expose state participants or initially leave scripts to application bootstrap?
- Which recipe represents late Spectrum registration without duplicate ownership?
- Which shortfalls block this application or permit degraded operation?
- How are compatible structural and state-store recovery points selected?
- Where does recovery progress live if recovery itself crashes?
- Which uncertain outcomes require human input?
- What minimal services let a recovery agent start?
- Which repairs should become repeatable recipes, and who verifies them?
- Which records/controller functions must survive failure of the mutable runtime?

## Decision Log
- Owner requirement: store findings and opportunities in Melder's ContextCompass.
- Owner proposal: customized state-machine scripts and useful partial reconstruction.
- Owner proposal: an agent may take over remaining work after sufficient infrastructure returns.
- Existing finding: structural completion is not full stateful application recovery.
- Open: APIs, datastore, participant model, topology and deployment.
- No runtime implementation or test execution performed in this capture.

## Evidence Map
Ranges are retained from the linked source investigation. They are reopening targets for future
implementation and evidence of the inspected baseline, not new runtime validation.

| Source range | Finding |
| --- | --- |
| src/melder/crystallizer/persistence/persistence_crystal.py:78-184 | Detached journal/twin representation |
| src/melder/crystallizer/crystal_loader_system/restore_engine.py:649-760 | Native replay stage chain |
| src/melder/crystallizer/crystal_loader_system/restore_engine.py:1739-1880 | Book/binding/root reconstruction |
| src/melder/crystallizer/crystal_loader_system/restore_engine.py:2455-2538 | Hydration and replay-required handling |
| src/melder/crystallizer/crystals/spell_crystal.py:291-299 | Hydratable classification |
| src/melder/crystallizer/crystals/spell_crystal.py:938-1039 | Actual target-kind classification |
| src/melder/aether/conduit/creations/creations.py:96-148 | Initially empty live/disposal stores |
| src/melder/aether/conduit/creations/creations.py:376-514 | In-process transfer of raw references |
| src/melder/aether/conduit/meld/conduit_meld.py:143-447 | Normal resolution dispatch |
| src/melder/aether/conduit/meld/conduit_meld.py:458-608 | Existence-directed reuse lookup |
| src/melder/aether/conduit/conduit.py:326-466 | Helper construction and normal-root crystal emission |
| src/melder/crystallizer/crystals/conduit_crystal.py:9-36 | Root-only structural contract |
| src/melder/crystallizer/crystal_loader_system/restore_engine.py:1141-1221 | Entity-kind folding boundary |
| src/melder/crystallizer/crystals/nexus_crystal.py:75-107 | Nexus root excludes Rift registry |
| src/melder/crystallizer/crystal_loader_system/restore_engine.py:1320-1548 | Hosted policy/research/Nexus recovery |
| src/melder/crystallizer/crystal_loader_system/restore_engine.py:2254-2452 | Cluster/contract replay and shortfalls |
| src/melder/aether/conduit/conduit_pool.py:62-161 | Lesser retention/reuse scaffold |
| src/melder/aether/conduit/spell_space/spell_space_pool.py:74-236 | Live SpellSpace allocation/reuse |
| src/melder/aether/conduit/spell_space/spell_space.py:112-208 | Live scope state/identity |
| src/melder/crystallizer/crystal_loader_system/restore_engine.py:310-375 | Completion independent of shortfalls |
| src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:462-507 | Dynamic-only frame emission gate |

## Dependencies / External References
- Primary investigation and composition/actor records are linked near the top.
- Related native naming/scope/identity work is linked under Improvement Opportunities.
- No new external research required or claimed by this capture.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none; the epic is the durable discussion artifact.
- DISPOSITION: none
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: structural restore, scope inventory, state recovery, scripts and assisted repair.
- IF_UNKNOWN: none; implementation questions remain explicit.

## Notes
- DATETIME: 2026-09-07T19:15:12Z
  TYPE: DECISION
  CLAIM: Owner requested this recovery epic, including state-machine scripts and possible agent
    assistance after partial reconstruction. Design discussion remains separate from implementation.
  EVIDENCE:
  - ../priv_commandops/context_compass/tickets/tasks/2026-09-07_crystallizer_restore_object_lifetimes_task.md:19-33
  IMPACT: The discussion now has a Melder-owned continuation point.
  NEXT: Select one stateful application scenario and classify its essential recovery participants.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-07T19:15:12Z
  TYPE: FACT
  CLAIM: The linked source investigation records selective native replay, empty new creation stores,
    absent lesser/SpellSpace/Rift population replay and complete reports that can retain shortfalls.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:310-375
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1141-1221
  - src/melder/aether/conduit/creations/creations.py:96-148
  IMPACT: Explicit application state, reconstruction procedures and readiness supplement native replay.
  NEXT: Map the first scenario onto the coverage table and declare remaining responsibilities.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-07T19:18:52Z
  TYPE: MEASURE
  CLAIM: Documentation checks resolved 25 evidence ranges and six local links. The staged draft and
    copied Melder epic matched by SHA256. Required core sections, diagram fences and whitespace were
    checked; scoped board/mailbox git diff --check passed. No runtime or coverage tests were run.
  EVIDENCE:
  - context_compass/tickets/epics/2026-09-07_stateful_application_recovery_epic.md:430-480
  IMPACT: The findings are stored and routed in Melder as a discussion epic, with source evidence
    and proposed recovery contracts separated. Runtime recovery guarantees remain future work.
  NEXT: Discuss one stateful mission/service recovery scenario with the owner.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared for the completed design scope.
- [ ] Acceptance criteria confirmed by owner.
- [ ] Applicable anti-pattern checks clear or escalated.

## Noting Behavior
- Distinguish owner proposals, source findings and selected contracts.
- Keep program decisions here and tactical traces in linked tasks.
- Do not convert optional agent assistance into a universal application requirement.

## Context / Handoff Summary
The requested findings are stored here. Native replay reconstructs supported structure/definitions
and selected control-plane state. Application instances/state, active scopes/sessions and execution
continuations need explicit treatment.

The proposed composition is native restore, application reconstruction/state-machine procedures,
optional agent assistance for declared gaps, and application readiness checks. Useful partial recovery
is a legitimate application-defined result; recreating every old object is not assumed.

Keep the agent starting environment, essential missing inputs, external outcomes, repeat behavior,
ownership and identity explicit. Coordinate lesser-structure additions with existing named-lesser
work. No source code, deployment, runtime restore or tests were performed for this capture.

NEXT SINGLE STEP: choose one mission/service example and classify required participants as native
replay, scripted construction/state load, transient reconstruction, agent-addressable repair,
deliberate omission or blocked input.
