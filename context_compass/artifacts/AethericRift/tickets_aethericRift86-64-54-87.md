# [Ticket] AethericRift / RiftDomain – Profiles, ACL Stack, and Remote API Contract

**Labels:** `melder-core`, `aetheric-rift`, `rift-domain`, `acl`, `remote-api`, `profiles`, `conduits`, `design-rfc`

---

## 1. Intent / Scope

This ticket locks down the **technical architecture and API contract** for:

* `AethericRift` – global control plane (auth, routing, registry).
* `RiftProfile` – a principal (AI / agent / human) with global caps.
* `RiftDomain` – a **workspace** / remote API surface for interacting with Melder via Conduits.
* ACL layers:

  * Spell ACLs,
  * Conduit ACLs,
  * RiftDomain ACLs,
  * RiftProfile ACLs.
* Token-based auth (SHA256-based opaque session token).
* Multi-domain per profile.
* RiftDomain’s **remote operations**:

  * `describe_rift`
  * `list_spells`
  * `describe_spell`
  * `invoke_spell`
  * `get_attr`
  * `set_attr`
  * `list_conduits`
  * `list_open_conduits`
  * `close_conduit`

This is **not** an implementation ticket; it’s the conceptual spec and behavior contract so we don’t keep wobbling on what Rift/AethericRift actually are.

---

## 2. Core Concepts (Ground Truth)

We keep **Melder semantics** intact. No generic façade.

### 2.1 Spells

* A **Spell** is a Melder construct that behaves like:

  * “an object with methods,” plus:

    * graph / dependency metadata (Phase 5 blueprints, SpellSystemIndex),
    * Existence semantics,
    * a role in the system (service, infra control, etc.).

* From the remote’s POV in a `RiftDomain`:

  * Spells are **named entrypoints** (`spell_key`).
  * You call methods via `invoke_spell`.
  * You read/write state via `get_attr` / `set_attr` (if allowed).

### 2.2 Conduits

* A **Conduit** is the DI runtime:

  * owns **Scopes**,
  * owns **Creations** (actual Python objects),
  * enforces Existence (unique, per-scope, many, etc.),
  * is the thing that ultimately builds and holds objects for Spells.

* From a `RiftDomain`’s POV:

  * A domain is wired to one or more Conduits.
  * All “real work” (object resolution, lifetime, method execution) goes through Conduits.

### 2.3 Scopes & Creations

* **Scope**: a lifetime / grouping boundary inside a Conduit.

  * A set of Creations that live and die together.
  * Can be prod/global (e.g. `prod`), lab (e.g. `lab:mission-123`), tenant-specific, etc.

* **Creation**: a realized object for a Spell within some Scope.

`RiftDomain` does **not** own scopes/lifetimes; it just **targets** them and reacts when they disappear.

---

## 3. AethericRift / RiftProfile / RiftDomain – Roles

### 3.1 AethericRift (Global Control Plane)

Responsibilities:

* **Registry**:

  * All known `RiftProfile`s.
  * All known `RiftDomain`s.
  * All known Conduits (and their metadata).
* **Auth**:

  * Maintains a mapping of `RiftSessionToken` → `RiftProfile` + allowed domains + expiry.
* **Routing**:

  * For each incoming remote call:

    * resolve profile from token,
    * resolve target `RiftDomain`,
    * enforce top-level ACL intersection,
    * forward call **synchronously** into the appropriate `RiftDomain`.

Constraints:

* No worker pools inside AethericRift.
* No consumer/producer pattern.
* Executes on the caller’s thread (whoever called into AethericRift).

### 3.2 RiftProfile (Principal)

Represents **who** is calling:

* AI agent, human user, external service, etc.

Holds:

* `profile_id`.
* Global capability caps (e.g., can this profile ever do GRAPH-level ops?).
* Set of allowed `RiftDomain` IDs (multi-domain per profile is allowed).
* Optional per-domain overrides (e.g., profile can see domain X as VIEW-only, domain Y as GRAPH).

`RiftProfile ACL` answers:

> "What is this principal ever allowed to do anywhere?"

### 3.3 RiftDomain (Workspace / Remote API)

A **workspace** that exposes:

* a curated subset of Spells,
* access to one or more Conduits,
* optional infra/control Spells (SpellSystemStates, ChangeControl, etc.).

This is the **remote the AI talks to**. It exposes the fixed API surface:

* `describe_rift`
* `list_spells`
* `describe_spell`
* `invoke_spell`
* `get_attr`
* `set_attr`
* `list_conduits`
* `list_open_conduits`
* `close_conduit`

Internal responsibilities:

* Map `spell_key` → underlying Spell/SpellIndex + Conduit + Scope-resolution strategy.
* Resolve calls into Conduits (and hence Creations).
* Enforce Domain-level ACL slice.
* Optionally maintain weakrefs / handle maps for attached objects (if we add handles later).

Constraints:

* **No threads, no queues.**
* **Re-entrant, thread-safe façade:**

  * protects its own internal maps with locks / safe containers.
  * all calls execute **synchronously** on the caller’s thread.
* Does **not** own lifetimes; Conduits and Scopes do.

---

## 4. ACL Stack – Who Controls What

For any operation, **effective permission** is:

> `SpellACL ∧ ConduitACL ∧ RiftDomainACL ∧ RiftProfileACL`
>
> If any one denies, the operation is denied.

### 4.1 Spell ACL – Surface of the Spell

Answers: *"What can anyone ever do to this Spell?"*

* Is the Spell exposable at all?
* Which methods can be invoked via `invoke_spell`?
* Which attrs are readable/writable via `get_attr` / `set_attr`?
* Which operation tiers are allowed:

  * `VIEW` – inspect graph/metadata only.
  * `STATE` – invoke spell, tweak state/params.
  * `GRAPH` – mutate graph/topology, structural overrides, etc.

