"""
Manifest builder for the solo codegen-creation family.

The solo manifest is deliberately tiny: the solo compilers consume only the
live root spell plus three scalar facts (route key, solo emit key, fast
transient flag), so the manifest is those facts plus lane provenance. One
spell-id resolution at hydration is the only live work a cache load defers.

Contract:
    - Manifest values are primitives only.
    - Published under the shared `MANIFEST_METADATA_KEY` so the cross-family
      cache envelope exports it without family-specific wiring.
"""

from typing import Any, Dict

from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.manifest_creation_cache import (
    MANIFEST_METADATA_KEY,
    SOLO_FAMILY_ID,
)

MANIFEST_VERSION = 2
FAMILY_ID = SOLO_FAMILY_ID

_VALID_ROUTE_KEYS = (
    "existing_creation",
    "spellspace",
    "unique_per_conduit",
    "many",
    "shared",
)


def build_solo_manifest(
        *,
        spell_codegen_model: Any,
        spell_codegen_plan: Any,
) -> Dict[str, Any]:
    """
    Build one marshal-safe solo manifest from model and plan truth.

    Contract:
        - Mirrors the legacy solo setup-step fact resolution exactly:
          root spell id from graph shape (runtime-shape fallback), route key
          from build kind/route family, solo emit key from the runtime
          record's existence, fast-transient from emit key plus disposal.

    Raises:
        RuntimeError:
            When required model/plan truth is missing.
    """
    spell_runtime_shape = spell_codegen_model.spell_runtime_shape
    if spell_runtime_shape is None:
        raise RuntimeError("solo manifest requires spell_runtime_shape.")
    no_overrides_plan = spell_codegen_plan.no_overrides_plan
    if no_overrides_plan is None:
        raise RuntimeError("solo manifest requires a no_overrides_plan.")
    overrides_plan = spell_codegen_plan.overrides_plan
    if overrides_plan is None:
        raise RuntimeError("solo manifest requires an overrides_plan.")

    root_spell_id = _resolve_root_spell_id(spell_codegen_model)
    runtime_record = spell_runtime_shape.records_by_spell_id[root_spell_id]
    route_key = _resolve_route_key(spell_codegen_model)
    solo_emit_key = _resolve_solo_emit_key(
        spell_codegen_model=spell_codegen_model,
        runtime_record=runtime_record,
    )
    fast_transient_no_overrides_enabled = (
        solo_emit_key == "many"
        and not runtime_record.has_disposal_methods
    )

    return {
        "manifest_version": MANIFEST_VERSION,
        "family_id": FAMILY_ID,
        "root_spell_id": root_spell_id,
        "route_key": route_key,
        "solo_emit_key": solo_emit_key,
        "fast_transient_no_overrides_enabled": (
            fast_transient_no_overrides_enabled
        ),
        "no_overrides_lane_id": no_overrides_plan.lane_id,
        "override_lane_id": overrides_plan.lane_id,
    }


def _resolve_root_spell_id(spell_codegen_model: Any) -> str:
    """
    Resolve the root spell id for the solo family.
    """
    graph_shape = spell_codegen_model.graph_shape
    if graph_shape is not None:
        return graph_shape.root_spell_id
    return next(
        iter(spell_codegen_model.spell_runtime_shape.records_by_spell_id.keys())
    )


def _resolve_route_key(spell_codegen_model: Any) -> str:
    """
    Resolve the creation-context route key from model truth.
    """
    if spell_codegen_model.build_kind == "existing_creation":
        return "existing_creation"
    return spell_codegen_model.route_family


def _resolve_solo_emit_key(
        *,
        spell_codegen_model: Any,
        runtime_record: Any,
) -> str:
    """
    Resolve the exact solo emit key from root-only model truth.

    Contract:
        - Mirrors the legacy solo setup step, including its tolerant record /
          spell existence fallbacks for polymorphic runtime records.
    """
    if spell_codegen_model.build_kind == "existing_creation":
        return "existing_creation"
    record_existence = getattr(runtime_record, "existence", None)
    if record_existence is not None:
        return record_existence.name
    spell_existence = getattr(runtime_record.spell, "existence", None)
    if spell_existence is not None:
        return spell_existence.name
    return spell_codegen_model.route_family


def validate_solo_manifest(manifest: Any) -> Dict[str, Any]:
    """
    Validate one solo manifest mapping and return it.
    """
    if not isinstance(manifest, dict):
        raise RuntimeError("solo manifest must be a dict.")
    if manifest.get("manifest_version") != MANIFEST_VERSION:
        raise RuntimeError(
            "solo manifest version mismatch: "
            f"{manifest.get('manifest_version')!r} != {MANIFEST_VERSION}."
        )
    if manifest.get("family_id") != FAMILY_ID:
        raise RuntimeError(
            f"solo manifest family mismatch: {manifest.get('family_id')!r}."
        )
    for required_field in (
            "root_spell_id",
            "route_key",
            "solo_emit_key",
            "fast_transient_no_overrides_enabled",
            "no_overrides_lane_id",
            "override_lane_id",
    ):
        if required_field not in manifest:
            raise RuntimeError(
                "solo manifest is missing required field "
                f"'{required_field}'."
            )
    return manifest


__all__ = [
    "FAMILY_ID",
    "MANIFEST_METADATA_KEY",
    "MANIFEST_VERSION",
    "build_solo_manifest",
    "validate_solo_manifest",
]
