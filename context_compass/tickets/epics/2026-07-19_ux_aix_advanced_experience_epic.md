# Epic: UX/AIX Advanced experience exploration

## Metadata
- Epic ID: EPIC-2026-07-19-ux-aix-advanced
- Status: done_pending_owner_run
- Owner: cowork
- Agent Name: examples_0
- Priority: p2
- Created: 2026-07-19T12:52:00Z
- Updated: 2026-08-02T15:43:51Z

## Objective
The isolation + AR tier: configuration surfaces fenced out of intermediate
(AethericFrameConfiguration, AetherConfiguration, SystemState), Nexus
enablement, rifts and rooms by RiftSpaceType (STATIC and CAPABILITY),
workstation binding canvases, frame viewers and the View* family, ward
policies, and checkpoint/load.

SCOPE CORRECTED 2026-08-02 (owner). The previous objective claimed research
sets with typed lanes, diff/impact/foresight reads, and drift views. Those are
MUTATION RESEARCH and belong to EXPERT, together with notch, codegen,
crystallizer save/load, and synthetic modules. See the tier scope note below.

## Ticket Contract
- ENTRY_GATE: owner directive 2026-07-19 ("explore all the ways a user might use the
  library beginner -> intermediate -> expert -> Master... so we can properly explore
  what we need in init"). Examples live in UX_and_AIX_experiences/03_advanced/.
- EXECUTION_BOUNDARY: UX_and_AIX_experiences/03_advanced/ examples + findings
  notes ONLY. (Folder was 03_expert before the 2026-07-25 rename; path
  corrected 2026-08-02.)
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

## DECISION - 2026-07-25 19:23 UTC - tier renamed to ADVANCED (README ladder match)
  RULING: owner (2026-07-22) - the ladder is Beginner/Intermediate/Advanced/
    Expert per the shipped README. This epic (formerly "Expert", folder
    03_expert) is now the ADVANCED tier: frames as worlds, static rooms,
    clusters, deep overrides. Folder renamed 03_expert -> 03_advanced; the two
    seeded lessons retiered in their headers (cluster declaration, deep
    override paths). Historical notes below keep their original wording.
  REREAD: OPTIONAL
  SCORE_0_TO_10: -

## MEASURE - 2026-07-26 17:13 UTC - advanced tier opens: owner syllabus wave 1 (lessons 03-05)
  WHAT: Owner syllabus for advanced: devops config, aetheric_frame config,
    frame management/layers of separation, utility-system logger, "static
    and compatibility mode", crystallizer basics LAST (owner adding epic
    items himself). Wave 1 authored after source verification:
    - 03_frames_as_worlds: categories arc ACT 3 - Spellbook(aetheric_frame=)
      births an isolated world; same class + name in two frames, zero
      collision; unique = singleton PER FRAME; per-frame reuse asserted.
    - 04_frame_posture_public_door: configure_aether_frame(system_state=
      "dynamic") pre-conjure -> plain conjures INHERIT and link (settle law
      driven from the config side); posture freezes at first conjure -
      reconfigure refuses (caught + printed).
    - 05_utility_system_logger: boots-silent law; attach_logger /
      enable_logging public doors; None detaches (BUG-278 retire law noted
      in source read).
    Harness: test_advanced_examples.py runner (sys.modules import law) +
    test_advanced_probes.py (4 rows: frame isolation pin, posture+freeze,
    devops-flag gate via seam, logger lifecycle).
  FINDINGS:
    - NO PUBLIC DOOR for frame devops flags (disable_*): component suite
      stages via PRIVATE book._aetheric_frame_configuration. Probe pins the
      gate through the seam; init/public-surface gap recorded for owner.
    - "compatibility mode" absent from src/melder - awaiting owner
      definition (concept map notes it).
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:366-1364 (verb sweep)
  - src/melder/aether/aether.py:502-560 (attach_logger contract, BUG-278)
  - src/melder/aether/spellbook/spellbook.py:203 (aetheric_frame ctor door)
  - grep: no public frame accessor on Aether; "compatibility" absent
  NEXT: Owner runs the harness (advanced rows now included); crystallizer
    lessons wait for the owner's epic additions + the acquisition-path
    probe's print.
  REREAD: REQUIRED
  SCORE_0_TO_10: -

## MEASURE - 2026-07-26 17:42 UTC - posture knob wave: lessons 06-07 + probes
  WHAT: 06 frame_caching_knob (system_caching_enabled via the public
    configure_aether_frame door). 07 frame_posture_cheatsheet - all 15
    AethericFrameConfiguration knobs mapped and explained in one runnable
    reference (mode / AR eligibility / sharing / caching / 7 devops brakes /
    transaction patience / 3 presets / freeze law), the advanced twin of
    beginner 37. Advanced probes now 5 rows (+caching door). Findings stand:
    no public staging door for devops brakes or cache_root_path.
  EVIDENCE:
  - UX_and_AIX_experiences/03_advanced/06-07_*.py
  - UX_and_AIX_experiences/pytest_examples/test_advanced_probes.py
  REREAD: OPTIONAL
  SCORE_0_TO_10: -

