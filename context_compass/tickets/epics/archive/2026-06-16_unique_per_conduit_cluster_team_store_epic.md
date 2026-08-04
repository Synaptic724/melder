# Epic: unique_per_conduit_cluster Team-Store (Cluster-Scoped Creations)

## Metadata
- Epic ID: EPIC-2026-06-16-unique-per-conduit-cluster-team-store
- Status: COMPLETE / LANDED (2026-06-20). The team-store ships and is live: a
  `unique_per_conduit_cluster` meld resolves through the elected leader's
  `Creations`, shared by every member root, and hard-errors while inert. The
  final facade lives PER ROOT CONDUIT (`Conduit._cluster_creations`), which
  DIVERGED from the cluster-owned-facade plan described in the body below. See
  "## Resolution (Closure)" for the as-built design; the planning body (Phases,
  Step E, "What cluster_creations is FOR", PHASE 3 HANDOFF) is retained as
  history and is partly superseded. Mediator elect/unelect strategies landed in
  the companion epic.
- Companion epic: 2026-06-16_cluster_leader_election_transactions_epic.md
  (mediator_builder_0 implements the real `elect_conduit_cluster_leader` /
  `unelect_conduit_cluster_leader` transaction strategies; this epic ships a
  no-op seam for them)
- Owner: cowork
- Agent Name: compiler_strategy_0
- Priority: p2
- Created: 2026-06-16T22:34:39Z
- Updated: 2026-06-20T00:00:00Z
- Target Window: 2026-Q2
- Related Program/Initiative: Existence/scoping correctness (follow-on to the
  unique_per_conduit_lineage resolver-root redesign)
- Prerequisite epic: 2026-06-13_unique_per_conduit_lineage_resolver_root_semantics_epic
  (built `Creations._root_creations` + the OWNER routing split this epic reuses)

## Resolution (Closure)
Shipped 2026-06-20. `unique_per_conduit_cluster` is a true team-store: one
instance per cluster, shared by every member root and its lessers/spellspaces,
regardless of which member owns the spell.

As-built design (note: this DIVERGED from the cluster-owned-facade plan in the
body below; that planning content is kept as history):
- The live team-store facade is PER ROOT CONDUIT: each root owns a
  `Conduit._cluster_creations: ClusterCreations`, passed down its lineage by
  reference (like `_root_creations`). The meld front door resolves through
  `conduit._cluster_creations.resolved_store()`, so the door never has to look
  up which cluster a conduit belongs to (the reason the facade moved off the
  cluster and onto the conduit).
- Election is a per-member walk, not a single cluster-facade write:
  `ConduitCluster.elect_leader` opens the `ELECT_CONDUIT_CLUSTER_LEADER`
  transaction and `bind_elected_leader` binds every member root's facade to the
  elected leader's `_creations`, recording `master_conduit_id`. `unelect_leader`
  / `unbind_elected_leader` drain member lineages, unbind every member facade,
  and clear `master_conduit_id`. `unbind` only drops the pointer; the leader's
  underlying `Creations` is cleaned solely by the leader conduit.
- While inert, `resolved_store()` / `get_creation` / `add_creation` hard-error,
  so a no-leader cluster meld fails at the meld door instead of resolving into
  nothing.
- Routing: `unique_per_conduit_cluster` has its own `cluster` route family,
  `_TEMPLATE_CLUSTER_*` door templates, an `is_cluster` inner-executor flag, and
  solo/generalized registration into the elected-leader store. The compiler
  stays cluster-agnostic; the gate is a runtime door check only.
- The cluster-owned `ConduitCluster.cluster_creations` facade from the original
  plan was constructed but never bound/resolved (vestigial) and has been REMOVED.

Closure checklist:
- [x] Per-conduit `_cluster_creations` facade + meld-door store-selection.
- [x] `cluster` route family, door templates, `is_cluster` flag, solo/generalized registration.
- [x] `elect_leader`/`unelect_leader` transactions + `bind_`/`unbind_elected_leader` domain walks.
- [x] Inert-by-default hard-error at the meld door.
- [x] Dead cluster-owned facade removed.
- [x] Test suite green (cluster integration/component/harness + cache-asset rehydration).

