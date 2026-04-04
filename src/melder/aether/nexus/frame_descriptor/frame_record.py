from typing import Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.spellbook.configuration.system_state import SystemState
from melder.utilities.general_base.cleanable import Cleanable


class FrameRecord(Cleanable):
    """
    Internal

    Canonical Nexus record for one AR-publishable frame.

    Purpose:
        Hold the frame-level posture Nexus needs to reason about one frame as a
        publishable AR/Rift source without depending on the richer shared
        Spellbook configuration object.

    Contract:
        - One record per frame name.
        - Carries only the current frame-level posture needed for the first
          passive-ingest slice.
        - Mutable through explicit Nexus upsert paths only.
        - Cleanup is idempotent and clears all owned references.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "frame_name",
        "frame_id",
        "config_origin_spellbook_id",
        "system_state",
        "ai_native_enabled",
        "rift_enabled",
        "root_conduit_count",
        "root_conduit_ids",
        "named_root_conduits",
        "conduit_cloud_entry_count",
        "conduit_cloud_names",
        "cluster_count",
        "cluster_names",
    ]

    def __init__(
            self,
            *,
            frame_name: str,
            frame_id: str,
            config_origin_spellbook_id: Optional[str],
            system_state: SystemState,
            ai_native_enabled: bool,
            rift_enabled: bool,
            root_conduit_count: int,
            root_conduit_ids: Tuple[str, ...],
            named_root_conduits: Tuple[Tuple[str, str], ...],
            conduit_cloud_entry_count: int,
            conduit_cloud_names: Tuple[str, ...],
            cluster_count: int,
            cluster_names: Tuple[str, ...],
    ) -> None:
        """
        Initialize one canonical frame record.

        Args:
            frame_name:
                Stable frame name.
            frame_id:
                Stable runtime frame id.
            config_origin_spellbook_id:
                Spellbook id that originally established the bound frame
                posture/config path when known.
            system_state:
                Current frame system state.
            ai_native_enabled:
                Whether AI-native posture is enabled for the frame.
            rift_enabled:
                Whether the frame is eligible for passive Nexus publication and
                later Rift-facing interaction.
            root_conduit_count:
                Count of root conduits currently registered in the frame.
            root_conduit_ids:
                Sorted tuple of root conduit ids currently registered.
            named_root_conduits:
                Sorted tuple of `(conduit_id, conduit_name)` for currently
                named root conduits.
            conduit_cloud_entry_count:
                Count of currently registered conduit-cloud entries.
            conduit_cloud_names:
                Sorted tuple of conduit-cloud entry names.
            cluster_count:
                Count of conduit clusters currently registered in the frame.
            cluster_names:
                Sorted tuple of cluster names currently registered in the frame.
        """
        super().__init__()
        self.frame_name = frame_name
        self.frame_id = frame_id
        self.config_origin_spellbook_id = config_origin_spellbook_id
        self.system_state = system_state
        self.ai_native_enabled = ai_native_enabled
        self.rift_enabled = rift_enabled
        self.root_conduit_count = root_conduit_count
        self.root_conduit_ids = root_conduit_ids
        self.named_root_conduits = named_root_conduits
        self.conduit_cloud_entry_count = conduit_cloud_entry_count
        self.conduit_cloud_names = conduit_cloud_names
        self.cluster_count = cluster_count
        self.cluster_names = cluster_names

    def cleanup(self) -> None:
        """
        Idempotently clear the record.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self.frame_name = None
        self.frame_id = None
        self.config_origin_spellbook_id = None
        self.system_state = None
        self.ai_native_enabled = None
        self.rift_enabled = None
        self.root_conduit_count = None
        self.root_conduit_ids = None
        self.named_root_conduits = None
        self.conduit_cloud_entry_count = None
        self.conduit_cloud_names = None
        self.cluster_count = None
        self.cluster_names = None
