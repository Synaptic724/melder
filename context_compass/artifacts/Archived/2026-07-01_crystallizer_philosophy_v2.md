# Crystallizer Philosophy V2 (Custody + Unfold)

## Metadata
- Artifact ID: ART-2026-07-01-crystallizer-philosophy-v2
- Parent Ticket: TASK-2026-07-01-crystallizer-mutation-research-philosophy-orientation
- Status: active
- Supersedes: ART-2026-04-26-crystallizer-philosophy (where conflicting; core thesis intact)
- Created: 2026-07-01T23:45:00Z
- Updated: 2026-07-02T00:30:00Z

## Purpose
Refresh the April crystallizer philosophy for the MutationResearch tool model
(see `2026-07-01_mutation_research_philosophy_v2.md`). The April doc's core remains true;
this document sharpens three duties and sets the build order. Where they disagree, THIS
document wins.

## North Star
A kube container holds a project and a small bootstrap. On start, crystals unfold into
synthetic modules, conduit world slices rebuild, frame and system configuration restores -
the whole checkpointed application is simply UP. Instant start, dynamic conduit loading,
everything reconstructed from retained truth.

From there, agents work at dev stations (Nexus workstations) building new objects - and
every object build comes with an impact map: what depends on it, what a change or removal
hurts, what else must move before a commit is honest (the MR impact engine; see the MR V2
document). Crystallizer's job in that picture is the unfold and the custody: everything
the assessment tools read, it retained; everything the bootstrap rebuilds, it saved.

## Core Thesis (Unchanged)
Crystallizer is the source-truth, persistence, and recovery bridge for managed software
artifacts. It is the SAVING tool and the REGENERATION system - the means by which worlds
unfold. It is not a second runtime, not a package manager, not an analyzer of change, and
it does not own MutationResearch graph semantics.

## Three Sharpened Duties

### 1. A crystal for every bound object (source custody)
Every object that crosses `bind` gets a `SpellCrystal`. Bind remains THE promotion boundary
from local construction into durable world truth; V2 makes the crystal mandatory at that
boundary rather than eligible.

Consequences:
- every spell version in MutationResearch has crystal-backed source truth by construction
- checkout of any historical version is always possible (rematerialize from crystal ->
  `bind_inactive` -> `notch`)
- the MR impact engine can ALWAYS read any object's source - codegen-born, file-born,
  synthetic, or mixed. Custody is crystallizer's contribution to change analysis; the
  analysis itself is MR's (code-based) and Sentinel's (runtime-based), not crystallizer's.
- file-backed binds capture the FULL module string (bridge-mechanic rule retained), codegen
  binds capture the synthetic source; authority classes from the April doc still apply

### 2. Per-version structural facts + load-order analysis
Crystallizer records what each retained version IS, and what the loader needs to unfold it:
- module/source truth: source text, source SHA256, canonical module name, authority kind
- module-version identity: full-module-text SHA256, distinct from the spell fingerprint
- dependency truth for UNFOLD ORDERING: imports, from-imports, export surface,
  internal/external dependency view - the existing `crystal_analysis/strategies/` scaffold
  is exactly this (import_statement / from_import_statement / export_surface)

Boundary (changed from the earlier V2 draft): blast-radius and change-impact analysis do
NOT live here. That is MutationResearch's impact engine, which reads crystal-custodied
source and queries melder's own dependency graph. Crystallizer computes save-time facts
about one version; it never judges a change.

### 3. MutationResearch hydration and persistence
Crystallizer is where ALL MutationResearch data lives.

- at activation: crystallizer loads the MR composition datasets (streams, version records,
  head pointers, index associations) and hydrates MR's in-memory objects so agents can
  query them
- at runtime: MR emits transaction-shaped plain-data payloads (stream created, version
  recorded, head moved, association changed); crystallizer routes them through the adapter
  contract
- adapter contract: JSON in / JSON out; transactions emitted as ordered plain-data lists;
  the HOST owns storage shape and update semantics
- first adapters: a SQLite mock adapter for tests, and a plain JSON file adapter
  (emit + read-back). These double as the reference implementations of the contract.

## What Stays True From April
- bind is the promotion boundary; publication (`sys.modules`) is never persistence
- conduit snapshots are the primary reload unit; single spells are not the honest unit
- synthetic modules are first-class: live in-memory embodiment, activation into
  `sys.modules` under canonical names, copy mode only at bootstrap/rebuild/reload
  boundaries (the hot-swap experiment boundary is non-negotiable)
- environment/package truth stays separate from world/module truth; `uv`-first validation;
  the loader validates and throws, it never becomes a package manager
- persistence is adapter-driven; crystallizer defines payload shapes, hosts own tables
- files are optional projections; the file <-> memory bridge mechanic stands

## What Changes From April
- crystals: from "eligible at bind" to "created at bind, always" (custody duty)
- `crystal_analysis/`: from placeholder scaffold to a named save-time facts + unfold-order
  service; impact/blast-radius analysis explicitly relocated to MR
- MR relationship: from "MutationResearch emits mutation transaction data into
  Crystallizer" (true but vague) to a concrete hydrate-at-boot / transact-on-change
  contract over named composition datasets
- mutation manifests in conduit snapshots now mean: the MR composition slice relevant to
  that conduit's world (streams + version records + heads for its indexes)

## Synthetic Module Integration (Build Target)
The loader chain gets built in this order, each stage consuming the previous:
1. `bootstrap_manifest` - what assets/crystals/modules/conduit slices a restore needs
2. `crystal_loader` - resolve crystals into activatable module/source truth
3. `synthetic_module_loader` - activate retained modules into `sys.modules` under canonical
   names (parent shells included; imports keep working unchanged)
4. `bootstrap_loader` - the internal loader: validate environment prerequisites (uv.lock as
   reference), activate modules, rebuild world slices, restore the MR composition, throw on
   missing prerequisites

This chain IS the north star's unfold step.

## Build Order (Shared With MR V2)
1. MutationResearch tool (composition + API + orchestration + transaction emission)
2. Crystallizer build-out: universal crystal-at-bind, save-time facts, adapter contract +
   SQLite/JSON adapters, MR hydration, then the loader chain above
3. MR impact engine (reads custody + facts from here, graph from melder)
4. Dynamic/introspective features afterward

## Summary
Crystallizer keeps its April identity - the saving tool and regeneration system - and gains
three sharpened duties for the tool model: source custody via a crystal for every bound
object, save-time structural facts plus unfold-order analysis (never change judgment,
which belongs to MR's code-based impact engine and Sentinel's runtime analyzer), and full
custody of MutationResearch's persisted composition behind a JSON-first adapter contract
testable against SQLite or plain JSON files - all in service of the north star: a small
bootstrap that unfolds a checkpointed application instantly, with agents building on top.
