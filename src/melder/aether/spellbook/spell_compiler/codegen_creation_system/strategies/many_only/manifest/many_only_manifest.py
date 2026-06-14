"""
Manifest builder for the many_only codegen-creation family.

The manifest captures both runtime lanes as pure data: the no-overrides lane
as the exact Codegen IR payload the many_only compiler's public
`codegen_ir` entrypoint consumes (steps rows + unrolled transient schema),
and the overrides lane as the row/targeting/signature inputs the many_only
override runtime rebuilds from at first meld.

Contract:
    - Manifest values are primitives, tuples, and dicts only.
    - Published under the shared `MANIFEST_METADATA_KEY` so the cross-family
      cache envelope exports it without family-specific wiring.

Bridging note:
    The unrolled-schema builder and the lane signature builders are bridged
    from the many_only compilers/steps; they are pure functions of plan data.
    Lift them into family-public seams when the legacy eager steps are
    retired.
"""

from typing import Any, Dict, Tuple

from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.manifest_creation_cache import (
    MANIFEST_METADATA_KEY,
    MANY_ONLY_FAMILY_ID,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.data.spell_generalized_codegen_lane_plan import (
    SpellGeneralizedCodegenPlanTargetKind,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.compilers.many_only_no_overrides_codegen_creation_compiler import (
    _build_many_only_unrolled_schema_from_plan as build_many_only_unrolled_schema_from_plan,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.many_only_codegen_creation_helpers import (
    ManyOnlyCodegenCreationHelpers,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.steps.many_only_finalize_creation_context_step import (
    ManyOnlyFinalizeCreationContextStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.steps.many_only_no_overrides_codegen_creation_step import (
    ManyOnlyNoOverridesCodegenCreationStep,
)

MANIFEST_VERSION = 3
FAMILY_ID = MANY_ONLY_FAMILY_ID


def build_many_only_manifest(
        *,
        spell_codegen_model: Any,
        spell_codegen_plan: Any,
) -> Dict[str, Any]:
    """
    Build one marshal-safe many_only manifest from model and plan truth.

    Raises:
        RuntimeError:
            When required lane plans or the targeting shape are missing.
    """
    no_overrides_plan = spell_codegen_plan.no_overrides_plan
    if no_overrides_plan is None:
        raise RuntimeError(
            "many_only manifest requires a no_overrides_plan."
        )
    overrides_plan = spell_codegen_plan.overrides_plan
    if overrides_plan is None:
        raise RuntimeError(
            "many_only manifest requires an overrides_plan."
        )
    override_targeting_shape = spell_codegen_model.override_targeting_shape
    if override_targeting_shape is None:
        raise RuntimeError(
            "many_only manifest requires override_targeting_shape."
        )

    steps = tuple(no_overrides_plan.steps)
    steps_rows = tuple(
        _build_many_only_no_overrides_row(step)
        for step in steps
    )
    transient_schema = build_many_only_unrolled_schema_from_plan(
        no_overrides_plan
    )
    root_instance_key = no_overrides_plan.root_instance_key
    if root_instance_key is not None:
        root_instance_key = (root_instance_key[0], root_instance_key[1])

    override_steps = tuple(overrides_plan.steps)
    plan_rows = tuple(
        ManyOnlyCodegenCreationHelpers.build_override_step_row(step)
        for step in override_steps
    )
    plan_signature = (
        ManyOnlyFinalizeCreationContextStep._build_override_plan_signature(
            overrides_plan=overrides_plan,
            plan_rows=plan_rows,
        )
    )

    return {
        "manifest_version": MANIFEST_VERSION,
        "family_id": FAMILY_ID,
        "route_key": _resolve_route_key_from_model(spell_codegen_model),
        "root_spell_id": no_overrides_plan.root_spell_id,
        "no_overrides": {
            "lane_id": no_overrides_plan.lane_id,
            "root_spell_id": no_overrides_plan.root_spell_id,
            "root_instance_key": root_instance_key,
            "step_spell_ids": tuple(
                step.spell.spell_index.current
                for step in steps
            ),
            "steps_rows": steps_rows,
            "transient_schema": transient_schema,
            "executor_signature": (
                ManyOnlyNoOverridesCodegenCreationStep._build_executor_signature(
                    no_overrides_plan=no_overrides_plan,
                )
            ),
        },
        "overrides": {
            "lane_id": overrides_plan.lane_id,
            "root_spell_id": overrides_plan.root_spell_id,
            "step_spell_ids": tuple(
                step.spell.spell_index.current
                for step in override_steps
            ),
            "plan_rows": plan_rows,
            "plan_signature": plan_signature,
            "empty_shape_key": (plan_signature, (), -1),
            "targets_by_spec": serialize_targets_by_spec(
                override_targeting_shape.targets_by_spec,
            ),
            "specificity_by_spec": dict(
                override_targeting_shape.specificity_by_spec
            ),
        },
    }


def _build_many_only_no_overrides_row(step: Any) -> Dict[str, Any]:
    """
    Build one schema-only no-overrides row from a many_only plan step.

    Contract:
        - Emits exactly the field set the many_only compiler's Codegen IR
          row hydration requires. `ManyOnlyCodegenPlanStep` carries no
          existence or lock-hint fields by design, so the two routing fields
          are family invariants: every step resolves into the CALLER store
          (the whole graph is `many`) and lock hints never apply to
          non-reusing steps (`use_spell_lock_hint` is False).
        - The shared generalized row builder is NOT usable here: it reads
          `step.existence`, which many_only steps do not expose.
    """
    contract_payload_items: Tuple[Any, ...] = ()
    if step.contract_payload:
        contract_payload_items = tuple(
            sorted(
                (
                    param_name,
                    ManyOnlyCodegenCreationHelpers.freeze_value(value),
                )
                for param_name, value in step.contract_payload.items()
            )
        )
    return {
        "instance_key": tuple(step.instance_key),
        "spell_id": step.spell.spell_index.current,
        "creations_target_kind": (
            SpellGeneralizedCodegenPlanTargetKind.CALLER
        ),
        "dependency_resolution_order": tuple(
            (
                param_name,
                tuple(dependency_keys),
            )
            for param_name, dependency_keys in step.dependency_resolution_order
        ),
        "uses_positional_override": bool(step.uses_positional_override),
        "contract_positional_override": (
            ManyOnlyCodegenCreationHelpers.freeze_value(
                step.contract_positional_override
            )
        ),
        "has_contract_payload": bool(step.has_contract_payload),
        "contract_payload_items": contract_payload_items,
        "use_spell_lock_hint": False,
    }


def _resolve_route_key_from_model(spell_codegen_model: Any) -> str:
    """
    Resolve the runtime route key from processor-owned model truth.
    """
    if spell_codegen_model.build_kind == "existing_creation":
        return "existing_creation"
    route_family = spell_codegen_model.route_family
    if route_family in (
            "spellspace",
            "unique_per_conduit",
            "many",
            "shared",
            "lineage",
    ):
        return route_family
    raise RuntimeError(
        "SpellCodegenModel route_family is not ready for many_only "
        f"manifest build: {route_family!r}."
    )


def serialize_targets_by_spec(
        targets_by_spec: Dict[str, Tuple[Any, ...]],
) -> Dict[str, Tuple[Tuple[Any, ...], ...]]:
    """
    Serialize processor override-target rows to marshal-safe tuples.
    """
    return {
        spec_key: tuple(
            (
                target_ref.node_id,
                target_ref.param_path_id,
                target_ref.param_name,
                target_ref.socket_kind_value,
            )
            for target_ref in target_refs
        )
        for spec_key, target_refs in targets_by_spec.items()
    }


def validate_many_only_manifest(manifest: Any) -> Dict[str, Any]:
    """
    Validate one many_only manifest mapping and return it.
    """
    if not isinstance(manifest, dict):
        raise RuntimeError("many_only manifest must be a dict.")
    if manifest.get("manifest_version") != MANIFEST_VERSION:
        raise RuntimeError(
            "many_only manifest version mismatch: "
            f"{manifest.get('manifest_version')!r} != {MANIFEST_VERSION}."
        )
    if manifest.get("family_id") != FAMILY_ID:
        raise RuntimeError(
            f"many_only manifest family mismatch: {manifest.get('family_id')!r}."
        )
    for required_field in (
            "route_key",
            "root_spell_id",
            "no_overrides",
            "overrides",
    ):
        if required_field not in manifest:
            raise RuntimeError(
                "many_only manifest is missing required field "
                f"'{required_field}'."
            )
    return manifest


def coerce_manifest_sequences(value: Any) -> Any:
    """
    Recursively coerce decoded sequences back into tuples.
    """
    if isinstance(value, (list, tuple)):
        return tuple(coerce_manifest_sequences(item) for item in value)
    return value


__all__ = [
    "FAMILY_ID",
    "MANIFEST_METADATA_KEY",
    "MANIFEST_VERSION",
    "build_many_only_manifest",
    "coerce_manifest_sequences",
    "serialize_targets_by_spec",
    "validate_many_only_manifest",
]
