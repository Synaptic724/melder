# Component patch: SpellCompiler and Validation Pipeline - cycle consumers (2026-09-26)

## Before
- Every spell that reaches a cycle read "Spell 'X' is part of a dependency cycle: ...", members and consumers alike.

## After
- Members: unchanged. Consumers: "Spell 'X' cannot be built: it needs 'Y', which is part of a dependency cycle: ...
  Break that cycle (...); 'X' itself is not part of that cycle." Y is the spell's direct dependency on the route.
  When Y is an intermediate it reads "which depends on a dependency cycle: ..."; when Y is a self-loop it reads
  "which depends on itself ('Y' -> 'Y')". For a self-loop cycle the fix reads "Fix '<loop spell>' (remove that
  constructor dependency or give that parameter a default)".

## Interface / state / failure deltas
- Message text only.

## Validation expectations
- Strategy unit tests and one integration test; suites green.
