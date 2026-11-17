# component_patch_spell_compiler

## Metadata
- Patch ID: spellmap_miss_waits_2026_11_16
- Component: SpellCompiler and Validation Pipeline (Phase 3 SpellMap resolution, Phase 4 required inputs), with the
  meld-time `UnresolvedInputError` text
- Status: implemented at 0.2.8303; merged into the canonical system docs
- Owner: Mark (accountable); melder_0 (synaptic_python_developer)
- Created: 2026-11-16T20:40:00Z
- Updated: 2026-11-16T20:50:00Z

## Component Purpose and Boundary
- Current boundary: Phase 3 resolves each constructor parameter against the spells registered when it runs. A
  single typed parameter that matches nothing is an UNRESOLVED_INPUT socket; a SpellMap default that matches nothing
  raises RuntimeError, outside the hidden-provider shape.
- Target boundary: unchanged ownership. Every parameter that matches nothing - typed or SpellMap - is an
  UNRESOLVED_INPUT socket; only the hidden-provider shape and several SpellMap candidates refuse.

## Before/After Behavior Summary
- Before: a SpellMap default whose address has nothing bound raised in Phase 3. At conjure the error arrived inside
  PhaseExecutionError ('local_frame'); at a late bind it came out of the bind's commit after the spell was registered.
- After: the socket is UNRESOLVED_INPUT with the SpellMap's canonical key. The bind or conjure succeeds; Phase 4
  warns (shown with validation warnings on); a bind under the SpellMap's frame re-gates the consumer; until a
  provider is there, a meld raises UnresolvedInputError naming the parameter and the SpellMap, constructing nothing,
  and a meld override supplies the value.

## Interface Deltas
- Inputs: none changed.
- Outputs: the Phase 4 UNRESOLVED_INPUT warning and UnresolvedInputError for a SpellMap parameter read "asks for the
  spell its default SpellMap(...) names, but nothing is bound there"; `expected_type` (the error field and the
  warning's detail) is that rendered SpellMap. A typed parameter's texts are unchanged.
- Error semantics: a SpellMap that matches nothing no longer raises at build time; UnresolvedInputError at meld.

## State and Lifecycle Deltas
- Owned state changes: none. The socket descriptor already carries the dependency key the watcher reads.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: a mistyped SpellMap address is reported at meld (and by the Phase 4 warning) instead of at bind
  or conjure.
- Removed failure mode: a SpellMap consumer bound before its provider is refused, and the refused late bind leaves
  it registered and uncompiled (the half-registration itself remains for other compile failures: #330).
- Changed failure mode: `SpellMap(ILogic)` naming a Protocol whose own definition is not bound waits as an
  unresolved input instead of failing at conjure.

## Dependency and Ordering Constraints
1. Phase 3's record must keep the SpellMap's canonical key as the socket's dependency key, so the existing watcher
   and the commit's dirty marker re-gate the consumer.
2. The meld text reads the SpellMap from the constructor signature's default on the failure path only.

## Validation Expectations
- Test/validation item: late bind before the provider (frame-named and class forms), meld refusal, provider later.
- Test/validation item: conjure with the address empty; override at meld.
- Test/validation item: the Phase 4 warning and the meld error name the SpellMap; a typed parameter's texts are
  unchanged.
- Test/validation item: the hidden-provider refusals and several candidates are unchanged; a direct caller raises.
- Evidence target: tests/unit, tests/component and tests/integration under melder/spellbook, the GIL off.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none open.

## Context / Handoff Summary
- What changed: implemented as specified. One refinement found while moving the wrong-frame method pin: the
  SpellMap rendering names a function or method spell by its qualified name, not its repr.
- Remaining risks: suites elsewhere that expect the zero-match raise (the full suite decides).
- Next entrypoint: code_description_patch_compiler_phase_3.md, then #329 Notes.
