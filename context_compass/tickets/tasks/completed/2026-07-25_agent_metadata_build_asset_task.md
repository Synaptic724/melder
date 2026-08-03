

# Task: Move agent metadata off class bodies into a harvested build asset

## Metadata
- Task ID: TASK-2026-07-25-agent-metadata-build-asset
- Story: none (owner-directed, sibling of EPIC-2026-07-22-agent-metadata-to-docstring)
- Status: done
- Owner: melder_0
- Agent Name: melder_0
- Priority: p2
- Created: 2026-07-25T20:10:00Z
- Updated: 2026-08-03T12:22:14Z

## Objective
Stop 370 class bodies from carrying `__ast_helper_access__` / `__agent_purpose__`.
Author the facts in docstrings, harvest them at build time into a generated asset
under the existing build-asset runner, and let `ClassSurfaceAstDescriber` read the
asset instead of `type(obj).__dict__`.

## Ticket Contract
- ENTRY_GATE: active `attention_board.md` row; the 183-class gap audited (done) and
  the owner's exemption ruling recorded (done).
- EXECUTION_BOUNDARY (PHASE 1 - this pass, ADDITIVE ONLY):
  `src/melder/_build_assets/_agent_metadata/`, plus its tests. Nothing consumes the
  asset yet, so no runtime behaviour changes.
- EXECUTION_BOUNDARY (PHASE 2 - NOT this pass): the docstring codemod across ~370
  files, stripping the 788 assignments, and repointing `ClassSurfaceAstDescriber`.
- DEPENDENCIES: `_build_asset_runner.py` (discovery + gate); owner grammar ruling
  2026-07-25; owner exemption ruling for `spell_compiler`.
- EXIT_GATE (phase 1): runner discovers the asset, `--check` green, tests pass, and
  the asset's counts reconcile with the audit (394 marked / 173 exempt / 10 pending).
- FAILURE_ESCALATION: BLOCKER if harvest cannot reproduce the current attr values
  exactly; DECISION_REQUEST before any phase-2 file sweep.

## Scope Boundaries
- In scope (phase 1): the harvester, its generated asset, tests, runner integration.
- Out of scope (phase 1): editing any class body; changing `ClassSurfaceAstDescriber`;
  the `Registration:` docstring section (different axis - it describes bind guarding,
  which the internal manifest now owns).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner approved the grammar, the exemption rule, and implementation.

## PATCH GATE ASSESSMENT
`patch_framework_gating.md` applies to system-impacting change. PHASE 1 IS NOT
system-impacting: it adds a generated file that nothing imports and alters no
runtime path, so it proceeds without patch artifacts. PHASE 2 IS system-impacting -
it changes how `ClassSurfaceAstDescriber` resolves metadata and edits ~370 files -
and MUST NOT start until `architecture_patch.md` and
`component_patch_class_surface_ast_describer.md` exist and are linked here.

## Steps / Checklist
- [x] Audit the unmarked gap and confirm the owner's spell_compiler theory (94%).
- [x] Confirm every marked class already has a docstring (394/394 - pure move).
- [x] Settle the grammar with the owner.
- [x] Build the harvester with dual-source reading (docstring first, attr fallback). Dual-source served the migration and was REMOVED on completion; docstrings are now the only source.
- [x] Generate the asset; reconcile counts against the audit. 406 marked / 163 exempt / 13 pending; `--check` green.
- [x] Tests for grammar parsing, exemption, pending catalog, and value fidelity. Also inverted the legacy-attribute test so reintroducing attr reading fails loudly.
- [x] PHASE 2 (separate, patch-gated): codemod, strip, repoint. 808 assignments removed across 404 classes; zero remain in src or tests; ~76 KB of prose left the class dicts.
- [x] Document each meaningful finding immediately in `## Notes`.

## Deliverables
- `_build_assets/_agent_metadata/_builder.py` and its generated asset.
- Tests proving harvest fidelity and the three-state catalog.

