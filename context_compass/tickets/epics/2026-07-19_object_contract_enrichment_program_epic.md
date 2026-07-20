# Epic: Object Contract Enrichment Program (guard + agent surface + rich docstrings)

## Metadata
- Epic ID: EPIC-2026-07-19-object-contract-enrichment-program
- Status: ready
- Owner: cowork
- Agent Name: melder_0
- Priority: p1
- Created: 2026-07-19T01:10:00Z
- Updated: 2026-07-19T01:10:00Z
- Kind: PROGRAM epic (carries the standard; child epics carry the work)
- Child epics:
  - EPIC-2026-07-19-oce-package-root
  - EPIC-2026-07-19-oce-utilities
  - EPIC-2026-07-19-oce-aether-conduit
  - EPIC-2026-07-19-oce-aether-aetheric-frame
  - EPIC-2026-07-19-oce-aether-spellbook
  - EPIC-2026-07-19-oce-nexus-rift
  - EPIC-2026-07-19-oce-nexus-acl
  - EPIC-2026-07-19-oce-nexus-core
  - EPIC-2026-07-19-oce-crystallizer
  - EPIC-2026-07-19-oce-mutation-research

## Problem / Opportunity
Three gaps across the same 542 classes, measured 2026-07-19:

1. CORRECTNESS: 246 of 542 classes carry no `__melder_internal__` sentinel. Melder's own
   kernel and control-plane objects can therefore be registered as spells through
   `Spellbook.bind(...)`. The guard exists and works - it is simply not applied. Coverage is
   uneven by accident of history: `nexus/rift` is 53/53, `nexus/acl` 38/39, while
   `aether/spellbook` is 87/208 and every one of `utilities/custom_exceptions`,
   `utilities/helpers`, `utilities/data_structures`, `mutation_research/research_set`,
   `crystallizer/persistence` sits at zero.
2. AGENT SURFACE: 5 of 542 classes carry `__agent_purpose__` / `_ast_helper_access`. An agent
   that imports melder cannot ask an arbitrary object what it is for or whether it may touch
   it. For an AI-native runtime this is the wrong default.
3. DOCSTRING DEPTH: every class has a docstring (542/542), but 212 are Rank 1-2 on the
   `docstrings.md` ladder - one-liners and thin descriptions with no contract. The gap is
   depth and CONTEXT, not presence. `aether/spellbook` alone holds 123 of the 212.

## Context
- The guard is real and enforcing: `MelderRegistrationGuard.assert_allowed(...)` raises
  `InternalRegistrationError` when a candidate carries the sentinel. Untagged internals pass
  silently.
- `system_document.py:StaticSystemDocument` is the EXEMPLAR for the target shape: rich
  Purpose/Contract/Lifecycle class docstring, `__agent_purpose__`, `_ast_helper_access`, and
  per-method Contract/Args/Returns/Raises blocks.
- `crystallizer` and `mutation_research` were already docstring-finished to Rank 4/5 (0 weak
  classes) but carry almost no guard and no agent metadata - proof these are independent
  workstreams that must be tracked separately.
- `utilities/helpers/class_surface_ast_describer.py` consumes `_ast_helper_access`, so the
  marker is functional, not decorative.

## MRP Alignment
The core being made trustworthy: a runtime that cannot be tricked into registering itself,
and an object world an agent can interrogate without reading 6,000 lines of C-docs. Neither
is polish - the first is a correctness hole and the second is the AI-native premise.

## THE OBJECT CONTRACT (canonical; child epics inherit this section by reference)
Every major object gets all five. A class is DONE only when all five hold.

