# Crystallizer / Persistence — Coverage Gaps & Remaining Work

## Metadata
- Artifact ID: ART-2026-07-08-crystallizer-persistence-gaps-and-remaining-work
- Parent Task: TASK-2026-07-08-investigate-crystallizer-implementation
- Owner: cowork
- Agent Name: mutation_research_0
- Status: active
- Created: 2026-07-08T22:07:12Z
- Disposition: retain_as_reference

## Purpose
Record, with source evidence, what the current `persistence/` crystallizer engine
does NOT yet cover, so MutationResearch build work and any crystallizer follow-up start
from a truthful gap map rather than the (now-diverged) philosophy docs. Written after a
full read of the record->checkpoint->restore spine plus `SpellCrystal` in full.

## Context (one paragraph)
The built crystallizer is the `persistence/` EMIT->twin->checkpoint->restore engine
(wired live: `Aether` constructs it; `Conduit`/`Frame`/`Ward`/`Cluster`/`Spellbook`/
`Transfer` emit twins gated on `_crystallizer.activated`). It structurally FORKED from the
philosophy (crystal_loader chain + crystal_analysis + asset_management), which is dead
scaffold. The engine MEETS most philosophy GOALS via a different mechanism, but real gaps
remain. Evidence paths below are `src/melder/...` unless noted.

---

## 1. Crystal analyzer (`SpellCrystal`) vs `crystal_analysis` — what is MISSING

`SpellCrystal` DOES (evidenced): root target identity + full bind-signature capture
(binding_name/spellframe/existence/permissions/disposal/profile_family/rebindability);
module classification synthetic/user_source/site_package/unknown
(`_classify_module_target`, spell_crystal.py:1150); a TRANSITIVE source-level import walk
with cycle protection (`_walk_module_dependencies`:1473, `_extract_import_targets_from_ast`
:1288 via `ast.parse`); direct-dependency edges (`_module_to_direct_dependencies`);
synthetic-source harvest for rebuild (`_harvest_synthetic_source`:1578).

It does NOT cover the following (the doubt was correct):

1. EXPORT SURFACE (`export_surface_strategy`). SpellCrystal captures IMPORTS, never a
   module's public export surface (`__all__`, public classes/functions). No field, absent
   from `describe()`.
   EVIDENCE: spell_crystal.py:1288-1405 (imports only), :1620-1681 (describe has no exports).
   WHY IT MATTERS: MR's impact engine needs "what does this module expose" to compute the
   blast radius of a removed/renamed symbol; restore currently doesn't need it (re-executes
   source), so it was skipped.

2. EXPLICIT LOAD-ORDER / DEPENDENCY-VIEW artifact (`dependency_view_strategy`). Only DIRECT
   edges are stored; there is no topological load order and no partitioned internal-vs-
   external dependency view. Ordering is DEFERRED to restore heuristics: synthetic modules
   sort by name dot-depth (`restore_engine._rebuild_synthetic_world`:1558), binds follow the
   spellbook's recorded `bind_order`. Philosophy V2 Duty#2 wanted crystal-side unfold-order.
   STATUS: partial — edges yes, order no.

3. SITE-PACKAGE DISTRIBUTION PROVENANCE. site_package modules are classified by PATH only;
   the crystal records no distribution/package NAME or VERSION. Philosophy wanted
   dist-name + snapshot-time version for env validation.
   EVIDENCE: spell_crystal.py:1150-1210 (path classification, no dist/version capture).
   STATUS: missing (ties to section 3, env/assets).

4. BINARY / NON-SOURCE DEPENDENCIES. `.pyd`/`.so`/`.pyc` classify but source is only read
   for `.py`/`.pyi` (`_resolve_module_source_text`:1247), so binary deps are leaves — their
   transitive deps are never walked.
   STATUS: limited by design.

5. DYNAMIC / RUNTIME IMPORTS. The walk is source-AST only; `importlib.import_module(var)`,
   `__import__`, and conditionally-imported deps are not captured. `unknown` deps are
   recorded as leaves, not walked (`_walk_module_dependencies`:1545-1555).
   STATUS: limited by design (documented "not a full object graph or runtime reachability").

6. NO REUSABLE ANALYZER/RESULT OBJECT. `crystal_analysis` implied a `crystal_analyzer` +
   `crystal_analysis_result`; the analysis is embedded in the `SpellCrystal` constructor
   instead. Structural difference, not a functional loss - but if a standalone analyzer is
   wanted (e.g. for MR to re-analyze arbitrary versions without a live Spell), it does not
   exist yet.

---

## 2. MutationResearch persistence (Phase B / P5) — the big unbuilt piece

