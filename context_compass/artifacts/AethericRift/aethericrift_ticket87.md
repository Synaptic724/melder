# [Ticket] AethericRift & RiftDomain – Final RFC (Workspaces, ACLs, Auth, and AI Usage Modes)

**Labels:** `melder-core`, `aetheric-rift`, `rift-domain`, `conduits`, `scopes`, `acl`, `ai-sre`, `design-rfc-final`

---

## 1. Intent / Scope

This is the **final high-level RFC** for the AethericRift / RiftDomain system before implementation tickets.

It captures:

* The **structural roles** of:

  * `AethericRift` (control plane / router),
  * `RiftProfile` (principal),
  * `RiftDomain` (workspace / remote interface),
  * `Conduit` / `Scope` / `Creation` (DI runtime),
* The **ACL stack** and how it gates power:

  * `SpellACL`, `ConduitACL`, `RiftDomainACL`, `RiftProfileACL`.
* The **auth/identity story**:

  * internal calls (no token, profile passed explicitly),
  * external/API calls via `RiftAuthKey` → `RiftProfile`.
* The **RiftDomain workspace semantics**:

  * what lives inside a domain (registries, weakref caches),
  * what it never owns (lifetimes, strong refs),
  * generic method contracts.
* The **AI usage modes**:

  * Observation,
  * Intervention (incident response),
  * Reconstruction (lab repro),
  * Mutation (graph changes under control).

This is not code; it’s the **behavioral contract** the implementation must follow.

---

## 2. Core Structural Roles

### 2.1 AethericRift – Control Plane & Router

**AethericRift** is the **entrypoint** for remote/agent calls into Melder.

Responsibilities:

* **Registry**

  * Tracks all `RiftProfile`s.
  * Tracks all `RiftDomain`s.
  * Knows about Conduits and how domains attach to them.

* **Identity & routing**

  * For internal calls: accepts `(profile_id, domain_id, op)` directly.
  * For external/API calls: maps `RiftAuthKey` → `profile_id` (+ allowed domains).
  * Resolves the target `RiftDomain` and forwards the operation.

* **Top-level ACL gate**

  * For each operation, evaluates the four ACL slices:

    * `SpellACL` (if applicable),
    * `ConduitACL` (if applicable),
    * `RiftDomainACL`,
    * `RiftProfileACL`.
  * If any denies, the op is rejected before touching a domain.

Constraints:

* No worker pools.
* No queues.
* No background threads.
* **All calls are synchronous** on the caller’s thread.

### 2.2 RiftProfile – Principal / Role

A **RiftProfile** represents **who** a call is acting as:

* AI agent persona (e.g. `ai_prod_observer`, `ai_mutation_lab`).
* Human / external service identity, if mapped.

Holds:

* `profile_id`.
* Global capabilities / caps (VIEW / STATE / GRAPH tiers, destructive ops allowed or not).
* Set of allowed `RiftDomain` ids (`allowed_domain_ids`).
* Optional per-domain limits (e.g. VIEW-only in prod domains, GRAPH allowed in lab domains).

`RiftProfileACL` answers:

> "Given this profile, across all domains, what classes of operations are ever allowed?"

### 2.3 RiftDomain – Workspace / Remote Interface

A **RiftDomain** is a **workspace** bound to one or more Conduits and a curated set of Spells, with a specific ACL slice.

It is the **remote interface** the AI interacts with.

Exposed operations (fixed surface):

* `describe_rift`
* `list_spells`
* `describe_spell`
* `invoke_spell`
* `get_attr`
* `set_attr`
* `list_conduits`
* `list_open_conduits`
* `close_conduit` (domain-level detach; real shutdown is via control spells)

Responsibilities:

* Maintain a **static registry** of:

  * Spells exposed in this domain (`spell_key → SpellDescriptor`).
  * Conduit attachments (`conduit_id → ConduitBinding`).
  * Domain ACL slice (what’s visible, what tier per spell).

* Maintain a **dynamic working set** (optional accelerators):

  * Weakrefs to recently used Creations keyed by `(spell_key, scope_id)` and/or `handle_id`.
  * Cached **attr/method descriptors** (what’s legal, not values).