Spell ACL is a **hard cap**. No domain or profile can exceed it.

### 4.2 Conduit ACL – Lifetimes & Scope Powers

Answers: *"What can be done to Scopes and Creations inside this Conduit?"*

Controls whether a caller (via a given profile/domain) may:

* Open new scopes.
* Close existing scopes.
* Create new creations in a scope.
* Destroy specific creations.
* Shut down / clean the Conduit entirely (for `close_conduit` with real impact).

Conduit ACL covers **lifetime and scope** operations, not spell method surfaces.

### 4.3 RiftDomain ACL – Workspace View

Answers: *"What does this RiftDomain expose and to what degree?"*

Per-domain:

* Which Spells appear in `list_spells`.
* For each Spell:

  * allowed operation tier **within this domain** (often a strict subset of Spell ACL).
* Which Conduits appear in `list_conduits` / `list_open_conduits`.
* Whether this domain is allowed to:

  * issue `close_conduit` calls,
  * call infra-control spells (SpellSystemStates, ChangeControl, etc.).

RiftDomain ACL defines the **workspace slice** of the global universe.

### 4.4 RiftProfile ACL – Principal Caps

Answers: *"What is this profile allowed to do anywhere?"*

Per-profile:

* Global caps:

  * may this profile ever perform GRAPH-level operations?
  * may this profile ever close a Conduit?
  * may this profile ever open scopes?
* Optional context/tag rules:

  * profile may only use `prod_*` domains in VIEW mode.
  * profile may use `lab_*` domains as GRAPH.

`RiftProfile ACL` is the outer guardrail; it can only further restrict.

---

## 5. Auth – RiftSessionToken (SHA256-Based)

We use an opaque session-style token to bind remote calls to a `RiftProfile` and its allowed domains.

### 5.1 Token Issuance

1. Client authenticates via some external mechanism (up to integrator: API key, OAuth, local login, etc.).

2. AethericRift resolves the corresponding `RiftProfile`.

3. AethericRift mints a **cryptographically random** 256-bit token.

4. AethericRift stores **only**:

   * `token_hash = SHA256(raw_token)`
   * `profile_id`
   * allowed `domain_ids`
   * `issued_at`, `expires_at`
   * optional rate-limiting metadata.

5. AethericRift returns the **raw token** once to the caller.

The caller must store and present this token on each request.

### 5.2 Request-Time Flow

On each remote request, the caller sends:

* `token` (raw),
* `domain_id` (or alias),
* requested operation (`describe_rift`, `invoke_spell`, etc.).

AethericRift then:

1. Computes `token_hash = SHA256(token)`.

2. Looks up `token_hash` in its token table.

3. Resolves `RiftProfile` and allowed domains.

4. Validates that `domain_id` is allowed for this profile.

5. Collects:

   * `SpellACL` (if a spell is involved),
   * `ConduitACL` (for the targeted Conduit),
   * `RiftDomainACL` (for this domain),
   * `RiftProfileACL`.

6. If all four allow the operation, it:

   * calls the appropriate `RiftDomain.*` method **synchronously** on the current thread.

7. Otherwise, returns an `AccessDenied` error with structured reason.

---

## 6. Multi-Domain per RiftProfile

We explicitly support **N RiftDomains per RiftProfile**.

### 6.1 Motivation

A single AI / principal may need multiple "access points" into Melder, e.g.:

* `orders_prod_observer` – VIEW/STATE access to live order system (read metrics, inspect graphs).
* `orders_lab_mutation` – GRAPH access to lab Conduits for mutation experiments.
* `ops_control` – control-plane spells (IncidentManager, ChangeControl, etc.).

Same `RiftProfile`, multiple `RiftDomain`s, different:

* spell sets,
* conduit attachments,
* ACL slices.

### 6.2 AethericRift Responsibilities

For each `RiftProfile`, AethericRift maintains:

* `allowed_domain_ids`: set of domains this profile can use.
* `default_domain_id`: used when callers omit domain.

On each request:

1. Resolve profile from token.
2. Validate `domain_id` ∈ `allowed_domain_ids`.
3. Dispatch to that `RiftDomain`.

The threading model **does not change**; domains are just different workspaces, not new runtimes.

---

## 7. RiftDomain Remote API Contract

This section freezes the meaning of the chosen operations:

* `describe_rift`
* `list_spells`
* `describe_spell`
* `invoke_spell`
* `get_attr`
* `set_attr`
* `list_conduits`
* `list_open_conduits`
* `close_conduit`

### 7.1 `describe_rift`

**Purpose:**

> Provide full situational context for this `RiftDomain`.

**Returns (conceptually):**

* `rift_id` / `domain_id`
* `frame_id` (AethericFrame name/id)
* `tags`: e.g. `["prod", "orders"]`, `["lab", "mutation"]`
* `capability_tier`: summary of allowed tiers in this domain (`VIEW` / `STATE` / `GRAPH`)
* `conduits`: list of conduit ids attached to this domain (with basic roles)
* optional description / notes.

### 7.2 `list_spells`

**Purpose:**

> Enumerate Spell entrypoints exposed in this RiftDomain.

Filtered by ACL intersection.

**Returns:** a list of spell descriptors, e.g.:

* `spell_key` (domain-local name, e.g. `"order_service"`)
* `spell_index` / lineage id
* `kind`: root service, infra-control, helper, etc.
* optional tags / description.

### 7.3 `describe_spell`

**Purpose:**

> Provide detailed information about a specific spell surface in this RiftDomain.

**Input:** `spell_key` (or `spell_index` if you allow that directly).

**Returns:**

* Identity:

  * `spell_key`,
  * underlying `SpellIndex` (lineage + version),
  * root vs helper role.
* Structural info (hooked from Phase 5 blueprints):

  * dependencies, DAG snippets,
  * sockets (normal + SpellContract / MutationContract),
  * default Existence semantics.
