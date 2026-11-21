# component_patch_codegen_validation

## Metadata
- Patch ID: codegen_room_contract_2026_11_21
- Component: Codegen Internal Engine - validation (`CodegenNameResolutionStrategy`)
- Status: implemented at 0.2.8311-0.2.8313; merged into src_components, src_architecture, tests_components and the
  source graph
- Owner: Mark (accountable); melder_0 (synaptic_python_developer)
- Created: 2026-11-21T22:16:54Z
- Updated: 2026-11-21T23:30:00Z

## Component Purpose and Boundary
- Current boundary: name resolution refuses a load of any name that is not exposed by the namespace configuration,
  always allowed (`True`, `False`, `None`, `result`), an allowed builtin, or bound somewhere in the submitted code.
  "Bound" means an `ast.Name` in Store context, a function or class definition, a parameter (`ast.arg`) or an import
  alias.
- Target boundary: unchanged ownership. "Bound" also covers the forms Python records as a plain string on another
  node: `except ... as name`, the match captures and PEP 695 type parameters.

## Before/After Behavior Summary
- Before (0.2.8310): `except ValueError as e` then `str(e)`, `case n` then `n`, `case [first, *rest]`,
  `case {'a': v, **rest}`, `case int() as n` and `def f[T](x: T)` are refused with "Name '<name>' is not available
  in the codegen namespace."
- After: those loads pass name resolution; a name nothing binds is still refused with the same message.

## Interface Deltas
- Inputs: none changed.
- Outputs: fewer `validation_issues` for valid code; the refusal text is unchanged.
- Error semantics: unchanged for never-bound names.

## State and Lifecycle Deltas
- Owned state changes: none.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- Removed failure mode: valid room code that binds a name through an exception handler, a match pattern or a type
  parameter is refused at validation, and `execute_codegen` never runs it.

## Dependency and Ordering Constraints
1. The check stays scope-insensitive, as it is for every other binding form: a name bound anywhere in the code
   passes everywhere. Runtime NameError still reports a load outside the binding's scope.

## Validation Expectations
- Test/validation item: each binding form accepted, at module level and inside a function.
- Test/validation item: the wildcard forms (`case _`, `[*_]`) bind nothing and stay harmless.
- Test/validation item: a never-bound name is refused next to each new form.
- Evidence target: tests/unit/melder/aether/test_codegen_validation_strategy_unit_matrix.py and the safe-room
  integration pins, the GIL off.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none open (owner, 2026-11-21).

## Context / Handoff Summary
- What changed: specified.
- Remaining risks: none known; the change only widens what counts as bound.
- Next entrypoint: code_description_patch_codegen_name_resolution.md.