- DATETIME: 2026-08-01T10:41:33Z
  TYPE: DECISION
  CLAIM: Ownership reassigned helper_f -> examples_0 under owner directive this session. ONLY the
    `Agent Name` field changed. `Owner: cowork` is deliberately unchanged: `owner` is the
    executor/runtime identity and `agent_name` is the assignment identity - different fields.
    No status, scope, acceptance criterion, or prior note was altered.
  EVIDENCE:
    - agent_onboarding/default/general/skills/agent_identity.md:21-24
    - tickets/epics/2026-07-19_ux_aix_advanced_experience_epic.md:5-10
  IMPACT: Tier stays `pending`; the owner syllabus wave 1 recorded here (lessons 03-05) is now
    examples_0's to author.
  NEXT: Beginner and intermediate tiers gate this one - do not open advanced authoring until the
    owner's 3.14t walkthrough of those tiers lands.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## State Transition Event - 2026-08-01T10:41:33Z
- from_state: assigned helper_f
- to_state: assigned examples_0
- transition_reason: owner directive this session (claim the four UX/AIX epics, remove helper_f
  from ownership). Status stays `pending` - assignment changed, lifecycle did not.

- DATETIME: 2026-08-02T15:43:51Z
  TYPE: DECISION
  CLAIM: TIER SCOPE FIXED BY OWNER. ADVANCED = checkpointing, loading, nexus
    STATIC mode, nexus CAPABILITY mode, plus the config surfaces fenced out of
    intermediate, the View* read family, and ward policies. EXPERT = notch,
    mutation research, codegen, crystallizer loading + saving, synthetic
    modules. `ConduitCloud` moves DOWN to INTERMEDIATE as dynamic-mode basics.
  EVIDENCE: owner directives 2026-08-01 (tier split) and 2026-08-02
    (ConduitCloud placement), this session.
  IMPACT: The prior Objective pulled research sets, diff/impact/foresight and
    drift views into advanced. Those are expert. Objective rewritten above.
  NEXT: Author arcs A-E below.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-08-02T15:43:51Z
  TYPE: MEASURE
  CLAIM: PUBLIC SURFACE COVERAGE. `melder.__all__` exports 65 names. 27 are
    exercised by at least one lesson across all tiers. 38 ARE NEVER USED
    ANYWHERE - 58% of the shipped root is untaught.
  EVIDENCE: scripted sweep of `md.<Name>` across
    `UX_and_AIX_experiences/**/[0-9]*.py` against `src/melder/__init__.py`
    `__all__`, run 2026-08-02.
  IMPACT: The unused set maps almost exactly onto the corrected tier split,
    which is a good sign the split is real and not arbitrary. 13 of the 38 are
    crystallizer/MR names that land in expert with no reshuffling needed.
  NEXT: Advanced arcs, in order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-08-02T15:43:51Z
  TYPE: PLAN
  CLAIM: Advanced authoring plan, five arcs, ~14 lessons, taking the tier from
    6 to ~20 (beginner is 41, intermediate 37).
    ARC A - config surfaces (08-09): AethericFrameConfiguration + SystemState;
      AetherConfiguration + AetherConfigurationBuilder.
    ARC B - nexus & rift (10-14): Nexus, NexusConfiguration, NexusFrameMode,
      Rift, RiftConfiguration, RiftSpace, RiftSpaceType (STATIC then
      CAPABILITY), Workstation.
    ARC C - read surfaces (15-17): FrameViewer, ViewFrame, ViewConduit,
      ViewSpell, ViewMultiFrame.
    ARC D - ward policies (18): Policies. (ConduitCloud removed - intermediate.)
    ARC E - checkpoint / load (19-20): PENDING the split ruling below.
  EVIDENCE: the 38-name unused set; owner approval 2026-08-02.
  IMPACT: Lesson numbering continues from 07. 06 stays RETIRED (owner ruling
    2026-07-26, file parked at `_to_delete/adv06_frame_caching_knob.py`) - do
    not refill the number.
  NEXT: Arc A first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-08-02T15:43:51Z
  TYPE: FACT
  CLAIM: THE "COMPATIBILITY MODE" FINDING WAS A TERMINOLOGY ERROR AND IS NOW
    CLOSED. The 2026-07-26 note recorded that "compatibility mode" is absent
    from `src/melder` and awaited an owner definition. The owner's term is
    CAPABILITY mode, and it exists: `CapabilityRiftSpace` alongside
    `StaticRiftSpace` and `CodegenRiftSpace`, selected by `RiftSpaceType`.
  EVIDENCE:
  - src/melder/nexus/rift/rift_space/capability_rift_space.py
  - src/melder/nexus/rift/rift_space/static_rift_space.py
  - src/melder/nexus/configuration/rift_space_type.py
  IMPACT: No missing feature and no owner definition needed. Arc B teaches it.
    The concept map at `03_advanced/_concept_map.txt` still carries the stale
    wording and needs the same correction.
  NEXT: Fix the concept map when arc B lands.
  REREAD: OPTIONAL
  SCORE_0_TO_10: 7
