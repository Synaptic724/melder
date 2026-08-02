# Epic: Replace __melder_registration_guard__ with a bind-time internal lookup

- Completed: 2026-07-27T23:19:33Z
- Summary: Guard replacement SHIPPED and owner-accepted. The retired
  `__melder_internal__` sentinel and the `MelderRegistrationGuard` /
  `_RegistrationGuardProxy` objects are gone from live code; refusal is now one
  module-level `assert_allowed(candidate, context="bind")` over an immutable
  `INTERNAL_MANIFEST` frozenset, exact `(module, qualname)` match with no MRO
  walk. Closure verified against live source on 2026-07-27, NOT taken on claim.

## Metadata
- Epic ID: EPIC-2026-07-22-internal-bind-guard-replacement
- Status: done
- Owner: melder_0
- Agent Name: melder_0, melder_1 (turned in by helper_f under owner directive
  2026-07-27)
- Priority: p3
- Created: 2026-07-22T10:18:00Z
- Updated: 2026-07-27T23:19:33Z

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Owner directed turn-in 2026-07-27. Exit shape re-verified
  against live source by helper_f rather than accepted on ticket claim:
  `assert_allowed` live at `src/melder/aether/spellbook/bind/bind.py:364`;
  `INTERNAL_MANIFEST` resolves from
  `src/melder/_build_assets/_bind_guard/bind_guard.py:93`; a repo-wide sweep for
  `MelderRegistrationGuard|_RegistrationGuardProxy|__melder_internal__` returns
  exactly ONE hit, `bind.py:68`, which is an ACCURATE docstring sentence
  explaining the behaviour change away from the retired sentinel - documentation,
  not residue, and retained per the preserve-comments rule.

## Closure Caveats (carried forward, do NOT lose)
- CANONICAL DOCS ARE STALE AGAINST THIS EPIC'S OWN DELIVERABLE. The manifest
  MOVED AGAIN after the docs were written: `src_architecture.md:597-602` and
  `src_components.md:2136-2163` cite
  `_build_assets/_init_manifest/internal_manifest.py`, a path that NO LONGER
  EXISTS on disk. melder_1 counts 13 such citations across the two docs.
  The mechanism is correct; the documented path is wrong TODAY.
- CORRECTION (helper_f, 2026-07-27T23:19:33Z, filed against my own error):
  an earlier revision of this section named the live path as
  `_build_assets/_bind_guard/bind_guard.py`. THAT IS WRONG AND WAS CAUGHT
  INDEPENDENTLY BY BOTH melder_0 AND melder_1 via the mailbox before it reached
  a doc fix. `bind_guard.py` is the LOADER - its own module docstring says the
  truth lives in a committed manifest and that only the manifest is generated,
  the loader being ordinary reviewed code. The COMMITTED MANIFEST is
  `_build_assets/_bind_guard/manifest/bind_guard_manifest.py`
  (`MANIFEST_VERSION 2.0.0`, `BUILT_FOR_VERSION 0.1.1`, `ENTRY_COUNT 582` -
  verified in source, not taken on claim). Repairing the docs from my original
  wording would have written the SECOND-NEWEST path. Root cause of the error:
  I read `bind_guard.py:93` (`INTERNAL_MANIFEST = _PAYLOAD["entries"]`), saw the
  symbol bound there, and stopped without tracing `_PAYLOAD` to its source.
- Note the entry count also drifted: both canonical docs say 577; live is 582.
- THREE `_build_assets/` subpackages now exist and only the retired one is
  described in the canonical docs: `_bind_guard/` (582), `_agent_documentation/`
  (406 marked), `_system_documents/` (4 docs, no cache by design). The runtime
  `.melc` cache helper moved OUT of `_build_assets/` to
  `utilities/caching_system/asset_cache.py` (imported at `bind_guard.py:28`).
- OPEN QUESTION RAISED TO OWNER BY melder_1, not resolved here: whether to
  re-point the docs a FOURTH time while the target is still moving.
- This does NOT reopen the epic - the objective (replace the guard mechanism) is
  met. It is doc drift and belongs to a doc lane. TASK-2026-07-25-guard-doc-truth
  is `ready` and is the natural home; it must NOT be closed as-is, because the
  drift it was written to fix has since regressed.
- Child tickets are NOT closed by this turn-in and remain independently routable
  (see the orphan note below).

## Child Tickets Left Open By This Closure
Closing this parent does not close its children. Still active at turn-in:
- `tickets/stories/2026-07-25_guard_manifest_truth_story.md` (melder_1, in_progress;
  board shows `review` awaiting owner acceptance - ticket/board disagree)
