# code_description_patch_compiler_phase_3

## Metadata
- Patch ID: spellmap_miss_waits_2026_11_16
- Component: `CompilerPhase3` SpellMap resolution
- Status: implemented at 0.2.8303
- Owner: Mark (accountable); melder_0 (synaptic_python_developer)
- Created: 2026-11-16T20:40:00Z
- Updated: 2026-11-16T20:50:00Z
- Trigger: changed error semantics (a raise becomes a recorded socket)

## Control Flow Commitments
- `_resolve_spellmap_default` collects candidates as before. With candidates: one returns its mapping, several raise
  (unchanged). With none:
  - `hidden_out` given (Phase 3's own call): the hidden-provider shape (a class lookup that missed an X registered
    elsewhere) extends `hidden_out`; every miss returns `{}`.
  - `hidden_out` None (a direct caller): raises the RuntimeError, with the hidden sentence in that shape (unchanged).
- `_build_local_frame_dag` hands an empty result to `_record_unresolved_miss` (unchanged); the SPELLMAP_DEFAULT
  branch now adds the socket to `socket_unresolved` whenever the dependency carries a SpellMap, and records hidden
  ids and frame keys only when `spellmap_hidden` has registrations.
- `_build_local_topology` marks the socket UNRESOLVED_INPUT and keeps `_dependency_key_for_dep`'s key (the
  SpellMap's canonical key) because the spell is resolvable (unchanged code).

## Edge and Error Semantics
- A SpellMap with an `override` payload whose address is empty records no payload (Phase 9 records a SpellMap
  payload only on a dependency edge) and waits like any other.
- A non-resolvable root resolves nothing and records nothing (unchanged).
- The meld-time error and the Phase 4 warning name the SpellMap through `UnresolvedInputError._spellmap_address_name`;
  the meld-time path reads it from the constructor signature's default and skips the class-lookup hidden-candidate
  search for a SpellMap parameter (Phase 3 records the hidden-provider shape itself).

## Invariants and Idempotency
- Phase 3 stays a pure function of the pool at the time it runs; re-running it after a provider arrives yields a
  NORMAL socket with the provider as its target.

## Explicit Non-Goals
- No change to `_spellmap_frame_matches`, the class-lookup rules, or the several-candidates error.
