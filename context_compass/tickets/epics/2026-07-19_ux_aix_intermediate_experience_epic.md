# Epic: UX/AIX Intermediate experience exploration

## Metadata
- Epic ID: EPIC-2026-07-19-ux-aix-intermediate
- Status: in_progress
- Owner: cowork
- Agent Name: examples_0
- Priority: p2
- Created: 2026-07-19T12:52:00Z
- Updated: 2026-08-01T10:41:33Z

## Objective
The working developer's tier: SpellBinder fluent binding, spellframes and contracts (SpellMap/SpellContract), SpellSpace scoped resolution, spellbook and aether configuration (+builders), conduit linking and the ConduitCloud, SpellIndex membership verbs, crystallizer activation + first checkpoint.

## Ticket Contract
- ENTRY_GATE: owner directive 2026-07-19 ("explore all the ways a user might use the
  library beginner -> intermediate -> expert -> Master... so we can properly explore
  what we need in init"). Examples live in UX_and_AIX_experiences/02_intermediate/.
- EXECUTION_BOUNDARY: UX_and_AIX_experiences/02_intermediate/ examples + findings notes ONLY.
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
- DATETIME: 2026-07-20T01:19:00Z
  TYPE: MEASURE
  CLAIM: SETTLE-THEN-INHERIT LANDED (owner-ruled; patch lane
    conjure_settle_then_inherit_2026_07_20). Code: Spellbook.
    _settle_or_inherit_conjure_mode (settlement via canonical
    bind_frame_configuration on unfrozen posture; inheritance otherwise;
    effective mode threaded to the entire conjure chain); check_system_state's
    mismatch throw DELETED (policy gate + missing-posture refusal retained). 4
    unit rows (settle/static-own-gate/frozen-automatic-ignores-flag/
    frozen-dynamic-inherits). UX payoff: _dynamic_world helper is now a PLAIN
    BOOK - zero private seams anywhere in intermediate; refusal probe flipped to
    settlement probe. compile green x5. pytest Not run - owner 3.14t:
    pytest tests/unit/melder/aether/spellbook/test_conjure_settle_or_inherit.py -q
    then the full suite + the UX harness.
  EVIDENCE:
  - context_compass/system_docs/patches/active/conjure_settle_then_inherit_2026_07_20/architecture_patch.md:1-40
  - src/melder/aether/spellbook/spellbook.py:5786-5800
  - tests/unit/melder/aether/spellbook/test_conjure_settle_or_inherit.py:1-80
  IMPACT: One declaration flows downhill; conjure(dynamic=True) finally does
    what everyone assumed; intermediate needs no substrate access at all.
  NEXT: Owner full-suite run (component tests that pre-posture frames land in
    the inherit case and should stay green; any red = the map missed a consumer).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-20T01:22:00Z
  TYPE: MEASURE
  CLAIM: OWNER-ORDERED INVESTIGATION: remove conjure's dynamic policing; conduits
    inherit the world's (frame's) posture; dynamic-only operations keep failing
    at THEIR OWN gates. Full impact map (source-verified): (1) PRECEDENT EXISTS -
    Spellbook._is_dynamic_posture() (spellbook.py:3191) already reads frame
    posture and bind_inactive (:4500) already gates on it: conjure is the odd one
    out. (2) THE CHECK - check_system_state (spellbook_creation_system.py:1104)
    does two jobs: [a] dynamic-flag vs posture mismatch throw = DELETE; [b]
    non-dynamic + non-default policy throw = RETAIN, keyed off POSTURE (that
    failure is on purpose - the policy cannot work). (3) FLAG CONSUMERS to switch
    to posture-derived: SpellbookCreationSystem._dynamic (:129, threaded :197/
    :218/:239), blueprint metadata dynamic_mode/automatic_mode (:436-437 - where
    the CONDUIT's mode is born), Spellbook._conjure_dynamic_hint (-> origin_
    dynamic :5299, config emission), the dynamic-crystallizer config-discipline
    guard in _conjure_within_transaction_window, ConduitCloud registration
    (dynamic-and-named -> postured-and-named). Downstream link/sever/transfer/
    upgrade gates UNCHANGED (they read conduit state, which is now born from
    posture). (4) EXTERNAL CALLSITES passing dynamic=: only THREE in src -
    __init__ docstring text, nexus_frame_manager.py:1028 (frames postured by
    builder; drop arg), restore_engine.py:1825 (replays recorded flag; frames
    stage binds posture BEFORE books in the canonical order, so posture already
    carries the truth; drop arg, twin field stays for history). (5) PARAM
    DISPOSITION - owner decision: remove outright (breaks the many test
    callsites; sweep needed) vs accept-and-ignore for one iteration with the
    test sweep separate. RECOMMENDATION: accept-and-ignore + deprecation note,
    sweep tests in the same wave the aetheric-frame introduction lands.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:3191-3205
  - src/melder/aether/spellbook/spellbook_creation_system.py:1099-1156
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1823-1830
  - src/melder/nexus/nexus_frame_manager.py:1026-1031
  IMPACT: Small, well-bounded change; one truth (frame posture) flows downhill;
    purposeful failures stay at the verbs that own them.
  NEXT: Owner reviews this map + rules param disposition -> patch-gated story
    (conjure_inherits_world_posture) implements with tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-20T00:58:00Z
  TYPE: DECISION
  CLAIM: Two owner semantic corrections applied. (1) POSTURE-ONCE LAW: the world
    is postured dynamic ONCE and locks - never rebind. My helper was rebinding a
    fresh posture object per book build (would hit the frozen frame on call two
    in one process); now ensure_dynamic_world() checks current posture and
    no-ops when already dynamic. (2) THE FLAG'S REAL MEANING taught explicitly:
    conjure(dynamic=True) is the PER-CONDUIT opt-in (cloud registration +
    link/sever arming) inside a world that permits it - world permission once,
    conduit opt-in each; a dynamic world can still host static roots. Lesson 21
    restructured to the three-step story (posture once -> book config per book ->
    conduit opt-in at conjure). New probe pins the posture-once idempotence
    (repeat ensure calls + multiple books, one world). Probe suite 16 rows.
  EVIDENCE:
  - UX_and_AIX_experiences/02_intermediate/_dynamic_world.py:1-30
  - UX_and_AIX_experiences/02_intermediate/21_dynamic_linking_basics.py:1-70
  IMPACT: The dynamic arc now teaches the lifecycle truthfully: one world
    decision, many conduit decisions.
  NEXT: Owner run: pytest UX_and_AIX_experiences/pytest_examples -v (80 lesson
    rows + 16 probes).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-20T00:56:00Z
  TYPE: DECISION
  CLAIM: Owner ruling after the dynamic-door investigation: RUN WITH CURRENT SHAPE
    for now - no runtime change; lesson 21 keeps the open two-layer ritual, the
    _dynamic_world helper serves 22-25; AethericFrameConfiguration and aetheric
    frames get their FORMAL introduction next iteration (the A-vs-B posture-door
    decision defers to that lane). Settled facts feeding that next iteration:
    frames are born automatic; conjure(dynamic=True) is a pure READER of frame
    posture and always refuses on plain books; SpellbookConfiguration has no
    posture surface (full verb table read); two runtime messages reference doors
    that do not exist (check_system_state's "set system_state in the
    configuration" + DuplicateSpellNameStrategy's disambiguation advice). TESTS
    (owner: "make sure tests exist for the intermediate"): runner covers all 25
    lessons as pytest rows; intermediate probes corrected - the old dynamic probe
    would have errored (plain-book dynamic conjure) and now ASSERTS the refusal
    law, plus a new helper-path probe proves the lesson-21 ritual links end to
    end. Probe suite: 4 intermediate rows + 11 beginner rows.
  EVIDENCE:
  - UX_and_AIX_experiences/pytest_examples/test_intermediate_probes.py:1-90
  - src/melder/aether/spellbook/spellbook_creation_system.py:1099-1155
  IMPACT: The tier is fully test-backed; the next iteration inherits settled
    facts instead of open questions.
  NEXT: Owner run: pytest UX_and_AIX_experiences/pytest_examples -v (25 beginner
    regressions... 40 beginner + 25 intermediate rows + 15 probes). Next
    iteration: aetheric-frame introduction + posture door A/B + the two
    lying-message fixes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-20T00:12:00Z
  TYPE: DECISION
  CLAIM: Owner correction: do NOT black-box everything - learners must see the
    dynamic setup done normally and learn spellbook configuration properly. New
    shape: lesson 21 rewritten as "configuring a dynamic world end to end, in
    the open" - it TEACHES the two configuration layers explicitly (world
    posture via md.AethericFrameConfiguration + system_state=dynamic bound with
    the public bind_frame_configuration verb; book config via
    SpellbookConfiguration.with_defaults + the freeze law, cross-referenced to
    19) and then does linking + contract sharing. Lessons 22-25 keep the
    _dynamic_world helper for focus; its docstring now points at 21 as the
    written-out ritual it repeats verbatim. Balance: configuration education in
    the open, substrate MECHANICS (what frames are, descriptor/ACL machinery)
    still tier-03.
  EVIDENCE:
  - UX_and_AIX_experiences/02_intermediate/21_dynamic_linking_basics.py:1-60
  IMPACT: The tier now teaches the real ritual once, properly, and reuses it
    quietly everywhere else - both owner requirements satisfied.
  NEXT: Owner run validates the tier.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-19T23:34:00Z
  TYPE: DECISION
  CLAIM: Owner scope ruling: AethericFrame objects are NOT introduced in
    intermediate - the substrate stays invisible. The dynamic posture lane IS
    public (frame.bind_frame_configuration + md.AethericFrameConfiguration with
    system_state=dynamic - owner-confirmed, component-suite canon), but it lives
    in tier 03; intermediate reaches it ONLY through the _dynamic_world helper,
    now rewritten as a declared black box (no substrate teaching in its
    docstring). 24's "frame's phone book" prose softened; lesson sweep confirms
    zero frame-API leaks in 01-25. Charter fence updated: intermediate =
    linking + dynamic + configurations; Nexus/MR/crystallizer/AethericFrame =
    advanced. Also corrected this wave: helper's ctor call fixed to the exact
    keyword-required AethericFrameConfiguration signature (the earlier draft
    would have TypeError'd - caught by signature read, not by the owner's run).
  EVIDENCE:
  - UX_and_AIX_experiences/02_intermediate/_dynamic_world.py:1-22
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:106-126
  IMPACT: Tier teaches dynamic behavior without exposing the substrate; the
    black-box helper is the single place tier 03 will later illuminate.
  NEXT: Owner run validates the tier end to end.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-19T16:10:00Z
  TYPE: DECISION
  CLAIM: Owner ruling: PERMISSIONS ARE LINKING VOCABULARY - read/create/block
    govern what LINKED conduits may do in dynamic worlds, and that is their ONLY
    purpose; they are not a local-meld concept. ALL permissions teaching moved out
    of beginner: 28 -> intermediate/11_permissions_linking_vocabulary (reframed);
    permissions= kwargs stripped from beginner 03/07/18/33/37/40 (defaults apply);
    37's cheatsheet row is now a tier-02 pointer ("linking policy for shared
    worlds"); beginner backfilled with 28_real_objects_no_wrappers (identity law:
    melder hands back the real instance, no proxies). Beginner grep-verified
    permissions-free (39's namespace inventory + 37's pointer row exempt).
    Beginner holds 40; intermediate 11.
  EVIDENCE:
  - UX_and_AIX_experiences/02_intermediate/11_permissions_linking_vocabulary.py:1-15
  - UX_and_AIX_experiences/01_beginner/28_real_objects_no_wrappers.py:1-25
  IMPACT: Hour one shrinks to pure local-world concepts; permissions debut beside
    link(), where they mean something.
  NEXT: Permissions example should grow a LIVE demo (linked borrower blocked/read-
    limited) once the linking lessons expand - verification-gated.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-19T23:16:00Z
  TYPE: MEASURE
  CLAIM: Owner syllabus AUTHORED - intermediate now 25 examples. Scope fence
    recorded: intermediate introduces LINKING + DYNAMIC + CONFIGURATIONS only;
    Nexus/MR/crystallizer -> advanced tier. Easy-first per owner: 19 spellbook
    configuration basics (with_defaults, set_property, the conjure-freezes law),
    20 phase-scheduler knobs (workers + barrier timeout, verified property names
    spellbook_configuration.py:102-111); lineage-automatic already lived at 05.
    DYNAMIC ARC (all doors source-verified this wave): 21 linking basics
    (link + add_spell_to_contract conduit.py:4855 + contracted meld), 22
    permissions LIVE (create vs read shares; prints document read's exact
    refusal/behavior), 23 transfer_of_ownership (conduit.py:3099, preflight
    report keys printed), 24 ConduitCloud via the PUBLIC Conduit.get_conduit_cloud
    (conduit.py:1514; has_conduit_name/get_conduit), 25 clusters +
    unique_per_conduit_cluster (create_cluster/add_conduit_to_cluster
    conduit_cloud.py:455/505; completes the expert-01 declaration). DYNAMIC DOOR
    GAP HANDLED HONESTLY: _dynamic_world.py shared helper mirrors the component
    suite's private-seam pattern with a loud header note - every dynamic lesson
    advertises the missing public API until the owner rules it. All compile
    green; dynamic arc UNRUN (runner verifies). Runner excludes _-prefixed
    helper by glob.
  EVIDENCE:
  - UX_and_AIX_experiences/02_intermediate/_dynamic_world.py:1-25
  - src/melder/aether/conduit/conduit.py:4855-4870
  - src/melder/aether/aetheric_frame/conduit_cloud.py:455-528
  IMPACT: The full intermediate story arc exists: configuration -> DI -> dynamic
    worlds -> sharing -> ownership -> the cloud -> clusters.
  NEXT: OWNER RUN: pytest UX_and_AIX_experiences/pytest_examples -v. Reds in
    21-25 are contract discoveries (permissions/cluster semantics have honest
    print-lanes). Advanced tier opens with Nexus/AR + crystallizer + MR when
    intermediate validates.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-19T22:39:00Z
  TYPE: MEASURE
  CLAIM: Skill-level audit round 3 + intermediate LOAD-OUT. MOVED beginner ->
    intermediate (harsh 4B lens): SpellBinder fluent basics (a second registration
    API is not hour-one), lambda spells (name law + frame address + callable law
    stacked), spell-ids/find_spell_by_id and book introspection (Spell/SpellIndex
    record objects are depth; the agent seat keeps 12+39). Beginner BACKFILLED to
    40 with true basics: bind-many-in-a-loop, constructor-defaults-just-work,
    same-name-across-frames (address-law payoff), reading-the-three-errors recap.
    26 gained the doc-canon FOURTH address form (spell as string = spell_id).
    INTERMEDIATE now 18: scanning, binder basics + full chain, hooks, spellspaces,
    lineage, metadata kwargs, lock context, spell_override, permissions x2,
    lambdas, ids/introspection, and the NEW DI ARC from the full C-doc read -
    15 constructor DI by annotation (SINGLE_BY_ANNOTATION), 16 SpellMap defaults
    (exactly-one law), 17 collection DI (list[Protocol] all-implementations),
    18 has_live_creation no-create probe. test_intermediate_examples.py runner
    added (same harness law). All compile green; DI arc is doc-canon but UNRUN -
    the runner is its verifier. Dynamic/crystallizer arc still blocked on the
    dynamic-frame-door owner ruling (prior note).
  EVIDENCE:
  - UX_and_AIX_experiences/02_intermediate/15_constructor_di_by_annotation.py:1-40
  - UX_and_AIX_experiences/pytest_examples/test_intermediate_examples.py:1-35
  IMPACT: Beginner is now pure hour-one basics; intermediate teaches the actual
    DI power tier from documented contract.
  NEXT: OWNER RUN: pytest UX_and_AIX_experiences/pytest_examples -v (beginner
    regressions + 18 intermediate rows + probes incl. dynamic refusal +
    crystallizer acquisition prints). Then: dynamic-door ruling unlocks the
    dynamic/crystallizer arc.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-19T16:58:00Z
  TYPE: MEASURE
  CLAIM: FULL C-doc re-read completed (owner-ordered; src_architecture 1-1996 +
    src_components 1-4068, every line, this session). Immediate yields for this
    epic: (1) MELD HAS A FOURTH ENTRY FORM - spell passed as a STRING is a
    spell_id (documented DI contract) - beginner 26 teaches three; spell-id form
    queued as the 26 completion. (2) DYNAMIC POSTURE FINDING - invariant:
    dynamic=True conjure requires system_state=dynamic, and the FRAME owns that
    gate (AethericFrameConfiguration.with_system_state/dynamic_defaults);
    SpellbookConfiguration.available_properties carries NO system_state key
    (verified :102-111). The only lanes that posture a dynamic frame today:
    Nexus (NexusFrameBuilder defaults dynamic+ai_native+rift) and the test
    suite's PRIVATE _sync_detached_frame_posture_to_aether helpers. Example 10
    (dynamic named worlds) would have FAILED the next run - PARKED to
    _to_delete; the intermediate probe (plain books + dynamic=True) stays and
    will document the refusal. OWNER QUESTION (design gap candidate): what is
    the intended PUBLIC door for a user to posture a dynamic frame WITHOUT
    Nexus ("crystallizer booting from dynamic no nexus" needs exactly this)?
    Options seen in canon: promote the test-support pattern to a public
    Spellbook/frame verb, a SpellbookConfiguration property that conjure
    derives, or ruling that Nexus IS the dynamic door. (3) Crystallizer
    acquisition candidate from canon: Crystallizer is singleton-constructed
    ("creates or recovers the hosted" + component tests import it directly) -
    the acquisition probe stands to confirm Crystallizer() returns the hosted
    root.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:1120-1135
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:102-114
  - tests/_frame_posture_test_support.py:148-210
  IMPACT: The dynamic/crystallizer arc is now blocked on ONE owner ruling
    instead of my guesses; a probable public-API gap surfaced exactly the way
    this lane is meant to surface them.
  NEXT: Owner rules the dynamic-frame public door; probes run; then the arc
    authors on canon.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-19T15:58:00Z
  TYPE: MEASURE
  CLAIM: Dynamic-mode arc opened (owner-directed). AUTHORED: 10_dynamic_named_worlds
    (canonical owner/borrower pattern LIFTED FROM the component suite - dynamic
    named roots + link()=True + static-vs-dynamic framing) and
    test_intermediate_probes.py (3 rows: dynamic pattern outside the component
    suite; crystallizer ACQUISITION-PATH probe - prints which public doors exist on
    Aether, because the user path to the live crystallizer in a dynamic no-Nexus
    world is NOT yet verified and the crystallizer lessons wait on this print;
    config-before-bind law - the crystallizer-off EXEMPTION pinned now, the
    active-crystallizer refusal (error text captured verbatim from a live run-2
    traceback) lands once acquisition is known). Tier stands at 10 examples.
    NEXT LESSONS QUEUED (verification-gated): crystallizer configure/activate in a
    dynamic no-Nexus world, config-before-bind demonstrated live, first
    checkpoint, CrystallizerBootstrap; then Nexus-static contrast when the expert
    tier opens AR.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_cluster.py:780-800
  - UX_and_AIX_experiences/pytest_examples/test_intermediate_probes.py:1-80
  IMPACT: Dynamic mode enters the curriculum on canon, not guesses; the
    crystallizer arc has its truth-gathering probe in place.
  NEXT: Owner runs the intermediate probes; their prints unlock the crystallizer
    lessons next wave.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8