* Translate generic calls into real work:

  * Resolve Spell → Conduit → Scope → Creation.
  * Invoke methods or read/write attrs on live objects.

Constraints:

* No threads, no queues.
* Re-entrant and thread-safe via minimal locking on internal maps.
* Does **not** own lifetimes; Conduits/Scopes do.

### 2.4 Conduit / Scope / Creation – DI Runtime

* **Conduit**

  * Owns **Scopes** (lifetime partitions).
  * Owns **Creations** (real DI objects) within those scopes.
  * Implements Existence rules (per-scope singletons, per-call, etc.).
  * Exposes resolution / creation APIs used by RiftDomain.

* **Scope**

  * A grouping/lifetime boundary inside a Conduit.
  * "All Creations in this Scope live and die together."

* **Creation**

  * A realized object for a Spell within a Scope.
  * Strongly owned by Conduit/Scope; never by RiftDomain.

Ownership invariant:

```text
Conduit/Scope:
    strong_owner(Creation)

RiftDomain:
    weak_owner(Conduit)
    weak_owner(Creation)
    strong_owner(Spell/Conduit metadata + descriptors)
```

If a Conduit/Scope dies, RiftDomain’s weakrefs simply go dead and operations degrade via errors.

---

## 3. ACL Stack – Power Boundaries

For any operation, **effective permission** is:

> `SpellACL ∧ ConduitACL ∧ RiftDomainACL ∧ RiftProfileACL`
>
> If any denies, the operation is denied.

### 3.1 SpellACL – Spell Surface

Answers:

> "What can *anyone* ever do to this Spell?"

Defines:

* Is the Spell exposable at all?
* Which methods are remotely invokable.
* Which attrs are readable/writable.
* Which operation tiers are allowed for this spell:

  * `VIEW` – inspect graphs/metadata.
  * `STATE` – invoke + tweak state/config.
  * `GRAPH` – structural change, override, mutation.

`SpellACL` is a **hard cap** per Spell.

### 3.2 ConduitACL – Lifetimes & Scopes

Answers:

> "What can be done to Scopes and Creations inside this Conduit?"

Defines whether calls may:

* Open new scopes.
* Close scopes.
* Create new Creations in a given scope.
* Destroy Creations.
* Shut down / clean the Conduit itself.

ConduitACL is about **lifetime and scope control**, not method surfaces.

### 3.3 RiftDomainACL – Workspace Slice

Answers:

> "What subset of the universe is visible in this Domain, and to what degree?"

Defines:

* Which Spells appear in `list_spells`.
* For each Spell:

  * effective tier in this domain (often a subset of SpellACL).
* Which Conduits appear in `list_conduits` / `list_open_conduits`.
* Whether `close_conduit` is allowed for attached Conduits.
* Whether infra/control spells (SpellSystemStates, ChangeControl, etc.) are exposed.

### 3.4 RiftProfileACL – Principal Caps

Answers:

> "What is this profile allowed to do **anywhere**?"

Defines:

* Global tier caps per profile (e.g. `ai_prod_observer` can never do GRAPH anywhere).
* Whether profile may:

  * close Conduits,
  * open scopes,
  * call destructive control spells.
* Optional domain tags (e.g. prod domains VIEW-only, lab domains GRAPH allowed).

`RiftProfileACL` is the outer guardrail; it can only restrict further.

---

## 4. Auth / Identity – Internal vs External

### 4.1 Internal (In-Process / Trusted)

In the internal Melder + CommandOps world, we keep auth **simple**:

```python
aetheric_rift.handle_call(profile_id: str, domain_id: str, op: RiftOperation)
```

* The caller (CommandOps agent, app code) is trusted to pass the correct `profile_id` and `domain_id`.
* AethericRift uses the ACL stack to decide whether the op is allowed.
* No session tokens are required internally.

### 4.2 External (HTTP / gRPC / Executor on Another Machine)

At a network/API boundary, we introduce **RiftAuthKey** as a simple identity mapping.

**RiftAuthKey:**