* Remote surface:

  * methods invokable via `invoke_spell`,
  * attrs visible via `get_attr` / `set_attr`,
  * effective operation tier (`VIEW` / `STATE` / `GRAPH`) for this domain.

`describe_spell` is how an AI learns “what this spell does” and how it may safely operate it.

### 7.4 `invoke_spell`

**Purpose:**

> Invoke work via a Spell in this RiftDomain.

**Inputs (conceptual):**

* `spell_key`
* `method` (optional; default could be main entrypoint)
* `args`, `kwargs`
* optional `context`:

  * may include target scope id, tenant id, mission id, etc.

**Behavior:**

1. AethericRift has already resolved Profile + Domain and done ACL intersection.
2. `RiftDomain.invoke_spell`:

   * resolves spell descriptor from `spell_key`;
   * determines appropriate Conduit and Scope (retrieval-first based on Existence + context);
   * consults Conduit/Creations to obtain a Creation;
   * resolves the method on that Creation;
   * calls it **synchronously** on the current thread.
3. Returns the method result.

Error cases (conceptually):

* `AccessDenied` (if deeper ACL denies this specific method).
* `CreationGone` (resolved Creation no longer exists: scope cleaned or GCed).
* `ScopeExpired` (requested scope was closed).
* `SpellNotFound` / `MethodNotFound`.

Exact error taxonomy will be finalized in a follow-up ticket; the key is that errors are **structured**, not random strings.

### 7.5 `get_attr`

**Purpose:**

> Read an attribute exposed by a Spell surface or resolved Creation.

**Inputs:**

* target identifier:

  * simplest: `spell_key` (+ optional context/scope info),
  * optionally: a handle returned by `invoke_spell` for a specific instance.
* `attr_path`: e.g. `"foo"`, `"config.max_discount"`.
* optional `context` (scope/session info if not using explicit handles).

**Behavior:**

* ACL per-attribute (Spell ACL + Domain ACL + Profile ACL).
* Resolve appropriate Spell/Creation via Conduit/Scope.
* Return the attribute value or a structured error.

### 7.6 `set_attr`

**Purpose:**

> Write an attribute on a Spell surface or resolved Creation.

Same targeting semantics as `get_attr`.

* Allowed only if:

  * Spell ACL marks attr writable,
  * Domain ACL allows writes for this Spell,
  * Profile ACL allows the required tier (`STATE` or `GRAPH`).

`set_attr` is the main non-structural state mutation primitive.

### 7.7 `list_conduits`

**Purpose:**

> Show which Conduits this RiftDomain is wired to.

**Returns:** a list of conduit descriptors, each containing at least:

* `conduit_id`
* attach mode (conceptual):

  * `"direct"` – real app Conduit,
  * `"linked_readonly"`,
  * `"linked_write"`,
  * `"lab_surrogate"`, etc.
* role / description (e.g. "prod_orders", "lab_mutation_universe").

This gives AI a sense of what **universes** it can touch from this domain.

### 7.8 `list_open_conduits`

Two possible semantics; we should pick **one** and stick with it (or split into two ops later).

**Preferred interpretation (for now):**

> List Conduits **and** any Scopes that are currently active/visible to this RiftDomain.

Each entry might include:

* `conduit_id`
* `scopes`: list of scope ids this RiftDomain can see in that Conduit.

This is especially useful for lab domains where multiple experimental scopes may be active.

### 7.9 `close_conduit`

This is the **sharpest knife** in the set and must be very explicit.

Two conceptual meanings (we may later split this into separate calls):

1. **Detach Conduit from this RiftDomain only**:

   * Domain-level: after this, `list_conduits` no longer shows it.
   * Does **not** necessarily shut down the Conduit globally.

2. **Actually stop/clean the Conduit**:

   * Tell the Conduit to clean scopes or shut itself down.
   * Destroys Creations and affects the underlying runtime.

For now, the safer default is:

* `close_conduit` = **detach from this RiftDomain**.
* Actual Conduit shutdown/cleanup should be triggered via **explicit infra Spells** (e.g. a `conduit_control` Spell) with GRAPH-tier ACL.

Either way, access to `close_conduit` must be guarded by:

* Conduit ACL (must explicitly allow detachment/shutdown),
* Domain ACL (domain is allowed to perform this control operation),
* Profile ACL (profile has the right tier),
* Spell ACL if routed through an infra Spell.

---

## 8. Execution Model (No Consumer/Producer Inside Rift)

We explicitly **reject** building a worker/queue model inside AethericRift/RiftDomain.

Execution chain per call:

1. Some worker (CommandOps agent thread, HTTP handler, etc.) calls into AethericRift.
2. AethericRift:

   * resolves `RiftProfile` from token,
   * resolves/validates `RiftDomain`,
   * performs ACL intersection,
   * calls `RiftDomain.*` **synchronously on the same thread**.
3. `RiftDomain` synchronously:

   * resolves Spell + Conduit + Scope,
   * calls into Conduit,
   * returns result or structured error.
4. No internal queues, no background threads, no producer/consumer.

Thread-safety is achieved by **re-entrancy + minimal locking** around internal maps, not by serializing calls or offloading work to internal workers.

Actual concurrency / scheduling is owned by **CommandOps / the host app**, not by AethericRift/RiftDomain.

---

## 9. Open Questions / Follow-Ups

1. **Exact error taxonomy**

   * Finalize concrete error types (`AccessDenied`, `SpellNotFound`, `MethodNotFound`, `ScopeExpired`, `CreationGone`, `OperationNotSupported`, etc.).
   * Decide encoding (exception classes vs error envelopes vs both).

2. **Scope-oriented API surface**

   * Do we expose explicit `list_scopes` / `open_scope` / `close_scope` at the RiftDomain level, or only indirectly via infra-control Spells?
   * How do Scope ids propagate in `invoke_spell` contexts?