## MEASURE - 2026-07-20 10:42 UTC - lesson 26 (conduit categories as factory types) + lesson 21 realigned
  WHAT: Owner-directed lesson: conduit CATEGORIES with shared dependencies over
    link - name conduits after your resolution ideas ("platform", "services",
    "workflows") and late-bind the edges BETWEEN categories with SpellContract
    sockets, instead of fronting scopes with abstract factories.
    - NEW 26_conduit_categories_as_factories.py: three category books/conduits;
      consumer classes declare md.SpellContract(spellframe=..., binding_name=...)
      holes; per edge: link -> add_spell_to_contract inside
      transaction("link", conduits=[consumer, provider]) -> 
      validate_contracts_and_define(); one meld at the TOP category resolves the
      two-hop chain. Idiom MIRRORED from the validated integration test
      test_conduit_spell_contract_resolves_after_dynamic_link (borrower pulls
      with conduit=<provider>, explicit link-transaction window, the
      validate-and-define verb) - all surfaces source-verified
      (SpellContract signature + md export at __init__.py:134/236;
      contracted spells land in the borrower _spell_id_pool via
      spellbook.py:_register_contracted_spell_id, the pool Phase 3 iterates).
    - REALIGNED 21_dynamic_linking_basics.py to settle-then-inherit: the manual
      bind_frame_configuration ritual is GONE from the lesson; step 1 is now the
      settlement law (first conjure(dynamic=True) settles + locks), step 2 the
      inheritance law (later books PLAIN-conjure and inherit), step 3 unchanged
      link/share/meld.
    - PROBES: broken test_probe_world_postures_once_then_locks (imported the
      deleted ensure_dynamic_world helper) replaced by
      test_probe_world_settles_once_then_inherits; stale lesson-21 docstring
      fixed; TWO new lesson-26 rows - single-hop socket closure (guaranteed
      mirror of the validated test) and the two-hop category chain (the stretch
      past the proven shape; a red there is a FINDING, not a lesson bug).
    Tier stands at 12 authored dynamic-arc examples (21-26) + probes.
  EVIDENCE:
  - src/melder/aether/conduit/meld/contracts/spell_contract.py:123-180
  - tests/integration/melder/conduit/test_conduit_integration_links_contracts.py:352-445
  - src/melder/aether/spellbook/spellbook.py:1195-1226
  - src/melder/aether/conduit/conduit.py:4956 (bare add self-admits; window optional)
  IMPACT: The owner's factory-replacement story is now a runnable lesson; the
    SpellContract late-binding vocabulary enters the curriculum on the proven
    integration idiom.
  NEXT: Owner runs pytest UX_and_AIX_experiences/pytest_examples -v; decode any
    reds (two-hop probe is the watch point).
  REREAD: REQUIRED
  SCORE_0_TO_10: -