- `tickets/tasks/2026-07-23_bind_guard_sentinel_vs_set_benchmark_task.md`
  (gemini_0 DEPARTED, in_progress, yet anchored CLOSED on the board - a
  pre-existing three-way disagreement flagged by melder_1 on 2026-07-25 and
  still unresolved)
- `tickets/tasks/2026-07-25_guard_doc_truth_task.md` (melder_1, ready - see caveat)
- `tickets/tasks/2026-07-25_guard_graph_node_task.md` (melder_1, ready)
- `tickets/tasks/2026-07-25_c1_code_map_restore_task.md` (melder_1, ready)
- `tickets/tasks/2026-07-25_init_cache_package_placement_task.md` (melder_0, in_progress)
- `tickets/tasks/2026-07-25_sentinel_deadcode_strip_task.md` (melder_1, done SUPERSEDED)

## Objective
Owner idea (2026-07-22, verbatim intent): investigate REMOVING the
`__melder_registration_guard__` sentinel system and replacing it with a
CACHED BIND-TIME LOOKUP that recognizes melder-internal classes - so that
binding an internal object is refused by ONE lookup bind already holds,
instead of by a sentinel attribute stamped onto every internal class across
all systems. Candidate recognitions the owner named:
1. A cached lookup over the internal libraries/directories that knows the
   SHA256 of all internal classes - a bind candidate matching an internal
   SHA256 is refused.
2. "Maybe a faster smarter way": see the candidate's DIRECTORY/module path
   and understand it is melder - path-based recognition, no hashing at all.
The goal is unchanged policy (we do not bind internal objects) with a less
invasive, more performant mechanism: "making bind hold a lookup that we
assess during bind is way more performant than using a fucken sentinel."

## Current State (measured 2026-07-22, filesystem-verified)
- `src/melder/__melder_registration_guard__.py` (177 lines): guard singleton,
  identity `_SENTINEL`, instantiated at package import.
- Tagging: 329 files / 374 occurrences of `__melder_internal__` in
  `src/melder` - every internal class carries the ClassVar sentinel by hand.
- Enforcement: exactly ONE live call site -
  `bind.py:286  _mrg.assert_allowed(spell, context="bind")` - refusing with
  `InternalRegistrationError` (utilities/custom_exceptions).
- THE ASYMMETRY: the CHECK is already centralized at bind; the TAGGING is
  the distributed cost (329 files of discipline; every new internal class
  must remember the stamp, and a missed stamp = a bindable internal).

## Investigation Lanes (questions to answer, not designs to follow)
LANE A - path/module recognition (the likely "faster smarter way"):
- Can bind decide "this is melder-internal" from the candidate class itself:
  `cls.__module__` prefix ("melder.") and/or the defining file's location
  under the installed package root?
- Cost profile vs today: one string prefix check vs one getattr - measure,
  do not assume.
- Edge cases to resolve: user SUBCLASSES of internal classes (today the
  ClassVar sentinel INHERITS - user-module subclasses are refused; a
  module-path check would flip that - which behavior is INTENDED? ruling
  needed); crystallizer SyntheticModule worlds (rebuilt user modules must
  never read as internal); vendored/renamed installs; functions/instances
  vs classes as bind candidates (what does the guard actually receive?).
OWNER LEADING DIRECTION (2026-07-22, end of discussion): SPLIT the
  concerns. Docstrings keep ONLY the AST/agent metadata (sibling epic; no
  load-bearing policy in docstrings, so no -OO concern for the guard). The
  GUARD becomes an ORIGIN LOOKUP in bind: "is this class defined inside
  melder?" - anything in melder is imported, not bound - refined Lane A
  with an ALLOWLIST: a small explicit set of melder utility classes that
  ARE bindable, consulted only AFTER a melder-origin hit (user binds never
  pay the allowlist probe). Check cost: one interned-string compare on
  type(candidate).__module__ - the cheapest candidate discussed. The Lane A
  subclass ruling stands as the one deliberate behavior flip (user
  subclasses of melder classes become bindable under origin semantics).
  Lanes A2/A3/B remain recorded as alternatives for the investigation to
  race against this direction.