* A random high-entropy secret string given to an integration/agent.
* Stored server-side only as `SHA256(key)`.
* Maps to:

  ```text
  key_hash -> {
      profile_id,
      allowed_domain_ids,
      enabled: bool,
      metadata: ...
  }
  ```

**Flow:**

1. Client (executor) calls HTTP/gRPC endpoint with header, e.g.:

   ```text
   Authorization: RiftKey <raw_key>
   ```

2. Gateway:

   * Computes `key_hash = SHA256(raw_key)`.
   * Looks up `key_hash`.
   * If missing or disabled → 401/403.
   * Resolves `profile_id` and `allowed_domain_ids`.

3. Gateway computes/chooses `domain_id` (from path/params) and checks it is allowed.

4. Gateway calls internal:

   ```python
   aetheric_rift.handle_call(profile_id, domain_id, op)
   ```

**Important:**

* Keys are **integration glue**, not core.
* Inside AethericRift, everything is still expressed in terms of `profile_id` + `domain_id` + `op`.
* No complex sessions; keys are static by default (can be rotated/disabled manually).

---

## 5. RiftDomain Workspace Semantics

### 5.1 Static Registry

Each `RiftDomain` holds:

* `spell_registry: spell_key -> SpellDescriptor`

  * Contains:

    * SpellIndex / lineage info.
    * Which Conduit(s) can realize it.
    * Allowed methods/attrs (post-ACL).
    * Existence / resolution hints.

* `conduit_bindings: conduit_id -> ConduitBinding`

  * Contains:

    * `ref = weakref.ref(conduit)`.
    * ConduitACL slice effective for this domain.
    * Attach mode (direct / linked / lab surrogate, etc.).

* `domain_acl_slice`

  * Effective per-spell tier and visibility.

This is the **toolbox catalog** for the workspace.

### 5.2 Dynamic Working Set (Weakrefs & Caches)

RiftDomain maintains:

* **Creation cache** (best-effort):

  ```python
  self._creations[(spell_key, scope_id)] = weakref.ref(obj)
  # optionally: handle_id -> weakref(obj)
  ```

* **Last-known scope per spell** (optional accelerator):

  ```python
  self._last_scope_for_spell[spell_key] = scope_id
  ```

* **Attr/method descriptors** (metadata, not values):

  ```python
  self._attr_descriptors[(spell_key, attr_path)] = AttrDescriptor(...)
  ```

Behavior:

* Weakrefs are **never** relied on for correctness:

  * If `ref()` is `None`, it is treated as cache miss + `CreationGone` or `ScopeExpired`.
* All lifetimes are controlled by Conduits/Scopes.
* Caches exist solely to:

  * reduce resolution cost,
  * give the AI a stable handle for ongoing interactions, as long as the underlying objects live.

### 5.3 Ownership & Lifetimes

* Conduits/Scopes own Creations strongly.
* RiftDomain:

  * must **never** keep a strong ref to a Creation or Conduit.
  * must respond gracefully to dead weakrefs:

    * `ConduitGone` if Conduit weakref is dead.
    * `ScopeExpired` / `CreationGone` if Creation weakref is dead.

---

## 6. Generic Operations – Behavioral Contracts

High-level behavior for the key RiftDomain methods.

### 6.1 `describe_rift`

Purpose:

> Give the AI full context for this workspace.

Should include:

* `domain_id` / `rift_id`.
* `frame_id` (AethericFrame).
* Tags (e.g. `["prod", "orders"]`, `["lab", "mutation"]`).
* Capability summary (VIEW / STATE / GRAPH in this domain).
* List of attached Conduits (ids + high-level roles).
* Optional notes.

### 6.2 `list_spells`

Purpose:

> List the Spell entrypoints visible in this domain.

Filtered by:

* SpellACL,
* DomainACL,
* ProfileACL.

Returns a list of descriptors:

* `spell_key`,
* SpellIndex / lineage summary,
* kind (service, infra-control, helper, etc.),
* optional tags.

### 6.3 `describe_spell`

Purpose:

> Provide detailed information about a spell’s surface and topology.

Includes:

* Identity:

  * `spell_key`, SpellIndex, role (root/helper/infra).
