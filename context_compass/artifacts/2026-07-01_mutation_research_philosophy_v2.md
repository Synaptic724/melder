# Mutation Research Philosophy V2 (Tool Model)

## Metadata
- Artifact ID: ART-2026-07-01-mutation-research-philosophy-v2
- Parent Ticket: TASK-2026-07-01-crystallizer-mutation-research-philosophy-orientation
- Status: active
- Supersedes: ART-2026-05-09-mutation-research-philosophy (where conflicting)
- Created: 2026-07-01T23:45:00Z
- Updated: 2026-07-02T00:30:00Z

## Purpose
Refine the May mutation philosophy into the model the runtime is now actually built for.
User-directed 2026-07-01. The May artifact remains valid background reading; THIS document
wins wherever the two disagree.

## Why A V2 Exists
Three runtime facts landed after the May philosophy was written and changed its ground:

1. The corrected SpellIndex model: an index holds ONE active selected spell plus a member
   set; version history belongs to MutationResearch, not the index.
2. Index operations became real mediated transactions: `bind_inactive` stages a candidate as
   a parked member with a concrete SHA256 `spell_id`; `notch` promotes it under a sealed
   NOTCH transaction whose commit now runs bind-parity structural validation and gates the
   promoted id's per-conduit verdicts. Promotion is a solved runtime mechanic.
3. The transaction admission plane (mediator + embargo claims) owns sealing and drain
   semantics. Nothing above it needs to re-own gates.

Because of these, the May design's heavier constructs are no longer required.

## Core Thesis
MutationResearch is a TOOL: the internal git system for managing spells, plus the
CODE-BASED analyzer agents use to understand change.

It is:
- the agent-facing API for facilitating spell change and querying structure history
- a queryable in-memory composition of branches, version records, and index associations
- the impact engine: the "mini rust-style compiler" that maps the blast radius of a
  proposed change against the live object world
- a diff-presentation layer over full-object versions

It is not:
- a runtime peer or second root
- an owner of gates, transactions, or object lifecycles
- a runtime-behavior analyzer (that is Sentinel/Interceptor in CommandOps)
- a persistence engine (that is crystallizer's adapter contract)

## Code Analysis vs Runtime Analysis
Two analyzers exist in the stack, split exactly along the package seam:

- MutationResearch (melder): CODE-BASED analysis - source, surfaces, versions, dependency
  structure. "What does the code say happens if I change this?"
- Sentinel/Interceptor (CommandOps): RUNTIME-BASED analysis - interception, observed
  behavior, breakpoint gates, watchdogs, live trial via versioned revertible replacement
  chains. "What does reality say about how this behaves?"

Neither reaches across the seam. A future assessment surface (the compiler-dream
assessment system) composes BOTH at the agent's tool surface - static verdicts from MR,
behavioral evidence from Sentinel - without merging the systems.

## The Git Mapping
- melder runtime = the working tree (live objects, staging, promotion, sealing)
- MutationResearch = refs + object index + porcelain (branches, heads, history, the API)
- Crystallizer = the object database + source custody + persistence adapters

## Responsibility Matrix
- Spell (melder):
  - SHA256 identity - each spell is unique by its nature
  - execution, lifecycle, ownership; low-level mutation primitives stay spell-owned
- SpellIndex (melder):
  - the stable runtime handle; one active selected spell; member set
- Runtime mechanics (melder):
  - direct live bind (agents may bind a new object and use it immediately)
  - staging = `bind_inactive` (parked member, real spell_id, unmeldable until promoted)
  - promotion = `notch` (mediated transaction; commit-backed validation + verdict gating)
  - sealing = mediator/embargo plane
  - dependency graph truth: the compiler already knows who depends on whom (symbolic
    graphs, blueprints, contracts, index-links) - MR QUERIES it, never re-derives it
- MutationResearch:
  - composition objects (below), agent query API, the impact engine, diff presentation,
    orchestration of the mechanics above per mutation act, persistence-transaction emission
- Crystallizer:
  - a SpellCrystal for EVERY bound object (bind = crystal creation) = SOURCE CUSTODY -
    the impact engine can always read any object's source
  - hydration of the MR composition at load; persistence of MR transactions via adapters
- Sentinel/Interceptor (CommandOps):
  - the runtime-based analyzer; out of MR's scope by design

## Composition Objects (In-Memory, Queryable)
On system load, crystallizer hydrates the MR composition datasets into memory so agents can
query the MR system directly.

### ResearchStream (branch)
- `branch_name`: freeform string; default `default`
- `branch_type`: optional enum (`development` | `experiment` | `production` | `test`),
  required only when `branch_type_enforcement` is on (retained from the May branch-type
  artifact; it is policy on stream records)
- head pointer: the stream's current version record
- index associations: one-or-many SpellIndex ids; CONVENTION is one index per branch,
  deliberately not enforced
- lifecycle metadata (created/updated, owning agent/campaign)

### VersionRecord
- `spell_id`: the SHA256 snapshot identity (the version IS the spell)
- parent version(s): ancestry, including merge parentage later
- branch association, timestamps, author agent, change reason
- crystal reference: the SpellCrystal backing this version's source truth
- optional module-version SHA when module truth moved with the change

### Query Surface (agent-facing)
- list streams; stream detail (head, indexes, type, activity)
- history of an index or stream; what is at head; what is active in the runtime
- divergence between streams; version detail; impact reports (below)

## Full Objects, Never Diffs
Retained and strengthened from May: each iteration in the system is a FULL object.

- a version is a real Spell with a real SHA and crystal-backed source
- diffs are DERIVED views computed between two full versions, never the storage form
- pruning a version removes one candidate, not the meaning of later versions

## The Impact Engine (The Change Compiler)
MR owns blast-radius analysis. The agent workflow it serves:

1. an agent builds a new code object at a Nexus workstation, binds it (directly and live,
   or staged), and unittests it at runtime
2. before COMMITTING the change (replace/remove/promote), the agent asks MR to map the
   blast radius
3. MR reports with compiler-grade precision: "removing `method_x` breaks objects 1-3 -
   object_1 calls it in `process()`, object_2 stores its result" - named, located,
   actionable
4. the agent sees the real shape of the change, widens the change set, THEN commits

Three inputs, none re-invented:
- old-vs-new surface diff: MR parses both versions' source (methods, attributes,
  signatures, docs)
