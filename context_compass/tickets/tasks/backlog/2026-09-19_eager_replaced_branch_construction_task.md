# Backlog: Investigate eager construction of replaced dependency branches

## Metadata
- Status: draft
- Owner: user
- Agent Name: updater_0
- Created: 2026-09-19T23:31:09Z
- Priority: p3

## Objective
Consider whether whole-child overrides should prune the replaced constructor and its unused dependencies.
This is existing runtime behavior, separate from non-resolvable registration or required-input preflight.

## Evidence and Scope
A graph containing only an ordinary required int argument reproduces construction before replacement;
it does not need any resolvable=False registration. Current many-only/generalized emitters execute all
plan steps before the parent receives the replacement. Compatibility tests preserve that behavior.

- `tests/component/melder/aether/conduit/test_conduit_component_non_resolvable_overrides.py`
  `test_ordinary_branch_override_also_constructs_its_registered_child`.
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:769-887`.

## Context / Handoff Summary
Parked, not an active request. No pruning fix or new preflight was implemented. Any future change must
preserve shared dependencies, override addressing, hooks, reuse and cached shape semantics; prefer
compile-time work where possible. Do not reopen this while turning in the completed definition feature.
