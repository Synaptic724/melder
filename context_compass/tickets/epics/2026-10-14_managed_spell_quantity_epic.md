# Epic: managed_spell_quantity - a pooled Existence whose objects are leased from the root and given back explicitly

## Metadata
- Epic ID: EPIC-2026-10-14-managed_spell_quantity
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-14T00:28:29Z
- Updated: 2026-10-15T08:55:25Z
- Target Window: 2026-Q4
- Related Program/Initiative: EPIC-2026-10-05-melder_services_and_pools (the pooled-lifetime goal moved here);
  MelderOps Iris logger churn (priv_commandops TASK-2026-10-05-channel_logger_pooling)

## Problem / Opportunity
MelderOps builds one Iris ChannelLogger per object (about 40 classes). On melder 0.2.8226 a logger meld cost 74-82 us
to create and 6.4-6.7 us to clean up, while a measurement-only pool reused one in about 9 us (parent epic, MEASURE
2026-10-05). Melder has no lifetime that reuses an object across holders: `many` builds a fresh object every time,
and the six existing Existence members cache by scope, never by lease. Melder already pools its own kernel objects
(SpellSpacePool, ConduitPool), elastic since 0.2.8234, but offers nothing like it for user bindings.

The owner chose a seventh Existence member, `managed_spell_quantity`: its objects are built once, handed out by a meld
or by injection into a constructor, given back explicitly, reset and reused, and owned by the root conduit until the
root is torn down.

## MRP Alignment (Most Reasonable Product)
One pool object per managed spell, owned by the root's Creations; one release core shared by every way back; explicit
leases with no automatic return; dependency rules like `unique`, enforced in Phase 6; the 0.2.8234 elastic retention
reused rather than rewritten. Ownership, teardown and thread safety are the core and must be right first; the
MelderOps logger win is the proof, not the design driver. Nothing about the six existing members changes.

## Ticket Contract
- ENTRY_GATE: the open questions below are answered and recorded in the Decision Log, patch docs are written and
  linked (architecture, Existence and Creations, site-plan lowering, Phase 6, the pool, bind and the release paths),
  and the first story is drafted. Not met: the owner set this epic to design iteration ("we're not yet ready to
  implement this").
- EXECUTION_BOUNDARY: the Melder kernel - the Existence enum and the resolution matrix, Bind (new keywords, class and
  reset checks, fingerprint), Creations (a root pool location), the ConduitMeld and SpellSpaceMeld doors, site-plan
  lowering and the many_only / generalized compilers (dispense sites, failed-construction return), Phase 6
  ScopeOrderingStrategy, AbstractElasticPool reuse, the release paths (mixin, protocol, ReleaseManagedSpell), the
  crystallizer record and cache generation, plus docs, graph and release note. Excluded: MelderOps adoption; service
  methods and the signature-scan memo (EPIC-2026-10-05); any behaviour change to the six existing members; async;
  automatic or GC-driven return.
- DEPENDENCIES: AbstractElasticPool (0.2.8234); the Creations disposal machinery; Phase 6 ScopeOrderingStrategy;
  the bind fingerprint and crystallizer custody; the fix of the many-child registration bug (a separate task and a
  prerequisite: a disposal-bearing `many` child must be disposed with the object it was built for).
- EXIT_GATE: required stories accepted; success metrics measured; a MelderOps prototype (Iris loggers as a managed
  spell) measured against the 74-82 us path; docs and AGENT_PURPOSE text updated; board and closure sync done.
- FAILURE_ESCALATION: DECISION_REQUEST when a design would change an existing Existence member, the spell id of an
  existing binding, crystallizer custody of existing records, or the frame -> conduit -> Book lock order; CONFLICT if
  two ways back would behave differently; BLOCKER if a release path cannot stay off the existing lock chains.

## Goals (Outcomes)
- `Existence.managed_spell_quantity`: objects built once and reused across leases, owned by the root conduit.
- Three modes chosen per spell at bind: elastic, limited and queued.
- Dispensing by a direct meld and by injection into a constructor during a meld.
- Explicit release through one core, reachable three ways (mixin, protocol member, ReleaseManagedSpell) plus the
  `managed_spell` with statement; no conduit and no Aether needed to release.
- Reset on release, disposal on destroy, and dependency rules like `unique` checked in Phase 6.
- A measured reuse win on the MelderOps logger with no regression on existing meld paths.

## Non-Goals (Explicit Exclusions)
- No automatic lease end: no return when a scope cleans up, no GC hooks or finalizers, no generator (yield) leases.
- No behaviour change to unique, unique_per_conduit, many, unique_per_conduit_cluster, unique_per_conduit_lineage or
  unique_per_spell_space, and no new spell id for an existing binding.
- No release through Aether and no separate ManagedSpells handle.
- No async or thread-bound conduit behaviour, no service methods, no signature-scan memo (EPIC-2026-10-05).
- No MelderOps code.

## Scope Boundaries
- In scope: the member, its bind configuration, the root pool, dispensing, the release core and its three entry
  points, the with statement, destroy paths, Phase 6 rules, recording and cache, docs, tests and benchmarks.
- Out of scope: MelderOps adoption, service methods, the signature-scan memo, async conduits, automatic return.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: opened by the owner (chat 2026-10-14) to document the plan agreed in EPIC-2026-10-05 and keep
  iterating on the design; implementation is not authorized ("we're not yet ready to implement this").

## Success Metrics
- Reusing an idle managed object (meld plus release) costs about 5 us or less to acquire and about 1 us to return for
  a ChannelLogger-like binding (the parent epic's lease targets), against 74-82 us for a fresh logger meld.
- Release routing adds about 100 ns or less per lease under free-threaded load (probe: 30-60 ns on 2 vCPUs).
- A limited pool never has more than N objects alive under a free-threaded stress test; queued waiters raise at
  their timeout and never hang.
- No leaks: weak-reference tests show every idle and every out object destroyed at root teardown and every index
  entry removed.
- Existing behaviour unchanged: spell ids of non-managed bindings identical, the full suite green, existing meld
  benchmarks within noise.

## Requirements (Functional + Non-Functional)
- F1 Member: `Existence.managed_spell_quantity` (name fixed by the owner; it is hashed into spell ids and written
  into records). Class spells only: method, lambda and existing-object bindings stay forced to unique.
- F2 Bind: `quantity=ManagedQuantity.elastic(...)` / `.limited(N)` / `.queued(N, timeout_seconds=...)` (working
  names) and a reset declaration (`reset_method_names`, optional); `disposal_method_names` stays optional. The
  configuration is frozen at bind and fingerprinted only for managed bindings, so no existing id moves.
- F3 Pool: one pool object per managed spell on the root conduit, stored in the root's ConduitCreations (a new
  location; ConduitCreations has empty `__slots__` today). It holds the idle objects, a record of every object that
  is out, the count, a leaf lock and the mode; elastic pools reuse the 0.2.8234 retention. The pool never
  constructs: on a miss the compiled plan builds the object and its dependencies (the ConduitPool shape).
- F4 Dispense: a direct meld, or an injection into a constructor during a meld, takes an idle object, else builds one
  the mode allows. Elastic always builds; limited raises before building anything at N; queued waits for a release
  up to its timeout, then raises.
- F5 Release core: trusted and explicit - Melder tracks no references to a leased object. The pool checks that the
  object is out from it (a second release or a foreign object raises), updates the count, runs the reset outside the
  lock and puts the object back with the idle ones. A reset that raises destroys the object, frees its place and
  raises the error.
- F6 Ways back, all ending in F5: a mixin (`obj.release_managed_spell()`; the pool is recorded on the object once,
  when it is built, never per lease); a protocol member Melder fills, for classes that cannot inherit (release still
  goes through Melder); the `ReleaseManagedSpell` singleton, which uses the object's own pool when it carries one,
  else maps `type(obj)` to the pools of that class and picks the pool that has the object out; and the
  `managed_spell` with statement, whose exit releases.
- F7 Index lifecycle: roots add their pools to the ReleaseManagedSpell index when they create them and remove them
  at teardown (also through lesser upgrade and crystallizer restore). The index is a leaf: its own lock, held only to
  publish a new copy; releases read it lock-free.
- F8 Destroy paths: purge of one object destroys it and frees its place; a failing reset destroys; an elastic trim
  destroys idle objects; root teardown destroys idle and out objects without a reset and removes the index entries.
  Disposal methods run only on destroy, never on release. Purge with no instance: open question 3.
- F9 Ownership: the user owns every release. An object never released stays out, holding its place in the count,
  until root teardown. Melder returns an object itself only when it was dispensed into a construction that failed.
- F10 Lifetimes (Phase 6): a managed spell's own dependencies follow the `unique` rule - it may depend on `unique`
  and not on unique_per_conduit_cluster, unique_per_conduit_lineage, unique_per_conduit or unique_per_spell_space.
  A `many` dependency belongs to the object it was built for and is disposed with it - for a managed object when
  that object is destroyed, never on release; Phase 6 does not refuse it. Today's runtime records a disposal-bearing
  `many` child's disposal in the meld's innermost scope instead (measured), so that fix is a prerequisite. Other
  managed spells as dependencies: open question 5.
- F11 Overrides on managed sites: open question 6 (refusal recommended - a built object is reused by other holders).
- F12 Inspection: per pool, the mode, the count and the outstanding objects; an optional held-too-long warning (open
  question 10).
- F13 Recording: the crystallizer records the managed configuration (a RecordVersion bump); a cache generation bump
  retires executors emitted before managed sites existed.
- N1 Thread safety (free-threaded 3.14): pool and index locks are leaves; reset and disposal run outside every
  lock; no lock is held across user code; nothing adds an edge to the frame -> conduit -> Book teardown order.
- N2 Performance: no regression on existing meld paths; routing and reuse costs measured and recorded.
- N3 Documentation: AGENT_PURPOSE on every new public surface; system docs, graph and release note updated.
- N4 Code rules: the synaptic_python_developer profile (no PEP 604 unions, no `__future__` annotations, value-only
  dataclasses, cleanup deletes owned fields, logger last).

## Constraints / Assumptions
- Melder never supplies a Conduit to a constructor today: a Conduit-typed parameter is an unresolved input, and
  Conduit cannot be bound as a spell - which is why release must not depend on a conduit.
- The bind guard matches exact (module, qualname) pairs and never walks the MRO, so a user class inheriting a Melder
  mixin binds normally.
- `type(obj)` returns the class object, hashed by identity: usable as a dict key with no inspect call.
- Python reports that nothing holds an object only as it destroys it, so no GC hook can return an object that is
  unused but alive.
- Phase 6 today ranks unique 0, cluster 1, lineage 2, unique_per_conduit 3, unique_per_spell_space 4, many 5, refuses
  a holder depending on a higher rank, and skips `many` on both sides.

## Dependencies / External References
- src/melder/aether/spellbook/existence/existence.py:60-117 (the six members)
- src/melder/aether/spellbook/spell_compiler/system/validation/scope_ordering_strategy.py:80-121 (ranks, rule)
- src/melder/aether/conduit/creations/conduit_creations.py:8-104 (the pool home)
- src/melder/aether/conduit/creations/creations.py:858-1019 (purge)
- src/melder/aether/conduit/conduit_pool.py:108-161 (pool shape: hand out or None, build on miss)
- src/melder/utilities/general_base/abstract_elastic_pool.py (the 0.2.8234 retention)
- src/melder/aether/spellbook/spellbook.py:5392-5404 (bind keywords)
- src/melder/aether/spellbook/bind/bind.py:35-100 (bind guard) and 1320-1368 (structural protocol check)
- src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:1100-1226
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:628-704 (unresolved inputs)
- tickets/epics/2026-10-05_melder_services_and_pools_epic.md (Decision Log and Notes, 2026-10-11 to 2026-10-13)
- artifacts/melder_object_pools_20261011/ (probes and runs)
- Prior art: Autofac pooled instances; .NET ObjectPool (a reset may refuse reuse); Apache Commons Pool; HikariCP

## Milestones (Track Progress)
- [x] Milestone 1: Design settled - the open questions answered and recorded in the Decision Log.
- [ ] Milestone 2: Patch docs written and linked - architecture, Existence and Creations, site-plan lowering, Phase 6,
      the pool, bind and the release paths.
- [ ] Milestone 3: Stories drafted and accepted by the owner.
- [ ] Milestone 4: Implemented with unit, component, integration, stress and leak tests and benchmarks.
- [ ] Milestone 5: MelderOps prototype measured against the 74-82 us logger meld.

## Stories (Required to Complete)
- [ ] Story: STORY-TBD-managed_pool_core - the pool object in the root's ConduitCreations, modes, accounting, the
      release core, destroy paths and teardown
- [ ] Story: STORY-TBD-managed_bind_and_phase6 - the member, bind keywords and checks, fingerprint, Phase 6 rules
- [ ] Story: STORY-TBD-managed_dispense - meld doors and site plans (direct meld and injection) and the
      failed-construction return
- [ ] Story: STORY-TBD-managed_release_paths - the mixin, the protocol member, ReleaseManagedSpell and the with
      statement
- [ ] Story: STORY-TBD-managed_recording - crystallizer record, cache generation, docs and release note

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-TBD-managed_pool_core
- [ ] Task: Complete story STORY-TBD-managed_bind_and_phase6
- [ ] Task: Complete story STORY-TBD-managed_dispense
- [ ] Task: Complete story STORY-TBD-managed_release_paths
- [ ] Task: Complete story STORY-TBD-managed_recording
- [ ] Prerequisite: EPIC-2026-10-14-many_child_follows_holder - a disposal-bearing `many` child is recorded
      with its holder's owner (the proof, TASK-2026-10-14-prove_many_child_registration_bug, is done; the fix
      task TASK-2026-10-14-fix_many_child_follows_holder landed as 0.2.8235 and is in review).