## MEASURE - 2026-07-20 11:02 UTC - harness run 3 decoded: 7 reds -> 5 contracts + 2 bugs, all fixed
  WHAT: Owner ran the full UX harness. Beginner tree stayed green; intermediate
    reds decoded and repaired:
    - 01 scan lesson: HARNESS bug - spec-loaded modules were never registered in
      sys.modules, so sys.modules[__name__] KeyErrored. Both runners now register
      before exec (the canonical import procedure).
    - 05 lineage: lesson re-conjured one book (one-book-one-conduit law).
      Rewritten: the family GROWS via create_lesser_conduit; three generations
      assert one shared ledger.
    - 17 collection DI: frame-wide LookupContainer holds ONE active spell per
      (frame_key, binding_name) - the two Handler providers now carry distinct
      binding names. NEW LAW recorded.
    - 21/22 sharing DIRECTION: add_spell_to_contract is a PULL - the named
      conduit must OWN the spell. Both lessons flipped to borrower-pulls
      (matches the validated integration idiom lesson 26 already used).
    - 25 clusters: unique_per_conduit_cluster requires an ELECTED LEADER
      (ClusterCreations.resolved_store hard-errors while inert). Lesson now
      calls cloud.get_cluster("workers").elect_leader(owner.id). NEW LAW.
    - 26 + two-hop probe: FINDING - the first hop closed (Flow.svc was a real
      Svc) but the CONTRACTED Svc, constructed from the workflows world, got the
      raw SpellContract descriptor for its own conf socket: contract sockets
      close PER-WORLD, and dynamic missing-provider WARNING proceeds, so the
      descriptor leaks silently. Lesson now teaches "a category FINISHES its own
      products" (services melds Svc before workflows pulls; shared lifetimes
      hand the finished instance across via owner creations). Probes split:
      owner-warmed chain asserts identity reuse; cold probe PINS the leak and
      raises the DIVERGENCE FLAG (should nested cross-conduit construction
      refuse instead of leak? owner ruling wanted).
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1722 (ownership check)
  - src/melder/aether/aetheric_frame/lookup_container.py:96 (signature claim)
  - src/melder/aether/conduit/creations/cluster_creations.py:163 (leader gate)
  - src/melder/aether/conduit/conduit_cluster.py:810 (elect_leader verb)
  IMPACT: Five runtime laws enter the charter; the factory-categories lesson now
    teaches the true per-world contract model instead of an accidental leak.
  NEXT: Owner reruns the harness; watch the two new lesson-26 probes and the
    descriptor-leak divergence flag for a ruling.
  REREAD: REQUIRED
  SCORE_0_TO_10: -