3. **Infra-control Spells vs direct Conduit ops**

   * Where do we draw the line between:

     * `close_conduit` as a direct Domain operation, vs
     * "call this control Spell that manages Conduit/Scope lifetimes"?

4. **RiftSessionToken lifecycle & rotation**

   * Do we support token rotation / refresh?
   * How do we revoke tokens (immediate blacklist vs expiry-only)?

5. **Observability hooks**

   * How do we surface:

     * which profile used which domain for which spells,
     * structured audit logs for GRAPH-level operations,
     * integration with IncidentManager.

---

## 10. Acceptance Criteria

This RFC is considered **accepted** when:

* We agree that:

  * `AethericRift` is purely control-plane (auth, registry, routing, no workers),
  * `RiftDomain` is the **only** remote API surface and remains synchronous and re-entrant,
  * Conduits/Scopes/C
    reations remain the sole owners of lifetimes and objects.
* The ACL stack is conceptually stable:

  * `SpellACL`, `ConduitACL`, `RiftDomainACL`, `RiftProfileACL` each have clear, non-overlapping responsibilities.
  * Effective permission is always the intersection of the four.
* The `RiftSessionToken` auth model is accepted as the default:

  * random token, SHA256 stored server-side,
  * bound to a `RiftProfile` and allowed domains.
* The `RiftDomain` API surface is frozen to the agreed set of operations (with this semantics):

  * `describe_rift`, `list_spells`, `describe_spell`, `invoke_spell`, `get_attr`, `set_attr`, `list_conduits`, `list_open_conduits`, `close_conduit`.
* We accept **multi-domain per profile** as a first-class design:

  * one `RiftProfile` may have multiple `RiftDomain` workspaces (prod observer, lab mutation, ops control, etc.).

Once this is accepted, implementation tickets can be spun out for:

* Building the `AethericRift` registry/auth router.
* Implementing `RiftDomain` and its API surface over existing Conduit/Scope/Spell infra.
* Implementing and testing the ACL evaluation across Spell/Conduit/Domain/Profile.
* Adding observability and DevOps hooks for dangerous operations (especially GRAPH-level).
# Ticket: AethericRift ACL System for Remotes (AI Access Control)

## 1. Summary

Design and implement an **ACL (Access Control List) system** for **AethericRift remotes** so that:

* Every **remote** (AethericRift-exposed object / state machine) carries an explicit, inspectable **access contract**.
* AI agents (or any caller) can only:

  * **see** remotes they are allowed to see,
  * **invoke** transitions/operations they are allowed to invoke,
  * under the **conditions / scopes** they are allowed to operate in.
* ACLs are configurable at **definition time** (when a remote is created) and can be **summarized/exported** for:

  * documentation,
  * audits,
  * AI prompt/tooling generation.

This ticket is about the **conceptual design** of ACLs for AethericRift, not the low-level implementation of the Rift itself.

---

## 2. Context & Goals

### 2.1 AethericRift recap

* AethericRift is the **toolchain gateway** into Melder/Aether for AI and external orchestrators.
* It exposes **remotes**:

  * Remotes are **objects**, not REST APIs.
  * Each remote is typically modeled as a **FSM/HSM** (finite or hierarchical state machine):

    * States = system situations.
    * Transitions = allowed operations.
* AI agents are expected to drive these remotes instead of directly poking raw services.

### 2.2 Why ACLs matter here

Because AethericRift is *the* surface through which AI can act:

* We cannot treat it as a loose “bag of tools”.
* We need **explicit, enforceable access control** per remote, per operation.
* Users must be able to:

  * mark remotes as visible/hidden to certain agents or roles,
  * restrict which transitions are callable,
  * express **contextual constraints** (time, environment, Conduit, etc.).

We want:

> **AethericRift Remotes = stateful tools with a built-in permission contract.**

---

## 3. ACL Model – High Level

### 3.1 ACL per remote

Each **Remote** should have an ACL descriptor attached at definition time:

* `RemoteACL` conceptually contains:

  * **Identity / Principal filters**

    * e.g. agent IDs, roles, groups, external principals.
  * **Operation-level permissions**

    * which transitions/actions are allowed vs denied.
  * **Scope/Context constraints**

    * e.g. must be inside Conduit X, or from Aether context Y.
  * **Conditions / Guards**

    * optional dynamic predicates derived from runtime state.

### 3.2 Principal model (who is calling?)

We need a simple but extensible concept of "who" is making a request via the Rift:

Possible identity dimensions:

* **Agent ID**: a specific agent instance (e.g. `agent://ase/commander-01`).
* **Agent role**: categories like `researcher`, `operator`, `supervisor`, `system`.
* **Conduit / Spellbook**: the calling environment.
* **External principal**: e.g. human user account, API client key.

ACL checks can work against any subset of these.

### 3.3 Basic permission types

At minimum, we want per-remote and per-operation differentiation between:

* `view` – can an agent see that this remote exists and inspect its descriptor?
* `invoke` – can an agent trigger a transition / method?
* `introspect` – can an agent query detailed internal state or history?
* `admin` – can an agent change configuration / ACL of this remote? (likely very restricted).

Per FSM/HSM transition, we also want:

* Allowed / denied for certain principals.
* Optional guard conditions beyond identity.

---

## 4. ACL Attachment to Remotes

### 4.1 Remote descriptor structure

Every remote should have a descriptor, something like:

* Identity:

  * `remote_id`
  * `name`
  * `category` (e.g. storage, messaging, control, external-system, etc.)
* Behavior:

  * State machine definition (states, transitions).
* ACL:

  * `RemoteACL` block, which contains:

    * global rules (for viewing, listing, etc.),
    * per-transition rules.

### 4.2 Defining ACLs at creation

