# [Ticket] AethericRift Interaction Modes — Static Exposure vs Workstation REPL (Philosophical Design)

**Labels:** `melder-core`, `aetheric-rift`, `repl`, `workstations`, `static-exposure`, `object-refs`, `acls`, `sessions`, `scopes`, `surfaces`, `infra-as-tools`

---

## 1) Intent

Define the **philosophical split** inside **AethericRift** between two interaction modes:

1. **Workstation / REPL Mode** — an interactive, stateful "bench" where agents/users operate over time, create and compose objects, and chain multi-step workflows.
2. **Static Exposure Mode** — an endpoint-oriented, intentionally narrow interface where a system owner exposes **specific objects + methods** and callers can only do **direct method calls** (still stateful objects, but no dynamic bench UX).

This ticket is about **meaning** and **runtime semantics**, not about endpoint transport (FastAPI/MCP/etc.) and not about monetization or distribution.

> AethericRift is library-level infrastructure.
> If someone wants HTTP/MCP/etc., they wrap Rift.
> The wrapper owns transport, auth, rate limits, serialization boundaries.

---

## 2) Non-Goals

* Not an endpoint spec (no REST routes, no JSON schema decisions).
* Not MCP compliance details.
* Not auth provider design (OAuth/JWT/etc.).
* Not a sandbox or safety product.
* Not a pricing / paid services discussion.

---

## 3) Core Concepts (Shared by Both Modes)

### 3.1 Conduit Reality Always Applies

* **Spells** define what can exist.
* **Conduits** define where/how spells live (existence rules, lifetimes, scoping, resolution surfaces).
* **Scopes** are the runtime session envelopes inside a conduit.

Rift never bypasses the conduit. All meaningful work happens inside a **surface + scope**.

### 3.2 Surface

A **Surface** is a named execution reality for Rift (often a conduit or surrogate conduit).

* One Rift can expose multiple surfaces (e.g. `dev`, `lab`, `prod`).
* Surrogate conduits remain the recommended surface form for curated / controlled exposure.

### 3.3 Sessions and Remotes

A **Session** is the unit of interaction ownership:

* A caller connects (internal agent or external adapter) and receives a session context.
* Sessions end explicitly or via policy (idle TTL / absolute TTL), followed by cleanup.

A **Remote** is the conceptual permission-bearing view used within a session.

### 3.4 ObjectRefs (Opaque Handles)

If the caller is not literally operating in-process with direct object references (and even for uniformity), Rift returns **ObjectRefs**:

* **ObjectRef** is opaque and session-bound (default stance).
* ObjectRefs always map to real objects living inside the server/runtime.
* The system may also support releasing refs or TTL-based eviction.

> Even if we refuse to call it a “handle protocol,” any cross-boundary integration implies opaque references.

### 3.5 ACLs and Effective Permission

Rift enforces **explicit owner-defined exposure** via ACL intersection:

* **Lineage ACL** (spell/lineage policy)
* **Surface/Conduit ACL** (environment policy)
* **Remote/Session ACL** (caller slice)

Effective permission is always the **intersection**.

Rift is not moralizing; the owner decides what is permitted.

### 3.6 Canonical Call Spec

Both modes compile to the same canonical internal representation:

**CallSpec** (conceptual):

* `session_id`
* `surface_id`
* `scope_id` (explicit or implicit)
* `target_id` (lineage/object/tool)
* `action` (invoke/construct/inspect/mutate/etc.)
* `args`
* `acl_profile` (derived)

The front door differs (text REPL vs direct method call), but the engine is the same.

---

## 4) Mode A — Workstation / REPL Mode

### 4.1 Definition

Workstation mode is a **stateful interactive bench** where a caller can:

* create objects inside a scope
* store results in a bench
* chain multi-step workflows
* reuse objects across steps
* optionally queue commands and run ordered or batched sequences

The user/agent is not merely “calling tools.” They are **operating inside a living substrate**.

### 4.2 Workstation Semantics

A workstation has:

* a **session**
* a chosen **surface**
* one or more active **scopes**
* an **AethericSpace** bench (object store + named bindings)

