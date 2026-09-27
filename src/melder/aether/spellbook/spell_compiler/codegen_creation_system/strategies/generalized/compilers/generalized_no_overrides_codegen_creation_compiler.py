"""
Runtime helpers shared by the generalized family's plans.

What remains of the generalized no-overrides compiler after normal melds moved to the site-plan
runtime (S2b-2) and the old step and transient emitters were retired (R2, 2026-09-26); the module
path is kept so no importer moves:
    - `_hydrate_steps_from_rows`: Codegen IR row hydration (manifest rows plus live spells ->
      step views), read by the hydrator and the site-plan lowering.
    - `_construct_spell_instance` / `_build_kwargs_no_overrides`: the generic construction helper
      plans call for steps they do not emit as a direct call.
    - `_raise_meld_construction_error`: the shared construction-failure raise.
    - `_register_spell_instance` / `_register_spell_instance_prebound`: registration helpers the
      opt-in singleton specializer's emitted source calls.
"""

from types import SimpleNamespace
from typing import Any, Dict, Optional, Sequence, Tuple

from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_schema_helpers import (
    CodegenCreationSchemaHelpers,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError

_MISSING = object()


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
            "existence",
            "creations_target_kind",
            "dependency_resolution_order",
            "collection_param_names",
            "uses_positional_override",
            "contract_positional_override",
            "has_contract_payload",
            "contract_payload_items",
            "use_spell_lock_hint",
            "must_register",
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

        existence_name = row["existence"]
        try:
            existence = Existence[existence_name]
        except KeyError as exc:
            raise RuntimeError(
                "No-overrides codegen step schema contains unknown existence "
                f"'{existence_name}' at index {row_index}."
            ) from exc

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
                existence=existence,
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
                must_register=row["must_register"],
            )
        )
    return tuple(hydrated_steps)


def _raise_meld_construction_error(spell: Any, exc: BaseException) -> None:
    """
    Raise the ``MeldExecutionError`` for a failed constructor call.

    Shared by the site-plan lowering, the inlined fast path, the generic
    ``_construct_spell_instance`` helper and the transient unrolled executor, so
    all of them report construction failures identically.
    Lives off the hot path: only the failure branch calls it.

    Contract:
        - Always raises ``MeldExecutionError`` chained from ``exc``. Unresolved
          inputs never reach it: every family decides them before the call
          (``UnresolvedInputError.for_unsupplied``, design v2 S4).

    Raises:
        MeldExecutionError: Always.
    """
    raise MeldExecutionError(
        spell_id=spell.spell_index.selected_spell_id,
        spell_name=spell.spell_name,
        message=f"Error invoking spell '{spell.spell_name}'.",
        inner=exc,
    ) from exc


def _construct_spell_instance(
        *,
        plan_step: Any,
        instance_results: Dict[Tuple[str, Optional[int]], Any],
) -> Any:
    """
    Construct one spell instance from dependency results and plan metadata.

    Contract:
        - Reads dependencies from prior step results using plan_step call recipe.
        - Applies plan-time contract payload fields.
        - Supports __args__ positional payloads when present.
        - Preserves tuple positional payloads without rebuilding list objects.
        - Raises MeldExecutionError when dependency results are missing or call
          target invocation fails.
    """
    spell = plan_step.spell
    kwargs = _build_kwargs_no_overrides(
        plan_step=plan_step,
        instance_results=instance_results,
    )

    if spell.existence is Existence.unique and spell.is_existing_creation:
        instance = spell.user_created_object
        if instance is None:
            raise RuntimeError(
                "[MELD] EXISTING_CREATION spell has no `user_created_object` "
                f"(spell_id={spell.spell_id})."
            )
        return instance

    if not (spell.is_class_spell or spell.is_method_spell or spell.is_lambda_spell):
        return spell.spell

    raw_args = kwargs.get("__args__", _MISSING)
    if raw_args is _MISSING:
        args: Sequence[Any] = []
        call_kwargs = kwargs
    elif isinstance(raw_args, tuple):
        args = raw_args
        if len(kwargs) == 1:
            call_kwargs = {}
        else:
            call_kwargs = dict(kwargs)
            call_kwargs.pop("__args__", None)
    elif isinstance(raw_args, list):
        args = raw_args
        if len(kwargs) == 1:
            call_kwargs = {}
        else:
            call_kwargs = dict(kwargs)
            call_kwargs.pop("__args__", None)
    else:
        raise MeldExecutionError(
            spell_id=spell.spell_index.selected_spell_id,
            spell_name=spell.spell_name,
            message="__args__ override must be a list or tuple.",
        )

    try:
        return spell.spell(*args, **call_kwargs)
    except Exception as exc:
        _raise_meld_construction_error(spell, exc)


