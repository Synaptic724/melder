# Epic: Service methods and Melder-hosted pools - let an owning service supply, lease and take back what Melder injects

## Metadata
- Epic ID: EPIC-2026-10-05-melder_services_and_pools
- Status: draft
- Owner: user
- Agent Name: opus_command_0
- Priority: p1
- Created: 2026-10-05T15:35:41Z
- Updated: 2026-10-05T16:28:09Z
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
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none in this repository yet; receipts live in priv_commandops (see Dependencies / External References)
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
Draft epic opened from the MelderOps logger-pool discussion. Three parts: memoize the per-meld SpellContract scan
(behavior-neutral, about 78 -> 21 us per ChannelLogger meld), service methods (an owned object supplies and takes
back what Melder injects, with the consumer's context), and a Melder-hosted pooled lifetime with service-scope
semantics. Next: the owner answers the six open questions; Milestone 1 can start independently.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
