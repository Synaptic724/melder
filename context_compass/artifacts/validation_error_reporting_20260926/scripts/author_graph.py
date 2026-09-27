"""Author graph prose for the conjure-report lane in a scratch descriptor tree (2026-09-26).

Usage: python author_graph.py <descriptor_root>
Edits authored fields only; the mechanical tier comes from extract_graph.py.
"""
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
P = "melder.aether.spellbook.spell_compiler"


def edit(rel: str, node_id: str, **fields: object) -> None:
    """Set authored fields on one node, or append to its responsibilities with `add=`."""
    path = root / rel
    data = json.loads(path.read_text(encoding="utf-8"))
    node = data["nodes"][node_id]
    add = fields.pop("add", None)
    replace = fields.pop("replace", None)
    for key, value in fields.items():
        node[key] = value
    if replace is not None:
        old, new = replace
        items = node["responsibilities"]
        assert old in items, (node_id, old)
        items[items.index(old)] = new
    if add is not None:
        node.setdefault("responsibilities", []).append(add)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("authored", node_id)


edit("melder/utilities/helpers/general_helpers.json", "melder.utilities.helpers.general_helpers.SpellInputUtils",
     add="names spell version ids for user-facing messages (describe_spell_id: the quoted spell name, or a "
         "12-character id when the lookup cannot name it)")
edit("melder/utilities/custom_exceptions/spellbook_validation_error.json",
     "melder.utilities.custom_exceptions.spellbook_validation_error",
     role="The build-time 'your graph is broken' error: names each refused spell with its errors and what to change.",
     responsibilities=["surface conjure and meld validation failures with their reasons, by spell name",
                       "keep the refused spell objects attached for tooling"])
edit("melder/utilities/custom_exceptions/spellbook_validation_error.json",
     "melder.utilities.custom_exceptions.spellbook_validation_error.SpellbookValidationError",
     role="Exception for refused spells whose message lists each broken spell's errors by name, whole-graph errors, "
          "a warning count and internal-error marking.",
     responsibilities=[
         "render the message once at construction from the spells' Phase 4/6 results and the conduit diagnostics "
         "handed in through system_diagnostics",
         "show errors only: warnings are counted; strategy sources, details payloads and spell ids are never printed",
         "drop exact repeats, a binding-key cycle already reported as CIRCULAR_DEPENDENCY, and restating codes "
         "(root_not_viable, broken_spell_in_dag) when another error is shown",
         "mark INTERNAL_CODES (Melder bookkeeping checks) as internal errors to report",
         "never raise while rendering; keep broken_spells exactly as supplied",
     ],
     owns_state=["broken_spells"])
edit("melder/aether/spellbook/spellbook_creation_system.json",
     "melder.aether.spellbook.spellbook_creation_system.SpellbookCreationSystem",
     add="hands the conduit resolution diagnostics to SpellbookValidationError at the conjure gate and the "
         "local-rerun gate, so a conduit-verdict refusal states its reasons (the phase artifacts are already cleaned)")
edit("melder/aether/spellbook/spell_compiler/validation/strategies/circular_dependency_strategy.json",
     f"{P}.validation.strategies.circular_dependency_strategy.CircularDependencyStrategy",
     add="names the cycle's members (the loop closed once) and says how to break it")
edit("melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.json",
     f"{P}.validation.strategies.contract_provider_presence_strategy.ContractProviderPresenceStrategy",
     add="each error says what to change; an ambiguity error states how many providers match the contract")
edit("melder/aether/spellbook/spell_compiler/validation/strategies/parameter_policy_strategy.json",
     f"{P}.validation.strategies.parameter_policy_strategy.ParameterPolicyStrategy",
     add="treats typing.Any as not injectable, matching Phase 1, so *args: Any / **kwargs: Any are not variadic DI")
edit("melder/aether/spellbook/spell_compiler/validation/strategies/annotation_shape_guard_strategy.json",
     f"{P}.validation.strategies.annotation_shape_guard_strategy.AnnotationShapeGuardStrategy",
     replace=("treat list[T] as the only collection DI form: warn LIST_ELEMENT_NOT_DI_TARGET for a non-injectable "
              "element and UNRESOLVED_FORWARD_REF for unresolved forward references",
              "treat list[T] as the only collection DI form: warn LIST_ELEMENT_NOT_DI_TARGET only when a user class "
              "sits inside a non-injectable element (list[Optional[Plugin]]) - plain data lists get nothing - and "
              "UNRESOLVED_FORWARD_REF for unresolved forward references"))
edit("melder/aether/spellbook/spell_compiler/validation/strategies/required_holes_strategy.json",
     f"{P}.validation.strategies.required_holes_strategy.RequiredHolesStrategy",
     replace=("adds the list-only collection hint to REQUIRED_HOLE for set, frozenset, dict and tuple annotations",
              "adds the list-only collection hint to REQUIRED_HOLE only when a set, frozenset, dict or tuple "
              "annotation holds a user class; plain data containers get no hint"))
edit("melder/aether/spellbook/spell_compiler/system/validation/scope_ordering_strategy.json",
     f"{P}.system.validation.scope_ordering_strategy.ScopeOrderingStrategy",
     add="names holder and dependency with their existences and says which existence to change")
edit("melder/aether/spellbook/spell_compiler/system/validation/cycle_detection_strategy.json",
     f"{P}.system.validation.cycle_detection_strategy.CycleDetectionStrategy",
     replace=("emit at most one coarse cycle_detected error for the frame",
              "emit at most one cycle_detected error for the frame, naming up to ten spells left in or behind the "
              "cycle (all of their ids in details)"))
print("done")
