# Epic: UX/AIX Intermediate experience exploration

## Metadata
- Epic ID: EPIC-2026-07-19-ux-aix-intermediate
- Status: in_progress
- Owner: cowork
- Agent Name: helper_f
- Priority: p2
- Created: 2026-07-19T12:52:00Z
- Updated: 2026-07-19T12:52:00Z

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


## Context / Handoff Summary
Method: every example imports melder as md ONLY - a deep-path import in an example
IS the finding. Examples are runnable scripts with honest asserts; they ride the
owner's 3.14t runs (device VM cannot import the runtime).