When a remote is registered with AethericRift, the creator should be able to specify ACLs via:

* **Fluent API / builder** on the Remote registration function.
* Perhaps a **policy profile** (preset ACL) for common patterns:

  * "read-only",
  * "operator-only",
  * "unsafe/experimental (hidden by default)", etc.

Example conceptual DSL (exact API later):

* `remote_acl.allow(role="operator").invoke_all()`
* `remote_acl.deny(role="agent_learner").invoke("shutdown")`
* `remote_acl.allow(agent_id="ase-root").admin()`

### 4.3 Defaults

We should define **safe defaults**:

* If no ACL is provided:

  * default to **non-visible** to AI agents,
  * visible only to system-level identities and human operators.
* This forces **opt-in exposure** of remotes to AI.

---

## 5. Operation- and State-Level Permissions

Since remotes are FSM/HSMs, ACLs must recognize state:

### 5.1 Transition-specific ACL

For each transition (operation) in a remote:

* We can attach a list of ACL rules:

  * "role X can invoke this transition from state S"
  * "agent Y is denied from invoking this transition ever"

This gives fine-grained control over what an AI can actually *do* even if it can see the remote.

### 5.2 State-aware constraints

We may need constraints like:

* "Only allow this transition if we’re in state `IDLE` and caller has role `operator`."
* "Never allow AI to invoke transitions that move into `DANGER` state without human presence."

We can model this via:

* guard predicates attached to transitions that have access to:

  * current state,
  * caller identity,
  * relevant environment flags.

This may integrate later with a more general **guard/condition** subsystem for AethericRift.

---

## 6. ACL Profiles & Settings (User-Facing)

We want users to be able to **select ACL presets** and **dump/export ACL configs**.

### 6.1 ACL Profiles

Define a small set of reusable profiles:

* `Profile.StrictReadOnly`:

  * AI can see remote, read limited state, but cannot invoke any transitions.
* `Profile.OperatorOnly`:

  * Only agents/identities with `role=operator` may invoke transitions.
* `Profile.SystemInternal`:

  * Hidden from most AI, callable only by system/supervisor roles.
* `Profile.SandboxExperiment`:

  * Visible to experimental agents, but confined to sandboxed state transitions.

Users can:

* apply a profile to a remote at creation,
* optionally override specific rules.

### 6.2 Exportable ACL descriptions

We should be able to **render ACLs** in a machine-readable and human-readable form:

* Machine readable (e.g. JSON/TOON-like):

  * for audits,
  * for AI prompt/tool injection,
  * for config-as-code.

* Human readable:

  * short summaries like:

    * "Remote X: visible to roles [operator, supervisor], transitions: start/stop restricted to operator, introspection to supervisor only."

This matches the user’s ask that **settings can be selected and output** clearly.

---

## 7. Integration Points

### 7.1 Identity plumbing

We need a consistent way to attach identity/principal information to:

* AI agent sessions.
* Internal calls into the AethericRift.

This likely means:

* A `CallerContext` or `PrincipalContext` object passed (or available via contextvar) into ACL checks.

### 7.2 Enforcement layer

The Rift needs a single ACL enforcement point:

* Before a remote is listed, described, or invoked:

  * Evaluate ACL with the current `CallerContext` and requested operation.
  * Decide allow/deny.
  * Return explicit error on denial.

No remote should be reachable bypassing this path.

### 7.3 Logging & audit hooks

ACL decisions should be loggable (at least in debug/audit mode):

* who tried to
* do what
* on which remote
* result: allowed/denied

This is especially important when AI is driving remotes.

---

## 8. Tasks

1. **Define ACL Data Model**

   * [ ] Design `RemoteACL` structure (principals, permissions, constraints).
   * [ ] Define per-transition ACL binding model in FSM/HSM descriptors.

2. **Principal / Identity Model**

   * [ ] Specify what a `Principal` / `CallerContext` looks like (agent ID, roles, Conduit, etc.).
   * [ ] Decide how this context is passed into AethericRift (explicit parameter vs ContextVar).

3. **Default Policies**

   * [ ] Define safe defaults (e.g., remotes hidden to AI unless explicitly exposed).
   * [ ] Implement a few standard profiles (read-only, operator-only, system-internal, sandbox-experiment).

4. **Remote Registration API**

   * [ ] Extend AethericRift remote registration to accept ACL definitions and/or profiles.
   * [ ] Add builder/fluent methods for fine-grained ACL specification.

5. **Enforcement Logic**

   * [ ] Implement central ACL check logic for:

     * listing remotes,
     * describing remotes,
     * invoking transitions.
   * [ ] Ensure no direct call path bypasses ACL checks.

6. **Export / Introspection**

   * [ ] Provide an API to dump/export ACL settings per remote (machine-readable and human-friendly strings).
   * [ ] Optionally integrate with docs/telemetry so users can see which remotes are exposed to which agents.

7. **Tests**

   * [ ] Remotes default to safe, non-AI-exposed ACL if none specified.
   * [ ] Applying a profile results in expected allowed/denied behavior.
   * [ ] Per-transition ACL rules are enforced correctly (e.g., operator can invoke; learner cannot).
   * [ ] ACL export reflects the actual effective rules.

---

## 9. Acceptance Criteria

* Each AethericRift remote has an attachable, inspectable `RemoteACL`.
* ACLs can express rules based on principals (agent id, roles, etc.) and operation types (view/invoke/introspect/admin).
* Transitions in a remote’s FSM/HSM can carry specific ACL rules.
* Defaults are safe: no remote is accidentally exposed to AI without explicit intention.
* Users can apply ACL profiles and override them where needed.
* A central enforcement layer ensures ACLs are honored for all remote operations.
* ACL configurations can be exported for documentation, audits, and AI tool metadata.

