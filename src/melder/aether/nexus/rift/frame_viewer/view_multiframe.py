"""
Multi-frame descriptor helper for the Rift-backed viewer surface.

This module holds the cross-frame inventory, grouping, and comparison helper
that reuses `FrameViewer` lookup utilities without taking ownership of frame-
local descriptor or ACL state.
"""
import threading
from contextlib import contextmanager
from typing import Any, Callable, Dict, Iterator, List, Optional, Protocol, Tuple
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.aether.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.aether.nexus.rift.frame_viewer.view_action_hooks import (
    decorate_public_view_actions,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.iconduitrecord import IConduitRecord
from melder.utilities.interfaces.ispellrecord import ISpellRecord


class _RiftViewerSurface(Protocol):
    """
    Narrow borrowed Rift surface used by ViewMultiFrame.
    """

    def list_assigned_frame_names(self) -> Tuple[str, ...]:
        ...

    def list_accessible_nexus_frame_names(self) -> Tuple[str, ...]:
        ...

    def list_accessible_non_nexus_frame_names(self) -> Tuple[str, ...]:
        ...


class _FrameViewerSurface(Protocol):
    """
    Narrow borrowed FrameViewer surface used by ViewMultiFrame.
    """

    _rift: _RiftViewerSurface

    @property
    def _lock(self) -> object:
        ...

    def _get_required_frame_descriptor(self, frame_name: str) -> FrameDescriptor:
        ...

    @contextmanager
    def _entered_view_action(self, *, action_name: str) -> Any:
        ...

    def _get_frame_names_for_query(
            self,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ...]:
        ...

    def _iter_conduit_records(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Iterator[IConduitRecord]:
        ...

    def _iter_spell_records(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Iterator[ISpellRecord]:
        ...

    def _build_spell_source_id(self, spell_record: ISpellRecord) -> str:
        ...

    def _normalize_spellframe_value(self, spellframe: object) -> Optional[str]:
        ...

    def _get_required_spell_record(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ISpellRecord]:
        ...


@decorate_public_view_actions
class ViewMultiFrame(Cleanable):
    """
    Purpose:
        Hold descriptor-oriented multi-frame and record-level viewer methods.

    Contract:
        - Owns only a borrowed reference to the parent `FrameViewer`.
        - Reuses the viewer's private descriptor and record utilities instead
          of duplicating lookup logic or Rift access.
        - Exposes cross-frame and descriptor-hosted inventory/comparison logic
          without introducing frame-local helper binding state.

    Lifecycle:
        Cleanup is idempotent and clears only the borrowed viewer reference.
        `ViewMultiFrame` is cheap to create and may be materialized on demand.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_viewer",
    ]

    def __init__(self, *, viewer: _FrameViewerSurface) -> None:
        """
        Initialize one multi-frame helper.

        Contract:
            - Stores only the borrowed parent viewer reference.
            - Does not cache descriptor, ACL, or record state locally.

        Args:
            viewer:
                Borrowed `FrameViewer` used to source descriptor and record
                utilities.

        Returns:
            None.
        """
        super().__init__()
        if viewer is None:
            raise TypeError("viewer cannot be None.")
        self._viewer = viewer

    def cleanup(self) -> None:
        """
        Idempotently drop the borrowed viewer reference.

        Contract:
            - Safe to call more than once.
            - Clears only the helper's borrowed viewer reference.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._viewer

    @property
    def _lock(self) -> threading.RLock:
        """
        Return the shared viewer lock.

        Returns:
            object: Borrowed lock used for grouped viewer reads.
        """
        return self._viewer._lock

    def _get_required_frame_descriptor(self, frame_name: str) -> FrameDescriptor:
        """
        Return one hosted frame descriptor through the parent viewer.

        Args:
            frame_name:
                Hosted frame name.

        Returns:
            FrameDescriptor: Descriptor for the requested frame.
        """
        return self._viewer._get_required_frame_descriptor(frame_name)

    @contextmanager
    def _entered_view_action(self, *, action_name: str) -> Any:
        """
        Enter one viewer action hook scope through the parent viewer.

        Args:
            action_name:
                Stable viewer action name.

        Returns:
            Any: Viewer hook scope context manager.
        """
        self.check_cleaned()
        with self._viewer._entered_view_action(action_name=action_name):
            yield

    def _get_frame_names_for_query(self, frame_name: Optional[str] = None) -> Tuple[str, ...]:
        """
        Return the concrete frame names that should be queried.

        Args:
            frame_name:
                Optional hosted frame name filter.

        Returns:
            Tuple[str, ...]: Hosted frame names selected for the query.
        """
        return self._viewer._get_frame_names_for_query(frame_name)

    def _iter_conduit_records(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Iterator[IConduitRecord]:
        """
        Yield descriptor-owned conduit records for the selected frame scope.

        Args:
            frame_name:
                Optional hosted frame name filter.

        Yields:
            IConduitRecord: Descriptor-owned conduit records.
        """
        for conduit_record in self._viewer._iter_conduit_records(
                frame_name=frame_name,
        ):
            yield conduit_record

    def _iter_spell_records(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Iterator[ISpellRecord]:
        """
        Yield descriptor-owned spell records for the selected frame scope.

        Args:
            frame_name:
                Optional hosted frame name filter.

        Yields:
            ISpellRecord: Descriptor-owned spell records.
        """
        for spell_record in self._viewer._iter_spell_records(
                frame_name=frame_name,
        ):
            yield spell_record

    def _build_spell_source_id(self, spell_record: ISpellRecord) -> str:
        """
        Build one published spell source id from a spell record.

        Args:
            spell_record:
                Descriptor-owned spell record.

        Returns:
            str: Published spell source id in `spellbook_id:spell_id` form.
        """
        return self._viewer._build_spell_source_id(spell_record)

    def _normalize_spellframe_value(self, spellframe: object) -> Optional[str]:
        """
        Return one stable string view of a spellframe value.

        Args:
            spellframe:
                Raw spellframe value.

        Returns:
            Optional[str]: Normalized spellframe name when present.
        """
        return self._viewer._normalize_spellframe_value(spellframe)

    def _get_required_spell_record(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ISpellRecord]:
        """
        Return one descriptor-owned spell record plus its hosted frame.

        Args:
            spell_source_id:
                Published spell source id in `spellbook_id:spell_id` form.
            frame_name:
                Optional hosted frame name to constrain the lookup.

        Returns:
            Tuple[str, ISpellRecord]: `(frame_name, spell_record)` for the resolved
            record.
        """
        resolved_frame_name, spell_record = self._viewer._get_required_spell_record(
            spell_source_id,
            frame_name=frame_name,
        )
        return resolved_frame_name, spell_record

    def _get_required_conduit_record(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, IConduitRecord]:
        """
        Return one descriptor-owned conduit record or raise.

        Args:
            conduit_id:
                Published conduit id.
            frame_name:
                Optional hosted frame name to constrain the lookup.

        Returns:
            Tuple[str, IConduitRecord]: `(frame_name, conduit_record)` for the
            resolved record.
        """
        if not conduit_id:
            raise ValueError("conduit_id cannot be empty.")
        matching_records: List[Tuple[str, IConduitRecord]] = []
        for current_frame_name in self._get_frame_names_for_query(frame_name):
            descriptor = self._get_required_frame_descriptor(current_frame_name)
            record = descriptor.conduit_records_by_id.get(conduit_id)
            if record is None:
                continue
            matching_records.append((current_frame_name, record))
        if len(matching_records) == 0:
            raise ValueError(
                "Conduit id '{0}' was not found.".format(conduit_id)
            )
        if len(matching_records) > 1:
            raise ValueError(
                "Conduit id '{0}' is ambiguous across hosted frames.".format(
                    conduit_id
                )
            )
        return matching_records[0]

    def _compare_sorted_value_sets(self, left_values: Tuple[str, ...], right_values: Tuple[str, ...]) -> Dict[str, Tuple[str, ...]]:
        """
        Return one deterministic shared/left-only/right-only value diff.

        Args:
            left_values:
                Left normalized value tuple.
            right_values:
                Right normalized value tuple.

        Returns:
            Dict[str, Tuple[str, ...]]: Shared and directional set deltas.
        """
        left_set = set(left_values)
        right_set = set(right_values)
        return {
            "shared": tuple(sorted(left_set & right_set)),
            "left_only": tuple(sorted(left_set - right_set)),
            "right_only": tuple(sorted(right_set - left_set)),
        }

    @staticmethod
    def _get_required_object_map(value: object, *, name: str) -> Dict[str, object]:
        """
        Return one validated string-keyed object map.

        Args:
            value:
                Candidate mapping.
            name:
                Field label for error reporting.

        Returns:
            Dict[str, object]: Validated string-keyed object map.
        """
        if not isinstance(value, dict):
            raise TypeError("{0} must be a dict[str, object].".format(name))
        normalized: Dict[str, object] = {}
        for current_key, current_value in value.items():
            if not isinstance(current_key, str):
                raise TypeError("{0} keys must be strings.".format(name))
            normalized[current_key] = current_value
        return normalized

    @staticmethod
    def _get_required_string_tuple(
            value: object,
            *,
            name: str,
    ) -> Tuple[str, ...]:
        """
        Return one validated tuple of strings.

        Args:
            value:
                Candidate iterable of strings.
            name:
                Field label for error reporting.

        Returns:
            Tuple[str, ...]: Validated tuple of strings.
        """
        if not isinstance(value, (tuple, list)):
            raise TypeError("{0} must be a tuple[str, ...].".format(name))
        normalized: List[str] = []
        for current_value in value:
            if not isinstance(current_value, str):
                raise TypeError("{0} must contain only strings.".format(name))
            normalized.append(current_value)
        return tuple(normalized)

    def _describe_spell_value_groups(self, *, frame_name: Optional[str], value_getter: Callable[[ISpellRecord], Optional[object]]) -> Dict[str, Tuple[str, ...]]:
        """
        Group spell source ids by one normalized spell-record value.

        Args:
            frame_name:
                Optional hosted frame name filter.
            value_getter:
                Callable that extracts the grouping value from one spell
                record.

        Returns:
            Dict[str, Tuple[str, ...]]: Grouping value mapped to spell source
            ids.
        """
        grouped_source_ids_by_value: Dict[str, List[str]] = {}
        for spell_record in self._iter_spell_records(frame_name=frame_name):
            current_value = value_getter(spell_record)
            if current_value is None:
                continue
            grouped_source_ids_by_value.setdefault(
                str(current_value),
                [],
            ).append(self._build_spell_source_id(spell_record))
        return {
            current_value: tuple(sorted(source_ids))
            for current_value, source_ids in grouped_source_ids_by_value.items()
        }

    def _describe_spell_value_collisions(self, *, frame_name: Optional[str], value_getter: Callable[[ISpellRecord], Optional[object]]) -> Dict[str, Tuple[str, ...]]:
        """
        Return spell value groups that have more than one published member.

        Args:
            frame_name:
                Optional hosted frame name filter.
            value_getter:
                Callable that extracts the grouping value from one spell
                record.

        Returns:
            Dict[str, Tuple[str, ...]]: Colliding value groups only.
        """
        grouped_source_ids_by_value = self._describe_spell_value_groups(
            frame_name=frame_name,
            value_getter=value_getter,
        )
        return {
            current_value: source_ids
            for current_value, source_ids in grouped_source_ids_by_value.items()
            if len(source_ids) > 1
        }

    def _describe_spellbook_mismatches(
            self,
            *,
            frame_name: Optional[str],
            value_getter: Callable[[ISpellRecord], Optional[object]],
    ) -> Dict[str, Dict[str, object]]:
        """
        Return spellbook groups whose selected value is not uniform.

        Args:
            frame_name:
                Optional hosted frame name filter.
            value_getter:
                Callable that extracts the compared value from one spell
                record.

        Returns:
            Dict[str, Dict[str, object]]: Spellbook mismatch summaries.
        """
        grouped_records_by_spellbook_id: Dict[str, List[ISpellRecord]] = {}
        for spell_record in self._iter_spell_records(frame_name=frame_name):
            grouped_records_by_spellbook_id.setdefault(
                spell_record.origin_spellbook_id,
                [],
            ).append(spell_record)
        mismatches_by_spellbook_id: Dict[str, Dict[str, object]] = {}
        for spellbook_id, spell_records in grouped_records_by_spellbook_id.items():
            current_values = {
                str(value_getter(spell_record))
                for spell_record in spell_records
                if value_getter(spell_record) is not None
            }
            if len(current_values) <= 1:
                continue
            mismatches_by_spellbook_id[spellbook_id] = {
                "source_ids": tuple(
                    sorted(
                        self._build_spell_source_id(spell_record)
                        for spell_record in spell_records
                    )
                ),
                "values": tuple(sorted(current_values)),
            }
        return mismatches_by_spellbook_id

    def _normalize_policy_name(self, policy: object) -> Optional[str]:
        """
        Return one stable string view of a conduit policy value.

        Args:
            policy:
                Raw conduit policy value.

        Returns:
            Optional[str]: Normalized conduit policy name when present.
        """
        if policy is None:
            return None
        if isinstance(policy, str):
            return policy
        policy_name = getattr(policy, "name", None)
        if isinstance(policy_name, str):
            return policy_name
        return str(policy)

    @staticmethod
    def _parse_spell_source_id(spell_source_id: str) -> Tuple[str, str]:
        """
        Parse one published spell source id into its canonical record key.

        Args:
            spell_source_id:
                Published spell source id in `spellbook_id:spell_id` form.

        Returns:
            Tuple[str, str]: `(spellbook_id, spell_id)` key.
        """
        parts = spell_source_id.split(":", 1)
        if len(parts) != 2:
            raise ValueError(
                "spell_source_id '{0}' must be in 'spellbook_id:spell_id' form.".format(
                    spell_source_id
                )
            )
        return parts[0], parts[1]


    def list_frame_names(self) -> List[str]:
        """
        Return the currently linked frame names in deterministic order.

        Returns:
            List[str]: Sorted linked frame names.
        """
        self.check_cleaned()
        with self._lock:
            return list(sorted(self._viewer._rift.list_assigned_frame_names()))

    def list_linked_frame_names(self) -> List[str]:
        """
        Return the currently linked frame names in deterministic order.

        Returns:
            List[str]: Sorted linked frame names.
        """
        self.check_cleaned()
        return self.list_frame_names()

    def list_nexus_frame_names(self) -> List[str]:
        """
        Return the currently accessible Nexus-managed frame names.

        Returns:
            List[str]: Sorted accessible Nexus-managed frame names.
        """
        self.check_cleaned()
        with self._lock:
            return list(
                sorted(self._viewer._rift.list_accessible_nexus_frame_names())
            )

    def list_non_nexus_frame_names(self) -> List[str]:
        """
        Return the currently accessible published non-Nexus frame names.

        Returns:
            List[str]: Sorted accessible published non-Nexus frame names.
        """
        self.check_cleaned()
        with self._lock:
            return list(
                sorted(self._viewer._rift.list_accessible_non_nexus_frame_names())
            )

    def count_frames(self) -> int:
        """
        Return the number of hosted frame descriptors.

        Returns:
            int: Hosted frame count.
        """
        self.check_cleaned()
        return len(self.list_frame_names())

    def count_root_conduits(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> int:
        """
        Return the number of root conduit records.

        Args:
            frame_name:
                Optional frame name. When omitted, counts across all hosted
                frames.

        Returns:
            int: Root conduit record count.
        """
        self.check_cleaned()
        frame_names = [frame_name] if frame_name is not None else self.list_frame_names()
        total_count = 0
        for current_frame_name in frame_names:
            descriptor = self._get_required_frame_descriptor(current_frame_name)
            total_count += len(
                {
                    conduit_record.root_conduit_id
                    for conduit_record in descriptor.conduit_records_by_id.values()
                }
            )
        return total_count

    def count_spell_records(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> int:
        """
        Return the number of spell records.

        Args:
            frame_name:
                Optional frame name. When omitted, counts across all hosted
                frames.

        Returns:
            int: Spell record count.
        """
        self.check_cleaned()
        frame_names = [frame_name] if frame_name is not None else self.list_frame_names()
        total_count = 0
        for current_frame_name in frame_names:
            descriptor = self._get_required_frame_descriptor(current_frame_name)
            total_count += len(descriptor.spell_records_by_key)
        return total_count

    def describe_frame(self, frame_name: str) -> Dict[str, object]:
        """
        Return a descriptor-level summary for one hosted frame.

        Contract:
            This host-level summary is limited to descriptor structure and
            published record identity. It does not expose payload bodies or
            ACL-shaped payload visibility.

        Args:
            frame_name:
                Hosted frame name to summarize.

        Returns:
            Dict[str, object]: Descriptor-level frame summary.
        """
        self.check_cleaned()
        descriptor = self._get_required_frame_descriptor(frame_name)
        frame_overview = descriptor.frame_overview
        return {
            "frame_name": frame_name,
            "frame_id": frame_overview.frame_id if frame_overview is not None else None,
            "nexus_label": (
                frame_overview.nexus_label if frame_overview is not None else None
            ),
            "nexus_version": (
                frame_overview.nexus_version if frame_overview is not None else None
            ),
            "conduit_record_count": len(descriptor.conduit_records_by_id),
            "root_conduit_count": len(
                {
                    conduit_record.root_conduit_id
                    for conduit_record in descriptor.conduit_records_by_id.values()
                }
            ),
            "spell_record_count": len(descriptor.spell_records_by_key),
        }

    def describe_frames(self) -> Dict[str, Dict[str, object]]:
        """
        Return descriptor-level summaries for all hosted frames.

        Returns:
            Dict[str, Dict[str, object]]: Hosted frame summaries keyed by frame
            name.
        """
        self.check_cleaned()
        return {
            current_frame_name: self.describe_frame(current_frame_name)
            for current_frame_name in self.list_frame_names()
        }

    def describe_frame_brief(self, frame_name: str) -> Dict[str, object]:
        """
        Return one compact descriptor-level frame summary.

        Purpose:
            Give the operator a smaller "start here" frame summary than
            `describe_frame(...)` while staying entirely on descriptor-owned
            host data.

        Contract:
            - Uses only descriptor/record identity and count data.
            - Does not expose payload bodies or ACL-shaped visibility details.
            - Always includes the frame's Nexus contract and top-level record
              counts.

        Args:
            frame_name:
                Hosted frame name to summarize.

        Returns:
            Dict[str, object]: Compact descriptor-level frame summary.
        """
        self.check_cleaned()
        frame_summary = self.describe_frame(frame_name)
        return {
            "frame_name": frame_summary["frame_name"],
            "frame_id": frame_summary["frame_id"],
            "nexus_contract": "{0}:{1}".format(
                frame_summary["nexus_label"],
                frame_summary["nexus_version"],
            ),
            "conduit_record_count": frame_summary["conduit_record_count"],
            "root_conduit_count": frame_summary["root_conduit_count"],
            "spell_record_count": frame_summary["spell_record_count"],
        }

    def describe_host_inventory(self) -> Dict[str, object]:
        """
        Return one compact host-level inventory summary.

        Purpose:
            Give the operator a quick overview of what the `FrameViewer` host
            is carrying without forcing a deeper descriptor walk.

        Contract:
            - Aggregates only descriptor-owned counts, names, and record-level
              identities.
            - Does not expose payload bodies or ACL-shaped detail.

        Returns:
            Dict[str, object]: Compact host-level inventory summary.
        """
        self.check_cleaned()
        return {
            "frame_count": self.count_frames(),
            "frame_names": tuple(self.list_frame_names()),
            "frame_ids": tuple(self.list_frame_ids()),
            "conduit_record_count": self.count_conduit_records(),
            "root_conduit_count": self.count_root_conduits(),
            "spell_record_count": self.count_spell_records(),
            "origin_spellbook_count": self.count_spellbooks(),
            "origin_spellbook_ids": tuple(self.list_origin_spellbook_ids()),
            "permissions": tuple(self.list_permissions()),
            "existence_kinds": tuple(self.list_existence_kinds()),
        }

    def describe_frames_inventory(self) -> Dict[str, Dict[str, object]]:
        """
        Return one compact per-frame descriptor inventory summary.

        Purpose:
            Give the operator a small inventory table across hosted frames
            without exposing anything deeper than descriptor-owned counts and
            stable record identity.

        Contract:
            - Multi-frame output stays shallow and descriptor-only.
            - Does not expose payload bodies or ACL-shaped visibility detail.
            - Includes only per-frame counts and stable host identity fields.

        Returns:
            Dict[str, Dict[str, object]]: Per-frame compact inventories keyed
            by frame name.
        """
        self.check_cleaned()
        return {
            current_frame_name: {
                "frame_id": self.describe_frame(current_frame_name)["frame_id"],
                "nexus_contract": "{0}:{1}".format(
                    self.describe_frame(current_frame_name)["nexus_label"],
                    self.describe_frame(current_frame_name)["nexus_version"],
                ),
                "conduit_record_count": self.describe_frame(current_frame_name)[
                    "conduit_record_count"
                ],
                "root_conduit_count": self.describe_frame(current_frame_name)[
                    "root_conduit_count"
                ],
                "spell_record_count": self.describe_frame(current_frame_name)[
                    "spell_record_count"
                ],
                "origin_spellbook_count": len(
                    self.list_origin_spellbook_ids(frame_name=current_frame_name)
                ),
                "index_count": len(
                    self.list_index_ids(frame_name=current_frame_name)
                ),
            }
            for current_frame_name in self.list_frame_names()
        }

    def compare_frames(
            self,
            left_frame_name: str,
            right_frame_name: str,
    ) -> Dict[str, object]:
        """
        Compare two hosted frame descriptors at the record-identity level.

        Purpose:
            Give the operator one descriptor-only diff between two hosted
            frames so they can see what differs without manually comparing the
            individual host list methods.

        Contract:
            - Uses descriptor-owned identities, counts, and normalized values
              only.
            - Does not expose payload bodies or ACL-shaped detail.
            - Returns shared sets plus left-only/right-only deltas for the most
              important descriptor-level inventories.

        Args:
            left_frame_name:
                Left hosted frame name.
            right_frame_name:
                Right hosted frame name.

        Returns:
            Dict[str, object]: Descriptor-level comparison summary.
        """
        self.check_cleaned()
        left_descriptor = self._get_required_frame_descriptor(left_frame_name)
        self._get_required_frame_descriptor(right_frame_name)
        left_frame_overview = left_descriptor.frame_overview
        right_frame_overview = self._get_required_frame_descriptor(
            right_frame_name
        ).frame_overview
        return {
            "left_frame_name": left_frame_name,
            "right_frame_name": right_frame_name,
            "same_frame_id": (
                left_frame_overview is not None
                and right_frame_overview is not None
                and left_frame_overview.frame_id == right_frame_overview.frame_id
            ),
            "same_nexus_contract": (
                left_frame_overview is not None
                and right_frame_overview is not None
                and left_frame_overview.nexus_label == right_frame_overview.nexus_label
                and left_frame_overview.nexus_version == right_frame_overview.nexus_version
            ),
            "conduits": self.compare_frame_conduits(
                left_frame_name,
                right_frame_name,
            ),
            "spells": self.compare_frame_spells(
                left_frame_name,
                right_frame_name,
            ),
            "spellbooks": self._compare_sorted_value_sets(
                tuple(self.list_origin_spellbook_ids(frame_name=left_frame_name)),
                tuple(self.list_origin_spellbook_ids(frame_name=right_frame_name)),
            ),
            "permissions": self._compare_sorted_value_sets(
                tuple(self.list_permissions(frame_name=left_frame_name)),
                tuple(self.list_permissions(frame_name=right_frame_name)),
            ),
            "existence_kinds": self._compare_sorted_value_sets(
                tuple(self.list_existence_kinds(frame_name=left_frame_name)),
                tuple(self.list_existence_kinds(frame_name=right_frame_name)),
            ),
            "spellframes": self._compare_sorted_value_sets(
                tuple(self.list_spellframes(frame_name=left_frame_name)),
                tuple(self.list_spellframes(frame_name=right_frame_name)),
            ),
        }

    def compare_frames_brief(
            self,
            left_frame_name: str,
            right_frame_name: str,
    ) -> Dict[str, object]:
        """
        Return one compact descriptor-only comparison summary for two frames.

        Purpose:
            Provide a smaller "what materially differs?" answer than the full
            `compare_frames(...)` payload.

        Contract:
            - Uses only descriptor-level comparison data derived from the full
              frame comparison.
            - Keeps multi-frame output shallow and count-focused.

        Args:
            left_frame_name:
                Left hosted frame name.
            right_frame_name:
                Right hosted frame name.

        Returns:
            Dict[str, object]: Compact descriptor-level frame comparison.
        """
        self.check_cleaned()
        full_comparison = self.compare_frames(left_frame_name, right_frame_name)
        conduit_comparison = self._get_required_object_map(
            full_comparison["conduits"],
            name="conduits",
        )
        conduit_id_comparison = self._get_required_object_map(
            conduit_comparison["conduit_ids"],
            name="conduit_ids",
        )
        spell_comparison = self._get_required_object_map(
            full_comparison["spells"],
            name="spells",
        )
        spell_source_id_comparison = self._get_required_object_map(
            spell_comparison["spell_source_ids"],
            name="spell_source_ids",
        )
        permissions_comparison = self._get_required_object_map(
            full_comparison["permissions"],
            name="permissions",
        )
        existence_comparison = self._get_required_object_map(
            full_comparison["existence_kinds"],
            name="existence_kinds",
        )
        return {
            "left_frame_name": left_frame_name,
            "right_frame_name": right_frame_name,
            "same_frame_id": full_comparison["same_frame_id"],
            "same_nexus_contract": full_comparison["same_nexus_contract"],
            "left_only_conduit_count": len(
                self._get_required_string_tuple(
                    conduit_id_comparison["left_only"],
                    name="left_only_conduit_ids",
                )
            ),
            "right_only_conduit_count": len(
                self._get_required_string_tuple(
                    conduit_id_comparison["right_only"],
                    name="right_only_conduit_ids",
                )
            ),
            "left_only_spell_count": len(
                self._get_required_string_tuple(
                    spell_source_id_comparison["left_only"],
                    name="left_only_spell_source_ids",
                )
            ),
            "right_only_spell_count": len(
                self._get_required_string_tuple(
                    spell_source_id_comparison["right_only"],
                    name="right_only_spell_source_ids",
                )
            ),
            "shared_permission_count": len(
                self._get_required_string_tuple(
                    permissions_comparison["shared"],
                    name="shared_permissions",
                )
            ),
            "shared_existence_kind_count": len(
                self._get_required_string_tuple(
                    existence_comparison["shared"],
                    name="shared_existence_kinds",
                )
            ),
        }

    def compare_frame_conduits(
            self,
            left_frame_name: str,
            right_frame_name: str,
    ) -> Dict[str, object]:
        """
        Compare the conduit-record inventories of two hosted frames.

        Args:
            left_frame_name:
                Left hosted frame name.
            right_frame_name:
                Right hosted frame name.

        Returns:
            Dict[str, object]: Conduit-record comparison summary.
        """
        self.check_cleaned()
        left_conduit_ids = tuple(
            self.list_conduit_record_ids(frame_name=left_frame_name)
        )
        right_conduit_ids = tuple(
            self.list_conduit_record_ids(frame_name=right_frame_name)
        )
        left_root_conduit_ids = tuple(
            self.list_root_conduit_ids(frame_name=left_frame_name)
        )
        right_root_conduit_ids = tuple(
            self.list_root_conduit_ids(frame_name=right_frame_name)
        )
        return {
            "record_counts": {
                "left": len(left_conduit_ids),
                "right": len(right_conduit_ids),
            },
            "conduit_ids": self._compare_sorted_value_sets(
                left_conduit_ids,
                right_conduit_ids,
            ),
            "root_conduit_ids": self._compare_sorted_value_sets(
                left_root_conduit_ids,
                right_root_conduit_ids,
            ),
        }

    def compare_frame_spells(
            self,
            left_frame_name: str,
            right_frame_name: str,
    ) -> Dict[str, object]:
        """
        Compare the spell-record inventories of two hosted frames.

        Args:
            left_frame_name:
                Left hosted frame name.
            right_frame_name:
                Right hosted frame name.

        Returns:
            Dict[str, object]: Spell-record comparison summary.
        """
        self.check_cleaned()
        left_spell_source_ids = tuple(
            self.list_spell_source_ids_for_frame(left_frame_name)
        )
        right_spell_source_ids = tuple(
            self.list_spell_source_ids_for_frame(right_frame_name)
        )
        left_index_ids = tuple(self.list_index_ids(frame_name=left_frame_name))
        right_index_ids = tuple(self.list_index_ids(frame_name=right_frame_name))
        left_spell_names = tuple(self.list_spell_names(frame_name=left_frame_name))
        right_spell_names = tuple(self.list_spell_names(frame_name=right_frame_name))
        left_binding_names = tuple(self.list_binding_names(frame_name=left_frame_name))
        right_binding_names = tuple(self.list_binding_names(frame_name=right_frame_name))
        return {
            "record_counts": {
                "left": len(left_spell_source_ids),
                "right": len(right_spell_source_ids),
            },
            "spell_source_ids": self._compare_sorted_value_sets(
                left_spell_source_ids,
                right_spell_source_ids,
            ),
            "index_ids": self._compare_sorted_value_sets(
                left_index_ids,
                right_index_ids,
            ),
            "spell_names": self._compare_sorted_value_sets(
                left_spell_names,
                right_spell_names,
            ),
            "binding_names": self._compare_sorted_value_sets(
                left_binding_names,
                right_binding_names,
            ),
        }

    def describe_binding_name_collisions(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Return binding-name collisions in the selected descriptor scope.

        Purpose:
            Surface visible ambiguity at the record-identity level when the
            same binding name is attached to multiple published spell records.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            Dict[str, Tuple[str, ...]]: Binding names mapped to the colliding
            spell source ids.
        """
        self.check_cleaned()
        return self._describe_spell_value_collisions(
            frame_name=frame_name,
            value_getter=lambda spell_record: spell_record.binding_name,
        )

    def describe_spell_name_collisions(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Return spell-name collisions in the selected descriptor scope.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            Dict[str, Tuple[str, ...]]: Spell names mapped to the colliding
            spell source ids.
        """
        self.check_cleaned()
        return self._describe_spell_value_collisions(
            frame_name=frame_name,
            value_getter=lambda spell_record: spell_record.spell_name,
        )

    def describe_index_groups(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Return spell-index groups in the selected descriptor scope.

        Purpose:
            Surface all published spell source ids grouped by spell-index id,
            even when an index currently has only one visible member.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            Dict[str, Tuple[str, ...]]: Spell-index ids mapped to published spell
            source ids.
        """
        self.check_cleaned()
        return self._describe_spell_value_groups(
            frame_name=frame_name,
            value_getter=lambda spell_record: spell_record.spell_index_id,
        )

    def describe_spellframe_groups(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Tuple[str, ...]]:
        """
        Return spellframe groups in the selected descriptor scope.

        Purpose:
            Group published spells by normalized spellframe value so frame-wide
            spellframe overlaps are obvious.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            Dict[str, Tuple[str, ...]]: Spellframe values mapped to published
            spell source ids.
        """
        self.check_cleaned()
        return self._describe_spell_value_groups(
            frame_name=frame_name,
            value_getter=lambda spell_record: self._normalize_spellframe_value(
                spell_record.spellframe
            ),
        )

    def describe_spellbook_permission_mismatches(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Dict[str, object]]:
        """
        Return spellbook groups whose permission posture is not uniform.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            Dict[str, Dict[str, object]]: Spellbook ids mapped to permission
            mismatch summaries.
        """
        self.check_cleaned()
        return self._describe_spellbook_mismatches(
            frame_name=frame_name,
            value_getter=lambda spell_record: spell_record.permissions.name,
        )

    def describe_spellbook_existence_mismatches(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Dict[str, object]]:
        """
        Return spellbook groups whose existence posture is not uniform.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            Dict[str, Dict[str, object]]: Spellbook ids mapped to existence
            mismatch summaries.
        """
        self.check_cleaned()
        return self._describe_spellbook_mismatches(
            frame_name=frame_name,
            value_getter=lambda spell_record: spell_record.existence.name,
        )

    def compare_spell_records(
            self,
            left_spell_source_id: str,
            right_spell_source_id: str,
            *,
            left_frame_name: Optional[str] = None,
            right_frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Compare two published spell records.

        Purpose:
            Give the operator one record-level spell diff without requiring them
            to manually compare multiple identity, provenance, and posture
            methods.

        Args:
            left_spell_source_id:
                Left published spell source id.
            right_spell_source_id:
                Right published spell source id.
            left_frame_name:
                Optional hosted frame constraint for the left spell.
            right_frame_name:
                Optional hosted frame constraint for the right spell.

        Returns:
            Dict[str, object]: Record-level spell comparison summary.
        """
        self.check_cleaned()
        resolved_left_frame_name, left_spell_record = self._get_required_spell_record(
            left_spell_source_id,
            frame_name=left_frame_name,
        )
        resolved_right_frame_name, right_spell_record = self._get_required_spell_record(
            right_spell_source_id,
            frame_name=right_frame_name,
        )
        return {
            "left_source_id": left_spell_source_id,
            "right_source_id": right_spell_source_id,
            "same_frame": resolved_left_frame_name == resolved_right_frame_name,
            "same_origin_spellbook": (
                left_spell_record.origin_spellbook_id
                == right_spell_record.origin_spellbook_id
            ),
            "same_owner_conduit": (
                left_spell_record.owner_conduit_id
                == right_spell_record.owner_conduit_id
            ),
            "same_spell_index_id": (
                left_spell_record.spell_index_id == right_spell_record.spell_index_id
            ),
            "same_spell_name": (
                left_spell_record.spell_name == right_spell_record.spell_name
            ),
            "same_binding_name": (
                left_spell_record.binding_name == right_spell_record.binding_name
            ),
            "same_spellframe": (
                self._normalize_spellframe_value(left_spell_record.spellframe)
                == self._normalize_spellframe_value(right_spell_record.spellframe)
            ),
            "same_permissions": (
                left_spell_record.permissions.name
                == right_spell_record.permissions.name
            ),
            "same_existence": (
                left_spell_record.existence.name
                == right_spell_record.existence.name
            ),
            "same_payload_type": (
                left_spell_record.payload.payload_type
                == right_spell_record.payload.payload_type
            ),
            "same_nexus_contract": (
                left_spell_record.nexus_label == right_spell_record.nexus_label
                and left_spell_record.nexus_version == right_spell_record.nexus_version
            ),
        }

    def compare_conduit_records(
            self,
            left_conduit_id: str,
            right_conduit_id: str,
            *,
            left_frame_name: Optional[str] = None,
            right_frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Compare two published conduit records.

        Args:
            left_conduit_id:
                Left published conduit id.
            right_conduit_id:
                Right published conduit id.
            left_frame_name:
                Optional hosted frame constraint for the left conduit.
            right_frame_name:
                Optional hosted frame constraint for the right conduit.

        Returns:
            Dict[str, object]: Record-level conduit comparison summary.
        """
        self.check_cleaned()
        resolved_left_frame_name, left_conduit_record = self._get_required_conduit_record(
            left_conduit_id,
            frame_name=left_frame_name,
        )
        resolved_right_frame_name, right_conduit_record = self._get_required_conduit_record(
            right_conduit_id,
            frame_name=right_frame_name,
        )
        return {
            "left_conduit_id": left_conduit_id,
            "right_conduit_id": right_conduit_id,
            "same_frame": resolved_left_frame_name == resolved_right_frame_name,
            "same_root_conduit_id": (
                left_conduit_record.root_conduit_id
                == right_conduit_record.root_conduit_id
            ),
            "same_origin_spellbook": (
                left_conduit_record.origin_spellbook_id
                == right_conduit_record.origin_spellbook_id
            ),
            "same_policy": (
                self._normalize_policy_name(left_conduit_record.payload.policy)
                == self._normalize_policy_name(right_conduit_record.payload.policy)
            ),
            "same_conduit_state": (
                left_conduit_record.payload.conduit_state.name
                == right_conduit_record.payload.conduit_state.name
            ),
            "same_peer_conduit_ids": (
                tuple(left_conduit_record.payload.peer_conduit_ids)
                == tuple(right_conduit_record.payload.peer_conduit_ids)
            ),
            "same_nexus_contract": (
                left_conduit_record.nexus_label == right_conduit_record.nexus_label
                and left_conduit_record.nexus_version == right_conduit_record.nexus_version
            ),
        }

    def list_spell_source_ids_for_frame(self, frame_name: str) -> List[str]:
        """
        Return spell source ids for one hosted frame.

        Purpose:
            Provide the canonical published spell identities for one hosted
            descriptor in deterministic order.

        Args:
            frame_name:
                Hosted frame name whose spell source ids should be returned.

        Returns:
            List[str]: Spell source ids for the frame.
        """
        self.check_cleaned()
        descriptor = self._get_required_frame_descriptor(frame_name)
        return [
            self._build_spell_source_id(descriptor.spell_records_by_key[record_key])
            for record_key in sorted(descriptor.spell_records_by_key.keys())
        ]

    def list_frame_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return published frame ids for the selected descriptor scope.

        Purpose:
            Surface the stable published frame identifiers without exposing any
            payload body data.

        Contract:
            - Reads only `FrameRecord` identity fields.
            - Returns ids in deterministic frame-order.
            - Omits frames that do not currently expose a `frame_overview`
              record.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns frame ids
                across all hosted descriptors.

        Returns:
            List[str]: Published frame ids in deterministic order.
        """
        self.check_cleaned()
        frame_ids: List[str] = []
        for current_frame_name in self._get_frame_names_for_query(frame_name):
            descriptor = self._get_required_frame_descriptor(current_frame_name)
            frame_overview = descriptor.frame_overview
            if frame_overview is None:
                continue
            frame_ids.append(frame_overview.frame_id)
        return frame_ids

    def list_nexus_contracts(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """
        Return the published Nexus dataset contracts for hosted frames.

        Purpose:
            Give the operator a direct host-level view of the record contracts
            currently attached to the selected descriptor scope.

        Contract:
            - Uses only record-level `nexus_label` / `nexus_version`.
            - Does not expose payload body content.
            - Returns one contract entry per frame that currently exposes a
              `frame_overview` record.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns contract
                entries across all hosted frames.

        Returns:
            List[Dict[str, str]]: Nexus contract entries in deterministic frame
            order.
        """
        self.check_cleaned()
        contracts: List[Dict[str, str]] = []
        for current_frame_name in self._get_frame_names_for_query(frame_name):
            descriptor = self._get_required_frame_descriptor(current_frame_name)
            frame_overview = descriptor.frame_overview
            if frame_overview is None:
                continue
            contracts.append(
                {
                    "frame_name": current_frame_name,
                    "nexus_label": frame_overview.nexus_label,
                    "nexus_version": frame_overview.nexus_version,
                }
            )
        return contracts

    def count_conduit_records(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> int:
        """
        Return the number of published conduit records.

        Purpose:
            Surface conduit-record inventory at the descriptor host level
            without reaching into conduit payload bodies.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, counts conduit
                records across all hosted frames.

        Returns:
            int: Published conduit-record count.
        """
        self.check_cleaned()
        return len(self.list_conduit_record_ids(frame_name=frame_name))

    def list_conduit_record_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return published conduit record ids for the selected scope.

        Purpose:
            Expose the conduit ids owned by the selected frame descriptor scope
            without surfacing payload details.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns conduit ids
                across all hosted frames.

        Returns:
            List[str]: Conduit ids in deterministic order.
        """
        self.check_cleaned()
        conduit_ids: List[str] = []
        for conduit_record in self._iter_conduit_records(frame_name=frame_name):
            conduit_ids.append(conduit_record.conduit_id)
        return conduit_ids

    def list_root_conduit_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return root conduit ids for the selected descriptor scope.

        Purpose:
            Surface conduit-root topology at the host level using record
            identity only.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns unique root
                conduit ids across all hosted frames.

        Returns:
            List[str]: Deterministically sorted root conduit ids.
        """
        self.check_cleaned()
        root_conduit_ids = {
            conduit_record.root_conduit_id
            for conduit_record in self._iter_conduit_records(frame_name=frame_name)
        }
        return list(sorted(root_conduit_ids))

    def count_spellbooks(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> int:
        """
        Return the number of distinct published origin spellbooks.

        Purpose:
            Surface spellbook provenance breadth at the descriptor host level.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, counts distinct
                spellbook ids across all hosted frames.

        Returns:
            int: Distinct origin spellbook count.
        """
        self.check_cleaned()
        return len(self.list_origin_spellbook_ids(frame_name=frame_name))

    def list_origin_spellbook_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return distinct origin spellbook ids for the selected scope.

        Purpose:
            Expose the spellbook provenance ids attached to the hosted spell
            records.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns distinct
                spellbook ids across all hosted frames.

        Returns:
            List[str]: Distinct spellbook ids in deterministic order.
        """
        self.check_cleaned()
        spellbook_ids = {
            spell_record.origin_spellbook_id
            for spell_record in self._iter_spell_records(frame_name=frame_name)
        }
        return list(sorted(spellbook_ids))

    def list_spell_record_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return published spell record ids for the selected scope.

        Purpose:
            Expose spell ids directly from `SpellRecord` ownership without
            surfacing payload bodies.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns spell ids
                across all hosted frames.

        Returns:
            List[str]: Spell ids in deterministic record order.
        """
        self.check_cleaned()
        spell_ids: List[str] = []
        for spell_record in self._iter_spell_records(frame_name=frame_name):
            spell_ids.append(spell_record.spell_id)
        return spell_ids

    def list_spell_record_keys(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[Tuple[str, str]]:
        """
        Return canonical spell record keys for the selected scope.

        Purpose:
            Surface the exact `(spellbook_id, spell_id)` storage identities
            attached to the selected descriptors.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns record keys
                across all hosted frames.

        Returns:
            List[Tuple[str, str]]: Spell record keys in deterministic order.
        """
        self.check_cleaned()
        record_keys: List[Tuple[str, str]] = []
        for spell_record in self._iter_spell_records(frame_name=frame_name):
            record_keys.append(spell_record.record_key)
        return record_keys

    def list_spell_names(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return published spell names for the selected scope.

        Purpose:
            Expose spell-name inventory directly from `SpellRecord` metadata.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns spell names
                across all hosted frames.

        Returns:
            List[str]: Spell names in deterministic record order.
        """
        self.check_cleaned()
        spell_names: List[str] = []
        for spell_record in self._iter_spell_records(frame_name=frame_name):
            spell_names.append(spell_record.spell_name)
        return spell_names

    def list_binding_names(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return published binding names for the selected scope.

        Purpose:
            Expose the spell binding identities currently represented in the
            hosted descriptors.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns binding names
                across all hosted frames.

        Returns:
            List[str]: Non-empty binding names in deterministic record order.
        """
        self.check_cleaned()
        binding_names: List[str] = []
        for spell_record in self._iter_spell_records(frame_name=frame_name):
            if spell_record.binding_name is None:
                continue
            binding_names.append(spell_record.binding_name)
        return binding_names

    def list_index_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return spell-index ids for the selected descriptor scope.

        Purpose:
            Expose SpellIndex identity directly from `SpellRecord` metadata.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns spell-index ids
                across all hosted frames.

        Returns:
            List[str]: Spell-index ids in deterministic record order.
        """
        self.check_cleaned()
        index_ids: List[str] = []
        for spell_record in self._iter_spell_records(frame_name=frame_name):
            index_ids.append(spell_record.spell_index_id)
        return index_ids

    def list_spellframes(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return normalized spellframe values for the selected scope.

        Purpose:
            Surface the logical spellframe inventory directly from
            `SpellRecord.spellframe` without exposing payload data.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns unique
                spellframe values across all hosted frames.

        Returns:
            List[str]: Distinct normalized spellframe values in deterministic
            order.
        """
        self.check_cleaned()
        spellframes = {
            normalized_spellframe
            for spell_record in self._iter_spell_records(frame_name=frame_name)
            if (
                (normalized_spellframe := self._normalize_spellframe_value(
                    spell_record.spellframe
                )) is not None
            )
        }
        return list(sorted(spellframes))

    def list_permissions(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return distinct spell permission names for the selected scope.

        Purpose:
            Surface the spell permission posture currently represented in the
            hosted descriptors.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns permission
                names across all hosted frames.

        Returns:
            List[str]: Distinct permission names in deterministic order.
        """
        self.check_cleaned()
        permissions = {
            spell_record.permissions.name
            for spell_record in self._iter_spell_records(frame_name=frame_name)
        }
        return list(sorted(permissions))

    def list_existence_kinds(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return distinct spell existence kinds for the selected scope.

        Purpose:
            Surface spell lifetime categories directly from `SpellRecord`
            metadata.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, returns existence
                kinds across all hosted frames.

        Returns:
            List[str]: Distinct existence-kind names in deterministic order.
        """
        self.check_cleaned()
        existence_kinds = {
            spell_record.existence.name
            for spell_record in self._iter_spell_records(frame_name=frame_name)
        }
        return list(sorted(existence_kinds))

    def describe_descriptor_inventory(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return a descriptor-only inventory summary for the selected scope.

        Purpose:
            Give the operator one compact host-level answer to "what descriptors
            do I have here?" without crossing into payload bodies.

        Contract:
            - Uses only `FrameRecord`, `ConduitRecord`, and `SpellRecord`
              identity/provenance fields.
            - May summarize one frame or the entire hosted viewer scope.
            - Does not expose payload body contents.

        Args:
            frame_name:
                Optional hosted frame name. When omitted, summarizes all hosted
                descriptors together.

        Returns:
            Dict[str, object]: Descriptor-only inventory summary.
        """
        self.check_cleaned()
        frame_names = self._get_frame_names_for_query(frame_name)
        return {
            "frame_count": len(frame_names),
            "frame_names": tuple(frame_names),
            "frame_ids": tuple(self.list_frame_ids(frame_name=frame_name)),
            "conduit_record_count": self.count_conduit_records(frame_name=frame_name),
            "root_conduit_ids": tuple(self.list_root_conduit_ids(frame_name=frame_name)),
            "spell_record_count": self.count_spell_records(frame_name=frame_name),
            "origin_spellbook_count": self.count_spellbooks(frame_name=frame_name),
            "origin_spellbook_ids": tuple(
                self.list_origin_spellbook_ids(frame_name=frame_name)
            ),
            "permissions": tuple(self.list_permissions(frame_name=frame_name)),
            "existence_kinds": tuple(
                self.list_existence_kinds(frame_name=frame_name)
            ),
        }

    def describe_descriptor_topology(self, frame_name: str) -> Dict[str, object]:
        """
        Return descriptor-topology groupings for one hosted frame.

        Purpose:
            Surface the descriptor-owned conduit/spell index structure in one
            place so the operator can understand how records are grouped before
            moving into payload-aware helper methods.

        Contract:
            - Uses only descriptor-owned indexes and record identity fields.
            - Does not expose payload body contents.
            - Requires one concrete hosted frame.

        Args:
            frame_name:
                Hosted frame name whose descriptor topology should be
                summarized.

        Returns:
            Dict[str, object]: Descriptor topology summary for the frame.
        """
        self.check_cleaned()
        descriptor = self._get_required_frame_descriptor(frame_name)
        conduit_ids_by_root_id: Dict[str, List[str]] = {}
        for conduit_record in self._iter_conduit_records(frame_name=frame_name):
            conduit_ids_by_root_id.setdefault(
                conduit_record.root_conduit_id,
                [],
            ).append(conduit_record.conduit_id)
        spell_source_ids_by_conduit_id: Dict[str, List[str]] = {}
        for conduit_id, record_keys in descriptor.spell_keys_by_conduit_id.items():
            for record_key in sorted(record_keys):
                spell_record = descriptor.spell_records_by_key[record_key]
                spell_source_ids_by_conduit_id.setdefault(conduit_id, []).append(
                    self._build_spell_source_id(spell_record)
                )
        spell_record_keys_by_spellbook_id: Dict[str, Tuple[Tuple[str, str], ...]] = {
            spellbook_id: tuple(sorted(record_keys))
            for spellbook_id, record_keys in (
                descriptor.spell_keys_by_spellbook_id.items()
            )
        }
        return {
            "frame_name": frame_name,
            "frame_id": (
                descriptor.frame_overview.frame_id
                if descriptor.frame_overview is not None
                else None
            ),
            "root_conduit_ids": tuple(
                sorted(conduit_ids_by_root_id.keys())
            ),
            "conduit_ids_by_root_id": {
                root_conduit_id: tuple(sorted(conduit_ids))
                for root_conduit_id, conduit_ids in conduit_ids_by_root_id.items()
            },
            "spell_source_ids_by_conduit_id": {
                conduit_id: tuple(spell_source_ids)
                for conduit_id, spell_source_ids in (
                    spell_source_ids_by_conduit_id.items()
                )
            },
            "spell_record_keys_by_spellbook_id": spell_record_keys_by_spellbook_id,
        }

    def describe_conduit_records(self, frame_name: str) -> List[Dict[str, object]]:
        """
        Return descriptor-only conduit record descriptions for one frame.

        Purpose:
            Surface the conduit record identities and lineage grouping owned by
            one frame descriptor without exposing conduit payload bodies.

        Args:
            frame_name:
                Hosted frame name whose conduit records should be described.

        Returns:
            List[Dict[str, object]]: Conduit record descriptions.
        """
        self.check_cleaned()
        descriptor = self._get_required_frame_descriptor(frame_name)
        descriptions: List[Dict[str, object]] = []
        for conduit_record in self._iter_conduit_records(frame_name=frame_name):
            owned_spell_keys = descriptor.spell_keys_by_conduit_id.get(
                conduit_record.conduit_id,
                set(),
            )
            descriptions.append(
                {
                    "frame_name": frame_name,
                    "conduit_id": conduit_record.conduit_id,
                    "root_conduit_id": conduit_record.root_conduit_id,
                    "origin_spellbook_id": conduit_record.origin_spellbook_id,
                    "nexus_label": conduit_record.nexus_label,
                    "nexus_version": conduit_record.nexus_version,
                    "is_root_conduit": (
                        conduit_record.conduit_id == conduit_record.root_conduit_id
                    ),
                    "owned_spell_record_count": len(owned_spell_keys),
                }
            )
        return descriptions

    def describe_spell_records(self, frame_name: str) -> List[Dict[str, object]]:
        """
        Return descriptor-only spell record descriptions for one frame.

        Purpose:
            Surface spell record identities and provenance directly from
            `SpellRecord` without crossing into spell payload bodies.

        Args:
            frame_name:
                Hosted frame name whose spell records should be described.

        Returns:
            List[Dict[str, object]]: Spell record descriptions.
        """
        self.check_cleaned()
        return [
            self.describe_spell_record(
                self._build_spell_source_id(spell_record),
                frame_name=frame_name,
            )
            for spell_record in self._iter_spell_records(frame_name=frame_name)
        ]

    def describe_spell_record(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Return one descriptor-only spell record description.

        Purpose:
            Give the operator one exact spell-record view built strictly from
            record identity and provenance fields.

        Contract:
            - Uses only `SpellRecord` fields and normalized spellframe values.
            - Does not expose payload body content.
            - When `frame_name` is omitted, searches the hosted frames for a
              unique matching spell source id.

        Args:
            spell_source_id:
                Published spell source id in `spellbook_id:spell_id` form.
            frame_name:
                Optional hosted frame name to constrain the lookup.

        Returns:
            Dict[str, object]: Descriptor-only spell record description.
        """
        self.check_cleaned()
        resolved_frame_name, spell_record = self._get_required_spell_record(
            spell_source_id,
            frame_name=frame_name,
        )
        return {
            "frame_name": resolved_frame_name,
            "source_id": spell_source_id,
            "record_key": spell_record.record_key,
            "spell_id": spell_record.spell_id,
            "spell_index_id": spell_record.spell_index_id,
            "origin_spellbook_id": spell_record.origin_spellbook_id,
            "owner_conduit_id": spell_record.owner_conduit_id,
            "spell_name": spell_record.spell_name,
            "binding_name": spell_record.binding_name,
            "spellframe": self._normalize_spellframe_value(spell_record.spellframe),
            "permissions": spell_record.permissions.name,
            "existence": spell_record.existence.name,
            "payload_type": spell_record.payload.payload_type,
            "payload_version": spell_record.payload.payload_version,
            "nexus_label": spell_record.nexus_label,
            "nexus_version": spell_record.nexus_version,
        }

    def list_spells_by_owner_conduit(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return spell source ids owned by one conduit.

        Purpose:
            Expose spell ownership at the descriptor host level without
            requiring a payload-aware helper path.

        Args:
            conduit_id:
                Required owner conduit id.
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            List[str]: Matching spell source ids in deterministic order.
        """
        self.check_cleaned()
        if not conduit_id:
            raise ValueError("conduit_id cannot be empty.")
        matching_source_ids: List[str] = []
        for spell_record in self._iter_spell_records(frame_name=frame_name):
            if spell_record.owner_conduit_id == conduit_id:
                matching_source_ids.append(self._build_spell_source_id(spell_record))
        return matching_source_ids

    def list_spells_by_spellbook_id(
            self,
            spellbook_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return spell source ids published by one origin spellbook.

        Args:
            spellbook_id:
                Required origin spellbook id.
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            List[str]: Matching spell source ids in deterministic order.
        """
        self.check_cleaned()
        if not spellbook_id:
            raise ValueError("spellbook_id cannot be empty.")
        matching_source_ids: List[str] = []
        for spell_record in self._iter_spell_records(frame_name=frame_name):
            if spell_record.origin_spellbook_id == spellbook_id:
                matching_source_ids.append(self._build_spell_source_id(spell_record))
        return matching_source_ids

    def list_spells_by_permission(
            self,
            permission: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return spell source ids with one permission posture.

        Args:
            permission:
                Required permission name.
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            List[str]: Matching spell source ids in deterministic order.
        """
        self.check_cleaned()
        if not permission:
            raise ValueError("permission cannot be empty.")
        normalized_permission = permission.lower()
        matching_source_ids: List[str] = []
        for spell_record in self._iter_spell_records(frame_name=frame_name):
            if spell_record.permissions.name.lower() == normalized_permission:
                matching_source_ids.append(self._build_spell_source_id(spell_record))
        return matching_source_ids

    def list_spells_by_existence(
            self,
            existence: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return spell source ids with one existence posture.

        Args:
            existence:
                Required existence-kind name.
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            List[str]: Matching spell source ids in deterministic order.
        """
        self.check_cleaned()
        if not existence:
            raise ValueError("existence cannot be empty.")
        normalized_existence = existence.lower()
        matching_source_ids: List[str] = []
        for spell_record in self._iter_spell_records(frame_name=frame_name):
            if spell_record.existence.name.lower() == normalized_existence:
                matching_source_ids.append(self._build_spell_source_id(spell_record))
        return matching_source_ids

    def list_spells_by_spellframe(
            self,
            spellframe_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return spell source ids with one normalized spellframe value.

        Args:
            spellframe_name:
                Required normalized spellframe name.
            frame_name:
                Optional hosted frame name. When omitted, scans all hosted
                frames.

        Returns:
            List[str]: Matching spell source ids in deterministic order.
        """
        self.check_cleaned()
        if not spellframe_name:
            raise ValueError("spellframe_name cannot be empty.")
        matching_source_ids: List[str] = []
        for spell_record in self._iter_spell_records(frame_name=frame_name):
            normalized_spellframe = self._normalize_spellframe_value(
                spell_record.spellframe
            )
            if normalized_spellframe == spellframe_name:
                matching_source_ids.append(self._build_spell_source_id(spell_record))
        return matching_source_ids
