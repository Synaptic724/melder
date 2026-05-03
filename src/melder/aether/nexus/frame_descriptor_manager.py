import threading
from typing import Any, Dict, List, Optional, Tuple
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.aether.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.nexus.frame_descriptor.conduit_descriptor_payload import (
    ConduitDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.frame_descriptor_payload import (
    FrameDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.spell_descriptor_payload import (
    SpellDescriptorPayload,
)
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.aether.nexus.frame_descriptor.conduit_record import ConduitRecord
from melder.aether.nexus.frame_descriptor.frame_record import FrameRecord
from melder.aether.nexus.frame_descriptor.spell_record import SpellRecord
from melder.utilities.interfaces.interfaces import (
    IAether,
    ISpellGeneralProfile,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameDescriptorManager(Cleanable):
    """
    Purpose:
        Own the Nexus frame-scoped descriptor and canonical-record subsystem.

    Contract:
        - The manager is the sole owner of the
          `frame_name -> FrameDescriptor` registry.
        - It owns posture refresh and publishability checks for passive Nexus
          publication.
        - It owns canonical frame, conduit, and spell record publication and
          removal.
        - It does not own process-wide Rift registry or Nexus configuration
          policy; those remain on `Nexus`.

    Threading:
        Uses one instance `threading.RLock` to serialize multi-step
        descriptor-store mutation and publish/remove flows.

    Lifecycle:
        Cleanup is idempotent and cascades into every owned descriptor before
        the manager drops its registry and substrate reference.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_aether",
        "_frame_descriptors_by_name",
    ]
    _SUPPORTED_NEXUS_RECORD_CONTRACTS = {
        ("default", "0.0.1"),
    }
    _SUPPORTED_FRAME_PAYLOAD_VERSIONS = {
        "0.0.1",
    }
    _SUPPORTED_CONDUIT_PAYLOAD_VERSIONS = {
        "0.0.1",
    }
    _SUPPORTED_SPELL_PAYLOAD_TYPES = {
        "general",
        "detailed",
    }
    _SUPPORTED_SPELL_PAYLOAD_VERSIONS = {
        "0.0.1",
    }

    def __init__(self, aether: IAether) -> None:
        """
        Initialize one frame-scoped Nexus state manager.

        Purpose:
            Bind the manager to the hidden `Aether` substrate and prepare the
            empty descriptor registry.

        Contract:
            - `aether` must be a live substrate reference.
            - Descriptor registry starts empty.

        Args:
            aether:
                Hidden Aether substrate used for frame lookup/creation and
                posture retrieval.

        Returns:
            None.

        Raises:
            TypeError: If `aether` is None.
        """
        super().__init__()
        if aether is None:
            raise TypeError("aether cannot be None.")
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._aether: IAether = aether
        self._frame_descriptors_by_name: Dict[str, FrameDescriptor] = {}

    def cleanup(self) -> None:
        """
        Idempotently cleanup the manager and all owned descriptors.

        Purpose:
            Tear down the descriptor registry and every owned descriptor in one
            deterministic pass.

        Contract:
            - Safe to call more than once.
            - Cleans each descriptor before clearing the registry.
            - Drops the substrate reference after owned teardown completes.

        Threading:
            Acquires the manager lock so cleanup cannot interleave with publish,
            lookup, or record-mutation work.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            for descriptor in self._frame_descriptors_by_name.values():
                descriptor.cleanup()
            self._frame_descriptors_by_name.clear()
            self._frame_descriptors_by_name = None
            self._aether = None
        self._lock = None

    def _refresh_frame_posture_cache(
            self,
            frame_name: str,
    ) -> Optional[AethericFrameConfiguration]:
        """
        Refresh cached frame posture from Aether for one frame.

        Purpose:
            Synchronize the descriptor's cached frame posture and live frame
            handle from the hidden substrate.

        Contract:
            - Ensures a descriptor exists for the frame name.
            - Clears cached posture/handle when the frame or posture is absent.
            - Attempts to refresh the runtime frame handle opportunistically
              after posture resolution.

        Args:
            frame_name:
                Stable frame name whose posture cache should be refreshed.

        Returns:
            Optional[AethericFrameConfiguration]:
                Bound frame posture when available, otherwise None.
        """
        self.check_cleaned()
        descriptor = self._get_or_create_frame_descriptor(frame_name)
        try:
            frame_posture = self._aether._get_aetheric_frame_configuration(frame_name)
        except ValueError:
            descriptor.set_frame_configuration(None)
            descriptor.set_frame_handle(None)
            return None

        if frame_posture is None:
            descriptor.set_frame_configuration(None)
            return None

        descriptor.set_frame_configuration(frame_posture)
        try:
            descriptor.set_frame_handle(self._aether._ensure_frame(frame_name))
        except Exception:
            descriptor.set_frame_handle(None)
        return frame_posture

    def _get_publishable_frame_posture(
            self,
            frame_name: str,
    ) -> Optional[AethericFrameConfiguration]:
        """
        Return a frame posture only when passive Nexus publication is allowed.

        Purpose:
            Centralize the passive-publication gate for frame-scoped canonical
            record publication.

        Contract:
            - Returns None when no frame posture is available.
            - Returns None when the frame exists but is not Rift-enabled.
            - Returns the cached/refreshed posture only when passive publication
              is allowed.

        Args:
            frame_name:
                Stable frame name whose passive-publication posture is needed.

        Returns:
            Optional[AethericFrameConfiguration]:
                Publishable frame posture or None when publication should
                short-circuit.
        """
        self.check_cleaned()
        descriptor = self._get_or_create_frame_descriptor(frame_name)
        frame_posture = descriptor.frame_configuration
        if frame_posture is None:
            frame_posture = self._refresh_frame_posture_cache(frame_name)
        if frame_posture is None:
            return None
        if not frame_posture.rift_enabled:
            return None
        return frame_posture

    def _publish_frame_record(self, spellbook: Any) -> bool:
        """
        Publish or update one canonical frame record.

        Purpose:
            Build or refresh the canonical `FrameRecord` summary for one
            Spellbook-owning frame.

        Contract:
            - Short-circuits when the frame is not publishable.
            - Refreshes descriptor frame handle and posture before publishing.
            - Replaces the owned frame overview record on the descriptor.

        Args:
            spellbook:
                Spellbook whose owning frame should be summarized.

        Returns:
            bool:
                True when publication occurred, False when the frame is not
                publishable.
        """
        self.check_cleaned()
        frame_name = spellbook._aetheric_frame
        with self._lock:
            frame_posture = self._get_publishable_frame_posture(frame_name)
            if frame_posture is None:
                return False

            frame = self._aether._ensure_frame(frame_name)
            descriptor = self._get_or_create_frame_descriptor(frame_name)
            descriptor.set_frame_handle(frame)
            descriptor.set_frame_configuration(frame_posture)
            with frame:
                root_conduit_ids = tuple(sorted(frame._conduits.keys()))
                named_root_conduits = tuple(
                    sorted(
                        (conduit._id, conduit._name)
                        for conduit in frame._conduits.values()
                        if conduit is not None and conduit._name is not None
                    )
                )
                conduit_cloud_names = tuple()
                conduit_cloud_entry_count = 0
                if frame._conduit_cloud is not None:
                    conduit_cloud_names = tuple(
                        sorted(frame._conduit_cloud._registry.keys())
                    )
                    conduit_cloud_entry_count = len(conduit_cloud_names)
                cluster_names = tuple()
                cluster_count = 0
                if frame._conduit_clusters is not None:
                    cluster_names = tuple(sorted(frame._conduit_clusters.keys()))
                    cluster_count = len(cluster_names)
            payload = FrameDescriptorPayload(
                system_state=frame_posture.system_state,
                ai_native_enabled=frame_posture.ai_native_enabled,
                rift_enabled=frame_posture.rift_enabled,
                root_conduit_count=len(root_conduit_ids),
                root_conduit_ids=root_conduit_ids,
                named_root_conduits=named_root_conduits,
                conduit_cloud_entry_count=conduit_cloud_entry_count,
                conduit_cloud_names=conduit_cloud_names,
                cluster_count=cluster_count,
                cluster_names=cluster_names,
            )
            self._validate_published_frame_payload(payload)
            frame_record = FrameRecord(
                frame_name=frame_name,
                frame_id=frame._id,
                config_origin_spellbook_id=spellbook._id,
                payload=payload,
            )
            self._validate_published_record_contract(
                nexus_label=frame_record.nexus_label,
                nexus_version=frame_record.nexus_version,
                label="frame record",
            )
            descriptor.set_frame_overview(frame_record)
            return True

    def _publish_conduit_record(self, conduit: Any) -> bool:
        """
        Publish or update one canonical conduit record.

        Purpose:
            Build or refresh the canonical `ConduitRecord` for one normal
            conduit.

        Contract:
            - Published conduit states in this slice are normal and lesser.
            - Short-circuits when the frame is not publishable.
            - Replaces the descriptor-owned conduit record for the conduit id.

        Args:
            conduit:
                Conduit instance to publish.

        Returns:
            bool:
                True when publication occurred, False when the conduit is not
                eligible.
        """
        self.check_cleaned()
        if conduit is None or conduit._conduit_state not in (
                ConduitState.normal,
                ConduitState.lesser,
        ):
            return False

        frame_name = conduit._aetheric_frame
        with self._lock:
            frame_posture = self._get_publishable_frame_posture(frame_name)
            if frame_posture is None:
                return False
            descriptor = self._get_or_create_frame_descriptor(frame_name)

            peer_conduit_ids = tuple(
                sorted(
                    peer._id
                    for peer in conduit._conduit_ward._get_links()
                    if peer is not None
                )
            )
            origin_spellbook_id = None
            if conduit._spellbook is not None:
                origin_spellbook_id = conduit._spellbook._id
            parent_conduit_id = self._resolve_parent_conduit_id(conduit)
            lineage_depth = self._compute_lineage_depth(conduit)

            payload = ConduitDescriptorPayload(
                conduit_name=conduit._name,
                conduit_state=conduit._conduit_state,
                policy=conduit._conduit_ward._policy,
                peer_conduit_ids=peer_conduit_ids,
                parent_conduit_id=parent_conduit_id,
                lineage_depth=lineage_depth,
            )
            self._validate_published_conduit_payload(payload)
            conduit_record = ConduitRecord(
                conduit_id=conduit._id,
                root_conduit_id=conduit._root_conduit_id,
                frame_name=frame_name,
                origin_spellbook_id=origin_spellbook_id,
                payload=payload,
            )
            self._validate_published_record_contract(
                nexus_label=conduit_record.nexus_label,
                nexus_version=conduit_record.nexus_version,
                label="conduit record",
            )
            descriptor.upsert_conduit_record(conduit_record)
            return True

    @staticmethod
    def _resolve_parent_conduit_id(conduit: Any) -> Optional[str]:
        """
        Resolve the published parent conduit id for one conduit.

        Args:
            conduit:
                Conduit-like object being published.

        Returns:
            Optional[str]: Parent conduit id when present; otherwise None.
        """
        conduit_ward = conduit._conduit_ward
        if conduit_ward is None:
            return None
        parent_conduit = conduit_ward._parent_conduit
        if parent_conduit is None:
            return None
        return parent_conduit._id

    @classmethod
    def _compute_lineage_depth(cls, conduit: Any) -> int:
        """
        Compute zero-based lineage depth for one conduit.

        Args:
            conduit:
                Conduit-like object being published.

        Returns:
            int: Zero-based lineage depth from the published conduit to the
            lineage root.
        """
        conduit_ward = conduit._conduit_ward
        if conduit_ward is None:
            return 0
        depth = 0
        parent_conduit = conduit_ward._parent_conduit
        while parent_conduit is not None:
            depth += 1
            parent_conduit_ward = parent_conduit._conduit_ward
            if parent_conduit_ward is None:
                break
            parent_conduit = parent_conduit_ward._parent_conduit
        return depth

    def _remove_conduit_record(
            self,
            conduit_id: str,
            frame_name: str,
    ) -> bool:
        """
        Remove one canonical conduit record.

        Purpose:
            Remove a descriptor-owned conduit record for a publishable frame.

        Args:
            conduit_id:
                Conduit id whose record should be removed.
            frame_name:
                Stable frame name that owns the descriptor.

        Returns:
            bool:
                True when removal occurred, False when the frame is not
                publishable.
        """
        self.check_cleaned()
        with self._lock:
            frame_posture = self._get_publishable_frame_posture(frame_name)
            if frame_posture is None:
                return False
            descriptor = self._get_or_create_frame_descriptor(frame_name)
            descriptor.remove_conduit_record(conduit_id)
            return True

    def _publish_spell_record(
            self,
            spellbook: Any,
            spell: Any,
            owner_conduit_id: Optional[str],
    ) -> bool:
        """
        Publish or update one canonical spell record.

        Purpose:
            Build or refresh the canonical `SpellRecord` for one spell owned by
            a Spellbook/frame pair.

        Contract:
            - Short-circuits when the frame is not publishable.
            - Preserves the existing AI-profile extraction behavior.
            - Replaces the descriptor-owned spell record for the canonical key.

        Args:
            spellbook:
                Owning Spellbook.
            spell:
                Spell instance to publish.
            owner_conduit_id:
                Owning conduit id when known; otherwise None.

        Returns:
            bool:
                True when publication occurred, False when the frame is not
                publishable.
        """
        self.check_cleaned()
        frame_name = spellbook._aetheric_frame
        with self._lock:
            frame_posture = self._get_publishable_frame_posture(frame_name)
            if frame_posture is None:
                return False
            descriptor = self._get_or_create_frame_descriptor(frame_name)

            profile = spell.profile
            payload: Optional[SpellDescriptorPayload] = None
            if isinstance(profile, ISpellGeneralProfile):
                payload = profile.to_descriptor_payload()
            if payload is None:
                raise RuntimeError(
                    "Spell publication requires a non-empty descriptor payload."
                )
            self._validate_published_spell_payload(payload)

            spell_record = SpellRecord(
                origin_spellbook_id=spellbook._id,
                frame_name=frame_name,
                owner_conduit_id=owner_conduit_id,
                spell_id=spell.spell_id,
                spell_index_id=spell.spell_index.id,
                spell_name=spell.spell_name,
                spellframe=spell.spellframe,
                binding_name=spell.binding_name,
                permissions=spell.permissions,
                existence=spell.existence,
                payload=payload,
            )
            self._validate_published_record_contract(
                nexus_label=spell_record.nexus_label,
                nexus_version=spell_record.nexus_version,
                label="spell record",
            )
            descriptor.upsert_spell_record(spell_record)
            return True

    def _remove_spell_record(
            self,
            origin_spellbook_id: str,
            spell_id: str,
            frame_name: str,
    ) -> bool:
        """
        Remove one canonical spell record by composite key.

        Purpose:
            Remove a descriptor-owned `SpellRecord` for a publishable frame.

        Args:
            origin_spellbook_id:
                Owning Spellbook id.
            spell_id:
                Current spell/version id.
            frame_name:
                Stable frame name that owns the descriptor.

        Returns:
            bool:
                True when removal occurred, False when the frame is not
                publishable.
        """
        self.check_cleaned()
        with self._lock:
            frame_posture = self._get_publishable_frame_posture(frame_name)
            if frame_posture is None:
                return False
            descriptor = self._get_or_create_frame_descriptor(frame_name)
            descriptor.remove_spell_record((origin_spellbook_id, spell_id))
            return True

    def _get_required_frame_descriptor(
            self,
            frame_name: str,
    ) -> FrameDescriptor:
        """
        Return one existing frame descriptor or raise.

        Purpose:
            Resolve a descriptor only when absence is a real invariant break.

        Args:
            frame_name:
                Stable frame name to resolve.

        Returns:
            FrameDescriptor:
                Existing descriptor for the frame.

        Raises:
            KeyError:
                If the frame has no descriptor yet.
        """
        self.check_cleaned()
        with self._lock:
            try:
                return self._frame_descriptors_by_name[frame_name]
            except KeyError as exc:
                raise KeyError(frame_name) from exc

    def _get_or_create_frame_descriptor(
            self,
            frame_name: str,
    ) -> FrameDescriptor:
        """
        Return one existing frame descriptor or create it.

        Purpose:
            Provide the canonical descriptor lookup/creation path for the
            frame-scoped store.

        Contract:
            - Creates at most one descriptor per frame name.
            - Reuses the existing descriptor when present.

        Args:
            frame_name:
                Frame name to resolve.

        Returns:
            FrameDescriptor:
                Existing or newly created descriptor.
        """
        self.check_cleaned()
        with self._lock:
            descriptor = self._frame_descriptors_by_name.get(frame_name)
            if descriptor is None:
                descriptor = FrameDescriptor(frame_name)
                self._frame_descriptors_by_name[frame_name] = descriptor
            return descriptor

    def _has_frame_descriptor(self, frame_name: str) -> bool:
        """
        Return whether a descriptor currently exists for the given frame name.

        Purpose:
            Provide a lightweight existence check for the descriptor registry.

        Args:
            frame_name:
                Frame name to inspect.

        Contract:
            Performs an existence check only; it does not create a descriptor
            on demand.

        Returns:
            bool: True when a descriptor exists for the frame.
        """
        self.check_cleaned()
        with self._lock:
            return frame_name in self._frame_descriptors_by_name

    def list_published_frame_names(self) -> Tuple[str, ...]:
        """
        Return the currently published frame names in sorted order.

        Purpose:
            Expose a detached snapshot of frame names whose descriptors still
            own published frame-overview state.

        Returns:
            Tuple[str, ...]: Sorted published frame names.
        """
        self.check_cleaned()
        with self._lock:
            return tuple(
                sorted(
                    frame_name
                    for frame_name, descriptor in self._frame_descriptors_by_name.items()
                    if descriptor.frame_overview is not None
                )
            )

    @classmethod
    def _validate_published_frame_payload(
            cls,
            payload: FrameDescriptorPayload,
    ) -> None:
        """
        Validate one published frame payload contract before descriptor ingest.

        Args:
            payload:
                Published frame descriptor payload.

        Returns:
            None.
        """
        if payload.payload_version not in cls._SUPPORTED_FRAME_PAYLOAD_VERSIONS:
            raise ValueError(
                "Unsupported frame descriptor payload version '{0}'.".format(
                    payload.payload_version,
                )
            )

    @classmethod
    def _validate_published_conduit_payload(
            cls,
            payload: ConduitDescriptorPayload,
    ) -> None:
        """
        Validate one published conduit payload contract before descriptor ingest.

        Args:
            payload:
                Published conduit descriptor payload.

        Returns:
            None.
        """
        if payload.payload_version not in cls._SUPPORTED_CONDUIT_PAYLOAD_VERSIONS:
            raise ValueError(
                "Unsupported conduit descriptor payload version '{0}'.".format(
                    payload.payload_version,
                )
            )

    @classmethod
    def _validate_published_spell_payload(
            cls,
            payload: SpellDescriptorPayload,
    ) -> None:
        """
        Validate one published spell payload contract before descriptor ingest.

        Args:
            payload:
                Published spell descriptor payload.

        Returns:
            None.
        """
        if payload.payload_type not in cls._SUPPORTED_SPELL_PAYLOAD_TYPES:
            raise ValueError(
                "Unsupported spell descriptor payload type '{0}'.".format(
                    payload.payload_type,
                )
            )
        if payload.payload_version not in cls._SUPPORTED_SPELL_PAYLOAD_VERSIONS:
            raise ValueError(
                "Unsupported spell descriptor payload version '{0}'.".format(
                    payload.payload_version,
                )
            )

    @classmethod
    def _validate_published_record_contract(
            cls,
            *,
            nexus_label: str,
            nexus_version: str,
            label: str,
    ) -> None:
        """
        Validate one published record/event contract before descriptor ingest.

        Args:
            nexus_label:
                Published Nexus dataset label.
            nexus_version:
                Published Nexus dataset version.
            label:
                Human-readable record label.

        Returns:
            None.
        """
        if (nexus_label, nexus_version) not in cls._SUPPORTED_NEXUS_RECORD_CONTRACTS:
            raise ValueError(
                "Unsupported {0} Nexus contract '{1}:{2}'.".format(
                    label,
                    nexus_label,
                    nexus_version,
                )
            )