- DATETIME: 2026-08-02T15:43:51Z
  TYPE: DECISION
  CLAIM: ARC E IS UNBLOCKED - THE COLLISION WAS MINE, NOT THE DESIGN'S. I read
    the tier split as name ownership ("crystallizer names belong to expert")
    when it is DEPTH ownership. OWNER RULING: the crystallizer names ARE the
    public doors, so advanced USES them. Advanced teaches "save a world, get
    it back" through `Crystallizer` / `CrystallizerBootstrap`. Expert teaches
    the machinery behind them - load plans, admission, custody, saving
    features, synthetic modules.
  EVIDENCE: owner ruling 2026-08-02 this session, on the DECISION_REQUEST this
    note replaces.
  IMPACT: A public name is not owned by one tier. Tiers own DEPTH OF USE, and
    the same door can appear at two tiers doing different work. Any future
    tier-scope reasoning must use that rule, not name partitioning - the
    partition reading would have left advanced unable to teach its own
    headline capability.
  NEXT: Arc E authored in plan order after arcs A-D.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-08-02T15:43:51Z
  TYPE: UNKNOWN
  CLAIM: Three exported names have no tier and no ruling: `Scan`,
    `SpellExaminer`, `ProtocolCrafter`.
  EVIDENCE:
  - a Scan lesson existed and was killed:
    `UX_and_AIX_experiences/_to_delete/_gone_05_scan_bind_decorator.py`
  - `SpellExaminer` is a spell introspection surface (read family, arc C
    shaped, but could sit with MR in expert)
  - `ProtocolCrafter` lives under `utilities/ai_native_support_tools/`;
    codegen-adjacent by the expert rule, but it is arguably the most
    AIX-shaped export in the package and may deserve an earlier slot
  IMPACT: Three public names could ship with zero lesson coverage in any tier.
  NEXT: Owner ruling. Not blocking arcs A-D.
  REREAD: REQUIRED
  SCORE_0_TO_10: 6

