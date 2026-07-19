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
   Sections, in order: Purpose / Responsibilities / Contract / Owned State /
   Threading / Lifecycle & Cleanup / Subsystem Context / System Context.
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

## Context / Handoff Summary
Program epic for a correctness-plus-enrichment pass over all 542 classes in `src/melder`.
Carries THE OBJECT CONTRACT (five items per class) and THE CHUNKING LAW (task <=10 classes,
story <=40, agent reads only contract + subsystem brief + its files). Ten child epics sized
from a measured baseline; execution starts with oce-package-root as the exemplar. The
headline correctness fact: 246 internals are currently bindable as spells.