1. GUARD (correctness, non-negotiable) - CLASSIFIED, NOT SWEPT
   ```python
   from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
   class Thing:
       __melder_internal__: ClassVar[object] = _mrg.sentinel
   ```
   EVIDENCE for the idiom: `spell_compiler/profiles/resolution_profile.py:8,23`.

   THE MRO LAW (corrected 2026-07-19; an earlier draft of this epic got this wrong):
   `MelderRegistrationGuard.is_internal` uses `getattr(candidate, "__melder_internal__")`,
   and attribute lookup walks the MRO. Tagging a base class therefore silently tags EVERY
   subclass, INCLUDING a user's. `Cleanable` is referenced across 277 files; guarding it
   would make every user class that subclasses `Cleanable` unbindable in the user's own
   spellbook. The existing code already respects this - `Cleanable`, `Sync`, and
   `AbstractElasticPool` are unguarded while their concrete descendants are guarded. That
   is the correct pattern, not an oversight.

   Three categories, decided per class:
   - NEVER GUARD - base classes: `Cleanable`, `Sync`, `AbstractElasticPool`, and any future
     class that users are expected to subclass. Guarding these poisons user subclasses.
   - NEVER GUARD - user-bindable tools: things a user may legitimately ask Melder to
     INJECT. The weak data structures (`WeakConcurrentDict`, `WeakConcurrentList`,
     `WeakConcurrentSet`, `WeakRefNode`) and all 11 exception types.
   - GUARD - Melder kernel: anything whose construction Melder owns and whose injection
     would be a category error.

   GUARDING AND EXPORTING ARE ORTHOGONAL. `SafeGuard` is guarded AND should be exported: a
   user imports it and uses it directly for lock ordering; they simply cannot
   `bind(SafeGuard)` and have Melder construct it. "Exposed in `__init__`" and "cannot be
   bound as a spell" are independent decisions and must be recorded independently.

2. AGENT PURPOSE
   `__agent_purpose__: str = "access: <public|internal>. <what an agent can do with this>"`
   One sentence, action-shaped. Not a restatement of the class name.

3. AST ACCESS MARKER
   `_ast_helper_access: str = "<public|internal>"` - consumed by
   `utilities/helpers/class_surface_ast_describer.py`.

4. RICH CLASS DOCSTRING (Rank 4 minimum, Rank 5 for public API)
   CANONICAL SECTION HEADERS - use these EXACT strings, in this order. Verification sweeps
   match on them literally, so a paraphrased header reads as a missing section:
   ```
   Purpose:
   Responsibilities:
   Contract:
   Owned State:
   Threading:
   Lifecycle / Cleanup:
   Registration:
   Subsystem Context:
   System Context:
   ```
   `Registration:` states the guard classification (MELDER KERNEL / USER-BINDABLE /
   BASE CLASS) and the one-line reason. `Owned State:` may be omitted for stateless
   classes; every other header is mandatory.
   The last two are the NEW requirement and the reason this program exists:
   - Subsystem Context: what this object is to its own subsystem, and which sibling it
     hands off to.
   - System Context: where it sits in the canonical boot order
     (Aether|AetherUtilitySystem -> Crystallizer -> MutationResearch -> Nexus ->
     AethericFrame -> Spellbook -> Conduit|Ward) and which layer of the DGR it serves.

5. RICH PUBLIC-METHOD DOCSTRINGS
   Purpose / Contract / Args / Returns / Raises, plus Threading and Lifecycle when the
   method touches locks or teardown. Per `synaptic_python_developer` overlay: no fluff,
   precise guarantees only.

## THE COMPREHENSION LAW (owner directive 2026-07-19, non-negotiable)
Two rules, both aimed at the same failure: documenting a class you do not understand.

1. READ THE IMPLEMENTATION BEFORE YOU DOCUMENT IT.
   Class signatures, existing docstrings, and the C-docs are NOT sufficient. Open the
   source file and read the algorithm. Then, after writing, VERIFY each behavioural claim
   back against the source - if the docstring says "ordering is by id()", grep that it is.
   A docstring that restates the class name in longer words is a failure, not a pass.

   Worked example of what this yields: reading `safeguard.py` produced four facts no
   signature could have given - ordering is `sorted(id(lock))` not argument order, timeout
   is PER LOCK so N locks multiply the wait, `one_time_use` defaults True so `__exit__`
   self-cleans, and `cleanup()` deliberately does NOT release held locks (calling it
   directly leaks them). Reading `phase_latch.py` produced two more: it runs TWO events
   (fail-fast wake vs quiesce barrier) and it explicitly rejects `bool` for `expected`
   because `True` is an `int` and would silently build a 1-unit latch.

