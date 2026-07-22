# Epic: Replace __melder_registration_guard__ with a bind-time internal lookup

## Metadata
- Epic ID: EPIC-2026-07-22-internal-bind-guard-replacement
- Status: active (investigation; NOT designed)
- Owner: UNASSIGNED
- Agent Name: -
- Priority: p3
- Created: 2026-07-22T10:18:00Z
- Updated: 2026-07-22T10:18:00Z

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
  synthetic-module world (false-positive risk).
- EXIT_GATE: see Exit Shape.
- FAILURE_ESCALATION: DECISION_REQUEST to owner on the subclass-semantics
  ruling and on any mechanism trade-off with user-visible behavior change.

## Notes
- DATETIME: 2026-07-22T10:18:00Z
  TYPE: MEASURE
  CLAIM: Epic captured from owner directive. Current-state numbers measured
    this session (329 files / 374 tags / 1 enforcement site / 177-line guard).
    UNASSIGNED by owner instruction; active for pickup.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:286
  - src/melder/__melder_registration_guard__.py:1-177
  - grep counts, 2026-07-22 session
  REREAD: OPTIONAL
  SCORE_0_TO_10: -

## Context / Handoff Summary
Investigation epic. The policy (internal objects never bind) is NOT in
question - only the mechanism. Answer lanes A-D with evidence and
measurements, get the subclass ruling from the owner, THEN design.
