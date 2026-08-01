# Epic: UX/AIX Beginner experience exploration

## Metadata
- Epic ID: EPIC-2026-07-19-ux-aix-beginner
- Status: done_pending_owner_walkthrough
- Owner: cowork
- Agent Name: examples_0
- Priority: p2
- Created: 2026-07-19T12:52:00Z
- Updated: 2026-08-01T10:41:33Z

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
- DATETIME: 2026-07-19T16:24:00Z
  TYPE: DECISION
  CLAIM: Owner cleanup ruling ("this is for noobs and garbo agents"): KILLED
    21_optional_melds (clever-dev try/except pattern + a bind(spell=object) anchor
    hack - novices melding speculatively against their own worlds is backwards) and
    27_meld_by_spell_name (probe-flavored, redundant with 26's address law).
    REWRITTEN 30_double_bind_outcome from exploratory printed-contract voice to a
    declarative lesson (refusal + the subclass fix, cross-linked to 24). BACKFILLED
    with the two simplest lessons the tier lacked: 21_the_basic_rhythm (bind
    everything -> conjure once -> meld everywhere - the program shape itself) and
    27_pass_the_conduit_around (main owns the conduit, functions receive it - no
    re-conjuring, no globals). Tier voice rule reaffirmed: beginner examples are
    DECLARATIVE lessons, never exploratory probes; probe voice lives in
    pytest_examples only. Beginner holds 40, compile green.
  EVIDENCE:
  - UX_and_AIX_experiences/01_beginner/21_the_basic_rhythm.py:1-35
  - UX_and_AIX_experiences/01_beginner/27_pass_the_conduit_around.py:1-30
  IMPACT: Hour one is now uniformly plain: three verbs, one order, real objects,
    simple structure habits.
  NEXT: Owner harness rerun covers the 4 changed files.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-19T15:44:00Z
  TYPE: DECISION
  CLAIM: (1) DECISION A RULED (owner convinced after the "why would you name
    something the same twice" chat): the DuplicateSpellNameStrategy REFUSAL IS
    CORRECT DESIGN - spell names are world-unique; the only fix is the LYING ERROR
    MESSAGE (currently promises binding_name/spellframe disambiguation that does
    not work) -> reword to "rename or subclass; spell names are world-unique by
    design", and flip the two divergence probes into intended-behavior pins. Small
    follow-up story when convenient. (2) TIER RE-REVIEW (owner-directed final
    pass): moved to intermediate - 10 lock-batching (concurrency), 21
    spell_override construction (the MUTATION lane's per-call door does not belong
    in hour one), 29 permissions block (points at sharing flows that live in tier
    02). Backfilled with true-beginner lessons: 10_explicit_cleanup (teardown
    verbs + guards), 21_optional_melds (KeyError contract as a feature -
    try/except optional dependencies), 29_many_state_isolation (fresh instances
    share nothing). Beginner holds at 40; intermediate now 9 seeded. Moved files
    re-tiered in headers; compile green x3 new.
  EVIDENCE:
  - UX_and_AIX_experiences/01_beginner/21_optional_melds.py:1-30
  - UX_and_AIX_experiences/02_intermediate/08_spell_override_construction.py:1-10
  IMPACT: Hour one now contains zero advanced lanes (no override door, no lock
    semantics, no sharing vocabulary); every open design question of the day is
    ruled.
  NEXT: Owner rerun of the beginner harness (3 new + address-law regression);
    name-strategy message fix as a small story; tier-02 authoring wave.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-19T15:28:00Z
  TYPE: DECISION
  CLAIM: Owner ruling on the core tension: SHA256 content-fingerprint uniqueness is
    ABSOLUTE AND INTENTIONAL - the same fingerprint never registers twice; users
    wanting near-twin classes differentiate them (subclass, added attribute -
    anything that shifts the fingerprint). Curriculum already aligned (24
    subclass-per-role = the minimal differentiation, and a subclass's own name
    sidesteps the name strategy entirely). DECISION A NARROWED accordingly: the SHA
    law is settled; the only open question is DuplicateSpellNameStrategy refusing
    DIFFERENT-SHA name-twins despite its own error text promising binding_name/
    spellframe disambiguation (probe-proven). Fix scope when ruled: strategy honors
    the disambiguators for different-SHA spells; same-SHA refusal untouched forever.
  EVIDENCE:
  - UX_and_AIX_experiences/pytest_examples/test_contract_probes.py:120-160
  IMPACT: Decision A is now a small, well-bounded strategy fix instead of an
    identity-model question.
  NEXT: Owner rules the narrowed decision A whenever ready.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-19T15:14:00Z
  TYPE: DECISION
  CLAIM: Owner correction: ENVIRONMENT framing removed from the curriculum (18
    rewritten, 40 de-environmented). Melder has no environment-switching pattern -
    an aetheric_frame can carry an environment-like name, but the same objects
    cannot register twice (content-fingerprint law), so per-env rebinding does not
    exist; the user's MODULE decides what to build. Bootstraps exist via
    crystallizer only; owner deliberately has no user-registered cached bootstraps
    ("a user would just make a module and decide what path to take"). DECIDED
    (owner + helper aligned, 2026-07-19): NO env/config holder in
    aetheric_utility_system - a user-bound config object (unique + read, framed)
    IS the process-wide configuration item; the library eats its own dog food.
    Ambient env holders = service-locator smell (untyped lookups, hidden
    coupling, invisible to the dependency graph); os.environ + the composition
    root covers literal env vars (beginner 18 teaches the pattern). Revisit only
    if INTERNAL subsystems ever need shared runtime settings (internal plumbing,
    not user API).
  EVIDENCE:
  - UX_and_AIX_experiences/01_beginner/18_bootstrap_pattern.py:1-15
  IMPACT: Curriculum stops implying a pattern the runtime forbids.
  NEXT: If the utility-system env-vars idea firms up, it gets its own strategy
    ticket.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-19T14:12:00Z
  TYPE: MEASURE
  CLAIM: Run 4 (owner): 51/51 GREEN - the beginner tier is VALIDATED end to end. 40
    examples + 11 contract probes, every lesson run-proven, four runtime laws
    discovered and pinned along the way (callable-unique, the address law, single-
    conjure, silent kwargs swallow) plus one divergence flag (name strategy vs
    owner's SHA design intent, decision A open). Owner approved the kwargs
    pass-through -> STORY-2026-07-19-bind-kwargs-transplant opened with the full
    seam map; teaching reserved for tier 02 per owner ("its an intermediate job").
  EVIDENCE:
  - tickets/stories/2026-07-19_bind_kwargs_transplant_story.md:1-1
  IMPACT: Tier 01 done and defended by its own harness; the exploration lane has
    already paid two runtime improvements back into the package.
  NEXT: Kwargs implementation wave (fresh context), then tier 02 authoring; owner
    rules decision A when ready.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-19T14:04:00Z
  TYPE: MEASURE
  CLAIM: Run 3: 47/51 green; the two remaining reds COMPLETED the address model -
    spell_name resolution derives its key from the NAME, so it misses framed binds
    (('billingservice','__default__') vs the bind's ('services','billing')) and a
    named bind answers only when the meld carries the same binding_name
    (('probe','the-probe') vs ('probe','__default__')). THE ADDRESS LAW is now fully
    mapped and taught: one spell = one (frame_key, binding_key) address; frame_key =
    spellframe else normalized name; binding_key = binding_name else default; meld
    forms are key constructors. 26 rewritten around the law (default-address spell
    answers object+name forms; framed spell answers only at (frame,name); both misses
    demonstrated); probe extended (spell_name+binding_name composes the key; bare
    spell_name KeyErrors on an empty default slot); charter law updated. Run 3 also
    CONFIRMED: silent-swallow pin, spell_name form, KeyError contract, double-bind
    RuntimeError, disposal at conduit.cleanup, and both divergence pins all green.
    Expected next run: 51/51.
  EVIDENCE:
  - UX_and_AIX_experiences/01_beginner/26_meld_address_forms.py:1-60
  - UX_and_AIX_experiences/pytest_examples/test_contract_probes.py:60-75
  IMPACT: The beginner tier now teaches the complete, run-proven resolution model.
  NEXT: Owner rerun (expected fully green) -> beginner tier VALIDATED; then tier 02
    authoring + the two runtime stories (kwargs pass-through per refined ruling;
    decision A still open).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-19T14:14:00Z
  TYPE: DECISION
  CLAIM: Owner REFINED the kwargs ruling: bind leftovers are the CONSTRUCTION PAYLOAD
    FOR THE USER'S SPELL OBJECT - "literally only for the spell object, not the
    binding object." Not binding metadata, not identity, no strategy interlock. The
    Spell carries the payload opaquely; creation passes it into the object
    (UserClass(**payload) / callable(**payload); instance spells reject non-empty
    payloads); rejection authority is the spell object's OWN signature. Patch doc
    rewritten to match; my earlier binding-identity framing retracted. Decision A
    (name strategy) stands alone and remains open.
  EVIDENCE:
  - context_compass/system_docs/patches/active/bind_kwargs_spell_transplant_2026_07_19/architecture_patch.md:1-45
  IMPACT: Simpler design: bind kwargs = deferred constructor args, nothing more.
  NEXT: Owner rules decision A; implementation story lands both (or transplant alone).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-19T14:01:00Z
  TYPE: DECISION
  CLAIM: Owner RULED decision B (upgraded): bind(**kwargs) leftovers TRANSPLANT ONTO
    THE SPELL - the Spell consumes what its profile recognizes and raises on
    leftovers itself ("fail via the spell object"), popping hook transfers first.
    Architecture patch authored: system_docs/patches/active/
    bind_kwargs_spell_transplant_2026_07_19/ (semantics, precedence law
    spell_override > bind kwargs > signature defaults, per-profile consumption,
    persistence + identity rules, blast radius). Implementation is its own story -
    NOT landed this wave. Decision A (DuplicateSpellNameStrategy honoring SHA +
    binding-address disambiguation) remains OPEN and interlocks via the identity
    rule; recommend ruling it before the transplant story lands.
  EVIDENCE:
  - context_compass/system_docs/patches/active/bind_kwargs_spell_transplant_2026_07_19/architecture_patch.md:1-60
  IMPACT: The silent-swallow footgun dies by design; bind gains the configured-
    construction lane users (and agents) instinctively reach for.
  NEXT: Owner rules decision A; then I open the implementation story and land both.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-19T13:56:00Z
  TYPE: MEASURE
  CLAIM: Run 2 processed - 30/40 examples green; every remaining red decoded into
    verified contracts and fixed. PROVEN: (1) meld address forms are spell object /
    spell_name / (spellframe, binding_name); binding_name alone -> ValueError - six
    examples corrected (17/18/20/21/32 gained frames; 26 rewritten as
    26_meld_address_forms teaching all three + the refusal). (2) Unregistered meld ->
    stable KeyError (06 corrected). (3) One book = ONE conduit (RuntimeError on
    second conjure) - 36 rewritten as 36_one_book_one_conduit. (4) bind swallows
    unknown kwargs SILENTLY (env="production" bound fine, ctor untouched) - probe
    rewritten to pin acceptance; 37 cheatsheet warns. (5) THE BIG ONE - DIVERGENCE:
    owner intent (twice stated: SHA256 content matching, potato-vs-potato passes
    with binding names) vs runtime: DuplicateSpellNameStrategy refuses ANY name
    collision - different SHAs with binding names REFUSED, same class across frames
    REFUSED - the strategy ignores the binding_name/spellframe disambiguation its
    own error message recommends. Two probes pin current behavior with divergence
    docstrings; 24 rewritten to subclass-per-role, 33 to collection-as-spell (the
    patterns that work TODAY). AGENTS.md discovered-laws section rewritten to run-2
    truth. Probe suite 11 rows, all now asserting current behavior.
  EVIDENCE:
  - UX_and_AIX_experiences/pytest_examples/test_contract_probes.py:25-45
  - UX_and_AIX_experiences/01_beginner/26_meld_address_forms.py:1-45
  - UX_and_AIX_experiences/01_beginner/36_one_book_one_conduit.py:1-35
  IMPACT: The curriculum now teaches only run-proven truth, and the harness
    surfaced one runtime bug candidate + one fail-fast design question.
  NEXT: Owner rerun expected fully green. DECISION_REQUEST below.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-19T13:56:30Z
  TYPE: DECISION_REQUEST
  CLAIM: Two runtime rulings needed from the owner. (A) DuplicateSpellNameStrategy:
    align implementation with stated intent - allow same-name spells when content
    SHAs differ AND (frame, binding_name) resolution paths are unique (the
    disambiguation its error text already promises), refusing only truly ambiguous
    spell_name lookups? Patch-gated story on approval; probes flip to pass-
    assertions. (B) bind(**kwargs) silent swallow of unknown keys: keep (lenient
    forward-compat channel) or fail fast on unrecognized keys (typo protection)?
    Fail-fast matches the house fail-fast law; lenient matches the with_kwargs
    "future parameters" docstring. Owner call.
  EVIDENCE:
  - UX_and_AIX_experiences/pytest_examples/test_contract_probes.py:120-160
  IMPACT: Both change public bind/conjure semantics - patch-gated stories either way.
  NEXT: Owner rules; I author the patch lane(s).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-19T13:52:00Z
  TYPE: MEASURE
  CLAIM: First harness run (owner, 3.14t) = the lane working as designed: 10 rows
    green, the rest red for THREE distinct causes, all now fixed. (1) ISOLATION:
    examples shared the process-wide Aether frame ("Conduit with name default
    already exists") - pytest_examples/conftest.py now applies the component-suite
    fixture verbatim (Aether._reset_singleton_for_tests + rebind Spellbook/
    Conduit._aether, before AND after each test). (2) LAW A - callable spells are
    ALWAYS unique (runtime: "Method and lambda spells must use Existence.unique"):
    03/20/32 rewritten - function factories teach one-shared-product; fresh-per-meld
    factories are classes bound many; 32 now contrasts both shapes. (3) LAW B -
    owner-corrected semantics: spells are SHA256 CONTENT-matched, not name-keyed;
    same-name different-internals coexists ("potato"/"potato" passes), same-
    fingerprint rebinds die at conjure unless frame-separated (binding_name alone
    provably failed) - 24/33 use frame separation, 30's lesson line corrected, and
    THREE new probes pin the boundaries (same-name-diff-SHA passes; same-SHA
    frameless fails; same-SHA cross-frame = the open question the probe answers
    either way). Plus: 36 conjures roots with explicit names (root names are
    frame-unique). AGENTS.md gains the discovered-laws section. Probe suite now 11
    rows. compile green across harness + tier.
  EVIDENCE:
  - UX_and_AIX_experiences/pytest_examples/conftest.py:1-30
  - tests/component/melder/aether/conduit/test_conduit_component_cleanup_frame_truth.py:10-30
  - UX_and_AIX_experiences/pytest_examples/test_contract_probes.py:120-190
  - UX_and_AIX_experiences/01_beginner/32_factory_functions.py:1-40
  IMPACT: The harness did its job on run one - two real runtime laws entered the
    curriculum as verified lessons instead of folklore, and the owner's SHA
    clarification is now machine-checked.
  NEXT: OWNER RERUN: pytest UX_and_AIX_experiences/pytest_examples -v. Expected:
    examples green; probe prints document spell_name/unregistered-meld/disposal/
    same-SHA-cross-frame; any remaining red = next lesson corrections.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

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


## MEASURE - 2026-07-20 11:26 UTC - lesson 25 reframed: spellframes as CATEGORIES (owner-directed arc)
  WHAT: Owner directive - the category idea threads the tiers. Beginner 25
    now teaches spellframes AS categories explicitly (organize one world's
    spells by the app's resolution ideas; (category, name) is the full
    address) and SEEDS the graduation: when a category needs its own OWNER
    and resolution conditions, it becomes a whole conduit (intermediate 26).
    Prose/prints only - every proven call untouched (tier stays validated).
  EVIDENCE:
  - UX_and_AIX_experiences/01_beginner/25_frames_as_dict_classification.py:1-14
  - UX_and_AIX_experiences/AGENTS.md (Curriculum arc: categories)
  REREAD: OPTIONAL
  SCORE_0_TO_10: -

## MEASURE - 2026-07-21 09:56 UTC - owner assessment: tier in a good spot
  WHAT: Owner call (end of 2026-07-20 session): "beginner and intermediate are
    in a good spot." Beginner stands validated (40 lessons + probes green) with
    the categories arc seeded at lesson 25. Exit-gate walkthrough remains the
    only open formality.
  REREAD: OPTIONAL
  SCORE_0_TO_10: -

## MEASURE - 2026-07-25 19:50 UTC - lesson 41: the lifecycle law (owner-directed)
  WHAT: New closing lesson 41_you_own_the_memory_now - the DI memory-
    ownership teach the owner called "very important": the runtime HOLDS
    what it builds, so the GC cannot free what the world references;
    cleanup() is how memory comes back. PROVEN in-lesson with a weakref
    watcher: del drops the user ref (object survives - runtime holds),
    conduit.cleanup() + gc.collect() kills it (watcher goes None,
    hard-asserted). A red here on the owner's run would itself be a
    finding (a retention leak). Concept map updated (TEARDOWN + THE
    LIFECYCLE LAW).
  EVIDENCE:
  - UX_and_AIX_experiences/01_beginner/41_you_own_the_memory_now.py
  REREAD: OPTIONAL
  SCORE_0_TO_10: -

- DATETIME: 2026-08-01T10:41:33Z
  TYPE: DECISION
  CLAIM: Ownership reassigned helper_f -> examples_0 under owner directive this session. ONLY the
    `Agent Name` field changed. `Owner: cowork` is deliberately unchanged: `owner` is the
    executor/runtime identity and `agent_name` is the assignment identity - different fields.
    No status, scope, acceptance criterion, or prior note was altered; helper_f's authored notes
    stand as the durable record of who did this work before the handover.
  EVIDENCE:
    - agent_onboarding/default/general/skills/agent_identity.md:21-24
    - tickets/epics/2026-07-19_ux_aix_beginner_experience_epic.md:5-10
  IMPACT: This tier is routable under examples_0; the 2026-07-25 board staleness notice about
    helper_f's silent lanes no longer gates it.
  NEXT: Owner ruling on the two carry-overs recorded in the attention-board note before tier work
    resumes (bind_kwargs_transplant story ownership; helper_f's two unconsumed mailbox messages).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## State Transition Event - 2026-08-01T10:41:33Z
- from_state: assigned helper_f
- to_state: assigned examples_0
- transition_reason: owner directive this session (claim the four UX/AIX epics, remove helper_f
  from ownership). Status field deliberately untouched - assignment changed, lifecycle did not.

## Context / Handoff Summary
Method: every example imports melder as md ONLY - a deep-path import in an example
IS the finding. Examples are runnable scripts with honest asserts; they ride the
owner's 3.14t runs (device VM cannot import the runtime).