* Structural info (from Phase 5 blueprints):

  * dependencies, DAG info,
  * normal + contract sockets.
* Remote surface:

  * which methods are invokable here,
  * which attrs are visible and whether they’re readable/writable,
  * effective tier (VIEW/STATE/GRAPH) in this domain.

### 6.4 `invoke_spell`

Purpose:

> Call a method on a Spell in this domain.

Inputs (conceptual):

* `spell_key`.
* `method` (defaults to canonical entrypoint if omitted).
* `args` / `kwargs`.
* optional `context` (e.g. scope hint, tenant, mission).

Behavior (high-level algorithm):

1. Resolve `SpellDescriptor` from `spell_key`.
2. Resolve `ConduitBinding` (Conduit weakref, attach mode, ACL slice).
3. Check all ACL (Spell / Conduit / Domain / Profile) allow this method at this tier.
4. Resolve Scope (based on Existence + context + domain config).
5. Attempt to reuse a cached Creation via weakref keyed by `(spell_key, scope_id)`:

   * If live: use it.
   * If dead or missing: use Conduit to resolve/create a Creation.
6. Invoke method synchronously on the current thread.
7. Cache weakref for future calls.

Error examples:

* `SpellNotFound` / `MethodNotFound`.
* `AccessDenied` (tier/ACL mismatch).
* `ConduitGone` (Conduit weakref dead).
* `ScopeExpired` / `CreationGone` (no live object for the chosen scope).

### 6.5 `get_attr` / `set_attr`

Purpose:

> Read/write attrs on Spell surfaces or Creations visible in this domain.

Targeting options (must be defined precisely in implementation tickets):

* Spell-level attr (config/meta) per Conduit/Scope.
* Creation-level attr for a particular instance (via `(spell_key, scope_id)` or handle).

Behavior:

* Resolve target Spell/Creation via the same algorithm as `invoke_spell`.
* Use `AttrDescriptor` to:

  * confirm visibility,
  * confirm readability/writability,
  * optionally enforce type/shape.
* Perform `getattr`/`setattr` on the live object.

ACL:

* SpellACL: attr exposed/writable?
* DomainACL: allowed tier (VIEW/STATE/GRAPH) for this attr.
* ProfileACL: profile allowed to do STATE/GRAPH in this domain?
* ConduitACL: does this Conduit allow state mutation from this domain?

### 6.6 `list_conduits`

Purpose:

> Show the Conduits this domain is bound to.

Returns descriptors containing at least:

* `conduit_id`.
* attach mode (direct/link/lab/etc.).
* role/label (e.g. `"prod_orders"`, `"lab_mutation_universe"`).

### 6.7 `list_open_conduits`

Preferred semantics:

> Show Conduits plus the Scopes currently visible in this domain.

Each entry:

* `conduit_id`.
* `scopes`: list of scope ids the domain can see / target.

Useful for lab domains with multiple concurrent experiment scopes.

### 6.8 `close_conduit`

Purpose:

> Detach this domain from a Conduit.

**Important:** In this RFC, `close_conduit` is defined as:

* Domain-level detach only:

  * Conduit may continue to exist for other domains.
  * This domain will no longer list/use it.

Actual Conduit shutdown/cleanup is the job of **infra/control spells** and Conduit-level APIs.

ACL:

* ConduitACL must allow detach.
* DomainACL must allow this op.
* ProfileACL must allow control-level ops for this domain.

---

## 7. AI Usage Modes – Behavior Story

This section summarizes how an AI uses the system in practice. Details will be implemented via specific control Spells.

### 7.1 Observation (Prod Watcher)

Domain: `orders_prod_observer`
Profile: `ai_prod_observer` (VIEW / limited STATE)

Capabilities:

* `describe_rift` → understand it’s prod, VIEW-tier only.
* `list_spells` / `describe_spell` → enumerate & understand `order_service`, `metrics`, etc.
* `invoke_spell`:

  * `metrics.get_timeseries` → QPS, error rates.
  * `order_service.get_health` → health summaries.
* `get_attr` for safe, read-only attributes.

No GRAPH changes, no destructive ops.

