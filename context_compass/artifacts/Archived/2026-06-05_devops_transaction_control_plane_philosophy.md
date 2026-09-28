# DevOps Transaction Control-Plane Philosophy

## Purpose
This artifact captures the current philosophy questions for the DevOps
transaction control plane so later implementation work can route back to one
retained model instead of rebuilding it from chat.

## Why This Exists
The current difficulty is not that the repo lacks classes. The difficulty is
that we still have unresolved responsibility boundaries:

- why DevOps state needs to exist at all
- what counts as a meaningful change to that state
- what the mediator is really orchestrating
- what the embargo system is actually acquiring
- when pending/queue/timeout behavior should happen

If we do not answer those questions explicitly, later code will smuggle those
answers in accidentally and we will keep refactoring around symptoms.

## What We Know
- `TransactionMediator` should be the front door for transaction requests.
- `TransactionMediator` can act as the orchestrator for transaction state
  transitions without introducing a second top-level orchestrator object.
- `DevopsInformationRegistry` should stay a small mirrored truth store:
  - spellbook ↔ normal root conduit
  - provider ↔ borrower conduits
  - cluster ↔ normal conduits
  - active transactions by id / identity / type / scope
- `DevopsIdentity.update_metadata(...)` should stay local-only.
- Root-session config clutter (`warn`, `change_control_mode`,
  `allow_multiple_root_transactions`) has already been removed from the active
  runtime/config surfaces.

## What Problem We Are Actually Solving
We are not trying to build a generic reporting plane.
We are trying to make transaction admission correct and cheap.

That means the DevOps control plane exists to answer:

- what is the current mirrored runtime reality?
- what scopes does this request need?
- do those scopes overlap active work?
- if they overlap, should the request wait or fail?
- when active work finishes, which pending requests should be retried?

If a piece of DevOps state does not help answer one of those questions, it is
probably not worth keeping fresh on the hot path.

## What We Are Not Trying To Build
We are not trying to build:
- a generic reporting system
- a giant always-fresh mirror of every runtime detail
- a second full object graph that shadows the actual runtime one-for-one
- a global root queue that serializes all work
- a second top-level orchestrator beside the mediator

Those all add cost faster than they add useful control-plane truth.

## Responsibility Map

### `DevopsInformationRegistry`
- Owns mirrored control-plane truth.
- Should not decide admission.
- Should not rebuild large relation sets from metadata churn.
- Should expose cheap lookup surfaces for strategies and mediator.
- Should behave like a small mirrored operational graph, not like a periodic
  reporting cache.

### `DevopsInformationStrategy`
- Should consume or reconcile the DevOps information state we actually care
  about.
- Should answer state/view questions for the mediator without pushing logic
  into runtime hot paths.
- Should stay separate from transaction-family strategy logic.
- Is the likely owner of "consume pending DevOps updates and produce a current
  enough mirrored view for admission."

### `TransactionStrategy`
- Defines what one transaction type touches.
- Computes blast radius and claim scope.
- Decides what overlap matters and what should be queueable.

### `EmbargoManager`
- Should act as the permission gate over claimed scopes.
- Owns acquired scopes, blocked scopes, and timeout-related pending state.
- Should not be thought of as a giant "stop all root work" switch.
- The important question is whether it acquires the specific scopes a request
  needs, not whether a root transaction exists somewhere.

### `TransactionMediator`
- Front door for requests.
- Owns transaction request state transitions.
- Should coordinate:
  - information strategy
  - transaction strategy
  - conflict / embargo decision
  - pending / admitted / active / timeout / release
- Should be the top-down owner of transaction request state transitions.
- Does not need a second top-level orchestrator if it already owns the request
  state machine.

### `TransactionSession`
- Owns the live admitted state after a request wins permission.
- Keeps commit/abort/rollback mechanics tied to one admitted request.

## Current Runtime Composition Problem
Today the pieces already exist, but the composition is not fully settled:

- the mediator is the front door, but its remaining queue fallback is still
  coarser than the scope model we want
- the registry now stores more honest mirrored truth, but we have not yet
  defined when and how real information strategies consume deferred updates
- the transaction strategies know how to compute affected state for current
  families, but we have not yet decided how much of the concurrency decision
  they should own
- the embargo system stores blocked scopes, but we have not yet decided how it
  should coordinate pending ordering and retry

So the system is currently neither fully top-down nor fully event-driven. It
has the pieces of both, and this artifact is about defining how they fit.

## The Core Design Question
What actually counts as a meaningful DevOps change?

We do not want to mirror everything.
We do not want generic reporting churn.
We want to update only what matters for:
- transaction planning
- conflict checks
- embargo checks
- active transaction lookup