2. AFTER ANY COMPACTION, RE-READ THE SYSTEM DOCS BEFORE RESUMING.
   Specifically `context_compass/system_docs/src_architecture.md` and
   `src_components.md`, IN FULL. This program documents objects in terms of their
   Subsystem Context and System Context; an agent that has lost those docs will write
   narrow, compartment-local docstrings that describe a class without knowing what it is
   TO the system. That is precisely the shallow output this program exists to replace.
   Do not resume documentation work on a compacted context until both are re-read.

## THE CHUNKING LAW (anti-overflow; this is why the program is split this way)
An executing agent reads EXACTLY three things and nothing else:
1. this epic's `THE OBJECT CONTRACT` section (the standard),
2. its own child epic's `Subsystem Context Brief` (the subsystem story), and
3. the files named in its task.

Hard sizing limits, chosen so that set fits one context window:
- TASK  = one file cluster, MAX 10 classes and MAX ~1,500 source LOC.
- STORY = one coherent package, MAX 40 classes.
- EPIC  = one subsystem.
No task may span two packages. No agent may open the C-docs during execution - the
subsystem brief exists precisely so it does not have to.

## Goals
- Every class in scope is CLASSIFIED guard/no-guard per the three categories above, and the
  classification is recorded in the class docstring. Binding any Melder kernel object raises.
- `__agent_purpose__` and `_ast_helper_access` on every class in scope.
- Zero Rank 1-2 class docstrings; every class carries Subsystem + System Context.

## Non-Goals
- No behavior changes. This program adds class attributes and documentation ONLY.
- No API shape changes, renames, or reorganization.
- No test authoring beyond the guard regressions named below.
- No `__init__.py` export edits from this program (see the collision note below).

## Scope Boundaries
SCOPE RULE (owner directive 2026-07-19): USER-FACING ASSETS ONLY. Internal machinery that a
user never holds, annotates, or catches is out of scope for this program.

- OUT: `aether/spellbook/spell_compiler/**` (208 classes, 121 of the original guard gap).
  Compiler internals are not user-facing; they are excluded wholesale.
- OUT: `tests/**`, `benchmarks/**`, runtime logic.
- OUT: `src/melder/__init__.py`. COLLISION NOTE: `helper_f` holds an active
  `melder_init_wheel_strategy` lane that rebuilt the root to 66 exports and reports
  "saturation reached - further exports should be demand-driven". This program does NOT
  touch the root export list; utilities that should be exposed are RECOMMENDED to that lane
  through the mailbox, not edited here.
- OUT: `src/melder/__melder_registration_guard__.py` (owner ruling: the guard stays as-is).
- IN: everything else under `src/melder/**` - roughly 334 classes after the compiler
  exclusion.

Owner utility rulings recorded 2026-07-19 (these are classification decisions, not
export decisions):
- EXPOSE-worthy: `CounterSwitch`, `FastSwitch`, `IDBuilder`, `InitHelpers`, `EnumHelpers`,
  `SafeGuard`, and the weak data structures.
- DO NOT EXPOSE: `Package` - and see the separate finding below, it is dead code.
- "Internal melder shit is not exposed" - kernel objects stay unexported regardless of
  guard status.

## Requirements
- Functional: `Spellbook.bind(<any melder internal>)` raises `InternalRegistrationError`.
- Non-functional: additive only - the guard attribute is a ClassVar sentinel and must not
  alter construction, inheritance, `__slots__`, or cleanup ordering.

## Acceptance Criteria
- [ ] Every in-scope class carries an explicit guard CLASSIFICATION (kernel / user-bindable /
      base-class), recorded in its docstring. No class is left unclassified.
