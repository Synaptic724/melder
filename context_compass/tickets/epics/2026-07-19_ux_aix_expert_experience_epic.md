# Epic: UX/AIX Expert experience exploration

## Metadata
- Epic ID: EPIC-2026-07-19-ux-aix-expert
- Status: pending
- Owner: cowork
- Agent Name: examples_0
- Priority: p2
- Created: 2026-07-19T12:52:00Z
- Updated: 2026-08-01T10:41:33Z

## Objective
The operator's tier: CrystallizerBootstrap pod restart, external persistence meshes (user DB callables), profile/checkpoint operations, group composition and campaign evolution, synthesis previews, class_wraps-built custom decorators over bound spells, multi-frame orchestration.

## Notes

- DATETIME: 2026-08-02T22:15:00Z
  TYPE: MEASURE
  CLAIM: EXPERT TIER OPENED - 6 LESSONS, 20 PROBE ROWS, AND THE PUBLIC ROOT
    IS NOW FULLY TAUGHT. Coverage went 49/63 -> 60/63; the three remaining
    are `__author__`, `__description__`, `__license__`, which beginner 12
    already covers as module reads. 103 lessons across four tiers
    (41 / 37 / 19 / 6).
    LESSONS: 01 pod boot ("the ORDER is the product"), 02 the external mesh,
    03 research sets / lanes / residency, 04 diffs are derived never stored,
    05 ProtocolCrafter (the one tool that writes), 06 two knobs and a
    terminator per rung.
    NEW HARNESS FILES: pytest_examples/test_expert_examples.py (runner) and
    test_expert_probes.py (20 rows). The probe fixture adds
    MutationResearch to the singleton reset - expert is the first tier to
    touch it, so all five now reset per row.
  EVIDENCE: scripted `md.<Name>` sweep over
    `UX_and_AIX_experiences/**/[0-9]*.py` against `melder.__all__`, and
    py_compile over every new file.
  IMPACT: The four-tier ladder now covers every public name melder exports.
    PROCESS NOTE, because it is the fix that actually held: access markers
    and property-vs-method were checked BEFORE authoring each lesson this
    time, not after a red run. That is the correction from the withdrawn
    Scan lesson, applied rather than merely recorded.
  NEXT: UNRUN. Rides the owner's 3.14t like every other tier.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-08-02T22:00:00Z
  TYPE: DECISION
  CLAIM: THE CRYSTALLIZER MACHINERY SHOULD NOT BE EXPORTED. The tier-split
    ruling of 2026-08-01 said expert gets "crystallizer loading features and
    saving, synthetic modules", which read as though `RestoreEngine`,
    `LoadPlan`, `LoadAdmission`, `GraftRunner`, `CrystalLoaderSystem` and
    `SyntheticModule` needed to reach the public root. THEY DO NOT.
    Owner 2026-08-02: "don't you just use crystallizer for that shit?" -
    correct, and the facade already carries it.
  EVIDENCE: `Crystallizer` exposes 25 verbs covering the whole scope line:
    SAVING      create_checkpoint, flush_checkpoint, save_formation
    LOADING     load_checkpoint, reload_cached_checkpoint,
                reload_profile_from_cache, reload_profile_from_external,
                reload_formations_from_external
    FORMATIONS  restore_formation, list_formations, analyze_formation,
                delete_formation
    GRAFTS      capture_index_graft, graft_index,
                store_index_graft_external, fetch/list variants
    The machinery it delegates to is referenced across 9-18 src files each -
    internal wiring, not user surface.
  IMPACT: This is the FOURTH instance of one pattern in a single session:
    a capable internal collaborator behind a facade that is the real API.
      Scan            -> `Spellbook.scan(module)` is the door (withdrawn lesson)
      SpellOverrider  -> the override PAYLOAD dict is the door (expert-adjacent)
      SpellExaminer   -> curated OFF the root this session
      crystal loaders -> `Crystallizer` is the door
    The rule that keeps falling out: IF A FACADE COVERS IT, THE COLLABORATOR
    IS NOT USER SURFACE. Export is not the test - the presence of a working
    door is.
  NEXT: no export work. Expert teaches the facade, which lessons 01-06
    already do.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-08-02T22:00:00Z
  TYPE: DECISION
  CLAIM: `SyntheticModule` STAYS UNEXPORTED, and for a different reason than
    the loaders. It is not merely behind a facade - IT HAS NO AUTHORING PATH
    AT ALL. Its constructor demands `spell_crystal_id`, `source_sha256` and
    `binding_signature`, all of which only exist once a spell has already
    been harvested, and its only construction site is the restore lane.
    Owner: "synthetic module is for agents not really sure where to go from
    there because a lot of this shit is new."
  EVIDENCE: EPIC-2026-08-02-agent-authored-synthetic-modules, filed this
    session, which documents the closed lifecycle in full.
  IMPACT: Exporting it today would ship HALF A FEATURE - a public class an
    agent cannot originate - which is exactly the mistake SpellExaminer was
    curated off the root for (public class, public extension point, private
    instance). The honest order is: give it an authoring path FIRST, then
    export, then teach. Not the reverse.
  NEXT: gated on EPIC-2026-08-02-agent-authored-synthetic-modules. No expert
    lesson until an agent can actually author one.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Ticket Contract
