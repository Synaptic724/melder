# Component patch: Existence classification (managed_spell_quantity_2026_10_15, S1)

Components: Existence (spellbook/existence), ResolutionStyleMatrix (spellbook), SpellArtifactProcessor (phase 9
model shell), ScopeOrderingStrategy (phase 6 system validation). Story:
STORY-2026-10-15-managed_existence_member.

## Before / after
- Existence: six `auto()` members -> seven; `managed_spell_quantity` is appended after `unique_per_spell_space`, so
  every existing member keeps its value and order. Its member docstring states the lease semantics; the class
  docstring's "six modes" and the AGENT_PURPOSE list name the seventh.
- ResolutionStyleMatrix: `EXPECTED_EXISTENCE_COUNT` 6 -> 7; `managed_spell_quantity` joins `ALL_EXISTENCE_NAMES`
  and `NON_UNIQUE_EXISTENCE_NAMES`, so the class-based family supports it and the callable and existing-object
  families list it unsupported; `LAST_UPDATED_ISO` moves to 2026-10-15. `validate()` keeps its rules.
- SpellArtifactProcessor `_build_model_shell`: `Existence.managed_spell_quantity` -> route family `"managed"`;
  any other unknown member still raises RuntimeError.
- ScopeOrderingStrategy: `scope_rank` gains `Existence.managed_spell_quantity: 0` (with unique). Before, a managed
  node had no rank and was skipped as holder and as dependency.

## Interface deltas
- Public: `Existence.managed_spell_quantity`.
- Internal: route family `"managed"` on `SpellCodegenModel.route_family` (consumed by S5's door templates; until S5
  a managed spell compiles no door and raises at the door compiler, so binding one is not useful before S5).

## State / failure deltas
- Phase 6 now refuses a managed holder of a cluster, lineage, per-conduit or spellspace dependency with the existing
  `scope_ordering_violation` diagnostic ("... depends on ... which lives for a shorter scope ..."), and accepts a
  managed holder of unique, managed or many dependencies; a holder of any existence may depend on a managed spell.
- Nothing changes for the six existing members: same values, names, ranks, routes and diagnostics.

## Dependency / ordering
- None inside the lane. S2 (bind options) and S5 (codegen) read the member and the route family.

## Validation expectations
- Unit: `ResolutionStyleMatrix.validate()` returns `()` with seven members; the class family supports the member and
  the two unique-only families list it unsupported; `_build_model_shell` maps it to `"managed"`; Phase 6 ranks (the
  accept/refuse cases above) - all under `-X gil=0` and `-X gil=1`.
- Existing suites green: the matrix, artifact processor and scope-ordering unit tests, the existence and
  scope-ordering integration tests.