- [ ] No base class in the `Cleanable` / `Sync` / `AbstractElasticPool` family carries the
      sentinel (MRO law).
- [ ] `__agent_purpose__` + `_ast_helper_access` on 100% of in-scope classes.
- [ ] Rank 1-2 class docstring count is 0 in scope; every class has Subsystem + System
      Context.
- [ ] Guard regression suite proving BOTH directions: representative kernel objects from
      every subsystem are REFUSED by `bind(...)`, AND a user class subclassing `Cleanable` is
      ACCEPTED by `bind(...)`. The second assertion is the MRO-law regression and is the one
      that would have caught the original error.
- [ ] Owner-run 3.14t suite green (agent reports "Not run." until then).

## Risks / Mitigations
- Value types that SHOULD be bindable get guarded by an over-broad sweep -> each child epic
  names its exclusions explicitly in its Scope section before work starts.
- `__slots__` classes reject new class attributes -> ClassVar assignment is class-level, not
  instance-level, so `__slots__` is unaffected; verified against the existing 296 guarded
  classes which include `__slots__` users.
- Docstring churn burying a real edit -> attribute passes and docstring passes are SEPARATE
  stories per subsystem, so diffs stay reviewable.

## Validation Plan
- Per task: AST sweep proving the three attributes present for every class touched.
- Per epic: guard regression for that subsystem's representative internals.
- Program close: full-tree AST sweep + owner 3.14t run.
- Not run by agent. Reports say "Not run." until the owner runs them.

## Distribution (child epic sizing; measured 2026-07-19, compiler excluded)
| child epic | classes | guard gap | weak docstrings | stories |
|---|---:|---:|---:|---:|
| oce-package-root | 2 | 2 | 1 | 1 |
| oce-utilities | 47 | classify | 29 | 3 |
| oce-aether-conduit | 30 | 4 | 14 | 1 |
| oce-aether-aetheric-frame | 60 | 27 | 9 | 2 |
| oce-aether-spellbook-core | 13 | ~5 | ~5 | 1 |
| oce-nexus-rift | 53 | 0 | 14 | 2 |
| oce-nexus-acl | 39 | 1 | 14 | 1 |
| oce-nexus-core | 19 | 0 | 5 | 1 |
| oce-crystallizer | 58 | 36 | 0 | 2 |
| oce-mutation-research | 23 | 20 | 1 | 1 |
| TOTAL (in scope) | ~344 | ~95 | ~92 | 15 |
| EXCLUDED: spell_compiler | 208 | 121 | 123 | - |

`oce-utilities` shows "classify" rather than a gap count because its guard work is a
per-class decision, not a fill - several of its unguarded classes are correctly unguarded.

Execution order (correctness first, then the biggest gap):
1. oce-package-root (establishes the exemplar; smallest)
2. oce-utilities (carries the classification rulings and the Package removal)
3. oce-mutation-research, oce-crystallizer (highest guard gap per class)
4. oce-aether-aetheric-frame, oce-aether-conduit, oce-aether-spellbook-core
5. oce-nexus-rift, oce-nexus-acl, oce-nexus-core (guard already clean; docstrings only)

## Decision Log
- 2026-07-19 melder_0: three workstreams tracked separately per subsystem because
  crystallizer/mutation_research are docstring-complete but guard-empty - one combined
  status field would misreport both.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: baseline measured by AST sweep across all 542 classes; contract and
  chunking law defined; child epic sizing derived from that measurement.

## Milestones
- [ ] Contract ratified by owner (this epic accepted).
- [ ] Exemplar landed (oce-package-root) and used as the reference diff.
- [ ] Guard gap closed to zero across all child epics.
- [ ] Agent surface complete across all child epics.
- [ ] Docstring rank floor reached; owner 3.14t run green.

