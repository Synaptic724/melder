# Component patch: SpellCompiler Phase 3 / Phase 4 - ambiguous provider report

<!-- BEGIN ENTRY: "Before and after" -->
## Before and after
- Before: `_resolve_single_by_annotation` raised `RuntimeError("SpellCrafter Phase 3: multiple DI candidates ...")`
  at >1 resolvable candidates; the spell's compile aborted; no Phase-4 issue existed.
- After: the resolver returns the candidates; the DAG builder records the parameter in `socket_ambiguous` (no
  dependency id); the topology socket is `AMBIGUOUS_INPUT`, `target_spell_ids=()`, `referenced_spell_ids` = the
  candidate ids in sorted order, `dependency_key` kept; `AmbiguousProviderStrategy` emits
  `SpellValidationIssue(severity="error", code="AMBIGUOUS_PROVIDER", message=..., details={spell_id,
  parameter_name, expected_type, candidates=[{spell_id, spell_name, spellframe, binding_name}, ...]})`.
- Message shape: "Parameter 'profile' on spell 'MCPScanner' expects ScanProfile, but 2 registered spells
  provide it: ScanProfile at (spellframe='agents', binding_name='ScanProfile'); ScanProfile at
  (spellframe='artificial_intelligence_tools', binding_name='ScanProfile'). Select one with a SpellMap default on
  the parameter (SpellMap(spellframe=..., binding_name=...)), supply it at meld with override={'profile': ...}, or
  bind only one provider of this type."
<!-- END ENTRY: "Before and after" -->

<!-- BEGIN ENTRY: "Validation expectations" -->
## Validation expectations
- Unit: the resolver returns both candidates; the topology socket kind/references; the strategy's issue from a
  two-candidate topology; the watcher includes the kind; the cycle strategy skips it.
- Component: `test_two_providers_remain_an_ambiguity_error` asserts the socket kind and the Phase-4 error.
- Integration: two providers -> `SpellbookValidationError` at conjure carrying the code, both addresses and both
  remedies; the two-`ScanProfile` shape; the five sites that pinned "multiple DI candidates" converted.
<!-- END ENTRY: "Validation expectations" -->