## DECISION - 2026-07-20 11:23 UTC - owner rulings on the SpellContract lane
  RULING 1 (order of operations; "the code is fine, you're just not
  understanding what to do"): per edge - conjure provider, conjure consumer,
  LINK after both are built, pull, MELD after the fact; chains assemble edge
  by edge in dependency order. The run-3 "descriptor leak" was USAGE ERROR
  (cold chain skipped the middle world's meld), not a runtime gap - the
  divergence flag is WITHDRAWN and the cold misuse probe DELETED.
  RULING 2 (normal code only; "just use link"): curriculum code must not pull
  mediator transactions into user flow. The transaction("link", conduits=[...])
  windows and validate_contracts_and_define ceremony (copied from the
  integration test) are stripped from lesson 26 and both contract probes;
  add_spell_to_contract SELF-ADMITS (conduit.py:4956). User surface = link /
  add_spell_to_contract / meld.
  STATE: lesson 26 and probes re-cut to canonical order + normal verbs;
  AGENTS.md laws rewritten accordingly. Awaiting owner harness rerun.
  REREAD: REQUIRED
  SCORE_0_TO_10: -

## MEASURE - 2026-07-20 11:17 UTC - run 4: everything green except 25; owner-directed fix landed
  WHAT: Owner run 4 - the full harness is GREEN except 25_clusters: election
    fixed the owner-side meld (the previous inert-store error is gone) but the
    MEMBER could not resolve ClusterBus at all (KeyError: not local, not
    contracted) - the join-time auto-share never delivered the spell.
    Owner-directed fix, both halves:
    1) bind carries permissions="create" explicitly - cluster auto-sharing
       contracts the spell to each joining member WITH the spell's own
       permissions (share_to_borrower uses spell.permissions).
    2) elect_leader(owner.id) moved BEFORE the member joins - the join-time
       share then fires against the ARMED cluster ("elect a leader and the
       rest falls into place").
  LAW (charter-bound next pass): cluster assembly order - create_cluster ->
    add the owner root -> elect the leader -> THEN add members -> meld.
  EVIDENCE:
  - UX_and_AIX_experiences/02_intermediate/25_clusters_unique_per_cluster.py:24-44
  - context: run-4 traceback (member-side KeyError clusterbus/__default__)
  IMPACT: With 25 green the intermediate tier (01-26) is fully run-proven.
  NEXT: Owner reruns row 25 (or the tier); on green, close out and open the
    next lesson wave.
  REREAD: OPTIONAL
  SCORE_0_TO_10: -

## DECISION - 2026-07-20 11:23 UTC - owner ruling: with-book lock context is not user value
  RULING: `with book:` (the Spellbook lock context) buys the user nothing - the
    mediator pattern + internal locks already own synchronization. Lesson 07
    retired to _to_delete/ (07_book_as_lock_context.py).
  REPLACEMENT at slot 07: 07_lesser_conduits_child_scopes.py - lesser conduits
    as lightweight child scopes (create_lesser_conduit; a child melds the
    root's world - "unique" resolves the SAME instance via owner creations;
    lessers are unnamed; upgrade_to_normal deferred to dynamic lessons), and
    the explicit-cleanup teaching from the retired lesson carries over
    (cleanup is a verb, post-cleanup bind guards).
  NOTE: lesson 25 additionally gained the missing owner.link(member) step this
    session - contracts ride links; the cluster auto-share adds spells into
    EXISTING contract buckets (ward refuses "link ... prior to spell contract
    initiation" and share_to_borrower swallows it silently).
  REREAD: OPTIONAL
  SCORE_0_TO_10: -

## MEASURE - 2026-07-20 11:26 UTC - category arc named across tiers (owner-directed)
  WHAT: Lesson 26's docstring now names THE ARC: beginner 25 (spellframes
    categorize spells WITHIN one world) -> intermediate 26 (conduits
    categorize WORLDS - each category gains an owner; permissions +
    contracts + links set resolution conditions at the boundary). Arc
    recorded in AGENTS.md as curriculum law.
  EVIDENCE:
  - UX_and_AIX_experiences/02_intermediate/26_conduit_categories_as_factories.py:1-26
  - UX_and_AIX_experiences/AGENTS.md (Curriculum arc: categories)
  REREAD: OPTIONAL
  SCORE_0_TO_10: -

## MEASURE - 2026-07-21 09:56 UTC - owner assessment: tier in a good spot
  WHAT: Owner call (end of 2026-07-20 session): "beginner and intermediate are
    in a good spot." Two rows still await one green run: 25_clusters (now with
    the owner.link(member) fix - contracts ride links) and the replacement
    07_lesser_conduits_child_scopes. After that run the tier is fully
    run-proven at 26 lessons. Boot-melds epic parked ACTIVE/unassigned for the
    owner's weekend design pass; the sophisticated follow-ons land in the
    advanced/expert tiers (names TBD).
  REREAD: OPTIONAL
  SCORE_0_TO_10: -