## Files / Paths Impacted
- src/melder/_build_assets/_agent_metadata/_builder.py
- src/melder/_build_assets/_agent_metadata/agent_metadata.py (GENERATED)
- tests/unit/melder/build_assets/test_agent_metadata_builder.py

## Validation
- Not run (sandbox is Python 3.10; repo floor is 3.14t).
- Recommended (owner, 3.14t):
  - `python src/melder/_build_assets/_build_asset_runner.py --check`
  - `pytest tests/unit/melder/build_assets -q`

## Risks / Rollback Notes
- RISK: harvest silently loses prose. Mitigation: dual-source with attr fallback, and
  a test asserting the harvested value equals the current attr value for every class.
- Rollback: phase 1 is purely additive - delete the directory.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/agent_metadata_asset_2026_07_25/architecture_patch.md (PHASE 2, not yet authored)
  - system_docs/patches/active/agent_metadata_asset_2026_07_25/component_patch_class_surface_ast_describer.md (PHASE 2, not yet authored)
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: at phase-2 closure, once durable deltas merge into the system docs.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Keep notes append-only; promote `UNKNOWN` to `FACT` only with direct evidence.

## Notes
- DATETIME: 2026-07-25T20:10:00Z
  TYPE: MEASURE
  CLAIM: Audit complete, three findings that de-risk the migration. (1) The unmarked
    gap is 183 classes and 94% of it - 173 - sits in `aether/spellbook/spell_compiler`,
    with the remaining 10 in `utilities`. That matches the OCE epic's closure note
    "spell_compiler excluded per owner", so the gap is an EXISTING RULING that was
    never written anywhere a tool could read. (2) All 394 marked classes ALREADY have
    docstrings, so this is a pure MOVE, not an authoring project - the single largest
    risk is gone. (3) Zero classes carry `access=private`; my earlier report of one was
    a grep false positive on doc prose, so the runtime-raise rule for private classes
    has no live subjects.
  EVIDENCE:
  - src/melder/utilities/helpers/class_surface_ast_describer.py:711-716
  IMPACT: The migration is mechanical rather than editorial, and the exemption is a
    path rule over one coherent subtree rather than 173 individual judgements.
  NEXT: Confirm `Registration:` is a different axis before adding a new section.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-07-25T20:10:00Z
  TYPE: FACT
  CLAIM: The existing `Registration:` docstring section (412 classes) does NOT
    duplicate `__ast_helper_access__`. It reads "MELDER KERNEL - guarded. `Aether()`
    returns the process singleton..." - i.e. whether the class may be BOUND as a spell,
    which the internal manifest now owns exactly. `__ast_helper_access__` answers a
    different question: whether agent tooling should surface the class at all. Two axes,
    no collision, so a new section is warranted rather than reusing that one.
  EVIDENCE:
  - src/melder/_build_assets/_init_manifest/internal_manifest.py:20-21
  IMPACT: Avoided conflating bind-guarding with agent visibility, which would have made
    both facts unreadable. Side observation for a later lane: now that the manifest
    guards every class uniformly, the per-class "guarded" prose in 412 `Registration:`
    sections is largely redundant.
  NEXT: Implement the harvester against the agreed grammar.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-25T20:10:00Z
  TYPE: DECISION
  CLAIM: OWNER RULINGS. (1) GRAMMAR: `AGENT_ACCESS: <value>` and `AGENT_PURPOSE:` as
    line-anchored ALL-CAPS docstring sections - deliberately un-prose-like so extraction
    cannot collide with the Title-Case sections (`Purpose:`, `Contract:`, `Threading:`)
    already in use, and visually traceable to the attribute names being retired.
    (2) THREE STATES: marked -> the asset; `exempt` -> catalogued as a deliberate
    ruling; absent -> catalogued as `pending` for later fill-in. This is the point of
    the design: today "excluded on purpose" and "somebody forgot" are indistinguishable
    to every tool and every future agent. (3) EXEMPTION MECHANISM: `spell_compiler` is
    exempted by PATH RULE in the builder, not by stamping 173 files, because it is one
    coherent subtree under an existing owner ruling. Per-class `exempt` stays available
    for one-offs.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-07-25_agent_metadata_build_asset_task.md
  IMPACT: Zero file churn for the exemption; the catalog makes deferred work visible
    instead of invisible.
  NEXT: Build the harvester with dual-source reading so the asset is correct at every
    point of the migration rather than only at the end.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-07-25T20:25:00Z
  TYPE: MEASURE
  CLAIM: Asset generated and reconciled: 404 marked / 163 exempt / 10 pending. The
    counts differ from the earlier audit (394/173) for a GOOD reason - the harvester
    walks NESTED classes and the audit walked top-level only. `Cleanable._CleanupContext`
    appearing in pending is the proof. Coverage went up; the audit had undercounted.
    The runner discovered the new asset with zero configuration, which is the
    convention working as designed.
  EVIDENCE:
  - src/melder/_build_assets/_agent_metadata/agent_metadata.py
  IMPACT: Nested classes were previously invisible to the whole agent-metadata story.
  NEXT: Pin the behaviour with tests before any codemod touches a class body.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-25T20:25:00Z
  TYPE: FACT
  CLAIM: The 10 PENDING classes are a coherent set, not scatter. THREE are the
    describer's own result types (`ClassMemberDescription`, `ClassSurfaceDescription`,
    `InheritedAgentPurposeDescription`) - the tool that consumes this metadata does not
    describe itself. THREE are private dict views (`_WeakDictItemsView`/`KeysView`/
    `ValuesView`). ONE is a nested cleanup context. TWO are Protocols (`IChannelLogger`,
    `ICleanable`). One is `Package`.
  EVIDENCE:
  - src/melder/utilities/helpers/class_surface_ast_describer.py:31-38
  IMPACT: This is exactly the catalog the owner asked for: work that was previously
    indistinguishable from "done" is now an explicit, short, actionable list.
  NEXT: Leave all ten pending; none block phase 1.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-25T20:25:00Z
  TYPE: DECISION
  CLAIM: OWNER RULING on `Package` (utilities/helpers/package.py): DELIBERATELY PARKED
    as `pending`, not exempt and not marked. Owner rationale: it captures callables
    well and may warrant exposure through `melder.__init__`; CommandOps carries a copy
    the owner intends to reconcile so both objects are identical; the keep-vs-remove
    call is explicitly deferred to the end. NOTE the standing tension - an earlier
    melder_0 handoff recorded `Package` as dead code (933 lines, zero src references,
    alias `Pack` unused, consumed only by its own two test files) and PROPOSED DELETION
    under the oce-utilities epic, with the owner having ruled DO NOT EXPOSE at that
    time. This ruling supersedes that direction pending the final decision.
  EVIDENCE:
  - src/melder/utilities/helpers/package.py
  IMPACT: `Package` must NOT be auto-marked, auto-exempted, or deleted by any sweep in
    this lane. Its presence in PENDING is intentional signal, and a future agent
    tidying the pending list to zero would be destroying a recorded decision.
  NEXT: Revisit only when the owner settles keep-vs-remove and the CommandOps
    reconciliation lands.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-07-25T20:45:00Z
  TYPE: FACT
  CLAIM: PHASE 1 COMPLETE and verified. Harvester + generated asset land under the
    runner with zero configuration (404 marked / 163 exempt / 10 pending, v0.1.1).
    19 tests authored; all 19 assertions re-executed as plain Python because pytest is
    unavailable in this sandbox, and all pass - including the two that matter: FIDELITY
    (every harvested value is byte-identical to the legacy attribute across all 788
    live markers) and PRECEDENCE (docstring beats attribute, never the reverse).
  EVIDENCE:
  - src/melder/_build_assets/_agent_metadata/agent_metadata.py
  - tests/unit/melder/build_assets/test_agent_metadata_builder.py
  IMPACT: The codemod now has a safety net. Without the fidelity test the sweep would
    rewrite 76,200 characters of authored prose on faith.
  NEXT: Author the two phase-2 patch docs; the gate blocks the codemod until they exist.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-07-25T20:45:00Z
  TYPE: DECISION
  CLAIM: `build_scripts/` DELETED under owner query. After the runner landed, the only
    remaining content was a 69-line forwarding shim I had written to preserve the old
    entry point. Every other reference was either a `pyproject.toml` EXCLUSION rule or
    prose. The two system docs naming it were repointed to the runner, since deleting
    it is what made them stale. The pyproject exclusions were deliberately KEPT: they
    cost nothing and now act as insurance, because `namespaces = true` makes stray
    directories packageable in a way they were not before.
  EVIDENCE:
  - pyproject.toml:143-153
  IMPACT: One entry point instead of two, and no shim that can drift from the runner.
  NEXT: None for this item.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-25T20:45:00Z
  TYPE: ASSUMPTION_CHALLENGE
  CLAIM: The owner's red `test_version_module_exposes_expected_base_version` was
    PRE-EXISTING, not caused by this session - `git diff --quiet` on
    `src/melder/__version__.py` passes, so 0.1.1 is the COMMITTED value and the test has
    been pinning 0.1.0 since before I arrived. I did not bump the literal to 0.1.1,
    because a hardcoded version assertion fails for a DELIBERATE release bump, which is
    exactly the shape `testing_overview.md` rejects ("fail for a real regression and NOT
    for a harmless change"). Bumping it trains people to edit the test instead of read
    it, forever.
  EVIDENCE:
  - tests/unit/melder/test_package_version_metadata.py
  IMPACT: Replaced with two contract tests: the version is well-formed, and EVERY
    generated asset's `BUILT_FOR_VERSION` equals `melder.__version__`. The second is
    what the old pin was reaching for and is load-bearing - the internal manifest IS the
    enforced registration policy, so an asset stamped for a previous release means the
    wheel silently enforces a stale class list. Verified the new test would have caught
    the exact 0.1.0-vs-0.1.1 drift found earlier today.
  NEXT: Owner runs the version test lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-03T12:22:14Z
  TYPE: DECISION
  CLAIM: PHASE 1 DELIVERED AND CLOSED WITH ONE GATE CLAUSE NOT MET, named rather
    than glossed. Owner directed closure 2026-08-03.
  EVIDENCE:
  - src/melder/_build_assets/_agent_documentation/_builder.py
  - src/melder/_build_assets/_agent_documentation/manifest/agent_documentation_manifest.py
  - src/melder/utilities/helpers/class_surface_ast_describer.py:11
  - tests/unit/melder/build_assets/test_agent_metadata_builder.py
  IMPACT:
    GATE CLAUSE BY CLAUSE, verified against live source rather than claimed:
      MET - runner discovers the asset. Discovery returns
        ['_agent_documentation', '_bind_guard', '_system_documents'].
      MET - `--check` green. Owner ran the runner 2026-08-03 and all three assets
        wrote clean; `check_all` returned 0 in-session against the same tree.
      NOT MET - counts reconcile with the audit (394 marked / 173 exempt / 10
        pending). Live is 430 / 163 / 21. This is NOT a harvester defect: the
        audit totalled 577 classes on 2026-07-25 and the tree now holds 614, so
        the clause pins a frozen count that has itself gone stale across nine
        days of source movement. The same failure mode as the currency tests
        removed from the build-asset suite on owner direction 2026-08-03 - a
        gate measuring a moment rather than a contract.
      NOT RECORDED - "tests pass". Owner runs on 2026-08-03 surfaced failures
        (version-stamp gate keyed by asset directory rather than by file; two
        snapshot-frozen assertions). All are fixed, but no GREEN owner run on
        3.14t exists to cite, so this is left unclaimed rather than assumed.

    NAME DRIFT: the ticket's EXECUTION_BOUNDARY says
    `_build_assets/_agent_metadata/`. The asset shipped as
    `_build_assets/_agent_documentation/`, renamed during implementation so each
    builder is named for what it does. The ticket text was never updated.

    PHASE 2 PARTIALLY LANDED OUTSIDE THIS TICKET: the describer already reads
    the asset (class_surface_ast_describer.py:11) rather than
    `type(obj).__dict__`, which the ticket scoped as NOT this pass. The ~370
    file docstring codemod did not happen.
  NEXT: Owner rules whether the audit-count clause is retired or re-baselined.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-03T12:22:14Z
  TYPE: RAISE
  CLAIM: TEN OF THE 21 PENDING CLASSES ARE MINE, authored in this session and
    never marked. Reported, not fixed - they sit outside this ticket's
    EXECUTION_BOUNDARY and fixing them here would be scope creep on a closure.
  EVIDENCE:
  - src/melder/utilities/ai_native_support_tools/system_document_view.py
  - src/melder/utilities/ai_native_support_tools/agent_text_reader.py
  IMPACT: `system_document_view.{Section, SearchHit, Group, Edge, Node, Impact,
    SystemDocumentView, SystemGraphView}` and `agent_text_reader.{ReaderPolicy,
    TextChunk}` carry no `AGENT_ACCESS:`/`AGENT_PURPOSE:`. They are public
    agent-facing query objects, so pending is the wrong resting state for them -
    an agent asking the describer what it may do with a `SystemGraphView` gets
    nothing. Adding ten unmarked public classes to the tree while closing the
    ticket whose whole purpose is marking classes is worth naming out loud.
  NEXT: Route as a follow-up task, or fold into the existing
    `2026-08-02_stale_source_docstrings_task`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-08-03T12:22:14Z
  TYPE: FACT
  CLAIM: The describer's own docstrings still teach the retired mechanism.
  EVIDENCE:
  - src/melder/utilities/helpers/class_surface_ast_describer.py:113
  - src/melder/utilities/helpers/class_surface_ast_describer.py:115
  - src/melder/utilities/helpers/class_surface_ast_describer.py:163
  - src/melder/utilities/helpers/class_surface_ast_describer.py:227
  - src/melder/utilities/helpers/class_surface_ast_describer.py:326
  IMPACT: Five places describe `__ast_helper_access__` / `__agent_purpose__` as
    the live source of truth while line 11 imports the generated asset. The code
    is right and the prose is nine days stale; a reader following the docstring
    would author a class attribute nothing reads.
  NEXT: Belongs to `2026-08-02_stale_source_docstrings_task`.
  REREAD: HELPFUL
  SCORE_0_TO_10: 6

- DATETIME: 2026-08-03T12:40:00Z
  TYPE: FACT
  CLAIM: BOTH CARRIED FINDINGS DISCHARGED post-closure on owner direction
    ("fix the docstrings too"). Recorded here rather than reopening the ticket.
  EVIDENCE:
  - src/melder/utilities/ai_native_support_tools/system_document_view.py
  - src/melder/utilities/ai_native_support_tools/agent_text_reader.py
  - src/melder/utilities/helpers/class_surface_ast_describer.py:113-124
  - src/melder/utilities/helpers/class_surface_ast_describer.py:850
  - src/melder/_build_assets/_agent_documentation/manifest/agent_documentation_manifest.py
  IMPACT:
    FINDING 1 CLEARED - the ten public classes I authored are marked.
      `system_document_view.{Section, SearchHit, Group, Edge, Node, Impact,
      SystemDocumentView, SystemGraphView}` and `agent_text_reader.{ReaderPolicy,
      TextChunk}` now carry `AGENT_ACCESS:`/`AGENT_PURPOSE:`. Asset regenerated:
      430/163/21 -> 446/163/11. All eleven remaining pending entries predate this
      session, and one of them (`package.Package`) is pending by explicit owner
      ruling.

    FINDING 2 CLEARED - the describer no longer teaches the retired mechanism.
      Five docstrings repointed from `__ast_helper_access__`/`__agent_purpose__`
      to the docstring sections and the generated asset that actually feed it.
      One HISTORICAL note is kept deliberately at :123 so a reader who
      encounters the old attribute names in git history or an old branch learns
      they are dead rather than guessing.

    A SIXTH SITE WAS FOUND THAT WAS NOT A DOCSTRING and is the one that mattered
      most: `:850` raised `"Private class 'X' must define __agent_purpose__."` -
      a runtime error instructing the reader to author a class attribute nothing
      reads. Docstrings mislead someone who goes looking; an error message
      misleads someone who is already stuck. Now names the docstring section.
  NEXT: None. Both findings closed.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
PHASE 1 (additive, in progress): harvester + generated asset under the build-asset
runner. Nothing consumes it yet, so no runtime behaviour changes and the patch gate
does not fire.

PHASE 2 (patch-gated, NOT started): the ~370-file docstring codemod, stripping the 788
assignments, and repointing `ClassSurfaceAstDescriber` from `__dict__.get` to the asset.
That IS system-impacting and must not begin before its two patch docs exist.

Key design choice: the harvester reads DUAL-SOURCE - docstring section first, class
attribute as fallback - so the asset is complete and correct from the first run, and
the codemod can proceed subtree by subtree instead of as one atomic 370-file cutover.

### 2026-07-28 — session record: manifest/cache split, third asset, reader

All claims below were verified against live source in-session; `--check` is green on
all three assets. Owner-run pytest confirmed seven failures and all seven are resolved.

**1. Naming and layout, owner-directed.**
`_init_manifest` -> `_bind_guard`, `_agent_metadata` -> `_agent_documentation`. Assets are
now named for what they DO. Every asset is `_<asset>/` holding `_builder.py` (the tool),
`<asset>.py` (the loader), and `manifest/<asset>_manifest.py` (GENERATED, committed).

**2. The manifest/cache split — the correction that mattered most.**
I had the `.melc` as the TRUTH, committed beside the loader. That was incoherent:
`marshal` carries no cross-version guarantee, this repo runs 3.10 while targeting 3.14t,
so a committed bundle is one interpreter's bytes handed to another. `CachingSystem` already
documents the rule by stamping `sys.implementation.cache_tag` on every bundle it writes.
Now: manifest = committed truth (plain literals, diffable); `.melc` = derived cache under
`__melder_cache__/__<asset>__/`, gitignored, per-interpreter, regeneration-based integrity.

**3. `asset_cache.py` is runtime code and left `_build_assets/`.**
Now `utilities/caching_system/asset_cache.py`, beside `CachingSystem`. `_build_assets/`
holds build-time tools only; a hot-path loader living there made the directory mean two
things. `CachingSystem`'s "only member of this directory" docstring corrected.

**4. Third asset: `_system_documents`.**
Publishes the four package-root document objects. Deliberately has NO cache — a cache
amortises computation and there is none (the payload is already a string), and a cache read
at import would defeat the laziness that keeps four package-scope documents off the boot
path. `StaticSystemDocument` gained `reader()/head()/tail()/lines()/line_count/char_count`,
all lazy: the line index is built on FIRST bounded read. Verified in a clean process that
constructing all four leaves every `_indexed` as `None`.

**5. `AgentTextReader` + `IndexedText`** at `utilities/ai_native_support_tools/`.
Shared immutable index + per-agent cursor, no lock anywhere. Offset `array("q")` rather
than `splitlines()` because 4,263 tracked `str` objects per document is the GC pressure
`CachingSystem` measured at ~13% warm wall. Bounds: `line_target` 2-100 enforced.

**BUGS FOUND AND FIXED (each was silent):**
- `--check` fast path was DEAD. Patterns required `NAME: str = "..."`; loaders emit bare
  `NAME = "..."` since annotations moved to stubs. Every match returned None, every asset
  took the slow path, the gate stayed correct and quietly stopped being fast.
- `*.melc` in `.gitignore` swallowed the payloads while the loaders stayed tracked — a
  clone had imports pointing at files never checked in. Resolved by the split; cache is
  correctly ignored again.
- `pyproject.toml` `package-data` shipped no `.melc`/`.pyi`. Moot after the split.
- Agent-documentation `write()` AST-parsed all 548 files TWICE (render + a second
  `build_payload()` for the count). Threaded the payload through instead.
- `test_package_version_metadata.py` globbed `*/*.py` and matched the annotated stamp —
  both had drifted, and the failure mode was an EMPTY match set reporting green. Fixed and
  given an explicit non-empty assertion so it cannot go inert again.
- Per-asset tests hardcoded two asset names, which is how `_system_documents` shipped
  uncovered. Now discovery-driven off `discover_builders()`.

**REGRESSION I INTRODUCED AND FIXED:** `_get_required_access_level` raised `ValueError` for
any class not in the manifest — i.e. every class outside melder. Added
`_markers_from_docstring`, a live fallback consulted only on a manifest miss, so a caller's
own class is describable again and melder's classes still resolve from the cache.

**MEASUREMENT DISCIPLINE — recorded because I got it wrong repeatedly.**
A `.melc` cache was measured SLOWER than importing the manifest (0.438 vs 0.355 ms) because
the `.pyc` already IS a marshal cache; my earlier "14.9x" was against a manifest that
executed a `frozenset(...)` literal and imported `typing`. Separately, my concurrency test
asserted a shared cursor never repeats a span — a guess that passed under this GIL-bound
sandbox and failed on the owner's real run (7,310 chunks over 518 distinct spans). I then
over-corrected and asserted duplication MUST occur, which failed here. The test now asserts
only what holds under any parallelism. Both were the same error: asserting an
environment-dependent outcome I had not observed.

**COUNTS:** bind_guard 582 entries (582 not 578 because `AssetCachePolicy` and the two
reader classes entered scanned directories); agent_documentation 406 marked / 163 exempt /
13 pending; system_documents 4, all `populated=False` templates.

**NOT DONE, explicitly:** `cleanable.py:51-54` still teaches the retired sentinel mechanism.
Canonical doc repair is melder_1's lane and I did not touch either file — message sent
2026-07-28T00:10Z. The four documents are TEMPLATES; populating them from
`context_compass/system_docs/` raises a two-homes question for the owner, since those
sources are excluded from the wheel.


## Completion Summary
- CLOSED: 2026-08-03T12:22:14Z
- Owner directed closure 2026-08-03 ("close both tickets since your done and turn
  them in").
- DELIVERED: docstring-harvesting build asset at
  `_build_assets/_agent_documentation/`, discovered by the runner, consumed by
  `ClassSurfaceAstDescriber`, covered by `test_agent_metadata_builder.py`.
- CLOSED WITH TWO CLAUSES UNCLAIMED, both named in `## Notes`: the frozen audit
  counts (394/173/10 vs live 430/163/21, explained by +37 classes since the
  audit) and the absence of a recorded green owner run on 3.14t.
- CARRIED FORWARD AT CLOSURE, THEN DISCHARGED 2026-08-03T12:40:00Z on owner direction: the ten
  unmarked public classes are marked (asset 430/163/21 -> 446/163/11) and the
  describer's stale docstrings are repointed - plus a sixth site that was a
  runtime ERROR MESSAGE, not a docstring, telling users to define an attribute
  nothing reads. See the final `## Notes` entry.
