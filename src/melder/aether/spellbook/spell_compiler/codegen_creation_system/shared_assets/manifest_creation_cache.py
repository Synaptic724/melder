"""
Shared cross-family manifest cache envelope.

Every manifest-first phase-11 family persists the same package shape:

    {
        "package_version": PACKAGE_VERSION,
        "family_id": <manifest family id>,
        "spell_id": <spell id>,
        "manifest": <marshal-safe family manifest>,
    }

This module owns the envelope: the shared creation-metadata key the families
publish manifests under, package build from that metadata, the package shape
check, and family-dispatched lazy loading. Family modules own their manifest
schema and hydration; this module only routes.

Contract:
    - `build_package(spell)` is family-agnostic: it exports whatever manifest
      the producing family stored on the creation artifact.
    - `load_creation_context_lazy(...)` dispatches on `family_id` with an
      explicit branch per supported family. Unknown families raise, so cache
      payloads from newer/unknown builds degrade to a cold-load skip in the
      conjure orchestration's best-effort loop.
"""

from typing import Any, Dict

MANIFEST_METADATA_KEY = "codegen_creation_manifest"
PACKAGE_VERSION = 2

GENERALIZED_FAMILY_ID = "generalized_codegen_creation"
SOLO_FAMILY_ID = "solo_codegen_creation"
MANY_ONLY_FAMILY_ID = "many_only_codegen_creation"


def build_package(spell: Any) -> Dict[str, Any]:
    """
    Build the marshal-safe cache package for one manifest-first spell.

    Raises:
        RuntimeError:
            When phase-11 output or the family manifest is missing.
    """
    artifact = spell._compiler_artifact
    if artifact is None:
        raise RuntimeError("cache export requires a compiler artifact.")
    spell_codegen_creation = artifact._spell_codegen_creation
    if spell_codegen_creation is None:
        raise RuntimeError("cache export requires spell_codegen_creation.")
    manifest = spell_codegen_creation.metadata.get(MANIFEST_METADATA_KEY)
    if manifest is None:
        raise RuntimeError(
            "cache export requires a manifest; the spell's phase-11 output "
            "was not produced by a manifest-first family."
        )
    if not isinstance(manifest, dict):
        raise RuntimeError("manifest must be a dict.")
    family_id = manifest.get("family_id")
    if not isinstance(family_id, str) or not family_id:
        raise RuntimeError("manifest is missing a family_id.")
    return {
        "package_version": PACKAGE_VERSION,
        "family_id": family_id,
        "spell_id": spell.spell_id,
        "manifest": manifest,
    }


def is_manifest_package(package: Any) -> bool:
    """
    Return whether one decoded cache payload is a manifest-first package.

    Contract:
        - Pure shape check; never raises on foreign payload shapes.
    """
    return (
        isinstance(package, dict)
        and package.get("package_version") == PACKAGE_VERSION
        and isinstance(package.get("family_id"), str)
        and isinstance(package.get("manifest"), dict)
    )


def load_creation_context_lazy(
        spell: Any,
        package: Dict[str, Any],
        *,
        publish: bool = True,
) -> Any:
    """
    Publish one lazy `CreationContext` from a manifest-first package.

    Contract:
        - Dispatches on the package's `family_id` to the owning family's lazy
          loader. Imports are local to keep family modules decoupled from this
          envelope at import time.

    Raises:
        RuntimeError:
            When the family is unknown or the family loader rejects the
            package.
    """
    family_id = package.get("family_id")
    if family_id == GENERALIZED_FAMILY_ID:
        from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.generalized_creation_cache import (
            load_creation_context_lazy as load_generalized_lazy,
        )
        return load_generalized_lazy(spell, package, publish=publish)
    if family_id == SOLO_FAMILY_ID:
        from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.solo_creation_cache import (
            load_creation_context_lazy as load_solo_lazy,
        )
        return load_solo_lazy(spell, package, publish=publish)
    if family_id == MANY_ONLY_FAMILY_ID:
        from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.many_only_creation_cache import (
            load_creation_context_lazy as load_many_only_lazy,
        )
        return load_many_only_lazy(spell, package, publish=publish)
    raise RuntimeError(
        f"Unknown manifest family '{family_id}' in cache package."
    )
