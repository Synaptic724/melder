from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, List, Optional, Tuple

from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_override_targeting_analysis import (
    SpellOverrideTargetRef,
)
from melder.aether.spellbook.spell_compiler.dag.target_spec import (
    TargetSpec,
    TargetSpecKind,
)
from melder.utilities.general_base.cleanable import Cleanable


class _Specificity(IntEnum):
    """
    Specificity ranking for override target matches.

    Purpose:
        Preserve the same conflict-resolution ordering currently used by the
        old Phase 10 override patch map:
        PATH > UNIQUE > BROADCAST.
    """

    PATH = 3
    UNIQUE = 2
    BROADCAST = 1


@dataclass(frozen=True, slots=True)
class SpellOverrideTargetSocketRef:
    """
    Compiler-owned override target socket row.

    Purpose:
        Replace the old runtime `SocketRef` dependency with one hashable row
        that still exposes the socket identity data required by the override
        runtime.
    """

    node_id: str
    param_path_id: int
    param_name: str
    socket_kind_value: int


class SpellOverrideTargetingCodegenCreation(Cleanable):
    """
    Compiler-owned override targeting artifact.

    Purpose:
        Replace the old `OverridePatchMap` runtime dependency with a new
        compiler-owned override-targeting surface built from processor targeting
        truth.

    Contract:
        - Owns `targets_by_spec` and `specificity_by_spec`.
        - Supports the same apply/apply_with_socket_shape semantics the old
          runtime expected.
        - Produces deterministic socket-shape rows for override specialization.
    """

    __slots__ = Cleanable.__slots__ + [
        "_root_spell_id",
        "_targets_by_spec",
        "_specificity_by_spec",
        "_resolved_targets_by_raw_key",
        "_last_single_cache",
        "_last_multi_cache",
    ]

    def __init__(
            self,
            *,
            root_spell_id: str,
            targets_by_spec: Dict[str, Tuple[SpellOverrideTargetSocketRef, ...]],
            specificity_by_spec: Dict[str, int],
    ) -> None:
        """
        Build one override-targeting creation artifact.

        Contract:
            Validates a non-empty root spell id, stores `targets_by_spec` by
            reference, and converts each `specificity_by_spec` value into a
            `_Specificity` enum (PATH > UNIQUE > BROADCAST) for conflict
            ordering. Initializes the raw-key resolution memo and the two
            last-entry apply caches (single/multi), which each publish as one
            atomic tuple snapshot to stay torn-read-safe on 3.14t.

        Args:
            root_spell_id:
                Root spell this override surface belongs to; must be non-empty.
            targets_by_spec:
                Per-spec tuple of target socket rows.
            specificity_by_spec:
                Per-spec integer specificity, coerced to `_Specificity`.

        Raises:
            ValueError: If `root_spell_id` is empty.

        Returns:
            None.
        """
        super().__init__()
        if not root_spell_id:
            raise ValueError("root_spell_id must not be empty.")
        self._root_spell_id = root_spell_id
        self._targets_by_spec = targets_by_spec
        self._specificity_by_spec = {
            key: _Specificity(value)
            for key, value in specificity_by_spec.items()
        }
        self._resolved_targets_by_raw_key: Dict[
            str,
            tuple[
                tuple[SpellOverrideTargetSocketRef, ...],
                _Specificity,
                tuple[tuple[object, ...], ...],
            ],
        ] = {}
        # Last-entry caches publish as ONE immutable tuple snapshot per
        # slot (torn-publication fix, 2026-07-12): this runtime is shared
        # by every thread melding the same compiled root, and per-field
        # publication let interleaved writers assemble a cache entry that
        # never existed in any real meld (key_B/value_B paired with
        # map_A/shape_A). A single reference store is atomic on 3.14t;
        # readers load the snapshot once and unpack.
        self._last_single_cache: Optional[
            tuple[
                str,
                object,
                Dict[SpellOverrideTargetSocketRef, object],
                tuple[tuple[object, ...], ...],
            ]
        ] = None
        self._last_multi_cache: Optional[
            tuple[
                tuple[tuple[str, int], ...],
                Dict[SpellOverrideTargetSocketRef, object],
                tuple[tuple[object, ...], ...],
            ]
        ] = None

    @classmethod
    def from_analysis(
            cls,
            *,
            root_spell_id: str,
            targets_by_spec: Dict[str, Tuple[SpellOverrideTargetRef, ...]],
            specificity_by_spec: Dict[str, int],
    ) -> "SpellOverrideTargetingCodegenCreation":
        """
        Build the artifact from processor-owned override targeting analysis.

        Contract:
            Normalizes each processor `SpellOverrideTargetRef` into a
            compiler-owned, hashable `SpellOverrideTargetSocketRef` (dropping the
            runtime SocketRef dependency), preserving per-spec grouping, then
            delegates to `__init__`.

        Args:
            root_spell_id:
                Root spell this override surface belongs to.
            targets_by_spec:
                Per-spec tuple of processor `SpellOverrideTargetRef` rows.
            specificity_by_spec:
                Per-spec integer specificity.

        Returns:
            SpellOverrideTargetingCodegenCreation: The compiler-owned artifact.
        """
        normalized_targets_by_spec: Dict[
            str,
            Tuple[SpellOverrideTargetSocketRef, ...],
        ] = {}
        for spec_key, target_refs in targets_by_spec.items():
            normalized_targets_by_spec[spec_key] = tuple(
                SpellOverrideTargetSocketRef(
                    node_id=target_ref.node_id,
                    param_path_id=target_ref.param_path_id,
                    param_name=target_ref.param_name,
                    socket_kind_value=target_ref.socket_kind_value,
                )
                for target_ref in target_refs
            )
        return cls(
            root_spell_id=root_spell_id,
            targets_by_spec=normalized_targets_by_spec,
            specificity_by_spec=specificity_by_spec,
        )

    def cleanup(self) -> None:
        """
        Deterministically release the override targeting artifact.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._targets_by_spec.clear()
        self._specificity_by_spec.clear()
        self._resolved_targets_by_raw_key.clear()

        del self._root_spell_id
        del self._targets_by_spec
        del self._specificity_by_spec
        del self._resolved_targets_by_raw_key
        del self._last_single_cache
        del self._last_multi_cache

    def _apply_with_socket_shape_prechecked(
            self,
            *,
            spell_override: Dict[str, object],
    ) -> tuple[
        Dict[SpellOverrideTargetSocketRef, object],
        tuple[tuple[object, ...], ...],
    ]:
        """
        Internal hot-path entry for socket-shape override application.
        """
        if spell_override is None or not spell_override:
            return {}, ()
        if len(spell_override) == 1:
            raw_key = next(iter(spell_override))
            value = spell_override[raw_key]
            # One-load snapshot read (torn-publication fix): the whole
            # cache entry travels as one tuple, so a hit can never pair
            # this call's key/value with another call's map/shape.
            single_snapshot = self._last_single_cache
            if single_snapshot is not None:
                cached_key, cached_value, cached_map, cached_shape = (
                    single_snapshot
                )
                if raw_key == cached_key and value is cached_value:
                    return cached_map, cached_shape
            matches, _, socket_shape = self._resolve_targets_for_raw_key(raw_key)
            if len(matches) == 1:
                override_map = {matches[0]: value}
            else:
                override_map = {
                    socket_ref: value
                    for socket_ref in matches
                }
            # One-store snapshot publication (atomic reference swap).
            self._last_single_cache = (
                raw_key,
                value,
                override_map,
                socket_shape,
            )
            return override_map, socket_shape

        multi_signature: Optional[tuple[tuple[str, int], ...]] = None
        if len(spell_override) <= 4:
            multi_signature = tuple(
                sorted(
                    (
                        raw_key,
                        id(value),
                    )
                    for raw_key, value in spell_override.items()
                )
            )
            # One-load snapshot read (torn-publication fix, multi lane).
            multi_snapshot = self._last_multi_cache
            if multi_snapshot is not None:
                cached_signature, cached_map, cached_shape = multi_snapshot
                if multi_signature == cached_signature:
                    return cached_map, cached_shape

        per_socket: Dict[
            SpellOverrideTargetSocketRef,
            tuple[_Specificity, object],
        ] = {}
        for raw_key, value in spell_override.items():
            matches, level, _ = self._resolve_targets_for_raw_key(raw_key)
            for socket_ref in matches:
                existing = per_socket.get(socket_ref)
                if existing is None:
                    per_socket[socket_ref] = (level, value)
                    continue
                existing_level, existing_value = existing
                if level > existing_level:
                    per_socket[socket_ref] = (level, value)
                elif level == existing_level and existing_value != value:
                    raise RuntimeError(
                        f"Conflicting overrides for socket {socket_ref}: multiple rules "
                        "with the same specificity."
                    )

        override_map = {
            socket: value
            for socket, (_, value) in per_socket.items()
        }
        socket_shape = self._build_socket_shape_from_matches(
            matches=tuple(override_map),
        )
        if multi_signature is not None:
            # One-store snapshot publication (atomic reference swap).
            self._last_multi_cache = (
                multi_signature,
                override_map,
                socket_shape,
            )
        return override_map, socket_shape

    def _resolve_targets_for_raw_key(
            self,
            raw_key: str,
    ) -> tuple[
        tuple[SpellOverrideTargetSocketRef, ...],
        _Specificity,
        tuple[tuple[object, ...], ...],
    ]:
        """
        Resolve one raw override key to target sockets and specificity rank.
        """
        cached = self._resolved_targets_by_raw_key.get(raw_key)
        if cached is not None:
            return cached

        spec = TargetSpec.parse(raw_key)
        spec_key = self._spec_key(spec)
        matches = self._targets_by_spec.get(spec_key)
        if spec.kind is TargetSpecKind.PATH:
            if not matches:
                raise RuntimeError(
                    f"No sockets found for override path '{'>'.join(spec.path or ())}'."
                )
        elif spec.kind is TargetSpecKind.UNIQUE:
            count = 0 if not matches else len(matches)
            if count == 0:
                raise RuntimeError(
                    f"No sockets found for unique override '*{spec.param_name}'."
                )
            if count > 1:
                raise RuntimeError(
                    f"Unique override '*{spec.param_name}' matched {count} sockets; "
                    "expected exactly one."
                )
        elif spec.kind is TargetSpecKind.BROADCAST:
            if not matches:
                raise RuntimeError(
                    f"No sockets found for broadcast override '**{spec.param_name}'."
                )
        else:
            raise RuntimeError(f"Unsupported TargetSpecKind: {spec.kind!r}")

        level = self._specificity_by_spec.get(spec_key)
        if level is None:
            raise RuntimeError(
                f"Specificity missing for override key '{raw_key}'."
            )
        resolved_matches = matches or ()
        resolved = (
            resolved_matches,
            level,
            self._build_socket_shape_from_matches(matches=resolved_matches),
        )
        self._resolved_targets_by_raw_key[raw_key] = resolved
        return resolved

    @staticmethod
    def _build_socket_shape_from_matches(
            *,
            matches: tuple[SpellOverrideTargetSocketRef, ...],
    ) -> tuple[tuple[object, ...], ...]:
        """
        Build deterministic socket-shape rows from target matches.
        """
        match_count = len(matches)
        if match_count == 0:
            return ()
        if match_count == 1:
            socket_ref = matches[0]
            return (
                (
                    socket_ref.node_id,
                    socket_ref.param_path_id,
                    socket_ref.param_name,
                    socket_ref.socket_kind_value,
                ),
            )
        if match_count == 2:
            first_ref = matches[0]
            second_ref = matches[1]
            first_row = (
                first_ref.node_id,
                first_ref.param_path_id,
                first_ref.param_name,
                first_ref.socket_kind_value,
            )
            second_row = (
                second_ref.node_id,
                second_ref.param_path_id,
                second_ref.param_name,
                second_ref.socket_kind_value,
            )
            if second_row < first_row:
                return second_row, first_row
            return first_row, second_row

        rows: List[tuple[object, ...]] = []
        for socket_ref in matches:
            rows.append(
                (
                    socket_ref.node_id,
                    socket_ref.param_path_id,
                    socket_ref.param_name,
                    socket_ref.socket_kind_value,
                )
            )
        rows.sort()
        return tuple(rows)

    @staticmethod
    def _spec_key(spec: TargetSpec) -> str:
        """
        Return the canonical lookup key for one parsed TargetSpec.
        """
        if spec.kind is TargetSpecKind.BROADCAST:
            return f"**{spec.param_name}"
        if spec.kind is TargetSpecKind.UNIQUE:
            return f"*{spec.param_name}"
        if spec.kind is TargetSpecKind.PATH:
            return ">".join(spec.path or ())
        raise RuntimeError(f"Unsupported TargetSpecKind: {spec.kind!r}")
