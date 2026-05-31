from typing import Dict, Optional, Tuple

from melder.utilities.general_base.cleanable import Cleanable


class SpellMutationPatchRef:
    """
    Processor-owned mutation target row.

    Purpose:
        Hold one normalized mutation-edge patch identity without keeping the raw
        `MutationEdgePatch` object in the fitted model.
    """

    __slots__ = [
        "child_spell_id",
        "param_name",
        "param_path_id",
        "old_parent_id",
    ]

    def __init__(
            self,
            *,
            child_spell_id: str,
            param_name: str,
            param_path_id: int,
            old_parent_id: Optional[str],
    ) -> None:
        """
        Build one normalized mutation patch row.
        """
        self.child_spell_id = child_spell_id
        self.param_name = param_name
        self.param_path_id = param_path_id
        self.old_parent_id = old_parent_id


class SpellMutationTargetingAnalysis(Cleanable):
    """
    Processor-owned mutation-targeting section.

    Purpose:
        Hold the normalized mutation-targeting truth derived from the rooted
        blueprint without retaining the old `MutationPatchMap` object.
    """

    __slots__ = Cleanable.__slots__ + [
        "patches_by_spec",
        "target_spec_count",
        "patch_count",
        "targeted_child_spell_count",
        "max_patches_per_spec",
        "path_depth_histogram",
        "max_target_path_depth",
    ]

    def __init__(
            self,
            *,
            patches_by_spec: Dict[str, Tuple[SpellMutationPatchRef, ...]],
            path_depth_histogram: Tuple[Tuple[int, int], ...],
    ) -> None:
        """
        Build one mutation-targeting section.
        """
        super().__init__()
        self.patches_by_spec = patches_by_spec
        self.target_spec_count = len(patches_by_spec)

        patch_rows = []
        child_spell_ids = set()
        max_patches_per_spec = 0
        for patches in patches_by_spec.values():
            patch_count = len(patches)
            if patch_count > max_patches_per_spec:
                max_patches_per_spec = patch_count
            for patch in patches:
                patch_rows.append(
                    (
                        patch.child_spell_id,
                        patch.param_name,
                        patch.param_path_id,
                        patch.old_parent_id,
                    )
                )
                child_spell_ids.add(patch.child_spell_id)

        self.patch_count = len(set(patch_rows))
        self.targeted_child_spell_count = len(child_spell_ids)
        self.max_patches_per_spec = max_patches_per_spec
        self.path_depth_histogram = path_depth_histogram
        self.max_target_path_depth = max(
            (depth for depth, _ in path_depth_histogram),
            default=0,
        )

    def cleanup(self) -> None:
        """
        Deterministically release owned mutation-targeting data.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self.patches_by_spec.clear()

        del self.patches_by_spec
        del self.target_spec_count
        del self.patch_count
        del self.targeted_child_spell_count
        del self.max_patches_per_spec
        del self.path_depth_histogram
        del self.max_target_path_depth