Deferred (Non-Goals / follow-ons, not in this epic): owner-leave re-home/transfer,
multi-cluster membership, and `JOIN_CLUSTER`/`EXIT_CLUSTER` single-member facade
transactions (join/leave into a live cluster).

## Problem / Opportunity
`unique_per_conduit_cluster` does not implement the scope its name implies. Today
its instance storage is **byte-for-byte identical to `unique`**: the creation
executors store into the binder's prebound `_owner_creations`
(`solo_no_overrides_codegen_creation_compiler.py:251`, same lane as `unique`).
The only thing that makes it "cluster" is that `ConduitCluster` auto-contracts
the binder's spell out to members via `cluster_link` contracts, so members reach
the binder's single instance.

Consequence: the cluster-scoped root id encodes the owner
(`cluster:{name}:{owner_id}:{spell_id}`, `conduit_cluster.py:663`), so storage is
per-owner. If two members bind the same spell and both share it, you get **one
instance per owner, not one per cluster**. The "all roots in a cluster share one
instance" (team-store) semantic is not actually delivered.

This is the cluster analogue of the lineage bug we just fixed, and the lineage
epic deliberately shaped `root_creations` + the OWNER routing split to be reused
here.

## Goals
- `unique_per_conduit_cluster` becomes a true team-store: **one instance per
  cluster**, shared by every member root (and their lessers/spellspaces),
  regardless of which member owns the spell.
- Reuse the lineage plumbing (`_root_creations` read-through) so there is **zero
  per-lesser fan-out and no pool walks** on any cluster state change.
- Every cluster state change (activate/elect, deactivate, future transfer) is a
  **single action** (no O(members) rewrites of the hot resolution path).
- A `unique_per_conduit_cluster` spell with no elected owner is **inert by
  default** and fails fast at meld; binding it is always allowed.
- The compiler stays cluster-agnostic; the gate is a runtime door check only.

## Non-Goals (Explicit Exclusions)
- **In-cluster ownership transfer / re-home** of the team-store when the owner
  leaves. v1 = owner-leave dissolves (cluster goes inert). The facade design
  makes transfer a later one-write extension; not implemented here.
- **Multi-cluster membership.** v1 enforces exclusivity (one cluster per
  conduit). Relaxing it later becomes "key the binding per cluster"; not now.
- Changes to `unique`, `unique_per_conduit`, `many`, `unique_per_spell_space`, or
  `unique_per_conduit_lineage` semantics.
- Changes to the recipe-sharing mechanism. `cluster_link` contracts that make a
  shared spell's recipe reachable by members are unchanged; only **instance
  storage** moves.

## Scope Boundaries
- In scope: the `cluster_creations` facade, the spell-side facade pointer + the
  cluster door flip, exclusivity enforcement, first-join leader election, the
  bind/unbind lifecycle wire, docs + tests. `Creations` stays untouched.
- Out of scope: transfer/re-home, multi-cluster, recipe-sharing internals, any
  unrelated existence or refactor.

## Design

### Core idea
A small **facade** object, `cluster_creations`, fronts the elected leader
conduit's `Creations`. The dependency is one-way: `ClusterCreations` knows about
`Creations`; **`Creations` knows nothing about clusters** and is left untouched.
A `unique_per_conduit_cluster` spell resolves its instance through the facade, so
every member of the cluster shares one team-store instance regardless of which
member owns the spell.

### Ownership (owns vs references -- important)
- A `ConduitCluster` **owns** one `cluster_creations` facade.
- The facade **references** (never owns) the leader conduit's `Creations`. The
  leader conduit owns and cleans its own `Creations`. `unbind()` only drops the
  facade's target reference; it never cleans the underlying store.

