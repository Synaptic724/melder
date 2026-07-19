# [Ticket] CommandOps Mutation Research - Community vs Enterprise Networking (AgentNet vs CommandNet)

**Labels:** commandops, architecture, mutation-research, community-vs-enterprise, networking, agentnet, commandnet

---

## 1. Intent

This ticket **philosophically defines** how mutation research works in CommandOps across two worlds:

1. **Community / Core Runtime** - single-app, single-process, no networking stack, but full access to AgentNet, sockets, cascades, SpellState, and Melder.
2. **Enterprise Runtime** - multi-zone, multi-app, with CommandNet-based networking and dedicated *research slave apps* running as separate CommandOps instances.

The goal is not implementation detail, but to lock in **what is allowed where**, and **how mutation research is framed** conceptually in each tier.

---

## 2. Core Concepts (Reused Across Both Tiers)

These are shared primitives; the difference between community and enterprise is **how far they reach**, not what they are.

### 2.1 AgentNet (Always Present)

* **AgentNet** is the **local mailbox + message stream** system.
* It is **in-process only** in the community edition.
* It owns:

  * Mailboxes per mission / agent.
  * A message stream abstraction (events, commands, replies).
  * The local scheduling contract (missions pull from their mailbox and do work).
* AgentNet does **not** care about networking - it only sees messages and identities.

### 2.2 Missions and Threads

* A **mission** is a long-running logical loop that consumes messages and produces work.
* In CommandOps, missions typically map to **threads** (or thread-bound event loops):

  * An AgentNet mission thread.
  * Conduit / orchestration missions.
  * (Enterprise) CommandNet missions.
* Threads belong to the runtime; agents and tools submit **intent**, not threads.

### 2.3 Sockets (DI/Contract Sockets)

* A **socket** is a **hole in the system** where an implementation can be bound:

  * Real spell / service.
  * Substitution / mock / proxy.
  * Mutation candidate.
* Sockets are already required for:

  * Late binding.
  * Revalidation.
  * Contract enforcement.
* Mutation research reuses this exact mechanism: research work simply binds **different providers** into existing sockets.

### 2.4 Cascades (Runtime Interceptors)

* **Cascades** are predicate-based interceptors that:

  * Observe calls (probe mode).
  * Record state / events (trace mode).
  * Optionally rewrite behavior/results (patch mode).
* Cascades are the **AOP-style hooks** for:

  * Probes/invariants.
  * Runtime debugging.
  * Experimental behavior during research.
* Probes are *part of* cascades, not something separate.

### 2.5 SpellState / ChangeControlCore / Incidents (Control Plane)

* **SpellState**: per-spellline runtime brain - stores validity, dirty reasons, mutation flags, and resolution gates.
* **ChangeControlCore**: tracks fallout - which roots depend on which spells, and which spells/roots are dirty.
* **IncidentManager**: collects structured incidents (validation failures, graph dirty, mutation failures, etc.).

These provide the **control plane** for both community and enterprise mutation research.

---

## 3. Community / Core: Mutation Research Inside a Single App

### 3.1 Constraints

* **No CommandNet.** Community/core runtime has **no networking stack** attached.
* All work happens in **one process**, in **one CommandOps app instance**.
* Only **AgentNet** is available:

  * missions, mailboxes, message streams,
  * but all local.

### 3.2 What Mutation Research Looks Like in Community

In community mode, mutation research is **local and scoped**:

* Mutation work runs in **dedicated missions/threads**:

  * AgentNet routes mutation jobs to a specific mission.
  * That mission owns a local workspace / scope.
* Each mutation workspace has its own:

  * Conduit(s) configured for research.
  * Sockets bound to mutation candidates or substitution objects.
  * Cascades attached for observation/probes.
* Thread kill + scope disposal is the hard boundary:

  * If a mutation mission misbehaves, the runtime can:

    * Kill that mission/thread via the internal killswitch.
    * Dispose its scope (Cleanable-style):

      * Remove it from Spellbook / AethericFrame.
      * Null out references.
      * Ban resolution via SpellState.
      * Mark affected spells/roots dirty in ChangeControlCore.
      * Emit incidents via IncidentManager.

### 3.3 Lineages: Prod vs Research (Community View)

* **Prod lineage**:

  * Small, curated spell versions.
  * Only spells that passed validation + promotion.
  * Used by all normal conduits and user workloads.

* **Research lineage**:

  * Potentially many experimental versions.
  * Created and run only inside mutation workspaces.
  * Most research spells **never** become prod versions.

Promotion is an explicit act:

* Research results are distilled into **change plans**.
* A change plan is applied to the prod lineage using existing control-plane machinery:

  * SpellState updates.
  * ChangeControlCore fallout.
  * Incidents if something goes wrong.

### 3.4 Philosophical Boundaries (Community)

