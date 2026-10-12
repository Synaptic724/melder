# Epic: Service methods and Melder-hosted pools - let an owning service supply, lease and take back what Melder injects

## Metadata
- Epic ID: EPIC-2026-10-05-melder_services_and_pools
- Status: in_progress
- Owner: user
- Agent Name: melder_1
- Priority: p1
- Created: 2026-10-05T15:35:41Z
- Updated: 2026-10-12T21:15:14Z
- Target Window: 2026-Q4
- Related Program/Initiative: MelderOps Iris logger churn (priv_commandops TASK-2026-10-05-channel_logger_pooling)

## Problem / Opportunity
MelderOps builds one Iris ChannelLogger per object: about 40 classes (agents, activities, missions, groups, agent
pools, operational memory, about 20 synchronization primitives) meld a fresh logger into Iris's lesser conduit
("iris_channel_loggers") at construction and destroy it at cleanup. Measured on MelderOps 0.1.1060 with melder
0.2.8226 (free-threaded CPython 3.14.8, 2 vCPU):
- Creating one logger through the meld takes 74-82 us and its cleanup (detach + Conduit.purge) 6.4-6.7 us; built
  directly without Melder, 10.7 us and 1.5 us. A Latch spends about 90% of its create-and-cleanup cost on its logger
  (98 us with its own logger, 9.6 us when handed one). The meld runs under the Iris lock, so threads queue on it.
- About two thirds of each meld is one uncached call: Meld._check_contracts_and_force_revalidation runs
  Meld._iter_spell_contract_defaults, which calls inspect.signature(call_target, annotation_format=FORWARDREF) on
  every meld, even for spells with no SpellContract defaults. Memoizing it per call target (measurement-only patch)
  cut the logger create from about 78 to about 21 us. The same code is in this repository (0.2.8227).

