- Completed: 2026-07-12T21:00:00Z
- Summary: All three slices delivered (distribution provenance channel w/
  describe+refold parity, binary .so/.pyd path+bytes-sha identity,
  merge-graft mode via public bind_inactive/notch verbs only) + 7-unit
  suite + merge integration arc; owner rulings pinned (index identity
  disposable; no mediator bypasses). Closed on owner directive; pytest
  Not run by agent - reopen on red. Promotion carried as debt.

# Task: crystallizer finishing slices (analyzer leaves + merge-graft mode)

## Metadata
- Task ID: TASK-2026-07-11-crystallizer-finishing-slices
- Parent: the crystallizer completion program (owner: "focus on the
  crystallizer stuff you planned on doing")
- Status: ready
- Owner: cowork
- Agent Name: melder_0
- Priority: p2
- Created: 2026-07-11T22:10:00Z
- Updated: 2026-07-11T22:10:00Z

## Scope (three slices, additive)
1. SITE-PACKAGE DISTRIBUTION PROVENANCE: the site_package custody
   strategy currently records the path-law classification only; enrich
   it with distribution metadata (name/version via importlib.metadata,
   resolved from the module's top-level package) so a restored world
   can say WHICH dependency versions the sealed world was built
   against. Additive payload key; honest None when metadata is absent.
2. BINARY/DYNAMIC-IMPORT DEPTH: today these classify as honest leaves;
   evaluate recording the .so/.pyd path + sha fingerprint (binary) and
   the importer-module edge (dynamic) so the impact engine's
   unknown_module answers shrink. Keep honesty: no parsing of binaries,
   just identity capture.
3. MERGE-GRAFT MODE - DECISION (the dial was delegated: "your call"):
   BUILD IT, as an opt-in GraftRunner mode
   (merge_into_index_id=<live index id>), implemented ONLY on the
   public verbs that now exist: members enter the TARGET index via
   add_spell_into_spellindex (+ notch when the record's selection
   should win, opt-in). The fresh-index-only law REMAINS THE DEFAULT -
   merge mode is explicit, never inferred; resident-member overlap
   rules carry over unchanged. Rationale: the law existed to protect
   general_0's unfinished seams; those seams SHIPPED (conduit.py
   :4003/:4075), so a safe merge lane is now buildable without
   touching index internals.

## Ticket Contract
- ENTRY_GATE: patch dir authored before code (system-impacting: new
  GraftRunner mode + custody payload keys).
- EXECUTION_BOUNDARY: crystal_analysis/custody + graft_runner.py +
  tests; no loader/record behavior changes.
- EXIT_GATE: slices landed + tests authored; owner-run 3.14t green.
- FAILURE_ESCALATION: BLOCKER note if the public add/notch verbs turn
  out not to support the merge flow shapes.

## Notes
- DATETIME: 2026-07-11T22:10:00Z
  TYPE: DECISION
  CLAIM: Merge-graft dial decided (owner-delegated): build as opt-in
    mode on public verbs; fresh-index-only stays default. See Scope 3
    for the full rationale and constraints.
  EVIDENCE: src/melder/aether/conduit/conduit.py:4003-4075
  IMPACT: the last undecided crystallizer question has an answer and a
    buildable shape.
  NEXT: open with slice 1 (smallest); patch dir first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-11T22:35:00Z
  TYPE: FACT
  CLAIM: ENTRY GATE SATISFIED + slice-1 design source-verified: the
    existing harvest_payload seam is RETENTION-ONLY and walk-gated to
    user_source (crystal_analyzer.py:512 "only the user-source class
    ever yields"), so provenance gets its OWN strategy verb
    (harvest_provenance) + always-on walk branch + a new
    distribution_provenance result channel (store/verb/property/
    describe/refold) + SpellCrystal passthrough. Patch dir
    crystallizer_finishing_slices_2026_07_11 authored with the full
    three-slice design incl. the DECIDED merge-graft shape
    (merge_into_index_id via public add/notch verbs only) and the
    slice-2 dynamic-import residue deferral.
  EVIDENCE:
  - system_docs/patches/active/crystallizer_finishing_slices_2026_07_11/architecture_patch.md
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py:499-529
  - src/melder/crystallizer/crystal_analysis/custody/site_package_custody_strategy.py:1-162
  IMPACT: implementation can start cold from this note + the patch.
  NEXT: implement slice 1 (strategy verb -> walk branch -> result
    channel -> SpellCrystal passthrough -> unit tests: resolved dist,
    unresolvable None, refold parity).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T22:45:00Z
  TYPE: FACT
  CLAIM: SLICE 1 PART 1 LANDED - SitePackageCustodyStrategy.
    harvest_provenance (:163; INERT until the walk consumes it, so no
    half-wired seam risk): top-level name -> packages_distributions()
    -> {distribution_name, distribution_version, all_distributions,
    top_level}; PackageNotFoundError -> version None; unresolvable ->
    honest None; the broad except is the DOCUMENTED best-effort
    exception (provenance must never break a bind-time walk). Module
    docstring's stale "future env-layer decision" line corrected
    (comments-never-lie). Dict import added. Disk-verified via
    file-tool grep (:163/:210); AST Not run (standing replica rot).
  EVIDENCE:
  - src/melder/crystallizer/crystal_analysis/custody/site_package_custody_strategy.py:163-235
  IMPACT: the provenance resolution core exists and is unit-testable
    in isolation.
  NEXT: PART 2 wiring - crystal_analyzer walk branch (beside :522,
    kind=="site_package", always-on) -> CrystalAnalysisResult
    distribution_provenance channel (store/record verb/property/
    describe key/refold in analyze_payload/cleanup del) -> SpellCrystal
    delegating property + describe passthrough -> unit tests (resolved
    dist e.g. pytest itself, unresolvable None, refold parity, verb
    cleanup guard).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T23:00:00Z
  TYPE: FACT
  CLAIM: SLICE 1 COMPLETE end to end + tested. Wiring landed: walk
    branch (crystal_analyzer, beside the S2 harvest; always-on,
    kind=="site_package"), result channel (slot + init + cleanup del +
    record_distribution_provenance verb + detached property + describe
    key beside user_module_sources + analyze_payload REFOLD with
    pre-slice .get tolerance), SpellCrystal describe passthrough
    (additive .get; carrier law - no logic). NEW 5-test suite
    test_distribution_provenance.py (ast OK, 101 lines): resolves an
    installed dist (pytest = deterministic fixture), top-level
    resolution for dotted submodules, unresolvable honest None,
    post-cleanup refusal, result channel record/describe/detachment.
    Ctor verified no-arg from source before use (store_cached_item
    lesson applied). Src files disk-verified via file-tool; AST Not
    run on grown files (standing replica rot).
  EVIDENCE:
  - src/melder/crystallizer/crystal_analysis/custody/site_package_custody_strategy.py:163-235
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py (walk branch + refold)
  - src/melder/crystallizer/crystal_analysis/crystal_analysis_result.py (channel)
  - src/melder/crystallizer/crystals/spell_crystal.py (describe key)
  - tests/unit/melder/crystallizer/crystal_analysis/test_distribution_provenance.py:1-101
  IMPACT: every sealed world now records which dependency versions it
    was built against - the third-party sibling of source drift.
  NEXT: slice 2 (binary sha capture into the same channel via
    BinaryUnknownCustodyStrategy) then slice 3 (merge-graft mode);
    owner run covers slice 1's live-walk leg (the analyzer branch runs
    in every bind-time analysis already exercised by the tree).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T23:15:00Z
  TYPE: FACT
  CLAIM: SLICE 2 COMPLETE + smart tests landed (suite 5 -> 7 tests,
    210 lines, file-tool verified; bash replica stale again).
    Implementation: BinaryUnknownCustodyStrategy.harvest_binary_identity
    (BINARY_EXTENSIONS class constant .so/.pyd/.dylib; path+bytes-sha256
    identity; vanished/unreadable file = path identity w/ sha None -
    half-answer beats silence; pathless/non-binary = None); walk gains
    the elif kind=="unknown" branch feeding the SAME provenance channel
    (consumers distinguish by keys); the record verb + property
    docstrings updated so the channel's contract covers both row shapes
    (docstrings-never-lie). SMART TESTS per owner directive: (a) ONE
    walk-level contract test drives the WHOLE slice-1 chain - real tmp
    package importing REAL pytest, site root derived from
    pytest.__file__ (deterministic, no path-text luck), asserts
    classification + distribution row w/ the REAL installed version +
    describe -> analyze_payload REFOLD PARITY (the MR seam law) in one
    test; (b) binary identity against REAL file bytes w/ independent
    hashlib verification + extension scoping + vanished-file identity.
  EVIDENCE:
  - src/melder/crystallizer/crystal_analysis/custody/binary_unknown_custody_strategy.py
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py (elif branch)
  - tests/unit/melder/crystallizer/crystal_analysis/test_distribution_provenance.py:1-210
  IMPACT: the dependency-environment provenance story is whole:
    distributions versioned, binaries fingerprinted, refold parity
    proven. Slice 3 (merge-graft) is the lane's last build.
  NEXT: slice 3 - GraftRunner merge_into_index_id mode via PUBLIC
    add_spell_into_spellindex (+ opt-in adopt_recorded_selection via
    notch_spell); overlap rules carry over; fresh-index-only stays
    default. Then closure walk + promotion for the whole lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T23:40:00Z
  TYPE: FACT
  CLAIM: SLICE 3 COMPLETE - the merge-graft mode is live end to end.
    DESIGN REFINEMENT vs the patch: merge target is a LIVE INDEX OBJECT
    (merge_into_index), not an id - the graft_index live-object facade
    precedent, avoiding a new by-id lookup surface. Runner: ctor gains
    merge_into_index + adopt_recorded_selection (adoption without a
    target = ValueError; RecordVersion/graft_kind gates unchanged);
    run() branches pre-anchor (merge needs no anchor member; the
    target's selection stands by default); NEW _merge_members parks
    every graftable member onto the target via PUBLIC
    conduit.bind_inactive(spell_index=target) and optionally adopts the
    recorded selection via PUBLIC conduit.notch_spell (stable
    content-SHA ids make the recorded selected_id address the live
    spell directly; ungrafted selection = honest shortfall
    "recorded_selection_not_grafted_not_adopted"). Report gains
    merged_into_existing + selection_adopted (fresh lane emits them
    too: False/True). Facade passthrough w/ docstring. Module + class
    docstrings truth-synced: fresh-index-only stays the DEFAULT; the
    historical "no index merging, ever" law is explained (it protected
    the then-unfinished seams; their shipping enabled this mode);
    overlap rule identical in both modes. SMART TEST (integration,
    cloned from the park test's proven harness): full merge arc -
    capture (active+parked) -> merge into a host index that already
    owns its own member -> target holds all three ids w/ adopted
    selection, merged member's live index IS the target, zero
    shortfalls + the adoption-without-target ValueError refusal in the
    same test. Tuple import added. All disk-verified via file-tool;
    AST Not run (standing replica rot).
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py (mode + _merge_members)
  - src/melder/crystallizer/crystallizer.py:647-712 (facade)
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:1743-1834
  IMPACT: ALL THREE SLICES COMPLETE - the crystallizer completion
    program's build list is empty except the adapter epic and the two
    discovery-first epics.
  NEXT: owner-run 3.14t over everything (asset_crud lane + all three
    slices) -> closure walks + one promotion pass (C-docs + graph:
    MeshInterfaceContract node, provenance channel, merge mode;
    re-verify counts vs mutation_0's 530/992 first).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-11T23:55:00Z
  TYPE: DECISION
  CLAIM: OWNER RULINGS PINNED (mediator challenge resolved). (1) The
    mediator audit satisfied the owner ("the things your using don't
    skip the mediator thats reasonable") - the audit table lives in the
    session record: every crystallizer structural write is a
    self-admitting public verb (engine :1304/:1364/:1425/:1478/:1556/
    :1684; runner :331/:389/:444/:467); zero private-seam writes
    package-wide; NO SKIPPING is the standing law going forward. (2)
    "The index_id doesn't matter, it's just about what spells are in
    it" - index identity is DISPOSABLE, membership is the unit of
    truth; pinned into the runner's class contract; this RESOLVES the
    merge-mode A/B/C question as A (keep both merge landing and
    adoption - membership placement through mediated verbs is exactly
    what grafts are for; identity preservation was never the contract).
    (3) Graft atomicity: per-verb admission is the managed design
    (each member entry its own mediated transaction); an umbrella span
    would need a shared-identity/nesting story in the mediator and is
    a RECORDED FUTURE DECISION for the mediator-strategies epic, never
    an improvised claim - noted in the runner contract.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py (contract block)
  IMPACT: the lane's design questions are all closed by owner ruling;
    nothing awaits but the test run.
  NEXT: owner-run 3.14t -> closure walks + the single promotion pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T00:10:00Z
  TYPE: FACT
  CLAIM: OWNER-RUN TRIAGE (merge test) - the merge arc held EXCEPT
    selection adoption: selected stayed the target's original member.
    ROOT CAUSE (source-verified, not the test's fault): the adoption
    resolved its Spell via find_spell_by_id, which returns the index's
    ACTIVE spell object for ANY member id (spellbook.py:1852-1855 -
    iterates _spells keyed by index, returns the registered spell when
    has_spell(queried_id)) - so the runner notched the target's own
    current selection: a SELF-NOTCH that legally moves nothing.
    selection_adopted=True was honest (notch ran + returned). FIX:
    resolve the adoptee via Spellbook._get_owned_spell (:2742 -
    active-OR-PARKED owned-member resolution; the exact seam the notch
    lifecycle harness uses at test_spell_index_notch_lifecycle.py:85;
    Optional-None on miss keeps the honest shortfall lane). Read-only
    private seam, documented in-line; the WRITE stays the mediated
    public notch verb. RESIDUE flagged: no PUBLIC parked-member
    accessor exists (harness + runner both lean on the private seam) -
    candidate small public verb for an owner-approved lane.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:1841-1857
  - src/melder/aether/spellbook/spellbook.py:2742-2761
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py (adoption fix)
  IMPACT: adoption now notches the actual grafted member; the fresh
    lane was never affected (its find_spell_by_id use resolves the
    anchor = the active member, correct by construction).
  NEXT: owner re-runs the merge test; on green -> closure + promotion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
ALL THREE FINISHING SLICES COMPLETE: distribution provenance (walk ->
channel -> describe -> refold parity), binary identity capture, and the
merge-graft mode (public-verbs-only writes, live-object target,
fresh-default preserved) - each with contract-grade tests (7 unit + 1
integration). Owner rulings pinned: no mediator skipping ever (audit
clean), index identity disposable/membership is truth (merge mode A
stands), graft atomicity = recorded future decision. Merge-adoption
triage fixed (find_spell_by_id self-notch trap -> _get_owned_spell).
Remaining: owner re-run -> closure + promotion. Owner runs tests; agent
reports Not run.
