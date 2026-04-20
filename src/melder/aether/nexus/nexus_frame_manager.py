import threading
from typing import Any, Dict, List, Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.nexus.frame_descriptor.frame_descriptor_payload import (
    FrameDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.frame_record import FrameRecord
from melder.aether.nexus.nexus_frame_builder import NexusFrameBuilder
from melder.aether.nexus.nexus_frame_configuration import NexusFrameConfiguration
from melder.aether.nexus.nexus_frame_record import NexusFrameRecord
from melder.spellbook.configuration.system_state import SystemState
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class NexusFrameManager(Cleanable):
    """
    Authoring and topology facade for Nexus-managed frames.

    Purpose:
        Centralize frame authoring, empty-frame initialization, optional root
        conduit bootstrap, and topology-aware frame access above the lower
        `Aether`, descriptor, and ACL subsystems.

    Contract:
        - Holds the authoritative Nexus-managed frame registry as
          `frame_name -> IAethericFrame`.
        - Holds the authored frame configuration registry as
          `frame_name -> NexusFrameConfiguration`.
        - Treats `Aether` as the real frame owner and disposal executor.
        - Exposes Rift-aware topology methods for `single`, `indexed`, and
          `one_per_workspace`.
        - Does not own a persistent attachment registry; it derives removal and
          access safety from current Nexus/Rift state when needed.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_nexus",
        "_frames_by_name",
        "_configurations_by_frame_name",
    ]

    def __init__(self, *, nexus: Any) -> None:
        """
        Initialize one Nexus frame-authoring facade.

        Args:
            nexus:
                Owning `Nexus` facade.

        Returns:
            None.
        """
        super().__init__()
        if nexus is None:
            raise TypeError("nexus cannot be None.")
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._nexus = nexus
        self._frames_by_name: Dict[str, Any] = {}
        self._configurations_by_frame_name: Dict[str, NexusFrameConfiguration] = {}

    def cleanup(self) -> None:
        """
        Idempotently clear manager-owned registry state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._frames_by_name.clear()
            for configuration in self._configurations_by_frame_name.values():
                configuration.cleanup()
            self._configurations_by_frame_name.clear()
            self._frames_by_name = None
            self._configurations_by_frame_name = None
            self._nexus = None
            self._id = None
        self._lock = None

    @property
    def id(self) -> str:
        """Return the stable manager id."""
        self.check_cleaned()
        return self._id

    def begin(self, frame_name: str) -> NexusFrameBuilder:
        """
        Begin one fluent authored-frame build.

        Args:
            frame_name:
                Stable authored frame name.

        Returns:
            NexusFrameBuilder: Fluent builder scoped to the frame name.
        """
        self.check_cleaned()
        return NexusFrameBuilder(manager=self, frame_name=frame_name)

    def exists(self, frame_name: str) -> bool:
        """
        Return whether the manager currently tracks a frame name.

        Args:
            frame_name:
                Frame name to check.

        Returns:
            bool: True when the frame is currently managed.
        """
        self.check_cleaned()
        with self._lock:
            return frame_name in self._frames_by_name

    def list_frame_names(self) -> Tuple[str, ...]:
        """
        Return the currently managed frame names in sorted order.

        Returns:
            Tuple[str, ...]: Managed frame names.
        """
        self.check_cleaned()
        with self._lock:
            return tuple(sorted(self._frames_by_name.keys()))

    def create_dynamic_frame(
            self,
            frame_name: str,
            *,
            immutable: bool = False,
            metadata: Optional[Dict[str, object]] = None,
            root_conduit_name: Optional[str] = None,
            creator_rift_id: Optional[str] = None,
    ) -> Any:
        """
        Create one dynamic Nexus-managed frame directly.

        Returns:
            IAethericFrame: Managed frame.
        """
        return self.create(
            NexusFrameConfiguration.create_dynamic_defaults(
                frame_name,
                immutable=immutable,
                metadata=metadata,
                root_conduit_name=root_conduit_name,
            ),
            creator_rift_id=creator_rift_id,
        )

    def create_automatic_frame(
            self,
            frame_name: str,
            *,
            immutable: bool = False,
            metadata: Optional[Dict[str, object]] = None,
            root_conduit_name: Optional[str] = None,
            creator_rift_id: Optional[str] = None,
    ) -> Any:
        """
        Create one automatic Nexus-managed frame directly.

        Returns:
            IAethericFrame: Managed frame.
        """
        return self.create(
            NexusFrameConfiguration.create_automatic_defaults(
                frame_name,
                immutable=immutable,
                metadata=metadata,
                root_conduit_name=root_conduit_name,
            ),
            creator_rift_id=creator_rift_id,
        )

    def create(
            self,
            configuration: NexusFrameConfiguration,
            *,
            creator_rift_id: Optional[str] = None,
    ) -> Any:
        """
        Create one managed frame from authored configuration.

        Args:
            configuration:
                Authored frame configuration.
            creator_rift_id:
                Optional creating Rift id when this is a Rift/topology-driven
                creation path.

        Returns:
            IAethericFrame: Realized managed frame.
        """
        self.check_cleaned()
        if not isinstance(configuration, NexusFrameConfiguration):
            raise TypeError(
                "configuration must be a NexusFrameConfiguration."
            )
        frame_name = configuration.frame_name
        with self._lock:
            existing_frame = self._frames_by_name.get(frame_name)
            if existing_frame is not None:
                raise ValueError(
                    "Nexus managed frame '{0}' already exists.".format(frame_name)
                )
            self._nexus._validate_nexus_frame_budget((frame_name,))
            frame = self._nexus._aether._ensure_frame(frame_name)
            self._frames_by_name[frame_name] = frame
            self._configurations_by_frame_name[frame_name] = configuration

        spellbook_configuration = configuration.to_spellbook_configuration()
        self._nexus._aether._bind_configuration(
            spellbook_configuration,
            frame_name,
        )
        frame_configuration = configuration.to_aetheric_frame_configuration()
        self._nexus._aether._bind_aetheric_frame_configuration(
            frame_configuration,
            frame_name,
        )
        self._ensure_descriptor_and_acl(frame_name)
        if creator_rift_id is not None:
            self._mirror_legacy_nexus_frame_record(
                frame_name,
                frame,
                creator_rift_id=creator_rift_id,
                immutable=configuration.immutable,
            )
        self._publish_frame_overview(
            frame_name,
            config_origin_spellbook_id=None,
        )
        if configuration.root_conduit_name is not None:
            self._bootstrap_root_conduit(
                frame_name,
                configuration,
                configuration.root_conduit_name,
            )
        return frame

    def remove(self, frame_name: str) -> None:
        """
        Remove one authored Nexus-managed frame.

        Args:
            frame_name:
                Managed frame name to remove.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            frame = self._frames_by_name.get(frame_name)
            if frame is None:
                raise ValueError(
                    "Nexus managed frame '{0}' was not found.".format(frame_name)
                )
            configuration = self._configurations_by_frame_name[frame_name]
            if configuration.immutable:
                raise ValueError(
                    "Nexus managed frame '{0}' is immutable.".format(frame_name)
                )
        if self._frame_is_in_active_rift_use(frame_name):
            raise ValueError(
                "Nexus managed frame '{0}' is still in active Rift use.".format(
                    frame_name
                )
            )
        frame.cleanup()

    def get_frame_for_rift(
            self,
            rift_id: str,
            frame_name: Optional[str] = None,
    ) -> Any:
        """
        Return one manager-owned frame for a Rift under the current topology.

        Args:
            rift_id:
                Requesting Rift id.
            frame_name:
                Optional explicit frame name.

        Returns:
            IAethericFrame: Resolved managed frame.
        """
        self.check_cleaned()
        self._nexus._require_enabled()
        with self._lock:
            requested_frame_name = self._resolve_frame_name_for_rift(
                rift_id,
                frame_name=frame_name,
                allow_creation=False,
            )
            try:
                return self._frames_by_name[requested_frame_name]
            except KeyError as exc:
                raise ValueError(
                    "Nexus managed frame '{0}' was not found.".format(
                        requested_frame_name
                    )
                ) from exc

    def create_frame_for_rift(
            self,
            rift_id: str,
            frame_name: Optional[str] = None,
            immutable: bool = False,
    ) -> Any:
        """
        Create or recover one managed frame for a Rift under current topology.

        Args:
            rift_id:
                Requesting Rift id.
            frame_name:
                Optional explicit frame name.
            immutable:
                Immutable flag for newly created frames.

        Returns:
            IAethericFrame: Created or recovered managed frame.
        """
        self.check_cleaned()
        self._nexus._require_enabled()
        requested_frame_name = self._resolve_frame_name_for_rift(
            rift_id,
            frame_name=frame_name,
            allow_creation=True,
        )
        nexus_frame_mode = self._nexus._configuration.get_property("nexus_frame_mode")
        if nexus_frame_mode.name == "one_per_workspace" and immutable:
            raise ValueError("one_per_workspace frames cannot be immutable.")
        with self._lock:
            existing_frame = self._frames_by_name.get(requested_frame_name)
            if existing_frame is not None:
                return existing_frame
        return self.create_dynamic_frame(
            requested_frame_name,
            immutable=immutable,
            creator_rift_id=rift_id,
        )

    def list_accessible_frame_names_for_rift(self, rift_id: str) -> Tuple[str, ...]:
        """
        Return the manager-owned frame names accessible to one Rift.

        Args:
            rift_id:
                Requesting Rift id.

        Returns:
            Tuple[str, ...]: Accessible managed frame names.
        """
        self.check_cleaned()
        self._nexus._require_enabled()
        self._nexus._get_required_rift(rift_id)
        with self._lock:
            nexus_frame_mode = self._nexus._configuration.get_property(
                "nexus_frame_mode"
            )
            if nexus_frame_mode.name == "single":
                shared_frame_name = self._nexus._configuration.get_property(
                    "default_nexus_frame_name"
                )
                if shared_frame_name in self._frames_by_name:
                    return (shared_frame_name,)
                return tuple()
            if nexus_frame_mode.name == "one_per_workspace":
                private_frame_name = self._determine_frame_name_for_rift(rift_id)
                if private_frame_name in self._frames_by_name:
                    return (private_frame_name,)
                return tuple()
            return tuple(sorted(self._frames_by_name.keys()))

    def get_frame_names_to_cleanup_for_removed_rift(
            self,
            rift_id: str,
    ) -> List[str]:
        """
        Return the authored frame names that should be disposed after Rift removal.

        Args:
            rift_id:
                Removed Rift id.

        Returns:
            List[str]: Frame names to dispose.
        """
        self.check_cleaned()
        with self._lock:
            nexus_frame_mode = self._nexus._configuration.get_property(
                "nexus_frame_mode"
            )
            if nexus_frame_mode.name == "single":
                if len(self._nexus._rifts_by_id) != 0:
                    return []
                shared_frame_name = self._nexus._configuration.get_property(
                    "default_nexus_frame_name"
                )
                configuration = self._configurations_by_frame_name.get(
                    shared_frame_name
                )
                if shared_frame_name not in self._frames_by_name:
                    return []
                if configuration is not None and configuration.immutable:
                    return []
                return [shared_frame_name]
            if nexus_frame_mode.name == "one_per_workspace":
                private_frame_name = self._determine_frame_name_for_rift(rift_id)
                configuration = self._configurations_by_frame_name.get(
                    private_frame_name
                )
                if private_frame_name not in self._frames_by_name:
                    return []
                if configuration is not None and configuration.immutable:
                    return []
                return [private_frame_name]
            return []

    def handle_aether_frame_disposal(self, frame_name: str) -> bool:
        """
        Drop manager-owned authored state after external Aether frame disposal.

        Args:
            frame_name:
                Disposed frame name.

        Returns:
            bool: True when the frame had manager-owned state.
        """
        self.check_cleaned()
        with self._lock:
            frame = self._frames_by_name.pop(frame_name, None)
            configuration = self._configurations_by_frame_name.pop(
                frame_name,
                None,
            )
        if frame is None and configuration is None:
            return False
        if configuration is not None and not configuration.cleaned:
            configuration.cleanup()
        if self._nexus._frame_descriptor_manager._has_frame_descriptor(frame_name):
            descriptor = self._nexus._frame_descriptor_manager._get_required_frame_descriptor(
                frame_name
            )
            descriptor.set_frame_handle(None)
            descriptor.set_frame_configuration(None)
            descriptor.set_frame_overview(None)
            descriptor.set_nexus_frame_record(None)
        self._nexus._frame_acl_manager._remove_frame_acl_container(frame_name)
        return True

    def _determine_frame_name_for_rift(self, rift_id: str) -> str:
        """
        Determine the manager-owned frame name for one Rift.

        Args:
            rift_id:
                Requesting Rift id.

        Returns:
            str: Derived managed frame name.
        """
        default_nexus_frame_name = self._nexus._configuration.get_property(
            "default_nexus_frame_name"
        )
        return "{0}:{1}".format(default_nexus_frame_name, rift_id)

    def _resolve_frame_name_for_rift(
            self,
            rift_id: str,
            *,
            frame_name: Optional[str],
            allow_creation: bool,
    ) -> str:
        """
        Resolve one frame name for a Rift under the current topology.

        Args:
            rift_id:
                Requesting Rift id.
            frame_name:
                Optional explicit frame name.
            allow_creation:
                True when the resolution path is a create-or-recover path.

        Returns:
            str: Resolved managed frame name.
        """
        self._nexus._get_required_rift(rift_id)
        nexus_frame_mode = self._nexus._configuration.get_property(
            "nexus_frame_mode"
        )
        if nexus_frame_mode.name == "single":
            shared_frame_name = self._nexus._configuration.get_property(
                "default_nexus_frame_name"
            )
            requested_frame_name = frame_name or shared_frame_name
            if requested_frame_name != shared_frame_name:
                raise ValueError(
                    "Shared Nexus mode only exposes the shared frame."
                )
            return requested_frame_name
        if nexus_frame_mode.name == "one_per_workspace":
            private_frame_name = frame_name or self._determine_frame_name_for_rift(
                rift_id
            )
            if private_frame_name != self._determine_frame_name_for_rift(rift_id):
                raise ValueError(
                    "Rift can only access its own private Nexus frame."
                )
            return private_frame_name
        if frame_name is None:
            if allow_creation:
                return self._allocate_indexed_frame_name()
            raise ValueError(
                "Indexed Nexus mode requires an explicit frame_name for access."
            )
        return frame_name

    def _allocate_indexed_frame_name(self) -> str:
        indexed_frame_name = "{0}-{1}".format(
            self._nexus._configuration.get_property("default_nexus_frame_name"),
            self._nexus._next_indexed_nexus_frame_number,
        )
        self._nexus._next_indexed_nexus_frame_number = (
            self._nexus._next_indexed_nexus_frame_number + 1
        )
        return indexed_frame_name

    def _ensure_descriptor_and_acl(self, frame_name: str) -> None:
        descriptor = self._nexus._frame_descriptor_manager._get_or_create_frame_descriptor(
            frame_name
        )
        frame = self._frames_by_name[frame_name]
        frame_configuration = self._nexus._aether._get_aetheric_frame_configuration(
            frame_name
        )
        descriptor.set_frame_handle(frame)
        descriptor.set_frame_configuration(frame_configuration)
        self._nexus._ensure_frame_acl_container(frame_name)

    def _publish_frame_overview(
            self,
            frame_name: str,
            *,
            config_origin_spellbook_id: Optional[str],
    ) -> None:
        frame = self._frames_by_name[frame_name]
        frame_configuration = self._nexus._aether._get_aetheric_frame_configuration(
            frame_name
        )
        descriptor = self._nexus._frame_descriptor_manager._get_or_create_frame_descriptor(
            frame_name
        )
        root_conduit_ids = tuple(sorted(frame._conduits.keys()))
        named_root_conduits = tuple(
            sorted(
                (conduit._id, conduit._name)
                for conduit in frame._conduits.values()
                if conduit is not None and conduit._name is not None
            )
        )
        conduit_cloud_names = tuple(
            sorted(frame._conduit_cloud._registry.keys())
        )
        cluster_names = tuple(sorted(frame._conduit_clusters.keys()))
        payload = FrameDescriptorPayload(
            system_state=frame_configuration.system_state,
            ai_native_enabled=frame_configuration.ai_native_enabled,
            rift_enabled=frame_configuration.rift_enabled,
            root_conduit_count=len(root_conduit_ids),
            root_conduit_ids=root_conduit_ids,
            named_root_conduits=named_root_conduits,
            conduit_cloud_entry_count=len(conduit_cloud_names),
            conduit_cloud_names=conduit_cloud_names,
            cluster_count=len(cluster_names),
            cluster_names=cluster_names,
        )
        frame_record = FrameRecord(
            frame_name=frame_name,
            frame_id=frame._id,
            config_origin_spellbook_id=config_origin_spellbook_id,
            payload=payload,
        )
        descriptor.set_frame_overview(frame_record)

    def _bootstrap_root_conduit(
            self,
            frame_name: str,
            configuration: NexusFrameConfiguration,
            root_conduit_name: str,
    ) -> Any:
        from melder.spellbook.spellbook import Spellbook

        spellbook_configuration = configuration.to_spellbook_configuration()
        self._nexus._aether._bind_configuration(
            spellbook_configuration,
            frame_name,
        )
        spellbook = Spellbook(
            aetheric_frame=frame_name,
            configuration=spellbook_configuration,
        )
        conduit = spellbook.conjure(
            name=root_conduit_name,
            automatic=(configuration.system_state == SystemState.automatic),
        )
        self._publish_frame_overview(
            frame_name,
            config_origin_spellbook_id=spellbook.id,
        )
        return conduit

    def _frame_is_in_active_rift_use(self, frame_name: str) -> bool:
        for rift in self._nexus._rifts_by_id.values():
            try:
                accessible_frame_names = set(
                    self.list_accessible_frame_names_for_rift(rift.id)
                )
            except Exception:
                continue
            if frame_name in accessible_frame_names:
                return True
        return False

    def _mirror_legacy_nexus_frame_record(
            self,
            frame_name: str,
            frame: Any,
            *,
            creator_rift_id: str,
            immutable: bool,
    ) -> None:
        descriptor = self._nexus._frame_descriptor_manager._get_or_create_frame_descriptor(
            frame_name
        )
        descriptor.set_nexus_frame_record(
            NexusFrameRecord(
                frame_name=frame_name,
                frame=frame,
                nexus_frame_mode=self._nexus._configuration.get_property(
                    "nexus_frame_mode"
                ),
                creator_rift_id=creator_rift_id,
                owner_rift_id=creator_rift_id,
                immutable=immutable,
            )
        )
        descriptor.nexus_frame_record.attach_rift_id(creator_rift_id)