- [x] Task: TASK-2026-10-14-investigate_managed_shell_design (fable_0) - the owner's shell shape investigated
      with a VM spike; done 2026-10-14: the settled shape, seam map, numbers and plan are in this epic's Notes.
      tickets/tasks/completed/2026-10-14_investigate_managed_shell_design_task.md
- [ ] Task: Benchmark meld, lease and release costs on the reference VM before and after each milestone.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- Every required story accepted with recorded evidence and the success metrics above measured.
- The MelderOps prototype shows the per-object logger cost cut against 74-82 us create plus 6.4-6.7 us cleanup.
- The owner accepts the design and the walkthrough.

## Risks / Mitigations
- A holder keeps using an object after releasing it, or releases it again after it went to someone else (identity
  cannot tell) -> documented caller contract; the with statement cannot do either.
- State leaks between holders when no reset is declared -> the reset choice is explicit at bind (open question 1).
- Leaked objects hold their place until root teardown, so limited and queued pools can run dry -> inspection lists
  the outstanding objects per pool.
- A queued wait inside a build holds that build's lock while the releaser may wait on it -> the timeout is required.
- The index or pool locks join an existing lock chain -> both are leaves, reset and disposal run outside them,
  covered by stress tests with frame and root teardown racing releases.
- A disposal-bearing `many` dependency is disposed under a live managed object (the measured many-child bug) ->
  fix the registration so the child is disposed with the object it was built for, before this epic lands.
- Spell-id or record compatibility -> new fingerprint parts only for managed bindings; RecordVersion and cache
  generation bumps.
- Index drift across frames, lesser upgrades and crystallizer restores -> register at pool creation, remove at
  teardown, with integration tests for each route.
- A release that arrives after its root was torn down -> open question 2.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Unit: pool accounting per mode, the release core (double and foreign release, failing reset), destroy paths.
- Component: dispensing by meld and by injection, the failed-construction return, the three ways back.
- Integration: several roots and frames managing one class, root and frame teardown, lesser upgrade, crystallizer
  restore.
- Free-threaded stress: concurrent dispense and release, the limit never exceeded, queued timeouts, releases racing
  root teardown.
- Leaks: weak-reference tests at root and frame teardown. Benchmarks: routing, reuse against build, no regression.

## Rollout / Adoption Plan
- Opt-in new Existence member and bind keywords; existing bindings are untouched. MelderOps adopts it after a Melder
  release that contains it.

## Open Questions
- 1) Reset: optional (decided 2026-10-14). Still open: is a reset's return value ignored (recommended), or may False
  mean "do not reuse me", destroying the object quietly?
- 2) A release that arrives after its root was torn down (the object was already destroyed): quiet no-op or error?
- 3) Purge with no instance: soft eviction (destroy idle objects now, destroy out objects at their release;
  recommended), refuse, or a hard purge?
- 4) Queued as the third mode, with a required timeout: confirmed?
- 5) Dependencies beyond the unique rule: allow other managed spells as dependencies? Contracted (borrowed)
  uniques from another root? Does a managed spell rank with unique as a dependency, so any holder may take one?
  (`many` dependencies are settled: they belong to the object they were built for.)
- 6) Overrides on managed sites: refuse (recommended)?
- 7) Names: ManagedSpellMixin, the protocol member, ReleaseManagedSpell, ManagedQuantity; keep or drop
  `conduit.release_managed_spell(obj)` beside the three ways back?
- 8) Answered 2026-10-14: the binding owner's root; pools stay with root scopes, no narrower pool scope for now.
- 9) Elastic defaults (the kernel pools use 20 idle kept, 256 at most) and whether limited and queued pools trim
  idle objects or keep everything they built.
