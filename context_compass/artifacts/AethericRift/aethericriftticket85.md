# [Ticket] AethericRift, RiftDomain, and Infra-as-Tools – Philosophical Architecture & ACL Model

**Labels:** `melder-core`, `commandops-core`, `aetheric-rift`, `infra-as-tools`, `acl`, `remote-agents`, `philosophy`, `design-rfc`

---

## 1. Intent

This ticket captures the **philosophical foundations** and **object model** for the AethericRift subsystem:

> A structured way for AI agents (and other remotes) to interact with **real Melder infrastructure** – spells, conduits, creations – as if the system itself were a tool graph.

The goal is *not* to specify full Python APIs, but to lock in:

* The **core objects**: `AethericRift`, `RiftDomain`, `RiftConduit`, `RiftLesserConduit`.
* How they relate to **Melder** (DI / infra-as-tools) and **CommandOps** (missions, agents, networking).
* The **ACL model** across:

  * object surfaces (spells, methods, attrs),
  * domains (workspaces),
  * agent profiles (who is allowed to do what).
* The philosophical stance that:

  * Remotes are **real principals**, not toys.
  * They can **create, call, and destroy** real DI objects – but only where ACLs explicitly allow it.

This ticket is a **north-star RFC** for designing the actual AethericRift APIs and data structures later.

---

## 2. High-Level Philosophy – Infra as Tools

We explicitly accept the following stance:

1. **Melder** is not just a DI container. It is an **infra-as-tools fabric**:

   * Spells, conduits, frames, and existence rules describe the *living architecture* of an application.
   * This architecture can be **exposed** to AI agents as a tool graph.

2. **CommandOps** is the environment where agents live and work:

   * Missions, threads, event loops.
   * Roles, policies, and orchestrated work.
   * Networked zones (in enterprise) via CommandNet.

3. **AethericRift** is the *bridge* between these worlds:

   * It exposes selected parts of the Melder graph as a **tool surface**.
   * It applies **ACLs** and profiles to keep this exposure sane.
   * It gives agents the feeling of a **"living REPL" into the system**, where they can:

     * inspect infrastructure,
     * call methods,
     * create and destroy objects,
     * eventually mutate structures.

4. Long-term we assume **increasing trust in AI**:

   * Future agents may be allowed to hold privileged roles (e.g., certified systems engineer, SRE bot, etc.).
   * Our architecture must be capable of granting them **real power** safely, not just read-only toys.
   * This is why infra-as-tools must feel terrifyingly powerful *by design*, but governed by ACLs and policy.

This RFC is about capturing that spirit and turning it into a structured object model we can actually build against.

---

## 3. Core Objects & Responsibilities

### 3.1 AethericRift (Control Plane)

**Role:** Global control plane and registry for remote access into Melder.

Responsibilities:

* Hosts **global ACL configuration**:

  * Which **Conduits** and **Spells/lineages** are exposable at all.
  * For each object: which operations and members can ever be exposed.
* Hosts **agent profiles** and authentication bindings:

  * Map credentials / tokens → `AgentProfile`.
  * Each profile has capability flags (e.g., can this agent ever mutate? ever destroy instances?).
* Hosts **domain registration**:

  * `register_domain(domain_config) → RiftDomain`.
  * Domain config selects a subset of conduits/tools and defines workspace-local ACLs.
* Provides **authorization decisions** (directly or via cached structures):

  * Given: (agent profile, domain, tool/object, operation) → allow/deny.
  * Enforces the rule: **effective permissions are the intersection** of:

    * Object ACL,
    * Domain ACL,
    * Agent Profile ACL.

AethericRift does *not* execute application methods, resolve DI, or manage object lifetimes. It **decides who is allowed to ask for what**.

---

### 3.2 RiftDomain (Workspace / View)

**Role:** A **workspace** created under AethericRift that presents a curated tool surface to one or more agents.

Rough mental model:

> "A RiftDomain is a view of the infra-as-tools universe, plus a primary DI space (RiftConduit) that backs it. Agents attach to domains; domains are thread-safe and can be shared by multiple agents."

Responsibilities:

* Bound to **one primary RiftConduit** and optional **RiftLesserConduits**.
* Represents a **projection** of the global tool universe:

  * Based on domain-level ACL policy.
  * Only selected conduits/spells appear; others are invisible.
* Exposes the **remote API** that AI agents call:

  * `list_tools()`
  * `describe_tool(tool_id)` (describe callable methods/attrs, doc summary, etc.)
  * `invoke(tool_id, method, args)`
  * `get_attr(tool_id, path)`
  * `set_attr(tool_id, path, value)`
  * `create_instance(tool_id, args)`
  * `destroy_instance(instance_handle)`
  * Future: `override`, `mutate`, etc.
* Delegates **every** operation through AethericRift's authorization logic:

  * Checks Object ACL, Domain ACL, Agent profile ACL.
  * Only then calls into its RiftConduit.

Important: **RiftDomain does not invent its own security rules.** It is a workspace that enforces the AethericRift ACL model consistently for all participating agents.

---

### 3.3 RiftConduit (Primary DI Universe for a Domain)

**Role:** The primary Conduit-like structure that backs a RiftDomain. It is the **actual DI universe** where real Melder objects live for that domain.

Responsibilities:

* Wraps or composes a real **Conduit** / **AethericFrame** region in Melder.
* Receives domain-approved operations and translates them into real operations:

  * Spell resolution & creation (Meld).
  * Method invocation on created objects.
  * Lifetime management (via cleanup / existence semantics).
* Holds the **strong references** to creations/objects for the remote universe:

  * If RiftConduit is cleaned, all objects in this universe are destroyed.
* Can be extended for introspection / mutation later:

  * e.g., hooking into SpellSystemState, ChangeControl, etc.

Key invariant:

> **RiftConduit assumes all requests have already passed ACL checks in RiftDomain / AethericRift.**

It is not a policy engine; it is the execution engine for the remote universe.

---

### 3.4 RiftLesserConduit (Scoped Sub-Universes)

**Role:** Optional sub-conduits under a RiftConduit to give agents more granular lifetimes and scopes.

Use cases:

* A single RiftDomain wants to host multiple **sub-workspaces** for experiments:

  * Short-lived test graphs.
  * Per-mission or per-agent sub-spaces.
* Each RiftLesserConduit can:

  * Hold its own set of creations.
  * Be cleaned independently (destroying its objects) without wiping the entire RiftConduit universe.

This is a **refinement**, not a mandatory concept. Philosophically, it extends the idea that:

> The remote is a real user controlling real DI objects, but can group them into sub-scopes for lifecycle isolation.

---

## 4. ACL Philosophy – Three Layers, One Intersection

We lock in a **three-layer ACL model**:

> Effective permission = **Object ACL** ∧ **Domain ACL** ∧ **Agent Profile ACL**

If any of these deny an operation, it is denied.

### 4.1 Object ACL (Tool Definition Surface)

Object ACLs are defined when the *human* developer registers a Conduit/Spell/Creation with AethericRift.

They answer:

> "For this spell / lineage / object, *what is the maximum surface we ever want to expose to any remote?"

Dimensions:

* Visibility:

  * Is this object exposable at all (yes/no)?
* Operation-level permissions:

  * `inspect_structure` (see topology, sockets, metadata)
  * `invoke` (call as a function / method)
  * `create_instance` / `destroy_instance`
  * `read_attr` / `write_attr`
  * `override_args` (value-level DI overrides)
  * `rewire_graph` (structural mutation override)
  * `mutate_spell` (enter Spell mutation research)
* Member surface:

  * Which methods/attrs are visible.
  * For each: which operations (read/write/invoke) are allowed.

**Important:** Object ACL is a *hard cap*:

* No domain or agent can ever exceed it.
* Mutable surfaces need to be **explicitly** marked; default is conservative.

---

### 4.2 Domain ACL (Workspace View / Projection)

Domain ACLs are defined when a **RiftDomain is created**.

They answer:

> "For this workspace, what subset of the global tool universe do we want to expose, and how?"

Examples:

* Domain A (safe end-user tooling):

  * Only shows high-level `ReportService`, `DashboardService`.
  * No access to raw database clients or internal caches.
