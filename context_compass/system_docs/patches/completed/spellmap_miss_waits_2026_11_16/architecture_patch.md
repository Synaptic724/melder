# architecture_patch

## Metadata
- Patch ID: spellmap_miss_waits_2026_11_16
- Status: implemented at 0.2.8303; deltas merged into src_components, src_architecture, tests_components and the
  source graph
- Owner: Mark (accountable); melder_0 (synaptic_python_developer) authors and implements
- Ticket: https://github.com/Synaptic724/melder/issues/329 (epic https://github.com/Synaptic724/melder/issues/328)
- Created: 2026-11-16T20:40:00Z
- Updated: 2026-11-16T20:50:00Z

## Patch Scope and Non-Goals
- Objective: a SpellMap default that matches nothing becomes an unresolved input at the SpellMap's address instead
  of an error, at conjure and at a late bind, so binding order never decides whether a SpellMap consumer binds.
  Decided by the owner on 2026-11-16 (the epic's Decision Log; #329 DECISION note).
- Non-goals: no change to what an address means (an omitted spellframe stays the bare frame; the class form
  `SpellMap(X)` stays; no binding-name-only SpellMap); the hidden-provider refusal and the several-candidates error
  stay; undoing a failed late bind is #330; no MelderOps change.

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| SpellCompiler Phase 3 (`CompilerPhase3`) | modify | a SpellMap miss records UNRESOLVED_INPUT instead of raising | none |
| Phase 4 required inputs (`RequiredHolesStrategy`) | modify | the warning names the SpellMap for a SpellMap socket | Phase 3 |
| meld refusal (`UnresolvedInputError`) | modify | the error names the SpellMap; one naming rule for both texts | none |
| SpellMap descriptor (`SpellMap`) | docstring | its contract said a SpellMap that matches nothing fails at build | none |

## Interface and Boundary Deltas
- `CompilerPhase3._resolve_spellmap_default(..., hidden_out=...)`: with `hidden_out` (Phase 3's own call) a miss
  returns `{}` instead of raising; the hidden-provider shape still fills `hidden_out`. Without `hidden_out` (a
  direct caller) every miss raises as before. Several candidates raise in every caller.
- `CompilerPhase3._record_unresolved_miss`: a SPELLMAP_DEFAULT socket that resolved to nothing is UNRESOLVED_INPUT,
  with hidden ids and frame keys only in the hidden-provider shape.
- `UnresolvedInputError._spellmap_address_name(spell_map)` (new, private static): renders a SpellMap as written
  (`SpellMap(spellframe='spectrum', binding_name='ServiceBuilder')`), the expected-type text of a SpellMap socket in
  the Phase 4 warning and the meld error.
- No public signature changes; no new public names.

## Cross-Component Invariants
- An UNRESOLVED_INPUT socket keeps its dependency key; for a SpellMap socket that is the SpellMap's canonical key,
  and the watcher index registers the consumer under the key's frame (`_extract_collection_frame_keys`).
- A bind's commit announces its binding keys' frames (`_default_dirty_marker`), so a provider bound under the
  SpellMap's frame marks the consumer dirty and its next meld re-runs Phases 1-4.
- Meld never constructs a consumer with an unsupplied UNRESOLVED_INPUT; the SpellMap object that is the parameter's
  Python default never reaches the constructor.
- A socket with hidden candidates is still refused in Phase 4 (HIDDEN_PROVIDER); the warning skips it as before.

## Migration and Rollout Order
1. Failing-first pins: a late bind before the provider, the class form with its class bound later, conjure with the
   address empty, the warning and meld-error texts.
2. Phase 3: `_resolve_spellmap_default` and `_record_unresolved_miss`, with their docstrings.
3. `UnresolvedInputError._spellmap_address_name`, the meld error and the Phase 4 warning for SpellMap sockets.
4. Docstrings that state the old raise (SpellMap, Phase 3, SocketKind, the watcher), moved pins.
5. System docs, graph descriptors, release note, notch 0.2.8303; the rebuild last.

## Rollback Strategy
- Rollback trigger: a consumer that relied on conjure or bind refusing a SpellMap with nothing at its address.
- Rollback steps: restore the raise in `_resolve_spellmap_default`; the texts may stay (they apply only to SpellMap
  sockets, which then never become unresolved).
- Post-rollback verification: the moved pins return to their 0.2.8302 expectations.

## Validation Expectations and Evidence Plan
- Late bind: a consumer of a frame-named SpellMap binds before its provider; its meld raises UnresolvedInputError
  naming the SpellMap; once the provider is bound at that address the meld wires it.
- Class form: `SpellMap(Provider)` with Provider bound bare later behaves the same.
- Conjure: an empty address conjures; a meld override supplies the value.
- Unchanged: hidden-provider refusals, several candidates, the direct-caller raise.
- Suites: unit, component and integration under melder/spellbook, then the full suite, the GIL off.

## Ticket Coverage Map
- Epic: https://github.com/Synaptic724/melder/issues/328
- Story: https://github.com/Synaptic724/melder/issues/329
- Tasks: none

## Unknowns and Decision Requests
- UNKNOWN: none for the code path.
- DECISION_REQUEST: none open; decided 2026-11-16.

## Context / Handoff Summary
- What changed: implemented at 0.2.8303 as specified here, with the pins listed under Validation; the durable
  deltas are merged into the canonical system docs and the graph. Moved on purpose: the zero-match pins of the
  component spell crafter, the hidden-provider control (D4), the break and error matrices and two wrong-frame
  cases, now waiting as unresolved inputs.
- What remains: the owner's acceptance on #329.
- Next entrypoint: component_patch_spell_compiler.md.
