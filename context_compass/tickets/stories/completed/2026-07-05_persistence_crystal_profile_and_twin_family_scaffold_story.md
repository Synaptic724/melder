# Story: PersistenceCrystal + PersistenceProfile + twin-family scaffold (S1, placeholders)
- Completed: 2026-07-06T20:45:00Z
- Summary: Grew from S1 scaffold into the FULL persistence-record build trail: twin family + profiles/checkpoints + all emission seams + removal ladder + relationships (index/contract/cluster) + local cache + 136-test program + 6 runtime bugs found/fixed. Notes = canonical evidence, newest last. Owner-directed closure 2026-07-06; restore engine continues in the bootstrap epic.


## Metadata
- Story ID: STORY-2026-07-05-persistence-crystal-profile-and-twin-family-scaffold
- Epic: EPIC-2026-07-03-wire-crystallizer-into-melder
- Parent Epic: EPIC-2026-07-02-agent-object-persistence-loop
- Status: review
- Owner: cowork
- Agent Name: melder_0
- Priority: p1
- Created: 2026-07-05T12:18:27Z
- Updated: 2026-07-05T12:25:04Z

## Objective
Lay the owner-modeled persistence structure inside crystallizer as compile-clean placeholders:
`Crystallizer._persistence_crystal -> PersistenceCrystal -> PersistenceProfile ("default" always) ->
twin family` with the owner hierarchy
`AetherCrystal -> MutationResearchCrystal & NexusCrystal & AethericFrameCrystal -> SpellbookCrystal
-> SpellBindingCrystal(+SpellCrystal ref) & ConduitCrystal`.
Flat maps per level inside the profile (the aetheric_frame storage pattern); tree presented at the
API; emissions always target "default".

## Ticket Contract
- ENTRY_GATE: user push (2026-07-05); epic ownership transferred to melder_0 (crystal_0 backup);
  design converged in-session (profiles model, dynamic-lane hard gate, hydration boundary,
  L3 intra-level order: binds before conjure, links replay last).
- EXECUTION_BOUNDARY: NEW files only under `src/melder/crystallizer/persistence/**`.
  No edits to crystallizer.py / spellbook.py / any existing source this story.
  Placeholders: full class skeletons (slots, init, cleanup, locks, contracts documented);
  trivial container verbs implemented; substantive behavior raises NotImplementedError.
- DEPENDENCIES: Cleanable base (utilities/general_base); SpellCrystal stays untouched at
  crystallizer root as the module-manifest leaf.
- EXIT_GATE: package py_compile-clean (sandbox 3.10); wc/tail write-integrity verified per file
  (mount fault active); structure matches the owner model verbatim; 3.14t: Not run (user runs).
- FAILURE_ESCALATION: CONFLICT if concurrent edits touch crystallizer/**; write-fault repairs
  logged per file.

## Scope Boundaries
- In scope: persistence_crystal.py, persistence_profile.py, crystals/{aether, aetheric_frame,
  nexus, mutation_research, spellbook, conduit, spell_binding}_crystal.py, empty __init__ files.
- Out of scope: crystallizer.py wiring (next story: needs full fresh read first), melder emit
  call-sites, freeze-at-bind, catch-up walk, adapter round-trip, restore engine, tests-at-density
  (land with behavior, not placeholders).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: user directed the build ("go ahead and build the placeholders").

## Steps / Checklist
- [x] Package dirs + empty __init__.py files.
- [x] Twin family: 6 twins + SpellBindingCrystal (pure-data carriers, parent refs, value payloads).
- [x] PersistenceProfile: flat level-maps + RLock + replace-on-emit record() dispatch + subtree
      stubs (NotImplementedError).
- [x] PersistenceCrystal: profiles map, "default" guaranteed, get/create/clear/list implemented,
      save_profile/hydrate_profile stubs.
- [x] py_compile + wc verify each file.

## Validation
- Not run. (Sandbox py_compile only; user runs 3.14t.)

## Applicable Anti-Patterns
- [ ] No edits to existing source files in this story.
- [ ] No implementation of substantive behavior disguised as placeholder.
- [ ] No closure without write-integrity verification (mount fault active).

## Noting Behavior
- Story notes: cross-file structure decisions, write-fault incidents, deviations from the model.

## Notes
- DATETIME: 2026-07-05T12:25:04Z
  TYPE: FACT
  CLAIM: S1 LANDED. 11 files under src/melder/crystallizer/persistence/** (6 twins +
    SpellBindingCrystal + PersistenceProfile + PersistenceCrystal + 2 empty __init__), 1,824
    lines total, compileall-clean on the 3.10 sandbox, pure CRLF, 0 NULs, written via bash +
    py_compile per file (zero write-fault incidents this pass). Runtime import is NOT
    executable on the sandbox: melder/__init__.py imports Nexus and
    nexus/frame_descriptor/frame_descriptor.py:153 evaluates Optional[AethericFrame] in a
    class body (3.14 deferred-annotations baseline) - a pre-existing repo property making ALL
    melder.* imports 3.14t-only; twin-family smoke test blocked by the same package-root
    import. Behavior verification lands with the next story's tests on user-run 3.14t.
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_crystal.py:1-317
  - src/melder/crystallizer/persistence/persistence_profile.py:1-423
  - src/melder/crystallizer/persistence/crystals/spell_binding_crystal.py:1-266
  IMPACT: The owner's persistence model exists as compile-verified structure; the emit sink
    (Crystallizer.emit -> PersistenceCrystal.record -> default profile) has a real receiving
    end for the wiring story.
  NEXT: crystallizer.py wiring story - fresh full read of crystallizer.py FIRST, then
    _persistence_crystal slot + __init__ + cleanup + emit() delegation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-05T12:25:04Z
  TYPE: RISK
  CLAIM: Two review flags for owner style call: (1) PersistenceProfile._replace_singleton
    uses getattr/setattr with a parameterized slot name - legal under the banned-patterns
    "truly dynamic name" clause but replaceable with three explicit branches if preferred;
    (2) _replace_mapped types its map parameter as Dict[str, object] (placeholder-grade
    typing; tightens to a Union or per-level overloads when behavior lands).
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_profile.py:305-345
  IMPACT: Both are contained to two private helpers; neither changes public contracts.
  NEXT: Owner accepts or directs the explicit-branch rewrite in the wiring story.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-07-05T12:55:00Z
  TYPE: FACT
  CLAIM: OWNER REVISION PASS LANDED (3 directives): (1) ACTIVE-PROFILE MODEL - PersistenceCrystal
    now mirrors the Aether/frame pattern: guaranteed "default" + named profiles + ONE active
    selection; record() routes to the ACTIVE profile; create_profile(nam