## Why We Might Need To Update DevOps State At All
We only need to update DevOps state when the answer to a transaction-admission
question could change.

That means updates matter when:
- a normal root conduit appears or disappears
- spellbook ↔ root-conduit ownership changes
- provider ↔ borrower edges change
- cluster membership of normal conduits changes
- an active transaction starts or ends
- a request claims scopes that should become visible to conflict/embargo logic

Updates probably do not matter when:
- a lesser conduit churns
- a spellspace churns
- descriptive metadata changes but no admission-relevant relation changes
- a runtime object wants to report a nicer description of itself

## Concrete Examples

### Example: `bind` on `ConduitA`
What probably matters:
- `spellbook:A`
- `conduit:A`
- maybe one `binding:<frame>:<name>` scope when the bind shape is that narrow

What probably does not matter:
- unrelated conduits
- unrelated clusters
- lesser conduits
- spellspaces

This is the archetype for a low-blast-radius request.

### Example: `link(A, B)`
What probably matters:
- `conduit:A`
- `conduit:B`
- `conduit_ward:A`
- `conduit_ward:B`
- maybe contract-specific scopes for the keys being linked

This is a medium-blast-radius request because it touches two peers and both
ward surfaces.

### Example: `cluster_link`
What probably matters:
- cluster id
- all participating normal conduits
- their wards
- their owning spellbooks when strategy planning depends on them

This is higher blast radius than `bind` because a cluster operation can fan out.

### Example: `transfer_ownership(A, B)`
What probably matters:
- `conduit:A`
- `conduit:B`
- both wards
- both spellbooks
- provider/borrower relations that will be changed or invalidated
- cluster relations if the transferred spell participates in shared cluster state

This is the archetype for a high-blast-radius request.

## What We Probably Care About
- root conduit registration / unregistration
- spellbook ↔ root conduit ownership
- provider ↔ borrower edges
- cluster membership of normal conduits
- active transaction registration / release
- explicit scope claims

## What We Are Probably Over-Caring About Today
- eager metadata refresh
- metadata-derived relation rebuilds
- broad root-session gating before real overlap checks
- using DevOps state as generic reporting instead of admission truth

## What We Probably Do Not Care About
- lesser conduit churn
- spellspace churn
- generic descriptive metadata
- periodic full refresh
- broad metadata-driven relation rebuilds

## Update Classification Questions
- Which events are `IGNORE`?
- Which events are `LOCAL_ONLY`?
- Which events are `DEFERRED_STRUCTURAL`?
- Which events are `IMMEDIATE_STRUCTURAL`?

We need to define this before the first real information strategy can be
implemented cleanly.

Working interpretation:
- `IGNORE`
  - no admission consequence
- `LOCAL_ONLY`
  - object-local change, no registry consequence
- `DEFERRED_STRUCTURAL`
  - relevant to admission, but can wait until a later reconciliation boundary
- `IMMEDIATE_STRUCTURAL`
  - must be reflected before another request can be admitted safely

We have not yet assigned every real runtime event into one of these buckets.

Candidate classification examples:

- `IGNORE`
  - lesser conduit attach/detach when admission truth does not consume them
  - spellspace activation/deactivation

- `LOCAL_ONLY`
  - descriptive `DevopsIdentity.update_metadata(...)`
  - human-facing label changes

- `DEFERRED_STRUCTURAL`
  - ownership-affecting updates that can wait until the next admission boundary
    without making immediate admission wrong

- `IMMEDIATE_STRUCTURAL`
  - transaction begin/end
  - provider ↔ borrower edge changes
  - cluster membership changes when strategies depend on them immediately
  - root conduit registration/unregistration

## Admission Philosophy
The key question is whether queueing is the first gate or whether scope
acquisition is the first gate.

Current leaning:
- scope acquisition / embargo is the real gate
- queueing should be what happens after a request is blocked by overlap
- unrelated work should proceed in parallel

That means admission should likely look like:
1. mediator receives request
2. information strategy makes mirrored truth current enough
3. transaction strategy computes claims
4. embargo/conflict decides whether those claims can be acquired
5. if yes:
   - request becomes active
6. if no:
   - request becomes pending or times out

Important boundary:
- the first question should be "can I acquire these scopes?"
- not "is another root transaction already alive?"

That means:
- admission should be serialized
- execution should not be serialized globally
- only overlapping claims should interfere

## State Machine Questions
We likely need explicit request states such as:
- `new`
- `planned`
- `blocked`
- `pending`
- `admitted`
- `active`
- `committing`
- `committed`
- `aborting`
- `aborted`
- `timed_out`

Open question:
- does pending block a thread,
- or does it return a handle/future and free the thread?

Related question:
- if pending blocks a thread, how expensive is that under real multi-threaded
  load?
- if pending returns a handle, who owns wakeup and retry?