- DATETIME: 2026-08-02T18:00:00Z
  TYPE: MEASURE
  CLAIM: ARCS A-E AUTHORED. Lessons 08-20 written (06 stays RETIRED), tier
    goes 6 -> 19 authored lesson files. `test_advanced_probes.py` goes 4 rows
    -> 62. Public-root coverage moves from 27/65 names exercised to 48/65 -
    advanced closed 21 names.
    REMAINING 17 UNUSED, and they sort cleanly:
      EXPERT (11): MutationResearch(+Configuration+Builder), ResearchSet,
        LaneState, LaneType, DiffEngine, ExternalPersistenceManager(+Config),
        CrystallizerBootstrap, ProtocolCrafter
      INTERMEDIATE (1): ConduitCloud (owner ruling 2026-08-02)
      UNRULED (2): Scan, SpellExaminer
      NOT LESSON MATERIAL (3): __author__, __description__, __license__
  EVIDENCE: scripted `md.<Name>` sweep over UX_and_AIX_experiences/**/[0-9]*.py
    against `melder.__all__`, run 2026-08-02 before and after authoring.
  IMPACT: The advanced tier's share of the public surface is done. Expert now
    has a fully enumerated target list rather than a vibe.
  NEXT: owner ruling on Scan and SpellExaminer; expert tier opens on the 11.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-08-02T18:00:00Z
  TYPE: FACT
  CLAIM: DEFECT - FRAME-SCOPED VIEW ACCESSORS DECLARE A DEFAULT THAT IS NEVER
    VALID. `FrameViewer.get_view_frame`, `get_view_conduit`, `get_view_spell`,
    `describe_visible_surface` and `describe_missing_surface` are all typed
    `frame_name: Optional[str] = None` and then reject None UNCONDITIONALLY
    with `ValueError: frame_name is required.` A reader who trusts the
    signature calls get_view_frame() and is refused for using the documented
    default.
  EVIDENCE:
  - src/melder/nexus/rift/frame_viewer/frame_viewer.py:2204 (call site)
  - src/melder/nexus/rift/frame_viewer/frame_viewer.py:2480 (unconditional raise)
  - owner 3.14t run 2026-08-02: 11 of 16 failures traced to this single cause
  IMPACT: This is the highest-yield finding of the tier. It cost arc C a full
    rewrite and it will cost every user the same confusion once. The fix is
    either `frame_name: str` with no default, or routing None somewhere.
    NOTE: get_view_multiframe() is HOST-SCOPED and correctly needs no name -
    the split itself is good design, only the signature is wrong.
  NEXT: owner decision - tighten the signature or restore default routing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-08-02T18:00:00Z
  TYPE: FACT
  CLAIM: TWO DOC DRIFTS, same shape as the known false `with_defaults()`
    docstring at spellbook_configuration.py:1062-1064.
    (a) `RiftSpaceType` documents a fourth member - "dynamic: Legacy alias for
        codegen" - that DOES NOT EXIST. No member, no `_missing_` handler, so
        RiftSpaceType("dynamic") raises.
    (b) `Workstation.describe_bindings` documents "a FOUR-KEY summary...
        always with all four keys present, so callers can index" and RETURNS
        FIVE - it also emits `target_store`. This one explicitly invites
        callers to rely on the count.
  EVIDENCE:
  - src/melder/nexus/configuration/rift_space_type.py:22,44,55
  - src/melder/nexus/rift/rift_space/workstation.py:416-450
  IMPACT: Three known drifts of identical shape now. Worth a sweep rather than
    three point fixes - a docstring that states a count or a member list is a
    testable claim and nothing currently tests them.
  NEXT: Both pinned in test_advanced_probes; each row asserts BOTH sides so it
    goes red when either the code or the prose is corrected.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-08-02T18:00:00Z
  TYPE: FACT
  CLAIM: INIT-SURFACE GAPS FOUND WHILE AUTHORING, all pinned as probes.
    (a) `md.AethericFrameConfiguration` is exported and CANNOT BE INSTALLED
        from the public root. Spellbook.__init__ takes a SpellbookConfiguration;
        every path to the live posture is private; configure_aether_frame
        reaches 2 of 15 knobs.
    (b) AR TARGETING IS UNREACHABLE. Nexus raises "AR requires rift_enabled on
        target frame" (nexus.py:2957) and nothing public sets rift_enabled.
        Rifts, rooms and workstations ARE reachable - only AR is not.
    (c) WARD POLICY IS WRITE-ONLY. `set_new_policy` is public; there is no
        public reader. Authority you can change and cannot audit.
    (d) `Conduit.set_new_policy` is annotated `policy: str` but the ward
        accepts `str | Policies` - the hint under-sells the code, and the
        exported enum works.
  EVIDENCE: lessons 08, 11, 18 + their probe rows.
  IMPACT: Four concrete items for the init/public-surface program, each with a
    test that flips when the gap closes.
  NEXT: owner triage.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-08-02T18:00:00Z
  TYPE: MEASURE
  CLAIM: FIRST OWNER RUN: 16 failures, FOUR root causes, three of them mine.
    MINE: (1) `Crystallizer.is_activated` is a @property, called as a method.
    (2) weak-binding probe passed a temporary with no strong reference, so the
    weakref died before assertion - correct melder behaviour, bad test.
    (3) I claimed the room kinds override ONE property; they override TWO.
    NOT MINE: (4) the frame_name default defect above, which accounted for 11
    of the 16.
  EVIDENCE: owner 3.14t run 2026-08-02, pytest_examples --last-failed.
  IMPACT: Correction (3) IMPROVED the curriculum. StaticRiftSpace overrides
    `command_system` AND `frame_viewer`, so the room kind narrows WHAT YOU MAY
    DO and WHAT YOU MAY SEE together, both by handing over a different class
    rather than guarding a shared one. Lessons 12 and 13 now teach the pair.
  NEXT: re-run; all 16 addressed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-08-02T18:00:00Z
  TYPE: FACT
  CLAIM: TWO CURRICULUM THROUGH-LINES emerged from the source rather than from
    a plan, and are now taught forward from the concept map.
    (1) PRESENCE IS NEVER LIVENESS. Every subsystem splits it into two bits:
        frozen/activated (09), is_configured/is_enabled (10),
        is_registered/is_active (11), and the crystallizer pair (19).
    (2) MELDER NEVER SUBSTITUTES. validate() raises rather than returning
        False (08); static has no meld() rather than refusing it (13); weak
        binding raises rather than degrading to strong (14); the blind-spot
        report refuses rather than returning an empty dict (17); a policy
        change that cannot be honestly applied is refused, never partial (18).
        THE ONE DELIBERATE EXCEPTION is flush_checkpoint's remote leg, which
        is lenient BY CONTRACT and says so (20).
  EVIDENCE: UX_and_AIX_experiences/03_advanced/_concept_map.txt
  IMPACT: These give the tier a spine and give a reader a predictive rule for
    objects they have not met. Worth carrying into expert.
  REREAD: OPTIONAL
  SCORE_0_TO_10: 7