## MEASURE - 2026-07-21 10:04 UTC - lesson 08 corrected: spell_override overrides spells INSIDE the graph
  WHAT: Owner flagged 08_spell_override_construction as "basically wrong". He
    is right on two counts: (1) the lesson only showed the FLAT form (root
    ctor kwargs) and never asserted it; the real power - proven by the
    component deep-override suite (test_conduit_component_meld_overrides_deep:
    ">"-path keys target dependency sockets, replace the actual object,
    whitespace-tolerant, missing path raises, untargeted sockets keep DI
    defaults) - was absent. (2) the lesson's NOTE claimed bind(**kwargs)
    "feeds lifecycle hooks" - stale since the metadata-kwargs feature (kwargs
    land on spell.metadata; lesson 06).
    FIXED: lesson 08 now teaches BOTH forms with hard asserts (flat dict ->
    root ctor kwargs; "transport>credentials" path -> replaces the object at
    that socket inside the graph). NEW PROBE
    test_probe_spell_override_targets_spells_inside_the_graph pins both forms
    plus untargeted-socket preservation, mirrored from the component idiom.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_meld_overrides_deep.py:392-427
  - UX_and_AIX_experiences/02_intermediate/08_spell_override_construction.py
  - UX_and_AIX_experiences/pytest_examples/test_intermediate_probes.py (tail probe)
  NEXT: rides the owner's next harness run with 25 and 07.
  REREAD: OPTIONAL
  SCORE_0_TO_10: -

## DECISION - 2026-07-21 10:38 UTC - owner ruling: override tiers split
  RULING: the top-level override stays SIMPLE at intermediate; the targeted
    deep form is an advanced teach. Lesson 08 back to the flat dict -> root
    ctor kwargs only (asserts kept, stale bind-kwargs NOTE stays corrected);
    the ">"-path socket-replacement form moved to the expert tier as
    03_expert/02_deep_spell_override_paths.py. The probe pinning BOTH forms
    stays in the intermediate mirror (runtime truth is tier-independent),
    docstring re-pointed at each form's tier.
  REREAD: OPTIONAL
  SCORE_0_TO_10: -