### Resolution (spell-side; Creations untouched)
The cluster door already resolves `unique_per_conduit_cluster` through the spell's
store pointer (today `spell._owner_creations`). Cluster keeps that shape: at
elect, the cluster's `unique_per_conduit_cluster` spells point at the cluster's
facade, and the door reads that pointer **live** in the executor (prebound capture
is disabled for the cluster lane, exactly as lineage disables it). The facade
fronts the leader's store, so all members -- and their lessers, which resolve the
same shared spell -- land in the one team-store. `Creations` is not involved in
resolution and carries no cluster field. The exact spell-side pointer is wired in
Phase 3, where the borrowed-spell resolution is verified so a co-member borrowing
the spell lands on the facade.

### Active / disabled gate (one bool, on the facade)
- `cluster_creations` has a single `active` bool: active when a leader store is
  bound, disabled otherwise.
- `get_creation` / `add_creation` **raise** when disabled: a
  `unique_per_conduit_cluster` meld with no elected leader is a hard error.
- No lock, no snapshot. The `elect_/unelect_conduit_cluster_leader` transactions
  freeze all melds before they bind/unbind, so the facade is never re-targeted
  while a meld reads it. The `active` bool is the only guard.
- Binding the spell is always fine. The **compiler does not gain cluster
  awareness**: the `unique_per_conduit_cluster` emit lane reads the spell-side
  facade pointer live and lets the facade's disabled-raise propagate.

### Election (v1)
- **First conduit to join the cluster becomes the owner** (kept simple).
  `create_cluster` makes an empty (disabled) facade; the first `handle_join`
  binds the facade to the joiner's `Creations` and records it as owner.
- Subsequent joiners' cluster spells resolve through the same facade; no
  `Creations` change.
- (Explicit `elect_cluster_owner(...)` is a clean future extension; not v1.)

