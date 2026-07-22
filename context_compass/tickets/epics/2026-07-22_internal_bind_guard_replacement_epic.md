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
