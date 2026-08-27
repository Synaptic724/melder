# Architecture Patch: persistence_loop_m1_m5_residue_2026_07_12

## Metadata
- Patch ID: persistence_loop_m1_m5_residue_2026_07_12
- Status: active
- Owner ruling: 2026-07-12 session - mutation_0 owns the persistence-loop epic
  (and all prior melder_0 lanes); owner ordered implementation of the remaining
  parts. This patch covers the two well-scoped residues: M1 (introspection) and
  M5 (codegen materialize verb). Remaining residue (load_order-driven unfold
  depth, R11 reverse-edge unseed, M8 callsign wiring) is staged as later slices.
- Ticket: tickets/epics/2026-07-02_agent_object_persistence_loop_epic.md

## Objective
M1: make synthetic modules introspectable (inspect.getsource / tracebacks / pdb)
via FIX B - non-angle-bracket `__file__` + loader `get_source` - plus the R12
linecache hygiene (clear on unpublish/cleanup and on re-exec).
M5: give the codegen room its missing materialization lane - one explicit
promotion verb (`materialize_codegen`) that validates through the existing
policy strategies and materializes accepted source as a live SyntheticModule.
Execution/preview lanes stay untouched: promotion is opt-in (residency-ladder
Progenitor act), never automatic.

## Non-Goals
- No change to execute_codegen / validate_codegen / research_preview semantics.
- No bind step inside the verb: bind stays a Spellbook act; once the agent (or
  user code) binds the materialized class, the landed M4 seam mints custody and
  the MR seams auto-record - the loop closes through existing machinery.
- No callsign/version-store wiring (M8) and no reverse-edge unseed (R11) here.
- No loader-chain reordering (load_order depth residue is a separate slice).

## Changed Components
- SyntheticModule loader machine (crystallizer/synthetic_module.py):
  `__file__` contract, loader `get_source`, linecache hygiene.
- CodegenCommandSystem (nexus/rift/command_system/codegen_command_system.py):
  +1 public verb, advertised per the discoverability law.

## Invariants (unchanged)
- World-first inversion: loader returns pre-existing objects; publish-before-
  exec; registry is the engine. get_source only READS retained source.
- Hot-swap boundary law, dynamic-lane gating, R-A covenant all untouched.
- Verb idiom: action-hook scope + rift-gate ticket + room lock + memory record.

## Invariants (new)
- Synthetic `__file__` is `synthetic://<module_name>.py` - never resolvable on
  any OS (":" illegal in Windows path segments; scheme-style on POSIX), so
  linecache stat always falls through to `__loader__.get_source`.
- Materialization is validation-gated: a rejected validation refuses the verb
  with the validator's own payload; nothing registers or publishes.
- R8 no-half-published law: exec failure inside materialize tears the module
  back down (cleanup) before the error propagates.
- Pre-bind sentinel identity: materialized-but-unbound modules carry
  `spell_crystal_id="unbound_codegen"` / `binding_signature="codegen_materialized"`
  (rebuild-lane sentinel precedent); bind replaces nothing - custody is minted
  fresh by the bind seam per M4.

## Interface Deltas
- `_SyntheticModuleImportLoader.get_source(fullname)` (importlib InspectLoader
  contract; returns retained source or raises ImportError for unregistered names).
- `SyntheticModule.__file__` format change `<synthetic:X>` -> `synthetic://X.py`
  (single construction site; no in-src consumer sniffs the old form - grep-proven).
- `CodegenCommandSystem.materialize_codegen(code, *, module_name, frame_name)`
  -> Dict payload; added to `_CODEGEN_COMMAND_METHOD_NAMES`.

## Migration Order
1. synthetic_module.py (M1) - self-contained.
2. codegen_command_system.py (M5) - depends on nothing from step 1.
3. Tests (unit: introspection contract; unit: verb contract with mocked engine).
4. Epic milestone/notes sync + board ownership sync.

## Rollback
Revert the two source files + tests. No record shape, custody, or config change.

## Ticket Coverage Matrix
| Delta | Epic item |
| --- | --- |
| __file__ + get_source + linecache | M1 / R12 / R13 / T-F5 |
| materialize_codegen verb | M5 ("the X") |
| advertisement tuple | discoverability law |
