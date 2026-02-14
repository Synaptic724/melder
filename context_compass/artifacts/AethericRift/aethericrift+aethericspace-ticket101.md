# [Ticket] AethericRift + AethericSpace – In‑Process Infra‑as‑Tools Exposure via Spell/Conduit ACLs and RiftTokens (Philosophical Design)

**Labels:** `melder-core`, `aetheric-rift`, `aetheric-space`, `infra-as-tools`, `acls`, `remotes`, `conduits`, `lineage`, `commandops`

---

## 1) Intent

This ticket defines the **philosophical model** for exposing Melder as a **powerful in‑process toolchain**.

**AethericRift** is the “entrance” to the living system—spells, conduits, scopes, and runtime objects—such that callers can:

* enumerate what is exposed,
* create/use real objects,
* call into spells and systems in sequences (and optionally parallel),
* and operate inside well-defined **conduit scopes**.

This is **not** about endpoint ownership.
We explicitly do **not** want to own transport, auth, networking, web servers, rate limiting, or serialization boundaries.

> If someone wants an endpoint, they wrap AethericRift at the entrance.
> The wrapper owns the endpoint. AethericRift remains a library-level gateway.

This document is intentionally **philosophical**: it defines objects and behaviors, not concrete APIs or attribute/method names.

---

## 2) Non‑Goals

* Not a security sandbox.
* Not a “safe tools” spec.
* Not a network protocol.
* Not a minimal MVP.
* Not implementation-level method lists.

AethericRift is designed for a world where the caller has been intentionally granted access via **RiftToken**, and exposure boundaries are defined by the system owner’s **ACL choices**.

---

## 3) Core Objects

### 3.1 SpellLineage vs SpellVersion

We maintain the foundational distinction:

* **SpellLineageId**: stable identity (“who you are”)
* **SpellVersionId**: structural snapshot (“which body you’re wearing”)

**Exposure is anchored to lineage**, while **execution resolves to a concrete version** through the chosen conduit and its current spell index.

Advanced modes may allow version pinning, but the default philosophical stance remains:

> lineage is what we expose; the conduit chooses the living version unless overridden.

---

### 3.2 Conduits and Scopes

* **Spells** define *what exists and can be wired.*
* **Conduits** define *where/how those spells live* (existence rules, lifetimes, scoping, resolution surfaces).
* **Scopes** are the runtime “session envelopes” within a conduit (the actual arena where objects are built and used).

AethericRift never bypasses conduit reality.
It always operates through a conduit and its scopes.

---

### 3.3 AethericRift

AethericRift is a **capability gateway** that:

* holds a conduit‑agnostic view of what can be exposed (“the catalog”)
* attaches to one or more conduits (raw conduits or surrogates)
* enforces ACLs consistently before allowing access or invocation
* issues **RiftTokens** and creates **Remote sessions** (conceptually)
* coordinates scope creation and lifetime context for toolchain actions

AethericRift is the building. It does not become the plumbing.

---

### 3.4 AethericSpace

AethericSpace is a **stateful object arena**:

* It stores **real objects** produced or consumed by the caller.
* It enables multi-step workflows where results from earlier operations remain available later.
* It is explicitly dynamic and runtime-first: objects exist, can be combined, and can be used as inputs for later operations.

> AethericSpace is not “a handle protocol.” It is the place objects live so callers can actually work.

AethericSpace is bounded by **remote session + scope lifetime**. When a session/scope ends, its space can be cleared as part of disposal.

---

### 3.5 RiftTokens and Remotes

A **RiftToken** is a capability grant:

* It is not a network credential.
* It is an in-process permission object used to authorize a caller’s use of the rift.

A **Remote** is the conceptual “keycard session”:

* The remote is what actually “holds” the active view of the rift.
* Remotes carry a permission profile derived from the RiftToken and rift configuration.
* A rift can mint multiple remotes with different power levels.

---

## 4) Exposure Model

### 4.1 Conduit‑Agnostic Catalog

We want a **replica-like view** of exposed spell capability that is **conduit agnostic**:

* AethericRift holds a catalog of which spell lineages exist and are eligible for exposure.
* This catalog is not “instances”; it’s a **map of identities and exposure rules**.

This achieves:

* stable discovery and tool listing
* consistent exposure decisions independent of which conduit later executes the spell
* decoupling of “what is allowed to be used” from “where it runs”

---

### 4.2 RiftSurfaces

AethericRift connects the catalog to reality via **surfaces**:

* A surface corresponds to a specific conduit context (raw or surrogate).
* A surface defines what it means to “execute” toolchain actions in that environment.

A rift can have multiple surfaces (e.g., prod, dev, lab), each with different conduit constraints and different ConduitACL policies.

---

### 4.3 Surrogate Conduits (Recommended Surface Form)

We keep the philosophical pattern:

* Surrogate conduits are “front-stage” conduits that present curated views and behaviors.
* They can proxy or wrap deeper systems while enforcing a higher-level exposure profile.

Even in a fully trusted in-process world, surrogate conduits remain valuable because they:

* provide a controlled “lobby” surface over deeper conduits
* allow curated composition points
* enable strong organizational boundaries without pretending we’re sandboxing Python

---

## 5) ACL Philosophy

This is the core stance:

> **Exposure is explicit and user-defined.**
> The system is not moralizing about what is safe.
> ACLs can allow or deny anything—including private/dunder/mangled members—if the owner chooses.

The ACL system exists to make exposure *intentional* and auditable, not “safe by default.”

---

### 5.1 Spell ACLs

Spell/Lineage ACLs define:

* whether a lineage is exposable at all
* which categories of interaction are permitted with that lineage through the rift (construction, invocation, inspection, mutation entry, etc.)
* optional restrictions around which members of an object are accessible when interacting through that lineage