This ticket defines the **conceptual ACL framework** for AethericRift remotes so that AI access is always **explicit, governed, and inspectable**, not implicit or ad hoc.
# Ticket: AI-Native AethericRift, IVR Control Surface, and python_toon Introspection Layer

## Summary

Introduce **AI-native capabilities** into Melder behind an explicit configuration flag (`ai_native_enabled`), and layer a dedicated **AethericRift** API on top of Aether and Conduits.

An **AethericRift** is an AI-facing, per-agent control surface that:

* Lives as an object in Aether (resolved via Melder like any other spell).
* Exposes a **graph/IVR-style introspection API** over Spellbooks, Conduits, Spells, Resolution plans, DAGs, Contracts, Mutations, etc.
* Optionally provides **controlled code-execution hooks** (for future ASE/CommandOps integration) but is initially focused on **introspection + orchestration**, not arbitrary eval.
* Uses a **TOON-style encoding** (via `python_toon` or equivalent) for low-token, AI-friendly structured responses.
* Is only available when `ai_native_enabled=True` in the `Configuration`.

The goal is to give agents (ASE/CommandOps) a clean, AI-native interface into Melder **without** polluting the core DI behavior or forcing non-AI users to pay for any overhead.

---

## Background / Context

Melder is evolving from a classic DI container into an **AI-native dependency and object graph engine**. We already have:

* **Spellbook / Spells / SpellIndex** for DI, versioning, and mutation tracking.
* **Conduits** as object graph roots with `Creations` managers and `Existence` semantics.
* **Configuration** that governs system state, debugging, disposal, hooks, etc.

We now want to:

1. Expose Melder’s internal structures to AI systems (ASE/CommandOps agents) in a **safe, structured, low-token, traversable way**.
2. Avoid giving raw, direct code control over internals by default, but allow AI-native users to **opt in** explicitly via configuration.
3. Keep all AI-native behavior *lateral* to normal DI: no safety nets, no moral guardrails, just additional capabilities for users who know what they’re doing.

The **AethericRift** is the abstraction for this: a per-agent, per-session object that gives agents a **stateful pointer into Melder’s world**, with IVR-like branching and TOON-encoded responses.

---

## Goals

1. **Introduce an AI-native mode flag**:

   * Add a new configuration property `ai_native_enabled: bool` (default: `False`).
   * When `False`: Melder behaves exactly as a normal DI system; no AI-native metadata is built or exposed.
   * When `True`: AI-native subsystems are activated (docstring/metadata caching, Rift registration, IVR control surfaces, TOON encoders).

2. **Define the AethericRift concept and lifecycle**:

   * A class (e.g. `AethericRift`) bound into Aether as a spell (e.g. via an `IRift` spellframe).
   * Each agent can obtain its own Rift instance via normal DI (`conduit.meld(IRift)` or similar).
   * Rifts act as **command + introspection portals**, not raw object handles.

3. **Design an IVR-style navigation model for Melder’s internal graph**:

   * A Rift provides a root menu ("sections") and nested menus for spells, conduits, plans, DAGs, frames, mutations, contracts, creations, etc.
   * Each Rift maintains a **pointer** to a current node/state, but also supports **parallelizable queries** (batch fetches of multiple nodes/sections).
   * Provide a `reset` mechanism to snap the pointer back to a well-defined root state.

4. **Integrate TOON-style encoding (python_toon)**:

   * Use a TOON-like format (e.g. via `python_toon`) to serialize introspection data:

     * Minimal punctuation.
     * Line-based tables.
     * Compact arrays and maps.
   * The goal is to be **AI-optimized**, not human-optimized: low token count, deterministic structure, easy to parse.

5. **Docstring and metadata caching (AI-native only)**:

   * When `ai_native_enabled=True`, cache docstrings and key metadata for:

     * Spells (class/method/lambda descriptions).
     * Spellframes / Protocols.
     * Resolution plans / DAGs (optional summaries).
   * This cache feeds into the TOON encoders and the IVR menus so ASE can reason about *what* things do, not just *how* they are wired.

6. **Preserve core Melder semantics**:

   * No safety rails or alignment logic in Melder itself.
   * AI-native mode is **for experts**; misuse is not Melder’s problem.
   * AI-native subsystems must be strictly additive and not modify the DI semantics.

---

## Non-Goals

* We are **not** implementing full code-execution or sandboxing in this ticket.

  * The Rift may grow execution capabilities later (e.g. code patches, dynamic mutation orchestration), but this ticket is about introspection + IVR control surfaces.
* We are **not** building moral/ethical guardrails or “safe AI” patterns.

  * Users can and will hurt themselves if they do stupid things; that’s acceptable.
* We are **not** defining or implementing ASE itself here.

  * ASE will use Rifts as a control surface, but its internal loops, personalities, and reasoning are out-of-scope.

---

## Design: AI-Native Mode Flag (`ai_native_enabled`)

### Configuration changes

* Add a new property to `Configuration.available_properties`:

  * `"ai_native_enabled": bool`

* Default semantics:

  * If not explicitly set, `ai_native_enabled` defaults to `False` (via `load_default_dictionary()`).
  * The property is **idempotent** once set (same rules as `system_state`, `debugging`, etc.), or defined as mutable depending on how we want to treat AI-native availability.

* Fluent API extensions:

  * `Configuration.with_ai_native(enabled: bool = True) -> IConfiguration`

    * Sets `ai_native_enabled`.
  * `Configuration.dynamic_defaults()` / `automatic_defaults()` may or may not enable AI-native mode by default – decision needed.

### Behavioral contracts

* When `ai_native_enabled=False`:

  * No AethericRift binding (IRift cannot be resolved).
  * No docstring/index caching.
  * No TOON/IVR layer attached to Spellbooks/Conduits.