- 10) Inspection: the outstanding-objects listing and an optional held-too-long warning.
- 11) The reset as a method overridden on the mixin, beside the name at bind (two ways to declare it)?

## Decision Log
- 2026-10-15 (owner, chat with melder_0): implement it. The owner: "you can use the way my spellspace pool and
  conduit pool work as elastic and focus on that and understand it, you gotta add transfer of ownership for it
  too thats important and it'll be available for pool objects too you'd follow the same mechanics, you'd need to
  implement all the phases so make a story for each implementation mechanic and investigate everything as you go
  please go ahead and implement this"; `ReleaseManagedSpell` goes in `src/melder/aether/conduit/creations/` as
  its own module; "add more details to the epic take out shit you don't need then implement it please, make the
  epic as detailed as you can because will compact multiple times building this".
- 2026-10-15 (owner, chat with melder_0): object hygiene is the agent's, done with its own tools - "if you have
  tools to work around this stuff and you have codegen what the hell is the problem, you can easily see oh yeah
  look my conduit has extra stuff, and flag it for recycling". Read as: Melder keeps the structure right and
  visible (`ReleaseManagedSpell.describe(cls)`: mode, count, idle per pool); recycling stays with the agent.
- 2026-10-15 (owner, chat with melder_0): purge is not part of this design, and the build is fable_0's
  composition as it stands. The owner: "why are you bringing up purge, when we never talked about purge, thats
  not even needed our new design with fable_0 makes the most sense, ReleaseManagedSpell and how we composed it".
- 2026-10-15 (owner, chat with melder_0): the five follow-up points are not design questions - Melder polices its
  structure, not the objects it hands out. The owner: "overrides can still override the target if this pooled
  object is its resolved graph node for it", "purge can destroy the class if people want", "why are you trying to
  enforce a model that doesn't make sense" and "you've made the same tool 6 times and the newest version is the
  one you like, you then destroy the whole scope, you go ahead and save your blueprint and put it into another
  container". The readings are in the ASSUMPTION_CHALLENGE note of 2026-10-15T01:34:21Z; the settled shape stands.
- 2026-10-14 (final shape, fable_0 for the owner): the Spell keeps the managed options; `ManagedSpellQuantity(deque)`
  of idle objects in the root's Creations under the spell id, an int `count`, no references to out objects;
  `ReleaseManagedSpell` maps the class to `(holder, spell_id)` pairs, registered at conjure, removed at teardown;
  release = optional reset + append; nothing destroyed on notch or cleanup_spell; overrides allowed; the seven-point
  implementation plan and the seam map are in the Notes of this timestamp. The owner hands implementation to the next
  agent ("I'll get opus to do the rest").
- 2026-10-14 (owner, chat with fable_0): the holder is a `deque` of idle objects in the Creations object under the
  spell id - `ManagedSpellQuantity(deque)`, the elastic system built in optionally - composed from the Spell, which
  retains every managed requirement as bind options; no settings object, no composition frame, no identity tracking
  ("we don't care about identity"); release appends. Measured 3-4x cheaper than the spike's shell (elastic cycle
  140 ns through ReleaseManagedSpell, 90 ns through the holder; limited 124 / 82; queue 265 / 239) with the limited
  and queue checks still passing (task MEASURE/DECISION notes of this timestamp).
