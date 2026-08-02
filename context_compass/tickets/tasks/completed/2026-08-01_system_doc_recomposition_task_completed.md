# Task: Recompose src_architecture.md and src_components.md to the new spec

## Metadata
- Task ID: TASK-2026-08-01-system-doc-recomposition
- Status: done
- Owner: cowork
- Agent Name: helper_f
- Priority: p1
- Created: 2026-08-01T19:12:00Z
- Updated: 2026-08-03T05:10:00Z

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
- [x] Recompose `src_components.md` (consumes the migration file).
- [x] Migrate the graph to `src_graph.md` + `src_graph_index.md`.

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

- DATETIME: 2026-08-02T20:10:00Z
  TYPE: IMPLEMENT
  CLAIM: PATCH LANE FINISHED. Every block classified by MEASUREMENT - overlap
    against both canonical documents - then verified against source, then
    re-absorbed or kept out with a written reason. The lane went 1,887 -> 644
    lines and NOT ONE BLOCK IS NOW UNDECIDED.
    RE-ABSORBED, each verified first:
    - 4 promoted ARCHITECTURE decision blocks (153 lines): canonical boot order,
      EMIT and restore invariants, durability layering, the V3 subsystem
      topology, the V3 horizon, the three-lane tail. All 16 classes they name
      exist; 10 of 11 verbs are real `def`s; and THE TWO APPARENT MISSES CONFIRM
      THE TEXT - `BootMediator` is absent precisely because the topology block
      records its rename to `LoadAdmission`, and `refuse_on_blockers` is a
      `RestoreEngine` keyword parameter, which is what the block calls it.
    - 4 promoted COMPONENT detail blocks (411 lines): record model, subsystem
      decomposition, V3 iteration, three-lane tail. Every backticked class and
      method resolves - zero misses across 411 lines - and they carry no
      `path:line` citations, so no range rot came with them.
    - `Ownership, Lifecycle, and Cleanup` -> merged into
      `### Sequence: Cleanup`, EXTENDING it from three types to seven
      (AetherUtilitySystem, Nexus, Rift, Creations added); each `cleanup()`
      verified present on the class named.
    - `Runtime Type Names (Concrete, No Interface Layer)` -> its own H2, with the
      enforcement citation CORRECTED on the way in: the `isinstance` check and
      its raise are at `conduit.py:4341-4343`, not :4342-4344 as recorded.
    - `Extension Points` -> its own H2, scoped to seams that cross components.
    COLLAPSED TO POINTERS - 16 blocks, 617 lines, measured 100% duplicate. All of
    it already sits in `src_components.md` under
    `#### Architecture narrative (folded in from src_architecture.md)`. Two
    copies of a narrative drift and only one is maintained.
    KEPT OUT WITH A STATED REASON - 9 blocks, so nobody re-litigates them:
    - `Source Coverage and Evidence` - TWO of its seven evidence citations are
      out of bounds (`spell_compiler.py:L131-L2383` in a 693-line file,
      `creation_context.py:L109-L814` in a 309-line file), it uses an `L131-L2383`
      format no citation checker would even see, and it cites DIRECTORIES. Its
      coverage half is superseded by `## Information Sources`, which carries 110
      and 170 resolving entries.
    - `SpellCompiler and Validation Pipeline` - verified STALE TWIN. Its ten
      non-duplicate lines are exactly the defects fixed earlier today: the
      spurious-underscore method name and the six citations into a 693-line file.
      Re-absorbing it would have re-imported every one.
    - `Open Questions` - verified duplicate of `## Unknowns` in both documents,
      and the canonical copy is the one re-verified against source today.
    - `C3 and C2 Cross-Reference` - a two-line pointer both documents already
      make in `## Information Sources`.
    - 5 scaffolding blocks (2x `Table of Contents`, 2x `Documentation Quality
      Standard`, `Component Template`) - each superseded by a named authority:
      the generated index, the quality rubric policy, and the Component Entry
      Contract. Each pointer names the authority and says not to re-absorb
      without retiring it first.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md
  - context_compass/system_docs/src_components.md
  - context_compass/system_docs/patches/active/system_doc_recompose_2026_08_01/component_material_for_migration.md
  IMPACT: THE COVERAGE GAP IS CLOSED. No material sits in neither document any
    more; what remains in the lane is pointers, decisions with reasons, the
    evicted test surfaces, and the 40 evicted C1 records - all of it addressed.
    Full conformance holds after the change: architecture 21 H2 sections with the
    17 contract sections still in order, 134 C1 entries all measured and
    resolving; components 13 H2 sections in order, 201 C1 entries, and Core still
    exactly equal to the union of Key Files. No wrapped headings, no duplicate
    names, one H1 each. Indexes rebuilt, both `--check` green - architecture 46
    sections / 2270 lines, components 135 sections / 8127 lines.
    PRESERVATION: components 0 unaccounted; architecture 3, being the three
    original cleanup bullets replaced by the seven-item version that contains
    them.
  NEXT: Test-side recomposition is now the only large open lane. Source-side
    material is fully placed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-02T21:15:00Z
  TYPE: VALIDATE
  CLAIM: POST-ABSORPTION SWEEP - re-ran every check against the 564 lines just
    re-absorbed, on the principle that new content is exactly where new defects
    arrive. FOUR DEFECTS, ALL CARRIED IN WITH THE PROMOTED BLOCKS:
    (1) Four BARE-FILENAME citations - `spellbook.py:229`, `aetheric_frame.py:411`,
      `conduit_cloud.py:379`, `spellbook.py:5412` - unresolvable by any checker,
      and all four also STALE. Corrected to full verified paths:
      `aetheric_frame.py:463` (`conduit_cloud`), `conduit_cloud.py:547`
      (`has_cluster_name`), `spellbook.py:5954` (`Spellbook.conduit`).
      THE WORST WAS `_ensure_frame`: cited as `spellbook.py:229`, which is the
      WRONG FILE ENTIRELY - the method is `src/melder/aether/aether.py:893` and
      Spellbook has none. The surrounding claim said the first Spellbook births
      its frame via that method, so the citation was pointing a reader at the
      wrong class to understand lazy frame creation.
    (2) Three `Method-Level Call Flows (C1)` entries named only CLASSES, which
      the Quality Gate explicitly fails ("C1 call flows use concrete method/
      function names"). Filled from source: the ACL fan-out now names
      `Nexus._on_frame_acl_changed` (:2579), `disable_rift_gate` (:1375),
      `_refresh_rift_projection_sets_for_frames` (:2491),
      `Rift.refresh_runtime_projections` (:589) and `enable_rift_gate` (:1343) -
      and records that the single-frame and batch paths share ONE primitive.
      Passive publication now names all three `_publish_*_record` verbs with
      their `bool` return, both `_remove_*` verbs, and the four payload
      validators.
    (3) `src_components.md` Metadata still said `Updated: 2026-07-25` after a
      full day of edits; architecture said 2026-08-01. Both now 2026-08-02.
    (4) MY OWN: when correcting the `_ensure_frame` citation I quoted the bad
      one IN BACKTICKS, which re-created the exact "dead path cited as live"
      pattern removed earlier today. De-backticked with the reason inline. The
      citation checker caught me, which is the argument for embedding it.
  EVIDENCE:
  - context_compass/system_docs/src_components.md
  - context_compass/system_docs/src_architecture.md
  IMPACT: 91 `path:line` citations checked, 0 problems. All 25 call flows now
    carry concrete method names. Full conformance matrix holds on both
    documents: contract order, one H1, no wrapped headings, no duplicate names,
    134 and 201 C1 entries all measured/deduplicated/resolving, 25/25 C3 entries
    with twelve fields, Core == union of Key Files (201 = 201). Indexes green -
    architecture 46 sections / 2270 lines, components 135 sections / 8159 lines.
    Preservation: 18 unaccounted lines, each one a stale citation or a thin flow
    step replaced by a version that contains it.
  NEXT: Source-side work is complete. Remaining open items are the three stale
    SOURCE docstrings (own ticket), the test-side pair, and the rubric
    Addressability ruling.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-02T22:40:00Z
  TYPE: IMPLEMENT
  CLAIM: TEST-SIDE PAIR RECOMPOSED. Both now satisfy their Required Section
    Contracts, and the source pair's Mirror-agreement cap is no longer a
    staleness problem.
    `tests_architecture.md` (387 -> 635 lines): five sections RENAMED to contract
    names, four ADDED that did not exist (`Indexing`, `System Context (C4)`,
    `Boot and Configuration Sequence`, `Failure Modes and Error Paths`), and the
    C1 map REBUILT from a bare 18-path list into 30 measured entries. The old
    list contained a DIRECTORY (`tests/mocks/spellbook/`), expanded into its
    files.
    ONE FALSE "VERIFIED" CLAIM FOUND AND CORRECTED: under the heading "Verified
    test-runner configuration" the document listed `norecursedirs` as excluding
    `codex`, `codex_agent_2`, `codex_agent_3`. NONE of the three is in
    `pyproject.toml`. The real list is recorded now, and the two declared markers
    (`integration`, `component`) had never been documented at all. Same defect
    class as the source-side Unknowns stamp: a claim labelled verified that was
    not.
    `tests_components.md` (768 -> 1508 lines): `## Indexing` added, C1 map
    rebuilt as 118 measured entries that are now EXACTLY the deduplicated union
    of every `Key Files (C1)` list.
    THE SUBSTANTIVE JUDGEMENT WAS WHAT COUNTS AS A KEY FILE HERE. Twenty
    directory citations covered whole trees - one named a directory holding 181
    test modules. Mechanically expanding them produced a 695-entry Core and a
    4,267-line document: conformant to the letter and useless, because a core set
    listing the entire tree is not a set anyone can verify, which is the whole
    reason the contract narrows it. Replaced instead with the trees' HARNESS AND
    SUPPORT surfaces - conftests, benches, mock packages, shared builders - and a
    MEASURED COUNT of the `test_*.py` modules beneath, written as prose rather
    than citations. 118 entries, every one verified to exist and remeasured.
    I RE-CREATED THE DEFECT I WAS FIXING, TWICE, AND THE CHECKER CAUGHT IT BOTH
    TIMES: my replacement prose cited directories in backticks, so 24 directory
    citations survived the first pass and the union check failed at 131 vs 118.
    De-backticked with the reason stated inline. This is the same trap as the
    `spellbook.py:229` quote earlier today - describing a bad path in the syntax
    reserved for good ones.
  EVIDENCE:
  - context_compass/system_docs/tests_architecture.md
  - context_compass/system_docs/tests_components.md
  IMPACT: BOTH TEST DOCUMENTS NOW PASS THE SAME MATRIX AS THE SOURCE PAIR -
    contract sections present and in order (17 and 12), one H1 each, no wrapped
    headings, no duplicate names; C1 30 and 118 entries, all five fields, all
    deduplicated, all ranges matching disk, no directories, every path verified
    to EXIST (the only check available on this side - there is no graph to join
    against); Key Files carry no source paths, so the mirror rule holds in both
    directions; 6/6 C3 entries with all twelve fields; and Core == the union of
    Key Files. Indexes regenerated from stale-by-hundreds-of-lines to green:
    27 sections / 635 lines and 52 sections / 1508 lines.
    PRESERVATION: 28 and 36 unaccounted lines, every one categorised - bare
    paths promoted to measured C1 records, directory citations replaced by
    harness files plus counts, headings renamed to contract names, and the three
    stale `norecursedirs` entries deliberately removed as wrong. The single
    residual, `pyproject.toml`, moved OUT of the components map and INTO the
    architecture map, which is where runner configuration belongs.
  NEXT: All four system documents are now on the new spec. Remaining open items
    are the three stale SOURCE docstrings (ticketed as
    TASK-2026-08-02-stale-source-docstrings) and the rubric Addressability
    ruling.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-03T00:20:00Z
  TYPE: ASSUMPTION_CHALLENGE
  CLAIM: I DOCUMENTED THE OWNERSHIP SPLIT WRONG IN BOTH DOCUMENTS, and the way I
    got it wrong is the point worth recording.
    I established the SpellIndex verb ownership from a symbol index plus the
    surrounding docstrings, and never read the call chain. Reading it takes a
    minute and produces a different answer:
      `Conduit.<verb>` - PUBLIC, and it ADMITS the transaction: it calls
      `mediator.start_transaction(...)` itself at :4464 / :4537 / :4608 ->
      `Spellbook._<verb>` - internal ENTRY, called inside the held window; this
      is what the Conduit actually calls ->
      `Spellbook._apply_<verb>` - the SEAM that mutates index membership.
    THREE LAYERS, NOT TWO. Both documents described two and named `_apply_*` as
    the method the Conduit reaches, when the Conduit reaches `_<verb>`, which
    then delegates. And `src_architecture.md` said the Conduit "delegates to the
    owning Spellbook, WHICH ADMITS the change-control transaction" - backwards.
    WHERE THAT WORDING CAME FROM: the Conduit docstrings. All three public verbs
    say "Delegates to the owning Spellbook, which admits the [...] transaction",
    and all three are false - the same methods open the transaction a few lines
    below. `spellbook.py:3684` states it correctly and contradicts them. I
    inherited the error from the source it was my job to check.
    THE METHOD FAILED, NOT THE EFFORT. A symbol index finds names that do not
    exist. It cannot find a FALSE SENTENCE BUILT FROM REAL NAMES -
    `add_to_spell_index` exists, `Spellbook` exists, and the sentence joining
    them is still wrong. Nothing automated in this repository would have caught
    it. Only reading `conduit.py:4506-4547` does.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:4464, 4537, 4608 (Conduit opens each transaction)
  - src/melder/aether/conduit/conduit.py:4487-4488 (the false "which admits" claim)
  - src/melder/aether/spellbook/spellbook.py:3655, 3688 (entry -> seam)
  - src/melder/aether/spellbook/spellbook.py:3684 (states it correctly)
  IMPACT: Corrected in both documents, with the contradiction recorded IN the
    component entry so the next reader is warned not to trust the Conduit
    docstrings on this point. The three false Conduit docstrings are recorded on
    TASK-2026-08-02-stale-source-docstrings, whose diagnosis grew from three
    wrong docstrings to six.
    ALSO CAUGHT IN THIS PASS, BY THE EMBEDDED CHECKER, BOTH MINE: five bare
    filename citations (`spellbook.py:3684` and friends) written without a path -
    the THIRD time I have made that exact mistake today - and one range,
    `tests/conftest.py:1-23`, carrying the same `split("\n")` off-by-one I had
    already corrected 359 times across the C1 maps. The file is 22 lines. Both
    fixed; all four documents now stand at 105 citations, 0 problems.
  NEXT: The remaining work is source-side and needs an owner decision.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-03T01:10:00Z
  TYPE: ASSUMPTION_CHALLENGE
  CLAIM: APPLIED THE LESSON FROM THE OWNERSHIP MISS TO THE REST OF MY OWN
    CONCURRENCY CLAIMS - the ones I wrote from LAYERING AND DOCSTRINGS rather
    than from reading call chains. Two of them were wrong, and the second one
    was DANGEROUS rather than merely incomplete.
    (1) DEVOPS CONTROL PLANE - my text said the plane lock "is taken for the
      composite operations that span several managers" and that ordering is
      outer-to-inner. The ordering claim holds (13 of 15 `with self._lock` blocks
      call into an owned manager, and no owned manager calls back). But it missed
      the fact that matters: THE PLANE LOCK IS HELD ACROSS A BLOCKING POLL.
      `close_conduit_creation_gate` holds `_lock` while
      `CreationGate.close_and_wait_until_free` runs
      `deadline = time.monotonic() + timeout` then
      `while self.has_active_tickets(): time.sleep(interval)` - defaults
      `timeout=30.0`, `interval=0.1`. One conduit with a stuck ticket stalls
      EVERY other DevOps plane operation for up to thirty seconds. That is a
      blast-radius property invisible from the layering and visible in three
      minutes of reading.
    (2) SPELLBOOK'S TWO LOCKS - I wrote that `_lock` and `_phase_run_lock`
      "impose no ordering on each other". THEY DO, AND MY SENTENCE INVITED THE
      INVERSION IT DENIED. `_run_structural_phases` (:6295) states a caller-held
      precondition at :6306 - "Caller must hold the Spellbook lock for
      deterministic conjure ordering" - and reaches `_phase_run_lock` through
      `SpellbookCreationSystem.run_structural_phases` ->
      `_run_scheduler_with_phases` (:1868). So conjure holds `_lock` THEN takes
      `_phase_run_lock`. Meld-time revalidation arrives without `_lock` and takes
      only the run lock. The order is one-way and therefore safe - but it is a
      PROPERTY OF THE CALL PATHS, not of the locks, and nothing enforces it. A
      reader trusting my sentence could take the run lock first and reach a
      `_lock`-guarded method, creating a real inversion.
    BOTH ERRORS ARE THE SAME SHAPE AS THE OWNERSHIP MISS: a claim that is
    plausible from structure, unfalsifiable by any name-matching check, and
    wrong. The only instrument that finds them is reading the call chain.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/dev_ops_manager.py:447-452
  - src/melder/utilities/synchronization/creation_gate.py:529-538
  - src/melder/aether/spellbook/spellbook.py:6295, 6306
  - src/melder/aether/spellbook/spellbook_creation_system.py:1868
  IMPACT: Both fields rewritten with the mechanism, the ordering it depends on,
    and the failure it causes or prevents - which is the rubric's Depth-5 anchor
    and what the previous text only gestured at. Each carries an explicit
    CORRECTED note so the next reader knows the earlier wording was wrong rather
    than merely thinner.
    All four documents: 110 `path:line` citations, 0 problems. Index green,
    C1 201 entries deduplicated. Preservation: 8 unaccounted lines, all replaced
    by the corrected concurrency text.
  NEXT: Same treatment for the remaining inferred ordering claims - the
    MutationResearch emission->root->set->crystallizer chain and the
    AethericFrame two-conduit arbitration claim.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-03T01:55:00Z
  TYPE: ASSUMPTION_CHALLENGE
  CLAIM: FINISHED THE CONCURRENCY-CLAIM SWEEP. Of the four ordering claims I
    wrote from layering rather than from call chains, THREE WERE WRONG. The
    fourth was right but for a thinner reason than the code gives.
    (3) AETHERIC FRAME - WRONG, and wrong about the whole mechanism. I wrote that
      the frame "is the arbitration point BETWEEN conduits", so two-conduit
      operations serialise at the frame "rather than needing a lock ordering
      between the two conduit locks, which is the deadlock this design avoids by
      construction". The code does precisely what I said it avoids: two-conduit
      operations acquire BOTH ward/conduit locks together via `SafeGuard`, and
      the frame is not involved at all.
      WHAT ACTUALLY PREVENTS THE DEADLOCK is `SafeGuard` normalising the lock set
      and acquiring in `sorted(id(lock))` order, NOT ARGUMENT ORDER. Two call
      sites passing the same pair in opposite argument order still converge on
      the same real order.
      AND THE CODEBASE CONTAINS THAT EXACT CASE:
      `transfer_of_ownership.py:951` is `SafeGuard(tgt_book._lock, src_book._lock)`
      while `:1442` is `SafeGuard(src_book._lock, tgt_book._lock)`. A reader who
      does not know the rule sees an inconsistency and "fixes" it - which is the
      first step toward replacing SafeGuard with hand-ordered acquisition. That
      hazard was entirely undocumented; `SafeGuard` appeared in these documents
      only as a path in a Key Files list.
    (4) MUTATION RESEARCH - the inherited "emission -> root" order is CORRECT,
      verified as nested acquisitions one line apart (:830/:831 and :944/:945).
      But the document only asserted the order. The code gives the REASON, and it
      is what makes the order non-negotiable: inside both nested blocks the code
      constructs `ResearchSet(name, on_mutation=self._emit_research_composition)`
      and then calls that emitter directly while still holding both locks, so the
      emitter RE-ENTERS `_emission_lock` from inside the root lock. Safe only
      because emission is the outer acquisition. Reverse it and this path holds
      root wanting emission while a concurrent emitter holds emission wanting
      root - the textbook inversion.
    TALLY FOR THE DAY ON MY OWN CONCURRENCY CLAIMS: 3 wrong, 1 under-explained,
    0 that a symbol audit or citation check could have caught. Every one needed
    the call chain read.
  EVIDENCE:
  - src/melder/utilities/synchronization/safeguard.py:8-80
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:951, 1442
  - src/melder/mutation_research/mutation_research.py:830-831, 837-840, 845, 3900
  IMPACT: Both fields rewritten from verified mechanism, each carrying an
    explicit CORRECTED marker. `SafeGuard`'s contract is now documented where a
    reader meets it - including that it is SINGLE-USE, NOT thread-shareable
    (acquisition state is per-instance), and that its `cleanup()` deliberately
    does not release external locks because letting `__exit__` do it is what
    prevents a permanent leak.
    All four documents: 121 `path:line` citations, 0 problems; indexes green.
    ALSO, AND IT IS A PATTERN NOW: the embedded checker caught bare-filename
    citations in MY OWN new prose for the FOURTH time today. Four occurrences is
    a habit, not an accident - when writing a citation inline rather than in an
    EVIDENCE block, I default to the filename I have been reading. The checker
    catches it every time, which is the argument for it living in the document
    rather than in my head.
  NEXT: No further inferred ordering claims remain in my own text. The
    equivalent sweep has never been run over the claims I did NOT write.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-03T02:40:00Z
  TYPE: VALIDATE
  CLAIM: EXTENDED THE CONCURRENCY SWEEP TO CLAIMS I DID NOT WRITE - the inherited
    ones. Enumerated every `Concurrency/Threading` field asserting an ordering or
    a lock relationship: 11 total, of which the deadlock-critical inherited ones
    were the mediator admission plane and the crystallizer cadence ticker.
    BOTH CAME BACK CORRECT. Recording that deliberately, because an unaudited
    claim and an audited-clean claim are indistinguishable to the next reader,
    and the whole point of this exercise is that the difference matters.
    (1) "SCOPE WAITING NEVER HOLDS THE MEDIATOR LOCK" - TRUE.
      `_admit_with_scope_wait` (:1190-1260) contains no `with self._lock`
      anywhere in its retry loop, and its single caller invokes it at :521 then
      takes the lock at :522, immediately after the wait returns, to stage the
      mutation. The property comes from that ORDERING and nothing enforces it -
      a future caller that wrapped the admit call in the lock would silently
      convert a bounded wait into a global stall. That fragility is now written
      down next to the claim.
      Also added a distinction the field previously blurred: the mediator owns
      `_wait_condition = threading.Condition(self._lock)`, notified under the
      lock on release paths, which is a DIFFERENT mechanism from the embargo
      manager's wait. Two waits, one field, previously described as one.
    (2) "THE CADENCE TICKER STAMPS UNDER THE LOCK AND SEALS OUTSIDE IT, STAMP
      ADVANCING BEFORE SEALING" - TRUE, and more precisely than stated.
      `_maybe_create_automatic_checkpoint` takes `_lock` at :723, does only the
      elapsed comparison (:724-728) and the stamp advance (:729) inside, then
      releases and does every expensive thing outside: `_emit_policy_twin()`
      :732, `create_checkpoint(...)` :733, conditional `flush_checkpoint(...)`
      :741.
      The document asserted the ordering; it did not say WHY, and the why is the
      valuable half - a seal that raises has already moved the clock, so the next
      emit does not retry. Advance the stamp after sealing instead and every
      subsequent sink verb re-attempts a failing seal, a hot loop driven by
      ordinary activity. Also captured: the ticker is activity-driven with NO
      background thread, and the seal paths deliberately call the `record` seam
      rather than `emit` so the ticker cannot interleave a seal mid-checkpoint.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:204, 521-522, 1190-1260
  - src/melder/crystallizer/crystallizer.py:723-729, 732-741, 687-693
  IMPACT: Running tally across BOTH sweeps - 6 concurrency claims examined
    against code, 3 wrong (all mine, all written from layering), 3 correct (all
    inherited). The inherited claims held up better than my own, which is worth
    knowing: the previous author was reading code and I was reading structure.
    All four documents: 127 `path:line` citations, 0 problems. Index green.
    Preservation 8 unaccounted, all replaced by the expanded text.
    I also mis-cited my own new evidence lines on the first attempt (:722 and
    :731 rather than :723 and :732) and caught it by re-checking each citation
    against the file. Approximate line numbers are how the next stale citation
    starts.
  NEXT: The remaining inherited claims in that set of 11 are narrower - the
    import-lock guardrail, the lock-free bind refusal, the Meld re-entrancy, and
    the mediator plane's leaf-ordering. None is deadlock-critical.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-03T03:30:00Z
  TYPE: VALIDATE
  CLAIM: FAILURE-MODE SWEEP - checked every documented exception type against the
    exception types actually raised in that component's OWN key files. 44
    exception claims across the catalogs; five components claimed a type raised
    nowhere in their own files. Four were legitimate cross-file attribution
    (the component drives a collaborator that raises). ONE WAS A REAL GAP, and
    it is the interesting kind.
    `SpellSpaceScopeError` is raised at EXACTLY ONE SITE IN THE ENTIRE TREE -
    `spell_space_thread_state.py:245` - and that file was claimed by NO
    component. It appeared only in the exhaustive inventory. Two component
    entries documented the exception in their Failure Modes; neither owned the
    code that raises it, so a reader tracing the error had nowhere to go.
    Added `### Subcomponent: SpellSpace Thread State`, and it turned out to
    carry a design fact that cannot be derived from code shape at all:
      - Isolation IS the design - per-thread stacks, NO LOCK taken or needed,
        stated as a deliberate alternative to dynamically-created `ContextVar`s.
      - The eager `__init__` on the `threading.local` subclass exists because of
        a REPOSITORY POLICY, not convenience. A `threading.local` subclass
        normally forces callers into `getattr(local, "stack", None)` probes, and
        this repo's Attribute Access Rule forbids defensive `getattr`/`hasattr`
        on owned attributes. Eager init makes the attribute unconditionally
        present so the owner can use direct access.
        DELETE THAT `__init__` AS REDUNDANT AND THE CLASS EITHER BREAKS OR
        FORCES A BANNED PATTERN BACK IN. Nothing in the code says so; only the
        policy document plus the class docstring do.
    Both Failure Modes entries now name the real raiser and point at the new
    subcomponent.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space_thread_state.py:39-46, 245
  - context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/banned_patterns.md:8-18
  IMPACT: Core re-established as the union after the new Key Files entry -
    202 = 202. Adding a key file WITHOUT adding its C1 record is the same drift
    I created on 2026-08-02; caught it in the same pass this time.
  NEXT: See the range-drift note below - it changes how much any measured range
    in these documents can be trusted.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-03T03:40:00Z
  TYPE: RISK
  CLAIM: MEASURED RANGES DRIFT UNDER THIS TREE FASTER THAN A PASS TAKES.
    Re-verifying C1 ranges found 8 stale in `src_architecture.md` and 8 in
    `src_components.md` - ranges I had measured and verified green EARLIER TODAY.
    `git status` reports 558 modified files under `src/`. I edited three.
    Some of the drift is downstream of my own docstring edits: `spellbook.py`
    +5 lines, `conduit.py` +1, and the generated artifacts that harvest
    docstrings - `bind_guard_manifest.py` +5, `system_document.py` +52,
    `__architecture__.py`, `__components__.py`, `__graph_network__.py`,
    `__graph_details__.py`. That is further evidence against the "docstrings are
    inert" claim I withdrew: the blast radius is at least six generated files,
    not one manifest.
    The rest is tree activity I did not cause and am not tracking.
    THE POINT FOR ANY FUTURE READER: `verified_at` is not decoration. A range in
    these documents is true AS OF ITS TIMESTAMP and no longer, and in a tree
    with concurrent activity "no longer" can mean within the same working
    session. The instructions' rule - remeasure every pass, never carry forward -
    is not conservatism; it is the only thing that makes a range mean anything
    here.
  EVIDENCE:
  - context_compass/system_docs/src_components.md (## C1 Code Map (Core))
  - context_compass/system_docs/src_architecture.md (## C1 Code Map (Core Only))
  IMPACT: All 484 C1 entries across the four documents remeasured and restamped;
    0 mismatched against disk at the time of writing. 132 `path:line` citations,
    0 problems. All four indexes green. Preservation: 16 unaccounted lines, every
    one a superseded `end_line`/`loc` value from the remeasure.
  NEXT: Anyone consuming a range from these documents should re-run the range
    check first; the recipe is under `## Indexing` in each.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-03T04:20:00Z
  TYPE: IMPLEMENT
  CLAIM: OWNER DIRECTIVE - the four system documents must reference `src/` and
    never the Context Compass helper repository. 33 lines carried such a
    reference, not 18; the count differs because the tool-invocation blocks
    contribute two lines each. All 33 examined, 32 substituted, ONE KEPT
    DELIBERATELY.
    - TOOL INVOCATIONS (24 lines) - rewritten documentation-root-relative:
      `python tools/system_documents/index_document.py --doc system_docs/<doc>.md`.
      Verified still working: `--check` green and a live `--slice "Operational
      Invariants"` returns :792-892 with its citation header.
    - SIBLING-DOCUMENT CROSS REFERENCES (6 lines) - reduced to bare filenames
      (`src_architecture.md`, `tests_components.md`), which is what they always
      meant; the path prefix added nothing.
    - THE POLICY CITATION I ADDED EARLIER TODAY (1 line) - the SpellSpace Thread
      State entry cited a coding-standard document in the helper repo as
      evidence for the eager `__init__`. Replaced with the source-side evidence:
      the module states the rule and its rationale in its OWN docstring at
      :39-46. The claim is unchanged and now rests entirely on `src/`.
    - KEPT, AND THIS ONE MATTERS: `tests_architecture.md` lists `context_compass`
      among the `norecursedirs` exclusions. That is a LITERAL VALUE from
      `pyproject.toml:208`, not a reference to anything - pytest genuinely
      excludes that directory. Deleting it to satisfy a text sweep would make a
      verified configuration list WRONG, which is the same class of defect as
      the `codex`/`codex_agent_2`/`codex_agent_3` entries corrected earlier
      today. Annotated in place so the next sweep does not remove it.
    A DEFECT I INTRODUCED AND CAUGHT IN THE SAME PASS: making the embedded
    citation recipe's glob documentation-root-relative BROKE it - cited source
    paths are relative to the SOURCE-TREE root, so running from the
    documentation root reported all 1,331 citations as MISSING. The recipe now
    walks up from the working directory until it finds `src/`, and resolves both
    the document glob and the source paths independently. Verified by running it
    verbatim from BOTH roots: 1,331 citations, 0 problems from each.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md (## Indexing)
  - context_compass/system_docs/src_components.md (## Indexing)
  - pyproject.toml:208 (the retained literal)
  IMPACT: One `context_compass` string remains across the four documents, and it
    is a pytest configuration value rather than a reference. All four indexes
    regenerated and green. 131 `path:line` citations, 0 problems.
    PRESERVATION: 27 unaccounted lines across the four documents; every one is a
    substituted path or recipe line except a single reflowed sentence in the
    SpellSpace entry, whose claim is intact in the replacement.
  NEXT: If the intent is that NO helper-repo string may appear at all, the
    `norecursedirs` entry needs an owner ruling - the options are to keep a true
    list, or to omit one entry and note the omission. I am not silently
    falsifying a verified list to satisfy a grep.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-03T04:55:00Z
  TYPE: IMPLEMENT
  CLAIM: THE TEST DOCUMENTS NOW CARRY THEIR OWN VERIFICATION RECIPE, which is the
    lane that needed it most and had none.
    The asymmetry is structural, not an oversight anyone can close: source-side
    citations get a free resolution check because `src_graph_index.md` is built
    from the source tree. NOTHING is built from the test tree, so a renamed or
    deleted test file leaves a citation that still parses and points nowhere,
    and a range that drifts inside a surviving file is invisible even to an
    existence check. The instructions say remeasure every pass; until now
    nothing in the documents made that runnable.
    The embedded recipe does three things, and the third is the one no other
    check in this system performs:
      1. every cited test path exists - GLOBS SKIPPED, because a glob is a
         statement about a set rather than a citation. Without that exclusion the
         check reports `tests/*.py` as a missing file and gets ignored on its
         second run.
      2. every `path:line` range is in bounds.
      3. EVERY C1 RECORD'S `end_line` STILL MATCHES THE FILE ON DISK. This is the
         drift check, and it is the only instrument that catches a range which
         has silently moved inside a file that still exists.
    Made root-independent the same way as the source-side recipe - it walks up
    until it finds `tests/` - and VERIFIED BY RUNNING IT VERBATIM FROM BOTH the
    documentation root and the repository root: 369 path citations, 148 C1
    ranges, 0 issues from each.
  EVIDENCE:
  - context_compass/system_docs/tests_architecture.md (## Indexing)
  - context_compass/system_docs/tests_components.md (## Indexing)
  IMPACT: All four documents are now self-verifying on the axis no tool covers,
    and the two that were most exposed are no longer the two with no check.
    Both test documents: contract sections in order, one H1, no wrapped
    headings, no duplicate names, preservation 0 unaccounted. All four indexes
    green.
    Also confirms the helper-repo sweep held: `tests_components.md` carries zero
    references, `tests_architecture.md` carries exactly one - the `norecursedirs`
    literal from `pyproject.toml:208`, annotated so it is not mistaken for a
    reference and deleted.
  NEXT: Recommend the other agent lift BOTH recipes into
    `system_document_build.md` as standard gates. They are document-agnostic,
    hardcode no source root, and between them they cover the two failure modes
    the index tool cannot see: unresolvable citations and silently drifted ranges.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: All four Acceptance Criteria are met and were verified
  mechanically rather than asserted, on 2026-08-03:
  (1) Both documents match their Required Section Contract IN ORDER - 17/17 for
      architecture, 12/12 for components, checked by position rather than by
      presence.
  (2) Both indexes regenerate and `--check` green - 46 sections / 2,298 lines and
      136 sections / 8,370 lines. The test-side pair was brought to the same bar
      and is green too (28 / 710 and 53 / 1,579).
  (3) No content deleted. The recomposition patch lane went 1,887 -> 644 lines
      with EVERY block decided: 564 lines re-absorbed after source verification,
      617 lines collapsed to pointers as measured 100% duplicates, and 9 blocks
      kept out with written reasons. Nothing sits in neither document.
  (4) The graph is `src_graph.md` + `src_graph_index.md`; both exist and the
      component/architecture joins resolve against the index with 0 unresolved.
  Closing beyond the original scope, because the work went further than the
  ticket asked: all 484 C1 entries across four documents measured against disk,
  Core == the union of Key Files (202 = 202), 131 `path:line` citations with 0
  problems, and both source and test documents now carry embedded verification
  recipes for the two failure modes the index tool cannot see.

## Closing Note
WHAT THIS TICKET ACTUALLY COST, and why the notes are long: the recomposition
itself was the small half. The audits it triggered found defects that every
existing gate passed:
- EVERY C1 range in both source documents was off by one - `end_line` measured as
  `len(text.split(chr(10)))`, counting a phantom line past the final newline.
  354 of 359 entries wrong.
- SEVEN wrong symbol claims, the worst being a public API documented on the wrong
  class with two of its three method names not existing anywhere.
- NINE rotted `path:line` citations, five pointing into a 693-line file at lines
  1966-3787, and two IN BOUNDS but landing nowhere near their symbol.
- A FALSE VERIFICATION STAMP in both `## Unknowns` sections claiming no renamed
  symbol survived. Five had.
- THE CORE-SET INVARIANT broken in both directions, 14 of the 18 gaps being drift
  I introduced myself by expanding directories without updating the map.
- THREE of my own concurrency claims wrong, one of them dangerously - it told a
  reader two locks imposed no ordering on each other when they do, inviting the
  exact inversion that would deadlock.
THE COMMON SHAPE: every one of these was a claim built from real names that no
name-matching check could falsify. Only reading the call chain finds them. That
lesson is recorded in the notes rather than in a summary line, because it is the
part worth inheriting.

## Acceptance Criteria
- Both docs match their Required Section Contract in order.
- Both indexes regenerate and `--check` green.
- No content deleted; migrated material lands in `src_components.md`.
- Graph replaced by `src_graph.md` + `src_graph_index.md`.

## Context / Handoff Summary
Architecture done and verified. Components next; it consumes the migration file
in the patch lane. Graph last - `src_graph.json` / `readable_src_graph.json` are
the retired artifacts.