- DATETIME: 2026-08-02T18:00:00Z
  TYPE: MEASURE
  CLAIM: CONFIGURATION DIVERGENCE, MEASURED. Nine public configuration objects
    carry FIVE different terminator sets. Subsystem activation is 3-to-1:
    Aether, Crystallizer and MutationResearch all require the CALLER to
    activate the configuration before the subsystem; NEXUS alone does it
    inside enable(). Owner note: "activate means something specific" - the
    divergence is Nexus, not the verb.
  EVIDENCE: _concept_map.txt tables; probe
    test_probe_caller_driven_activation_is_the_house_rule_three_to_one.
  IMPACT: Hard evidence for EPIC-2026-08-01-configuration-surface-uniformity,
    collected as a by-product of teaching rather than as a separate
    investigation.
  NEXT: feed into that epic when it reopens.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-02T18:20:00Z
  TYPE: DECISION
  CLAIM: THE LAST TWO UNRULED PUBLIC NAMES ARE RULED. Owner 2026-08-02:
    `Scan` -> INTERMEDIATE. `SpellExaminer` -> INTERNAL, "not for users or
    agents" - NO TIER, recorded as a REJECTED CURATION CALL per this epic's
    exit gate.
  EVIDENCE: owner directive this session.
  IMPACT: Every name in `melder.__all__` now has a tier or a documented
    reason for having none. The advanced tier's contribution to the
    init/public-surface program is complete on the classification axis.
    Note for the intermediate epic: a Scan lesson EXISTED and was killed
    (`_to_delete/_gone_05_scan_bind_decorator.py`) - it returns at
    intermediate, and whoever picks it up should read why it died first.
  NEXT: intermediate epic gains Scan and ConduitCloud.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-08-02T18:40:00Z
  TYPE: DECISION
  CLAIM: THE SPELLEXAMINER CONFLICT BELOW IS RESOLVED AND EXECUTED. Owner
    ruling 2026-08-02: remove it from `__all__`. Done, following the existing
    counter-example law rather than half-removing it:
      - `src/melder/__init__.py` - import AND `__all__` entry removed
        (`__all__` is now 64 names, py_compile clean)
      - `tests/unit/melder/test_package_public_surface.py` - the identity
        assertion dropped, and "SpellExaminer" added to the curated-exclusions
        tuple in `test_internal_depths_stay_off_the_root` beside ConduitWard
        and Meld, with the reasoning inline
      - the advanced probe inverted to pin the REMOVAL
    Removing only the `__all__` entry would have left `melder.SpellExaminer`
    still resolving - advertised-as-gone but reachable - and that test asserts
    exclusions are absent from `__all__` AND the namespace.
  EVIDENCE: verified after edit - zero remaining references to
    `md.SpellExaminer` / `melder.SpellExaminer` outside `src/melder/`.
  IMPACT: THE REASON MATTERS MORE THAN THE REMOVAL, and it is recorded at the
    exclusion site: this was not an internal helper that leaked. It was
    exported WITH a working extension point - `register_profile_builder(...)`
    and "the registry remains open for explicit extension" - that nobody could
    reach, because the only live instance is Bind's private
    `self._spell_examiner`. Public class, public extension API, private
    instance: half a feature. If that extension point is ever wanted for real,
    the fix is NOT to re-export the class - it is to expose the examiner on
    `Bind`.
  NEXT: NOTE FOR THE OWNER - `tests/unit/melder/test_package_public_surface.py`
    is not this epic's suite. The edit is minimal and follows that file's own
    convention, but whoever owns it should see it rather than discover it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-08-02T18:20:00Z
  TYPE: CONFLICT
  CLAIM: [RESOLVED 2026-08-02 - see the DECISION above.] `SpellExaminer` IS
    RULED INTERNAL BUT IS STILL PUBLIC, AND THE CLASS ITSELF SAYS NOTHING. It is exported from `melder.__all__`, and unlike
    `Scan` - which carries `AGENT_ACCESS: internal` and `AGENT_ACCESS: public`
    markers on its surfaces - `SpellExaminer` declares NO access marker of any
    kind. So it is currently neither public nor internal by its own account,
    while sitting in the public root.
  EVIDENCE:
  - src/melder/__init__.py `__all__` contains "SpellExaminer"
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/spell_examiner.py
    - no AGENT_ACCESS / Internal / Public API marker in the class docstring
  - src/melder/aether/spellbook/bind/scan.py:101,277 - Scan DOES mark itself
  IMPACT: An unmarked name in `__all__` is the worst of both worlds: agents
    and users will find it by enumeration and have nothing telling them not
    to use it. The owner ruling exists only in a ticket, not in the code.
  NEXT: OWNER DECISION - either mark it internal and drop it from `__all__`,
    or mark it public and give it a tier. Pinned by
    test_probe_spell_examiner_is_exported_but_carries_no_access_marker, which
    goes red the moment either half is acted on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-02T20:00:00Z
  TYPE: DECISION
  CLAIM: THE TIER WAS RENUMBERED 02..20 -> 01..18, SEQUENTIAL WITH NO GAPS.
    EVERY LESSON NUMBER IN THE NOTES ABOVE THIS LINE IS OLD NUMBERING. Read
    them through this map:
      02->01 03->02 04->03 05->04 07->05 08->06 09->07 10->08 11->09
      12->10 13->11 14->12 15->13 16->14 17->15 18->16 19->17 20->18
    The gaps existed because 01 was DELETED (owner 2026-08-02, cluster stub -
    intermediate teaches clusters) and 06 was RETIRED (owner 2026-07-26,
    turn-off-the-cache lesson). Both numbers are now RECLAIMED by real
    lessons; the retired titles live in a history block in
    `03_advanced/_concept_map.txt`, not in the numbered inventory.
    ARC BOUNDARIES IN NEW NUMBERS: A=06-07, B=08-12, C=13-15, D=16, E=17-18.
  EVIDENCE: owner directive 2026-08-02 ("make sure the numbering is correct").
    Verified after the change: 18 files sequential 01-18, every
    `TIER: advanced (NN)` header matches its filename, ZERO dangling
    cross-references across lessons + probes + concept map, no duplicate
    inventory entries.
  IMPACT: TWO CLASSES OF REFERENCE ALMOST SURVIVED THE REMAP AND BOTH WERE
    CAUGHT ONLY BY CHECKING, NOT BY REASONING:
      (1) my remap regex was LOWERCASE-ONLY, so ~60 capital "Lesson NN"
          references in probe docstrings went untouched;
      (2) ranges like "lessons 19-20" had only the FIRST number moved,
          leaving "lessons 17-20".
    Anyone repeating a mechanical sweep over this corpus should assume the
    same shape of miss and verify by enumeration afterwards.
  NEXT: historical notes above are left AS WRITTEN - rewriting them would
    destroy the record of when things were learned. Use the map.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-02T20:45:00Z
  TYPE: DECISION
  CLAIM: RESOLVED BY OWNER 2026-08-02 - THE MARKERS ARE WRONG, NOT THE
    LESSONS. Owner ruling: "anything that shows as a public method is not
    internal, agent fucked it up." So the `Internal` markers on the
    Nexus/Rift method surface are a DOCUMENTATION DEFECT introduced by a
    prior agent, not a statement of intent.
  IMPACT: ARCS B AND C STAND AS AUTHORED - no lesson changes. Lessons 09-15
    teach a genuinely public surface; the mislabelling is the bug.
    THIS IS NOW A SOURCE DEFECT FOR THE OWNER'S PROGRAM, and it is larger
    than the three docstring drifts already recorded: 55 methods across two
    files carry a marker that contradicts their own class's public export.
    An agent reading `Internal` on `Nexus.create_rift` will correctly refuse
    to use the documented way to create a rift - which is exactly what
    happened to ME during this audit, and I nearly withdrew eight correct
    lessons over it.
    SCOPE OF THE FIX (not performed - source work outside this epic's lane):
      nexus/nexus.py       40 methods marked `Internal`, 0 marked `Public API`
      nexus/rift/rift.py   15 methods marked `Internal`, 0 marked `Public API`
    Reference for what correct looks like: aether/conduit/conduit.py carries
    66 `Public API` markers against 40 `Internal`.
  NEXT: hand to whoever owns nexus/. A marker sweep, not a code change.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-08-02T20:30:00Z
  TYPE: FACT
  CLAIM: [RESOLVED - see the DECISION above. Retained for the evidence.]
    THE ENTIRE NEXUS/RIFT METHOD SURFACE IS MARKED INTERNAL OR IS
    UNMARKED. NOT ONE METHOD ON EITHER CLASS CARRIES A `Public API` MARKER.
    Measured:
      nexus/nexus.py           40 `Internal`, 0 `Public API`
      nexus/rift/rift.py       15 `Internal`, 0 `Public API`
    versus surfaces known to be user-facing:
      aether/spellbook/spellbook.py   96 `Internal`, 24 `Public API`
      aether/conduit/conduit.py       40 `Internal`, 66 `Public API`
    So the convention EXISTS and is applied consistently elsewhere. Nexus
    and Rift simply have none of it. `Nexus.create_rift` states `Internal`
    outright; `Rift.mark_active` / `mark_inactive` / `mark_registered` /
    `list_assigned_frame_names` / `create_frame_link` are unmarked or
    Internal; `Nexus.has_rift` is Internal.
  EVIDENCE: marker census run 2026-08-02 over the four files above.
  IMPACT: ARCS B AND C - EIGHT LESSONS, 09 THROUGH 15 IN THE NEW NUMBERING -
    ARE BUILT ENTIRELY ON THAT SURFACE. create_rift, mark_active, has_rift
    and list_assigned_frame_names appear in nearly every one. This is the
    SAME CLASS OF ERROR as the withdrawn Scan lesson (owner: "scan is not
    meant to be user surfaced"), except it is 8 lessons rather than 1.
    I CANNOT RESOLVE THIS FROM THE CODE. Two readings are equally
    consistent with what is there:
      (a) the subsystem is genuinely internal-by-method and arcs B/C teach
          things users should not call - they need withdrawal or rewriting;
      (b) the subsystem is intended as public and the marker pass simply
          has not been done on it - in which case the LESSONS are fine and
          the MARKERS are the gap.
    The classes themselves ARE exported from `melder.__all__` (Nexus, Rift,
    RiftSpace, RiftSpaceType, RiftConfiguration, Workstation, FrameViewer,
    ViewFrame/Conduit/Spell/MultiFrame), which weakly favours (b) - but
    SpellExaminer and Scan were also exported and both turned out to be (a).
    Export is not evidence of intent in this codebase.
  NEXT: OWNER RULING REQUIRED before arcs B and C can be called done. I have
    NOT deleted or altered them pending that call - the last time I acted on
    my own reading of an access question I authored an anti-pattern.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-02T21:00:00Z
  TYPE: MEASURE
  CLAIM: TIER CLOSED OUT AT 19 LESSONS. A stale-plan audit found the concept
    map's PLANNED section still listing every finished arc as unbuilt, plus
    ONE genuinely unbuilt item that belonged here: the wildcard/broadcast
    override grammar. Authored as lesson 19 with six probe rows (advanced
    probes now 70). Public-root coverage 49/63; the remaining 14 are 11
    expert names and 3 dunders.
  EVIDENCE: 03_advanced/19_wildcard_and_broadcast_overrides.py; probes
    test_probe_unique_wildcard_resolves_a_single_socket,
    _refuses_when_it_matches_twice, _broadcast_hits_every_match,
    _broadcast_refuses_when_it_matches_nothing,
    _exact_path_beats_broadcast_on_overlap,
    _many_keeps_override_blast_radius_inside_the_call.
  IMPACT: Lesson 01 taught only the PATH form. The other two targeting
    forms - `*param` (exactly one match REQUIRED) and `**param` (at least
    one REQUIRED) - are the never-substitute rule applied to TARGETING, and
    melder's own reasoning is the best line in the lesson: a wildcard that
    silently matched the wrong count "would apply the caller's intent to the
    wrong object or to nothing at all, and BOTH FAIL INVISIBLY AT RUNTIME".
    `SpellOverrider` is AGENT_ACCESS: internal ("users supply the override
    PAYLOAD, never this object") so the lesson teaches the DICT and never
    touches the class - the access marker was checked BEFORE authoring this
    time, which is the process fix from the withdrawn Scan lesson.
  NEXT: nothing further authorable. The tier is unrun.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-08-02T21:00:00Z
  TYPE: FACT
  CLAIM: REGRESSION I INTRODUCED AND FIXED - the enum-to-string conversion
    removed the LAST `md.SystemState` reference in the corpus, dropping a
    public exported name to ZERO lesson coverage. Restored in lesson 06,
    where it is genuinely instructive: the property hands back a
    `SystemState` member rather than the string that was passed, because
    normalization happens at the door.
  EVIDENCE: coverage sweep before/after; 03_advanced/06_frame_posture_object.py
  IMPACT: A mechanical sweep can silently un-teach a public name. Any future
    conversion of this kind should re-run the coverage sweep as part of the
    change, not after someone asks.
  REREAD: OPTIONAL
  SCORE_0_TO_10: 6

- DATETIME: 2026-08-02T21:30:00Z
  TYPE: CONFLICT
  CLAIM: A LIVE EPIC IN ANOTHER LANE NAMES ONE OF THIS TIER'S LESSONS AS
    COLLATERAL, AND THAT LESSON ALSO HAD A REAL BUG.
    `attention_board.md:121` records EPIC-2026-08-02-process-wide-spell-id-
    uniqueness with the owner ruling "one spell_id means one spell,
    PROCESS-WIDE - which deliberately retires the per-frame multi-tenancy
    that 03_advanced/02_frames_as_worlds.py teaches."
    INVESTIGATING THAT TURNED UP A SEPARATE, OLDER DEFECT IN THE LESSON: it
    named the SAME frame twice - `aetheric_frame="tenant-a"` on BOTH books -
    while its prose claimed two worlds. It only ever passed because
    duplicate spell_ids across two Spellbooks on ONE frame were not caught.
    S1 of that epic landed `Spellbook._spell_id_integrity_checker`, which
    refuses exactly that at conjure. The lesson was about to go red, and
    for a correct reason.
  EVIDENCE:
  - src/melder/aether/aether_configuration.py:108 (process_wide_unique_spell_ids
    default True) and :548 (with_ setter)
  - src/melder/aether/spellbook/spellbook.py:2587 (the checker), :6407 (call site)
  - context_compass/attention_board.md:121
  IMPACT: FIXED - the frames now differ ("tenant-a" / "tenant-b") and the
    lesson teaches what it always claimed to. BUT NOTE THE SCOPE CORRECTION:
    the checker AS LANDED IS PER-FRAME, not process-wide - its own contract
    says it refuses "when any spell_id this Spellbook owns is already
    registered IN THE AETHERIC FRAME". So per-frame isolation still holds
    today and the lesson is currently correct. S2 of that epic ("unified
    set", genuinely process-wide) is READY AND UNASSIGNED; landing it WOULD
    retire what this lesson teaches. The board's "PROCESS-WIDE" phrasing
    describes the RULING, not the code that has shipped so far.
    This tier's own probe (test_probe_frames_isolate_names_and_singletons)
    already used two DIFFERENT frames and is unaffected.
  NEXT: whoever picks up S2 must retire or rewrite
    `03_advanced/02_frames_as_worlds.py` in the same change. A pointer to
    that obligation is now in the lesson's own docstring so it cannot be
    missed by someone reading only the file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## State Transition Event - 2026-08-02T21:30:00Z
- from_state: pending
- to_state: done_pending_owner_run
- transition_reason: all five arcs authored (19 lessons, 01-19 sequential),
  70 advanced probe rows, public-root coverage 49/63, static audit clean on
  method names / exported names / keyword arguments. Nothing further is
  authorable without execution. Moving to `done_pending_owner_run` rather
  than `done` because the tier has NEVER been run green in its current
  shape: every advanced file was rewritten twice after the last real signal
  (enum-to-string conversion, then the renumber). Last measured result was
  61/64 advanced and 26/27 intermediate.

## Context / Handoff Summary
Method: every example imports melder as md ONLY - a deep-path import in an example
IS the finding. Examples are runnable scripts with honest asserts; they ride the
owner's 3.14t runs (device VM cannot import the runtime).

STATE AT 2026-08-02 (third update this session): ARCS A-E ALL AUTHORED AND
RENUMBERED. 18 lessons, SEQUENTIAL 01-18, no gaps. Advanced probes at 64
rows, intermediate at 27. Public-root coverage 48/63 (`__all__` shrank from
65 to 63 - SpellExaminer and Scan were both curated off this session).

NUMBERING NOTE: every lesson number in the notes ABOVE the renumber DECISION
is OLD numbering. The mapping is in that note. Arc boundaries in the NEW
numbers are A=06-07, B=08-12, C=13-15, D=16, E=17-18.

DO NOT TREAT THE TIER AS GREEN. The first owner run gave 16 failures across
four root causes (three mine, one the frame_name defect); those were fixed,
then EVERY advanced file was rewritten twice more - once converting enums to
strings, once renumbering. Nothing has been executed since. The last good
signal was 61/64 advanced and 26/27 intermediate.

THE ONE THING TO ACT ON: the frame_name defect. Five FrameViewer reads declare
`frame_name: Optional[str] = None` and reject None unconditionally. It caused
11 of 16 failures and forced arc C to map its surfaces off the exported TYPES
instead of live instances. Arc C is honest as written, but it teaches less
than it could until a frame can actually be assigned from the public root.

STILL OPEN: owner ruling on `Scan` and `SpellExaminer` (the only two unruled
public names). ConduitCloud belongs to INTERMEDIATE, not here. Everything else
unused is expert material and is now enumerated in the MEASURE note above.

STATE AT 2026-08-02: 7 lesson slots used, 6 authored (06 is RETIRED, not
missing - do not refill it). Tier scope was corrected by the owner on
2026-08-01/02 and the Objective above was rewritten to match; the prior
objective had mutation-research material sitting in advanced.

The plan is the PLAN note above: arcs A-E, ~14 lessons, numbering from 08.
Arcs A-D are unblocked. ARC E IS BLOCKED on the DECISION_REQUEST - checkpoint
and load have no public door outside the crystallizer names that were assigned
to expert, so someone has to rule on whether advanced gets the simple
`CrystallizerBootstrap` door or gives the arc up entirely.

`ConduitCloud` is NOT part of this tier as of 2026-08-02 - it belongs to
intermediate as dynamic-mode basics.