The owner then asked for a pool, and the discussion showed the real gap is structural: Melder cannot let an owning
service supply the objects it injects.
- Method, lambda and existing-object bindings are forced to Existence.unique ("per-scope construction is
  meaningless for them"), so a method binding runs once per frame: never per consumer, never with the consumer's
  context, and with no release hook.
- So Iris cannot be the provider of loggers. Melder either builds a blank ChannelLogger itself (the consumer fills in
  its identity afterwards, and the logger lands in the root, not Iris's conduit) or each consumer pulls one from Iris
  by hand and destroys it itself. A pool cannot work cleanly because only the consumer knows when to give one back,
  and some consumers hand their logger to a child that destroys it too.
- Melder already pools, but only its own kernel objects: AbstractElasticPool (elastic stretch/decay sizing),
  SpellSpacePool (a lease flag: a released space refuses meld and purge) and ConduitPool (a scaffold).

Other containers have both missing primitives: Autofac's PooledInstancePerLifetimeScope (instances come from the pool
on resolve and go back when the lifetime scope ends; IPooledComponent hooks; custom policies), EF Core's
AddDbContextPool (reset and returned when the DI scope is disposed), CDI producer methods that receive an
InjectionPoint, Guice's built-in Logger binding named after the class it is injected into, dishka's @provide methods
with generator finalization when a scope exits, and di's scopes with teardown on exit.

## MRP Alignment (Most Reasonable Product)
Give Melder the two general primitives mature containers have, instead of a logger-specific workaround: service
methods (a provider method on a live owned object, resolved per injection with the consumer's context and a release
path) and a pooled lifetime Melder hosts for any binding (leases end with the scope that took them). Fix the per-meld
signature scan first because it is cheap, behavior-neutral and speeds up every meld. Loggers are the first consumer,
not a special case.

## Ticket Contract
- ENTRY_GATE: the owner answers the open questions below (each recorded in the Decision Log) and the stories for the
  first milestones are drafted.
- EXECUTION_BOUNDARY: the Melder kernel - Spellbook.bind (a new binding kind and/or Existence member), Meld /
  ConduitMeld / SpellSpaceMeld resolution, the Creations stores and disposal, reuse of AbstractElasticPool - plus their
  docs and tests. Excluded: MelderOps adoption (Iris as the logger service, Spectrum's own logger), tracked in
  priv_commandops; any change to the meaning of the six existing Existence modes.
- DEPENDENCIES: AbstractElasticPool and the SpellSpacePool lease pattern; bind as the crystallizer's recording moment
  and the content-derived spell_id (new binding kinds must fingerprint and record deterministically).
- EXIT_GATE: required stories accepted; a MelderOps prototype (Iris supplying pooled ChannelLoggers through the new
  primitives) measured against the 74-82 us path; docs and AGENT_PURPOSE text updated; board/closure sync done.
- FAILURE_ESCALATION: DECISION_REQUEST when a design changes an existing Existence mode, the spell_id fingerprint,
  crystallizer custody, or the thread-confinement contract of spellspaces.

## Goals (Outcomes)
- A meld of a spell resolves its SpellContract defaults once per call target, not once per meld.
- Service methods: a binding whose provider is a method on a live owned object (for example Iris.provide_logger),
  invoked per resolution under a lifetime other than unique, given an injection context (who is asking), with an
  optional release method Melder calls when the lease ends.
- A pooled lifetime: Melder hosts an elastic pool per pooled binding, acquires on meld, returns on scope end through
  reset/return hooks, destroys overflow, and reclaims every lease and idle object when the owner or conduit retires.
- A defined "service scope": what ends a lease, and in which order leases are returned before their pools retire.

## Non-Goals (Explicit Exclusions)
- No change to the behavior of unique, unique_per_conduit, many, unique_per_conduit_cluster,
  unique_per_conduit_lineage or unique_per_spell_space.
- No MelderOps code in this epic.
- No general-purpose pool API for user code outside bindings unless the owner decides otherwise.
- No async provider or release methods and no thread-local conduit types in the first implementation; they come later
  (Decision Log), so the design must leave room for them.

## Scope Boundaries
- In scope: the signature-scan memo; service-method bindings; a pooled lifetime; service-scope semantics; tests,
  benchmarks and docs for each.
- Out of scope: MelderOps adoption (priv_commandops), LogXide, redesigning existing lifetimes.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: opened from the owner's MelderOps discussion; stays draft until the open questions are decided.
- from_state: draft
- to_state: in_progress
- transition_reason: the owner chose to work from this epic with melder_1 and set the pool direction in chat
  (2026-10-11): pools as an Existence family that Creations services, configured on the Spell, with limits,
  exhaustion and elasticity; design discussion first ("lets think about this stuff a bit please").

## Success Metrics
- After the first resolution, a meld of a spell without SpellContract defaults calls inspect.signature zero times
  (counted in a test); the MelderOps logger create drops to about 25 us or less on the reference VM.
- A pooled lease of a ChannelLogger-like binding costs about 5 us or less to acquire and about 1 us to return.
- A lease used after it was returned is refused (or provably inert, per the decided contract) instead of acting for
  the next holder.
- No leaks: weakref tests show every lease and idle object reclaimed at conduit and frame teardown.

## Requirements (Functional + Non-Functional)
- Functional: memoize Meld._iter_spell_contract_defaults per call target, invalidated on rebind; bind a service method
  with an allowed lifetime and optional release method; pass an injection context; pooled lifetime with reset/return
  hooks and elastic sizing; leases carry a released flag; deterministic return order at scope end.
- Functional: a service method is keyed by its return annotation and admitted to single-annotation resolution (today
  a method spell is keyed by its function name and kept out of it); release is an explicit call - the product's
  disposal method recycling it, or an owner release method - never generator (yield) finalization.
- Non-functional: safe on free-threaded CPython 3.14 (deque hand-off, advisory counters as in AbstractElasticPool, no
  conduit lock held while a provider method runs); new binding kinds fingerprint and record deterministically; every
  public surface documented with AGENT_PURPOSE.
- Non-functional, async-ready (async itself comes later): async arrives as new conduit types with thread-local
  behavior - an event loop runs on one thread, and MelderOps runs parallel asyncio as one loop per thread - so pools
  and service methods must work when a conduit is bound to one thread or loop and must not assume every conduit is
  shared across threads; no blocking lock is held across a provider or release call; the binding API leaves room for
  async def provider and release methods.

## Constraints / Assumptions
- MelderOps consumers make their identity (a ULID) in their own constructors, after their dependencies are injected,
  so a service may need either a Melder-assigned identity in the injection context or a deferred initialize step.
- Method and lambda bindings stay forced to unique; service methods are a deliberate new binding kind, not a
  loosening of that rule.

## Dependencies / External References
- Melder: src/melder/aether/conduit/meld/meld.py:1271-1386 (contract check and signature scan);
  src/melder/aether/spellbook/bind/bind.py:1105-1160 (method/lambda/existing-object bindings forced to unique);
  src/melder/aether/spellbook/existence/existence.py:1-138; src/melder/utilities/general_base/abstract_elastic_pool.py;
  src/melder/aether/conduit/spell_space/spell_space_pool.py:49-58 (lease flag rationale);
  src/melder/aether/conduit/conduit_pool.py:39 (scaffold).
- priv_commandops: context_compass/tickets/tasks/2026-10-05_channel_logger_pooling_task.md (measurements, facts,
  owner decisions); receipts in context_compass/artifacts/2026-10-04_logxide_logging_migration/perf2/logger_pool/
  (cost_1060.txt, meld_profile_1060.txt, di_precedents.txt, probe_logger_cost.py, profile_meld.py).
- External: https://autofac.readthedocs.io/en/latest/advanced/pooled-instances.html ;
  https://learn.microsoft.com/en-us/ef/core/performance/advanced-performance-topics ;
  https://docs.jboss.org/weld/reference/latest/en-US/html/injection.html ;
  https://github.com/google/guice/wiki/BuiltInBindings ; https://dishka.readthedocs.io/en/stable/provider/provide.html ;
  https://adriangb.com/di/0.79.2/scopes/

## Milestones (Track Progress)
- [ ] Milestone 1: Signature-scan memo - lands alone, no behavior change, meld benchmark before/after recorded.
- [ ] Milestone 2: Service-method design accepted - binding API, allowed lifetimes, injection context, release hook.
- [ ] Milestone 3: Pooled lifetime and service-scope design accepted - pool ownership, hooks, lease flag, teardown
      order.
- [ ] Milestone 4: Service methods and pooled lifetime implemented with tests, stress tests and docs.
- [ ] Milestone 5: MelderOps prototype measured - Iris supplies pooled loggers; Spectrum's logger decided.

## Stories (Required to Complete)
- [ ] Story: STORY-TBD-meld_contract_scan_memo - memoize the per-meld SpellContract default scan
- [ ] Story: STORY-TBD-service_method_bindings - provider methods on owned objects with injection context and release
- [ ] Story: STORY-TBD-pooled_existence - a Melder-hosted elastic pool per pooled binding, with lease flags
- [ ] Story: STORY-TBD-service_scope - what ends a lease and the return order before pools retire
- [ ] Story: priv_commandops (TBD) - Iris as the logger service; Spectrum's own logger

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-TBD-meld_contract_scan_memo
- [ ] Task: Complete story STORY-TBD-service_method_bindings
- [ ] Task: Complete story STORY-TBD-pooled_existence
- [ ] Task: Complete story STORY-TBD-service_scope
- [x] Task: TASK-2026-10-12-make_kernel_pools_elastic - the elastic retention the pooled backend reuses (0.2.8234)
- [ ] Task: Benchmark meld and lease costs on the reference VM before and after each milestone.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- Every milestone's criteria met with recorded evidence, and the success metrics above reached.
- The MelderOps prototype shows the per-object logger cost cut against 74-82 us create plus 6.4-6.7 us cleanup.
- The owner accepts the design and the walkthrough.

## Risks / Mitigations
- A stale handle acts for the next holder after its lease is reissued (for loggers: records under another object's
  identity) -> released flag checked on use, documented contract, and MelderOps fixes parent-to-child logger sharing
  during adoption.
- State leaks between leases (EF Core's caveat) -> a mandatory reset hook and tests that cover identity, overrides
  and caches.
- Teardown order -> pools drain before their conduit or frame retires; disposal paths stay idempotent when Melder's
  own disposal calls cleanup again.
- Free-threading contention -> deque-based pools and advisory counters; no conduit lock held across provider methods.
- Custody and fingerprinting -> the new binding kind records at bind and gets a deterministic spell_id.
- Scope creep into a general DI redesign -> limited to the memo plus the two primitives and service-scope semantics.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Unit tests per primitive; free-threaded stress tests (concurrent acquire/return, return during teardown); weakref
  leak tests at conduit and frame teardown; meld and lease benchmarks; the MelderOps A/B against 0.1.1060.

## Rollout / Adoption Plan
- Milestone 1 ships alone in the next Melder release. Service methods and the pooled lifetime are opt-in binding
  options. MelderOps adopts them after a Melder release that contains them.

## Open Questions
- 1) Pool owner: does Melder host the pool per binding, or does the service own its pool while Melder only calls its
  acquire and release methods?
- 2) What ends a lease: the consumer's disposal (Melder returns what it injected into it), spellspace exit, conduit
  retirement, or an explicit release?
- 3) Injection context: which of the requesting binding, the consumer class, the conduit and the spellspace does a
  service method receive, and can Melder assign the consumer's identity before construction so the service can stamp
  it?
