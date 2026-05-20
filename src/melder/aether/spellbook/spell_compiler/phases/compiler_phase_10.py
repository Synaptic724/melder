from typing import Optional, Tuple

from mypy_extensions import mypyc_attr

from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.aether.spellbook.spell_compiler.blueprints.patch_maps import (
    PatchMapBuilder,
)
from melder.utilities.interfaces.irootresolutionblueprint import IRootResolutionBlueprint
from melder.utilities.interfaces.ispell import ISpell


@mypyc_attr(native_class=True)
class CompilerPhase10:
    """
    Compiler phase 10 surface.

    Purpose:
        Expose the current patch-map build behavior through a compiler-owned
        phase class.

    Contract:
        - Slot-only phase surface with no explicit `__init__`.
        - Directly ports the canonical `SpellCrafter` phase-10 behavior.
        - Does not own spell, artifact, or runtime collaborator lifecycle.
    """

    __slots__ = ()

    def _get_required_root_blueprint_phase5(
            self,
            artifact: SpellCompilerArtifact,
    ) -> IRootResolutionBlueprint:
        """
        Return the Phase 5 root blueprint or raise.

        Returns:
            IRootResolutionBlueprint: Attached Phase 5 root blueprint.
        """
        root_blueprint = artifact._root_blueprint_phase5
        if root_blueprint is None:
            raise RuntimeError("SpellCrafter Phase 5 root blueprint is required.")
        return root_blueprint

    def _build_phase10_patch_maps_input_signature(
            self,
            root_blueprint: Optional[IRootResolutionBlueprint],
    ) -> Optional[Tuple[object, ...]]:
        """
        Build a deterministic phase10 input signature for patch-map reuse.

        Purpose:
            Detect whether phase10 patch-map inputs changed so warm runs can
            safely skip redundant patch-map rebuilds.
        Contract:
            - Returns None when blueprint input is unavailable.
            - Includes only lightweight blueprint identity/shape fields.
        Args:
            root_blueprint:
                Phase5 root blueprint used as patch-map source.
        Returns:
            Optional[Tuple[object, ...]]:
                Deterministic signature tuple or None when unavailable.
        """
        if root_blueprint is None:
            return None
        path_registry_identity = None
        socket_ref_count = 0
        ordered_node_count = 0
        try:
            path_registry_identity = id(root_blueprint.path_registry)
            socket_ref_count = len(root_blueprint.socket_refs or ())
            ordered_node_count = len(root_blueprint.ordered_node_ids or ())
        except Exception:
            return None
        return (
            root_blueprint.root_spell_id,
            path_registry_identity,
            socket_ref_count,
            ordered_node_count,
        )

    def _mark_phase8_11_codegen_ir_dirty(
            self,
            artifact: SpellCompilerArtifact,
    ) -> None:
        """
        Mark phase8_11 codegen export as stale.

        Purpose:
            Record that one or more Phase8-11 artifacts are changed and a new IR
            export is required before consumers read phase8_11 payloads.
        Contract:
            - Idempotent; repeated calls keep the dirty state true.
            - Does not mutate codegen payloads directly.
        Returns:
            None.
        """
        artifact._phase8_11_codegen_ir_dirty = True

    def run(
            self,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
    ) -> None:
        # ------------------------------------------------------------------
        # Phase 10 - Patch Maps
        # ------------------------------------------------------------------
        """
        Phase 10 - Patch map compilation.

        Compiles override and mutation patch maps for spells using
        Phase-5 blueprints. Existing-creation spells are treated as a no-op.

        Purpose:
            Precompute override and mutation targeting so meld can apply
            TargetSpec overrides without scanning the blueprint every call.

        Contract:
            - Requires Phase 5 artifacts to be available.
            - Builds maps only when a blueprint is attached for this spell.
            - Replaces any existing patch maps for this spell.
            - Does not mutate the root blueprint.

        Args:
            spell:
                Spell currently in phase execution.
            artifact:
                Spell compiler artifact that owns this phase state.
        Returns:
            None.

        Raises:
            RuntimeError:
                If Phase 5 artifacts are missing or the root blueprint is
                missing for this spell.
        """
        artifact.check_cleaned()
        if spell.is_existing_creation:
            return

        root_blueprint = self._get_required_root_blueprint_phase5(artifact)
        patch_maps_input_signature = self._build_phase10_patch_maps_input_signature(
            root_blueprint,
        )
        if (
                patch_maps_input_signature is not None
                and patch_maps_input_signature == artifact._phase10_patch_maps_input_signature
                and artifact._override_patch_map_phase10 is not None
                and artifact._mutation_patch_map_phase10 is not None
        ):
            return

        builder = PatchMapBuilder(
            blueprint=root_blueprint,
        )
        try:
            override_patch_map = builder.build_override_patch_map()
            mutation_patch_map = builder.build_mutation_patch_map()
        finally:
            builder.cleanup()

        # Hot-swap patch maps without cleaning previous objects in-place.
        # Concurrent runners may still be reading the prior maps.
        artifact._override_patch_map_phase10 = override_patch_map
        artifact._mutation_patch_map_phase10 = mutation_patch_map
        artifact._phase10_patch_maps_input_signature = patch_maps_input_signature
        self._mark_phase8_11_codegen_ir_dirty(artifact)
