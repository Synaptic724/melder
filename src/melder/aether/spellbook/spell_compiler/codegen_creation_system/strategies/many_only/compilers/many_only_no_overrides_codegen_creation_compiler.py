"""
Codegen IR helpers of the many_only family.

What remains of the many_only no-overrides compiler after normal melds moved to the site-plan
runtime (S2b-2) and the old step and transient emitters were retired (R2, 2026-09-26); the module
path is kept so no importer moves:
    - `ManyOnlyCodegenPlanCallMode`: the call-mode labels of the Phase-10 transient schema;
    - `_build_many_only_unrolled_schema_from_plan`: the manifest's transient schema (data only);
    - `_hydrate_steps_from_rows` / `_resolve_root_instance_key`: manifest row hydration, read by
      the hydrator.
"""

from types import SimpleNamespace
from typing import Any, Dict, Optional, Sequence, Tuple
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_schema_helpers import (
    CodegenCreationSchemaHelpers,
)


class ManyOnlyCodegenPlanCallMode:
    """
    Many-only compiler-local call-mode labels.
    """

    __slots__ = ()
    CALL0: int = 0
    CALL1: int = 1
    CALL2: int = 2
    CALL3: int = 3
    CALL4: int = 4
    CALL5: int = 5
    CALL6: int = 6
    CALL7: int = 7
    CALL8: int = 8
    CALLN: int = 9


def _build_many_only_unrolled_schema_from_plan(
        plan: Any,
) -> Optional[Dict[str, Any]]:
    """
    Build a many-only-local unrolled schema from the standalone no-overrides plan.

    Contract:
        - Returns None when the plan does not expose the many-only unrolled arrays.
        - Returns None when any step has disposal methods because disposal-aware
          many registration must stay on the step-plan emitter.
        - Returns None when any call mode is CALLN.
    """
    if not hasattr(plan, "step_call_modes"):
        return None
    if any(plan.step_has_disposal_methods):
        return None
    call_modes = tuple(plan.step_call_modes)
    if ManyOnlyCodegenPlanCallMode.CALLN in call_modes:
        return None
    return {
        "step_count": len(plan.steps),
        "root_step_index": plan.root_step_index,
        "call_modes": call_modes,
        "dep1": tuple(plan.step_dep1),
        "dep2a": tuple(plan.step_dep2a),
        "dep2b": tuple(plan.step_dep2b),
        "dep3a": tuple(plan.step_dep3a),
        "dep3b": tuple(plan.step_dep3b),
        "dep3c": tuple(plan.step_dep3c),
        "dep4a": tuple(plan.step_dep4a),
        "dep4b": tuple(plan.step_dep4b),
        "dep4c": tuple(plan.step_dep4c),
        "dep4d": tuple(plan.step_dep4d),
        "dep5a": tuple(plan.step_dep5a),
        "dep5b": tuple(plan.step_dep5b),
        "dep5c": tuple(plan.step_dep5c),
        "dep5d": tuple(plan.step_dep5d),
        "dep5e": tuple(plan.step_dep5e),
        "dep6a": tuple(plan.step_dep6a),
        "dep6b": tuple(plan.step_dep6b),
        "dep6c": tuple(plan.step_dep6c),
        "dep6d": tuple(plan.step_dep6d),
        "dep6e": tuple(plan.step_dep6e),
        "dep6f": tuple(plan.step_dep6f),
        "dep7a": tuple(plan.step_dep7a),
        "dep7b": tuple(plan.step_dep7b),
        "dep7c": tuple(plan.step_dep7c),
        "dep7d": tuple(plan.step_dep7d),
        "dep7e": tuple(plan.step_dep7e),
        "dep7f": tuple(plan.step_dep7f),
        "dep7g": tuple(plan.step_dep7g),
        "dep8a": tuple(plan.step_dep8a),
        "dep8b": tuple(plan.step_dep8b),
        "dep8c": tuple(plan.step_dep8c),
        "dep8d": tuple(plan.step_dep8d),
        "dep8e": tuple(plan.step_dep8e),
        "dep8f": tuple(plan.step_dep8f),
        "dep8g": tuple(plan.step_dep8g),
        "dep8h": tuple(plan.step_dep8h),
    }


