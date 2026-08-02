# Epic: UX/AIX Advanced experience exploration

## Metadata
- Epic ID: EPIC-2026-07-19-ux-aix-advanced
- Status: pending
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

## Context / Handoff Summary
Method: every example imports melder as md ONLY - a deep-path import in an example
IS the finding. Examples are runnable scripts with honest asserts; they ride the
owner's 3.14t runs (device VM cannot import the runtime).

STATE AT 2026-08-02 (second update this session): ARCS A-E ALL AUTHORED.
Lessons 08-20 exist, probes are at 62 rows, public-root coverage is 48/65.
First owner run produced 16 failures across four root causes; all addressed
and awaiting a re-run. Do NOT treat the tier as green until that re-run lands.

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