### 7.2 Intervention (Incident SRE)

Domain: `ops_control`
Profile: `ai_incident_sre` (VIEW + controlled STATE, no GRAPH in prod)

Capabilities:

* Pull logs/traces from Spells like `log_reader`, `trace_reader`.
* Open incidents via `incident_manager`.
* Inspect runtime state through safe attrs on live Creations.
* Perform **bounded interventions**:

  * Restart pools, drain traffic, tweak safe knobs via STATE-tier spells.

No direct topology mutations in prod domains.

### 7.3 Reconstruction (Lab Repro)

Domain: `orders_lab_mutation`
Profile: `ai_mutation_lab` (VIEW/STATE/GRAPH in lab only)

Capabilities:

* Clone prod blueprints into lab via control Spells (`spell_system_control`).
* Open dedicated lab Scopes for repro.
* Replay prod traffic traces against lab Creations.
* Inspect internal state more aggressively.

All breakage is contained to lab Conduits/Scopes.

### 7.4 Mutation (Graph Changes under Control)

Same domain/profile as reconstruction (`orders_lab_mutation` / `ai_mutation_lab`).

Capabilities:

* Inspect mutation surfaces via `describe_spell` + MutationContract sockets.
* Propose and apply graph mutations in lab via `mutation_control` Spells.
* Re-run repro traffic to compare metrics before/after mutation.
* Open change requests via `change_control` with evidence.

Promotion to prod is mediated by ChangeControl and humans, not auto-applied.

---

## 8. Execution Model & Concurrency

* AethericRift and RiftDomain are **pure façades**:

  * no internal worker pools,
  * no consumer/producer patterns.
* All calls are **synchronous** and execute on the caller’s thread.
* Thread-safety is via **re-entrancy + minimal locking** on internal maps.
* Conduits/Scopes own concurrency semantics for Creations (locks, existence, etc.).
* Structural/GRAPH ops may later require explicit mutation locks (future ticket).

---

## 9. Open Questions (To Be Split into Implementation Tickets)

1. **Precise scope resolution rules for `invoke_spell`**

   * How context, existence semantics, and domain config choose or create a Creation.

2. **Attr targeting semantics**

   * Spell-level vs instance-level attrs.
   * Handle vs `(spell_key, scope_id)` addressing.

3. **Final error taxonomy**

   * Exactly when to raise `ConduitGone`, `ScopeExpired`, `CreationGone`, `AccessDenied`, etc.

4. **Domain lifecycle**

   * Who creates/destroys domains.
   * Static vs dynamic (per mission/agent) domains.

5. **Structural concurrency control**

   * Whether GRAPH-tier ops require explicit locks or are just ACL-gated.

6. **Observability & audit**

   * How to log AI operations (especially GRAPH-level) into IncidentManager / ChangeControl.

---

## 10. Acceptance Criteria

This RFC is considered accepted when:

* The roles of `AethericRift`, `RiftProfile`, `RiftDomain`, and `Conduit/Scope/Creation` are agreed as described.
* The ACL stack is stable and non-overlapping:

  * `SpellACL` → spell surface.
  * `ConduitACL` → lifetimes/scopes.
  * `RiftDomainACL` → workspace slice.
  * `RiftProfileACL` → global caps per principal.
* The auth story is accepted:

  * internal calls pass `profile_id` directly,
  * external calls may use `RiftAuthKey` as a simple mapping to profiles/domains.
* The RiftDomain workspace semantics are accepted:

  * static registry + weakref-based working set,
  * no ownership of lifetimes.
* The generic method contracts are stable:

  * `describe_rift`, `list_spells`, `describe_spell`, `invoke_spell`, `get_attr`, `set_attr`, `list_conduits`, `list_open_conduits`, `close_conduit`.
* The four AI usage modes (Observation, Intervention, Reconstruction, Mutation) are recognized as the primary design targets for this subsystem.

Once accepted, implementation can proceed in smaller tickets focused on:

* AethericRift core.
* RiftDomain implementation.
* ACL engine.
* Conduit bindings.
* AI control spells (metrics/logs/trace, spell_system_control, mutation_control, change_control).
