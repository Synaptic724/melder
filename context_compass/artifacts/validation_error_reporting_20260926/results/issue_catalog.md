# Conjure validation messages - catalog for the owner review (2026-09-26)

Source of truth: results/issue_catalog_raw.txt (AST extraction of every SpellValidationIssue and SystemDiagnostic
construction in src/melder, file:line per entry). Paths below are relative to
src/melder/aether/spellbook/spell_compiler/. "User-fixable" = the user's bindings can cause it; "internal" = the
message describes Melder's own bookkeeping (index, blueprint, socket refs); whether internal ones are reachable
from user code is UNKNOWN unless stated.

## How they reach the user
- Phase 4 (per spell, 13 strategies registered in validation/validation_system.py:179-191): an error-severity issue
  makes the spell broken; conjure raises SpellbookValidationError listing ALL of that spell's issues, warnings too.
- Phase 6 (per conduit, 23 strategies in phases/compiler_phase_6.py:304-326): the conjure gate raises when the
  conduit verdict has an ERROR, but phase artifacts (Phase 4 and Phase 6 results) are cleaned first
  (spellbook_creation_system.py:1475 inside _prepare_resolution_for_conjure, gate at :243-257), so the exception
  prints "(none recorded)" - the reason is lost. Diagnostics without a spell id (e.g. cycle_detected) make the
  gate name every spell in the pool.

## Phase 4 errors (break the spell)
| code | fires when | message quality |
| --- | --- | --- |
| CIRCULAR_DEPENDENCY | spell reaches itself through its dependencies | path in 64-hex ids, start id repeated; no fix hint |
| BINDING_RESOLUTION_CYCLE | same cycle, by binding key | duplicates CIRCULAR_DEPENDENCY for every cycle |
| SELF_DEPENDENCY | spell depends on itself | ok; "configuration bug" is vague |
| DUPLICATE_SPELL_NAME | two visible spells share a name | good: says why and how to fix |
| DANGLING_DEPENDENCY | dependency id not visible in the book | names the dependency by hex id only |
| CONTRACT_IN_AUTOMATIC_MODE | SpellContract socket in an automatic world | good; could say conjure(dynamic=True) |
| SPELL_CONTRACT_INVALID | parameter marked contract, default is not a SpellContract | internal-sounding ("marked") |
| SPELL_CONTRACT_AMBIGUOUS | several providers match the contract key | does not name the providers |
| SPELL_CONTRACT_NON_RESOLVABLE_PROVIDER | contract selects a resolvable=False provider | good: says what to do |
| EXISTING_CREATION_MISSING_INSTANCE | existing-object spell has no instance | emitted by two strategies (duplicate) |
| EXISTING_CREATION_INVALID_EXISTENCE | existing object not Existence.unique | good |
| EXISTING_CREATION_PROFILE_MISMATCH | existing object lacks an instance profile | internal (bind builds profiles); two strategies |
| EXISTING_CREATION_PARAMETERS_PRESENT | existing object "has constructor parameters" | unclear what the user did |
| VARIADIC_DI_UNSUPPORTED | *args/**kwargs annotated for DI | no fix hint |
| DI_MISSING_ANNOTATION | "marked for DI but has no annotation" | Phase 1 never marks unannotated params DI (reachability UNKNOWN) |
| DI_BUILTIN_ANNOTATION | builtin annotation used for DI | Phase 1 never makes builtins DI (reachability UNKNOWN) |
| DI_COLLECTION_MISSING_ELEMENT / DI_COLLECTION_NON_FRAME | list DI without / with non-DI element | Phase 1 only makes list[T] DI when T is injectable (UNKNOWN) |
| SPELLMAP_DEFAULT_MISSING / SPELLMAP_DEFAULT_INVALID / SPELLMAP_MISSING_TARGET | bad SpellMap default | ok; MISSING is internal-sounding |
| MISSING_RESOLUTION_FRAME | "Phase 3 has not been run" | internal |
| MISSING_BINDING_PROFILE, NON_CLASS_SPELL_TARGET, CLASS_PROFILE_MISSING, NON_CALLABLE_SPELL_TARGET, CALLABLE_PROFILE_MISSING | bind metadata missing or wrong kind | internal; bind should never produce these |

## Phase 4 warnings (never break the spell)
| code | fires when | message quality |
| --- | --- | --- |
| REQUIRED_HOLE | plain parameter, no default | ok; container hint appended for dict/set/tuple |
| UNRESOLVED_INPUT | single typed parameter, no provider | good: says both fixes and the error you will get |
| OVERRIDE_REQUIRED | parameter references a resolvable=False definition | ok |
| LIST_ELEMENT_NOT_DI_TARGET | list[str]/list[Any]/list[non-class] | noise for data lists; doubles REQUIRED_HOLE |
| UNRESOLVED_FORWARD_REF (x2) | annotation is an unresolved ForwardRef | ok |
| SPELL_CONTRACT_MISSING_PROVIDER | contract key has no provider (dynamic) | ok |
| SPELLMAP_BINDING_NAME_NOT_NORMALIZED | SpellMap binding_name not normalized | good: gives the fixed value |
| NO_SPELLBOOK_FOR_DEPENDENCY_CHECK | spell has no owning book | internal |
| MISSING_DEPENDENCY_GRAPH | resolution frame without a graph | internal; message names no spell |

## Phase 6 diagnostics (conduit-level; reason currently lost at conjure)
User-fixable:
| code | severity | message quality |
| --- | --- | --- |
| cycle_detected | error | "Cycle detected in system dependency graph." - no spells, no path |
| scope_ordering_violation | error | hex ids; no fix hint (make the holder narrower or the dependency broader) |
| visibility_gap_dependency_filtered (x4 sites) | error | hex ids; "not visible to this Spellbook" gives no reason |
| collection_socket_no_providers | warning/error | good: has a remediation sentence |
| contract_cycle_detected | error | path of contract keys |
| root_dag_{node,edge,fan_out,depth}_limit_exceeded | configurable | hex root id; no hint which setting |
| dependency_type_unexpected | warning | hex ids; unclear what is wrong |
| broken_spell_in_dag | error | restates a Phase-4 break |
| root_not_viable | error | consequence of other errors (noise) |
| lineage_version_conflict, contracted_version_drift, identity_mixing_detected | error | version/lineage jargon, hex ids |
Internal consistency (Melder bookkeeping):
missing_index_node, edge_mismatch_index, edge_missing_from_blueprint, index_node_missing_from_blueprints,
missing_index_dependency, root_lineage_mismatch, root_lineage_conflict, lineage_conduit_conflict,
root_missing_in_index, root_not_marked_in_index, missing_root_blueprint, root_missing_in_dag, dag_orphan_node,
missing_phase4_validation, topology_dependency_mismatch, socket_ref_duplicate, socket_ref_missing_in_index,
socket_ref_missing_in_index_name, dag_index_orphan_socket, contract_key_missing.
