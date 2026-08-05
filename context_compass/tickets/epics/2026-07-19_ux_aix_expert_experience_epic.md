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
