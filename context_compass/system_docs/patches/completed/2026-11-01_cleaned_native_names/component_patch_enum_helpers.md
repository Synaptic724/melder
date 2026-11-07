# EnumHelpers contract
<!-- BEGIN ENTRY: "EnumHelpers declared-name lookup" -->
## Purpose and boundary
Public native name normalization in src/melder/utilities/helpers/general_helpers.py.
## Before and after
Before: enum[value.lower()] cannot reach uppercase CLEANED. After: preserve that lowercase-key
fast path and, on a miss, match the actual declared member names case-insensitively.
## Interface and errors
Return a requested-family member unchanged; accept names, never enum values as alternate names.
None, unknown names, incompatible types and foreign enum families MUST keep ValueError refusal.
## State and lifecycle
Retain the existing bounded64-entry cache. Its key MUST distinguish input types so an equal raw
string cannot authorize a foreign StrEnum. No new mutable registry or cleanup owner is introduced.
## Failure delta
Uppercase/mixed declared names become reachable; unsupported inputs must not bypass validation.
## Dependencies and order
Read helper fully, write causal regressions, record RED, then implement and run the full helper module.
No SpellInputUtils behavior or caches change.
## Validation and unknowns
Prove lowercase/uppercase/mixed names, passthrough, aliases, old lower-key precedence, unsupported
values, and wrong-family refusal cold and after equal-string cache warming in both call orders.
Cache cross-type bypass is a hypothesis until the causal run; no helper input is guessed.
<!-- END ENTRY: "EnumHelpers declared-name lookup" -->