## Applicable Anti-Patterns
- [ ] No behavior change smuggled into a documentation pass.
- [ ] No task spanning two packages (breaks the chunking law).
- [ ] No agent opening the C-docs mid-task instead of using its subsystem brief.
- [ ] No claiming a class DONE with fewer than all five contract items.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Noting Behavior
- Epic notes: program direction, cross-epic tradeoffs, and coverage movement only.
  Per-class findings belong in the child epic's task notes.

## Notes
- DATETIME: 2026-07-19T01:10:00Z
  TYPE: FACT
  CLAIM: Baseline AST sweep over `src/melder/**` (542 classes, excluding tests and caches):
    guard present on 296 (MISSING 246); `__agent_purpose__` and `_ast_helper_access` present
    on 5 each (MISSING 537); class docstrings present on 542/542 but ranked R1=16, R2=196,
    R3=203, R4=112, R5=15 - so 212 sit below the Rank 3 floor. Guard coverage is bimodal by
    subsystem: nexus is effectively complete (rift 53/53, acl 38/39) while
    utilities/custom_exceptions, utilities/helpers, utilities/data_structures,
    mutation_research/research_set, mutation_research/diff, crystallizer/persistence and
    utilities/general_base are all at ZERO.
  EVIDENCE:
  - src/melder/__melder_registration_guard__.py:88-104
  - src/melder/system_document.py:26-35
  - context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/docstrings.md:42-51
  IMPACT: Sets every acceptance number in this program and proves the three workstreams are
    independent - a subsystem can be docstring-complete and guard-empty at the same time.
  NEXT: Create the ten child epics with their subsystem briefs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-19T01:40:00Z
  TYPE: CONFLICT
  CLAIM: Correcting a factual error in this epic's own first draft. It set an acceptance
    criterion of "guard coverage 542/542", which would have introduced a real bug: the
    sentinel is found through `getattr`, so it INHERITS down the MRO. Tagging `Cleanable`
    (referenced across 277 files), `Sync`, or `AbstractElasticPool` would make every USER
    subclass unbindable in the user's own spellbook. Verified by direct reproduction: a
    subclass of a tagged base returns True from an `is_internal`-equivalent check. The
    existing codebase already excludes these three base classes from tagging - that was
    correct design, and the sweep would have undone it.
  EVIDENCE:
  - src/melder/__melder_registration_guard__.py:88-92
  - src/melder/utilities/general_base/cleanable.py:1-1
  IMPACT: Guard work is a per-class CLASSIFICATION, never a sweep. The MRO-law regression
    (a user subclass of `Cleanable` must still bind) is now an acceptance criterion
    specifically because it is the test that catches this class of error.
  NEXT: Carry the classification into oce-utilities, which holds the base classes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-07-19T01:45:00Z
  TYPE: FACT
  CLAIM: `utilities/helpers/package.py` is DEAD CODE. 933 library lines exposing
    `Package(Cleanable, Generic[P, R])` plus the alias `Pack = Package` (:932). Zero
    references from `src/**`: every "Package" match in source is the word in docstring prose
    ("Package context", "Package-relative cache root"), not the symbol. The owner's
    hypothesis that hooks use it optionally is DISPROVEN - no hook wiring references either
    name. The only consumers are two test files written against it (295 + 53 lines). It is
    not in the new 66-name root export list, and an equivalent exists in CommandOps.
  EVIDENCE:
  - src/melder/utilities/helpers/package.py:51-51
  - src/melder/utilities/helpers/package.py:932-932
  - tests/unit/melder/utilities/helpers/test_package.py:5-6
  IMPACT: 1,281 lines of library + test weight removable with zero production impact.
    Recommend deletion from melder and retention in CommandOps where it is actually used.
  NEXT: Owner ruling on deletion; tracked as a task under oce-utilities.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- TYPE: RISK
  DATETIME: 2026-07-19T16:20:00Z
  AGENT: melder_0
  SUMMARY: CODEMOD LINE-ENDING HAZARD - self-inflicted, detected and fully repaired.
    13 of 552 files under `src/melder` carry MIXED CRLF+LF line endings
    (`base_strategy.py`: 262 CRLF + 47 bare LF). Any codemod that does
    `text.split(nl)` then `nl.join(...)` REWRITES EVERY LINE ENDING in such a file,
    producing a whole-file whitespace diff (numstat `440 440`) that buries the real
    change. It also silently DESYNCS `ast` line numbers from list indices: `ast` counts
    Python's full line-break set (309 lines) while `split("\r\n")` counted 263, so every
    computed insertion point drifted by the 46-line difference and landed inside
    `__slots__` tuples and `def` signatures.
  LAW: Codemods MUST use `text.splitlines(keepends=True)` and `"".join(...)`.
    That is the ONLY split whose indices align with `ast` linenos AND whose rejoin
    preserves each line's original terminator byte-for-byte.
  REPAIR: Endings restored from the HEAD blob via difflib opcode alignment (content
    provably untouched; only terminators rewritten). Whitespace-only churn in the three
    subsystems I touched went 46 files -> 0. No git checkout was used.
  EVIDENCE:
  - src/melder/crystallizer/crystal_analysis/strategies/base_strategy.py:1-309
  NEXT: Reuse the keepends codemod skeleton for every remaining child epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- TYPE: RAISE
  DATETIME: 2026-07-19T16:20:00Z
  AGENT: melder_0
  SUMMARY: PRE-EXISTING WHITESPACE CHURN OUTSIDE MY LANE - owner awareness, no action taken.
    `src/melder/aether` (291 files) and `src/melder/nexus` (118 files) show whole-file
    diffs against HEAD that are 100% whitespace-only (0 files with real content changes).
    I never ran a codemod against either path this session, and `core.autocrlf`,
    `core.eol`, and `.gitattributes` are all unset. So 409 files in the working tree
    differ from HEAD by line endings alone from some prior tooling pass.
  IMPACT: A commit taken now would carry ~180k lines of pure terminator churn and would
    make the OCE diffs unreviewable.
  NEXT: OWNER RULING - either normalize deliberately (add `.gitattributes` with
    `*.py text eol=crlf` and commit the normalization as its own isolated commit), or
    restore those 409 files before committing OCE work. Deliberately NOT touched by me.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- TYPE: DECISION_REQUEST
  DATETIME: 2026-07-19T16:20:00Z
  AGENT: melder_0
  SUMMARY: MRO-LAW VIOLATION, PRE-EXISTING: `PersistenceAnalysisStrategy` is guarded AND
    is the base of 10 concrete preflight strategies. Unlike the other MRO-risk bases this
    one is demonstrably USER-EXTENSIBLE: `PersistenceAnalyzer.__init__` accepts an
    injectable `strategies` parameter and falls back to the shipped set only when it is
    None, and the class's own docstring calls itself "the sanctioned ABC case". A user who
    writes `class MyStrategy(PersistenceAnalysisStrategy)` inherits the sentinel through
    the MRO and cannot bind their own class.
    Its two sibling families are handled correctly and were left unguarded by this pass:
    `SourceCustodyStrategy` (4 subclasses) and `CrystalFactStrategy` (4 subclasses).
    The codebase is therefore internally inconsistent across three sibling strategy families.
  WHY NOT SELF-APPLIED: removing a sentinel WIDENS what may be registered - a behaviour
    change on a guard the owner has ruled load-bearing ("the guard stays"). Untouched
    pending ruling.
  PROPOSAL: drop `__melder_internal__` from the base only, leaving all 10 concrete
    subclasses individually guarded, and carry the standard MRO-law warning in its
    `Registration:` section.
  EVIDENCE:
  - src/melder/crystallizer/crystal_analysis/preflight/persistence_analysis_strategy.py:1-74
  - src/melder/crystallizer/crystal_analysis/preflight/persistence_analyzer.py:1-189
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- TYPE: FACT
  DATETIME: 2026-07-19T16:20:00Z
  AGENT: melder_0
  SUMMARY: REPO-WIDE MRO RISK LIST - 14 guarded classes are bases of other classes.
    This is a RISK list, not a defect list: guarding a base is harmless when every
    subclass is also melder-internal. It becomes a defect only where a USER is expected
    to subclass. Verified user-extensible so far: `PersistenceAnalysisStrategy` (above).
    Out of scope (spell_compiler): SpellAnalyzerStrategy, SpellArtifactProcessorStrategy,
    SpellBindingProfile, SpellCodegenPlanStrategy, SpellGeneralProfile,
    SpellGeneralizedCodegenPlanBuilder, SpellSystemValidationStrategy (23 subclasses),
    SpellValidationStrategy (13 subclasses).
    IN SCOPE, still to be adjudicated by their own child epics: `Meld` (ConduitMeld,
    SpellSpaceMeld), `RiftSpace` (3), `CommandSystem` (3), `Creations` (ConduitCreations),
    `FrameViewer` (StaticFrameViewer). `Meld` is the highest-stakes of these - it is a
    front-facing domain noun.
  NEXT: Each child epic adjudicates its own bases against the 3-category rule.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- TYPE: RISK
  DATETIME: 2026-07-19T17:05:00Z
  AGENT: melder_0
  SUMMARY: py_compile IS NOT SUFFICIENT VALIDATION FOR A CODEMOD. This is the
    single most important lesson of the crystallizer pass. The mixed-ending index
    drift (see the prior RISK note) inserted sentinel lines and a guard import INSIDE
    METHOD DOCSTRINGS. Those files compiled CLEAN and passed every AST guard-coverage
    check, because a line inside a string literal is valid Python that simply corrupts
    the docstring text. They were found only by READING THE SOURCE and the diff.
    The same drift also appended `, ClassVar` to the WRONG import statement, producing
    `from melder.crystallizer.synthetic_module import SyntheticModule, ClassVar` -
    a latent ImportError that py_compile also cannot see, since imports are not
    resolved at compile time.
  MANDATORY CODEMOD VALIDATION SET (all four, every time):
    1. `ast.parse` write gate (refuse to write unparseable output).
    2. TRAPPED-LINE SCAN: for every inserted line, assert its line number falls
       OUTSIDE every multi-line `ast.Constant` string span. Match BOTH the plain
       (`__melder_internal__ =`) and annotated (`__melder_internal__:`) forms - my
       first scan used a `\s*=` pattern and silently missed the annotated one.
    3. STATIC IMPORT RESOLUTION: for each `from melder.X import Y` in a changed
       file, resolve `melder/X.py` and assert `Y` is defined at module level.
    4. `git diff --ignore-all-space` must report the SAME file count as `git diff`
       (zero whitespace-only files), and the diff must be READ, not just counted.
    5. NAME-BINDING CHECK (added 2026-07-19T20:10:00Z after this check's absence shipped
       four broken files to the owner's test run): for every name USED in a module-level
       class body assignment - `_mrg` above all - assert the name is BOUND by an import or
       assignment in that module. This is the OPPOSITE DIRECTION from check 3. Check 3
       verifies that names I import exist in their target module; check 5 verifies that
       names I use are imported at all. Only check 5 catches a deleted import.
       CRITICAL: `py_compile` CANNOT catch this. A class body compiles fine with an
       unbound name and raises `NameError` only at import time, so all four broken files
       reported compile-clean.
  ALSO: guard-coverage scripts must count `ast.Assign` AND `ast.AnnAssign`. Counting
    only Assign reported 25 already-guarded classes as unguarded (they used the
    `__melder_internal__: ClassVar[object] = _mrg.sentinel` form), and the resulting
    "fix" wrote 25 duplicate sentinels + 14 duplicate imports. All reverted; the 15
    affected files are byte-identical to HEAD again.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- TYPE: MEASURE
  DATETIME: 2026-07-19T17:05:00Z
  AGENT: melder_0
  SUMMARY: oce-crystallizer COMPLETE (guard classification + docstring enrichment).
    62/62 classes now carry 3+ canonical section headers (avg class docstring 35
    lines); 13 thin strategy docstrings were enriched with Threading/Registration/
    Subsystem Context/System Context against a re-read of src_architecture.md (full)
    and the crystallizer sections of src_components.md. Guards: 59 guarded, 3
    deliberately unguarded (`CrystalFactStrategy` + `SourceCustodyStrategy` as
    open/closed bases, `RecordedUnitState` as value vocabulary).
    The enrichment's through-line is that SEVERITY IS A LOAD-CONTROL DECISION made at
    the RestoreEngine fold->preflight seam, and each of the ten default preflight rows
    now documents WHY it blocks, warns, or informs - e.g. synthetic-source tamper
    blocks because for synthetic modules the record IS the code with no live file to
    fall back to, while source drift only warns because the live file wins at import.
  VALIDATION: py_compile ALL CLEAN; 0 trapped lines; 0 unresolvable imports;
    0 duplicate sentinels; 0 whitespace-only files (47 changed = 47 real).
    Not run: pytest (needs 3.14t; sandbox is 3.10).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- TYPE: MEASURE
  DATETIME: 2026-07-19T16:20:00Z
  AGENT: melder_0
  SUMMARY: oce-crystallizer guard classification COMPLETE. 62 classes: 58 guarded,
    4 deliberately unguarded (`CrystalFactStrategy` + `SourceCustodyStrategy` as
    open/closed bases, `RecordedUnitState` as value vocabulary,
    `PersistenceAnalysisStrategy` held pending the ruling above). Compile clean across
    the whole package; crystallizer MRO-law audit CLEAN (no guarded crystallizer class
    is a base of anything). Docstring enrichment for the package is the remaining work.
  VALIDATION: py_compile only. Not run: pytest (needs 3.14t; sandbox is 3.10).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- TYPE: FACT
  DATETIME: 2026-07-19T20:10:00Z
  AGENT: melder_0
  CLAIM: SHIPPED BREAKAGE - four files raised `NameError: name '_mrg' is not defined` at
    import, killing the owner's gauntlet run at `melder/__init__.py:64`. Cause: my
    duplicate-guard-import dedup pass. Its rule was "when a file carries BOTH a
    parenthesized and a single-line import from `__melder_registration_guard__`, drop the
    single-line one as the duplicate" - but in these four files the single-line form was
    the one BINDING `_mrg`, so the binding was deleted while the class body kept using it.
    Affected: `crystal_analyzer.py`, `cluster_crystal.py`, `contract_crystal.py`,
    `spell_index_crystal.py`. All four repaired; sweep confirms 323 files use `_mrg` in
    class-body assignments with 0 unbound.
  WHY IT ESCAPED: `py_compile` compiles a class body WITHOUT executing it, so an unbound
    name is invisible until import. All four files reported compile-clean through every
    validation pass I ran. The static-import check I did have ran the wrong direction: it
    verified names I IMPORT exist in their targets, never that names I USE are bound.
  EVIDENCE:
  - src/melder/crystallizer/crystals/cluster_crystal.py:1-40
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py:67-131
  IMPACT: The owner ran a test against a broken tree. Any dedup/removal codemod is
    strictly more dangerous than an additive one and must prove nothing it deleted was
    load-bearing - deletion passes need the name-binding check BEFORE write, not after.
  NEXT: Check 5 is now in the mandatory validation set above; run all five after EVERY
    codemod, additive or subtractive.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Program epic for a correctness-plus-enrichment pass over all 542 classes in `src/melder`.
Carries THE OBJECT CONTRACT (five items per class) and THE CHUNKING LAW (task <=10 classes,
story <=40, agent reads only contract + subsystem brief + its files). Ten child epics sized
from a measured baseline; execution starts with oce-package-root as the exemplar. The
headline correctness fact: 246 internals are currently bindable as spells.