### Lifecycle / cleanup
- **Owner root cleaned or leaves** -> `facade.unbind()` (null the store ref; do
  NOT clean the owner's `Creations`) -> facade disabled -> cluster inert.
  (Transfer deferred.)
- **Member (non-owner) root cleaned or leaves** -> drop its `_cluster_creations`
  reference and remove it from cluster membership.
- **Cluster deleted** -> facade `cleanup()` (drop its reference; the store itself
  is owned/cleaned by the owner conduit).
- Conduit/root teardown must notify its cluster (at most one under exclusivity)
  so the facade unbinds and membership updates -- this is the main new lifecycle
  wire and where the care goes.

### Exclusivity (enables the single pointer)
- `ConduitCloud.add_conduit_to_cluster` rejects (fail-fast `ValueError`) a conduit
  already in a cluster. One cluster per conduit is what keeps the resolution a
  single binding (mirrors lineage's single root).

## Acceptance Criteria
- Five member conduits in one cluster, each melding the same
  `unique_per_conduit_cluster` spell, observe **one** shared instance (one
  `add_creation`, four reads), proven by identity assertion.
- Two clusters with the same spell yield **two** isolated instances.
- A `unique_per_conduit_cluster` meld with no elected owner raises a hard error
  (inert), while binding the spell succeeds.
- Adding a conduit already in a cluster to a second cluster raises `ValueError`.
- Owner leave/cleanup makes the cluster inert without cleaning the owner's
  `Creations` prematurely and without dangling references on any member.
- `unique`, `unique_per_conduit`, `many`, `unique_per_spell_space`,
  `unique_per_conduit_lineage` behavior unchanged; full unit + conduit/spellbook
  integration suites green.

## Implementation Plan (MRP, phased like the lineage sub-moves)

- **Phase 1 -- inert scaffolding.** Add the `cluster_creations` facade class
  (normal class with `cleanup()`, `Optional[Creations]`, `TYPE_CHECKING` import,
  rich docstring, owned by `ConduitCluster`). Add `Creations._cluster_creations:
  Optional[cluster_creations] = None` (slots, `__init__`, `del` in cleanup).
  No door change -> zero behavior change.
- **Phase 2 -- membership + binding.** Enforce exclusivity in
  `add_conduit_to_cluster`. First-join binds the facade to the owner's
  `Creations`; each join binds the joining root's `_cluster_creations` to the
  facade; leave drops it. Still no door change (inert).
- **Phase 3 -- flip the door.** The `unique_per_conduit_cluster` codegen lane
  stops using prebound `_owner_creations` and reads
  `caller_creations._root_creations._cluster_creations`, with the enabled/disabled
  gate (mirror of the lineage door flip, tasks #36/#39). Turns the feature on.
- **Phase 4 -- cleanup wire + transaction seam (no-op).** Owner/member root
  teardown -> facade unbind / ref drop / membership removal; cluster delete ->
  facade cleanup. Leader bind/unbind is wrapped in `elect_conduit_cluster_leader`
  / `unelect_conduit_cluster_leader` **transactions**. THIS epic defines those
  call sites and ships a **no-op strategy** (runs the facade rebind effect with no
  coordination) so the cluster system is functionally complete and testable in a
  single-threaded / quiescent setting. The **real coordinated strategy** (quiesce
  the affected member lineages -> safe window -> commit the rebind) is implemented
  by `mediator_builder_0` in the companion epic. My work stops cleanly at the
  no-op seam: the bind/unbind effect methods + the transaction call sites + the
  no-op strategy registration, with the required contract documented for the
  mediator.
- **Phase 5 -- tests + docs.** Unit (facade bind/unbind/enabled-disabled,
  exclusivity rejection, first-join election) + integration (five-member one
  instance, two-cluster isolation, inert hard-error, owner-leave dissolve).
  Update `src_architecture.md` / `src_components.md` existence model.

## Risks / Mitigations
- Risk: cleanup wire misses a teardown path -> dangling facade ref or stale owner
  store. Mitigation: route all root teardown through one cluster-notify seam;
  test owner-clean and member-clean explicitly.
- Risk: facade indirection on the cluster door path. Mitigation: cluster melds
  are not the hot path (binds/`unique` are); it is one delegated call behind the
  same `_root_creations` read lineage already does.
- Risk: a meld is mid-create against the owner store while it is unbound/disposed
  ("spell built, store yanked"). Mitigation: leader bind/unbind runs inside the
  `elect_/unelect_conduit_cluster_leader` transactions; the real strategy
  (mediator_builder_0) drains in-flight melds across the affected member lineages
  and gives a safe window for the facade rebind. NOTE: within THIS epic the
  strategy is a **no-op**, so full concurrency safety lands only when the
  companion epic ships -- until then the cluster store must be exercised
  single-threaded / quiescent (tests and the seam are built to that boundary).
  (`add_creation`/`get_creation` are lock-free today; the transaction envelope,
  not a new hot-path lock, is what makes the swap safe.)
- Risk: public-API drift. Mitigation: existence enum unchanged; behavior
  corrected; cluster admin API additions are additive.

## Open Questions
- Q1 (election): v1 uses first-join-as-owner. Confirm, or switch to an explicit
  `elect_cluster_owner(cluster, conduit)` state transition. USER CONFIRM.
- Q2 (inert error surface): hard error at the door is decided. Optionally also a
  friendlier earlier check at meld validation -- defer unless wanted.
- Q3 (empty-cluster persistence): a cluster whose owner left stays inert until
  deleted (its facade is empty). Confirm that is acceptable vs auto-deleting an
  empty cluster.

## Decision Log
- 2026-06-16 DECISION (with user): cluster instances live in an **owner
  conduit's** `Creations`, fronted by a cluster-owned `cluster_creations`
  **facade**; members bind their root to the facade and resolve through
  `_root_creations`. ("Master conduit makes more sense -- we don't break the
  pattern.")
- 2026-06-16 DECISION (with user): **exclusive** membership (one cluster per
  conduit) to keep the resolution a single binding and the code fast.
- 2026-06-16 DECISION (with user): `unique_per_conduit_cluster` is **inert until
  an owner is bound**; the meld door hard-errors when the binding is empty.
  Binding the spell is always allowed; the compiler stays cluster-agnostic.
- 2026-06-16 DECISION (with user): `unbind()` only nulls the facade's reference;
  it never cleans the owner's `Creations` (facade references, never owns).
- 2026-06-16 DECISION (with user): owner-leave **dissolves** (inert) in v1;
  in-cluster ownership transfer / re-home is **deferred** (a later one-write
  extension on the facade).
- 2026-06-16 DECISION (with user): owner bind/unbind is performed **through the
  mediator transaction system**, not hand-rolled gate/lock orchestration. The
  transaction coordinates the cross-conduit quiesce (a high-footprint, multi-
  member operation a single conduit's cleanup cannot do) and the facade rebind is
  its committed effect. Reuses the envelope clusters already use for
  `cluster_link`. This is why the gate-quiesce vs store-lock question is resolved
  as "neither directly" -- the transaction provides the safe window.
- 2026-06-16 DECISION (with user): WORK SPLIT. context_compass has no co-op /
  collaboration workflow, so the work is split by ownership rather than
  parallelized: THIS epic (compiler_strategy_0) builds the whole cluster system
  against a **no-op** `elect_/unelect_conduit_cluster_leader` transaction seam;
  the companion epic (mediator_builder_0) implements the real coordinated
  strategies. Contract-first, single shared seam, no overlapping file edits.

## Notes
- DATETIME: 2026-06-16T22:34:39Z
  TYPE: FACT
  CLAIM: `unique_per_conduit_cluster` storage is identical to `unique` today
    (prebound `_owner_creations.add_creation(spell_id, ...)`); it is only made
    "cluster" by `ConduitCluster` contract-sharing the binder's spell to members.
    Cluster-scoped root id includes owner_id, so storage is per-owner, not
    per-cluster.
  EVIDENCE:
  - src/.../codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:251
  - src/melder/aether/conduit/meld/conduit_meld.py:518-528
  - src/melder/aether/conduit/conduit_cluster.py:582-600 (_get_shareable_spells filters to the existence), :663 (_cluster_root_id)
  - src/melder/aether/aetheric_frame/conduit_cloud.py:435-485 (membership; multi-membership currently allowed)
  IMPACT: Multiple owners of the same spell -> one instance per owner; team-store
    semantic not delivered.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-06-16T22:34:39Z
  TYPE: DECISION
  AGENT: compiler_strategy_0
  CLAIM: Reuse the lineage `_root_creations` read-through so only root conduits
    carry a `_cluster_creations` binding and lessers/pools never get touched on
    any cluster state change. Facade indirection makes elect/dissolve/transfer a
    single write.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:86-92 (_root_creations default + intent)
  - src/melder/aether/conduit/conduit.py:307-322, 1590, 1695 (root/lesser/upgrade repoints)
  - src/melder/aether/conduit/spell_space/spell_space.py:130 (spellspace repoint)
  NEXT: user confirms Q1 (election); implement Phase 1 (inert scaffolding) for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Cluster team-store is the follow-on to the lineage resolver-root redesign and
reuses its machinery. `unique_per_conduit_cluster` today stores like `unique` and
fakes cluster scope via contract-sharing; this epic gives it a real cluster store
via an owner conduit's `Creations` fronted by a cluster-owned `cluster_creations`
facade. Member roots bind to the facade; lessers resolve through `_root_creations`;
the door hard-errors when the binding is empty (inert); the compiler stays
cluster-agnostic. Membership is exclusive (one cluster per conduit). Owner-leave
dissolves in v1; transfer/re-home and multi-cluster are deferred and shaped to be
one-write extensions on the facade.

---

# PHASE 3 HANDOFF (fresh-context resume)

> Written 2026-06-17 by compiler_strategy_0 at the end of an overloaded session,
> for a FRESH context to execute Phase 3 cleanly. The older "Design / Resolution"
> prose above (the "spell-side pointer / `spell._owner_creations`" wording around
> lines 88-110) is SUPERSEDED by the corrected model in this section. Where they
> conflict, THIS section wins. Read this section first.

## The one-sentence model (say it back before coding)
A `unique_per_conduit_cluster` spell's team instance lives in the ELECTED LEADER
conduit's root `Creations`. The cluster owns a `cluster_creations` facade that
fronts that leader store. The door for a cluster spell **gets the store from the
cluster's `cluster_creations` facade and uses it exactly like the `lineage` route
uses `caller_creations._root_creations`.** That is the entire job.

Verbatim user framing to anchor on (do not re-litigate these):
- "the point of the cluster_creations is just to use the root_creations inside
  it, for the elected conduit ... you reach into cluster_creations literally just
  get it and put it into creation_context."
- "you get it from the cluster_creations that was elected" -- NOT from the spell,
  NOT from `caller_creations`, NOT from `_owner_creations`.
- "your entire job for the unique_per_conduit_cluster defined spells is to reach
  into the facade and shove it into the creation_context door."
- "cluster is just the root creations" -> copy the `lineage` route.
- "the spell doesn't need to know about this object, `owner_creations` is only for
  uniques now."
- "creations should not know about cluster."

## What is ALREADY DONE (landed, inert, do not redo)
1. **The facade** -- `src/melder/aether/conduit/creations/cluster_creations.py`.
   `ClusterCreations(Cleanable)`. State: `_store: Optional[Creations]`,
   `_active: bool`. API: `bind(store)` (sets store + active), `unbind()` (clears,
   idempotent), `is_active()`, `get_creation(spell_id)`, `add_creation(spell_id,
   item, *, has_disposal_methods=False, disposal_methods=None)`. When `not
   _active`, `get_creation`/`add_creation` RAISE `RuntimeError("cluster_creations
   is disabled: no elected cluster leader.")`. No internal lock (by design --
   concurrency for bind/unbind comes from the mediator quiesce). `cleanup()`
   idempotent; references, never owns, the leader store.
2. **ConduitCluster ownership** -- `src/melder/aether/conduit/conduit_cluster.py`.
   `__slots__` has `cluster_creations`, `master_conduit_id`; `__init__` builds an
   empty `ClusterCreations()` and `master_conduit_id=None`; `cleanup()` cleans the
   facade and dels both. Cluster already has `members`, `shared_spells`,
   `handle_join`/`handle_leave`/`share_to_borrower`, `_get_shareable_spells`
   (filters existence == `unique_per_conduit_cluster`), `_cluster_root_id`.
   NOTE: join/leave do NOT yet fire elect/unelect (that is a Phase 3 call site).
3. **Exclusivity** -- `src/melder/aether/aetheric_frame/conduit_cloud.py`.
   `add_conduit_to_cluster` raises `ValueError` if the conduit is already in any
   cluster (one cluster per conduit) before `add_member`/`handle_join`.
4. **Mediator transaction machinery** -- companion epic
   `2026-06-16_cluster_leader_election_transactions_epic.md`,
   `elect_conduit_cluster_leader` / `unelect_conduit_cluster_leader` strategies
   are LANDED by mediator_builder_0. They quiesce the affected member lineages,
   then run the facade `bind(leader._creations)` / `unbind()` as the committed
   effect. THE QUIESCE IS THEIRS; you do not add locks for it.

Net effect today: the facade exists but NOTHING resolves through it. Cluster
spells still behave like `unique` (the old path). The tree is clean/green; this
is a safe reset point.

## What PHASE 3 must do (the only remaining work for this epic)

### Step A -- Door route: add a `cluster` route that copies `lineage`
File: `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/
shared_assets/creation_runtime_door_compiler.py`.
- `_build_no_overrides_lines` and `_build_with_overrides_lines` each have a
  `lineage` branch (no-overrides ~lines 629-664; overrides ~923-995). The lineage
  branch does: `root_creations = caller_creations._root_creations`, then
  get-or-create-once under `root_creations._lock`, then calls the inner
  `_no_overrides_executor(caller_creations, root_creations, False)` with the
  RESOLVED store.
- Add a sibling `cluster` branch that is the SAME body, except the resolved store
  comes from the elected facade instead of `caller_creations._root_creations`.
  Recommended (keeps it a literal lineage copy with a real lock): reach into the
  active facade to obtain the elected leader's `Creations`, then run the identical
  get-or-create-once-under-`_lock` body on that real `Creations`. The facade's
  `is_active()`/disabled-raise provides the inert hard-error for free.
- ONE detail to confirm with the user before writing (this is the only genuinely
  open point): the create-once race for two concurrent melds is handled by
  lineage via `root_creations._lock`. The facade has no lock. So either (a) the
  facade hands out its bound `Creations` to the route and the route locks that
  real store's `_lock` (RECOMMENDED -- byte-for-byte lineage, keeps `Creations`
  cluster-ignorant), or (b) add a `get_or_create_once(spell_id, factory)` to the
  facade delegating under `_store._lock`. Pick (a) unless the user prefers (b).
  Do NOT add a lock to the facade itself.

### Step B -- Route-key mapping: route cluster existence to the new route
- `unique_per_conduit_cluster` currently resolves to the `shared` route key (same
  lane as `unique`). Grep `resolve_route_key` and the existence->route mapping
  (it is computed in a codegen state/step, then read by the finalize steps).
  Map `unique_per_conduit_cluster` -> the new `cluster` route key.

### Step C -- Finalize steps: hand the facade in as the store
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/
  solo/steps/solo_finalize_creation_context_step.py` builds the door via
  `compile_creation_context_hooks_no_overrides_executor(... owner_creations=
  root_spell._owner_creations ...)` (lines 64 and 74).
- For the `cluster` route only, the store the door should resolve through is the
  cluster's `cluster_creations` facade, NOT `root_spell._owner_creations`
  (`_owner_creations` is unique-only now). The finalize step needs the cluster's
  facade for the spell's owner conduit. Source it from the owner conduit's
  cluster (exclusivity => at most one). Do the equivalent in the GENERALIZED and
  MANY_ONLY finalize steps (siblings under
  `.../codegen_creation_system/strategies/{generalized,many_only}/steps/`).
- Reminder: the door is built LAZILY on first meld, which is necessarily AFTER
  the conduit has joined the cluster, so the facade is always available at build
  time. Do not invent a "rebuild on join" step -- there is none, and the facade
  is a stable object whose target is swapped by bind/unbind.

### Step D -- Meld liveness probe: split cluster out
- `src/melder/aether/conduit/meld/conduit_meld.py`, `meld_existing_spell`
  liveness probe (~lines 518-533) currently groups `unique`/`cluster`/`lineage`
  reading `target_spell._owner_creations`. Split `cluster` out: its liveness
  must consult the elected facade (active? has the instance?) instead of
  `_owner_creations`. `meld()` resolves `target_spell` via `_resolve_spell_by_id`
  (`meld.py:1253` -- local pool, then `_spells_by_id`, then
  `_contracted_spells_by_id`), so a borrowed cluster spell resolves to the
  OWNER's Spell object; co-members converge on the owner's spell, which is why a
  single facade per cluster is correct.

### Step E -- Call sites: fire elect on first join, unelect on leader leave
File: `src/melder/aether/conduit/conduit_cluster.py` (compiler_strategy_0 owns
these call sites; the strategies themselves are mediator_builder_0's, landed).
- `handle_join`: when the cluster gains its first member (or per the v1
  first-join-as-leader rule), run the `elect_conduit_cluster_leader` transaction
  for that conduit; record `master_conduit_id`; the transaction's committed
  effect calls `self.cluster_creations.bind(leader._creations)`.
- `handle_leave` / leader teardown: when the elected leader leaves or is cleaned,
  run `unelect_conduit_cluster_leader`; its effect calls
  `self.cluster_creations.unbind()`; clear `master_conduit_id`; cluster goes
  inert (v1 dissolve -- no transfer).
- Use `conduit.transaction("cluster_link", conduits=[...])`-style entry the
  cluster already uses for sharing; confirm the exact transaction entry point and
  strategy names with the companion epic before wiring.

## What `cluster_creations` is FOR (so the model doesn't drift again)
> SUPERSEDED (2026-06-20): the as-built facade lives PER ROOT CONDUIT
> (`Conduit._cluster_creations`), not as a single cluster-owned facade. The
> swappable-handle reasoning below still holds, but `bind`/`unbind` happen on
> each member's facade via `bind_`/`unbind_elected_leader`. See "## Resolution
> (Closure)" at the top.
The leader is a RUNTIME cluster fact -- the spell and the caller do not and must
not know which conduit is the elected leader. The facade is the cluster's single,
swappable handle to "whoever the leader is right now." That is exactly why the
store must come FROM the facade at door-resolve time and not be captured from the
spell or the caller: elect/unelect swap the facade's target (`bind`/`unbind`)
under the mediator's frozen-meld window, and every cluster spell transparently
follows. `bind` = elect points the empty facade at the leader's `Creations`;
`unbind` = unelect clears it (inert). `Creations` and `Spell` stay cluster-blind.

## Reading list (open these, in this order, in the fresh context)
1. THIS section + the Design/Decision Log above (but treat the old "spell-side
   pointer" wording as superseded -- see the banner at the top of this section).
2. `src/melder/aether/conduit/creations/cluster_creations.py` -- the facade (done).
3. `src/melder/aether/conduit/conduit_cluster.py` -- cluster ownership + join/
   leave + `_get_shareable_spells` + `_cluster_root_id` (call sites land here).
4. `src/melder/aether/aetheric_frame/conduit_cloud.py` -- `add_conduit_to_cluster`
   exclusivity + cluster registry + `get_clusters_for_conduit`.
5. `src/.../codegen_creation_system/shared_assets/creation_runtime_door_compiler.py`
   -- THE template. Study the `lineage` route (no-overrides ~629-664; overrides
   ~923-995). The `cluster` route is a copy of it.
6. `src/.../codegen_creation_system/strategies/solo/steps/
   solo_finalize_creation_context_step.py` -- where the store is handed to the
   door (`owner_creations=root_spell._owner_creations`, lines 64/74). Plus the
   generalized + many_only sibling finalize steps.
7. `src/melder/aether/conduit/meld/conduit_meld.py` -- meld flow + liveness probe
   (~518-533) to split cluster out.
8. `src/melder/aether/conduit/meld/meld.py` -- `_resolve_spell_by_id` (1253):
   proves borrowed cluster spells resolve to the owner's Spell.
9. `src/melder/aether/conduit/creations/creations.py` -- the store; `_root_creations`
   field; lock-free `get_creation`/`add_creation` (`add_creation` raises on
   duplicate key -> this is why create-once-under-`_lock` matters).
10. `2026-06-16_cluster_leader_election_transactions_epic.md` + the landed
    elect/unelect strategy files -- confirm transaction entry + strategy names
    before wiring Step E.

## Hard DON'Ts (each was a mistake this session; do not repeat)
- DON'T put the facade or store on the `Spell`. The store is sourced at the
  finalize/door from `cluster_creations`. The spell stays cluster-blind.
- DON'T touch `Creations` to know about clusters. It stays cluster-ignorant.
- DON'T repoint `_owner_creations` for cluster. `_owner_creations` is unique-only.
- DON'T add a lock to the facade. Use the leader `Creations._lock` for create-once
  (Step A), and trust the mediator quiesce for bind/unbind.
- DON'T add snapshots, defensive None-guards, broad `try/except: pass`, or extra
  aliases (alias only if >2 refs). Trust `check_cleaned()` and deterministic
  cleanup. Synaptic rules: no PEP 604 unions (use Optional/Union), TYPE_CHECKING
  imports, approval-loop (no edits without user confirmation).
- DON'T invent a "rebuild door on join" step. The door builds lazily on first
  meld, after join; the facade is stable.
- DON'T re-derive the design from scratch -- it is settled. Say the one-sentence
  model back to the user, confirm the single open point (Step A lock choice),
  then implement A->E.

## Phase 4 / 5 (after Phase 3)
- Phase 4 cleanup wire: owner/member teardown -> facade unbind / membership
  removal; cluster delete -> facade cleanup. (Election bind/unbind already runs
  through the mediator transactions -- the no-op seam in the original plan is
  obsolete now that mediator_builder_0 landed the real strategies.)
- Phase 5: tests (five-member one-instance identity; two-cluster isolation; inert
  hard-error; owner-leave dissolve; exclusivity rejection) + docs
  (`src_architecture.md` / `src_components.md` existence model). Cannot run 3.14t
  tests in this environment -- hand to user for validation (report "Not run.").