- dependent usage maps: MR's AST analysis over the dependents' source - what each
  dependent actually touches on the target (crystal custody guarantees the source is
  always readable)
- dependent enumeration: melder's own dependency graph answers WHO depends; MR never
  re-derives edges the compiler already owns

The impact engine is the analytical twin of the runtime's hard guards: the ward RAISES
when a contract-locked removal is attempted; the impact engine explains why and what to
fix first, before the guard is ever hit.

## The Mutation Act
1. agent calls the MR API with the target index (and stream, or `default`)
2. candidate materialization: new source -> crystal -> either direct live bind (use it
   now) or `bind_inactive` staging (parked member)
3. MR records the VersionRecord on the stream and emits persistence transactions
4. pre-commit: the agent runs the impact engine; widening happens here
5. promotion when chosen: `notch` (or the direct-bind equivalent commit) - the sealed
   transaction performs structural checks and arms meld revalidation; MR moves the stream
   head and records it

## Checkout
Any historical version can rematerialize: rebuild source from its crystal, stage via
`bind_inactive`, promote via `notch`. This is why crystal-backed retention per version
record is mandatory - it is what keeps old versions checkout-able.

## Persistence Contract
MR keeps NO private persistence. All composition data lives in crystallizer's systems:
- MR emits transaction-shaped plain-data payloads (stream created, version recorded, head
  moved, association changed)
- crystallizer routes them through its adapter contract (JSON in / JSON out; host owns
  storage shape)
- test posture: a SQLite mock adapter, or plain JSON emit + read-back
- on load, crystallizer hydrates the composition back into MR's in-memory objects

## The AIX Contract (Design Principle)
The MR API is built for the agent as an inhabitant, not a builder:

- full situational awareness, zero required mechanism knowledge: an agent should know
  where it is, what it is building, who depends on it, and what its change touches -
  without understanding phases, gates, claims, or verdicts
- "you don't need to know how to build a house to live inside one"
- small verb set: build, bind, test, map impact, commit
- errors that teach: impact reports arrive at the moment of need, name the specific
  surface, and say what to do next - the system documents itself through its refusals
- if using the tool requires understanding melder internals, the tool has failed

## Kill List (From The May Model)
- `SpellMutationNode` / `CreationMutationNode`: retired. The Spell + its SpellCrystal +
  compiler/cache bundles ARE the snapshot; a bespoke node graph duplicates them.
- `MutationConduit` as gate-orchestrator: retired. The mediator plane owns sealing; notch
  commit owns promotion checks; the agent surface is the MR API itself.
- `MutationFrame`: retired. The May doc already marked it go/no-go; the tool model has no
  frame-scoped need.
- Diff-chain or node-ledger thinking anywhere: versions are full objects.

## What Survives From May
- snapshot-first (strengthened above)
- lanes/streams with one head each (now the ResearchStream object)
- branch naming + optional BranchType enforcement (config-level policy)
- module-integrity concerns: module-version SHA and blast-radius verdict classes
  (`target_only` | `sibling_spell_impact` | `module_context_impact` | `mixed` | `unknown`)
  now live inside MR's impact engine, reading crystal-custodied source
- restricted vs unrestricted module mutation postures (policy over impact verdicts)
- multi-agent research intent: parallel streams, later convergence

## Open Questions (Deliberately Kept Open)
- world merge semantics across streams/conduits: bind collisions, link topology, authority
  selection (IMPORTANT_CONSIDERATION still governs; merge-model decision remains parked)
- fork-to-new-lineage rules when a fork must become a separately live callable future
- unrestricted module mutation ergonomics (rename/republish flows)
- the assessment fusion: how MR verdicts and Sentinel behavioral evidence compose into one
  agent-facing assessment (the compiler-dream assessment system; sized at roughly +20k LOC
  on top of MR's ~20k core)

## Build Order
1. MutationResearch tool: composition objects, query API, mutation-act orchestration over
   the existing runtime mechanics, transaction emission
2. Crystallizer build-out: universal crystal-at-bind, source-custody facts, adapter
   contract with SQLite/JSON test adapters, MR hydration, synthetic-module integration and
   the loader chain
3. The impact engine (needs 1 + 2: versions to compare, custody to read, graph to query)
4. Dynamic and introspective features afterward (recomposition, richer world merge,
   assessment fusion with Sentinel)

## Summary
MutationResearch is the internal git for spells and the stack's code-based analyzer: a
queryable in-memory composition of research streams and full-object version records, an
agent API that materializes candidates through live bind or `bind_inactive`, promotes
through `notch`, and - before any commit - maps the blast radius of a change with
compiler-grade precision by reading crystal-custodied source and querying melder's own
dependency graph, while Sentinel remains the runtime-based analyzer on the CommandOps side
and crystallizer holds all persistence behind its adapter contract.