LANE A2 - DOCSTRING MARKER (owner extension, 2026-07-22): the sibling
  agent-metadata epic moves access metadata to docstring level - bind could
  read THAT marker as its guard signal ("this is easy to implement... a
  marker there instead of a sentinel would be much cheaper"). One
  convention, two consumers: agents/AST tooling read it offline, bind reads
  it live. Cost profile: docstrings already exist on every class (zero new
  memory), the check is one cls.__doc__ prefix probe, cache-able per class.
  MUST-ANSWER edges: (1) `python -OO` strips docstrings - the guard would
  vanish; fallback (AST-from-source, build-time manifest) or documented
  refusal to support -OO needs a ruling. (2) class __doc__ does NOT inherit
  - user subclasses of internal classes would NOT carry the marker, same
  behavior flip as the module-path lane (the Lane A subclass ruling covers
  both). (3) user classes whose docstrings coincidentally match the marker
  grammar - marker must be unambiguous.
LANE A3 - MELDER-DEFINED DUNDER METHOD (owner extension, 2026-07-22):
  replace the sentinel ATTR with a melder dunder METHOD on internal
  classes, and the guard becomes a method probe at bind. Why a method:
  it is the least-impacted carrier - untouched by -OO, ignored by
  dataclass/init machinery and data-plane reflection sweeps, no
  interaction with instance state or serialization. The probe at bind is
  ONE direct check on the candidate, replacing today's slow path
  (guard singleton -> assert_allowed call chain -> context strings) with
  a single lookup/call; the 177-line guard module collapses into it.
  Investigation questions: per-class definition vs hoisting to a shared
  internal base (inheritance kills the per-class stamping AND preserves
  today's subclass-refusal semantics - but base-scope correctness must be
  proven: does every internal class sit under one base, and does nothing
  user-facing?); presence-check vs call-and-answer; spoof/collision
  (a user defining the same dunder); memory/import cost measured, not
  assumed.
LANE B - internal SHA256 manifest:
- A cached registry of internal-class fingerprints consulted at bind.
- When is it built - build-time shipped manifest vs first-import scan vs
  lazy per-directory? What is import-time/first-bind cost over 329 files?
- Drift: patched/edited installs vs a shipped manifest; how does the
  registry stay honest without becoming its own maintenance burden?
- Note melder already fingerprints candidates during bind profiling -
  can the existing bind-time SHA be reused so the lookup is one set probe?
LANE C - removal blast radius:
- Everything that reads `__melder_internal__` or the guard besides bind
  (scan? SpellBinder? Rift workstation binding? crystallizer?); tests
  pinning InternalRegistrationError and sentinel behavior; the documented
  "user-instantiated but NOT user-bindable" contract (e.g. SpellContract
  descriptors must stay constructible by users while staying unbindable).
- The refusal UX must remain teach-grade and the exception type should
  survive (InternalRegistrationError), whatever the mechanism.
LANE D - the perf claim, measured:
- Benchmark bind-time cost: sentinel getattr vs path check vs SHA set
  probe, cold and warm, on the owner's 3.14t. The claim that the lookup
  beats the sentinel is the epic's premise - PROVE or adjust it.

## Exit Shape (what done looks like)
- A DECISION doc choosing the mechanism (or rejecting the change) with
  measurements attached.
- If chosen: the sentinel stamp removed from all ~329 files, the guard
  module retired or reduced, bind holding the one lookup, refusal UX
  unchanged, full suite green.

## Ticket Contract
- ENTRY_GATE: picked up explicitly; investigation lanes A-D answered with
  EVIDENCE (file:line + measurements) BEFORE any code change.
- EXECUTION_BOUNDARY: investigation phase touches no runtime code; the
  replacement phase is its own story set after the DECISION.
- DEPENDENCIES: bind pipeline (bind.py guarded entry), binding profile
  fingerprinting, InternalRegistrationError contract, crystallizer
  synthetic-module world (false-positive risk), and the sibling epic
  EPIC-2026-07-22-agent-metadata-to-docstring (shared docstring grammar if
  Lane A2 wins - ONE sweep serves both).
- EXIT_GATE: see Exit Shape.
- FAILURE_ESCALATION: DECISION_REQUEST to owner on the subclass-semantics
  ruling and on any mechanism trade-off with user-visible behavior change.

## Notes
- DATETIME: 2026-07-24T00:05:00Z
  TYPE: DECISION
  CLAIM: OWNER RULING - mechanism is a BUILD-TIME MANIFEST of `(module, qualname)`
    string tuples, not the sentinel and not a set of class objects. A build
    script scans `src/melder` and emits a generated module; bind checks
    `(module, qualname) in MANIFEST`. SCOPE RULING: guard EVERY class in
    `src/melder` - NO exclusion list, utilities included. Guarding and exporting
    remain orthogonal (the 9 exceptions + ProtocolCrafter stay importable and
    catchable, just never bindable - the existing SafeGuard precedent).
  EVIDENCE:
  - src/melder/__melder_registration_guard__.py:62-89 (MRO law + orthogonality)
  IMPACT: The blanket rule is ONLY safe because a (module, qualname) manifest is
    EXACT-MATCH and does NOT inherit. Listing `Cleanable` blocks `Cleanable`
    itself; a user subclass carries a different module/qualname, is absent from
    the manifest, and binds normally. Under the sentinel this was impossible -
    MRO propagation made a guarded base poison all 325 Cleanable subclasses,
    which is the entire reason today's curated 357-class split exists. The
    manifest retires that classification problem outright.
    ACCEPTED BEHAVIOR CHANGE: user subclasses of internal classes (e.g.
    `class MyRoom(RiftSpace)`) become BINDABLE; today the inherited sentinel
    refuses them. Owner-accepted as the deliberate flip.
  NEXT: Build `build_scripts/build_internal_manifest.py`, the `__init_cache__`
    codegen + cold-boot fallback, then strip the 397 sentinel stamps.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-07-24T00:05:00Z
  TYPE: MEASURE
  CLAIM: AST census of `src/melder` (module-level classes). 549 total: 357
    guarded, 192 unguarded. By top-level dir (guarded/unguarded): aether 154/148,
    nexus 112/1, crystallizer 59/3, mutation_research 18/5, utilities 13/34,
    root 1/1. DIRECTORY-BASED GUARDING IS NOT VIABLE - aether is a ~50/50 split.
    The 192 unguarded are user-extensible bases (Cleanable 325 subclasses;
    TransactionStrategy 30; CodegenCreationFamilyStep 30;
    DevopsInformationStrategy 10; CodegenCreationDiscoveryStrategy 10;
    SpellCodegenStrategy 8; CodegenPlanDiscoveryStrategy 6; SourceCustodyStrategy
    4; CrystalFactStrategy 4; DiffStrategy 3; Sync; AbstractElasticPool), plus
    internal analysis data-carriers and the 11 custom exceptions.
  EVIDENCE:
  - AST scan over src/melder/**/*.py, 2026-07-23
  IMPACT: Under the manifest ruling all 549 are covered - STRICTER than today,
    since the 148 unguarded aether analysis/strategy classes finally get covered
    at zero risk to user extension. Generator should assert the count at build.
  NEXT: Manifest generator emits all module-level classes; verify 549 at build.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-24T00:05:00Z
  TYPE: FACT
  CLAIM: `class_wraps` REMOVED from the package root (owner directive). A
    functools.wraps-style class-decorator helper with ZERO internal consumers -
    only the `__init__` import, the `__all__` entry, and a docstring mention.
    All three removed; `grep class_wraps src/` is clean apart from its own module.
  EVIDENCE:
  - src/melder/__init__.py (import, __all__ entry, docstring line removed)
  - tests/unit/melder/test_package_public_surface.py:286,296 (STILL ASSERTS IT -
    knowingly red until updated)
  IMPACT: Public root drops 66 -> 65 names. One test red by design.
  NEXT: Strip the class_wraps assertion from test_package_public_surface.py.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-23T19:11:52Z
  TYPE: DECISION
  CLAIM: LANE D PERF SPIKE & ARCHITECTURAL VERDICT COMPLETE (gemini_0, Python 3.14.0 free-threaded / no-GIL).
    Task TASK-2026-07-23-bind-guard-sentinel-vs-set-benchmark handed off and measured by gemini_0 per owner directive.
    (1) INSTANTIATION COST AT 1,000,000 OBJECTS:
        - WITHOUT Sentinel: 33.881 ms (33.88 ns/obj)
        - WITH Sentinel (__melder_internal__): 34.219 ms (34.22 ns/obj)
        - Instantiation Delta: +0.338 ms (+0.34 ns/obj) across 1,000,035 objects.
        - CONCLUSION: Pinning __melder_internal__ on class bodies carries 1.0% OVERHEAD TOPS (+0.34 ns/object) even at 1,000,000 live objects.
    (2) MEMORY FOOTPRINT:
        - Class-Level Sentinel (__melder_internal__ = _mrg.sentinel): Attributes live on Class.__dict__ once. 0 bytes per instance (80.1 bytes/obj for both).
        - Instance-Level Sentinel (self._melder_guard = SENTINEL in __init__): Adds +8 bytes/instance (+800 KB per 100k objects).
    (3) BIND CHECK FREQUENCY & CLOCK TIME:
        - Bind checks run ONLY on ~350 spell definitions during boot/bind (NEVER on live runtime objects).
        - Total startup clock time for ~350 bind checks: Sentinel = 0.029 ms vs Set = 0.022 ms.
        - Total lifetime startup difference: 7 microseconds (0.000007 seconds).
    (4) ARCHITECTURAL CONCLUSION:
        - Sentinel pinning is zero-memory-cost, cycle-free, and preserves automatic MRO subclass protection.
  EVIDENCE:
  - tests/experimentation/pinning_sentinel_1mil_pure.py
  - tests/experimentation/real_mrg_1mil_benchmark.py
  - tests/experimentation/class_vs_instance_sentinel.py
  - context_compass/tickets/tasks/2026-07-23_bind_guard_sentinel_vs_set_benchmark_task.md
  REREAD: OPTIONAL
  SCORE_0_TO_10: 10

- DATETIME: 2026-07-25T18:19:28Z
  TYPE: FACT
  CLAIM: The ruled mechanism is SHIPPED. `manifest_loader.py` exposes
    `INTERNAL_MANIFEST` as a frozenset of `(module, qualname)` tuples; the generated
    cache carries 578 entries stamped `BUILT_FOR_VERSION`; `assert_allowed` is one
    exact-match membership test; `bind.py:285` remains the single call site. Zero live
    `__melder_internal__` stamps remain in `src/melder` - the eight textual hits are
    all docstring prose. `build_scripts/build_internal_manifest.py` exists.
  EVIDENCE:
  - src/melder/__melder_cache__/__init_cache__/manifest_loader.py:32-69
  - src/melder/__melder_cache__/__init_cache__/internal_manifest.py:18-24
  - src/melder/__melder_registration_guard__.py:189-210
  - src/melder/aether/spellbook/bind/bind.py:285-285
  IMPACT: The epic's Exit Shape is substantially met on the code side. What remains is
    truth-alignment, not mechanism work, so the epic should not read as undesigned.
  NEXT: Execute STORY-2026-07-25-guard-manifest-truth.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-07-25T18:19:28Z
  TYPE: CONFLICT
  CLAIM: Read in journal order this epic argues AGAINST its own outcome. The last note
    before this one (gemini_0, Lane D, 2026-07-23T19:11:52Z) concludes that sentinel
    pinning is "zero-memory-cost, cycle-free, and preserves automatic MRO subclass
    protection" - a recommendation to KEEP the sentinel. The owner DECISION one day
    later (2026-07-24T00:05:00Z) ruled for the manifest and the code shipped. Lane D's
    conclusion is superseded, but nothing in the epic says so.
  EVIDENCE:
  - context_compass/tickets/epics/2026-07-22_internal_bind_guard_replacement_epic.md:203-226
  - context_compass/tickets/epics/2026-07-22_internal_bind_guard_replacement_epic.md:144-167
  IMPACT: An agent resuming from the epic tail would defend the retired mechanism and
    could reintroduce sentinel stamping as a "fix".
  NEXT: Leave both notes intact - append-only stands - and let this entry plus the
    corrected Handoff Summary carry the supersession.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
MECHANISM RULED AND SHIPPED. Owner ruled 2026-07-24 for a build-time manifest of
`(module, qualname)` string tuples; the code has landed (`manifest_loader.py`,
generated `internal_manifest.py` at 578 entries, guard rewritten to exact-match
lookup, `bind.py:285` still the one call site, sentinel stamps gone from source).

IMPORTANT FOR RESUMERS: Lane D (gemini_0, 2026-07-23) recommended KEEPING the sentinel
and its note sits last in journal order. That recommendation was SUPERSEDED by the
owner ruling the following day. Do not act on it.

Remaining work is truth-alignment, not mechanism design, and is carried by
STORY-2026-07-25-guard-manifest-truth: correct five guard-claim drift sites across
`src_architecture.md` and `src_components.md`, rebuild the empty C1 Code Map as a full
package inventory, correct the stale guard node in `src_graph.json` and regenerate the
readable graph, and strip the dead sentinel surface still present in the guard module
(patch-gated, blocked until patch artifacts exist).

Separately observed and owner-routed elsewhere: a 2026-07-25 gauntlet run raised
`ModuleNotFoundError: No module named 'melder.__melder_cache__.__init_cache__'`, so the
documented cold-boot cache rebuild did not engage in that environment.