def _hydrate_steps_from_rows(
        *,
        steps_rows: Sequence[Dict[str, Any]],
        spell_lookup: Optional[Dict[str, Any]],
) -> Tuple[Any, ...]:
    """
    Hydrate executable step adapters from schema-only Phase11 step rows.

    Contract:
        - Requires spell_lookup when schema rows are used.
        - Validates required row fields and existence enum names.
        - Returns adapters exposing the same attributes consumed by the no-
          overrides compiler/runtime helpers in this module.
        - Contract payload entries are resolved to LIVE values here (2026-09-26):
          a phase-9 reference in a row is read back from the consumer's
          descriptor through `spell_lookup` (the consumer is always a step of
          the same lane), scalars pass through, and the adapter also carries
          the references (`contract_payload_refs`) so it mirrors a plan step.

    Raises:
        RuntimeError:
            When a row is invalid, a spell id is unknown, or a reference cannot
            be resolved (consumer missing, descriptor without a payload, key
            absent).
    """
    if spell_lookup is None:
        raise RuntimeError(
            "No-overrides codegen schema rows require spell_lookup for step hydration."
        )

    descriptor_cache: Dict[Tuple[str, str], Any] = {}
    hydrated_steps = []
    for row_index, row in enumerate(steps_rows):
        required_fields = (
            "instance_key",
            "spell_id",
            "creations_target_kind",
            "dependency_resolution_order",
            "collection_param_names",
            "uses_positional_override",
            "contract_positional_override",
            "has_contract_payload",
            "contract_payload_items",
            "use_spell_lock_hint",
        )
        for field_name in required_fields:
            if field_name not in row:
                raise RuntimeError(
                    "No-overrides codegen schema row is missing required field "
                    f"'{field_name}' at index {row_index}."
                )

        spell_id = row["spell_id"]
        spell = spell_lookup.get(spell_id)
        if spell is None:
            raise RuntimeError(
                f"No-overrides codegen step schema references unknown spell_id '{spell_id}'."
            )

        dependency_resolution_order = tuple(
            (
                param_name,
                tuple(dependency_keys),
            )
            for param_name, dependency_keys in row["dependency_resolution_order"]
        )
        contract_payload_items, contract_positional_override = (
            CodegenCreationSchemaHelpers.resolve_contract_payload_row_values(
                row, spell_lookup, descriptor_cache,
            )
        )
        contract_payload = None
        if row["has_contract_payload"]:
            contract_payload = {
                param_name: value
                for param_name, value in contract_payload_items
            }

        hydrated_steps.append(
            SimpleNamespace(
                instance_key=tuple(row["instance_key"]),
                spell=spell,
                creations_target_kind=row["creations_target_kind"],
                dependency_resolution_order=dependency_resolution_order,
                collection_param_names=frozenset(row["collection_param_names"]),
                uses_positional_override=row["uses_positional_override"],
                contract_positional_override=contract_positional_override,
                has_contract_payload=row["has_contract_payload"],
                contract_payload=contract_payload,
                contract_payload_refs=(
                    CodegenCreationSchemaHelpers.contract_payload_refs_from_row(row)
                ),
                use_spell_lock_hint=row["use_spell_lock_hint"],
            )
        )
    return tuple(hydrated_steps)


def _resolve_root_instance_key(
        *,
        steps: Tuple[Any, ...],
        root_spell_id: Optional[str],
) -> Optional[Tuple[str, Optional[int]]]:
    """
    Resolve the root instance key from Phase 11 step metadata.

    Contract:
        - Prefers the canonical (spell_id, None) root key when present.
        - Falls back to the first step whose spell_id matches root_spell_id.
        - Returns None when no matching step exists.
    """
    if root_spell_id is None:
        return None
    for plan_step in steps:
        # Concrete typing for mypy: callers only rely on 2-tuple instance keys.
        instance_key: Tuple[str, Optional[int]] = plan_step.instance_key
        if instance_key[0] == root_spell_id and instance_key[1] is None:
            return instance_key
    for plan_step in steps:
        # Concrete typing for mypy: fallback branch expects a tuple instance key.
        fallback_instance_key: Tuple[str, Optional[int]] = plan_step.instance_key
        if fallback_instance_key[0] == root_spell_id:
            return fallback_instance_key
    return None


