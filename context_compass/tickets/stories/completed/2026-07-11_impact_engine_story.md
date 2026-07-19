# Story: S3 impact engine - blast radius over retained manifests

## Metadata
- Story ID: STORY-2026-07-11-impact-engine
- Parent: EPIC-2026-07-11-crystallizer-v3-horizon-iteration (tranche S3)
- Status: closed
- Owner: cowork
- Agent Name: melder_0
- Priority: p1
- Created: 2026-07-11T23:30:00Z
- Updated: 2026-07-11T23:30:00Z

## Problem / Opportunity
The record now knows everything an impact question needs - every custody
crystal carries its module world (module_targets, per-module direct
dependency edges, export surfaces, bind-time fingerprints, and since S2
optionally the retained text) - but nothing ANSWERS the questions: "which
spells break if module X changes?", "what has drifted on disk since the
world sealed, and what does that drift touch?". S3 builds the read-only
view that turns the manifests into blast-radius answers.

## Ticket Contract
- ENTRY_GATE: epic tranche order (owner 2026-07-11; S1+S2 code-complete).
- EXECUTION_BOUNDARY: crystal_analysis/ (the engine), persistence
  profile/system (ONE additive read seam), crystallizer.py (facade
  verbs), tests, patch docs. Read-only over the record everywhere.
- DEPENDENCIES: SpellCrystal manifests (shipped); S2
  physical_module_fingerprints + user_module_sources (shipped).
- EXIT_GATE: owner-run green; acceptance walk; then epic-wide promotion.
- FAILURE_ESCALATION: anything needing record mutation -> CONFLICT + stop
  (this story is a VIEW; the record never changes shape for it).

## Pinned Design (from source, 2026-07-11)
1. READ SEAM (additive, dict-only): PersistenceProfile.
   describe_spell_crystals() -> {spell_id: describe() payload +
   "custody_state": "active"|"inactive"} across BOTH custody maps;
   PersistenceSystem passthrough (active profile). No twin objects
   escape (record law).
2. ENGINE: crystal_analysis/impact_engine.py - ImpactEngine (Cleanable),
   constructed over the detached custody map (pure data in, pure data
   out). Indexes built once at construction: module -> spells that carry
   it (reverse of module_targets) and module -> modules that import it
   (reverse of the per-crystal module_to_direct_dependencies union).
   Verbs:
   - spells_touching_module(module) -> direct dependents;
   - blast_radius_of_module(module) -> transitive closure over reverse
     import edges: {modules, spells, spellbooks, custody_states};
   - blast_radius_of_spell(spell_sha) -> the radius of its root module
     (a spell change IS its module world changing);
   - describe_source_drift() -> per recorded fingerprint: live file
     re-hashed (read_text/utf-8, the CRLF-safe custody read) ->
     unchanged | drifted | absent, and for every drifted/absent module
     its blast radius (the "what will my uncommitted edits break" view);
   - describe() -> the full detached report.
3. FACADE (activation-gated, byte-compatible additive):
   Crystallizer.analyze_impact(module_name=None, spell_id=None) - one
   verb, view keyed by which argument arrived (both None = full
   drift+radius report).
4. Tests: unit over synthetic custody payloads (reverse-index closure,
   inactive flagging, unknown-module honesty) + drift with tmp files
   (drifted/absent/unchanged) + facade smoke.

## Acceptance Criteria
- "Which spells does module X reach?" answers transitively with
  spellbook edges and custody states, from the record alone.
- Drift report names every module whose live file differs from (or no
  longer backs) its sealed fingerprint, with its radius.
- Zero record mutations; facades additive; unknown inputs answer
  honestly (empty radius + "unknown_module"/"unknown_spell" marker).

## Applicable Anti-Patterns
- [ ] Patch docs before code.
- [ ] Read-only: no record reshaping, no twin escape.
- [ ] "Not run." until the owner runs.

