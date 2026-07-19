# Persistence Design Detail — CRUD Adapter + MutationResearchCrystal (full context)

## Metadata
- Artifact ID: ART-2026-07-03-persistence-design-detail
- Epic: EPIC-2026-07-03-crystallizer-persistence
- Parent: EPIC-2026-07-02-agent-object-persistence-loop
- Status: active ; Agent: crystal_0 ; Created: 2026-07-03
- Companions: first-cut + bootstrap design details, the code-map/proof-ledger, Crystallizer V2 +
  MR V2 canon.

## Purpose
The single, host-owned storage seam every other layer rides: one db-write entry + one hydrate/load
point. Defines the CRUD adapter contract and makes MR persist through it (MutationResearchCrystal).

## The adapter contract (P1)
- Persistence model = a callable the HOST implements satisfying a specific PROTOCOL (typed contract,
  canonical) OR a JSON codec (portability option). Owner preference: class contracts canonical, JSON as
  the option. Aligns with Crystallizer V2 Duty 3 (JSON in/out, adapters, host owns storage shape).

## CRUD + transactions (P2, P3)
- CRUD verbs: create / read / update / delete over NAMED DATASETS.
- A "transaction" = an ORDERED BATCH of CRUD ops applied ATOMICALLY (all-or-nothing).
- Crystallizer defines the payload SHAPES; the host owns the tables/backend.

## Single seam (P4)
- ONE db-write entry point + ONE hydrate/load point. Everything (first-cut crystals, bootstrap
  snapshots, MR composition) flows through this one seam. (= parent M7, = bootstrap epic's storage
  dependency, = first-cut C6 stub.)

## MutationResearchCrystal (P5) - the MR data seam
- MR's composition persists as MutationResearchCrystal through this CRUD layer: ResearchStream
  (branch: name, optional branch_type, head pointer, index associations), VersionRecord (spell_id
  SHA snapshot, parents, branch, timestamps, change reason, crystal reference, optional module-version
  SHA), heads, index associations. This is HOW git-style ops reload/unload into the system.
- Persistence ONLY conveys the data - it has no idea what a branch/head MEANS. MR semantics live in MR's
  lane. On load, crystallizer hydrates the composition back into MR's in-memory objects (MR V2).

## Reference adapters (P6)
- SQLite mock (tests) + plain JSON-file adapter (emit + read-back). These double as the reference
  implementations of the contract.

## Crystallizer <-> MR: two narrow seams (subsystems properly separated)
- READ seam: crystallizer gives MR always-readable source CUSTODY + the DEPENDENCY GRAPH; MR queries
  them (that's how the impact engine sees blast radius). Crystallizer doesn't know MR is reading.
- WRITE seam: MR conveys MutationResearchCrystal through THIS adapter; crystallizer hydrates on load.
- MR depends on crystallizer (+ Nexus); crystallizer NEVER depends on MR. Crystallizer is standalone
  (bootstrap tool) without MR. MR is a separate program with its own canon (MR V2 + parked merge model).

## Scaffold + alignment
- 0-byte scaffold dirs (prior survey): crystallizer/crystal_loader/, /asset_management/. asset_transaction
  stub. Realizes parent M7.

## Open questions
- Typed-protocol vs JSON default per dataset. Dataset + key schema (soft assignment + keys for
  DB-loaded systems). Whether MutationResearchCrystal is one dataset or several (streams/versions/heads).
