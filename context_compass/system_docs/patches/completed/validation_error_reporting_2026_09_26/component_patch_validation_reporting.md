# Component patch: SpellCompiler validation reporting (2026-09-26)

## Before
- SpellbookValidationError listed every Phase-4 issue of each refused spell (warnings included, strategy order), a
  details repr per issue, 64-hex ids twice per spell, "Phase 4 issues"/"Phase 6 diagnostics" headings and "(none
  recorded)" sections.
- The conjure gate cleaned phase artifacts first and passed only spells, so Phase-6 reasons never reached the
  message; id-less errors named every spell in the pool; a diagnostic naming a missing dependency produced
  "raised with no broken spells".
- Several user-facing messages named spells by id; the id-cycle path repeated its start node; `*args: Any` broke
  the spell.

## After
- First line: "Spellbook validation failed. Broken spells: A, B." (names; the substrings kept for matchers).
- One block per spell with errors ("Name (frame 'x'):"), each error "  - <message> [CODE]"; whole-graph errors in
  their own block; exact duplicates dropped; BINDING_RESOLUTION_CYCLE hidden when CIRCULAR_DEPENDENCY is shown for
  the same spell; root_not_viable and broken_spell_in_dag dropped when another error is shown.
- Internal codes: "  - [internal] <message> [CODE]" plus one footer asking to report it.
- Footer: "N warnings not shown ...; conjure(validation_warnings=True) logs them." when Phase-4 warnings exist.
- Gates hand `system_diagnostics` from the conduit resolution state; spells without errors are not listed when
  diagnostics explain the failure.

## Interface / state / failure deltas
- Additive keyword `system_diagnostics`; `broken_spells` unchanged (gate fallback kept for the attribute).
- No state change; message text only, plus the two misfire fixes.

## Dependency / ordering
- Renderer reads diagnostics at construction (the resolution state owns them and may clean them later).

## Validation expectations
- Unit: exception renderer, strategy messages, misfires. Component: scope-ordering conjure message. Suites green.