MR is stubbed on BOTH ends of the engine today:
- RECORD: `MutationResearchCrystal` carries config/activation only ("Phase A"); composition
  (streams/versions/heads/index associations) is "Phase B / persistence epic P5" and
  deliberately absent. EVIDENCE: persistence/crystals/mutation_research_crystal.py:13-24.
- RESTORE: `restore_engine._replay_mutation_research` only REPORTS "recorded, not restored,
  too new". EVIDENCE: persistence/restore_engine.py:747-767.

Remaining work:
1. Build MR in-memory composition objects: `ResearchStream` (branch: name + optional
   BranchType + head + index associations), `VersionRecord` (spell_id SHA = the version,
   parents, crystal ref, module-version SHA), head pointers, index associations.
2. Extend `MutationResearchCrystal` Phase A -> Phase B to carry that composition as a
   value-only twin payload (the profile already holds the singleton MR slot;
   PersistenceProfile._mutation_research_crystal). No new crystal object needed.
3. MR emits its composition twin through `crystallizer.emit(...)` at mutation acts.
4. Flesh out `_replay_mutation_research` to actually rebuild + hydrate the composition from
   the folded MR twin (today it reports).
5. MR/Nexus lifecycle-state REPLAY (currently "reported not replayed first cut" -
   restore_engine.py:567-571).
6. MR impact engine (the blast-radius "change compiler") - entirely unbuilt; the
   high-value analysis piece; reads crystal-custodied source (section 1) + melder's own
   dependency graph. Needs the export-surface gap (1.1) closed to be precise.

---

## 3. Asset / environment management (`asset_management`) — unbuilt requirement

The persistence-TRAFFIC subset is covered (PersistenceCrystal.to_cached_item/from_cached_item
JSON codec + CrystallizerCache + ExternalPersistenceManager). The GENERAL asset/environment
layer is genuinely unbuilt anywhere:
1. General asset store for arbitrary NON-source files (binaries, configs, resources, `.pyc`).
2. Environment/package assets: `uv.lock` capture + validation on restore; site-package
   presence/version checks; `uv`-first dependency recovery.
3. Restore ENV GATE: today a missing import at hydration becomes a reported shortfall
   (`restore_engine._hydrate_target`:1499-1511) - there is no hard prerequisite gate or
   recovery path as the philosophy's bootstrap_loader described.
DECISION NEEDED: is env/asset persistence ever in scope? If not, this stays closed and the
`asset_management` dir is pure dead scaffold.

---

## 4. Persistence engine open stubs / first-cut tolerances

1. `PersistenceProfile.compose_frame_subtree` / `compose_conduit_subtree` are
   `NotImplementedError` placeholders. EVIDENCE: persistence/persistence_profile.py:788-832.
   (Note: formations already do scoped capture via `capture_formation_slice`, so these may
   be redundant - confirm before building.)
2. Contract INDEX-SUBSCRIPTION replay is reported, not replayed.
   EVIDENCE: persistence/restore_engine.py:1451-1459.
3. Contract detail LABEL DRIFT: replayed details re-record as "received" regardless of the
   original initiated/received label - a documented first-cut tolerance.
   EVIDENCE: persistence/restore_engine.py:1391-1408.
4. Cluster LEADER election + explicit shared-entry replay are reported, not replayed.
   EVIDENCE: persistence/restore_engine.py:1375-1389.
5. Checkpoint-chain hardening is ONGOING (multiple 2026-07-07 fixes: checkpoint-number
   minting, staged-custody capture gap). Treat the chain-integrity lane as in-flight.

---

## 5. Cleanup: remove the 5 dead directories

`crystal_analysis/`, `crystal_loader/`, `asset_management/`, `crystal_management/`,
`crystallizer/mutation_research/` have ZERO references repo-wide and ZERO executable code
(empty or docstring-only). Their philosophy roles are carried by live code (SpellCrystal,
restore_engine, PersistenceProfile, MutationResearchCrystal) except the general asset/env
requirement (section 3), which is unmet whether or not the folder exists.

STATUS: removal attempted from the agent sandbox and BLOCKED (mount denies `rm`; touch is
allowed, rm returns "Operation not permitted"). USER ACTION REQUIRED - run on the host:

```
git rm -r src/melder/crystallizer/crystal_analysis \
          src/melder/crystallizer/crystal_loader \
          src/melder/crystallizer/asset_management \
          src/melder/crystallizer/crystal_management \
          src/melder/crystallizer/mutation_research
```

(Do NOT touch `src/melder/mutation_research` - that is the real MR runtime.)

---

## Priority read for MR build
Sections 2 (MR Phase B) then 1.1 (export surface, needed by the MR impact engine) are the
critical path. Section 3 (asset/env) is a scope decision. Section 4 is engine hardening,
mostly independent of MR.
