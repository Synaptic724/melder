"""
Manifest builder for the generalized codegen-creation family.

The manifest is the family's single serialization-shaped truth: one
marshal-safe mapping holding every schema-only fact both runtime lanes need.
The live phase-11 path builds the manifest and publishes lazy doors over it;
the cache path persists the manifest and hydrates it through the same
hydrator at first meld. One assembly program, two callers.

Contract:
    - Manifest values are primitives, tuples, and dicts only. No live spell
      objects, no code objects, no plan/model references.
    - Lane rows extend `CodegenCreationSchemaHelpers.build_phase11_step_ir_row`
      with family row flags (`spell_is_callable`, `spell_is_existing_creation`)
      so source emission never consults live spells.
    - The manifest is stored on `SpellCodegenCreation.metadata` under
      `MANIFEST_METADATA_KEY` for codec export.
"""

from typing import Any, Dict, Optional, Tuple

from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_schema_helpers import (
    CodegenCreationSchemaHelpers,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.manifest_creation_cache import (
    GENERALIZED_FAMILY_ID,
    MANIFEST_METADATA_KEY,
)

# Version 3: rows carry `spell_has_disposal_methods` (bind-time spell truth)
# as the authoritative emit-time disposal fact. Version-2 manifests are
# rejected by validation and regenerate as cold cache.
MANIFEST_VERSION = 3
FAMILY_ID = GENERALIZED_FAMILY_ID


def build_generalized_manifest(
        *,
        spell_codegen_model: Any,
        spell_codegen_plan: Any,
) -> Dict[str, Any]:
    """
    Build one marshal-safe manifest from phase-9 model and phase-10 plan truth.

    Raises:
        RuntimeError:
            When a required lane plan or targeting shape is missing.
    """
    no_overrides_plan = spell_codegen_plan.no_overrides_plan
    if no_overrides_plan is None:
        raise RuntimeError(
            "generalized manifest requires a no_overrides_plan."
        )
    overrides_plan = spell_codegen_plan.overrides_plan
    if overrides_plan is None:
        raise RuntimeError(
            "generalized manifest requires an overrides_plan."
        )
    override_targeting_shape = spell_codegen_model.override_targeting_shape
    if override_targeting_shape is None:
        raise RuntimeError(
            "generalized manifest requires override_targeting_shape."
        )

    return {
        "manifest_version": MANIFEST_VERSION,
        "family_id": FAMILY_ID,
        "route_key": _resolve_route_key_from_model(spell_codegen_model),
        "root_spell_id": no_overrides_plan.root_spell_id,
        "no_overrides": _build_no_overrides_lane_payload(
            no_overrides_plan=no_overrides_plan,
        ),
        "overrides": _build_overrides_lane_payload(
            overrides_plan=overrides_plan,
            override_targeting_shape=override_targeting_shape,
        ),
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
        "SpellCodegenModel route_family is not ready for generalized "
        f"manifest build: {route_family!r}."
    )


def _build_no_overrides_lane_payload(
        *,
        no_overrides_plan: Any,
) -> Dict[str, Any]:
    """
    Build the schema-only no-overrides lane payload.
    """
    steps = tuple(no_overrides_plan.steps)
    steps_rows = tuple(
        _enrich_phase11_row(row, step)
        for row, step in zip(
            CodegenCreationSchemaHelpers.get_phase11_step_ir_rows(
                no_overrides_plan,
                include_override_metadata=False,
            ),
            steps,
        )
    )
    transient_schema = CodegenCreationSchemaHelpers.build_fast_transient_schema(
        no_overrides_plan.fast_transient_plan,
    )
    root_instance_key = no_overrides_plan.root_instance_key
    if root_instance_key is not None:
        root_instance_key = CodegenCreationSchemaHelpers.normalize_instance_key(
            root_instance_key
        )
    return {
        "lane_id": no_overrides_plan.lane_id,
        "root_spell_id": no_overrides_plan.root_spell_id,
        "root_instance_key": root_instance_key,
        "step_spell_ids": tuple(
            step.spell.spell_index.current
            for step in steps
        ),
        "steps_rows": steps_rows,
        "transient_schema": transient_schema,
        "executor_signature": build_no_overrides_executor_signature(
            no_overrides_plan=no_overrides_plan,
            transient_schema=transient_schema,
        ),
    }


def _build_overrides_lane_payload(
        *,
        overrides_plan: Any,
        override_targeting_shape: Any,
) -> Dict[str, Any]:
    """
    Build the schema-only overrides lane payload.
    """
    steps = tuple(overrides_plan.steps)
    plan_rows = tuple(
        _enrich_phase11_row(row, step)
        for row, step in zip(
            CodegenCreationSchemaHelpers.get_phase11_step_ir_rows(
                overrides_plan,
                include_override_metadata=True,
            ),
            steps,
        )
    )
    plan_signature = build_override_plan_signature(
        overrides_plan=overrides_plan,
        plan_rows=plan_rows,
    )
    return {
        "lane_id": overrides_plan.lane_id,
        "root_spell_id": overrides_plan.root_spell_id,
        "step_spell_ids": tuple(
            step.spell.spell_index.current
            for step in steps
        ),
        "plan_rows": plan_rows,
        "plan_signature": plan_signature,
        "empty_shape_key": (plan_signature, (), -1),
        "targets_by_spec": serialize_targets_by_spec(
            override_targeting_shape.targets_by_spec,
        ),
        "specificity_by_spec": dict(override_targeting_shape.specificity_by_spec),
    }


def build_no_overrides_executor_signature(
        *,
        no_overrides_plan: Any,
        transient_schema: Optional[Dict[str, Any]],
) -> str:
    """
    Build the deterministic no-overrides executor signature.

    Contract:
        - Family-owned replacement for the signature builder that previously
          lived on the legacy no-overrides step.
    """
    step_signature_rows = tuple(
        CodegenCreationSchemaHelpers.build_no_overrides_codegen_creation_step_signature_row(
            step
        )
        for step in no_overrides_plan.steps
    )
    if transient_schema is None:
        transient_signature = None
    else:
        transient_signature = (
            CodegenCreationSchemaHelpers.build_fast_transient_signature(
                transient_schema
            )
        )
    root_instance_key = CodegenCreationSchemaHelpers.normalize_instance_key(
        no_overrides_plan.root_instance_key
    )
    return CodegenCreationSchemaHelpers.hash_codegen_signature(
        no_overrides_plan.root_spell_id,
        root_instance_key,
        step_signature_rows,
        transient_signature,
    )


def build_override_plan_signature(
        *,
        overrides_plan: Any,
        plan_rows: Any,
) -> Tuple[Any, ...]:
    """
    Build the stable override plan signature used by specialization caching.

    Contract:
        - Family-owned replacement for the signature builder that previously
          lived on the legacy finalize step.
    """
    steps_rows_signature = CodegenCreationSchemaHelpers.hash_codegen_signature(
        tuple(plan_rows)
    )
    step_spell_ids = tuple(
        step.spell.spell_index.current
        for step in overrides_plan.steps
    )
    return (
        "generalized_overrides_lane_plan",
        CodegenCreationSchemaHelpers.hash_codegen_signature(
            overrides_plan.lane_id,
            overrides_plan.root_spell_id,
            step_spell_ids,
            steps_rows_signature,
        ),
        steps_rows_signature,
    )


def _enrich_phase11_row(
        row: Dict[str, Any],
        step: Any,
) -> Dict[str, Any]:
    """
    Stamp family row flags onto one shared phase-11 row.

    Contract:
        - `spell_is_callable` and `spell_is_existing_creation` let the family
          emitter make the inlinable-common-shape decision from row data
          alone, so source emission never consults live spells.
        - `spell_has_disposal_methods` is the authoritative emit-time disposal
          fact, read from bind-time spell truth (which composes into the spell
          fingerprint alongside existence) rather than trusting plan-step
          plumbing for disposal data.
        - Additive only; shared row fields are never mutated.
    """
    # Copy before stamping: the contract line below ("never mutated") was
    # previously violated by in-place key writes, harmless only because every
    # consumer rebuilt rows from scratch. With plan-level row memoization in
    # the SharedCompilerExecutions lane, in-place stamping of a shared row
    # would poison sibling consumers, so enrichment operates on a copy.
    spell = step.spell
    enriched = dict(row)
    enriched["spell_is_callable"] = bool(
        spell.is_class_spell
        or spell.is_method_spell
        or spell.is_lambda_spell
    )
    enriched["spell_is_existing_creation"] = bool(spell.is_existing_creation)
    enriched["spell_has_disposal_methods"] = bool(spell.has_disposal_methods)
    return enriched


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


def validate_generalized_manifest(manifest: Any) -> Dict[str, Any]:
    """
    Validate one manifest mapping and return it.
    """
    if not isinstance(manifest, dict):
        raise RuntimeError("generalized manifest must be a dict.")
    if manifest.get("manifest_version") != MANIFEST_VERSION:
        raise RuntimeError(
            "generalized manifest version mismatch: "
            f"{manifest.get('manifest_version')!r} != {MANIFEST_VERSION}."
        )
    if manifest.get("family_id") != FAMILY_ID:
        raise RuntimeError(
            "generalized manifest family mismatch: "
            f"{manifest.get('family_id')!r}."
        )
    for required_field in (
            "route_key",
            "root_spell_id",
            "no_overrides",
            "overrides",
    ):
        if required_field not in manifest:
            raise RuntimeError(
                "generalized manifest is missing required field "
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