Potential states we may also need:
- `reconciling`
- `waiting_for_retry`
- `rejected`

Those are not decided yet, but we may need them if we want cleaner reasoning
around delayed requests.

## Ordering Questions
We still need to answer:
- how pending requests are ordered
- whether ordering is global or scope-local
- when a pending request is retried
- who wakes it up

The likely direction is:
- scope-local ordering
- not one global FIFO across unrelated work

We still need to define:
- whether order is per scope or per overlap class
- whether one request can wait on multiple scopes at once
- how retries are de-duplicated when multiple blocking scopes are released
- whether FIFO is even always desirable, or whether some strategies need a more
  constrained fairness model

## Things We Are Struggling With
- distinguishing mirrored truth from derived reporting
- deciding what events should update the registry at all
- deciding how much of the current bottom-up event model to keep
- defining the top-down transaction state machine without adding redundant
  objects
- deciding whether queueing survives at all in coarse form
- deciding whether "queue" is even the right language, or whether this is
  really "pending acquisition of claimed scopes"

## Current Pressure Points
- We want maximum speed, which pushes us toward fewer updates and more reads.
- We want truthful enough control-plane state, which pushes us toward some
  explicit mirrored reality.
- We do not want the hot path to maintain generic reporting state.
- We do want transaction admission to have enough truth to make real overlap
  decisions.
- We need a top-down request state machine, but we do not want to invent a
  second top-level orchestrator object when the mediator can own that flow.

## Candidate Data Structures
These are candidate shapes, not final decisions.

- `identities_by_key`
- `objects_by_key`
- `spellbook_to_conduits`
- `conduit_to_spellbook`
- `provider_to_borrowers`
- `borrower_to_providers`
- `cluster_to_conduits`
- `conduit_to_clusters`
- `transactions_by_id`
- `transaction_ids_by_identity`
- `transaction_ids_by_scope`
- maybe `pending_request_ids_by_scope`
- maybe `request_to_claimed_scopes`
- maybe `request_to_blocking_scopes`

The open question is not whether we can build these. The open question is which
of them must stay hot and which can be deferred or derived.

## Models We Are Explicitly Suspicious Of
- one global FIFO over all root requests
- periodic full registry refresh
- eager metadata-driven relation rebuilds
- letting transaction strategies also maintain the registry directly
- putting lesser-conduit churn into the mirrored reality by default
- forcing the hot path to keep reporting-perfect state

## What "Fresh Enough" Probably Means
The registry does not need to be perfect all the time.
It needs to be fresh enough that transaction admission is truthful.

So the likely rule is:
- local-only events can stay local
- deferred structural events can accumulate
- the admission boundary can force reconciliation when a request family needs it

That is different from "always fresh" and different from "rarely updated."
It is demand-shaped freshness.

## Questions To Answer Before Bigger Implementation
1. What exact scope vocabulary should transaction strategies emit?
2. Which DevOps events are immediate, deferred, local-only, or ignored?
3. Does pending block a thread or return a resumable handle?
4. Should queueing be scope-local only?
5. What is the first real `DevopsInformationStrategy`:
   - update consumption
   - state view building
   - or both?
6. Does `EmbargoManager` need to grow into the true scope-acquisition engine?
7. Should `TransactionMediator` own retry/wakeup for pending requests directly?
8. When a request becomes pending, what exact object represents that pending
   state and who owns its timeout?
9. Should the registry itself expose prebuilt node views, or should
   information strategies derive those from the mirrored maps on demand?
10. How much state can remain deferred before admission truth becomes too stale?
11. Should the information strategy layer expose read-model results directly, or
    only mutate the registry and let the mediator/strategies read raw maps?
12. Which event families should be capable of waking pending requests?
13. What is the smallest useful abstraction for a pending transaction object?

## Current Direction
The current best direction is:
- keep `TransactionMediator` as the top-down transaction orchestrator
- keep `DevopsInformationRegistry` small and cheap
- use `DevopsInformationStrategy` beside the registry, not inside transaction
  strategies
- make scope acquisition the real gate
- let unrelated work proceed in parallel

Short version:
- mirrored truth should stay small
- updates should be classified
- strategies should mostly read
- mediator should orchestrate request state
- embargo should gate scope acquisition
- pending/timeout should happen only when scope acquisition fails

## Practical Middle Ground
The likely middle ground is:
- no giant reporting plane
- no giant orchestrator class beyond the mediator
- a small honest mirrored truth
- explicit event classes
- admission-time reconciliation when needed
- scope acquisition as the real gate
- pending state only for requests that truly overlap active or embargoed scopes

## Status
This is a philosophy artifact, not a final design document.
Anything not already landed in code should be treated as design direction, not
runtime truth.