* When `ai_native_enabled=True`:

  * AI-native subsystems are wired:

    * AethericRift is bound and resolvable.
    * Docstring/metadata indexers are enabled at bind/conjure time.
    * IVR menus and TOON encoders become available.

---

## Design: AethericRift Concept

### High-level role

An **AethericRift** is an object living in Aether that:

* Represents a **session** for an AI agent (or human tool) to interact with Melder.
* Encapsulates:

  * A **navigation pointer** into the internal graph (IVR state).
  * Access to the AI-native index (docstrings, metadata, resolution plans, DAGs, etc.).
  * Methods for querying structured information about spells, conduits, frames, contracts, mutations, and creations.
* Acts as a **control surface**, not a raw handle to every underlying object.

### Spell & Aether integration

* Define a spellframe (e.g. `IRift`) to represent the Rift interface.

* Bind `AethericRift` as a class spell implementing `IRift`.

* An agent (or system) obtains a Rift via standard Melder resolution:

  * `rift = conduit.meld(IRift)`

* Multiple Rifts can coexist:

  * Per-agent, per-session, per-node, etc.
  * Rifts are just creations with `Existence` semantics like any other spell.

### Responsibilities

1. **IVR Root & Navigation**

   * Expose a root entry method returning TOON-encoded sections, e.g.:

     ```
     sections[7]: {id,name}
       1,spells
       2,conduits
       3,frames
       4,plans
       5,dag
       6,mutations
       7,contracts
     ```

   * Each section maps to a handler method in the Rift:

     * `list_spells(...)`
     * `list_conduits(...)`
     * `list_frames(...)`
     * `list_plans(...)`
     * `list_mutations(...)`
     * `list_contracts(...)`

2. **Pointer State**

   * The Rift maintains an internal **pointer** to the current “node” in the logical graph, e.g.:

     * `("root")`
     * `("spell", spell_id)`
     * `("conduit", conduit_id)`
     * `("plan", spell_id)`

   * Navigation methods update this pointer when the AI chooses branches:

     * `navigate_to_spell(spell_id)`
     * `navigate_to_conduit(conduit_id)`
     * `navigate_to_section("mutations")`

3. **Reset**

   * Provide `reset()` to snap the Rift back to the root IVR node:

     * Pointer is set to `("root")`.
     * Any temporary state associated with the current view is cleared.

4. **Parallel Queries vs Pointer**

   * While the IVR pointer is conceptually single, the API should support **parallelizable querying**:

     * Batch calls to `get_spells([id1, id2, ...])`.
     * Listing all spells for a frame or binding.
     * Fetching multiple DAG fragments at once.

   * Rifts are free to:

     * Maintain a primary pointer for stateful navigation.
     * Still serve stateless, batch-style queries for ASE agents that need high-bandwidth inspection.

5. **Session Identity (Optional)**

   * A Rift may carry an `agent_id`, `session_id`, or similar for logging and telemetry, but that can be added later.

---

## Design: IVR-Style Control Surface

The IVR model is:

* **Stateful**: the Rift tracks a current location in the graph.
* **Branch-based**: each response lists what sections or actions are available next.
* **Resettable**: agents can always jump back to root.
* **Composable**: agents can query multiple branches in parallel (via multiple Rifts or batch APIs).

### Example flows

1. **Spell Introspection**

   1. Agent calls `rift.root()` → gets top-level sections.

   2. Agent chooses "spells" → `rift.list_spells()`.

   3. Agent chooses a spell → `rift.navigate_to_spell(spell_id)`.

   4. Rift returns:

      ```
      spell:
        id: 01H...
        name: Repo
        frame: IRepo
        version: 6
      sections[4]: {id,name}
        1,requirements
        2,plan
        3,dag
        4,mutations
      ```

   5. Agent chooses "requirements" → `rift.get_requirements(spell_id)`.

2. **Conduit Topology**

   * Explore which spells are active in a Conduit.
   * Inspect creation counts, existence policies, and linked contracts.

3. **Mutation Analysis**

   * List mutations for a spell.
   * Inspect version history as a TOON table.

### Reset Behavior

* `reset()` must:

  * Return the Rift to root navigation.
  * Optionally emit a simple TOON confirmation:

    ```
    state:
      pointer: root
      ok: true
    ```

---

## Design: python_toon Integration

We want all AI-native responses to be encoded in a **TOON-like** format, e.g. something like:

```python
from python_toon import encode

encode({
  "spell": {...},
  "requires": [...],
})
```

Which yields minimal, line-based, column-aware formats, e.g.:

```
spell:
  id: 01HF...
  name: Repo
  frame: IRepo
  version: 6
requires[3]: {param,kind,target}
  db,frame,IDatabase
  logger,map,ILogger:primary
  config,frame,IConfig
```

### Requirements on the TOON encoder

* Must handle Python dictionaries, lists, primitive types.
* Should support **tabular encoding** for uniform lists of dicts.
* Should be deterministic: same input → same TOON output.
* Should minimize punctuation and verbosity.

### Where TOON is used

* All Rift responses (IVR menus, spell lists, requirements, DAGs, mutation histories, etc.).
* Potentially for logging AI-native telemetry in ASE/CommandOps.

---

## Design: Docstring & Metadata Caching (AI-Native Only)

When `ai_native_enabled=True`, we want to cache:

1. **Spell docstrings**:

   * From classes, functions, and lambdas (when possible).
   * Summaries of what each spell does.

2. **Frame/Protocol docstrings**:

   * Semantics of each interface / Protocol used as a spellframe.

3. **Resolution & DAG metadata** (optional, future):

   * High-level summaries of resolution plans and DAGs.

### Where the cache lives

* Likely as an internal index structure in Spellbook or an AI-specific sidecar object, e.g.:

  * `AiMetadataIndex` or similar, built at conjure-time when AI mode is enabled.

* Index keyed by:

  * SpellIndex / spell_id.
  * Spellframe / frame key.