* Domain B (lab for an AI infra engineer):

  * Shows lower-level `OrderProcessor`, `PricingService`, `InventoryService`.
  * Might enable override and destroy operations on lab-specific sub-conduits.

Domain ACLs can only **down-scope**:

* They cannot grant an operation or member that Object ACL disallows.
* They can hide entire conduits / spells even if Object ACL allows them.

Per-domain policy is how we carve the infra-as-tools space into sensible workspaces.

---

### 4.3 Agent Profile ACL (Who Is Calling)

Agent profiles are defined in **AethericRift** and attached to credentials or tokens.

They answer:

> "What classes of operations can this agent ever perform, anywhere?"

Examples:

* `safe_viewer`:

  * Can inspect structure and invoke safe tools.
  * No creation/destruction, no overrides, no mutations.
* `lab_builder`:

  * Can create/destroy instances in lab domains.
  * Can override parameters but not rewire graphs.
* `mutation_engineer`:

  * Can enter mutation mode, rewire graphs, and apply experiment-level overrides in designated research domains.

Agent Profile ACLs are **global capability caps**:

* Even if Object ACL & Domain ACL allow `destroy_instance`, a `safe_viewer` profile cannot perform it.
* Profiles can later be tied into CommandOps roles, missions, or external auth systems.

---

### 4.4 Combined Authorization Flow

For every remote operation:

1. Agent authenticates → AethericRift resolves **AgentProfile**.
2. Operation arrives at **RiftDomain** with:

   * `agent_profile_id`,
   * `domain_id`,
   * `tool_id` / `object_ref`,
   * `operation` (invoke, create, destroy, etc.).
3. RiftDomain/AethericRift evaluate:

   * Object ACL for that tool/object,
   * Domain ACL for this domain,
   * Agent Profile ACL for this agent.
4. If all three say **yes**, the operation is forwarded to the appropriate `RiftConduit` / `RiftLesserConduit`.
5. Otherwise: operation is denied with a structured error.

No ACL logic should be smuggled directly into Conduits or Spells. They assume that requests they receive from RiftDomain are already authorized.

---

## 5. Multi-Agent Semantics in a Single Domain

A RiftDomain can be **shared by multiple agents** concurrently.

This creates two categories of operations:

### 5.1 Safe Concurrency (Calls & Reads)

Operations like:

* `invoke` on services designed to be thread-safe.
* `get_attr` on read-only views.

These are "normal concurrency" problems and are up to the underlying objects / systems (and Melder’s lifetime patterns) to handle correctly. AethericRift merely ensures ACLs are respected.

### 5.2 Dangerous Concurrency (Lifetimes & Structure)

Operations like:

* `destroy_instance` on shared singletons or long-lived creations.
* `override_args` or `rewire_graph` on spells used by other agents.
* `mutate_spell` that changes the graph under another agent mid-operation.

These drain directly into **ChangeControl**, mutation locks, and lifetime rules.

Philosophical constraints:

* Structural/mutation-level operations should require **locks or policies** beyond simple ACL allow/deny.
* Domains that are meant to be "lab spaces" for heavy mutation should be clearly separated from domains servicing normal workloads.
* In some domains, destructive operations may be:

  * restricted to agents holding a mutation lock,
  * or simply disallowed.

We do not fully specify lock semantics here, but we acknowledge that ACL alone is insufficient for structural concurrency. Later tickets will specify **mutation locks**, **graph-scoped locks**, and interaction with ChangeControl state.

---

## 6. Tool Surface – Objects, Methods, and Attrs

From an agent’s perspective, the infra-as-tools surface ultimately looks like:

* **Tools** (named entries): representing spells/creations.
* **Methods**: operations the agent can invoke.
* **Attributes**: values the agent can read or write.

AethericRift + RiftDomain expose this surface according to ACL.

Philosophical points:

* We do **not** invent new, arbitrary tool abstractions. Tools are real spells/creations projected into a tool namespace.
* Each tool’s exposed surface is derived from:

  * Object ACL (which methods and attrs are externally meaningful),
  * Domain ACL (which of those are visible in this domain).
* Where possible, the tool graph should feel **ergonomic and semantic**:

  * e.g., `order_service.create_order`, `inventory_service.reserve_stock`, `metrics.log_event`.