- 4) Which lifetimes may a service method use: many, unique_per_conduit, unique_per_spell_space?
- 5) Stale-lease behavior: refuse loudly (the SpellSpace pattern) or provably inert (a logger call must never raise)?
- 6) MelderOps side: is Spectrum's own logger removed and handled natively, or leased like any consumer and returned
  before Iris retires its conduit?

## Decision Log
- 2026-10-12: fix the elastic retention of the kernel pools first, proven by gauntlet runs before and after
  (1-3 threads, then a 20-thread maximum on the owner's machine). The owner: "shells are not cheap a conduit is
  very expensive to build" ... "experiment prove its good then lets do it, then prepare a big test before you
  do the codechange on my computer with 20 threads and lets push it to the max baseline, then codechange and
  test again".
- 2026-10-11: a new Existence member, `pooled_spell`, extended through everything; Creations maintains the pools
  in conduits and spellspaces; the ConduitPool / SpellSpacePool elastic system is reused as it is; users configure
  a pooled spell, including a limit that raises; scope rank between unique_per_spell_space and many. The owner:
  "I never said use many, I said make a new existence, called pooled_spell and thats it thats the point we then
  extend everything and we allow users to configure a spell thats pooled in specific ways and resolution matches
  that process and they can even have a limit that throws an exeception" ... "a pooled object should be more
  significant than a many object but less significant than a unique_per_spellspace so resolution order still
  permits it lets discuss these ideas and trade offs".
- 2026-10-11: pools live in the existing machinery, not in a new service object. The owner: "I think the last time we
  talked about this, you suggested a different service kinda like a spellspace, but I'm thinking we just extend melder
  so that the creations system can service a new kind of object, and we extend the existence framework to allow for
  pools and we can have different kind of pool configurations that can be managed on the spell object, and we can even
  introduce concepts like exhaustion and limits or elasticity". Then: "lets think about this stuff a bit please" -
  design discussion before any story.
- 2026-10-05: async arrives later as conduit types with thread-local behavior, replacing the per-execution-context
  tracking suggested in the async entry below. The owner: "it just means providing more conduit types that have
  threadlocal behavior because async generally is single threaded but I have parallelized asyncio in melderops ... So
  a conduit would have some unique properties to a thread and support more concrete async behaviors but this is for
  later not really right now".
- 2026-10-05: Melder-hosted pools are a priority and service methods are manageable. The owner: "Anyhow its manageable
  thats the point on the pool side melder is extremely fast so it being able to host objects like a pool is a big win".
- 2026-10-05: async is not in the first implementation but will be supported later. The owner: "im hesitant on
  supporting async right now but I will support it normal async and parallelized asyncio so its a good move". The
  design must not block it (Requirements: async-ready).
- 2026-10-05: no generator (yield) finalization. The owner: "Im not a fan of the yield approach because the stack needs
  to be small"; release is an explicit method call.
- 2026-10-05: the owner opened this epic from the MelderOps logger-pool discussion to implement it in Melder; the
  MelderOps pool is held until these primitives exist (priv_commandops TASK-2026-10-05-channel_logger_pooling).

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/melder_object_pools_20261011/ (design probes and their run logs)
  - the MelderOps receipts live in priv_commandops (see Dependencies / External References)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - service methods and pooled lifetimes in Melder
- IF_UNKNOWN: ask user before implementation

## Notes
- DATETIME: 2026-10-05T15:35:41Z
  TYPE: PLAN
  CLAIM: Opened at the owner's request ("Make an epic in melder with this context as so that we can try to implement
    it") from the MelderOps ChannelLogger pool discussion: memoize the per-meld signature scan, add service methods
    and a Melder-hosted pooled lifetime, then let MelderOps adopt them for Iris loggers. The six open questions above
    gate the design stories.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:1271-1386
  - src/melder/aether/spellbook/bind/bind.py:1105-1160
  - src/melder/utilities/general_base/abstract_elastic_pool.py:290-345
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:49-58
  IMPACT: Gives the logger pool a general home in Melder instead of a MelderOps-only workaround.
  NEXT: Owner answers the open questions; then draft STORY-TBD-meld_contract_scan_memo first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-10-05T15:35:41Z
  TYPE: MEASURE
  CLAIM: MelderOps 0.1.1060 with melder 0.2.8226: a ChannelLogger meld costs 74-82 us to create and 6.4-6.7 us to clean
    up; two thirds of the meld is inspect.signature in Meld._iter_spell_contract_defaults; memoized, the create is
    19-23 us; a measurement-only pool reuses a logger for 8.6-8.9 us plus 0.9 us (create figures include 4-7 us for
    the test registrant's ULID).
  EVIDENCE:
  - priv_commandops: context_compass/artifacts/2026-10-04_logxide_logging_migration/perf2/logger_pool/cost_1060.txt:1-40
  - priv_commandops: context_compass/artifacts/2026-10-04_logxide_logging_migration/perf2/logger_pool/meld_profile_1060.txt:1-63
  IMPACT: Sets the baseline the milestones are measured against.
  NEXT: Re-measure the meld against this repository's current source before Milestone 1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-10-05T16:04:39Z
  TYPE: FACT
  CLAIM: Melder already runs method spells through the same execution plan as class spells; three things keep a method
    from serving as a per-scope provider: bind forces method and lambda spells to Existence.unique; a method spell's
    type key is its function name, not its return type; and single-annotation resolution passes
    require_class_spell=True, which excludes METHOD and LAMBDA spells (collection resolution admits them). Service
    methods therefore need a bind permission, return-type keying with single-socket admission, an injection context,
    and a release path. The owner ruled out yield-based finalization (Decision Log).
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:1149-1158
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:261-278
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:431-438
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:628-690
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:706-745
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1084-1096
  IMPACT: Scopes STORY-TBD-service_method_bindings to bind and Phase 3 resolution plus the injection context; the call
    path itself exists.
  NEXT: Owner answers the open questions; draft the service-method story with these anchors.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-05T16:10:00Z
  TYPE: DECISION
  CLAIM: The owner confirmed the direction: Melder-hosted pools are a priority ("melder is extremely fast so it being
    able to host objects like a pool is a big win"), service methods are manageable, and async (plain asyncio and
    parallel asyncio) comes later, so the first implementation is synchronous but async-ready. The main constraint
    that follows: Melder's managed spellspace stack is deliberately per thread (threading.local, chosen over
    ContextVar objects), and asyncio tasks interleave on one thread, so leases and the active service scope must not
    be tracked by thread.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space_thread_state.py:10-30
  - src/melder/aether/conduit/spell_space/spell_space_thread_state.py:65-95
  IMPACT: Adds the async-ready requirement and the async non-goal; open question 2 (what ends a lease) must be
    answered without thread identity.
  NEXT: Owner answers the open questions; Milestone 1 (signature-scan memo) can start independently.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-05T16:28:09Z
  TYPE: DECISION
  CLAIM: The owner corrected the async direction: async support means new conduit types with thread-local behavior,
    because an event loop runs on one thread and MelderOps runs parallel asyncio as one loop per thread; such a
    conduit has properties unique to its thread and supports more concrete async behaviors. This supersedes the
    previous note's constraint that leases must not be tracked by thread - the per-thread spellspace design fits this
    model. Tasks interleaving on one loop inside such a conduit are left to those later async behaviors. Not part of
    the first implementation.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space_thread_state.py:65-95
  IMPACT: The async-ready requirement now asks only that pools and service methods work with thread-bound conduits;
    no change to how the first implementation tracks scopes.
  NEXT: Owner answers the open questions; no story is drafted until the owner asks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T22:37:13Z
  TYPE: DECISION
  CLAIM: Owner, chat 2026-10-11: work from this epic with melder_1 (taken over from opus_command_0). Direction for
    the pool: no separate service or scope object; Creations services a new kind of object, the Existence framework
    gains pooled lifetimes, pool configurations (limits, exhaustion, elasticity) are managed on the Spell. Service
    methods and the signature-scan memo stay in the epic, unordered for now. The owner asked to think it through
    before anything is drafted: the next step is a design discussion grounded in Existence, Creations, the scope
    exits and AbstractElasticPool as they are today.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-05_melder_services_and_pools_epic.md:208-214
  IMPACT: Replaces the "service scope" idea (Goal 4, STORY-TBD-service_scope) with pooled existences inside Creations;
    the open questions are re-framed around Existence and the Spell's pool configuration.
  NEXT: Read existence.py, the Creations stores and scope-exit disposal, AbstractElasticPool and the scope-ordering
    validation, then bring the owner a design sketch with the decisions it needs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-11T22:41:03Z
  TYPE: FACT
  CLAIM: What the owner's direction lands on today. (1) An Existence member is pure routing - it picks which Creations
    store holds an instance (`SitePlanEmission._route`: conduit, spellspace, lineage root, cluster leader, the spell's
    owner store); the enum caches nothing. (2) A scope ends by retiring its store (`Creations.clear_all`,
    `reset_for_pool`, `cleanup`): the disposal registry is detached and walked newest-first, dispatching on the entry
    type (a tuple for a slotted object, a `ManyDisposalBucket` for many), failures aggregated - so a third entry type
    is the natural "new kind of object Creations services". (3) A disposal-bearing `many` registers in the meld's
    innermost scope store (spellspace, else conduit), also when it is built as a child inside a slotted holder's miss,
    so it retires with that scope, not with its holder. (4) `AbstractElasticPool` already implements elasticity
    (stretch target_idle on a miss, decay when quiet, idle retention between baseline_idle and max_idle) but no
    limit or exhaustion: acquire creates on every miss, and its counters are advisory (racy by design), so they cannot
    enforce a hard cap. (5) Phase 6 `ScopeOrderingStrategy` ranks lifetimes (unique 0 ... many 5) and refuses a
    broader holder of a narrower dependency; `many` holders are exempt. (6) Existence is switched on across the meld
    doors and code generation (by text: conduit_meld 20 references, spellspace_meld 18, the generalized compilers 34,
    lane plans 17, site-plan lowering 13, bind 11, spellbinder 8): a new member threads through all of them, plus the
    cache generation and the crystallizer record.
  EVIDENCE:
  - src/melder/aether/spellbook/existence/existence.py:1-138
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1323-1338
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1390-1475
  - src/melder/aether/conduit/creations/creations.py:57-293
  - src/melder/aether/conduit/creations/creations.py:376-468
  - src/melder/aether/conduit/creations/creations.py:1227-1323
  - src/melder/utilities/general_base/abstract_elastic_pool.py:13-470
  - src/melder/aether/spellbook/spell_compiler/system/validation/scope_ordering_strategy.py:1-148
  IMPACT: Pools fit the store-retirement machinery; limits/exhaustion are new pool code; where a lease is registered
    (innermost scope vs the holder's store) is the decision the design turns on; a new Existence member is a
    cross-cutting change.
  NEXT: Bring the owner the design sketch and its decisions (lease boundary, member vs policy, pool home, exhaustion).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T22:54:29Z
  TYPE: HYPOTHESIS
  CLAIM: Re-read after compaction. Correction to the previous note: Phase 6 `ScopeOrderingStrategy` skips `many` on
    BOTH sides - a `many` holder may depend on anything, and a `many` dependency of any holder is never ranked. But a
    disposal-bearing `many` is not unowned: built as a child inside a slotted holder's miss it registers in the meld's
    innermost scope store (`many_store` = spellspace store, else the meld's conduit store), while the holder publishes
    in its own route (conduit, owner, lineage or cluster store). Hypothesis: a `unique_per_conduit` holder first built
    inside a spellspace, or a `unique` holder first built through a lesser conduit, keeps a child that is disposed
    when that spellspace exits or that lesser returns to its pool, and later melds return the same holder holding the
    disposed child. If true it is a live gap in today's `many` (not caused by pools), and it is exactly the stale-lease
    failure a pooled lifetime would turn into "another holder's object".
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/system/validation/scope_ordering_strategy.py:80-121
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1323-1338
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1390-1471
  - src/melder/aether/conduit/creations/creations.py:419-467
  - context_compass/system_docs/src_components.md:3582-3592
  IMPACT: Decides the lease boundary for pools (innermost scope vs the holder's store) and may be a separate defect
    for the owner to rule on; the design discussion should state it as measured, not inferred.
  NEXT: Run a public-API probe on a /tmp copy of src (spellspace and lesser cases plus a root-built control) and
    record the result as a MEASURE note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-11T22:55:37Z
  TYPE: MEASURE
  CLAIM: The hypothesis holds on 0.2.8233 (3.14.7 free-threaded, GIL off and on; public API, a /tmp copy of src).
    A: a `unique_per_conduit` holder first built inside a spellspace - after the space exits, root melds return the
    same holder and its `many` Child has been disposed (`close` ran). B: a `unique` holder first built through a lesser
    conduit - after the lesser's pool return, the same holder with a disposed Child. C (control): the holder built at
    the root keeps an open Child across a spellspace cycle; it closes at root teardown. So a disposal-bearing `many`
    dependency follows the innermost scope, not its holder, and Phase 6 does not refuse the shape. This is today's
    `many`, not a pool effect; a pooled lease registered the same way would go back to the pool and be reissued to
    another consumer while the holder still uses it.
  EVIDENCE:
  - context_compass/artifacts/melder_object_pools_20261011/probe_disposal_many_under_slotted_holder.py:1-102
  - context_compass/artifacts/melder_object_pools_20261011/runs/probe_disposal_many_under_slotted_holder.txt:1-17
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1390-1451
  IMPACT: A pooled lease must end with its holder (or slotted holders of a pooled dependency must be refused at
    Phase 6); the existing `many` gap is a separate defect question for the owner.
  NEXT: Re-read AbstractElasticPool, the SpellSpacePool lease flag and bind's forced-unique rule, then send the owner
    the design discussion with this measured gap.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T22:56:11Z
  TYPE: FACT
  CLAIM: `AbstractElasticPool` documents that a release into a retired pool destroys the object ("those releases find
    a retired pool and destroy rather than retain"), but `release()` never reads `_cleaned`: it appends to `_idle` and
    keeps the object whenever the idle count is within `target_idle`, so the object is neither destroyed nor reachable
    by cleanup, and `acquire()` can still pop it. `SpellSpacePool.release` has the same shape. `acquire()` constructs
    through the abstract `create_object(...)`, so the pool owns construction; counters are advisory and nothing caps
    the live count (`max_idle` caps retention only). For a Spell pool this means: construction must stay in the
    compiled plan (the pool hands out idle objects and accounts, it does not build), exact limits need new accounting,
    and the retired-pool release path must be implemented, not inherited.
  EVIDENCE:
  - src/melder/utilities/general_base/abstract_elastic_pool.py:54-60
  - src/melder/utilities/general_base/abstract_elastic_pool.py:192-212
  - src/melder/utilities/general_base/abstract_elastic_pool.py:290-345
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:270-301
  IMPACT: Reuse the elastic retention policy, not the acquire/release pair as-is; the doc/code gap in the base is a
    small separate fix (or correction) to raise with the owner.
  NEXT: Read bind's forced-unique rule and whether the bind fingerprint hashes existence, then send the design
    discussion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-11T22:58:20Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Pooled-existence design sent to the owner. Objective: Creations services leased objects, Existence declares
    pooled lifetimes, the Spell carries limits/exhaustion/elasticity, with no change to the six existing modes.
    Options for the shape: (A) new members threaded through every Existence switch; (B) a pool modifier on many /
    unique_per_spell_space / unique_per_conduit, enum unchanged; (C) hybrid - members at the API and on the Spell,
    each with a routing base (pooled -> many), so routing switches read the base and only construction, registration
    and retirement learn pooling. Recommended: C, `Existence.pooled` first, per-scope members after. Mechanics
    recommended: one pool per Spell version (lease carries its pool; a return to a retired pool destroys); the pool
    hands out idle objects and accounts while the compiled plan still builds on a miss; a lease registers in the store
    of the nearest stored site above it (the holder's `c{i}` already passed into its miss), or the innermost scope at
    the meld's top level - correct for any holder, unlike today's many (MEASURE above); a third disposal-registry
    entry type returns instead of disposing (purge of one instance = early return); Phase 6 refuses pooled spells
    whose dependencies do not outlive the pool (scoped lifetimes, disposal-bearing many, other pooled spells,
    unresolved inputs) and supplied override values on pooled sites; exhaustion raise (default) and overflow first,
    wait later and root-meld-only with a timeout (a waiter inside a holder's miss holds build locks); exact live
    accounting under a leaf pool lock only when a limit is set; elastic idle retention reused from
    AbstractElasticPool; configuration frozen at bind and fingerprinted (new parts only for pooled bindings, so
    existing ids do not move). Cost: about 120 Existence references by text, cache generation 21, a RecordVersion
    bump, Phase 6 rules, patch docs, graph and docs.
  EVIDENCE:
  - src/melder/aether/spellbook/existence/existence.py:3-138
  - src/melder/aether/spellbook/bind/bind.py:1009-1022
  - src/melder/aether/spellbook/bind/bind.py:1120-1158
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1366-1451
  - src/melder/aether/conduit/creations/creations.py:419-467
  - src/melder/utilities/general_base/abstract_elastic_pool.py:290-345
  IMPACT: Gives the owner one recommended path with the decisions that change it; nothing is drafted or built yet.
  NEXT: Owner decides (1) shape, (2) lease boundary and whether today's many gets the same fix as a separate task,
    (3) exhaustion set, (4) configuration frozen vs live-managed, (5) whether the signature-scan memo lands first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-11T22:58:20Z
  TYPE: DECISION_REQUEST
  CLAIM: Five owner decisions gate the first story: the five listed in the NEXT line above. Until then no patch docs,
    stories or code.
  EVIDENCE: context_compass/tickets/epics/2026-10-05_melder_services_and_pools_epic.md:208-215
  IMPACT: The patch docs (architecture, Creations, site-plan lowering, Phase 6, pool) are written from these answers.
  NEXT: Record the owner's answers in the Decision Log, then draft the patch docs and the pooled-existence story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-11T23:04:15Z
  TYPE: DECISION
  CLAIM: Owner, chat 2026-10-11, answering the shape question: a new Existence member named `pooled_spell`, not a
    `many`-based modifier or hybrid ("I never said use many, I said make a new existence, called pooled_spell"), and
    everything is extended for it. Users configure a pooled spell in specific ways and resolution follows that
    configuration, including a limit that raises an exception. The elastic system of ConduitPool / SpellSpacePool is
    reused as it is in the pooled backend. Creations maintains the pools; pooled objects live in conduits and in
    spellspaces. Scope rank sits between `unique_per_spell_space` and `many` ("more significant than a many object
    but less significant than a unique_per_spellspace so resolution order still permits it"). The owner asked to
    discuss these ideas and their trade-offs next, so nothing is drafted yet.
  EVIDENCE: context_compass/tickets/epics/2026-10-05_melder_services_and_pools_epic.md:208-215
  IMPACT: Supersedes options B and C of the previous STRATEGY_DISCUSSION (option A, named `pooled_spell`); moves the
    pool home from the Spell to the Creations stores; fixes the Phase 6 rank. Open: lease end, pool lifetime across
    store resets, limit scope, the pooled object's own dependencies, and the transitive holder check.
  NEXT: Read resolution_style_matrix.py, ConduitPool and the Existence switch map, then answer with the trade-offs of
    this design.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T23:09:18Z
  TYPE: FACT
  CLAIM: Grounding for the owner's design. (1) `ConduitPool.create_object` never constructs: it returns an idle shell
    or None and the conduit layer builds on a miss; `return_lesser_conduit` appends, then trims - the shape a pooled
    backend needs, because the compiled plan must build the object and its dependencies on a miss. (2) Every conduit
    builds a `SpellSpacePool` and every normal root a `ConduitPool`, both baseline_idle 20 / max_idle 20, so stretch
    and decay never move today; a pooled spell configured with baseline < max would be their first real user. (3)
    `ResolutionStyleMatrix` is the drift-tested support policy: six members expected, class spells support all,
    method / lambda / existing-object families unique-only. (4) About 180 Existence references in 31 source files:
    the two meld doors 38, generalized manifest compiler 27, generalized lane plan 17, site-plan lowering 13, bind 11,
    spellbinder 8, Phase 6 8, many-only discovery and plan 9, artifact processor 6, static command system 6,
    Creations / Conduit / SpellSpace 11. (5) `SpellSpaceMeld.purge` admits only many and unique_per_spell_space; a
    managed space's store is cleared lock-free on exit under a thread-confinement contract.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_pool.py:106-161
  - src/melder/aether/conduit/conduit.py:349-363
  - src/melder/aether/spellbook/resolution_style_matrix.py:107-162
  - src/melder/aether/conduit/meld/spellspace_meld.py:222-239
  - src/melder/aether/conduit/creations/creations.py:1286-1322
  IMPACT: "Reuse the elastic system as it is" maps onto an AbstractElasticPool subclass in the ConduitPool style; the
    reference count sizes "extend everything".
  NEXT: Send the owner the trade-offs of the new member (name, pool scope, lease end, Phase 6, configuration).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-11T23:09:18Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Trade-offs of the owner's design, sent with recommendations. Name (owner asked mid-turn for a Melder-style
    name): members name the instance's lifetime, so drop `_spell`; `summoned` recommended (meld summons from the
    scope's pool, `dismiss(obj)` returns it), `leased` the plain alternative (the kernel's own lease word),
    `resource_managed` accurate but silent about return; decide before the first landing because `existence.name` is
    hashed into spell ids and written into records. Rank between unique_per_spell_space and many: Phase 6 then
    refuses every longer-lived holder of a pooled object, but it skips many on both sides (S -> many -> pooled passes,
    the measured gap) and does not cover the pooled object's own dependencies across leases (disposal-bearing many,
    nested pooled) - walk through many for pooled holders and refuse those dependencies in slice 1. Pool scope per
    spell in the configuration: `conduit` (default; spellspace melds lease from the owner conduit's pool, reuse across
    requests, no unique_per_spell_space dependencies) or `spell_space` (drained at space exit); store reset or
    teardown destroys a pool's idle objects and outstanding leases; limits are per pool, not frame-wide. Limit: exact
    live count under the pool lock only when set; exhaustion raises before anything is built (reserve, build,
    unreserve on failure). Lease end: explicit return (`purge` / `dismiss`, identity-keyed) or the end of the store it
    was registered in; reset hooks before reuse. Extension: ~180 references, the resolution matrix, cache generation,
    RecordVersion, Nexus, docs, graph, plus a member-exhaustiveness test for every Existence switch.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:1009-1022
  - src/melder/aether/spellbook/spell_compiler/system/validation/scope_ordering_strategy.py:80-121
  - src/melder/aether/conduit/conduit_pool.py:106-161
  - context_compass/artifacts/melder_object_pools_20261011/runs/probe_disposal_many_under_slotted_holder.txt:1-17
  IMPACT: Replaces the previous five asks with five for this design.
  NEXT: Owner decides: (1) name, (2) pool scope per spell (conduit default / spell_space) or the meld's own store,
    (3) lease end with reset hooks, (4) the Phase 6 additions, (5) configuration frozen in the spell id or live.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-12T18:35:40Z
  TYPE: FACT
  CLAIM: Owner challenged "stretch and decay never move today" (the kernel pools behave elastically). Read through:
    the kernel pools ARE elastic in live count - a miss always builds (SpellSpacePool.acquire / acquire_untracked
    call `create_object`; lesser creation builds a new Conduit when `ConduitPool.create_object()` returns None), and
    a return keeps the object only while `len(idle) <= _target_idle`, destroying the overflow, so bursts grow without
    a cap and shrink back to the retained target. What does not move is `_target_idle` itself: only the base class's
    `_advisory_stretch_after_miss` / `_advisory_decay_after_overflow` write it, only the base `acquire()` / `release()`
    call them, SpellSpacePool overrides both and ConduitPool is driven through `create_object()` /
    `return_lesser_conduit()`, and both pools are built with baseline_idle 20 = max_idle 20 (stretch needs target <
    max, decay target > baseline). SpellSpacePool's own docstring says the pools are created fixed for that reason.
    `prewarm_spellspaces` / `prewarm_lesser_conduits` clamp to `max_idle`.
  EVIDENCE:
  - src/melder/utilities/general_base/abstract_elastic_pool.py:290-345
  - src/melder/utilities/general_base/abstract_elastic_pool.py:416-470
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:188-301
  - src/melder/aether/conduit/conduit_pool.py:106-161
  - src/melder/aether/conduit/conduit.py:349-363
  - src/melder/aether/conduit/conduit.py:1372-1470
  - src/melder/aether/conduit/conduit.py:2816-2833
  IMPACT: For the pooled backend, "copy the elastic system as it is" gives demand-driven growth plus a fixed retained
    target; a moving target needs the base acquire/release (or their stretch/decay calls) wired into the new pool.
  NEXT: Confirm with a burst probe (50 nested spellspaces, 50 lessers) reading each pool's describe(), then answer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-12T18:36:37Z
  TYPE: MEASURE
  CLAIM: Burst probe on the working tree's source (byte-identical copy, 0.2.8233): both kernel pools are elastic in
    live count - 50 nested managed spellspaces gave 50 distinct live spaces and 50 lessers gave 50 distinct live
    shells, and after each burst the pools kept 20 idle and destroyed the rest; a second burst reused the 20 and built
    30 more. `target_idle` read 20 before, during and after both bursts of both pools (baseline 20, max 20), so the
    retained target does not stretch or decay; growth and shrink come from build-on-miss plus trim-on-return.
  EVIDENCE:
  - context_compass/artifacts/melder_object_pools_20261011/probe_kernel_pool_elasticity.py:1-65
  - context_compass/artifacts/melder_object_pools_20261011/runs/probe_kernel_pool_elasticity.txt:1-14
  IMPACT: The owner is right that the pools behave elastically; the narrower claim stands. A pooled spell can copy
    the kernel behaviour as its default and opt into a moving target (baseline < max, the base stretch/decay calls,
    tested with the base's `time_func` clock); its limit caps the elastic live count.
  NEXT: Answer the owner with the measurement; the five design asks stay open.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-12T18:39:12Z
  TYPE: FACT
  CLAIM: How `target_idle` behaves in the base pool, for the moving-target question. It is the retained-idle count
    a release keeps (append, then trim one oldest object if the deque exceeds it); it never limits live objects.
    Stretch runs only in the base `acquire()` after a miss: +stretch_percent of the current target (default 200%,
    at least 1), capped at max_idle. Decay runs only in the base `release()` after an overflow trim: once 1800 s have
    passed since the last stretch and 600 s since the last decay, -10% of the stretched target (at least 1), floored
    at baseline_idle. So decay is event-driven - a pool that goes quiet keeps its stretched idle objects until releases
    overflow again - and each release trims at most one object, so after a decay the idle count only reaches the new
    target as acquires drain it. The constructor defaults max_idle to baseline_idle (0 by default), so a pool built
    with defaults retains nothing.
  EVIDENCE:
  - src/melder/utilities/general_base/abstract_elastic_pool.py:114-190
  - src/melder/utilities/general_base/abstract_elastic_pool.py:290-345
  - src/melder/utilities/general_base/abstract_elastic_pool.py:416-470
  IMPACT: A pooled spell that wants retained objects to shrink when quiet needs a time-based trim (or accepts the
    event-driven decay); this belongs in the pooled-backend design, not in the kernel pools.
  NEXT: Answer the owner's question about target_idle; the six design asks stay open.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-12T18:42:12Z
  TYPE: MEASURE
  CLAIM: Exact simulation of the real AbstractElasticPool (base acquire/release, fake clock, single thread) for
    bursts of 20..200 live up, 180..20 down, then 220 every ten minutes. Kernel settings (20/20): target 20 and 20
    kept throughout; each burst reuses 20 and builds and destroys the rest - 1,640 built and 1,620 destroyed over
    the 19 up/down bursts. Elastic settings (20/200): the first burst's first three misses stretch the target
    20 -> 60 -> 180 -> 200; ramping up keeps everything (200 built, 0 destroyed over up/down); ramping down keeps 200
    idle with no decay, because decay only runs inside a release that overflows; under overload (220) decay fires
    every 40 minutes (200 -> 180) and the next burst's misses stretch it back to 200, and kept idle stays 200 while
    the target is 180 (one trim per release).
  EVIDENCE:
  - context_compass/artifacts/melder_object_pools_20261011/sim_elastic_pool_target_idle.py:1-142
  - context_compass/artifacts/melder_object_pools_20261011/runs/sim_elastic_pool_target_idle.txt:1-79
  - src/melder/utilities/general_base/abstract_elastic_pool.py:290-345
  - src/melder/utilities/general_base/abstract_elastic_pool.py:416-470
  IMPACT: The base algorithm's stretch saturates and its decay does not run when quiet; the kernel pools sidestep it
    by pinning baseline = max. A pooled spell should either copy the fixed retention or get a time-based decay.
  NEXT: Send the owner the steps-to-variables table and the 20-200 results; ask fixed retention vs fixed decay.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-12T18:53:50Z
  TYPE: DECISION
  CLAIM: Owner, chat 2026-10-12: fix the elastic retention of the pools (target_idle stretch and decay), noting that
    pooled shells are not cheap - "a conduit is very expensive to build". Sequence the owner set: show the whole fix;
    baseline melder_gauntlet with many iterations on the current version; run 1-3 threads before and after; push the
    load past the 20 retained shells so retention and elasticity are exercised; experiment until the fix is proven,
    then do it; before the code change, prepare a big 20-thread test pushed to the maximum and record that baseline
    on the owner's machine; then make the code change and run the same test again.
  EVIDENCE: context_compass/artifacts/melder_object_pools_20261011/runs/sim_elastic_pool_target_idle.txt:1-79
  IMPACT: Opens a separate task under this epic for the AbstractElasticPool / SpellSpacePool / ConduitPool fix; the
    pooled-spell design waits on it (the pooled backend reuses this elastic system).
  NEXT: Locate melder_gauntlet and its knobs, open the task ticket and board row, then patch docs and the baseline.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-12T21:15:14Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: TASK-2026-10-12-make_kernel_pools_elastic landed at 0.2.8234 and the owner turned it in (2026-10-12):
    AbstractElasticPool stretches to what a burst needed and decays when quiet, and both kernel pools run 20/256; the
    owner's native big test shows no regression at 20 threads and a 3-22x shorter return tail past 20. The pooled
    backend this epic plans can reuse that elastic system as it is. The pooled_spell design, its five asks and the
    release-into-a-retired-pool gap stay open; the owner moved to new work, so the epic stays open and unscheduled.
  EVIDENCE: context_compass/tickets/tasks/completed/2026-10-12_make_kernel_pools_elastic_task.md:13-17
  IMPACT: The first pooled-spell story still waits on the owner's answers to the five asks.
  NEXT: When the owner returns to pools, record his answers to the five asks, then patch docs and the first story.
  REREAD: REQUIRED
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
In progress under melder_1. Owner direction (2026-10-11): pools are Existence lifetimes that Creations services,
configured on the Spell (limits, exhaustion, elasticity); service methods and the signature-scan memo stay in the
epic, unordered. Findings (Notes, 2026-10-11): Existence is routing; Creations retires a store newest-first and
dispatches on the registry entry type; AbstractElasticPool gives elastic idle retention only (no limit, and its
documented release-into-a-retired-pool destroy is not implemented); a disposal-bearing many under a slotted holder
follows the innermost scope and is disposed under a live holder (measured, artifacts/melder_object_pools_20261011/).
The owner then chose a first-class member (working name `pooled_spell`, a Melder-style name under discussion),
pools maintained by Creations in conduits and spellspaces, the ConduitPool/SpellSpacePool elastic system reused,
per-spell configuration with a raising limit, and a rank between unique_per_spell_space and many. Trade-offs and
five asks went back (latest STRATEGY_DISCUSSION note). Next: record the answers, then patch docs and the story.
No source changed in this epic.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