* Community users get a **powerful local lab** inside a single app:

  * They can run research missions, experiments, cascades.
  * They can generate and test new spell graphs.
* They do **not** get distributed zones, slave apps, or cross-process AgentNet.
* The guiding principle:

  > "One runtime, many scopes. Mutation is powerful but locally contained."

---

## 4. Enterprise: CommandNet, Zones, and Research Slave Apps

### 4.1 CommandNet vs AgentNet (Enterprise View)

* **AgentNet (Enterprise)**

  * Same as community: in-process mailboxes, message streams, missions.
  * Still the **core orchestration layer** inside each app instance.

* **CommandNet (Enterprise-only)**

  * A **networking skin** around AgentNet.
  * Implemented as one or more **CommandNet missions** per CommandCenter.
  * Each CommandNet mission:

    * Subscribes to certain AgentNet streams.
    * Serializes messages (e.g., TOON).
    * Ships them over a chosen transport:

      * raw sockets,
      * HTTP,
      * Redis,
      * RabbitMQ,
      * Kafka, etc.
    * Deserializes inbound messages and pushes them into local AgentNet.
  * Core never hard-depends on any specific transport. Transports are a **pluggable, enterprise-only concern**.

**Key rule:**

* Community = AgentNet-only.
* Enterprise = AgentNet **plus** CommandNet missions if configured.

### 4.2 Zones: Multiple App Instances as Separate Worlds

In enterprise mode, CommandOps can run multiple **zones**:

* Each zone is a full CommandOps app instance:

  * Its own CommandCenter.
  * Its own AgentNet.
  * Its own AethericFrame + Spellbook + Conduits.
  * Its own persistence stream.
* Zones talk to each other via **CommandNet missions** using the chosen transport.

Typical roles:

* **Zone 0 - Primary / Operational**

  * Handles user-facing workloads, production missions, and stable agents.
  * Runs in a conservative mode: cascades mostly probe/observe, mutation constrained.

* **Zone N - Research / Slave Apps**

  * Each "slave app" is a zone focused on research:

    * Aggressive cascades (patch mode, AOP surgery).
    * Structural graph mutation.
    * Simulation and scenario runs.
  * They can be:

    * on the same host,
    * or remote hosts (GPU boxes, separate servers).

### 4.3 Mutation Research in Enterprise

In enterprise, mutation research is **federated across zones**.

* Primary zone can:

  * Dispatch research missions to slave zones via CommandNet.
  * Provide snapshots of prod spell graphs and configs.

* Research zones:

  * Rebuild spell graphs locally via Melder.
  * Attach cascades for deep introspection.
  * Run large mutation campaigns and simulations.
  * Produce **ReleasePlans** and diagnostics as TOON payloads.

* Primary zone:

  * Receives ReleasePlans from research zones via CommandNet.
  * Applies them using the same SpellState / ChangeControlCore / Incident pipeline.
  * Remains the **source of truth** for real traffic.

### 4.4 Persistence and Observability Across Zones

* All zones log into a shared or federated persistence layer:

  * Each record tagged with: `zone_id`, `frame_id`, `conduit_id`, `mission_id`.
* This allows:

  * Comparing research outcomes across zones.
  * Auditing decisions: which research zone proposed which change.
  * Replaying important scenarios in new zones.

Philosophically:

> Community gives you *one world with many scopes*.
>
> Enterprise gives you *many worlds (zones) that can talk*.

---

## 5. Philosophical Summary

1. **AgentNet is universal.**

   * It is the local nervous system: mailboxes, message flow, missions.
   * Exists in both community and enterprise.

2. **CommandNet is optional and enterprise-only.**

   * It is not a new brain, just a network skin over AgentNet.
   * Implemented as missions with pluggable transports (sockets, HTTP, Redis, Rabbit, Kafka, etc.).

3. **Mutation research is tiered.**

   * Community: research is local, scoped, and thread-bound:

     * mutation missions + scopes in a single app instance;
     * killswitch + scope disposal as containment.
   * Enterprise: research spreads into separate zones (slave apps):

     * each with its own CommandOps runtime;
     * talking over CommandNet;
     * primary zone as arbiter of what becomes prod.

4. **Lineages are split by purpose.**

   * Prod lineage: curated versions, small and stable.
   * Research lineage: large, noisy, mostly never promoted.
   * Promotion is explicit and always goes through the control plane.

5. **Holes are first-class.**

   * Sockets and cascades are not hacks; they are deliberate, structural holes:

     * for binding providers,
     * for inserting substitution objects and mutation candidates,
     * for intercepting and observing runtime behavior.
   * AI does not get a private runtime - it uses these holes inside the same system the human uses.

This ticket should be treated as the **philosophical north star** for:

* where mutation research is allowed to run,
* how networking is layered (or not) in community vs enterprise,
* and how CommandOps thinks about "worlds" (zones) versus "scopes" (workspaces) inside a world.