This is where “interactive system” lives.

### 4.3 REPL Command Language

The REPL is a **syntax**, not the semantic core.

* REPL input is text.
* Text parses into CallSpecs.
* Results are returned as data and/or ObjectRefs.
* The bench can bind ObjectRefs to human-friendly symbols (e.g. `$1`, `@db`, `bench.foo`).

### 4.4 What Workstation Mode Enables

* exploratory workflows
* multi-step agent missions
* runtime-first probing
* toolchain composition across objects
* long-lived sessions with explicit cleanup

### 4.5 Policies

Workstations must be policy-governed:

* idle timeouts
* maximum object count / memory policy (optional)
* scope lifetime boundaries
* explicit teardown contracts

Workstation mode is not about being "safe" — it’s about being **coherent**.

---

## 5) Mode B — Static Exposure Mode (Endpoint-Oriented, Call-Only)

### 5.1 Definition

Static Exposure mode is for callers that want:

* “Call this method on that object/tool.”
* “Give me the return.”

The object being called may be stateful.

The key difference is not object state.
The key difference is **no bench UX** and **no dynamic exploration surface**.

### 5.2 Exposure Is Explicit Registration

Static exposure is owner-defined:

* The owner registers **targets** (objects, lineages, tools)
* The owner registers **allowed methods/actions**
* The owner selects surfaces and ACL slices

Static exposure is not “whatever exists in the runtime.”
It is a curated interface.

### 5.3 ObjectRefs Still Exist

Static exposure can still return ObjectRefs because:

* stateful objects may need to persist across calls
* long workflows may involve chained references

However:

* callers do not get bench management (no “workspace variables”)
* callers do not get broad discovery or introspection unless explicitly allowed

Static mode is **call-only**, not “interactive substrate.”

### 5.4 Invocation Semantics

Static mode should feel like:

* `call(target_ref, method_id, args) -> result`

And nothing more.

The runtime still uses sessions/scopes for coherence and cleanup, but the interface stays narrow.

### 5.5 Intended Use

* HTTP endpoints built by the customer
* MCP tools built by the customer
* simple external integrations
* stable surfaces for production usage

---

## 6) Why Two Modes Exist

This split prevents two common failures:

1. **Forcing everyone into “bench land”** when they only want a stable callable interface.
2. **Accidentally exposing the entire runtime substrate** when the owner only wants to expose a few capabilities.

Workstation mode is the power user / agent mission world.
Static mode is the operational integration world.

Same engine. Different policies.

---

## 7) Relationship to CommandOps

* CommandOps can supervise sessions/workstations as first-class runtime entities.
* CommandOps can provide scheduling, command queue semantics, overwatch patterns, incident capture, and deterministic cleanup discipline.
* Static exposure mode remains compatible: it is still just CallSpecs executed through Rift.

Rift is the interface substrate.
CommandOps is law/culture/scheduler.

---

## 8) Acceptance Criteria (Philosophical)

This ticket is satisfied when we agree on the following mental model:

* AethericRift is a library-level gateway.
* Both interaction modes share the same internal CallSpec engine.
* Workstation/REPL mode provides a stateful bench (AethericSpace) with scoped lifetimes.
* Static exposure mode is explicit registration + call-only interaction (still sessioned, still ObjectRefs).
* ACL enforcement is the single arbiter of allowed capability.
* Surfaces are first-class and can represent curated surrogate conduits.
* Transport is out of scope; wrappers adapt external calls into Rift.

---

## 9) Open Philosophical Questions

* Should static mode require an explicit session always, or support an implicit “ephemeral session per call” adapter pattern?
* How should ref lifetime be expressed for static mode (session-bound only, TTL, explicit release)?
* What is the minimum discovery surface in static mode (none, list only registered methods, or allow optional introspection under ACL)?
* How should multi-scope workstations be expressed (single active scope vs multiple concurrent scopes)?

---

## 10) Notes

This ticket intentionally does not cover:

* package distribution, paid update channels, Cloudsmith/Azure artifact hosting
* commercial license mechanics
* endpoint design
* security sandboxing

Those belong in separate tickets.