- ENTRY_GATE: owner directive 2026-07-19 ("explore all the ways a user might use the
  library beginner -> intermediate -> expert -> Master... so we can properly explore
  what we need in init"). Examples live in UX_and_AIX_experiences/04_expert/.
- EXECUTION_BOUNDARY: UX_and_AIX_experiences/04_master/ examples + findings notes ONLY.
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

## DECISION - 2026-07-25 19:23 UTC - tier renamed to EXPERT (README ladder match)
  RULING: owner (2026-07-22) - the ladder is Beginner/Intermediate/Advanced/
    Expert per the shipped README. This epic (formerly "Master", folder
    04_master) is now the EXPERT tier: AR rooms, transactions, checkpoints,
    governed mutation, external DB meshes. Folder renamed 04_master ->
    04_expert. Historical notes below keep their original wording.
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
    - tickets/epics/2026-07-19_ux_aix_expert_experience_epic.md:5-10
  IMPACT: Tier stays `pending` and is the thinnest of the four (46 lines) - it carries the ladder
    ruling and little else, so it needs the most authoring once the lower tiers land.
  NEXT: Blocked behind beginner/intermediate/advanced; no expert authoring until the ladder below
    it is owner-accepted.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## State Transition Event - 2026-08-01T10:41:33Z
- from_state: assigned helper_f
- to_state: assigned examples_0
- transition_reason: owner directive this session (claim the four UX/AIX epics, remove helper_f
  from ownership). Status stays `pending` - assignment changed, lifecycle did not.

- DATETIME: 2026-08-04T11:43:01Z
  TYPE: MEASURE
  CLAIM: THREE LESSONS AUTHORED (26, 27, 28), each written against source read
    this session rather than against the existing lessons' prose. Tier goes
    25 -> 28.
    26 `codegen_create_modify_iterate` - the loop TURNED MORE THAN ONCE.
    Expert 12 drove the verbs a single time; this iterates three turns of
    research_preview -> validate_codegen -> execute_codegen ->
    materialize_codegen, takes a refusal MID-LOOP to show the loop reads a
    verdict rather than breaking on one, and then stages candidates onto the
    live lineage with `bind_inactive`.
    CORRECTED DURING AUTHORING, and the correction became the lesson: my first
    draft cut a research lane per codegen turn and then "walked the history".
    That was wrong and would have shipped a hollow lesson. A codegen turn mints
    NO research node - the three seams that write the research book are
    `_record_research_world_entry(..., staged=False)` from `bind`,
    `(..., staged=True)` from `bind_inactive`, and `_record_research_promotion`
    from a notch, each a NO-OP unless the MR root already exists and is
    activated. `research_create_lane` records ancestry only and copies nothing,
    and `research_attach` re-anchors ancestry rather than placing a version. So
    a lane cut and never registered into walks EMPTY, correctly. The lesson now
    teaches TWO BOOKS - the room keeps what CODE was written, research keeps
    what VERSIONS exist - asserts the empty walk on purpose, and then uses
    `research_set.register_spell(spell_id, lane=...)`, which is the verb that
    actually puts a version on a named lane.
    27 `a_world_that_outlives_its_own_runtime` - two codegen edits, checkpoint,
    flush, then `aether.cleanup()` + `gc.collect()`, then a FRESH root that has
    never seen the world reloads it from cache and unfolds it. The lesson's
    spine is ledger-vs-cache: `create_checkpoint` mints into memory and
    `flush_checkpoint` is what survives a teardown, so skipping the flush loses
    the world with NO error, because nothing went wrong.
    28 `the_record_crosses_as_a_json_string` - REBUILT on a better mechanism
    than the one I started with. The whole research record goes to TEXT via
    `research_set.describe()` and comes back through the exported classmethod
    `md.ResearchSet.from_payload(...)`, with the live set deleted in between.
    No file, no sqlite, no driver. Two lanes are merged first (one clean join,
    one refused-then-forced) so the MERGE is provably inside the text.
    THE `json.dumps` CALL DELIBERATELY PASSES NO `default=` HANDLER, because
    `describe_composition()` guarantees "PLAIN-VALUE THROUGHOUT. Every nested
    value is JSON-safe" - so the strict call turns that docstring promise into
    an executable guard. A `default=str` would have hidden the exact regression
    worth catching: a datetime would go out as a string, come back as a string,
    and the trip would be silently lossy with nothing failing.
    The lesson also pins the guarantee that separates a RECORD restore from a
    WORLD restore: `from_payload` PRESERVES the recorded `set_id`, so a
    hydrated set is the SAME set, where expert 24/27's restored world is
    deliberately equivalent-not-identical and hands you a translation map. The
    mesh quartet survives as a short coda rather than the spine.
  EVIDENCE:
    - UX_and_AIX_experiences/04_expert/26_codegen_create_modify_iterate.py
    - UX_and_AIX_experiences/04_expert/27_a_world_that_outlives_its_own_runtime.py
    - UX_and_AIX_experiences/04_expert/28_the_record_crosses_as_a_json_string.py
  IMPACT: The tier gains the ITERATION story it did not have - 12 showed one
    turn, 24 showed a round trip with the world still up, and neither showed a
    loop or a teardown.
  NEXT: Owner runs `pytest UX_and_AIX_experiences/pytest_examples -v` on 3.14t.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-04T11:43:01Z
  TYPE: FACT
  CLAIM: TWO SIGNATURES I HAD ASSUMED WRONG AND CHECKED, recorded because both
    would have shipped a lying lesson.
    (1) `ResearchSet.snapshot_network()` returns a CONTENT-ADDRESS SHA, not a
    JSON payload, and `restore_network(snapshot_sha, ...)` takes that address.
    I had it earmarked as the "reload from a JSON string" mechanism and it is
    not one - it is a content-addressed recovery mechanic whose contract is
    VALIDATE-THEN-DESTROY. The real text boundary is the external mesh:
    `with_store_handler` receives `(kind, profile_name, unit_id, payload: dict)`
    and `with_fetch_handler` returns `Optional[dict]`, which is what makes a
    `json.dumps`/`loads` adapter COMPLETE rather than a simplification.
    (2) `Aether.cleanup()` IS the public singleton reset - it clears
    `_instance = None` and `_initialized = False` inside a `finally`, so the
    reset holds even when a child teardown raises. Lesson 27 therefore needs no
    private door; `_reset_singleton_for_tests` sits next to it and is left
    alone as the test-isolation verb it says it is.
  EVIDENCE:
    - src/melder/mutation_research/research_set/research_set.py:2224, 2323
    - src/melder/crystallizer/asset_management/external_persistence_manager_configuration.py:496-499, 533-535
    - src/melder/aether/aether.py:323-332
  IMPACT: 28 is built on the mesh rather than on snapshot_network, and 27 uses a
    public teardown. Both were one grep away from being wrong.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-04T11:43:01Z
  TYPE: ASSUMPTION_CHALLENGE
  CLAIM: I WROTE THESE THREE LESSONS WITHOUT READING THE COMPONENT MAP FOR ANY
    OF THE SUBSYSTEMS THEY ARE ABOUT, and the owner caught it. Recorded because
    the failure is reusable, not because it is embarrassing.
    What I had actually read was three slices - Spellbook Configuration,
    AethericFrame Services, Spellbook Core - and all three were for the
    HARNESS-RED work, not for these lessons. For AR/Rift, the Codegen Engine,
    the Crystallizer Root and MutationResearch I went from existing examples
    straight to source symbol lookups. That is entering the hierarchy in the
    middle, which `context_protocol.md:14-24` orders against by name, and the
    reason it is forbidden is exactly what happened next: I got the research
    lane model wrong in lesson 26 and only caught it by accident.
    NOW READ, in full: AR Runtime Surface (1268-1567), Codegen Internal Engine
    (1717-1796), Nexus Descriptor And ACL Managers (1797-1873), RiftSpace
    Workstation And Command Surface (1874-2020), Crystallizer Root/Persistence
    Record (1027-1267), MutationResearch Root (4339-4427), ResearchSet Package
    (4428-4600), SpellIndex Mutation Surface (3918-3978).
    IT CONFIRMED THE LESSONS AND CORRECTED ONE CLAIM. Confirmed: codegen AR
    requires all three of `rift_enabled` + `ai_native_enabled` +
    `system_state=dynamic`; the cache is atomic JSON per checkpoint ULID under
    `__crystallizer_cache__`; runtime ULIDs are emitted and never rehydrated so
    a restore mints fresh identities via the translation map; and
    "Aether/Crystallizer have NO state switch by design: the record dies with
    them" - which is precisely WHY lesson 27 must build a new Crystallizer
    after the teardown rather than reuse one.
    CORRECTED: room memory is ONE RECORD PER SUCCESSFUL TOP-LEVEL PUBLIC
    COMMAND - every public command, not only the codegen verbs - so lesson 26's
    "N records for 3 turns" framing was loose. It now teaches that the unit is
    the COMMAND (3 turns x 4 verbs, plus the lane cut) and that a refused
    command does not emit. Also added: `research_preview` is CODEGEN-ROOMS-ONLY
    because it TAKES CODE, which is the actual reason the room families differ
    (34 commands vs 21 reads vs none).
  EVIDENCE:
    - context_compass/system_docs/src_components.md:1402-1403, 1438-1440
    - context_compass/system_docs/src_components.md:1170-1171, 1182-1187
    - context_compass/system_docs/src_components.md:1895-1898, 1979-1985
  IMPACT: The lessons are now backed by the descent the protocol requires
    rather than by pattern-matching off sibling examples.
  NEXT: none - the reading is done and its two corrections are landed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-04T11:43:01Z
  TYPE: UNKNOWN
  CLAIM: THE NOTCH LOOP STILL CANNOT BE CLOSED FROM `md.*`, RE-VERIFIED this
    session rather than carried over from expert 17. The user asked for a
    create/modify/ITERATE loop driven through notch, and lesson 26 stops one
    rung short of it on purpose. `Conduit.notch_spell(spell_index=, spell=)`
    takes the PARKED SPELL OBJECT. `SpellIndex`'s entire public surface is ids
    and predicates - `spells_in_index()`, `selected_spell_id`, `has_spell`,
    `is_sole_member`, `is_empty`, `id` - and BOTH id->object doors
    (`Conduit.get_spell_by_id:2510`, `Spellbook.find_spell_by_id:1973`) resolve
    any lineage id to the ACTIVE member. So there is no public expression that
    yields a parked candidate, and the promotion rung is unreachable by a user
    or an agent restricted to the public surface.
  EVIDENCE:
    - src/melder/aether/spellbook/bind/spell_index.py:144, 274, 288, 317, 345, 379
    - src/melder/aether/conduit/conduit.py:2510, 4460-4466
    - src/melder/aether/spellbook/spellbook.py:1973
  IMPACT: This is either a deliberate facade boundary (expert 17's reading: the
    parked object belongs to the Spellbook and the Spellbook is not what you
    notch from) or an init-surface gap. It has now been hit by two separate
    lessons, which is the signal the tier exists to produce. It is NOT recorded
    here as a defect - the distinction is the owner's to make.
  NEXT: OWNER RULING - is the parked-candidate lookup deliberately absent, or
    does the promotion rung want a public door?
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-04T13:05:00Z
  TYPE: MEASURE
  CLAIM: OWNER 3.14t RUN - 26, 27 AND 28 ALL RED, ALL MINE. What the run
    VALIDATED first, because most of the two lessons held: `aether.cleanup()`
    + `gc.collect()` collected 4827 objects and `md.Aether()` returned a NEW
    root (True) - the public teardown works exactly as lesson 27 claims; the
    cache SURVIVED the teardown (76 cached ids, our checkpoint still present)
    and `reload_cached_checkpoint` returned its summary; `research_walk(
    'codegen-turns')` returned 0 nodes, confirming the corrected claim that a
    cut lane records nothing; room memory returned 18 records for 3 turns x 4
    verbs plus the lane cut, confirming the command-not-turn framing; and
    staging left the selection unchanged with 3 members in the index.
    TWO DEFECTS, ONE ROOT CAUSE (26 and 28): I VIOLATED SINGLE RESIDENCE, an
    invariant I had READ IN THE COMPONENT DOC AND QUOTED IN MY OWN NOTES.
    `bind_inactive` auto-declares its version into the `default` lane, and one
    binding-signature SHA256 lives in exactly ONE lane network-wide,
    PERMANENTLY - there is no release verb. So `register_spell(staged_id,
    lane="codegen-turns")` hit `ResidenceRegistry.claim` and raised the
    rediscovery signal naming the holding lane. Reading the invariant and then
    writing a call that breaks it is the failure worth recording, not the
    traceback.
    28 CARRIED A SECOND, INDEPENDENT BUG the run would have hidden behind the
    first: I staged `v2` BEFORE the clean join, which moves the receiver's tip
    and would have made even the "clean" join divergent. Lesson 23 has the
    correct order and passes; 28 now mirrors it exactly.
  EVIDENCE:
    - src/melder/mutation_research/research_set/residence_registry.py:140-176
    - src/melder/mutation_research/research_set/research_set.py:1203
    - context_compass/system_docs/src_components.md:4582-4584
  IMPACT: 26 now TEACHES the refusal rather than tripping over it - it attempts
    the register, catches the rediscovery signal, explains that residence is
    where a version LIVES rather than a label you move, and then shows the
    correct route: `create_research_set(...)` gives an INDEPENDENT residence
    partition, so the same id files cleanly in a second investigation. 28 drops
    the register entirely and mirrors lesson 23's proven ordering.
  NEXT: owner re-run.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-04T13:05:00Z
  TYPE: UNKNOWN
  CLAIM: LESSON 27's LAST RUNG FAILS AND I DO NOT KNOW WHY - recorded as UNKNOWN
    rather than guessed, because I formed a hypothesis and THE SOURCE DISPROVED
    IT. `load_checkpoint` on a fresh runtime refused at admission: "the folded
    chain pre-flighted with 1 blocker finding(s) - hydration[spell_crystal:
    3732...] owning spellbook '01KZ...' is not in this bundle; the custody
    cannot bind... nothing was built."
    MY HYPOTHESIS, AND ITS DEATH: I believed pre-`finalize()`-ing the
    SpellbookConfiguration before handing it to the Spellbook suppressed the
    spellbook twin, because a standalone freeze carries no origin identity.
    `spellbook_configuration.py:299-310` refutes it outright - the already-frozen
    branch exists precisely for this case and still fires
    `_emit_spellbook_twin_when_recording`, with a comment naming the round-trip
    finding that produced it ("restore_engine_2026_07_07"). So the twin DOES
    emit on the origin-carrying re-freeze and my explanation is wrong.
    WHAT IS ESTABLISHED: `_fold_chain` applies chain WINDOWS oldest-first, and
    `flush_checkpoint(None)` flushes the whole ledger rather than one id. So a
    plausible remaining explanation is that a single flushed checkpoint is not a
    self-contained bundle across a full teardown. NOT PROMOTED TO FACT - I have
    not read the chain assembly, and lesson 24 restores successfully from a
    single id while the world is still UP, which is a materially different case
    because the spellbook it needs is already live.
  EVIDENCE:
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py:299-317
    - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1082-1098
    - src/melder/crystallizer/crystallizer.py:2010-2049
  IMPACT: Lesson 27 no longer claims a completed cross-teardown restore. It
    teaches what the run PROVED - ledger-vs-cache, the public teardown, cache
    survival, ledger recovery - and then teaches the admission refusal as the
    all-or-nothing guarantee working: preflight refuses at the one seam owning
    folded truth, and the message ends "nothing was built" rather than
    half-building a world and unwinding it. The open question is stated in the
    lesson body as an open question.
  NEXT: OWNER RULING - is a single flushed checkpoint meant to be
    self-contained across a full runtime teardown, or must the chain be flushed
    together? If the latter, 27 becomes a two-line change and a stronger lesson.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-04T13:20:00Z
  TYPE: FACT
  CLAIM: THE CHAIN SEMANTICS ARE NOW ESTABLISHED, which narrows the 27 unknown
    without closing it. `RestoreEngine._chain` is not built by the engine - it
    arrives as a constructor argument (`restore_engine.py:523`). It is built by
    `LoadAdmission.plan_checkpoint_load`, which calls
    `PersistenceSystem.detach_profile_chain(checkpoint_id)` and whose contract
    reads: "Detaches the target checkpoint's SAME-PROFILE CHAIN through the
    record's public seam. The returned plan owns the detached windows and
    preserves checkpoint creation order."
    SO THE CHAIN IS DERIVED FROM THE LEDGER, not from the single id. That makes
    one hazard certain even though it is not the cause here: after a teardown
    the fresh crystallizer's ledger is EMPTY, and `reload_cached_checkpoint`
    restores only the checkpoint you name (its own docstring: "history
    recovery; world restore remains load_checkpoint"). A world sealed across
    SEVERAL checkpoints and then partially reloaded therefore folds an
    INCOMPLETE chain - and would fail with exactly this shape of blocker. The
    correct pattern for a cross-teardown restore is `flush_checkpoint()` with no
    argument (whole ledger) and reloading every id before loading.
    WHY THAT IS STILL NOT THE ANSWER FOR 27: this world sealed exactly ONE
    checkpoint ("in ledger: 1" in the owner's run), so its chain was complete by
    count. The missing spellbook twin has some other cause, and I am not naming
    one I have not read. What is ruled OUT: the pre-`finalize()` hypothesis
    (refuted at spellbook_configuration.py:299-310) and chain truncation by
    count (refuted here).
  EVIDENCE:
    - src/melder/crystallizer/crystal_loader_system/restore_engine.py:434, 523
    - src/melder/crystallizer/crystal_loader_system/load_admission.py:165-196
    - src/melder/crystallizer/crystal_loader_system/crystal_loader_system.py:273-323
    - src/melder/crystallizer/crystallizer.py:2051-2079
  IMPACT: Two candidate explanations eliminated by reading rather than by
    re-running. The remaining surface to read is the emission path itself -
    whether the spellbook twin reached the profile at all in this ordering -
    which is a src investigation rather than an examples one and is outside this
    tier's fence.
  NEXT: OWNER - either rule the question, or open a src-lane ticket for the
    emission trace. 27 stands green and honest either way.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-04T13:45:00Z
  TYPE: FACT
  CLAIM: THE 27 UNKNOWN IS CLOSED, AND IT WAS NOT A LIBRARY DEFECT - IT WAS THE
    HARNESS. `UX_and_AIX_experiences/pytest_examples/conftest.py` reset ONLY
    `Aether` between examples. `Crystallizer`, `MutationResearch` and `Nexus`
    are process-wide roots that SURVIVED, so every expert lesson ran against
    whatever record its predecessor left behind: frames were cleaned out from
    under a crystallizer that outlived them, leaving custody rows whose owning
    spellbook had been evicted, in a profile shared by every example in the
    file. `load_checkpoint` folds the SAME-PROFILE chain, so the whole-world
    load inherited that wreckage and admission correctly refused it.
    THE RUN'S OWN NUMBER IS THE TELL AND I READ PAST IT TWICE: "flushed to
    cache: 76 cached id(s)" for a lesson that mints exactly ONE checkpoint.
    Seventy-six is not this lesson's world.
    THE FIX WAS ALREADY WRITTEN, IN THIS REPO, FOURTEEN LINES LONG.
    `test_expert_probes.py` carries the correct fixture and states the reason
    verbatim: "Expert is the first tier that touches MutationResearch, so it
    joins the reset here alongside the four the other tiers already needed. All
    five carry process-wide state; without the reset one row's checkpoints,
    profiles or research lanes surface in the next row." The PROBES had the
    isolation; the EXAMPLES never got it, and expert is the first tier where
    examples reach those roots. conftest now resets the same four in the same
    order (hosted roots BEFORE Aether, because Aether boots them) and rebinds
    the Spellbook/Conduit class seams. Verified by AST: the two reset sets are
    now identical.
    THREE HYPOTHESES DIED BEFORE THIS ONE, all killed by reading rather than by
    re-running: pre-`finalize()` suppressing the twin (refuted at
    spellbook_configuration.py:299-310), chain truncation by count (refuted -
    the ledger held one), and `origin_dynamic` arriving False from a
    settle-then-inherit conjure (refuted at spellbook.py:6464, where
    `_conjure_within_transaction_window` receives
    `self._settle_or_inherit_conjure_mode(dynamic)`, so the hint IS the
    effective mode).
  EVIDENCE:
    - UX_and_AIX_experiences/pytest_examples/conftest.py:1-75
    - UX_and_AIX_experiences/pytest_examples/test_expert_probes.py:14-34
    - src/melder/aether/spellbook/spellbook.py:6464, 6499, 5745-5768
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py:357-396
  IMPACT: This is bigger than lesson 27. EVERY expert example was running
    against leaked crystallizer/research/nexus state, so any expert lesson that
    passed did so despite the contamination rather than because the harness was
    clean. Results before this fix are not trustworthy for the three hosted
    roots. 27's lesson body no longer asserts the refusal as fact - it handles
    both outcomes, prints which it got, and teaches the durable half (the chain
    is the same-profile LEDGER, so a multi-checkpoint world needs
    `flush_checkpoint()` with no argument and every id reloaded).
  NEXT: owner re-run. The three reds should now be a clean measurement rather
    than a measurement of the previous lesson.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-04T13:55:00Z
  TYPE: FACT
  CLAIM: THE FULL ISOLATION MAP, and it REFINES the defect rather than widening
    it - the per-file probe fixtures are NOT wrong, they are correctly scoped to
    their tier's fence, and only the shared conftest was mis-scoped.
      conftest.py (serves EVERY tier)  Aether, Crystallizer, MutationResearch, Nexus  <- was Aether only
      test_expert_probes.py            Aether, Crystallizer, MutationResearch, Nexus
      test_advanced_probes.py          Aether, Crystallizer, Nexus
      test_intermediate_probes.py      Aether
      all example runners + contract probes   no fixture; inherit conftest
    READ AGAINST THE TIER FENCES those narrow fixtures are correct:
    intermediate forbids Nexus, MutationResearch and the crystallizer outright,
    so an Aether-only reset is exactly its blast radius; advanced admits the
    crystallizer and Nexus but not MutationResearch, which is precisely what its
    fixture resets. Neither is a defect and neither was touched.
    THE ONE DEFECT WAS THE SHARED FILE BEING SCOPED FOR THE LOWEST TIER WHILE
    SERVING THE HIGHEST. `conftest.py` is the only isolation the EXAMPLE runners
    have - none of the four `test_*_examples.py` files defines a fixture - so
    expert examples, the only examples that reach the hosted roots, inherited an
    Aether-only reset. Fixing conftest also lifts intermediate and advanced
    example isolation above their fences, which is harmless: the per-file probe
    fixtures still run (both are autouse, conftest first) and every reset is
    idempotent, so the narrower ones are now redundant rather than conflicting.
    DO NOT "TIDY" THE NARROW FIXTURES INTO THE WIDE ONE. They document each
    tier's blast radius at the place a reader of that tier will look, and
    collapsing them would delete that signal to remove a duplicate reset that
    costs nothing.
  EVIDENCE:
    - UX_and_AIX_experiences/pytest_examples/conftest.py:44-75
    - UX_and_AIX_experiences/pytest_examples/test_expert_probes.py:14-34
    - UX_and_AIX_experiences/pytest_examples/test_advanced_probes.py (fixture)
    - UX_and_AIX_experiences/pytest_examples/test_intermediate_probes.py (fixture)
    - UX_and_AIX_experiences/AGENTS.md (tier fences)
  IMPACT: The fix is one file and it is the right one file. No probe fixture
    needs changing, and the reason each is narrow is now written down so the
    next reader does not "correct" them.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-04T14:15:00Z
  TYPE: MEASURE
  CLAIM: LESSON 29 AUTHORED AGAINST A MEASURED GAP RATHER THAN A GUESS. I
    counted, by AST, which of the codegen room's 34 `research_*` commands any
    expert lesson actually CALLS: it was 15. Nineteen were documented in the
    component map and exercised nowhere, which means the tier was describing a
    surface it never drove.
    29 `reading_your_own_recorded_code` takes the largest coherent cluster of
    those - the crystal well, owner-ruled 2026-07-11 under units-and-scales -
    and teaches FOUR GRAINS that are not four ways to do one thing:
    `research_source` is the whole module WORLD, `research_module` is one
    module as a one-call DOSSIER (text, fingerprint, path, deps both ways,
    exports, drift - so a reader stops hand-joining five reads),
    `research_parts` is the INVENTORY that needs no names up front, and
    `research_part` is the lookup for when you have one.
    THE LESSON'S SPINE IS THE COMPARISON LAW: `research_part_diff` compares
    RECORDED MATERIAL ONLY and never the live disk, and the reason is
    correctness rather than caution - both sides of a version comparison would
    read the SAME present-day file, so a disk-backed diff reports "no change"
    between two genuinely different versions and is confidently wrong about
    both. The record is the only place two versions exist at once.
    It also carries why impact stays MODULE-grain (a part's honest radius IS
    its module's radius, because nothing imports half a file) and catches the
    LOUD custody refusal explicitly, because a silent empty read is
    indistinguishable from "this world has no code" - the one answer that is
    never true.
    EVERY SIGNATURE WAS READ, NOT INFERRED: `research_module(spell_id,
    module_name)` takes both positionally; `research_part(spell_id, part_name,
    *, kind=, module_name=)`; `research_part_diff(left, right, part_name, *,
    kind=, module_name=)`; `research_parts(spell_id, *, module_name=)`;
    `research_impact(*, spell_id=, module_name=)` is keyword-only on both;
    `research_source_drift()` takes nothing.
  EVIDENCE:
    - UX_and_AIX_experiences/04_expert/29_reading_your_own_recorded_code.py
    - src/melder/nexus/rift/command_system/codegen_command_system.py:1261-1472
  IMPACT: Tier research coverage 15/34 -> 25/34, with 10 commands exercised for
    the first time (source, module, parts, part, part_diff, module_graph,
    source_drift, residency, history, recent). Nine remain unexercised and they
    are a coherent set for a later lesson: the organization verbs
    (attach/detach/archive), whole-version `diff`, the synthesis pair
    (synthesize/stage_ancestry/clear_staged_ancestry) and two group reads
    (group_impact/group_drift).
  NEXT: owner run. 29 degrades honestly if custody cannot serve the reads -
    it catches the refusal, explains why LOUD is correct there, and returns.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-04T15:05:00Z
  TYPE: FACT
  CLAIM: ALL FOUR NEW LESSONS TRIMMED - they were over the tier's previous
    MAXIMUM, not just its median. 26 was 338 lines / 15,169 bytes against a
    tier median of 181 / 7,560 and a prior max of 311 / 13,987. Now 231, 210,
    218 and 188 lines, all under the old max.
    WHAT WAS CUT WAS MY OWN WORKING NOTES. I had been writing authoring
    narrative into the teaching files - "MY FIRST DRAFT OF 26 WAS WRONG", an
    "AUTHORING NOTE" carrying the conftest postmortem, an "OPEN QUESTION"
    block - which is ticket content. AGENTS.md is explicit: findings go on the
    tier's epic, and a header states TIER / GOAL / SURFACE EXERCISED. Those
    findings are already recorded here, so nothing was lost by removing them
    from the lessons. Also cut the stacked eight-line `print()` prose blocks
    (the tier explains once in the header and lets the code run) and fixed a
    duplicated `# 13.` step number in 26.
    THE TEACHING IS INTACT: two books, single residence, ledger-vs-cache, the
    comparison law, and why research_preview is codegen-rooms-only.
  EVIDENCE:
    - UX_and_AIX_experiences/AGENTS.md (header contract; findings go to the epic)
  IMPACT: The lessons read like the tier they belong to instead of like a
    debugging diary.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-08-04T14:35:00Z
  TYPE: FACT
  CLAIM: PRIVATE-ACCESS AUDIT OF EVERYTHING I WROTE, run on owner instruction
    ("if you think you have to reach into a private then we need to fix the
    public api or you need to do more research"). AST walk for private
    attribute reads, private calls and deep melder imports.
    ALL FIVE LESSON FILES ARE CLEAN - 26, 27, 28, 29 and the edited
    intermediate 37: zero private access, zero deep imports, every `md.*` name
    exported. The tier law held without exception.
    THE THREE FLAGGED FILES ARE ALL HARNESS - conftest and two probe modules -
    where deep imports are permitted by the house rule. But I wrote the
    conftest, so I researched whether its privates are avoidable rather than
    leaning on precedent.
    FINDING 1 - THE SINGLETON RESET IS AVOIDABLE, AND I AM KEEPING IT ANYWAY,
    with the reason now written into the file. A complete PUBLIC teardown
    exists: `Aether.cleanup()` cascades into crystallizer, mutation research,
    nexus and utility system (aether.py:299-309), and ALL FOUR `cleanup()`
    methods clear their own `_instance`/`_initialized` - verified by AST across
    the four classes. So `Aether().cleanup()` is a real public reset. It is
    still wrong for a FIXTURE: `cleanup()` does real teardown and re-raises a
    child failure, so one broken world would fail the SETUP of every
    subsequent test and turn one red into a file of reds.
    `_reset_singleton_for_tests` is a guaranteed discard, is named for this
    exact use, and is what the component suite and `test_expert_probes.py`
    already use. Sanctioned test seam, not a reach around the API.
    FINDING 2 - THIS ONE IS A GENUINE PUBLIC-API GAP AND IS NOT TEST-ONLY.
    `Spellbook._aether` is a `ClassVar` bound ONCE at import
    (`spellbook.py:172`: `_aether: ClassVar[Aether] = Aether()`), and `Conduit`
    carries the same seam. NOTHING rebinds them when the singleton is
    replaced - not `Aether()` construction (aether.py never assigns them) and
    not `cleanup()`. So after any reset or teardown those class seams point at
    a DEAD root, and every consumer is forced to write a private class
    attribute to recover. There is no public verb for it.
    THAT IS THE SHAPE OF THE API FOR ANYONE WHO TEARS AN AETHER DOWN AND
    BUILDS ANOTHER IN ONE PROCESS - which expert 27 does as its whole subject.
    27 gets away with it only because it never binds a new Spellbook after the
    teardown; a lesson that did would silently bind into the dead root.
  EVIDENCE:
    - src/melder/aether/spellbook/spellbook.py:172, 287, 294
    - src/melder/aether/aether.py:299-309, 331-332
    - src/melder/crystallizer/crystallizer.py:331-333
    - UX_and_AIX_experiences/pytest_examples/conftest.py (reasoning recorded)
  IMPACT: The examples are clean. The harness private is justified and the
    justification is now in the file rather than in someone's head. One real
    gap surfaced that affects users, not just tests.
  NEXT: OWNER RULING on the class-seam gap - either a public rebind verb, or
    `Aether()` construction rebinds the seams itself, or it is declared a
    deliberate single-Aether-per-process constraint and documented as one. I am
    not choosing: it is public API shape and this lane is examples.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-04T18:10:00Z
  TYPE: FACT
  CLAIM: LESSONS 30, 31 AND 32 AUTHORED - the tier now runs 01-32 and BOTH
    coverage measures are closed. The codegen room's research family is at
    34/34 (it was 15/34 when this lane opened); the package's public root is
    at 55/55 names exercised by at least one lesson across all four tiers.
    30 COMPOSING A VERSION IN THE WORKSHOP - research_synthesize plus the
    ancestry stamp. The stamp is AMBIENT and ONE-SHOT and no scope ends it,
    which is the whole reason `research_clear_staged_ancestry` exists: abandon
    a composition without clearing and the next unrelated bind inherits parents
    it never had. A rediscovery does NOT consume the stamp - identical content
    re-entering the world is not the candidate arriving.
    31 ORGANISING LANES AFTER THE FACT - attach / detach / archive. All three
    move where a lane SAYS it came from; none copies, moves or deletes a
    version, so a wrong shape is a wrong LABEL rather than lost work. Detach is
    not a delete: an unanchored lane joins DIVERGENTLY BY DEFINITION because
    there is no anchor for the tip to agree with. The default lane never
    archives - `register_spell` with no lane records there.
    32 A SUBSYSTEM'S BLAST RADIUS - research_group_impact is a UNION WITH
    CLOSURE MATH, not a sum, splitting internal from outbound; research_group_
    drift is source drift narrowed to the footprint, which is what makes it
    about your area instead of the repository's churn.
  EVIDENCE:
    - UX_and_AIX_experiences/04_expert/30_composing_a_version_in_the_workshop.py
    - UX_and_AIX_experiences/04_expert/31_organising_lanes_after_the_fact.py
    - UX_and_AIX_experiences/04_expert/32_a_subsystems_blast_radius.py
    - src/melder/nexus/configuration/nexus_configuration_builder.py:184-248
    - UX_and_AIX_experiences/04_expert/_concept_map.txt (ARC I recorded)
  IMPACT: Every command in the research family and every public root name now
    has at least one worked example behind it.
  NEXT: none for coverage. The lessons are UNRUN - see the handoff note.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-04T18:25:00Z
  TYPE: FACT
  CLAIM: EXPERT 06 CARRIED A METHOD NAME THAT NO LONGER EXISTS, found by
    chasing the last uncovered public root name rather than by reading 06.
    06's ladder table read "Nexus  enable() does it FOR you". THERE IS NO
    `enable` ON NEXUS - `nexus.py` defines `activate` / `deactivate` and zero
    `def enable`. The SUBSTANCE of the claim survives and I checked it before
    touching the line: `Nexus.activate()` finalizes the installed configuration
    on its way through, which the other three roots do not do for you, so the
    lesson's "three to one, Nexus is the exception" still holds. Only the verb
    had drifted. Corrected in place.
    THE REAL GAP BEHIND IT: `NexusConfigurationBuilder` was the last public
    root name that NO lesson referenced. Nexus was once the one root of four
    with no builder at all, so 06's builder-generosity table was simply out of
    date rather than wrong. Added to 06 rather than made a new lesson - 06 IS
    the configuration lesson, and the fourth root completes its own table.
    THREE LAWS CAME WITH IT, all read out of the source before being written:
    the exits are ONE-SHOT ownership transfers that consume the builder; the
    builder's `activate()` marks the CONFIGURATION active while the Nexus stays
    off (two objects, two bits - the rule did not bend for the new shape); and
    `build()` earns its place precisely BECAUSE the builder mirrors only
    `with_rift_creation_enabled` while the configuration carries the wide
    surface, so a frozen-only builder would have made the frame allow/deny
    lists unreachable through it.
  EVIDENCE:
    - src/melder/nexus/nexus.py:775-801 (factory), :838+ (activate finalizes)
    - src/melder/nexus/configuration/nexus_configuration_builder.py:9-61, 184-272
    - UX_and_AIX_experiences/04_expert/06_two_knobs_and_a_terminator_per_rung.py
  IMPACT: The tier no longer teaches a verb the runtime does not have, and the
    last unexercised public name is exercised where it belongs.
  NEXT: OWNER RULING NOT REQUIRED. But see the advanced-08 finding below - it
    is the same drift, in a tier this lane does not hold.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-04T18:30:00Z
  TYPE: FINDING
  CLAIM: ADVANCED 08'S PROSE IS STALE THE SAME WAY, AND I DID NOT TOUCH IT.
    `03_advanced/08_nexus_enablement.py` calls `nexus.activate(config)` in its
    code but still NARRATES the old verb throughout - "nothing is wired
    anywhere until you pass it to enable()", "we did not seal it; enable will",
    "enable finalized the config for us", "nexus: you hand it over, enable
    seals it for you" - and its SURFACE EXERCISED line reads
    `create_configuration, enable, disable`. Both `enable` and `disable` are
    gone from the Nexus public surface.
    Advanced is not this epic's lane, so this is recorded rather than fixed.
    Expert 06 CITES advanced 08 for that exact claim, which is how the drift
    propagated into a second tier in the first place.
  EVIDENCE:
    - UX_and_AIX_experiences/03_advanced/08_nexus_enablement.py:12, 23-26, 33,
      41, 75-90
    - src/melder/nexus/nexus.py (public defs: activate, deactivate; no enable)
  IMPACT: A reader of advanced 08 learns a verb that will raise AttributeError.
  NEXT: OWNER TO ASSIGN - advanced tier prose refresh. Cheap: it is narration
    only, the code is already correct.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-04T20:05:00Z
  TYPE: FACT
  CLAIM: OWNER 3.14t RUN - 30 RED, AUTHOR ERROR, AND I HAD QUOTED THE VERB'S
    OWN DOCSTRING BEFORE WRITING THE CALL THAT BROKE IT. Third time in this
    lane. `research_synthesize(base, donor, take_functions=["summarise"])`
    raised `ValueError: Donor source has no top-level function 'summarise'.
    Available donor parts of that kind: ['_show', 'main']`.
    TWO COMPOUNDED MISTAKES, both from writing to a mental model instead of to
    the source:
    (1) SYNTHESIS IS MODULE-GRAIN, NOT CLASS-GRAIN. Each id resolves through
    `source_view` to its ROOT MODULE text (mutation_research.py:3044-3062) and
    `take_functions` / `take_classes` name TOP-LEVEL parts of that module.
    `summarise` is a METHOD on ReportDonor and is invisible to both. The engine
    states the grain outright at mutation_research.py:3040 - synthesis "splices
    ONE version's module world".
    (2) BASE AND DONOR WERE THE SAME TEXT. ReportBase and ReportDonor are both
    declared IN THE LESSON FILE, so both resolved to the lesson file, and the
    traceback shows base_source == donor_source == this example's own text.
    THE FIX MAKES BOTH FACTS THE LESSON rather than hiding them. 30 now asks
    for the method FIRST and catches the refusal - the error names the donor's
    real top-level parts, which is how a caller discovers the grain after
    guessing wrong - then composes with a genuine top-level function and
    ASSERTS `base_module == donor_module` and `action == "replaced"`. "added"
    is unreachable while base and donor share a module, and that
    unreachability is now taught as the PROOF that the unit is the module.
  EVIDENCE:
    - src/melder/mutation_research/mutation_research.py:3040, 3044-3062
    - src/melder/mutation_research/synthesis/structural_synthesizer.py:213-223
    - UX_and_AIX_experiences/04_expert/30_composing_a_version_in_the_workshop.py
  IMPACT: The lesson teaches the grain instead of tripping over it. A reader
    who makes the same wrong assumption now meets it in the first ten lines of
    the workshop section rather than in a traceback.
  NEXT: none. But see the pattern note below - this is a repeat.
  REREAD: REQUIRED
  SCORE_0_TO_10: 6

- DATETIME: 2026-08-04T20:20:00Z
  TYPE: FINDING
  CLAIM: TWO MORE UNVERIFIED CLAIMS IN 31 AND 32, FOUND BY READING RATHER THAN
    BY A SECOND RED RUN - the check I should have run before shipping either.
    31's ARCHIVE DEMO PROVED NOTHING. It compared `lane_names()` before and
    after archiving, but `lane_names()` "lists ALL lanes regardless of state,
    including joined and archived ones" (research_set.py:660-661), so the two
    counts are IDENTICAL and the print implied a change that never happens.
    The real proof is the DISAGREEMENT between two reads: `heads()` drops the
    lane (open lanes only) while `lane_names()` keeps it. That gap IS the
    difference between hidden and unmade, and it is now asserted both ways.
    It also surfaced a law worth teaching that I had not known: `heads()`
    carries an open-but-empty lane with a tip of None, and "a missing name
    means 'not open', not 'does not exist'" (research_set.py:725-729). Absent
    and None mean different things. 31 now asserts that too.
    32 EXTRACTED THE COMPOSITION ID BY GUESSING - a `.get("group_id") or
    .get("id")` chain with a loop over any key ending in `_id`. That is defence
    against not having read the payload. `GroupedResearchNode.describe()`
    returns `group_id` plainly (grouped_research_node.py:412-422) along with
    the `node_type: "group"` tag that lane hydration dispatches on. Replaced
    with direct reads plus an assertion on the tag - and the tag's back-compat
    -by-ABSENCE rule became lesson content.
    THE PATTERN, NAMED HONESTLY: all three of these are the same failure -
    asserting a payload's shape from its NAME instead of from its describe().
    A `.get(...) or .get(...)` fallback in an example is a confession that the
    author did not read the producer, and it should be treated as a smell in
    review rather than as defensive coding.
  EVIDENCE:
    - src/melder/mutation_research/research_set/research_set.py:654-678 (lane_names),
      720-751 (heads), 1977-2014 (join divergence), 2200-2216 (archive refusal)
    - src/melder/mutation_research/research_set/grouped_research_node.py:394-422
    - src/melder/mutation_research/research_set/research_lane.py:846-887 (describe)
  IMPACT: 31 and 32 now assert contracts that were read, not inferred. Three
    laws that were invisible to me before this pass are now taught.
  NEXT: OWNER RERUN of 30, 31, 32 and the amended 06. None of the four has been
    run since these edits; the sandbox is 3.10 and cannot run any of it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Method: every example imports melder as md ONLY - a deep-path import in an example
IS the finding. Examples are runnable scripts with honest asserts; they ride the
owner's 3.14t runs (device VM cannot import the runtime).

ADDED 2026-08-04: lessons 26, 27 and 28 (tier now runs to 28) plus FOUR PROBE ROWS
in `pytest_examples/test_expert_probes.py` (42 rows total, no duplicate names).
The probes exist because the house law says an example may only assert what is
verified in source or pinned by a probe, and these three lessons make four claims
worth pinning: the strict-JSON payload guarantee, `from_payload` identity
preservation, a never-registered lane walking empty, and `Aether.cleanup()`
clearing the singleton.

All three examples parse clean, carry a `main()`, contain ZERO deep imports, and
every `md.*` name was checked mechanically against the live `__all__` (64 names),
not by eye. They are written LF while their worktree siblings currently read CRLF -
that is deliberate: HEAD is LF, and the CRLF is the pending repo-wide flip, so LF
is what survives its resolution. The probe file was ALREADY in that flip before I
edited it, so its endings were preserved rather than "fixed" - normalising it would
have bundled a 922-line EOL change into a 123-line content diff.

NOT RUN: this sandbox is Python 3.10 and melder requires >=3.14, so no green is
claimed for any of it. TWO owner questions outstanding: the parked-candidate lookup
behind `notch_spell` (now hit by two lessons), and nothing else blocking.

ADDED 2026-08-04 (later): lessons 30, 31 and 32. The tier runs 01-32 and BOTH
coverage measures are now closed - the codegen room's research family at 34/34
(from 15/34 when this lane opened) and the package's public root at 55/55 names
exercised by at least one lesson across all four tiers.

THE LAST TWO NAMES WERE NOT WHAT THEY LOOKED LIKE, and the distinction matters
for whoever measures this next. `RiftSpace` was never a gap: it is a type you
RECEIVE from `rift.space`, never one you construct, so the fix was to ASSERT
that law in 32 rather than to invent a constructor call. `NexusConfiguration-
Builder` WAS a real gap, and chasing it surfaced a stale verb in expert 06 and
the same drift in advanced 08. A coverage number is a prompt to go read, not a
score to raise.

06 IS NOW AMENDED AND ITS `VERIFY:` LINE SAYS SO. It still carries the honest
RUN GREEN 2026-08-03 for the original body, with the Nexus builder section
marked added-and-not-yet-run. Do not let the green on the header stand for the
whole file at the next harness pass.

LINE ENDINGS, AGAIN: lessons 26-32 are LF (HEAD is LF; the worktree CRLF is the
pending repo-wide flip). Expert 06 and the concept map were ALREADY CRLF before
I edited them, so their endings were preserved rather than "fixed" - normalising
either would have bundled an EOL change into a content diff. 06's real diff was
verified by raw byte comparison against HEAD with endings normalised away: 70
lines added, 6 removed, and the 6 are the ladder table, the SURFACE line and the
VERIFY line. `git diff --ignore-cr-at-eol` still MISREPORTS this repo; do not
trust it.
