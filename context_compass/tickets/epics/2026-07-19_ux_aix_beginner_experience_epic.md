# Epic: UX/AIX Beginner experience exploration

## Metadata
- Epic ID: EPIC-2026-07-19-ux-aix-beginner
- Status: in_progress
- Owner: cowork
- Agent Name: helper_f
- Priority: p2
- Created: 2026-07-19T12:52:00Z
- Updated: 2026-07-19T12:52:00Z

## Objective
First-contact UX + the agent first-read: bind/conjure/meld, lifecycles, function and instance spells, named bindings, scan_bind, scopes, the error vocabulary, and the hardcopy self-documentation. Prove the root serves the first hour with zero deep-path imports.

## Ticket Contract
- ENTRY_GATE: owner directive 2026-07-19 ("explore all the ways a user might use the
  library beginner -> intermediate -> expert -> Master... so we can properly explore
  what we need in init"). Examples live in UX_and_AIX_experiences/01_beginner/.
- EXECUTION_BOUNDARY: UX_and_AIX_experiences/01_beginner/ examples + findings notes ONLY; init changes route to the init composition story.
- DEPENDENCIES: init composition story (the 66-name root is the surface under test);
  prior tiers' findings.
- EXIT_GATE: every example runs green on the owner's 3.14t; every discovered
  init-surface gap either landed on the init story or recorded as a rejected
  curation call with reasons; owner walkthrough of the tier.
- FAILURE_ESCALATION: DECISION_REQUEST on any gap whose fix would widen the public
  surface beyond the ConduitWard law.

## Noting Behavior
- MEASURE per authoring wave (examples written, surfaces exercised, gaps found).
- DECISION for every init-surface change the tier proposes.

## Notes
- DATETIME: 2026-07-19T13:46:00Z
  TYPE: MEASURE
  CLAIM: Owner caught two GUESSED contracts in the capstone; source probes settled
    both and the tier got a verification harness so guessing ends here. TRUTH 1:
    with-book is LEGAL but __exit__ ONLY releases the book lock (spellbook.py:679-692)
    - it is an atomic-bind-batch context, NOT auto-cleanup; example 10 rewritten as
    10_book_as_lock_context.py teaching the real semantics + explicit cleanup().
    TRUTH 2: bind(**kwargs) feeds _add_hooks_to_spell - a HOOK channel; env="production"
    was flatly wrong. The real configured-construction lanes: factories, prebuilt
    instances, and meld(spell_override=dict) ("constructor/factory argument overrides",
    conduit.py meld docstring). FIXES x5: 21 rewritten as 21_configured_construction.py
    (factory + spell_override), 18 bootstrap binds a prebuilt Settings(env), 37
    cheatsheet row corrected (**kwargs = hook lists) + demo de-kwarged, 40 capstone
    (prebuilt config, lock-batch framing, explicit cleanup), intermediate/02
    (with_kwargs now passes a NAMED bind param; ctor config moved to spell_override).
    HARNESS: UX_and_AIX_experiences/pytest_examples/ - test_beginner_examples.py
    (parametrized runner: every example's main() must go green + narrate) +
    test_contract_probes.py (8 sharp rows: kwargs-refusal, spell_override delivery,
    lock-only with, name-forms, unregistered meld, double-bind, disposal firing).
    Charter law added: examples assert only source-verified or probe-proven behavior.
    RUN: pytest UX_and_AIX_experiences/pytest_examples -v (3.14t).
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:679-692
  - UX_and_AIX_experiences/pytest_examples/test_contract_probes.py:1-120
  - UX_and_AIX_experiences/01_beginner/21_configured_construction.py:1-45
  IMPACT: The tier's claims are now falsifiable in one command; the two wrong
    lessons died before any learner met them.
  NEXT: OWNER RUNS: pytest UX_and_AIX_experiences/pytest_examples -v; probe output
    hardens 07/27/30/35 prints into asserts next wave.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-19T13:36:00Z
  TYPE: DECISION
  CLAIM: Owner ruling: strings are the PREFERRED spelling in beginner examples.
    Flipped 32 files to existence="unique"/"many"/"unique_per_conduit" and
    permissions="read"/"create"/"block"; six vocabulary-teaching files deliberately
    keep the enum forms (07 reframed as strings-preferred/enums-typed, 19 map, 37
    cheatsheet, 39 inventory, 12 first-read, 06 errors). Grep-verified zero enum
    CALLS outside the keep-set. StrEnum question answered with evidence, not
    vibes: the LRU makes string normalization a cached dict hit and melds never
    re-normalize (existence compiles into the creation strategy at bind), so
    StrEnum buys nothing measurable at bind time - its real case is ergonomics
    (string equality, native serialization; persistence already stores .name so
    values are safe) and it stays a PARKED patch-gated story on owner demand.
    FOUND AND FIXED while grounding the answer: EnumHelpers.convert_enum_and_check
    was @lru_cache(maxsize=8) against a >8-key closed vocabulary (6 existences + 3
    permissions as string AND member-passthrough keys) - eviction churn on the
    exact path the cache serves. Bumped to 64 with an explanatory comment
    (general_helpers.py). pytest Not run - rides owner 3.14t.
  EVIDENCE:
  - src/melder/utilities/helpers/general_helpers.py:20-26
  - UX_and_AIX_experiences/01_beginner/07_strings_as_vocabulary.py:1-15
  - src/melder/crystallizer/crystals/spell_crystal.py:240-240
  IMPACT: Beginner reads like config; the typed form stays taught; the enum
    normalization cache now actually caches.
  NEXT: Owner 3.14t (suite + 40 beginner scripts); StrEnum story on demand.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-19T13:28:00Z
  TYPE: DECISION
  CLAIM: Owner pedagogy ruling applied - beginner teaches the SMALL-AGENT basics
    (design principle now in the charter: a 4B model with a 64k window should become
    USEFUL: shared/fresh/scoped, frames as dicts, typed melds, Protocols, one
    bootstrap function; fun and simple beats complete). MIGRATIONS: lineage ->
    intermediate 05; spellspace declaration RETIRED (intermediate 04 already lives
    it); cluster -> expert 01 (its live demo needs dynamic linking anyway). Beginner
    existence set is now unique/many/unique_per_conduit ONLY (owner hedged on
    per_conduit; kept - scoped is the third leg of useful). Freed slots filled with
    the exact basics the owner named: 16 typed melding (py.typed pays off in the
    editor), 17 Protocols as shapes (static duck typing meets DI, two swappable
    spells), 18 the bootstrap composition-root pattern (build_world() -> (book,
    conduit)). 19 lifecycle map rewritten to the beginner three + honest later-tiers
    footnote (enumerates md.Existence so the count never rots); 37 cheatsheet line
    follows. 29's prose de-clustered. Tier grep clean; compile green x46 across three
    tiers; beginner holds at 40.
  EVIDENCE:
  - UX_and_AIX_experiences/01_beginner/18_bootstrap_pattern.py:1-40
  - UX_and_AIX_experiences/01_beginner/17_protocols_as_shapes.py:1-50
  - UX_and_AIX_experiences/02_intermediate/05_existence_unique_per_conduit_lineage.py:1-10
  - UX_and_AIX_experiences/03_expert/01_existence_unique_per_conduit_cluster.py:1-10
  IMPACT: The beginner tier is now a small-agent curriculum: three lifecycles, all
    address forms, dict-style classification, typing idioms, and one bootstrap habit.
  NEXT: Owner 3.14t pass; then tier 02 authoring (now seeded with 5: scanning,
    full chain, hooks, spellspaces, lineage).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-19T13:23:00Z
  TYPE: MEASURE
  CLAIM: Owner expansion + pedagogy restructure landed. MOVES to intermediate (tier
    02 now 4 examples): scan_bind decorator + module scanning, SpellBinder full chain,
    registration hooks, spellspace live demo (owner: spellspaces are intermediate;
    beginner keeps unique_per_spell_space as DECLARATION-ONLY vocabulary, mirroring
    the cluster pattern). BEGINNER now 40 examples in five arcs: first contact
    (01-04), scopes/errors/vocab/disposal/frames/context/binder-basics/agent-read
    (05-12), the EXISTENCE arc - each of the six lifecycles studied closely + the
    one-page lifecycle map (13-19), the WAYS-TO-BIND arc - lambdas, ctor kwargs,
    spell ids + find_spell_by_id, book introspection via spells mapping, same-class-
    many-names (20-24), the DICT-STYLE CLASSIFICATION arc the owner asked for -
    frames as top keys + names as sub-keys (25), meld by binding_name alone (26),
    meld by spell_name (27, printed contract), permissions read/block (28-29),
    double-bind outcome (30, printed contract), required-vocabulary fail-fast (31),
    factories (32), prebuilt registries (33), scope contrast in one tree (34),
    multi-verb disposal (35), one-book-many-conduits (36), the full bind-kwargs
    cheatsheet (37), meld-a-frame-as-dict helper (38), the agent inventory pattern
    classifying md.__all__ (39), and the capstone app (40). Tier law grep-verified:
    zero conjure(dynamic/scan/spellspace USAGE (remaining 'dynamic' hits are prose
    pointers to later tiers); zero banned patterns (one type:ignore caught in my own
    draft of 31 and removed - the law applies to examples too). compile green x44
    across both tiers; md-only imports throughout. INIT FINDINGS: still zero gaps -
    40 beginner workflows complete from md.* alone.
  EVIDENCE:
  - UX_and_AIX_experiences/01_beginner/25_frames_as_dict_classification.py:1-55
  - UX_and_AIX_experiences/01_beginner/19_lifecycle_map.py:1-30
  - UX_and_AIX_experiences/01_beginner/37_bind_vocabulary_cheatsheet.py:1-60
  - UX_and_AIX_experiences/02_intermediate/04_spellspace_scoped_resolution.py:1-40
  IMPACT: The beginner tier is now a complete course: every lifecycle, every bind
    form, every address form, the dict-style classification mental model, and both
    printed-contract examples that the first 3.14t run will turn into documentation.
  NEXT: Owner 3.14t pass over 01_beginner/ (40 scripts); contracts documented by run:
    07 unregistered-meld, 27 spell_name form, 30 double-bind, 35 disposal order,
    18/17/29 declaration-only acceptances. Then tier 02 authoring continues.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-19T13:14:00Z
  TYPE: MEASURE
  CLAIM: Owner tier-law correction applied + registration wave landed. (1) TIER LAW:
    beginner = STATIC conjure only, no dynamic, no Nexus, no MutationResearch - all 7
    offending conjure(dynamic=True, name=...) calls rewritten to book.conjure();
    tier is grep-verified dynamic-free. (2) claude.md renamed AGENTS.md per owner.
    (3) Registration wave: +7 examples (09-15), SpellBinder fluent API source-verified
    first (spellbinder.py:246-692: bind/with_existence/as_unique/as_many/
    as_unique_per_conduit(+cluster/lineage/spell_space)/with_permissions/
    under_spellframe/named/with_kwargs/with_pre_hook(s)/with_activation_hook(s)/
    with_post_hook(s)/finalize->str, ctor defaults existence=unique permissions=create).
    09 fluent basics + binder reuse, 10 the full chain incl. with_kwargs ctor
    injection + per-conduit frame policy, 11 hook trio (printed order = the runtime
    documentation), 12 strings-as-vocabulary (existence/permissions accept names),
    13 disposal_method_names teardown contract (staged prints: conduit vs book
    cleanup), 14 spellframe grouping ((frame, name) is the full address), 15 context-
    managed Spellbook with post-exit guard honesty. 15 examples total; compile green
    x15; md-only imports; 120-col clean. INIT FINDINGS: still zero gaps - the full
    registration vocabulary reaches beginner UX from md.* alone.
  EVIDENCE:
  - UX_and_AIX_experiences/01_beginner/10_spellbinder_full_chain.py:1-60
  - UX_and_AIX_experiences/01_beginner/13_disposal_contract.py:1-45
  - src/melder/aether/spellbook/spellbinder.py:246-692
  IMPACT: Registration UX ("how to register shit") is now covered end to end at the
    beginner tier: direct bind, fluent binder, decorator scan, strings, kwargs,
    hooks, disposal, frames, context management.
  NEXT: Owner 3.14t pass over the 15 scripts; three examples deliberately PRINT
    contracts the run will document (07 unregistered-meld, 11 hook firing points,
    13 disposal stage). Then tier 02.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-19T12:52:00Z
  TYPE: MEASURE
  CLAIM: Tier authored - 8 examples, every verb source-verified before writing
    (conjure(policy/dynamic/name) spellbook.py:5658, meld(spell/spell_name/
    binding_name/spellframe/spell_override) conduit.py:3594, scan(module)->list[str]
    :4877, Existence members existence.py:24-72, Permissions read/create/block
    :34-36). Coverage: 01 hello-meld, 02 unique-vs-many, 03 function+instance spells,
    04 binding_name disambiguation, 05 @scan_bind + module scan, 06 lesser-conduit
    scopes (unique_per_conduit), 07 catchable error family from root, 08 the AIX
    first-read (workflow-map docstring, version, four hardcopy docs, __all__).
    INIT-SURFACE FINDINGS: ZERO gaps at this tier - every beginner workflow completes
    from md.* alone; the 66-name root fully serves first-contact UX and the agent
    first-read. One honest unknown for the 3.14t run: whether melding an unregistered
    spell raises SpellbookValidationError vs returns None (07 handles both and PRINTS
    which - the run itself documents the contract).
  EVIDENCE:
  - UX_and_AIX_experiences/01_beginner/01_hello_meld.py:1-40
  - UX_and_AIX_experiences/01_beginner/08_agent_first_read.py:1-40
  - src/melder/aether/spellbook/spellbook.py:5658-5664
  - src/melder/aether/conduit/conduit.py:3594-3602
  IMPACT: Beginner tier is authored evidence that the loaded init works at first
    contact; the tier's zero-gap result is itself a finding for the init story.
  NEXT: Owner: python UX_and_AIX_experiences/01_beginner/0N_*.py on 3.14t (or one
    loop); then iterate tier 02 (intermediate).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8


## Context / Handoff Summary
Method: every example imports melder as md ONLY - a deep-path import in an example
IS the finding. Examples are runnable scripts with honest asserts; they ride the
owner's 3.14t runs (device VM cannot import the runtime).