## Notes
- DATETIME: 2026-07-11T23:30:00Z
  TYPE: FACT
  CLAIM: Investigation complete. No enumerate-all-custody read exists
    (only get_spell_crystal(spell_id) - persistence_profile.py:703); the
    manifests carry everything else needed (module_targets,
    module_to_direct_dependencies, physical_module_fingerprints,
    export_surfaces, module_load_order - crystal_analysis_result.py
    describe surface). Engine home = crystal_analysis/ (the shared
    analysis service package, per the V3 decomposition).
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_profile.py:703-712
  - src/melder/crystallizer/crystal_analysis/crystal_analysis_result.py:56-72
  IMPACT: S3 is a pure-view build; risk is index correctness, covered by
    closure unit tests.
  NEXT: patch doc -> read seam -> engine -> facade -> tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T00:20:00Z
  TYPE: FACT
  CLAIM: IMPLEMENTED per the pinned design (patch
    crystallizer_s3_impact_engine_2026_07_11 authored FIRST). (1) Read
    seam: PersistenceProfile.describe_spell_crystals (both custody maps,
    additive custody_state key, detached payloads only) +
    PersistenceSystem active-profile passthrough. (2)
    crystal_analysis/impact_engine.py - ImpactEngine: construction builds
    module->carrying-spells + module->importers reverse indexes plus
    fingerprint/path maps (first-writer-wins; SHAs content-derived);
    verbs spells_touching_module, blast_radius_of_module (transitive
    closure, honest unknown_module), blast_radius_of_spell (root-module
    radius + identity, honest unknown_spell), describe_source_drift
    (CRLF-safe read_text re-hash -> unchanged|drifted|absent|unreadable
    + radius per non-unchanged), describe. (3)
    Crystallizer.analyze_impact(module_name|spell_id|neither) -
    activation-gated, one question per call (both = ValueError), engine
    built + cleaned per call. (4) 4-test unit suite (transitive closure +
    narrow radius, honest unknowns, spell=root-module equivalence, drift
    classification over real tmp files with radii).
  EVIDENCE:
  - src/melder/crystallizer/crystal_analysis/impact_engine.py:1-335
  - src/melder/crystallizer/persistence/persistence_profile.py:744-782
  - src/melder/crystallizer/crystallizer.py:558-620
  - tests/unit/melder/crystallizer/crystal_analysis/test_impact_engine.py:1-173
  IMPACT: The epic's third question is answerable from the record alone;
    S1+S2+S3 all code-complete - the crystallizer_v3_horizon epic's
    build surface is DONE pending the owner sweep.
  TESTS: Not run (sandbox; rot on grown files - disk verified via
    file-tool; new files parsed clean).
  NEXT: owner 3.14t sweep (covers MR triage fixes + disabled-lane test +
    S3); on green: closure walks (MR epic, S2 story, S3 story, epic) +
    the batched patch promotion (now FIVE dirs) + graph regen.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T04:40:00Z
  TYPE: FACT
  CLAIM: CLOSED - owner runs GREEN. ACCEPTANCE WALK: (1) "which spells
    does module X reach?" answers transitively from the record alone
    with spellbook edges + custody states (closure unit tests incl. the
    narrow-radius counter-case); (2) the drift report names every
    module whose live file differs from/no longer backs its sealed
    fingerprint, each with its radius (tmp-file matrix green); (3) zero
    record mutations (read seam is describe-only), facades additive
    (analyze_impact one-question contract), unknown inputs answer
    honestly (unknown_module/unknown_spell markers, unit-proven).
    Post-build conformance: spell_id vocabulary sweep applied same day
    (mutation_0's flag, zero callers churned).
  EVIDENCE:
  - tests/unit/melder/crystallizer/crystal_analysis/test_impact_engine.py:1-173
  IMPACT: The manifests answer the questions they were built for; the
    graft lane's blast-radius precondition now exists.
  NEXT: none (story closed); promotion rides the batched pass.
  REREAD: OPTIONAL
  SCORE_0_TO_10: 9

## Context / Handoff Summary
S3 tranche: read-only ImpactEngine over the custody manifests (reverse
dependency indexes + transitive blast radius + fingerprint drift view),
one additive profile read seam, one activation-gated facade verb.