- 2026-10-14 (owner, chat with fable_0; ruling on the investigation task's four points): the out-record holds strong
  references (F9 as written: an unreleased object holds its place until the scope is torn down; no weak record);
  notch and cleanup_spell destroy nothing - the old version's shell and its objects stay until the scope is destroyed
  or purged; injection into any holder is a lease the holder keeps for its life (no Phase 6 rule); overrides on a
  managed site are allowed - the supplied object is used for that construction and no lease is taken (reverses
  default (g)); `ManagedShell` and `ManagedQuantity` are one class (the bind-time declaration and the per-root live
  shell). The owner's model: "sometimes you don't care about old objects ... you've made the same tool 6 times and the
  newest version is the one you like, you then destroy the whole scope"; objects that are out "maybe are still being
  used".
- 2026-10-14 (fable_0, TASK-2026-10-14-investigate_managed_shell_design): the shell shape measured on the 0.2.8238
  working copy - the three modes and the one way back pass a 15-check stress probe under 3.14t; inside a real emitted
  plan a managed site costs 400-550 ns per creation over a warm `unique` read (acquire ~272 ns, release ~628 ns,
  routing through `ReleaseManagedSpell` +93-100 ns), against 74-82 us for a fresh logger meld; the warm meld lane,
  the other sites and the many registration are untouched. Recommended for the patch docs: one Existence member,
  one shell module (`ManagedShell`, `ManagedQuantity`, `ReleaseManagedSpell`), one door template, one lowering site
  shape, the fourth record shape in the five store readers, one Phase 6 rank entry, two bind keywords, a cache
  generation and RecordVersion bump; one leaf lock per shell (the lock-free variant rejected); a weak out-record
  with one persistent weakref per object; `with` as a small class released through the dispensing shell. Owner
  rulings requested (the task's DECISION_REQUEST): the weak out-record against F9's letter, retiring the shell on
  notch and cleanup_spell, injection into slotted holders as a lifetime lease, overrides refused.
- 2026-10-14 (chat with fable_0): the simplest path - `ReleaseManagedSpell` is the one way back and hosts a
  `with`; a new `Conduit.managed_spell_meld("target")` is the meld-plus-release form; protocol and mixins
  dropped; the object is "managed in creations as a special interface": a shell in the Creations store, looked
  up by spell id like today, that pulls the object out in the mode's way or puts it back; the root owns it; a
  reset list at bind (`managed_spell_reset_methods=[]`); the three modes `limited_quantity`, `elastic`,
  `queue`; "we need the most minimal change here and the same features and keep it easy". fable_0 opened
  TASK-2026-10-14-investigate_managed_shell_design to investigate it with a VM spike ("see what happens").
- 2026-10-14: pools stay with root scopes - the root that owns the binding - and no narrower pool scope is offered for
  now. The owner: "I think we keep it to root scopes for now and leave it at that, its reasonable".
- 2026-10-14: the reset is optional; a pool without a declared reset returns objects as they are. The owner: "if a
  Spell Requires ReleaseManagedSpell to release it, and an optional reset method then what else do we need".
- 2026-10-14: a `many` dependency belongs to the object it was built for, so Phase 6 does not refuse one under a managed
  spell; the runtime must dispose it with that object. The owner: "if unique depends on a many with disposal it
  doesnt matter because it was built for that unique".
- 2026-10-14: a managed spell's own dependencies follow the lifetime rule of `unique`: it may depend on unique, not on
  narrower lifetimes. The owner: "it cannot depend on specific kinds of lifetimes make it similar to unique but it
  can depend on unique".
- 2026-10-14: this epic opened to document the plan and keep iterating; implementation is not authorized. The owner:
  "lets document our current plan and keep iterating we're not yet ready to implement this".
- 2026-10-13: the class defines the target: `ReleaseManagedSpell` maps a managed class to the root pools it goes back
  to, each root registers its pools in it, and pools live in the root's Creations ("store the pool objects in the
  creation object for root_types"); a release runs the reset registered at bind; cleanup methods stay optional.
- 2026-10-13: three ways back over one release core - a mixin, a protocol member and the generalized singleton keyed by
  type. The owner: "why don't we allow all 3 options?"
- 2026-10-13: no release through Aether ("I'm against using the aether to do it I object on that one"), no separate
  ManagedSpells handle, and no conduit required to release ("we don't want everything to require the conduit").
- 2026-10-13: injection is in: a meld of a holder whose constructor takes a managed spell dispenses a pooled object
  into it ("channel logger is injected during the meld ... the pool object gets dispensed").
- 2026-10-13: release is the common, trusted hand-back and Melder tracks no references ("its very symbolic we don't
  check we just trust"); the with statement is the shortcut.
- 2026-10-13: mode purposes: elastic manages space, like many with reuse; limited is for connection-like resources.
  Purge is not the normal path: it destroys one object and frees its place in the count.
- 2026-10-13: the user owns every lease: no automatic return when a scope cleans up, no yield, and an object never
  released holds its place until root teardown ("we cannot baby sit the user"). Purge deletes.
- 2026-10-12: leases are explicit - the `managed_spell` with statement and `release_managed_spell`, not purge.
- 2026-10-12: composition: pools live on the root conduit in a new Creations location; a meld creates from the pool;
  the mode is chosen per spell at bind (limited, elastic and a third, `queued` proposed); a reset named at bind runs on
  return; an object not released stays used until root teardown; deep changes are acceptable if other features are
  preserved.
- 2026-10-12: the member is named `managed_spell_quantity`; no SpellSpace-like manager object to meld through.
- 2026-10-12: the kernel pools' elastic retention was fixed first (landed 0.2.8234) and is the retention a managed pool
  reuses.
- Full owner quotes and the earlier history (pooled_spell, 2026-10-11): the Decision Log of EPIC-2026-10-05.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/melder_object_pools_20261011/ (probes and runs, shared with EPIC-2026-10-05)
  - artifacts/managed_shell_spike_20261014/ (the spike: the deque-holder probe, the earlier shell prototype,
    the captured plan and door probes, logs; retained from the closed investigation task)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - the managed_spell_quantity Existence member and its release paths
- IF_UNKNOWN: ask user before implementation

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose and design; the whole ticket; initial revision
  2026-10-14T00:28:29Z; evidence in Notes. Design decisions: the owner, in chat, as recorded in the Decision Log.
- Assigned implementer: melder_0 (synaptic_python_developer), by owner directive on 2026-10-15; its Notes from
  2026-10-15T00:16:35Z on.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: fable_0 (synaptic_python_developer); the design as of 2026-10-14T17:19:37Z; verdict in the
  DECISION note of 2026-10-14T22:15:12Z; independent of the author's lane

## Notes
- DATETIME: 2026-10-14T00:28:29Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Opened at the owner's request (chat 2026-10-14: "create an epic on this and lets document our current plan and
    keep iterating we're not yet ready to implement this") to hold the managed_spell_quantity plan agreed in
    EPIC-2026-10-05 between 2026-10-11 and 2026-10-13. The decided design is in Goals, Requirements F1-F13 and N1-N4
    and the Decision Log; eleven open questions remain. Iteration continues in chat; no patch docs, stories or code
    until the owner calls the design settled.
  EVIDENCE: context_compass/tickets/epics/2026-10-05_melder_services_and_pools_epic.md:211-299
  IMPACT: This epic is the active route for the pool design; EPIC-2026-10-05 keeps the memo and service methods.
  NEXT: Settle open questions 1-3 with the owner (the reset rule, a late release, purge with no instance).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T00:28:29Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: What "like unique" means in today's Phase 6. ScopeOrderingStrategy ranks unique 0, cluster 1, lineage 2,
    unique_per_conduit 3, unique_per_spell_space 4, many 5 and refuses a holder whose rank is lower than its
    dependency's (a broader holder of a narrower dependency); a `many` holder is skipped, and so is every `many`
    dependency. Giving managed_spell_quantity the rank of unique therefore lets it depend only on unique among the
    slotted members, and lets any holder depend on it. It does not catch a disposal-bearing `many` dependency, which
    follows the meld's innermost scope rather than its holder (measured on 0.2.8233); under a pooled object reused
    across leases, that child would be disposed under a live managed object. F10 needs a managed-specific rule for
    `many` dependencies or the gap fixed first (open question 5).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/system/validation/scope_ordering_strategy.py:80-121
  - src/melder/aether/spellbook/existence/existence.py:60-117
  - context_compass/artifacts/melder_object_pools_20261011/runs/probe_disposal_many_under_slotted_holder.txt:1-17
  IMPACT: F10 is one rank entry plus one managed-specific rule for `many` dependencies.
  NEXT: Owner answers open question 5; then the Phase 6 patch doc.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T02:27:52Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: ASSUMPTION_CHALLENGE
  CLAIM: The owner challenged the earlier FACT note's call for a Phase 6 rule on `many` dependencies ("if unique
    depends on a many with disposal it doesnt matter because it was built for that unique"). He is right about the
    rule: the dependency is legitimate and Phase 6 should not refuse it - that note's "managed-specific rule" is
    withdrawn. The defect is in the runtime, measured on 0.2.8233: a `unique` holder first melded through a lesser
    keeps its `many` child, but the child's disposal is recorded in the lesser's store, so the lesser's pool return
    runs `close()` on the child while the root keeps returning the same holder (case B; case A the same for a
    `unique_per_conduit` holder built in a spellspace; case C, built at the root, stays open until root teardown).
    For a managed object reused across leases the same recording would dispose its child after the first lease's
    scope ends. Requirement F10 now reads: a `many` child is disposed with the object it was built for; the
    registration fix is a prerequisite task.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:258-260
  - context_compass/artifacts/melder_object_pools_20261011/probe_disposal_many_under_slotted_holder.py:68-96
  - context_compass/artifacts/melder_object_pools_20261011/runs/probe_disposal_many_under_slotted_holder.txt:1-17
  IMPACT: No Phase 6 change for `many`; the fix belongs to Melder's `many` registration and helps today's holders too.
  NEXT: Owner agrees to open the many-child registration fix as its own task; then open questions 1-3.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T02:39:19Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: The owner widened the many-child defect beyond `unique` ("not just for uniques but for almost all uniques
    that depend on root") and asked for red regression tests before any fix. The prerequisite task is opened:
    TASK-2026-10-14-prove_many_child_registration_bug maps every holder lifetime and first-meld route and proves the
    affected ones with tests; the fix waits for the owner's review. Design questions 1-3 resume after that review.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-14_prove_many_child_registration_bug_task.md:1-40
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:191-194
  IMPACT: F10's prerequisite has a routed owner-facing task; the epic's tranche order is the task, then questions 1-3.
  NEXT: Complete the task's investigation and show the owner the red tests.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-14T13:02:18Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: STRATEGY_DISCUSSION
  CLAIM: The owner asked why a root must own the pool if ReleaseManagedSpell routes releases ("why can't any scope
    own it?"). Answer given: the singleton answers how an object finds its pool, not how long the pool lives, who
    shares it or what N counts. (1) Floor: leases are user-owned and can outlive any lesser or spellspace, whose stores
    are disposed on every pool return, so a narrower owner would destroy objects still in use or orphan their
    releases - the defect class TASK-2026-10-14-prove_many_child_registration_bug is proving for `many` children.
    (2) Ceiling: managed objects depend only on `unique` (F10), which lives in the binding owner's store and dies with
    that root; an owner above it (the singleton) would keep idle objects holding disposed uniques. (3) Reuse: pools in
    pooled shells rebuild every cycle. (4) N would be per scope, and one pool per binding keeps the singleton's
    type -> pool read at one dict get (+29/+62 ns measured); per-scope pools turn it into a scan and republish the
    index every scope cycle. Locating (only named conduits are found by name) is not the constraint: the mixin and the
    index hold the pool directly. A narrower opt-in pool scope stays possible later. The owner accepted ("nvm").
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:99-128
  - context_compass/artifacts/melder_object_pools_20261011/runs/probe_release_routing_cost.txt:1-3
  - context_compass/artifacts/melder_object_pools_20261011/runs/probe_disposal_many_under_slotted_holder.txt:1-17
  IMPACT: F3 stands (root of the binding owns the pool); open question 8 keeps the owner-root wording.
  NEXT: No change; resume open questions 1-3 after the many-child task review.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-14T15:18:51Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: ALIGNMENT_CHECK
  CLAIM: Two decisions recorded (root scopes own the pools; the reset is optional). The owner asked what else is
    needed to move on. Before the patch docs, these still change the code's shape; each has a recommended default:
    (a) ways back - read "a Spell requires ReleaseManagedSpell to release it" as the singleton being the only way back
    plus the `managed_spell` with statement over it, dropping the mixin and the protocol member (the routing probe
    shows no win for the mixin: +31 vs +29 ns at 1 thread, +52 vs +62 ns at 2) - to confirm, it changes F6, Q7, Q11;
    (b) a reset's return value is ignored and a raising reset destroys the object, frees its place and raises (Q1);
    (c) root teardown disposes the stores first so holders' disposal methods can still release, destroys the pools
    last, and a release after that raises a clear error (Q2); (d) purge with no instance is a soft eviction (Q3);
    (e) queued stays, with a required timeout (Q4); (f) a managed spell depends only on uniques of its own root - no
    contracted uniques, no other managed spells - and ranks with unique as a dependency (Q5); (g) overrides on a
    managed site are refused (Q6); (h) elastic sizes are set at bind, defaulting to 20/256, and limited and queued
    pools keep what they built (Q9); (i) inspection lists mode, count and outstanding objects, no held-too-long
    warning yet (Q10). New from the many-child task: (j) a managed object is destroyed alone (trim, purge, failing
    reset) long before its root's store is, so its own `many` children must be recorded with the object in its pool
    entry and disposed when that object is destroyed - the general fix (children follow the holder's store) does not
    cover it. Also pending: the owner's three answers on the many-child task (how its red tests land, purge
    semantics, opening the fix task), a prerequisite of implementation, not of the patch docs.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:238-255
  - context_compass/artifacts/melder_object_pools_20261011/runs/probe_release_routing_cost.txt:1-3
  - context_compass/tickets/tasks/2026-10-14_prove_many_child_registration_bug_task.md:232-249
  IMPACT: One reply settles the design; then the patch docs and the first story can be written.
  NEXT: Owner confirms (a)-(j) or changes any; record the answers in the Decision Log, then draft the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T17:19:37Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: F10's prerequisite landed as 0.2.8235 (EPIC-2026-10-14-many_child_follows_holder, fix task in review): a
    slotted holder's disposal-bearing `many` children are now recorded in, and disposed with, the holder's owner's
    store. That covers today's lifetimes; a managed object destroyed alone (trim, purge, failing reset) still needs
    its own children kept with it in its pool entry - default (j) stands unchanged. The design still waits on the
    owner's answers on defaults (a)-(j).
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-14_many_child_follows_holder_epic.md:173-191
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1319-1381
  IMPACT: The prerequisite no longer blocks the patch docs once the owner accepts the fix.
  NEXT: Owner confirms (a)-(j) or changes any; then the patch docs and the first story.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-14T22:15:12Z
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Owner direction recorded (Decision Log, 2026-10-14, chat with fable_0): the shell-in-creations shape with
    one way back and the three modes; investigation opened as TASK-2026-10-14-investigate_managed_shell_design
    (fable_0), a read-and-spike lane that does not touch the tree. fable_0's review of this epic (chat,
    2026-10-14) stands as its independent review: the decided core holds against 0.2.8238; four points to settle
    before the patch docs - what the out-record holds (recommended: a weak index whose callback frees the
    place), reserve-before-children in a managed miss, binding mutation paths (notch, cleanup_spell, transfer),
    and injection into slotted holders (a lease for the holder's life; limited pools exhaust).
  EVIDENCE:
  - tickets/tasks/completed/2026-10-14_investigate_managed_shell_design_task.md:1-60
  - tickets/epics/2026-10-14_managed_spell_quantity_epic.md:238-275
  IMPACT: melder_1 keeps the lane (patch docs and stories); the task's findings feed Milestone 1.
  NEXT: the investigation task's seam reads and spike; the owner answers (a)-(j) and the four points.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T23:07:01Z
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The investigation task's result (its MEASURE and DECISION notes): the owner's shell shape holds against
    0.2.8238 with the minimal change set named in the Decision Log entry of this date, and the measured costs sit
    inside the success metrics (acquire 272 ns and release 628 ns against about 5 us and 1 us; routing +93-100 ns
    against about 100 ns; a reuse cycle 400-550 ns over a warm unique read; the logger case wins by two orders).
    Four rulings are the owner's: the weak out-record (F9), shell retirement on notch and cleanup_spell (and purge
    with no instance as the same soft eviction, Q3), lifetime leases into slotted holders, overrides refused (Q6).
    The patch docs stay in this lane (melder_1); the task moves to review for the owner.
  EVIDENCE:
  - tickets/tasks/completed/2026-10-14_investigate_managed_shell_design_task.md:187-355
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_modes_run2.txt:1-19
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_plan_shape_run1.txt:1-11
  IMPACT: Milestone 1 can close on the owner's rulings plus defaults (a)-(j); Milestone 2's patch docs have a
    measured shape to describe.
  NEXT: Owner rules on the four points and (a)-(j); then the patch docs and the first story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T23:45:47Z
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: THE SETTLED SHAPE (owner rulings of 2026-10-14 in chat with fable_0; implementation handed to the next
    agent by the owner: "add a ton of detailed notes to the epic, I'll get opus to do the rest").
    (1) `Existence.managed_spell_quantity`, a seventh `auto()` member; class spells only (the callable and
    existing-object families stay unique-only). (2) The
    Spell retains every managed requirement as bind options - the mode (`elastic` | `limited_quantity` | `queue`), the
    limit, the queue timeout, the elastic idle cap, and the optional `managed_spell_reset_methods` list - no settings
    object, no composition frame; they are hashed into the spell id for managed bindings only, so no existing id
    moves, and the crystal records them. (3) The holder is `ManagedSpellQuantity(deque)`: the deque holds the IDLE
    objects of one managed spell in one root; the mode and numbers are composed from the Spell when the root's owner
    store is stamped at conjure, and the holder lives in the root's Creations under the spell id as a new record
    shape beside the slotted object and the `many` list; `count` is an int of objects built and alive (limited and
    queue accounting), not a list - the holder keeps NO reference to any object it handed out ("we don't care about
    identity"); one leaf lock plus a Condition, used only on the cold paths (the limited check, the queue wait and
    notify, the elastic trim's count); the elastic system is built into the subclass optionally (trim the oldest idle
    above `max_idle` on append, defaults 20/256 like the kernel pools; the 0.2.8234 decay band only if idle memory
    ever matters). (4) Dispense is inlined in the emitted plan - `try: v = h.pop()` / `except IndexError:
    v = _miss(...)` - no method call, no lock (`deque.pop`/`append` are atomic per object on 3.14t); the miss:
    limited raises when
    `count >= limit`, queue waits `cond.wait_for(count < limit or idle, timeout)` then raises, elastic always builds;
    `count += 1`, then the site's children, then the object; a failed build takes `count` back and disposes the
    children it built. (5) `ReleaseManagedSpell`: a dict keyed by the managed class (`type(obj)` is the class object,
    identity-hashed, one dict get) whose value is the pair `(holder, spell_id)` - the holder for the release itself,
    the spell id as the key into the root's Creations for every cold path; root conduits register their pairs at
    conjure (and a post-conjure bind, and the transfer flip) and unregister at teardown; `release(obj)` runs the reset
    names registered at bind, if any, then `append` - "that's how you clean it up and return it and that's it";
    `release(obj, target)` with the meld-style target when the same class has two pairs (two binding names in one
    frame, or the same id in two frames under per-frame ids); the bare call raises an ambiguity then. Helpers on the
    class are welcome: `managed(obj)` (a small `__enter__`/`__exit__` class, never a generator), `release_all(...)`,
    `describe(cls)`. (6) `Conduit.managed_spell_meld("target")`: meld plus the lease class whose `__exit__` releases
    through the dispensing holder. (7) Nothing is destroyed on notch or cleanup_spell: the old version's holder and
    its objects stay until the scope is destroyed or purged (0.2.8219's "product left alive in its slot" applies);
    `purge(instance)` disposes that object and takes `count` down; `purge_all` disposes the idle objects; root teardown
    disposes the idle objects and drops the registry pair (out objects are the user's - no references are kept, so
    they are not Melder's to destroy; F8's "and out objects" clause is withdrawn). (8) Overrides on a managed site are
    allowed: the key-set plan skips the site, the supplied object is used, no lease is taken (reverses default (g)).
    Injection into any holder is a lease that holder keeps for its life; no Phase 6 rule (managed ranks with
    `unique`: it depends only on `unique`, anyone may depend on it). A managed object's disposal-bearing `many`
    children: a side map id(object) -> children, written only at build and only when there are any, read only when
    that object is destroyed (trim, purge) - never on the warm path. (9) A reset that raises: the object is not
    appended; it is disposed, `count` goes down, the error propagates (owner default (b)). (10) Cache generation 21
    retires executors emitted before managed sites; RecordVersion moves for the recorded options.
  EVIDENCE:
  - tickets/tasks/completed/2026-10-14_investigate_managed_shell_design_task.md:356-460
  - context_compass/artifacts/managed_shell_spike_20261014/probe_deque_holder.py:28-104
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_deque_holder_run1.txt:1-7
  IMPACT: Requirements F3, F5, F6, F7, F8 and F9 of this epic read with these rulings (next note); the measured
    warm cycle is three to five warm `unique` reads.
  NEXT: the implementation plan (PLAN note below) and the seam map (FACT note below).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-10-14T23:45:47Z
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: WHICH REQUIREMENT LINES THE RULINGS SUPERSEDE (read F1-F13 and the open questions with this). F2: the
    options live on the Spell (plain bind keywords), the ManagedQuantity working names are dropped; the class merge
    the owner asked for is "no second object at all". F3: the pool is the `deque` holder in the root's Creations
    under the spell id, not a new ConduitCreations location; it holds idle objects and `count`, no record of out
    objects. F5: the release core checks nothing - no "out from this pool" test, no double or foreign refusal; the
    reset is optional and its return value is ignored; a raising reset destroys the object and raises. F6: one way
    back, `ReleaseManagedSpell` (mixin and protocol member dropped), plus the `with`. F7: the index maps the class to
    `(holder, spell_id)` pairs; registered at conjure, removed at teardown. F8: root teardown destroys IDLE objects
    only (no references to out objects exist); purge of one object destroys it; the elastic trim destroys idle
    objects; disposal runs only on destroy. F9 stands as written. F11: overrides allowed (Q6 answered: allow). F12:
    inspection is `describe(cls)` - mode, count, idle; no outstanding-object listing (no references). Open questions:
    Q1 reset optional, return ignored, raise destroys; Q2 a release after its root was torn down raises plainly (the
    pair is gone); Q3 purge with no instance destroys the idle objects, out objects come back as usual; Q4 queue
    stays, timeout required; Q5 managed depends only on unique, anyone may depend on it, `many` children follow the
    object; Q6 allowed; Q7 names: `ManagedSpellQuantity`, `ReleaseManagedSpell`, `managed_spell_reset_methods`,
    `Conduit.managed_spell_meld`; no `conduit.release_managed_spell`; Q8 root scopes; Q9 elastic 20/256 at bind,
    limited and queue keep what they built; Q10 no held-too-long warning; Q11 one way to declare the reset (bind).
  EVIDENCE:
  - tickets/epics/2026-10-14_managed_spell_quantity_epic.md:99-128
  - tickets/epics/2026-10-14_managed_spell_quantity_epic.md:238-258
  - tickets/tasks/completed/2026-10-14_investigate_managed_shell_design_task.md:356-460
  IMPACT: Nothing in F1-F13 needs rewriting by hand; this note is the overlay the implementer applies.
  NEXT: the seam map.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T23:45:47Z
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: THE SEAM MAP, read on the 0.2.8238 working copy (every range opened, not searched). (a) The enum:
    `existence.py:60-117`, six `auto()` members, `__str__` returns the bare name; the seventh is additive.
    (b) The resolution matrix: `resolution_style_matrix.py:108-165` - `EXPECTED_EXISTENCE_COUNT = 6`,
    `ALL_EXISTENCE_NAMES`, `NON_UNIQUE_EXISTENCE_NAMES` and the family policy (class_based supports all; callable
    and existing-object families are unique-only and list the non-unique names as unsupported) - add the member to
    all three tuples and the count; `validate()` refuses an unclassified name. (c) The route family:
    `spell_artifact_processor.py:118-146` maps Existence to `route_family` and raises on an unknown member - add
    `"managed"`; the manifests whitelist it: `strategies/many_only/manifest/many_only_manifest.py:196-214` and
    `strategies/generalized/manifest/generalized_manifest.py:72-90`. (d) The door templates:
    `shared_assets/creation_runtime_door_compiler.py:498-865`, one `(route, lane)` template per existence; the
    `unique` templates at 602-629 (no overrides) and 796-821 (hooks) are the model: the managed template reads the
    holder from `_owner_creations._creations.get(_spell_id)`, inlines `try: creation = holder.pop() / except
    IndexError:` and calls the plan's miss; the warm lane of `Conduit.meld` (`conduit.py:4878-4938`) calls the
    emitted door and never reads a store, so it does not change. (e) The lowering: `site_plan_lowering.py:1331-1470`
    - `_emit_context` places shared sites and `many` steps, `_owner_store_constant` (S9) binds an automatic unique
    site's store as `c{i}`, `_emit_shared_hit` emits the read/miss pair, `_emit_miss` emits the children-first miss;
    a managed site is a third shape: bind the holder as `h{i}` under the S9 condition (automatic owner, stamped
    store), emit the inline pop, and a miss that reserves (`count`) before the children. (f) The store:
    `creations.py` - record shapes and locks 10-120; `_dispose_disposable_registry` 470-560 and `_dispose_entry`
    576; `purge` 1082 and `_detach_purge_entries` 1188; `extract_spell_creations` 1302-1376 and
    `restore_spell_creations` 1377-1470 - each dispatches by isinstance on the three shapes today; the holder is
    the fourth and gets an explicit branch in all five. (g) Ownership stamping: `Spell._add_owned_conduit`
    (`spell.py:1558-1606`) is called at conjure (`spellbook_creation_system.py:1350-1375`), at a post-conjure
    `bind_inactive` (`spellbook.py:5255-5290`) and `bind` (5590-5620), and at the transfer flip
    (`transfer_of_ownership.py:1470-1505`), after which `_move_creations` (1506-1545) extracts and restores the
    spell's records per lineage member - compose the holder and register the pair here; the holder is the same object
    after a move. (h) The doors outside the store: `conduit_meld.py:843-1086` and `spellspace_meld.py:783-1027`
    (live-creation probes, purge resolution, existing lookups) need the holder branch. (i) Phase 6:
    `scope_ordering_strategy.py:80-121`, the `scope_rank` dict; managed = 0 with unique. (j) Bind:
    `Spellbook.bind` 5400-5450 (keywords) and 5540-5545 (non-hook kwargs flow into `spell.metadata`, which the
    fingerprint does NOT hash); `Bind._bind_logic` 571-640 and the `disposal_method_names` flow 464-570 are the
    model for the reset names; `Bind.sha256_profile` 911-1010 hashes spellframe, names, existence, disposal names
    and resolvable - add the managed options there with a default that leaves every non-managed hash byte-identical
    (the `resolvable` precedent). (k) Cache: `caching_system.py:190-212`, generation 20 is current; add 21.
    (l) Records: `record_version.py:84` CURRENT 4.1.0; the spell crystal must carry the options.
    (m) Notch and disposal leave products alone: `_apply_notch` (`spellbook.py:3824-3965`) parks the outgoing
    version and tears down its creation context only; `_dispose_spell` (4325-4420) cleans the Spell.
  EVIDENCE:
  - src/melder/aether/spellbook/existence/existence.py:60-117
  - src/melder/aether/spellbook/resolution_style_matrix.py:108-165
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:118-146
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/manifest/many_only_manifest.py:196-214
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/manifest/generalized_manifest.py:72-90
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:498-865
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1331-1470
  - src/melder/aether/conduit/conduit.py:4878-4938
  - src/melder/aether/conduit/creations/creations.py:10-120
  - src/melder/aether/conduit/creations/creations.py:470-620
  - src/melder/aether/conduit/creations/creations.py:1082-1206
  - src/melder/aether/conduit/creations/creations.py:1302-1470
  - src/melder/aether/spellbook/spell.py:1558-1606
  - src/melder/aether/spellbook/spellbook_creation_system.py:1350-1375
  - src/melder/aether/spellbook/spellbook.py:5255-5290
  - src/melder/aether/spellbook/spellbook.py:5590-5620
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1470-1545
  - src/melder/aether/conduit/meld/conduit_meld.py:843-1086
  - src/melder/aether/conduit/meld/spellspace_meld.py:783-1027
  - src/melder/aether/spellbook/spell_compiler/system/validation/scope_ordering_strategy.py:80-121
  - src/melder/aether/spellbook/spellbook.py:5400-5450
  - src/melder/aether/spellbook/bind/bind.py:464-640
  - src/melder/aether/spellbook/bind/bind.py:880-1010
  - src/melder/utilities/caching_system/caching_system.py:190-212
  - src/melder/crystallizer/persistence/record_version.py:84-85
  - src/melder/aether/spellbook/spellbook.py:3824-3965
  IMPACT: Every edit point is named with its model; the only UNKNOWN left is which crystal fields carry the options
    (`spell_crystal.py` and the restore engine's bind replay were not opened for this).
  NEXT: the plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-10-14T23:45:47Z
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: THE NUMBERS (VM, CPython 3.14.7t, `-X gil=0`, caching off; the probes and logs are in the artifacts
    folder). Reference: a warm `unique` site read 30 ns; `Manager()` construction 70 ns; a whole
    `conduit.meld("Worker")` 337 ns; a fresh Iris logger meld on MelderOps 74-82 us (parent epic). The owner's deque
    holder, acquire + release per cycle, one idle object: elastic 140 ns through `ReleaseManagedSpell` / 90 ns
    through the known holder (with a declared `reset()` 215 / 149); limited_quantity(4) 124 / 82; queue(4, 1.0 s)
    265 / 239. The spike's earlier `ManagedShell` (entries, weakrefs, a locked warm path) cost 505 / 407, 484 / 389
    and 567 / 461 for the same modes, and inside a real emitted plan 715 ns per Worker creation against 166 ns
    plain; a lock-free variant of it saved only 115-145 ns per cycle and lost the teardown invariants - both are
    reference only now. Stress: limited(3) never exceeds 3 under 8 threads; queue(1, 0.25 s) waits then raises at
    its timeout; a waiter is served by a release (the same object, no build). The `contextlib.contextmanager` form
    of the `with` costs about 600 ns more than a plain class - emit a class. Rerun: `python -X gil=0
    <artifacts>/probe_deque_holder.py` (standalone), `probe_plan_shape.py` and `probe_plan_capture.py` (need
    `tests/experimentation` and the repo on the path, cwd anywhere; they build a world through the certification
    harness and capture the emitted plan).
  EVIDENCE:
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_deque_holder_run1.txt:1-7
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_door_modes_run2.txt:1-4
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_plan_shape_run1.txt:1-11
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_modes_run2.txt:1-19
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_cost_variants_run1.txt:1-8
  - context_compass/artifacts/managed_shell_spike_20261014/logs/probe_plan_capture_worker_source.txt:1-23
  IMPACT: Success metric 1 (about 5 us to acquire, about 1 us to return) is met by 30x; metric 2 (routing about
    100 ns) by the singleton's +50 ns; the benchmark task of this epic can reuse the probes.
  NEXT: the plan.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T23:45:47Z
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: IMPLEMENTATION ORDER AND TESTS (one lane, one writer per file; each `src/` change notches 0.0001 and adds
    its release-note entry; assets rebuilt last). 1. Enum, matrix, route family and manifest whitelists (seams a-c);
    unit: `ResolutionStyleMatrix.validate()` green with seven members, the processor maps the member. 2. Bind
    options on the Spell, the fingerprint (managed only), the crystal fields and RecordVersion; unit: a non-managed
    binding's id is byte-identical before and after, a managed binding's id changes with its mode/limit/timeout/
    reset names, record and restore round-trip the options. 3. `ManagedSpellQuantity(deque)` and the Creations
    composition at `_add_owned_conduit`, the five readers' branch, purge semantics (one object; idle on purge_all),
    teardown disposes idle; unit per mode: count accounting, limited raise, queue wait/timeout/served-by-release,
    elastic trim at max_idle, reset order and the raising reset; stress: limited never exceeds N under threads.
    4. `ReleaseManagedSpell` (register at the three stamping points and the transfer, unregister at teardown; the
    pair; the ambiguity rule and the target form), the lease class, `Conduit.managed_spell_meld`; unit: routing,
    ambiguity, release after teardown raises plainly; component: `with` releases on exit. 5. The door templates and
    the lowering site shape (the inline pop, the reserve-first miss, children before the object, failure path);
    component: a direct meld dispenses and reuses, injection into a `many` holder and into a `unique` holder, an
    override skips the site, a `many` child with disposal dies with its managed object on trim/purge, a transfer
    moves the holder and releases keep working, a notch leaves the old holder in place; integration: two roots in
    one frame with the same class under two binding names (ambiguity, target), per-frame ids with one id in two
    frames, crystallizer record/restore of a managed world. 6. Phase 6 rank entry; unit: managed may depend on
    unique only, any holder may depend on managed. 7. Cache generation 21; unit: an old-generation bundle is cold.
    8. Docs: src_architecture (boundary list, the meld sequence, operational invariants, failure modes, code map),
    src_components (Creations, Meld doors, Bind, the lowering, Phase 6), tests docs, graph descriptors, the README's
    Existence section, the running release note; `AGENT_PURPOSE` on every new public surface. Benchmarks: the
    probes above as the before/after; no regression on the existing meld paths (the harness's five shapes).
  EVIDENCE:
  - tickets/epics/2026-10-14_managed_spell_quantity_epic.md:160-200
  - context_compass/special_instructions/agent_contribution_guide.md:1-97
  - context_compass/artifacts/managed_shell_spike_20261014/probe_deque_holder.py:28-104
  IMPACT: The stories of this epic can be cut along steps 1-2, 3-4, 5, 6-7 and 8.
  NEXT: the owner assigns the implementer; TASK-2026-10-14-investigate_managed_shell_design closes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T00:16:35Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner reassigned this epic to melder_0 (chat 2026-10-15: "go ahead and take on the new epic for creating
    the new existence type fable should have done a good job explaining it go read all that please"), the next
    agent fable_0's handoff names. melder_1 keeps EPIC-2026-10-14-slotted_lifetime_ownership_fixes, whose rebuild
    and acceptance are still open on files this epic also changes (creations.py, site_plan_lowering.py,
    transfer_of_ownership.py, conduit.py): this lane writes no `src/` file until that lane has rebuilt and released
    them. The seam check, the patch docs and the stories touch no shared file. The codex_bridge listing failed
    ("Codex app tool request failed") and melder_1 and fable_0 are Claude sessions the bridge does not reach, so
    this ticket and its board row are the coordination record.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:547-552
  - context_compass/tickets/epics/2026-10-14_slotted_lifetime_ownership_fixes_epic.md:393-450
  - context_compass/artifact_board.md:105-105
  - context_compass/mailbox_board.md:96-98
  IMPACT: One writer for this ticket and its board row; no `src/` overlap with melder_1's open lane.
  NEXT: The owner rules on the DECISION_REQUEST below; meanwhile check the seam map against the 0.2.8240 tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T00:16:35Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: Read whole, the settled shape (2026-10-14T23:45:47Z) leaves five points the patch docs cannot decide alone.
    (1) Two versions of one class in one root: a parked version gets a holder when bind_inactive stamps it, and the
    shape says neither whether its pair is registered nor how a release picks a version - the meld-style target
    names the index, not the version. Recommended: register every holder; with several pairs of one class a bare
    release raises the ambiguity, and `release(obj, spell_id)` or the lease class picks exactly. (2) Q2's "a
    release after its root was torn down raises plainly" holds only while no other root manages that class: with
    one other pair left, the object (and the disposed uniques it holds) is appended to that root's holder
    silently. Recommended: the caller's contract (release before the leasing root ends; afterwards the object is
    yours); protection needs per-object identity, which the shape rules out. (3) The `many`-children side map
    keyed by `id(object)`: recommended that root teardown dispose the children recorded for out objects too (the
    store's own record; those objects' uniques die with the root anyway) and that a build finding an entry under
    its id dispose those stale children first (left by a dead out object). (4) An override reaching below a
    managed site, into the managed object's own constructor inputs, is unruled (ruling 8 covers supplying the
    managed object itself): recommended a refusal like unique's "already exists". (5) `purge(instance)` of an
    idle object must also take it out of the deque (a cold `deque.remove`), or the disposed object is dispensed
    again; purging an object the holder did not build miscounts (the caller's contract, as a double release is).
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:551-591
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:606-622
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:657-662
  - context_compass/tickets/tasks/completed/2026-10-14_investigate_managed_shell_design_task.md:472-481
  - context_compass/system_docs/src_architecture.md:522-547
  IMPACT: Milestone 1 closes on these five answers; the patch docs carry them and the rest of the shape as written.
  NEXT: Record the owner's answers in the Decision Log, then the seam check and the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T00:18:39Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: fable_0's seam map (read at 0.2.8238) still locates every seam on the 0.2.8240 tree. Definition spans from
    the syntax tree: site_plan_lowering.py `_emit_context` 1331-1361, `_emit_many` 1363-1393,
    `_owner_store_constant` 1396-1419, `_emit_shared_hit` 1421-1443, `_emit_miss` 1445-1513; creations.py record
    shapes 10-111, purge 1082-1186, extract/restore 1302-1474; spell.py `_add_owned_conduit` 1558-1607; Phase 6
    `scope_rank` 80-87; bind.py `_bind_logic` 571-820 and `sha256_profile` 911-1022; the cache generation history
    190-211; RecordVersion CURRENT 84. One drift: 0.2.8239 moved transfer_of_ownership.py's flip to 1383-1510 and
    `_move_creations` to 1512-1555 (cited 1470-1505 and 1506-1545). These are locations, not behaviour: each body
    is read whole before its patch doc. src/, release_docs/, llm_support/ and system_docs/ are clean against HEAD
    7fc8dd48e (committed 2026-10-15T00:14:03Z) at 0.2.8240; whether melder_1's rebuild ran before it is UNKNOWN.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1331-1513
  - src/melder/aether/conduit/creations/creations.py:10-111
  - src/melder/aether/conduit/creations/creations.py:1082-1474
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1383-1555
  - src/melder/__version__.py:12-12
  IMPACT: The seam map needs no rework before the patch docs; the two transfer citations take their new ranges.
  NEXT: On the owner's answers, read each seam body whole and write the patch docs, architecture first.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T01:34:21Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: ASSUMPTION_CHALLENGE
  CLAIM: The owner rejected the DECISION_REQUEST of 2026-10-15T00:16:35Z (chat 2026-10-15): points 2-5 policed
    objects Melder hands out, which the runtime model rules out - agents iterate, keep the newest version and destroy
    the whole scope. Read under it, nothing is left open. (1) Two different classes are two types, so each routes to
    its own pool. One class object bound twice is one key with two spell ids (the fingerprint hashes the class shape
    plus the bind options, and bind refuses only an equal id), and the active version's pool takes its releases (a
    notch re-points it): same class, same code. (2) A release after its root ended is the agent's business. (3) Root
    teardown disposes everything the root recorded, the pooled objects' recorded `many` children included. (4) An
    override replaces the pooled node when the pooled object is the resolved node, no lease; one aimed at the pooled
    object's own inputs builds that object fresh for that construction, no lease (melder_0's reading of "overrides
    allowed"). (5) Purge disposes what it targets; a purged idle object leaves the queue. From the fingerprint:
    method bodies are not hashed, so a body-only rewrite keeps its spell id and, rebound after cleanup_spell, meets
    the old pool, as a slotted replacement meets its old slot today (0.2.8219).
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:522-547
  - src/melder/aether/spellbook/bind/bind.py:961-1022
  - src/melder/aether/spellbook/spellbook.py:5226-5241
  - src/melder/aether/spellbook/spellbook.py:5270-5285
  IMPACT: Milestone 1 is met: the settled shape of 2026-10-14T23:45:47Z stands with these readings.
  NEXT: On the owner's go-ahead, read each seam body whole and write the patch docs, architecture first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T01:37:31Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Scope narrowed by the owner (chat 2026-10-15): purge is not part of this design ("we never talked about
    purge, thats not even needed"), and the build is fable_0's composition as recorded: the Existence member, the
    bind options on the Spell, `ManagedSpellQuantity(deque)` in the root's Creations, the inline pop and the
    reserve-first miss, `ReleaseManagedSpell` keyed by class to `(holder, spell_id)` with the optional reset then
    `append`, `Conduit.managed_spell_meld`, and scope teardown disposing what the root holds. Withdrawn: the
    settled shape's `purge(instance)` / `purge_all` lines and point (5) of the 2026-10-15T01:34:21Z note. The store's
    purge reader only has to leave a managed record untouched; the patch docs state how.
  EVIDENCE: context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:558-611
  IMPACT: No managed purge verb is built; the rest of the settled shape is unchanged.
  NEXT: On the owner's go-ahead, write the patch docs from the settled shape, architecture first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T08:51:04Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: The owner authorized implementation (Decision Log, 2026-10-15 "implement it"). Tranche order: (1) read the
    kernel elastic pools whole (AbstractElasticPool, SpellSpacePool, ConduitPool) - the elastic mode reuses their
    retention mechanics; (2) read the transfer path's creation moves whole (TransferOfOwnership, Creations
    extract/restore) - a transfer carries a managed pool and its idle objects the same way; (3) archive the
    superseded epic text verbatim under artifacts/managed_spell_quantity_20261015/ and rewrite the epic as the full
    build spec; (4) one story per implementation mechanic; (5) patch docs, then each story red tests -> src -> green ->
    notch -> release note, rebuild last. `ReleaseManagedSpell` lives in src/melder/aether/conduit/creations/.
  EVIDENCE: context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:1-60
  IMPACT: The lane moves from design to build; every finding lands here before the next tranche.
  NEXT: Read abstract_elastic_pool.py, spell_space_pool.py and conduit_pool.py whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T08:52:31Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The kernel elastic pools, read whole on 0.2.8240. `AbstractElasticPool` keeps idle objects in `_idle`
    (a deque set once at init; `cleanup()` destroys them and clears it, never replaces it); a hit is
    `_idle.pop()` (newest, warmest); a miss builds and calls `_note_miss()`, which only stamps the pressure clock
    (settle 1800 s, lock-free). A return appends and stops when at most `baseline_idle` are idle (no clock, no
    lock); above that `_rebalance_after_return()` reads the clock and, under `_lock` (a leaf RLock held for counter
    and deque work only), stretches `target_idle` to the observed idle count while a miss is recent (capped at
    `max_idle`), else decays it 10% per 600 s toward the baseline, detaches the surplus oldest first and destroys
    it outside the lock through `destroy_object` (a raising destroy re-pools the rest). `max_idle == baseline_idle`
    is a fixed-capacity pool: a return above the baseline evicts the oldest, no clock, no lock. Objects out are
    not reclaimed by `cleanup()`. ConduitPool and SpellSpacePool are the model subclasses: their own fast paths
    pop or `_note_miss()` and let the caller build (ConduitPool returns None on a miss), release appends and
    rebalances above the baseline; Conduit builds both at baseline 20 / max 256.
  EVIDENCE:
  - src/melder/utilities/general_base/abstract_elastic_pool.py:123-264
  - src/melder/utilities/general_base/abstract_elastic_pool.py:328-378
  - src/melder/utilities/general_base/abstract_elastic_pool.py:449-599
  - src/melder/aether/conduit/conduit_pool.py:108-165
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:188-307
  IMPACT: `ManagedSpellQuantity` subclasses `AbstractElasticPool` (owner: elastic works like these pools): elastic
    is baseline 20 / max 256 with the same stretch and decay; limited_quantity and queue are fixed-capacity at N
    (nothing to trim; the count gate refuses or waits). The plan's warm path pops the holder's `_idle` deque, and
    `destroy_object` runs the Spell's disposal methods plus the object's recorded `many` children.
  NEXT: Read Creations (record shapes, cleanup, extract/restore) and the transfer creation moves whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T08:55:25Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Creations and the transfer path, read whole on 0.2.8240. `Creations` keeps `_creations` (the live object or
    `many` list per spell id, the only map resolution reads), `_disposable_creations` (cleanup-only: an
    `(object, methods)` tuple, a `ManyDisposalBucket` or a `HolderDisposalEntry`), `_slot_guards` and a leaf
    `_lock`. `cleanup()` detaches both maps under the lock, disposes the disposable registry newest-first (a
    dependency registers before its dependent, so insertion order is creation order), then deletes its fields and
    keeps `_lock` as a tombstone. `extract_spell_creations` / `restore_spell_creations` move one spell id's rows
    (`scope` unique or many, `stored`, `disposal_methods`, `children`); restore replaces what the id held. Transfer
    `execute()`: under both conduit locks `_flip_registry_and_spellbooks` stamps the ACTIVE member on the target
    (`_add_owned_conduit` with the target's store) and `_migrate_inactive_members` moves parked members without
    re-stamping them; then `_move_creations` extracts and restores every member id (its rollback re-extracts the
    target and restores the source) or, with `move_creations=False`, `_teardown_creations` extracts the active
    member's rows and keeps them only for rollback. Lineage spells skip both.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:118-296
  - src/melder/aether/conduit/creations/creations.py:306-363
  - src/melder/aether/conduit/creations/creations.py:489-542
  - src/melder/aether/conduit/creations/creations.py:1302-1474
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:367-507
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1079-1104
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1470-1590
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1592-1636
  IMPACT: Design decisions for the build: (1) pools get their own map in Creations, `_managed_quantities[spell_id]`,
    so no reader of `_creations` (lookups, live probes, purge) can mistake a pool for an object; (2) Creations
    disposes its pools before the disposable registry, because a pool is created at conjure, before the uniques its
    objects hold, and reverse insertion order would close those uniques first; (3) extract/restore carry a
    `managed` row holding the same pool object, so a transfer moves the pool with its idle objects, and the
    ReleaseManagedSpell registry follows the store (a store registers a pool it takes, unregisters one it gives
    up); (4) the Spell keeps a borrowed reference to its pool, so dispensing does not depend on `_owner_creations`,
    which the flip re-stamps for the active member only. UNKNOWN: whether a notch re-stamps a parked member's owner
    store after a transfer (check `_apply_notch` in the transfer story).
  NEXT: Archive the epic verbatim, rewrite it as the build spec and open one story per mechanic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Opened 2026-10-14 (melder_1) to hold the managed_spell_quantity plan. The owner settled the shape with fable_0 the
same day (Decision Log; Notes of 2026-10-14T23:45:47Z: the settled shape, the requirement overlay, the seam map,
the numbers and the implementation plan) and on 2026-10-15 reassigned the epic to melder_0, whose five follow-up
points the owner resolved under the runtime model - Melder polices its structure, not the objects it hands out
(ASSUMPTION_CHALLENGE note of 2026-10-15T01:34:21Z). Milestone 1 is met, and the seam map still locates every seam on
0.2.8240 (FACT note of 2026-10-15T00:18:39Z). Nothing is drafted beyond this epic and nothing is built. Next, on the
owner's go-ahead: read each seam body whole, write the patch docs (architecture first), then the stories along the
plan's steps. No `src/` edit until EPIC-2026-10-14-slotted_lifetime_ownership_fixes (melder_1) is accepted and its
files are free; each landed `src/` slice takes its notch from `__version__` at landing (0.2.8240 now) and its
release-note entry; the rebuild is last. The earlier discussion stays in EPIC-2026-10-05 (Notes 2026-10-11 to
2026-10-13).

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
