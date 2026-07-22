from typing import Dict, Optional, Tuple

from melder.utilities.general_base.cleanable import Cleanable


class SpellOverrideTargetRef:
    """
    Processor-owned override target row.

    Purpose:
        Hold one normalized override-target socket identity without keeping a
        raw `SocketRef` object in the fitted model.
    """

    __slots__ = [
        "node_id",
        "param_path_id",
        "param_name",
        "socket_kind_value",
    ]

    def __init__(
            self,
            *,
            node_id: str,
            param_path_id: int,
            param_name: str,
            socket_kind_value: int,
    ) -> None:
        """
        Build one normalized override target row.

        Args:
            node_id:
                Blueprint node id the override targets.
            param_path_id:
                Parameter path id within the node.
            param_name:
                Parameter name at that path.
            socket_kind_value:
                Integer socket-kind discriminator (the normalized SocketRef
                kind, kept as a value rather than the raw object).

        Returns:
            None.
        """
        self.node_id = node_id
        self.param_path_id = param_path_id
        self.param_name = param_name
        self.socket_kind_value = socket_kind_value


class SpellOverrideTargetingAnalysis(Cleanable):
    """
    Processor-owned override-targeting section.

    Purpose:
        Hold the normalized override-targeting truth derived from the rooted
        blueprint without retaining the old `OverridePatchMap` object.
    """

    __slots__ = Cleanable.__slots__ + [
        "targets_by_spec",
        "specificity_by_spec",
        "target_spec_count",
        "targeted_socket_count",
        "targeted_spell_count",
        "max_targets_per_spec",
        "single_target_spec_count",
        "multi_target_spec_count",
        "path_depth_histogram",
        "max_target_path_depth",
    ]

    def __init__(
            self,
            *,
            targets_by_spec: Dict[str, Tuple[SpellOverrideTargetRef, ...]],
            specificity_by_spec: Dict[str, int],
            path_depth_histogram: Tuple[Tuple[int, int], ...],
    ) -> None:
        """
        Build one override-targeting section.

        Contract:
            Stores the three inputs by reference and derives the summary stats
            in one pass over `targets_by_spec`: spec count, distinct targeted
            socket and spell counts, max/single/multi targets-per-spec, and
            (from the histogram) the max target path depth.

        Args:
            targets_by_spec:
                Per-spec tuple of `SpellOverrideTargetRef` rows.
            specificity_by_spec:
                Per-spec integer specificity score.
            path_depth_histogram:
                (path_depth, count) pairs over the targeting paths.

        Returns:
            None.
        """
        super().__init__()
        self.targets_by_spec = targets_by_spec
        self.specificity_by_spec = specificity_by_spec
        self.target_spec_count = len(targets_by_spec)

        target_rows = []
        target_spell_ids = set()
        max_targets_per_spec = 0
        single_target_spec_count = 0
        multi_target_spec_count = 0
        for targets in targets_by_spec.values():
            target_count = len(targets)
            if target_count > max_targets_per_spec:
                max_targets_per_spec = target_count
            if target_count == 1:
                single_target_spec_count += 1
            elif target_count > 1:
                multi_target_spec_count += 1
            for target in targets:
                target_rows.append(
                    (
                        target.node_id,
                        target.param_path_id,
                        target.param_name,
                        target.socket_kind_value,
                    )
                )
                target_spell_ids.add(target.node_id)

        self.targeted_socket_count = len(set(target_rows))
        self.targeted_spell_count = len(target_spell_ids)
        self.max_targets_per_spec = max_targets_per_spec
        self.single_target_spec_count = single_target_spec_count
        self.multi_target_spec_count = multi_target_spec_count
        self.path_depth_histogram = path_depth_histogram
        self.max_target_path_depth = max(
            (depth for depth, _ in path_depth_histogram),
            default=0,
        )

    def cleanup(self) -> None:
        """
        Deterministically release owned override-targeting data.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self.targets_by_spec.clear()
        self.specificity_by_spec.clear()

        del self.targets_by_spec
        del self.specificity_by_spec
        del self.target_spec_count
        del self.targeted_socket_count
        del self.targeted_spell_count
        del self.max_targets_per_spec
        del self.single_target_spec_count
        del self.multi_target_spec_count
        del self.path_depth_histogram
        del self.max_target_path_depth