def _build_kwargs_no_overrides(
        *,
        plan_step: Any,
        instance_results: Dict[Tuple[str, Optional[int]], Any],
) -> Dict[str, Any]:
    """
    Build keyword arguments for one step without runtime override payloads.

    Contract:
        - Uses dependency_resolution_order produced by Phase 9.
        - Collection sockets (`plan_step.collection_param_names`) always map
          to a list, even with exactly one wired member.
        - Non-collection single dependencies map to one value; multiple map
          to a list.
        - Includes plan-time contract payload values.
    """
    dependency_resolution_order = plan_step.dependency_resolution_order
    contract_positional_override = plan_step.contract_positional_override
    if (
            not dependency_resolution_order
            and contract_positional_override is None
            and not plan_step.has_contract_payload
    ):
        return {}
    if (
            not dependency_resolution_order
            and contract_positional_override is None
            and plan_step.has_contract_payload
    ):
        contract_payload = plan_step.contract_payload
        if not contract_payload:
            return {}
        if not plan_step.uses_positional_override:
            return dict(contract_payload)
        contract_kwargs: Dict[str, Any] = {}
        for param_name, value in contract_payload.items():
            if param_name == "__args__":
                continue
            contract_kwargs[param_name] = value
        return contract_kwargs

    spell = plan_step.spell
    spell_id = spell.spell_index.selected_spell_id
    kwargs: Dict[str, Any] = {}
    collection_param_names = plan_step.collection_param_names
    for param_name, dependency_keys in dependency_resolution_order:
        dependency_count = len(dependency_keys)
        if dependency_count == 0:
            if param_name in collection_param_names:
                # Zero-provider required collection socket: inject an empty
                # list (owner policy) instead of omitting the parameter.
                kwargs[param_name] = []
            continue
        if dependency_count == 1:
            dependency_key = dependency_keys[0]
            try:
                dependency_value = instance_results[dependency_key]
            except KeyError as exc:
                raise MeldExecutionError(
                    spell_id=spell_id,
                    spell_name=spell_id,
                    node_id=spell_id,
                    param_name=param_name,
                    message=(
                        f"Dependency '{dependency_key[0]}' missing while "
                        f"building args for '{spell_id}'."
                    ),
                ) from exc
            if param_name in collection_param_names:
                # A list[Frame] socket with one wired member still injects a
                # one-element list; collection-ness is socket truth, not arity.
                kwargs[param_name] = [dependency_value]
            else:
                kwargs[param_name] = dependency_value
            continue
        if dependency_count == 2:
            first_dependency_key = dependency_keys[0]
            second_dependency_key = dependency_keys[1]
            try:
                first_value = instance_results[first_dependency_key]
            except KeyError as exc:
                raise MeldExecutionError(
                    spell_id=spell_id,
                    spell_name=spell_id,
                    node_id=spell_id,
                    param_name=param_name,
                    message=(
                        f"Dependency '{first_dependency_key[0]}' missing while "
                        f"building args for '{spell_id}'."
                    ),
                ) from exc
            try:
                second_value = instance_results[second_dependency_key]
            except KeyError as exc:
                raise MeldExecutionError(
                    spell_id=spell_id,
                    spell_name=spell_id,
                    node_id=spell_id,
                    param_name=param_name,
                    message=(
                        f"Dependency '{second_dependency_key[0]}' missing while "
                        f"building args for '{spell_id}'."
                    ),
                ) from exc
            kwargs[param_name] = [
                first_value,
                second_value,
            ]
            continue

        values = []
        for dependency_key in dependency_keys:
            try:
                values.append(instance_results[dependency_key])
            except KeyError as exc:
                raise MeldExecutionError(
                    spell_id=spell_id,
                    spell_name=spell_id,
                    node_id=spell_id,
                    param_name=param_name,
                    message=(
                        f"Dependency '{dependency_key[0]}' missing while "
                        f"building args for '{spell_id}'."
                    ),
                ) from exc
        if not values:
            continue
        if len(values) == 1 and param_name not in collection_param_names:
            kwargs[param_name] = values[0]
        else:
            kwargs[param_name] = values

    if contract_positional_override is not None:
        kwargs["__args__"] = contract_positional_override

    if plan_step.has_contract_payload:
        contract_payload = plan_step.contract_payload
        if contract_payload:
            for param_name, value in contract_payload.items():
                if param_name == "__args__" and plan_step.uses_positional_override:
                    continue
                kwargs[param_name] = value

    return kwargs


def _register_spell_instance(
        *,
        spell: Any,
        instance: Any,
        creations: Any,
        existence: Existence,
) -> None:
    """
    Register a constructed instance into creations for no-overrides execution.

    Contract:
        - Shared/per-conduit singleton scopes use add_creation.
        - many uses add_many_creations only when disposal methods exist.
        - spellspace scope uses add_creation on the direct spellspace-owned store.
    """
    _register_spell_instance_prebound(
        spell_id=spell.spell_id,
        instance=instance,
        creations=creations,
        existence=existence,
        has_disposal_methods=spell.has_disposal_methods,
        disposal_methods=spell.disposal_method_names,
    )


def _register_spell_instance_prebound(
        *,
        spell_id: str,
        instance: Any,
        creations: Any,
        existence: Existence,
        has_disposal_methods: bool,
        disposal_methods: Optional[Sequence[str]],
) -> None:
    """
    Register a constructed instance using prebound spell registration metadata.

    Contract:
        - Uses spell-static metadata (`spell_id`, disposal flags/methods)
          supplied by the generated step lane.
        - Preserves the same existence routing semantics as
          `_register_spell_instance`.
    """

    if existence in (
            Existence.unique,
            Existence.unique_per_conduit,
            Existence.unique_per_conduit_cluster,
            Existence.unique_per_conduit_lineage,
    ):
        creations.add_creation(
            spell_id,
            instance,
            has_disposal_methods=has_disposal_methods,
            disposal_methods=disposal_methods,
        )
        return

    if existence is Existence.many:
        if not has_disposal_methods:
            return
        creations.add_many_creations(
            spell_id,
            instance,
            has_disposal_methods=has_disposal_methods,
            disposal_methods=disposal_methods,
        )
        return

    if existence is Existence.unique_per_spell_space:
        creations.add_creation(
            spell_id,
            instance,
            has_disposal_methods=has_disposal_methods,
            disposal_methods=disposal_methods,
        )
        return

    raise RuntimeError(
        f"[MELD] Unsupported Existence '{existence}' for registration "
        f"(spell_id={spell_id})."
    )