### When the cache is built

* At bind-time or conjure-time:

  * When a spell is created and `ai_native_enabled=True`, extract and store docstrings/metadata.
* On mutation:

  * When a spell’s implementation changes, mark its AI metadata as stale and re-extract on next refresh.

### Exposing metadata via Rift

* Rift should provide metadata endpoints like:

  * `get_spell_doc(spell_id)` → TOON with summary and details.
  * `get_frame_doc(frame_key)`.

* Example TOON response:

  ```
  doc:
    target: spell
    id: 01HF...
  summary:
    resolve repo → use IRepo
  details:
    line[3]:
      - uses IDatabase for persistence
      - logs via ILogger
      - requires IConfig for DSN
  ```

---

## Design: Dynamic Toolchain View

The AethericRift + AI-native index + TOON responses effectively form a **dynamic toolchain** for agents:

* Agents can:

  * Inspect what spells exist.
  * Inspect how they wire together.
  * Inspect how they have mutated over time.
  * Inspect which Conduits are running, and with what creations.
  * Use that information to plan and coordinate activity in ASE/CommandOps.

* This is *not* a general-purpose Python REPL.

  * It is a **domain-specific control panel** for Melder.
  * Over time, we may add controlled mutation commands (e.g. rebind, rollback to version, update contracts).

---

## Open Questions

1. **Where exactly should the AI metadata index live?**

   * As part of Spellbook.
   * As a sidecar object bound into Aether.
   * As part of a dedicated `AiNativeSubsystem` that holds Rifts + metadata.

2. **How “heavy” should docstring caching be by default?**

   * Do we limit cached length?
   * Do we store raw docstrings, TOON-ified summaries, or both?

3. **How much of the mutation graph is exposed in v1?**

   * Minimal version history or full mutation DAG.

4. **How do we want to name the Rift frame and spell?**

   * `IRift` / `AethericRift` vs something else.

5. **Do we expose any mutation commands in v1?**

   * Or keep v1 strictly read-only and introspective.

---

## Implementation Plan / Tasks

### 1. Configuration: AI-Native Mode

* [ ] Add `"ai_native_enabled": bool` to `Configuration.available_properties`.
* [ ] Extend `load_default_dictionary()` to set `ai_native_enabled=False` by default.
* [ ] Add `with_ai_native(enabled: bool = True)` fluent helper.
* [ ] Wire property into Spellbook/Conduit creation so AI-native subsystems know whether they should initialize.

### 2. AethericRift Core Class

* [ ] Define a spellframe/interface for the Rift (e.g. `IRift`).
* [ ] Implement `AethericRift` class:

  * [ ] Holds references to Spellbook, Conduit, and AI metadata index.
  * [ ] Maintains IVR pointer state.
  * [ ] Exposes root `sections` view.
  * [ ] Exposes navigation operations (spells, conduits, frames, plans, dag, mutations, contracts).
  * [ ] Exposes `reset()`.
  * [ ] Exposes batch query helpers (`get_spells([...])`, etc.).
* [ ] Bind `AethericRift` into Spellbook only when `ai_native_enabled=True`.

### 3. IVR Navigation Model

* [ ] Design and implement the root sections and their identifiers.
* [ ] Implement handlers for each top-level section.
* [ ] Implement pointer updates for spell/conduit/plan/mutation-level nodes.
* [ ] Implement reset semantics.
* [ ] Ensure all responses are TOON-encoded via `python_toon`.

### 4. python_toon Integration

* [ ] Integrate or implement a TOON encoder (`python_toon` or equivalent).
* [ ] Provide helpers for common patterns:

  * [ ] `encode_sections(list_of_sections)`.
  * [ ] `encode_spell_list(spells)`.
  * [ ] `encode_requirements(requirements)`.
  * [ ] `encode_dag(dag_nodes)`.
  * [ ] `encode_mutation_history(history)`.
* [ ] Ensure deterministic output for testing and AI consumption.

### 5. Docstring & Metadata Index

* [ ] Implement an `AiMetadataIndex` (or equivalent) that can:

  * [ ] Index spells, frames, and optionally resolution/DAG metadata.
  * [ ] Attach docstrings and high-level descriptions.
  * [ ] Provide lookups by spell_id and frame key.
* [ ] Hook index building into bind/conjure when `ai_native_enabled=True`.
* [ ] Expose metadata endpoints via AethericRift (`get_spell_doc`, `get_frame_doc`, etc.).

### 6. Tests

* [ ] Tests that `ai_native_enabled=False` yields no Rift binding and no metadata indexing.
* [ ] Tests that enabling AI-native mode makes `IRift` resolvable from a Conduit.
* [ ] Tests for IVR root sections and navigation correctness.
* [ ] Tests for TOON encoding equivalence (stable formatting).
* [ ] Tests for docstring indexing and retrieval via Rift.
* [ ] Tests for batch/parallel queries returning the expected TOON structures.

### 7. Documentation

* [ ] Add a dedicated **AI-Native Mode** section to Melder docs:

  * [ ] Explain `ai_native_enabled` and the opt-in nature of AI-native features.
  * [ ] Describe AethericRift conceptually as a per-agent control surface.
  * [ ] Explain the IVR navigation model and TOON encoding.
  * [ ] Explicitly state that Melder does **not** provide safety rails or guardrails: misuse is the user’s responsibility.

---

## Notes / Philosophy

* AI-native features are for **professionals and experimenters**, not beginners.
* Melder’s responsibility is to provide **correct, deterministic, powerful primitives** – not to protect users from themselves.
* AethericRift + AI-native indexing + TOON encoding is the **foundation** for ASE/CommandOps agents to introspect and manipulate live Melder worlds.
* `ai_native_enabled` is the clear line between "Melder as a normal DI container" and "Melder as an AI-native object universe".
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
