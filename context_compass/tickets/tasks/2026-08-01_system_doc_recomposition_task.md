# Task: Recompose src_architecture.md and src_components.md to the new spec

## Metadata
- Task ID: TASK-2026-08-01-system-doc-recomposition
- Status: in_progress
- Owner: cowork
- Agent Name: helper_f
- Priority: p1
- Created: 2026-08-01T19:12:00Z
- Updated: 2026-08-01T19:12:00Z

## Problem / Opportunity
The owner updated context_compass with a new documentation system. Both canonical
system docs predate it and satisfy neither the Required Section Contract nor the
new index mechanics.

## Ticket Contract
- ENTRY_GATE: owner directive; new standards read.
- EXECUTION_BOUNDARY: `system_docs/` only. No source edits.
- DEPENDENCIES: `src_architecture_instructions.md`, `src_components_instructions.md`,
  `system_document_build.md`, `src_graph_generation.md`, `src_graph_usage.md`.
- EXIT_GATE: both docs pass their contract; both indexes `--check` green; graph
  migrated to `src_graph.md` + `src_graph_index.md`.
- FAILURE_ESCALATION: BLOCKER if content would be lost rather than moved.

## Build Order
- [x] Read the new standards; confirm the old graph skills are retired.
- [x] Recompose `src_architecture.md`.
- [ ] Recompose `src_components.md` (consumes the migration file).
- [ ] Migrate the graph to `src_graph.md` + `src_graph_index.md`.