Spell ACLs are the **semantic exposure contract**: “this is allowed to be part of the rift world.”

---

### 5.2 Conduit ACLs

Conduit ACLs define the exposure contract **within a specific surface**:

* In conduit A, a lineage may be permitted broadly.
* In conduit B, the same lineage may be restricted or disabled.

This is the primary lever for practical system partitioning:

* prod vs dev vs lab behavior
* operational discipline
* “this environment is allowed to do X”

Conduit ACLs must be understood as *environmental boundaries*, not “security.”

---

### 5.3 Remote ACLs

Remote ACLs define **per-token/per-caller slices**:

* which surfaces are accessible
* which lineages are visible
* which interaction categories are enabled within those lineages

A rift can issue many remotes with different slices, all backed by the same internal system.

---

### 5.4 Effective Permission

Effective permission is the **intersection** of:

* spell/lineage ACL
* conduit ACL (surface)
* remote ACL (token/profile)

The rift enforces this intersection consistently as the single arbiter of “what is allowed.”

---

## 6) Behavioral Model of Use

### 6.1 Toolchain Composition

The rift world is “toolchain style”:

* operations can be chained sequentially
* operations can be parallelized where the caller chooses
* outputs can be stored in AethericSpace and reused later
* complex workflows can be constructed without “code deployment,” because the caller is operating directly in the runtime substrate

This is aligned with:

* stateful agent missions
* runtime-first experimentation
* interactive system construction and probing

---

### 6.2 Queueing and Execution Semantics

Remote interactions are treated as **commands** against the rift environment:

* commands may be queued and executed in order
* the system may support parallel batches, with explicit semantics around scope sharing vs scope isolation

The important philosophical requirement:

> Any execution must be clearly associated with a scope, and scope determines what objects exist and how they are cleaned.

---

### 6.3 Scope Binding via Context

Scope identity and active conduit surface must be treated as **first-class runtime context**:

* the rift ensures commands run inside the intended scope context
* context defines “which conduit reality” the command is operating within
* object lifetimes follow scope and remote/session lifecycle

This is the mechanism that makes the system coherent even when highly dynamic.

---

## 7) AethericSpace Semantics

AethericSpace exists because we want **real object workflows**, not “stateless tool calls.”

Philosophically:

* AethericSpace stores object references and allows later operations to re-use them.
* The space is part of the remote’s working environment (their “bench”).
* The space can host:

  * constructed objects
  * intermediate results
  * system objects the remote intentionally pulls into its workspace

### Lifecycle and Cleanup

AethericSpace is governed by:

* Remote lifetime (session end clears space)
* Scope lifetime (scope disposal clears objects created/owned in that scope)
* Optional policies: explicit purge, snapshot, export (conceptual)

The main requirement is:

> object existence is never “mystical.” If the scope is gone, the bench is cleared.

---

## 8) Relationship to Melder’s Living Architecture

AethericRift must remain compatible with:

* spell lineages and version evolution
* conduit existence rules (singleton vs many vs localized)
* contract links and borrowed capabilities
* dynamic changes over time (especially in mutation research)

Rift exposure does not rewrite Melder semantics; it wraps them.

---

## 9) Relationship to CommandOps and Mutation Research

This design intentionally supports the “living organism” vision:

* **CommandOps missions** can hold RiftTokens and operate through remotes as part of stateful loops.
* Mutation research can be expressed as:

  * using specific lab surfaces/conduits,
  * operating through a rift-mediated capability envelope,
  * producing runtime-first experimentation without forcing everything through static code workflows.

AethericRift is the “infra-as-tools” gateway; CommandOps is “law, culture, scheduler.”

---

## 10) Safety and Responsibility Stance

We explicitly accept:

* the system can expose extreme power
* the user decides what is permitted
* ACLs are explicit control choices, not a guarantee of “safety”
* endpoint security, transport-layer auth, external threat models are out of scope

The correct philosophical disclaimer:

> AethericRift is designed to be placed behind whatever boundary a system owner chooses
> (in-process only, internal trusted runtime, or wrapped by an endpoint they own).

---

## 11) Acceptance Criteria (Philosophical)

This ticket is satisfied when the team agrees on the following mental model:

* AethericRift is a library-level entrance to Melder; it does not own endpoints.
* AethericSpace stores real objects and enables stateful toolchain workflows.
* Exposure is lineage-anchored; execution resolves to versions through conduits.
* Conduit surfaces provide environmental reality; rifts don’t bypass conduit rules.
* ACLs are explicit and owner-defined; they may allow anything, including private/dunder access, if intentionally configured.
* Effective permissions are always an intersection of lineage, conduit surface, and remote/token profiles.
* The system naturally supports multi-step, queued, and optionally parallel workflows using scopes/context.
* The division of responsibility remains clean:

  * Melder = living architecture (graphs, conduits, lineages, existence)
  * AethericRift = capability exposure + scoping + ACL enforcement
  * CommandOps = agents/missions/policies operating on that substrate

---

## 12) Notes and Open Philosophical Questions

* How do we want to represent “surface identity” across multiple conduits and surrogate conduits so that exposure stays comprehensible?
* How do we want to reason about “follow current” vs “pinned version” in a world where callers can hold long-lived objects in AethericSpace?
* How should incidents/telemetry be expressed when ACL violations occur (purely diagnostic vs governance-enforced)?

These are not implementation questions; they’re stability-of-meaning questions.

---

If you want, I can also restructure this into a **two-part ticket** (AethericRift/AethericSpace core + ACL philosophy as its own RFC) so it’s easier to reference when you start mutation research, without re-litigating “endpoint vs not” every time.