## MEASURE - 2026-07-25 19:33 UTC - closing wave first half: 27 sever_link + 28 upgrade_to_normal
  WHAT: Owner-directed. Two new lessons close the biggest fence gaps:
    - 27_sever_link: the UNDO of the dynamic arc - contracts die with the
      link; the borrower loses the RIGHT TO RESOLVE (next meld refuses) while
      the owner's live instances are untouched; double-sever refuses. Lesson
      prints refusal types loosely (exact exception shapes pinned on the
      owner's first run per harness law); probe uses pytest.raises(Exception)
      + type prints for the decode pass.
    - 28_upgrade_to_normal: lesser grows up in place - named, world-
      registered, discoverable via cloud.get_conduit_by_name, and its
      per-conduit creations SURVIVE the promotion (identity-asserted).
      Idiom mirrored from the validated component test
      test_component_conduit_upgrade_transfers_lesser_creations_and_reuses_
      unique + the lifecycle integration test (cloud lookup).
    Concept map updated: both verbs moved from gaps to covered; remaining
    fence gaps = live link policies + conduit lifecycle hooks.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_creations.py:392-436
  - tests/integration/melder/conduit/test_conduit_integration_lifecycle.py:318-353
  - UX_and_AIX_experiences/02_intermediate/27_sever_link.py, 28_upgrade_to_normal.py
  NEXT: Owner harness run picks up 25 (link fix), 07/08 (rework), 26 probes,
    and now 27/28 - one run validates the whole tail.
  REREAD: OPTIONAL
  SCORE_0_TO_10: -

## MEASURE - 2026-07-25 19:50 UTC - owner-directed: sever retention beat + lesson 29 scoped cleanup
  WHAT: (1) Lesson 27 gained the CREATIONS-RETENTION beat: after sever the
    owner's has_live_creation stays True - severing revokes resolution
    rights, never memory (probe asserts it too). (2) New lesson 29
    scoped_cleanup_lesser_conduits: the throwaway-scope pattern - child
    conduit per job, child.cleanup() fires disposal_method_names
    scope-locally (job session closed, root session untouched, root keeps
    resolving), then root.cleanup() one level up; carries the lifecycle
    law forward from beginner 41. Concept maps updated.
  EVIDENCE:
  - UX_and_AIX_experiences/02_intermediate/27_sever_link.py (retention beat)
  - UX_and_AIX_experiences/02_intermediate/29_scoped_cleanup_lesser_conduits.py
  NEXT: One owner harness run validates the whole tail: 25 fix, 07/08
    rework, 26 probes, 27/28/29, beginner 41.
  REREAD: OPTIONAL
  SCORE_0_TO_10: -

## MEASURE - 2026-07-26 17:42 UTC - configuration knob-by-knob wave (owner-directed): lessons 30-34
  WHAT: Full SpellbookConfiguration inventory read from source (5 properties:
    disposal, disposal_method_names, phase_scheduler_workers_per_spellbook,
    phase_scheduler_barrier_timeout_milliseconds,
    generalized_singleton_specialization_enabled; 11 hooks in 4 families;
    idempotent keys = the disposal pair; add_hook keyed by BOOK id). Five new
    lessons: 30 disposal + idempotent + freeze laws; 31 the specialization
    speed knob (zero semantic change); 32 meld pipeline hooks; 33 conduit
    lifecycle hooks in order; 34 link + contract hooks across the arc -
    CLOSES the parked conduit-hooks gap. Remaining fence gap: live link
    policies only. Probes: 3 new intermediate rows (config laws,
    specialization semantics, all hook families with stream print).
  EVIDENCE:
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:136-176,659-700
  - UX_and_AIX_experiences/02_intermediate/30-34_*.py
  REREAD: OPTIONAL
  SCORE_0_TO_10: -

## MEASURE - 2026-07-26 20:11 UTC - owner flagged lesson 31 as fabricated; corrected from source + wave audited
  WHAT: GUILTY on 31: the property name came from available_properties, but I
    wrote its MECHANISM from the inline comment instead of reading the
    consumer. Source truth (generalized_hydrator.py:540-600 +
    generalized_manifest_no_overrides_compiler.py:1118+): the knob arms the
    generalized no-overrides lane's THIRD door stage (cold -> hot ->
    SPECIALIZED) - after the first successful hot execution the executor body
    is REBUILT with owner-store `unique` DEPENDENCY singletons captured in
    its closure behind per-dep EPOCH GUARDS, then self-swapped into the
    published context; the flag reads once per hydration and
    missing/unavailable = OFF. My original demo (dependency-less unique
    melded thrice) exercised none of it. Lesson 31 + its probe + the concept
    map line rewritten to the honest shape: MANY root over UNIQUE dep -
    fresh roots, one captured dep, semantics identical to knob-off.
  AUDIT of the rest of the wave (owner-ordered): lesson 30 idempotent law
    EXACT per set_property source (RuntimeError "Cannot modify idempotent
    property ... once set"; frozen refusal separate); lesson 34 contract
    hooks REAL (on_contract_created firing sites conduit.py:5277,5554);
    32/33 hook wiring documented in C-docs (meld pre/post, conjure and
    cleanup hook firing). No other fabrications found.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:540-600
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:228-236
  - src/melder/aether/conduit/conduit.py:5277,5554
  LESSON: a config comment is not a mechanism - read the CONSUMER before
    explaining a knob.
  REREAD: OPTIONAL
  SCORE_0_TO_10: -

## DECISION+MEASURE - 2026-07-26 23:06 UTC - config curriculum re-cut per owner rulings
  RULINGS: (1) compiler-lane knobs are NOT curriculum - 31 specialization
    lesson RETIRED to _to_delete with its probe; (2) advanced 06 caching
    lesson RETIRED ("why would someone turn off cache"; cache teaching waits
    for the crystallizer arc and must name WHERE the cache lives on disk);
    (3) spellbook config gets a proper DEFINITION pass; (4) AFC enters
    INTERMEDIATE via the framewide-spellbook-config story.
  LANDED:
    - 31_spellbook_config_defined: the four items with real semantics
      (disposal switch, teardown vocabulary, pipeline workers, barrier
      timeout as the anti-hang knob) + the four laws (closed registry /
      idempotent pair / freeze / completion - bare config refuses at
      conjure). Written for someone who knows nothing.
    - 35_one_config_every_book: manual share (ONE config object handed to
      every book - fully public, identity-asserted) + the frame-owned
      automatic adoption via shared_framewide_spellbook_configuration
      (mechanism source-verified at spellbook.py:5292-5358: flag gates
      adoption of the frame-owned rich config; first book binds it, later
      books adopt THE SAME OBJECT).
    - Probes: 3 new rows (definition laws w/ refusal types printed; manual
      share; frame-owned adoption pinned VIA SEAM - the staging door for the
      posture flag is a recorded public-surface FINDING, same family as the
      devops brakes).
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:5292-5358 (adoption machinery)
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py (full def inventory, 1185 lines)
  REREAD: OPTIONAL
  SCORE_0_TO_10: -

## MEASURE+DECISION - 2026-07-27 11:36 UTC - framewide spellbook config: owner challenge, full trace, lesson 35 corrected
  OWNER CHALLENGE: "how is your single config shared with everyone ... the
    aetheric_frame_configueration ... by default will have it shared with all
    spellbooks" - then "I thought by default it would use 1 spellbook
    configuration unless you override it".
  TRACE (whole path read, no inference):
    - DEFAULT IS PER-BOOK, not per-frame. shared_framewide_spellbook_
      configuration is False at every origin: AFC ctor default
      (aetheric_frame_configuration.py:118), the frame's minted posture
      (aetheric_frame.py:224), and with_defaults() resets it to False
      (:1177) - so dynamic_defaults()/automatic_defaults(), which are
      with_defaults() + a state (:1362, :1399), are False too.
    - Every sharing path early-outs while the flag is False:
      _get_configuration_from_aether (spellbook.py:5306),
      _bind_configuration_to_aether (:5620),
      _is_frame_owned_shared_configuration (:5347). With it off,
      _initialize_configuration falls to the mint branch (:5281-5283):
      fresh SpellbookConfiguration + load_default_dictionary, unlocked.
    - TURNING IT ON TAKES TWO STEPS, and the flag alone does nothing:
      (1) SWITCH - frame posture carries the flag True; the Spellbook holds
          the frame-owned posture BY REFERENCE
          (_initialize_aetheric_frame_configuration, :5359-5376).
      (2) PUBLICATION - configure_aether_frame() is the ONLY caller of
          _bind_configuration_to_aether (:5909-5910). conjure() does NOT
          publish (conjure path carries no bind call; the creation system
          only freezes, spellbook_creation_system.py:298).
    - AFTER both: later books adopt the frame-owned object at __init__
      (:311 -> :5238) and are LOCKED; a DIFFERENT config handed to a later
      book raises "Aether configuration does not match" (:5257); first
      publisher wins (aether.py:1194 leaves an existing config in place); a
      pre-existing book that later publishes ADOPTS and cleans up its own
      local config (:5626-5637); adoption is total - no per-book override;
      book cleanup SKIPS cleaning a frame-owned shared config (:479-486).
  FINDINGS (public-surface program):
    - The SWITCH has no public door: only the AFC ctor kwarg (:118) and
      with_shared_framewide_spellbook_configuration() (:607) set it, and
      configure_aether_frame() never touches it. (Already entry #2 in the
      pile; now with the full mechanism attached.)
    - configure_aether_frame(disposal=...) is unusable on an auto-minted
      book: load_default_dictionary already sets disposal and
      disposal_method_names, and both are idempotent set-once
      (spellbook_configuration.py:148), so the door raises "Cannot modify
      idempotent property". It only works on a user-supplied config that
      left them unset. NEW FINDING.
  LANDED:
    - 35_one_config_every_book REWRITTEN: leads with the per-book default
      (asserted: two books, same frame, two configs), keeps manual share as
      the runnable public path, and states the frame-owned mechanics
      correctly (switch + publication, conjure does not publish).
    - Probes RECUT to the truth - the old row claimed conjure() published,
      which is FALSE and would have gone red on the owner's harness:
      * test_probe_config_is_per_book_by_default - tripwire: goes red on
        purpose if the runtime ever defaults sharing ON.
      * test_probe_frame_owned_config_needs_switch_and_publication - switch
        alone changes nothing.
      * test_probe_frame_owned_config_adoption_via_seam - switch + publish,
        adoption identity, locked flag, mismatched-config refusal, both
        worlds conjure and meld.
  OPEN FOR OWNER: is default-shared the INTENT? If yes it is a one-line flip
    (mint the frame posture with True, aetheric_frame.py:224) plus a ruling
    on whether with_defaults() (:1177) keeps bulldozing the flag to False.
    Lesson + probes today document the CODE as written.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:118,607,1177,1362,1399
  - src/melder/aether/aetheric_frame/aetheric_frame.py:224
  - src/melder/aether/spellbook/spellbook.py:311,5238,5257,5281,5306,5347,5359,5620,5626,5909
  - src/melder/aether/aether.py:1194
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:148,559
  LESSON: "shared by default" was the owner's intent, not the code's
    behaviour - trace every origin AND every gate before writing the law.
  REREAD: OPTIONAL
  SCORE_0_TO_10: -

## CORRECTION - 2026-07-27 22:20 UTC - I was wrong twice; owner was right about the frame posture

MEASURE: owner pushed back a second time ("go research the code because
your not understanding"). Re-traced the whole surface instead of
re-asserting. Two defects in my previous note, one of them shipped into
four files.

DEFECT 1 (mine, shipped): "conjure() does NOT publish - configure_aether_
frame() is the ONLY caller of _bind_configuration_to_aether" is FALSE. I
grepped spellbook.py ONLY, not the tree. The second caller lives in
spellbook_creation_system.py:299, inside _prepare_spellbook_for_conjure,
which runs `if not spellbook.is_configuration_locked(): _validate_and_
freeze_configuration(); _bind_aetheric_frame_configuration_to_aether();
_bind_configuration_to_aether()`. Reached from Spellbook.conjure
(spellbook.py:6248 -> creation system :210 -> :278). So conjure IS a
publication door. The ORIGINAL probe comment I "corrected" was right.

DEFECT 2 (mine, analytical): the owner's claim was about the
AethericFrameConfiguration; I answered about shared_framewide_spellbook_
configuration, which governs a DIFFERENT object. He is CORRECT: the
frame POSTURE is shared with every spellbook on the frame BY DEFAULT,
unconditionally, no flag. AethericFrame mints exactly one posture
(aetheric_frame.py:218-224); Spellbook._initialize_aetheric_frame_
configuration (spellbook.py:5359-5376) only RETRIEVES it via
Aether._get_aetheric_frame_configuration (aether.py:1264-1297 ->
frame.frame_configuration, aetheric_frame.py:563-573) and retains the
reference. A Spellbook never mints its own. Therefore configure_aether_
frame(system_state=..., system_caching_enabled=...) mutates the SHARED
object (spellbook.py:5884-5889) and reconfigures the whole frame for
every book on it.

DECISION: the standing law is TWO OBJECTS, TWO DEFAULTS.
  - AethericFrameConfiguration (narrow posture): shared framewide by
    default, always. No opt-in.
  - SpellbookConfiguration (rich per-book config): per-book by default;
    frame-owned sharing needs the switch (shared_framewide_spellbook_
    configuration=True, minted False at aetheric_frame.py:224) AND a
    publication through either door.
The three consumer gates on the rich-config path are unchanged and still
verified: spellbook.py:5306, :5347, :5620.

ALSO TRACED (new, not previously recorded): AethericFrame.
bind_frame_configuration (aetheric_frame.py:626-724) ABSORBS a different
incoming posture field-by-field into the existing frame-owned object
(including with_shared_framewide_spellbook_configuration at :687) and
cleanup()s the incoming one, then freezes. conjure(dynamic=True) settles
the world by mutating and rebinding the SAME retained object
(spellbook.py:6045-6061) precisely to avoid bulldozing pre-conjure flags.

LANDED: probe file - step-2 law rewritten to name BOTH doors, and a new
probe test_probe_frame_posture_is_shared_framewide_by_default pins the
owner's law (same posture object across two books; mutation through one
visible through the other; rich configs still separate). Lesson 35
docstring now opens with the two-objects/two-defaults split. Concept map
lesson-35 block rewritten. Four probes now, not three.

FINDINGS (unchanged, re-verified): no public injection door for a
user-built AethericFrameConfiguration - the only constructions are
aetheric_frame.py:219, restore_engine.py:1654, nexus_frame_
configuration.py:327, and no Spellbook accessor exposes the retained
posture (grep for a public frame-configuration door returns nothing).
The class IS exported (melder/__init__.py:68/198) with no way to install
one. Also unchanged: configure_aether_frame(disposal=...) is unusable on
an auto-minted book (idempotent pre-set).

LESSON: grep the TREE, not the file. A single-file caller search
produced a confident, wrong, shipped law. And when the owner names an
object, trace THAT object before defending a different one.

EVIDENCE: spellbook_creation_system.py:296-300; spellbook.py:5359-5376,
:5238-5289, :5306, :5347, :5597-5650, :5854-5910, :6045-6061, :6248;
aetheric_frame.py:218-224, :563-573, :626-724; aether.py:1264-1297,
:1194; aetheric_frame_configuration.py:118, :607, :659-700, :1177,
:1580; melder/__init__.py:68, :198.

## MEASURE+DECISION - 2026-07-27 22:25 UTC - the shared-config PROCESS, written for users; switch door is BLOCKING

MEASURE: owner asked for the actual process a user follows to get ONE
SpellbookConfiguration shared by every spellbook, and told me to stop
demonstrating posture sharing with the caching knob. Ran the exhaustive
tree grep I should have run the first time.

EXHAUSTIVE SWITCH TRACE (`grep -rn shared_framewide src/`, excluding the
posture class itself) - SIX sites, all of them:
  aetheric_frame.py:224   mint, passes False
  aetheric_frame.py:687-688  bind_frame_configuration absorbs the flag
                             from a DIFFERENT incoming posture
  spellbook.py:5308, :5349, :5620  the three consumer gates
Every construction site in the runtime leaves it False or omits it:
aetheric_frame.py:219 (False), restore_engine.py:1654, and
nexus_frame_configuration.py:327 `to_aetheric_frame_configuration()`
which does not pass the kwarg at all. No Spellbook accessor exposes the
retained posture. AetherConfiguration/AetherConfigurationBuilder are
logging-only. CONCLUSION: shape 2 (frame-owned shared rich config) is
COMPLETE machinery that is UNREACHABLE from any public API.

ORDERING LAW (new, source-verified): the switch must be flipped BEFORE
the frame's first conjure. conjure -> _prepare_spellbook_for_conjure
calls _bind_aetheric_frame_configuration_to_aether, which binds the
retained posture and FREEZES it (aetheric_frame.py:667-726), and
with_shared_framewide_spellbook_configuration raises "Cannot modify
frame configuration after it is frozen" once frozen
(aetheric_frame_configuration.py:653-656). Note configure_aether_frame
does NOT freeze the posture - it only freezes and binds the RICH config
- so it is not the deadline; the first conjure is.

DECISION: lesson 35 now teaches the PROCESS, not the trivia. Shape 1
(manual share) is presented as THE answer that works today, as three
numbered steps - build one config for the frame, set policy once, hand
the same object to every book - with the runnable proof. Shape 2 is
documented in full with its ordering law and an explicit HONEST GAP
paragraph saying no public switch exists. Probes now pin all four facts;
the posture-sharing probe uses THE SWITCH ITSELF as its observable
instead of system_caching_enabled (owner: the cache knob is a dumb
demonstration of a configuration law - agreed, it taught nothing about
the subject).

BLOCKING FOR OWNER - the door. Cheapest correct placement is a
`shared_framewide_spellbook_configuration: Optional[bool] = None` kwarg
on configure_aether_frame(): that method already mutates the shared
frame posture (system_state, system_caching_enabled) and already runs
_validate_and_freeze_configuration + _bind_configuration_to_aether right
after, so setting the flag there lands in exactly the right order -
switch, freeze, publish, later books adopt. It does not freeze the
posture, so it does not fight the ordering law. Until that exists, the
curriculum cannot show shape 2 as normal code, because a lesson may
import melder as md ONLY and the only setters are the posture ctor
kwarg (:118) and with_shared_framewide_spellbook_configuration() (:607).

LANDED: 35_one_config_every_book.py rewritten around the two-object
split and the two shapes with numbered steps (5030 bytes, CRLF, AST OK);
probe file's posture probe re-cut off the caching knob; concept map
lesson-35 block rewritten to the process; four probes total.

EVIDENCE: aetheric_frame.py:218-224, :563-573, :626-726, :687-688;
aetheric_frame_configuration.py:118, :607, :653-656, :1177;
spellbook.py:5238-5289, :5308, :5349, :5359-5376, :5558-5568,
:5597-5650, :5854-5910, :6045-6061, :6248;
spellbook_creation_system.py:296-300;
spellbook_configuration.py:113, :1049; aether.py:1194, :1264-1297;
nexus_frame_configuration.py:327; nexus_frame_manager.py:994-1029;
restore_engine.py:1654; melder/__init__.py:68, :198.

- DATETIME: 2026-08-01T10:41:33Z
  TYPE: DECISION
  CLAIM: Ownership reassigned helper_f -> examples_0 under owner directive this session. ONLY the
    `Agent Name` field changed. `Owner: cowork` is deliberately unchanged: `owner` is the
    executor/runtime identity and `agent_name` is the assignment identity - different fields.
    No status, scope, acceptance criterion, or prior note was altered.
  EVIDENCE:
    - agent_onboarding/default/general/skills/agent_identity.md:21-24
    - tickets/epics/2026-07-19_ux_aix_intermediate_experience_epic.md:5-10
  IMPACT: This is the only one of the four tiers reading `in_progress`, so it is the live lane and
    the one where a stale assignment would have done real damage.
  NEXT: Owner ruling on the inbound helper_f mailbox message dated 2026-07-20T00:55:00Z, which
    names THIS epic: melder_0 already folded the settle-then-inherit law into src_architecture.md
    and warns the lane owner not to re-fold it at closure. That warning transfers with the epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## State Transition Event - 2026-08-01T10:41:33Z
- from_state: assigned helper_f
- to_state: assigned examples_0
- transition_reason: owner directive this session (claim the four UX/AIX epics, remove helper_f
  from ownership). Status stays `in_progress` - assignment changed, lifecycle did not.

## Context / Handoff Summary
Method: every example imports melder as md ONLY - a deep-path import in an example
IS the finding. Examples are runnable scripts with honest asserts; they ride the
owner's 3.14t runs (device VM cannot import the runtime).