## Notes
- DATETIME: 2026-08-01T19:12:00Z
  TYPE: FACT
  CLAIM: THE SHIPPED .md INDEXES WERE STALE ON ARRIVAL. `--check` reported
    src_architecture_index.md at 229 lines against a live 2249, and
    src_components_index.md at 252 against 5381. They were generated against the
    STARTER docs that ship with the package, not against this repo's documents, so
    nothing could slice either doc until regenerated.
  EVIDENCE:
  - context_compass/system_docs/src_architecture_index.md
  - context_compass/system_docs/src_components_index.md
  IMPACT: Any agent trusting those indexes would have been refused by the tool -
    which is the tool behaving correctly. The failure mode to watch for is an
    agent reading a doc WHOLE because slicing refused, which is the cost the
    index exists to avoid.
  NEXT: Regenerate after each recomposition pass.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-01T19:12:00Z
  TYPE: IMPLEMENT
  CLAIM: `src_architecture.md` RECOMPOSED, 2249 -> 1752 lines. It now carries
    EXACTLY the 17 contract sections in contract order, one H1, no container
    headings.
    - `## Indexing` ADDED (did not exist).
    - `## Data Flows and Sequences` MOVED UP ahead of `## Operational Invariants`;
      it had sat after Failure Modes.
    - `## C1 Code Map` REBUILT: 134 entries, each carrying path/start_line/
      end_line/loc/verified_at MEASURED from disk. All resolved.
    - `## Table of Contents` REMOVED - the generated index replaces it, and a
      hand-maintained contents list is a second addressing surface that drifts.
    - 34 non-contract H2s MOVED, NOT DELETED, to the patch lane at
      `system_docs/patches/active/system_doc_recompose_2026_08_01/component_material_for_migration.md`
      (1225 lines). Four had headings WRAPPED across two physical lines - the
      defect that produces one-line index fragments - and were unwrapped.
    TWO DEFECTS THE SCRIPT CAUGHT BEFORE WRITING, not after:
    (1) one C1 "path" was a DIRECTORY (`mutation_research/research_set/`) and
    cannot carry a line range; it was EXPANDED into its 8 real modules rather
    than given a plausible number, per the rule that an unverified range stays
    UNKNOWN instead of being invented. That is why 126 file entries became 134.
    (2) The first run aborted on that directory BEFORE any write, so the document
    was never left half-recomposed.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md
  - context_compass/system_docs/src_architecture_index.md
  IMPACT: Index regenerated in the same pass: 36 sections over 1751 lines, all 36
    ranges validated against their own headings, `--check` OK, and a live
    `--slice "Operational Invariants"` returns 576-639 with its citation header.
    OPEN COVERAGE GAP, DELIBERATE AND BOUNDED: until the components pass lands,
    the migrated material is in NEITHER canonical document. Recorded in the
    architecture doc's own handoff summary so it cannot be discovered by accident.
  NEXT: `src_components.md`, consuming the migration file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-02T13:00:00Z
  TYPE: VALIDATE
  CLAIM: Both documents CONFORMED to the 2026-08-02 revision of
    `src_architecture_instructions.md` / `src_components_instructions.md`.
    Re-read both skills plus `system_document_build.md` first. FOUR defect
    classes found and closed; three of them the previous pass did not know were
    defects because the rules postdate it.
    (1) FIVE DIRECTORY CITATIONS in `Key Files (C1)` of `src_components.md`
      (crystal_loader_system/, crystal_analysis/, crystals/, nexus/acl/,
      nexus/frame_descriptor/). A directory has no line range and can never
      resolve against a graph keyed by source file. EXPANDED into real modules,
      every one verified present in `src_graph_index.md` BEFORE writing.
      Expansion also recovered two modules the old parenthetical had omitted -
      `graft_runner.py` and `user_world_rebuild.py`. Subpackages too deep to be
      key files (acl 41 modules, crystal_analysis 22) are named as prose with
      measured counts, NOT as citations, so they cannot re-enter the join.
    (2) TWO TEST PATHS in `Key Files (C1)` and the SAME TWO in `## C1 Code Map
      (Core)`. The rule is explicit that the graph is built from the source tree
      and a test path is a guaranteed miss, not a near miss. MOVED, NOT DELETED,
      to the patch lane under a heading naming `tests_components.md` as the
      destination, with their measured ranges retained so the test-side pass
      does not remeasure. They REMAIN in `## Information Sources` deliberately:
      they were read as evidence, and that section records what was consulted,
      not what a component claims as its own.
    (3) ONE DEAD PATH cited as if live - `crystal_loader/bootstrap_manifest.py`,
      removed in the 2026-07-10 decomposition. The fact was worth keeping; the
      backticked form made a mechanical join report it forever. Restated as a
      historical note.
    (4) SYSTEMATIC OFF-BY-ONE ACROSS ALL 359 C1 ENTRIES, the one that matters
      most and was invisible to every structural check. Every `end_line` was
      `len(text.split(chr(10))))`, which counts a phantom line after the final
      newline. `src/melder/__init__.py` was documented as ending at 261; it ends
      at 260. `loc` was inflated by one on every entry in both documents. 131 of
      134 architecture entries and 223 of 225 components entries were wrong; the
      five that matched are the files with no trailing newline. ALL REMEASURED
      from disk with `splitlines()` and restamped `verified_at`.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md
  - context_compass/system_docs/src_components.md
  - context_compass/system_docs/patches/active/system_doc_recompose_2026_08_01/component_material_for_migration.md
  IMPACT: Join integrity is now REAL rather than assumed. Strict re-parse of both
    contract fields: architecture 134 cited paths / 0 unresolved, components 241
    Key Files paths + 225 C1 entries / 0 unresolved. Contract order 17/17 and
    12/12, in order. One H1 each, zero wrapped headings, zero duplicate section
    names. Both indexes regenerated in the same pass, both `--check` green
    (37 sections / 1806 lines; 129 sections / 7266 lines).
    CONTENT PRESERVATION GATE: baseline multiset captured BEFORE the first edit.
    Architecture 0 unaccounted lines. Components 12 unaccounted, ALL of them the
    deliberately reshaped directory-cite lines - verified at content level per
    the gate's own instruction to compare extracted content on a reshape: 20 of
    20 module tokens and 6 of 6 semantic claims still present.
    NOTE ON THE GATE'S RECIPE: as written it emits false positives whenever the
    document and its migration target share lines, because `uniq -c` counts shift
    and `diff` reports the old count row as a loss. Ran it as the containment
    check it specifies (every baseline line's count must be met or exceeded
    across document plus targets) rather than as raw `diff`.
  NEXT: Test-side mirror. Both test indexes are STALE - tests_architecture_index
    115 lines against a live 386, tests_components_index 140 against 767 - and
    neither test document mentions aetheric_mediator, Cleanable,
    crystal_loader_system or graft_runner at all.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-02T13:05:00Z
  TYPE: VALIDATE
  CLAIM: Both documents SCORED against
    `design_engineer/policies/system_document_quality_rubric.md`, scored from the
    files on disk after the index rebuild, not from the draft in context.
    src_architecture = 85 / 100, band B (usable).
      Fidelity 4/5 (24.0) - every C1 entry resolves and was remeasured this pass;
        scored 4 not 5 because absence of a caught error is not evidence of
        accuracy, and prose claims were not independently re-derived.
      Contract completeness 5/5 (15.0) - 17/17 present, in order, populated.
      Depth 4/5 (12.0).
      Addressability 5/5 (15.0) - one H1, unique names, no wraps, and no
        container H2, which this contract genuinely permits.
      Join integrity 5/5 (15.0) - 134/134 resolve, all ranges measured today.
      Mirror agreement 2/5 (4.0) - `tests_architecture.md` is 13 days stale with
        a stale index.
    src_components = 71.5 / 100, band C (usable, refresh before high-risk work).
      Fidelity 4/5 (24.0).
      Contract completeness 3/5 (9.0) - all 25 C3 entries carry all 12 fields,
        but 50 of 300 field slots are a single sub-55-character bullet, which is
        the rubric's own anchor for 3. Concentrated in Observability (11),
        Extension Points (9), Concurrency/Threading (8). Example:
        src_components.md `Component: Public API and Runtime Guardrails` ->
        `Extension Points: - None.` - a not-applicable with no reason, which the
        rubric scores as blank rather than as a decision.
      Depth 3.5/5 (10.5) - averaged per entry per the components profile.
      Addressability 3/5 (9.0) - `## C3 Components Catalog` indexes as a
        3,033-line range, 41.7% of the document, in one slice.
      Join integrity 5/5 (15.0) - 466 cited paths resolve, all ranges measured
        today.
      Mirror agreement 2/5 (4.0) - `tests_components.md` stale and unaware of
        subsystems this document now covers; section name drift
        (`C1 Code Map (Key Paths)` against `C1 Code Map (Core)`).
  EVIDENCE:
  - context_compass/agent_onboarding/default/design_engineer/policies/system_document_quality_rubric.md
  - context_compass/system_docs/src_components.md
  - context_compass/system_docs/tests_components.md
  IMPACT: Both clear the 60 threshold, so downstream work may proceed. Components
    at 71.5 carries the caveat the C band requires: the next reader inherits it
    here rather than inheriting false confidence.
    ONE FINDING FOR THE SKILL AUTHOR, NOT A DEFECT IN THE DOCUMENT: Addressability
    is CAPPED AT 3 for any conformant `src_components.md`. The rubric scores 3
    when "a container heading exists that a reader could select by mistake", and
    the components section contract REQUIRES `## C3 Components Catalog`, which is
    exactly that container. The document cannot score above 3 without violating
    its own contract. The criterion is measuring the contract, not the document.
  NEXT: Owner ruling on whether the components Addressability anchor should
    exempt a contract-required catalog heading.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-02T14:20:00Z
  TYPE: IMPLEMENT
  CLAIM: DEPTH PASS against the two criteria the rubric scored lowest.
    `src_components.md`: ALL 50 HOLLOW C3 FIELD SLOTS ELIMINATED, 0 of 300
    remaining, across 14 components. Each rewrite was driven from source read
    this pass, not from the existing text, and the non-obvious ones carry
    `path:line` EVIDENCE. What the pass actually surfaced, none of which the
    thin bullets said:
    - `Spellbook` owns TWO RLocks and the second is never acquired in its own
      module. `_phase_run_lock` is taken from `SpellbookCreationSystem`, which
      reaches in as `spellbook._phase_run_lock`, because meld-time revalidation
      hits the scheduler path from multiple threads WITHOUT the Spellbook lock;
      the run lock makes register/run/release atomic per run. The old text said
      "Internal RLock guards most mutable operations."
    - `bind()` returns TWO DIFFERENT SHAPES depending on call style - the Spell
      on a direct call, the decorated object when used as a decorator - so
      callers cannot assume a Spell came back. Old text: "Spell and SpellIndex
      instances."
    - `SpellbookConfiguration.freeze()` is a CRYSTALLIZER EMISSION TRIGGER, not
      just a seal. Old text: "Frozen configuration and hook maps."
    - `Conduit` silently OVERRIDES a lesser conduit's name to None and continues;
      the single warning is the only trace, and a later name lookup fails with no
      explanation. Old text: "Logs via SafeLogger."
    - `Creations` cleanup AGGREGATES disposal failures into an ExceptionGroup and
      disposes in REVERSE CREATION ORDER. Old text: "Logs errors during cleanup."
    - `PhaseScheduler`'s latch invariant - every dequeued unit reports EXACTLY
      ONCE, done units are skipped not re-run, and the caller calls
      `wait_all_reported` before raising. Old text: "Dedicated worker threads
      and shared queue."
    ONE CLAIM CORRECTED, NOT JUST DEEPENED: DevOps Control Plane Observability
    said "minimal internal logging". `dev_ops_manager.py` has NO logger at all -
    zero call sites. The field now says so and points at the information
    registry as the actual read point.
    `src_architecture.md`: Operational Invariants and Failure Modes deepened
    where they asserted a rule without its mechanism. The Aether singleton
    invariant now names the double-checked `__new__` guard and the
    IDENTITY-CHECKED teardown (`_instance is self`) that stops a stale instance
    unseating the live one. The four posture-gated operations - link, sever,
    ownership transfer, lesser-to-normal upgrade - are now stated AS A SET with
    the shared rationale and the frame-before-book ordering consequence, rather
    than as four unrelated bullets a reader might 'fix' individually.
  EVIDENCE:
  - context_compass/system_docs/src_components.md
  - context_compass/system_docs/src_architecture.md
  IMPACT: Hollow C3 slots 50 -> 0. Both indexes regenerated and `--check` green
    (37 sections / 1866 lines; 129 sections / 7624 lines). Join unchanged and
    still clean: architecture 134 cited / 0 unresolved, components 571 / 0. All
    359 C1 ranges still match disk.
    CONTENT PRESERVATION: baseline captured BEFORE the first edit of this pass.
    49 components lines and 8 architecture lines unaccounted, and every one is a
    thin bullet REPLACED by a superset. Verified at content level per the gate's
    reshape rule by checking each removed bullet's key terms against the
    CONTAINING COMPONENT ENTRY rather than against the file as a whole - a
    whole-file check would pass on a claim that had migrated to the wrong
    component. 45 of 49 matched outright; the remaining 4 are rewordings that
    sharpened the claim (`Phase results (UnitOfWork sequences)` ->
    `Dict[str, Sequence[UnitOfWork]]`), confirmed by hand.
  NEXT: Mirror agreement is now the binding constraint on BOTH documents and
    cannot be fixed from the source side.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-02T14:35:00Z
  TYPE: VALIDATE
  CLAIM: RESCORED both documents from disk after the index rebuild.
    src_architecture 85 -> 89.5 (band B).
      Fidelity 4.5/5 (27.0, was 24.0) - deepened claims now carry openable
        references; still not 5, because the pre-existing prose was not
        re-derived line by line this pass.
      Contract completeness 5/5 (15.0). Depth 4.5/5 (13.5, was 12.0).
      Addressability 5/5 (15.0). Join integrity 5/5 (15.0).
      Mirror agreement 2/5 (4.0) - UNCHANGED and now the largest single loss.
    src_components 71.5 -> 83.5 (band C -> band B).
      Fidelity 4.5/5 (27.0, was 24.0).
      Contract completeness 5/5 (15.0, was 9.0) - 0 of 300 hollow slots.
      Depth 4.5/5 (13.5, was 10.5) - averaged per entry per the profile.
      Addressability 3/5 (9.0) - unchanged and STRUCTURALLY CAPPED, see the
        prior entry.
      Join integrity 5/5 (15.0). Mirror agreement 2/5 (4.0) - unchanged.
  EVIDENCE:
  - context_compass/agent_onboarding/default/design_engineer/policies/system_document_quality_rubric.md
  IMPACT: Both documents are now band B and usable as design inputs without a
    caveat. Every remaining loss is one of two things and NEITHER is fixable by
    editing these two files: Mirror agreement (10 points each) needs the
    test-side recomposition, and components Addressability (6 points) needs an
    owner ruling on the rubric anchor. Further editing of the source documents
    has a low ceiling from here - roughly 5 points each, all in Fidelity, and
    only by re-deriving prose that is not currently suspected of being wrong.
  NEXT: `tests_architecture.md` and `tests_components.md`. Both indexes are
    stale and both documents predate subsystems these now cover.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-02T15:40:00Z
  TYPE: VALIDATE
  CLAIM: FIDELITY AUDIT - the criterion I had scored 4.5 on the grounds that
    nothing looked wrong, which the rubric names as an anti-pattern. Built a
    symbol index from `src/` (every `class`/`def`) and checked every symbol the
    two documents claim, excluding regions that explicitly document removal.
    SEVEN WRONG CLAIMS FOUND. Every one would have wasted a future reader's time,
    and one was wrong about architecture, not just spelling:
    (1) THE SERIOUS ONE. Both documents claimed `Spellbook.notch_spell(...)`,
      `add_spell_into_spellindex(...)` and `remove_spell_from_spellindex(...)` as
      the transaction-backed SpellIndex verbs, in SIX places. Wrong on both
      counts. The verbs live on `Conduit` - `notch_spell` (conduit.py:4392),
      `add_to_spell_index` (:4482), `remove_from_spell_index` (:4560) - and two
      of the three names do not exist anywhere in the tree. Spellbook exposes NO
      public verb here; it owns the `_apply_notch` / `_apply_add_to_index` /
      `_apply_remove_from_index` seams that run inside the held transaction
      window. The corrected text now states the ownership split, because that
      split is the actual design: the Conduit admits the transaction (it owns the
      lineage), the Spellbook applies the membership change (it owns the index
      maps), and neither half is callable alone.
    (2) `_capture_phase8_11_codegen_ir_if_dirty()` - real name has no leading
      underscore.
    (3) `_get_conjure_hook_map()` - real name is the public static
      `SpellbookCreationSystem.get_conjure_hook_map(spellbook)`.
    (4) `_initialize_conduit_hooks()` - does not exist. Replaced with the real
      chain: `_ensure_local_conduit_hooks` -> `_collect_conduit_hook_chain` ->
      `_fire_conduit_hooks`.
    (5) `Meld._resolve_spell_for_live_creation_probe(...)` - does not exist and
      has no near match. Real entry is `describe_live_creation_status(...)`,
      abstract on the base.
    ROOT CAUSE, AND IT IS NOT IN THESE DOCUMENTS: three of the five wrong names
    were copied faithfully from STALE SOURCE DOCSTRINGS. The documents were doing
    their job; the source lied to them.
      - src/melder/aether/spellbook/spellbook.py:155 - the class AGENT_PURPOSE
        docstring advertises `notch_spell, add_spell_into_spellindex,
        remove_spell_from_spellindex` as Spellbook-owned. None of the three is a
        Spellbook method.
      - src/melder/aether/conduit/conduit.py:6171 - a `:meth:` cross-reference to
        `_initialize_conduit_hooks`, which does not exist.
      - src/melder/aether/spellbook/spellbook_creation_system.py:1256 - an error
        MESSAGE string naming `_get_conjure_hook_map`; the method it reports on
        is `get_conjure_hook_map`. A raised error will name a symbol the reader
        cannot find.
    NOT FIXED HERE - source changes do not belong to a documentation ticket, and
    silently editing them would hide the finding. They need their own ticket, and
    until then any regeneration of these sections can re-introduce the same five
    names from the same three docstrings.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md
  - context_compass/system_docs/src_components.md
  IMPACT: Symbol claims re-audited after the fix: architecture 2 residual flags,
    components 9, and ALL of them verified legitimate - stdlib calls
    (`sys._is_gil_enabled`), real enum members (IGNORE, PLAIN, SPELL, METHOD,
    UNWIND), and classes the documents correctly describe as REMOVED
    (`IrisLoggerFactory`, `StdLoggerFactory`, `Conduit.get_mutation_research`).
    Preservation: 19 unaccounted lines across both documents, every one a line
    of a corrected wrong claim.
  NEXT: A source ticket for the three stale docstrings.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-02T15:55:00Z
  TYPE: IMPLEMENT
  CLAIM: C2 SUBCOMPONENTS CATALOG - 62 entries that no gate and no rubric
    criterion has ever measured, which is exactly why I had not looked at them.
    Audited: all 62 carry `Parent Component` and at least one source path, median
    14 lines of content, and the de facto shape is `Purpose` /
    `Contract/Interface` / `Data Structures` / `Concurrency/Threading` at 59+ of
    62. Not the neglect the pattern predicted - but UNDOCUMENTED, and an
    undocumented convention is one a reader has to reconstruct by diffing entries.
    - The catalog now opens with a `HOW TO READ THIS CATALOG` preamble stating
      the shape, stating that the instructions define NO C2 contract so this is
      the document's own convention, and stating that the three builder/engine
      entries carrying `Invariants/Guarantees` instead of `Data Structures` are a
      DELIBERATE variant rather than drift.
    - Those three were the only entries missing `Concurrency/Threading`, the
      field a reader can least afford to infer. Filled from source, and the
      answers were not uniform: `NexusFrameBuilder` has NO lock and is safe by
      CALLER CONFINEMENT (sharing it across threads is unsupported, not merely
      slow); `FrameACLBuilder` holds an RLock whose justification the source
      states against 3.14t - grouped draft-field mutation is not incidentally
      atomic without a GIL; `CodegenSystem` holds one RLock per room protecting
      the validate-before-execute ordering its own invariant asserts.
  EVIDENCE:
  - context_compass/system_docs/src_components.md
  IMPACT: The catalog is now self-describing, so a reader arriving after
    compaction can tell a required field from an accidental one without diffing
    62 entries. Indexes regenerated, `--check` green (37 sections / 1890 lines;
    129 sections / 7716 lines). Join still 0 unresolved on both documents; all
    359 C1 ranges still match disk.
  NEXT: Test-side recomposition remains the largest open gap.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-02T16:40:00Z
  TYPE: VALIDATE
  CLAIM: CITATION AUDIT - the `path:line` references inside `EVIDENCE:` blocks,
    which NOTHING in this system has ever checked. The index tool validates the
    document's own structure; the join validates that cited FILES resolve. Neither
    looks at line numbers, so a citation rots in the one way that is invisible:
    the file still exists, the reference still parses, and it points at the wrong
    code with full confidence.
    NINE WRONG OF 81.
    (1) FIVE citations pointed into `spell_compiler.py` at lines 1966-3787. That
      file is 693 lines. The compiler was decomposed into `phases/` and
      `artifact_processor/` subpackages and the ranges were never remapped, so
      they had been unresolvable for some time while still reading as evidence.
      Re-derived to `spell_compiler_artifact.py:146/203/322` for the IR-freshness
      bit and `phases/shared_compiler_executions.py:1342/1432-1451/1435/1477` for
      capture, set-flush and reset.
    (2) TWO were IN BOUNDS and still wrong, which is the more dangerous shape
      because a bounds check passes them: `change_control_manager.py:1403-1475`
      cited for `is_root_dirty`, which is at :1595, and `meld.py:502-532` cited
      for `_gated_validation_required`, which is at :760. Neither range contained
      the symbol it was cited for.
    (3) FOUR were stale by tens of lines or off by one -
      `spellbook.py:6115-6121` (Conduit hook prose, cited for conjure's
      effective-mode resolution, really :6148), `conduit_ward.py:974` (the guard
      is acquired at :973, the lookup is :974 - the claim was about the ORDER),
      `mutation_research.py:590,668,3380` (all three wrong; the emission-lock
      ordering lives at :220/:804-830/:905-944/:3874), and two def citations off
      by one.
    (4) TWO BARE FILENAMES, `bind.py:363` and `bind.py:364`, with no path at all -
      unresolvable by any automated check, and THE TWO DOCUMENTS DISAGREED WITH
      EACH OTHER about the same call site. The call is on 364; `src_components.md`
      said 363. Cross-document contradiction inside the source pair, which no
      gate covers - the rubric's Mirror criterion only pairs src with tests.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md
  - context_compass/system_docs/src_components.md
  IMPACT: All 81 citations now in bounds, and every corrected one was verified to
    CONTAIN the symbol it is cited for rather than merely to sit in the right
    file. Indexes regenerated, `--check` green (38 sections / 1930 lines; 130
    sections / 7777 lines). Join unchanged, 0 unresolved. All 359 C1 ranges still
    match disk. Preservation: 8 unaccounted lines, every one a stale citation
    that was replaced.
  NEXT: The two source documents should be checked against each other routinely,
    not only against the test side.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-02T16:55:00Z
  TYPE: IMPLEMENT
  CLAIM: The citation check now TRAVELS WITH THE DOCUMENTS. Both
    `src_architecture.md` and `src_components.md` gained a
    `### Verifying the path:line citations in this document` subsection under
    `## Indexing`, carrying a runnable recipe, the 2026-08-02 audit result as the
    worked example, and the warning that in-bounds is necessary but NOT
    sufficient - with the two in-bounds-but-wrong citations named as the reason.
    Fixing nine citations helps once. A reader who can re-run the check helps
    every time, and this is the lane that rots fastest because it rots on SOURCE
    edits rather than document edits - nobody touching the document is present
    when it breaks.
    THE RECIPE EARNED ITS PLACE IMMEDIATELY: run once as written, it found the
    two bare `bind.py:NNN` references that the audit's own `src/`-anchored regex
    had missed entirely, including the cross-document contradiction. The embedded
    version is deliberately broader than the one I audited with.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md (## Indexing)
  - context_compass/system_docs/src_components.md (## Indexing)
  IMPACT: Both documents are now self-verifying on the one axis no tool covers.
    Recommend the other agent lift this into
    `system_document_build.md` as a standard gate, since it is document-agnostic
    and hardcodes no source root.
  NEXT: Test-side recomposition; the same citation rot is guaranteed there and is
    WORSE, because test paths appear in no graph and nothing checks them at all.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-02T17:45:00Z
  TYPE: VALIDATE
  CLAIM: Four more audits of things nothing checks. Three came back CLEAN, and
    recording that matters as much as the failures - an unaudited section and an
    audited-clean section look identical to the next reader.
    (1) NUMERIC CLAIMS - every count in both documents, re-measured against
      source: lock acquisition sites (63), logger call counts (19/1 in aether,
      77 in conduit, 79/11 in conduit_ward), subpackage module counts (acl
      builder 4 / configurations 27 / validator 10 / 41 beneath top level;
      crystal_analysis custody 5 / strategies 5 / preflight 12 / 22 beneath),
      `spell_compiler.py` at 693 lines, and the inherited 574-module package
      total. ALL 15 CORRECT, including the inherited ones.
    (2) UNKNOWNS - the four `SpellState` advanced flags are STILL genuinely
      unknown: each is defined in `spell_state.py` and
      `spell_state_change_reason.py` and has ZERO producer or use sites in
      runtime code. The entry's `blocked` status and its MR-runtime-seam
      attribution are accurate, so it stays. The ARTIFACT OWNERSHIP block also
      verified: all nine slots are declared on `SpellCompilerArtifact`, and all
      four publisher classes exist.
    (3) DIAGRAMS - every symbol a diagram names that appears nowhere else in the
      document was checked against source. `_convert_to_normal_conduit` and
      `create_new_preset_spellbook` are real; the rest are diagram-internal
      labels. Terminology aligned; nothing to fix.
    (4) ONE REAL DEFECT, AND IT IS A DEFECT OF THE WORST KIND - a false
      assurance. Both `## Unknowns` sections carried: "re-verified 2026-07-25:
      every source path cited in this document resolves on disk AND NO RENAMED
      SYMBOL SURVIVES AS A LIVE CLAIM." The second half was untrue. Yesterday's
      audits found five renamed or invented symbols still cited as live and nine
      `path:line` citations pointing at the wrong code. A reader trusting that
      stamp would have skipped exactly the check that was needed.
      The stamp now states what a path sweep actually covers and why it is not a
      symbol sweep: A PATH RESOLVES WHENEVER THE FILE EXISTS, WHICH STAYS TRUE
      THROUGH EVERY RENAME INSIDE THAT FILE. Both halves are now genuinely
      re-verified as of 2026-08-02, by different means, and the entry says which
      means. Closing instruction added: do not widen a future stamp beyond what
      was actually run.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md (## Unknowns)
  - context_compass/system_docs/src_components.md (## Unknowns)
  IMPACT: A verification stamp is a load-bearing claim - it tells the next reader
    what they may skip. An overstated one is worse than none, because it converts
    a gap into a gap nobody will look for.
  NEXT: Same question for the test-side documents, which carry their own stamps.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-02T18:00:00Z
  TYPE: IMPLEMENT
  CLAIM: GLOSSARY RE-ABSORBED into `src_architecture.md` - 77 lines, 42 terms,
    restored ahead of `## System Boundary and External Interfaces`.
    It was moved to the patch lane during the 2026-08-01 recomposition on the
    reading that the Required Section Contract was a whitelist. IT IS NOT. The
    instructions state it is a MINIMUM IN A FIXED RELATIVE ORDER and that other
    sections are permitted and common - the exact misreading the skill now warns
    costs roughly 1,200 lines. This is that misreading being reversed with the
    content it actually cost, not just acknowledged in a handoff note.
    Verified before restoring rather than restored on faith: ALL 42 GLOSSARY
    TERMS RESOLVE TO REAL CLASSES IN `src/`. A glossary of stale names would have
    been worse than no glossary.
    The migration file now holds a POINTER, not a second copy. Two copies of a
    glossary drift, and only one of them is the document anyone maintains.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md
  - context_compass/system_docs/patches/active/system_doc_recompose_2026_08_01/component_material_for_migration.md
  IMPACT: Architecture now carries 18 H2 sections, with all 17 contract sections
    still present AND in contract order - a non-contract section between them
    does not disturb relative order, which is the point of the rule being about
    order rather than membership. Index regenerated, `--check` green (39 sections
    / 2029 lines). Components index green (130 sections / 7791 lines).
    Preservation: 4 unaccounted lines per document, all four being the rewrapped
    old verification stamp, which the replacement quotes verbatim in context.
  NEXT: The remaining patch-lane material is ~840 lines of promoted patch blocks
    and per-subsystem responsibility narratives. Each needs the same judgement
    the glossary got - verify first, then re-absorb or keep out with a reason.
    Do NOT bulk-restore: the glossary earned its way back by being 42-for-42
    accurate, and the promoted patch blocks have not been checked.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-02T18:50:00Z
  TYPE: VALIDATE
  CLAIM: STRUCTURAL ALIGNMENT ANSWERED PROPERLY - re-read the build sequence,
    preservation gate, quality gate and validation commands in both
    `*_instructions.md`, plus the heading-shape rules in
    `system_document_build.md`, then measured EVERY rule rather than answering
    from memory. That surfaced a real break that eight prior passes missed.
    THE CORE-SET INVARIANT WAS VIOLATED IN BOTH DIRECTIONS.
    `src_components_instructions.md` defines Core as "the deduplicated union of
    every `Key Files (C1)` list in the C3 catalog", and says the set MAINTAINS
    ITSELF - change a component's key files and core follows. It had not been
    following:
      - 40 entries were measured into Core that NO component claimed: the deep
        `nexus/acl/**` profile, validator and configuration modules. The Frame
        ACL entries state explicitly that these are not key files, so Core was
        carrying 40 modules its own catalog disowned.
      - 18 files that components DO claim were absent from Core, and 14 OF THOSE
        18 WERE MY OWN DRIFT - the 2026-08-02 directory expansions added
        crystallizer paths to `Key Files (C1)` and never added them here. Fixing
        the directory-citation rule created a fresh violation of a different
        rule, which is exactly the failure mode of checking rules one at a time.
      - 2 records were duplicated, in a set the instructions call deduplicated.
    Reconciled to equality: Key Files union 201, C1 map 201, symmetric
    difference 0.
    NOTHING WAS DESTROYED, AND THE TWO HALVES WENT TO DIFFERENT PLACES BECAUSE
    THEY ARE DIFFERENT THINGS. The 40 MODULES stay catalogued with purpose text
    in `### Full Package Inventory (exhaustive, retained)`. Their MEASURED
    RANGES, which that inventory does not carry, went verbatim to the patch lane
    so a later promotion does not remeasure. My first draft of the note claimed
    the inventory preserved both; it does not, and the note was corrected before
    it could become the next false assurance.
  EVIDENCE:
  - context_compass/system_docs/src_components.md (## C1 Code Map (Core))
  - context_compass/system_docs/patches/active/system_doc_recompose_2026_08_01/component_material_for_migration.md
  IMPACT: FULL CONFORMANCE MATRIX NOW PASSES ON BOTH DOCUMENTS - 11 shared checks
    each (one H1; contract sections present and in order; no wrapped headings; no
    duplicate section names; no directory and no test path in Key Files; Key
    Files resolve to the graph; C1 carries all five fields; C1 ranges match disk;
    C1 deduplicated; C1 resolves to the graph) plus, for components, 25/25 C3
    entries carrying all twelve fields, Core == union of Key Files, and the
    exhaustive inventory retained. Architecture: 39 sections / 2029 lines,
    components: 130 sections / 7691 lines, both `--check` green.
    Also verified against `system_document_build.md`: architecture has NO
    container H2 at all (its rule), components keeps every entry at H3 with the
    load-bearing `Component: ` / `Subcomponent: ` prefixes, and the diagram
    contract holds.
    PRESERVATION ARITHMETIC EXACT: 7 unaccounted lines, all explained -
    2 deduplicated records with their field lines, and the
    `verified_at: 2026-08-02T13:00:45Z` count moving 223 -> 181, which is
    223 - 40 evicted - 2 deduplicated. It reconciles to the line.
  NEXT: The answer to "are we structurally aligned" is now YES for both source
    documents, and it was NO before this pass despite every earlier check
    passing. The test-side pair has never been measured against any of this.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Acceptance Criteria
- Both docs match their Required Section Contract in order.
- Both indexes regenerate and `--check` green.
- No content deleted; migrated material lands in `src_components.md`.
- Graph replaced by `src_graph.md` + `src_graph_index.md`.

## Context / Handoff Summary
Architecture done and verified. Components next; it consumes the migration file
in the patch lane. Graph last - `src_graph.json` / `readable_src_graph.json` are
the retired artifacts.