The important idea: **infra-as-tools is not a fake layer** – it is a curated, ACL-governed view of the real system objects.

---

## 7. Lifetimes and Ownership

We adopt the following stance on lifetimes:

1. **Real objects, real lifetimes.**

   * When an agent requests `create_instance`, a real DI object is instantiated via Meld in RiftConduit.
   * When an agent requests `destroy_instance`, that object is really cleaned and its references removed.

2. **RiftConduit (and lesser conduits) own canonical references.**

   * Remotes hold **handles** (IDs, weakrefs, etc.)
   * Strong references live in RiftConduit / RiftLesserConduit collections.

3. **RiftDomain is not a second owner.**

   * It indexes visible objects (often via weakrefs) for tool listing and routing.
   * It does not anchor lifetime.

4. **When a Conduit is cleaned, its universe dies.**

   * Cleaning a RiftConduit destroys all objects it owns.
   * The associated RiftDomain becomes unable to interact with those instances.

5. **Optional sub-scoping via RiftLesserConduit.**

   * Allows finer-grained lifetime groups (per experiment, per mission) without polluting global Conduit lifetime.

This respects Melder’s core semantics (Conduits and Existence rules) while giving remotes explicit handles to create and destroy things.

---

## 8. Security & Risk Tradeoffs

We do **not** pretend this design is safe by default. It is intentionally powerful.

Key tradeoffs:

* **Pros:**

  * AI agents can work with the *real system*:

    * debug, automate, observe, experiment.
  * Infra-as-tools becomes a first-class concept.
  * The architecture can evolve with future, more-capable agents (GPT-x running as real engineers).

* **Cons / Risks:**

  * Misconfigured ACLs can grant too much power.
  * Multi-agent mutation without proper locks can introduce instability.
  * Exposing mutation capabilities in the wrong domain can damage production-like systems.

Mitigations (philosophical commitments):

* Sensible **defaults**:

  * Object ACL defaults to minimal surfaces and no mutation.
  * Domain ACL defaults to read-only / safe operations.
  * Agent profiles are conservative unless explicitly elevated.
* **Separation of domains**:

  * Prod-like domains vs lab domains.
  * Different agent profiles allowed in each.
* Integration with **SpellSystemState**, **ChangeControl**, and **IncidentManager** in future tickets:

  * So dangerous operations are tracked, monitored, and recoverable.

---

## 9. Open Questions (Future Tickets)

1. **Exact data model for Object/Domain/Agent ACLs:**

   * How to represent them (dataclasses, TOON, config files, etc.).
   * How to persist / reload them.

2. **Mutation lock semantics:**

   * How to coordinate multi-agent structural changes in the same domain.
   * How locks interact with ChangeControl and SpellState.

3. **TOON / JSON command surfaces:**

   * Exact format of operations from agents (tool calls, attr reads/writes, etc.).

4. **Observability surfaces for AethericRift:**

   * How domains, conduits, tools, and ACLs are introspected and debugged.

5. **CommandOps integration:**

   * How missions, zones, and CommandNet glue into AethericRift for distributed setups.

These should be separate design tickets that reference this philosophical RFC.

---

## 10. Acceptance Criteria (Conceptual)

This ticket is "accepted" when the following are true conceptually:

* The team shares a clear mental model of:

  * `AethericRift` as **control plane**,
  * `RiftDomain` as **workspace/view**,
  * `RiftConduit` / `RiftLesserConduit` as **DI universes**.
* There is agreement on the **three-layer ACL model** and the intersection rule:

  * Object ACL (tool surface),
  * Domain ACL (workspace view),
  * Agent Profile ACL (global capabilities).
* We accept that:

  * Remotes can be **real principals** with lifetime and (eventual) mutation control,
  * but only where ACLs and future lock/policy mechanisms explicitly allow it.
* Future design tickets for concrete APIs, data models, and integration points will reference this RFC and stay consistent with its spirit.

This RFC is the philosophical spine for AethericRift and RiftDomain. Implementation details can evolve, but if they drift from these core ideas, we revisit this document and either update it or adjust the design.
