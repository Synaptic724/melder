import threading
from typing import Dict, List, Optional, Set, Tuple
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.aether.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.nexus.frame_descriptor.frame_descriptor_payload import (
    FrameDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.frame_record import FrameRecord
from melder.aether.nexus.nexus_frame_builder import NexusFrameBuilder
from melder.aether.nexus.nexus_frame_configuration import NexusFrameConfiguration
from melder.spellbook.configuration.system_state import SystemState
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces import (
    IAethericFrame,
    IConduit,
    INexus,
)


class NexusFrameManager(Cleanable):
    """
    Authoring and topology facade for Nexus-managed frames.

    Purpose:
        Centralize rooted frame authoring and topology-aware frame access above
        the lower `Aether`, descriptor, and ACL subsystems.

    Contract:
        - Holds the authoritative Nexus-managed frame registry as
          `frame_name -> IAethericFrame`.
        - Holds the authored frame configuration registry as
          `frame_name -> NexusFrameConfiguration`.
        - Every managed frame is dynamic, AI-native, and Rift-enabled.
        - Treats `Aether` as the real frame owner and disposal executor.
        - Uses strict-create semantics for Nexus-managed frame authoring:
          creation raises when the target frame already exists.
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
        "_next_indexed_frame_number",
        "_creating_frame_names",
        "_frames_by_name",
        "_configurations_by_frame_name",
    ]

    def __init__(self, *, nexus: INexus) -> None:
        """
        Initialize one Nexus frame-authoring facade.

        Purpose:
            Bind the manager to its owning `Nexus` facade and start the
            authoritative manager-owned registries empty.

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
        self._nexus: INexus = nexus
        self._next_indexed_frame_number: int = 1
        self._creating_frame_names: Set[str] = set()
        self._frames_by_name: Dict[str, IAethericFrame] = {}
        self._configurations_by_frame_name: Dict[str, NexusFrameConfiguration] = {}

    def cleanup(self) -> None:
        """
        Idempotently clear manager-owned registry state.

        Purpose:
            Tear down the manager-owned authored-frame registry, authored
            configurations, and indexed-frame allocator state without directly
            disposing runtime frames. Runtime teardown remains driven by the
            normal Aether cleanup path.

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
            self._creating_frame_names.clear()
            del self._next_indexed_frame_number
            del self._creating_frame_names
            del self._frames_by_name
            del self._configurations_by_frame_name
            del self._nexus
            del self._id
        del self._lock

    @property
    def id(self) -> str:
        """
        Return the stable manager id.

        Returns:
            str: Stable manager identity.
        """
        self.check_cleaned()
        return self._id

    def begin(self, frame_name: str) -> NexusFrameBuilder:
        """
        Begin one fluent authored-frame build.

        Purpose:
            Create a builder that accumulates authored frame posture and
            optional bootstrap intent before the frame is realized.

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

        Purpose:
            Expose the authoritative manager-owned registry membership check
            used after the legacy descriptor-owned Nexus-frame-record path was
            removed.

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

        Purpose:
            Expose a detached snapshot of the authoritative manager-owned
            registry without leaking the mutable internal dictionary.

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
            root_conduit_name: str = "root",
    ) -> IConduit:
        """
        Create one rooted dynamic Nexus-managed conduit directly.

        Purpose:
            Provide the non-fluent shortcut for the common AI-native dynamic
            authored frame posture used by internal agent workspaces.

        Returns:
            IConduit: Root conduit for the managed frame.
        """
        return self.create(
            NexusFrameConfiguration.create_dynamic_defaults(
                frame_name,
                immutable=immutable,
                metadata=metadata,
                root_conduit_name=root_conduit_name,
            ),
        )

    def create(
            self,
            configuration: NexusFrameConfiguration,
    ) -> IConduit:
        """
        Create one rooted Nexus-managed conduit from authored configuration.

        Purpose:
            Realize an authored Nexus-managed workspace through the repo-native
            `Spellbook` -> `conjure(...)` path so the caller gets a rooted
            conduit instead of an empty frame shell.

        Contract:
            - Rejects duplicate manager-owned frame names.
            - Treats the manager registry as the authoritative Nexus-managed
              frame set.
            - Uses the public `Spellbook` API to bind configuration and conjure
              the root conduit.
            - Returns the rooted conduit, not the frame object.

        Args:
            configuration:
                Authored frame configuration.

        Returns:
            IConduit: Root conduit for the managed frame.
        """
        self.check_cleaned()
        if not isinstance(configuration, NexusFrameConfiguration):
            raise TypeError(
                "configuration must be a NexusFrameConfiguration."
            )
        self._validate_configuration_contract(configuration)
        return self._create_configuration(
            configuration,
            validate_raw_mode=True,
        )

    def _create_configuration(
            self,
            configuration: NexusFrameConfiguration,
            *,
            validate_raw_mode: bool,
    ) -> IConduit:
        """
        Realize one rooted Nexus-managed conduit from authored configuration.

        Purpose:
            Share the frame-realization body between the public raw manager
            authoring path and the internal Rift-scoped topology path while
            letting only the public raw path enforce the extra raw-mode gate.

        Args:
            configuration:
                Authored frame configuration to realize.
            validate_raw_mode:
                True when the call originated from the public raw manager
                authoring path and must enforce raw mode constraints.

        Returns:
            IConduit: Root conduit for the managed frame.
        """
        frame_name = configuration.frame_name
        if validate_raw_mode:
            self._validate_raw_creation_for_mode(frame_name)
        root_conduit: Optional[IConduit] = None
        spellbook_id: Optional[str] = None
        frame: Optional[IAethericFrame] = None
        with self._lock:
            if (
                    frame_name in self._frames_by_name
                    or frame_name in self._creating_frame_names
            ):
                raise ValueError(
                    "Nexus managed frame '{0}' already exists.".format(frame_name)
                )
            self._validate_frame_budget((frame_name,))
            self._creating_frame_names.add(frame_name)

        try:
            frame = self._nexus._aether._create_frame(frame_name)
            root_conduit = self._conjure_root_conduit_for_configuration(
                configuration
            )
            spellbook_id = root_conduit._spellbook.id
            with self._lock:
                self._creating_frame_names.discard(frame_name)
                if frame_name in self._frames_by_name:
                    raise ValueError(
                        "Nexus managed frame '{0}' already exists.".format(
                            frame_name
                        )
                    )
                self._frames_by_name[frame_name] = frame
                self._configurations_by_frame_name[frame_name] = configuration
            self._ensure_descriptor_and_acl(frame_name)
            self._publish_frame_overview(
                frame_name,
                config_origin_spellbook_id=spellbook_id,
            )
            return root_conduit
        except Exception:
            with self._lock:
                self._creating_frame_names.discard(frame_name)
                if self._frames_by_name.get(frame_name) is frame:
                    self._frames_by_name.pop(frame_name, None)
                if (
                        self._configurations_by_frame_name.get(frame_name)
                        is configuration
                ):
                    self._configurations_by_frame_name.pop(frame_name, None)
            if root_conduit is not None:
                try:
                    root_conduit.cleanup()
                except Exception:
                    pass
            if frame is not None and not frame.cleaned:
                try:
                    frame.cleanup()
                except Exception:
                    pass
            raise

    def _validate_raw_creation_for_mode(self, frame_name: str) -> None:
        """
        Validate raw manager creation against the active Nexus frame mode.

        Purpose:
            Keep direct `NexusFrameManager` authoring aligned with the same
            `single` / `indexed` / `one_per_workspace` behavior model already
            enforced by the Rift-facing Nexus APIs.

        Contract:
            - Requires the owning Nexus to be enabled before direct authoring.
            - In `single`, only the canonical shared frame name may be created
              directly through the manager.
            - In `one_per_workspace`, raw manager creation is rejected because
              the path carries no Rift owner identity.
            - In `indexed`, explicit named creation remains allowed.

        Args:
            frame_name:
                Candidate frame name for the raw manager creation path.

        Returns:
            None.

        Raises:
            ValueError:
                If the current Nexus frame mode does not allow raw creation for
                the requested frame name.
        """
        self.check_cleaned()
        self._nexus._require_enabled()
        nexus_frame_mode = self._nexus._configuration.get_property(
            "nexus_frame_mode"
        )
        if nexus_frame_mode.name == "single":
            shared_frame_name = self._nexus._configuration.get_property(
                "default_nexus_frame_name"
            )
            if frame_name != shared_frame_name:
                raise ValueError(
                    "single Nexus mode only allows raw creation of the shared "
                    "frame '{0}'.".format(shared_frame_name)
                )
            return
        if nexus_frame_mode.name == "one_per_workspace":
            raise ValueError(
                "Raw NexusFrameManager creation is not allowed in "
                "one_per_workspace mode; use Rift.create_nexus_frame() or "
                "Nexus.create_nexus_frame_for_rift()."
            )

    def remove(self, frame_name: str) -> None:
        """
        Remove one authored Nexus-managed frame.

        Purpose:
            Request disposal of one manager-owned frame through the normal
            Aether cleanup path after validating that the frame still exists,
            is not immutable, and is no longer in active Rift use.

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
    ) -> IAethericFrame:
        """
        Return one manager-owned frame for a Rift under the current topology.

        Purpose:
            Resolve a previously created Nexus-managed frame according to the
            active topology mode while enforcing the same access rules that the
            Rift facade exposes publicly.

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
            root_conduit_name: str = "root",
            immutable: bool = False,
    ) -> IConduit:
        """
        Create one rooted Nexus-managed conduit for a Rift.

        Purpose:
            Provide the topology-aware strict-create path used by the Rift
            facade so shared, indexed, and one-per-workspace modes all create
            through one authoritative implementation while leaving recovery to
            the getter path.

        Args:
            rift_id:
                Requesting Rift id.
            frame_name:
                Optional explicit frame name.
            root_conduit_name:
                Root conduit name to use for newly created frames.
            immutable:
                Immutable flag for newly created frames.

        Returns:
            IConduit: Root conduit for the newly created frame.

        Raises:
            ValueError: If the target frame already exists or creation is not
                valid under the current topology rules.
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
            raise ValueError(
                "Nexus managed frame '{0}' already exists.".format(
                    requested_frame_name
                )
            )
        return self._create_configuration(
            NexusFrameConfiguration.create_dynamic_defaults(
                requested_frame_name,
                immutable=immutable,
                root_conduit_name=root_conduit_name,
            ),
            validate_raw_mode=False,
        )

    def authorize_frame_link_for_rift(
            self,
            rift_id: str,
            frame_name: str,
    ) -> bool:
        """
        Authorize one Rift frame-link request against Nexus-managed topology.

        Purpose:
            Let the Rift attachment path ask the manager whether a target frame
            is Nexus-managed and, if so, enforce the active topology rules
            before the frame link is created.

        Contract:
            - Returns `False` when the target frame is not manager-owned, so
              the caller can continue with the generic target-frame path.
            - Returns `True` when the frame is manager-owned and accessible to
              the requesting Rift.
            - Raises `ValueError` when the frame is manager-owned but the Rift
              is not allowed to attach to it under the active topology mode.

        Args:
            rift_id:
                Requesting Rift id.
            frame_name:
                Target frame name being attached through the Rift frame-link
                path.

        Returns:
            bool: True when the frame is manager-owned and authorized.
        """
        self.check_cleaned()
        self._nexus._require_enabled()
        self._nexus._get_required_rift(rift_id)
        with self._lock:
            if frame_name not in self._frames_by_name:
                return False
        self.get_frame_for_rift(rift_id, frame_name=frame_name)
        return True

    def list_accessible_frame_names_for_rift(self, rift_id: str) -> Tuple[str, ...]:
        """
        Return the manager-owned frame names accessible to one Rift.

        Purpose:
            Materialize the current frame visibility for one Rift from the
            authoritative manager registry and active topology mode.

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

        Purpose:
            Compute post-Rift-removal cleanup candidates directly from the
            manager registry and current Nexus topology mode instead of using a
            second attachment registry.

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

        Purpose:
            Synchronize the manager, descriptor, and ACL layers after Aether
            has already decided to dispose a frame. This is the bridge between
            runtime frame teardown and Nexus-side authored metadata cleanup.

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
            descriptor.clear_runtime_publication_state()
        self._nexus._frame_acl_manager._remove_frame_acl_container(frame_name)
        return True

    def _determine_frame_name_for_rift(self, rift_id: str) -> str:
        """
        Determine the manager-owned frame name for one Rift.

        Purpose:
            Derive the private frame name used by `one_per_workspace` mode
            without relying on any legacy descriptor-backed Nexus-managed
            frame bookkeeping.

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

        Purpose:
            Centralize topology-sensitive frame-name resolution so both
            retrieval and strict-create flows enforce the same naming and
            visibility rules.

        Args:
            rift_id:
                Requesting Rift id.
            frame_name:
                Optional explicit frame name.
            allow_creation:
                True when the resolution path is a strict-create path.

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
        """
        Allocate the next deterministic indexed Nexus-managed frame name.

        Purpose:
            Keep indexed Nexus-frame naming inside the frame manager so the
            manager owns both authoritative storage and indexed name
            allocation for authored frames.

        Returns:
            str: Newly allocated indexed Nexus-managed frame name.
        """
        indexed_frame_name = "{0}-{1}".format(
            self._nexus._configuration.get_property("default_nexus_frame_name"),
            self._next_indexed_frame_number,
        )
        self._next_indexed_frame_number = self._next_indexed_frame_number + 1
        return indexed_frame_name

    def _ensure_descriptor_and_acl(self, frame_name: str) -> None:
        """
        Provision descriptor and ACL container state for one authored frame.

        Purpose:
            Keep the descriptor-side cached frame/configuration references and
            the ACL container aligned with the newly realized manager-owned
            frame before higher-level viewing or command surfaces inspect it.

        Args:
            frame_name:
                Managed frame name being provisioned.

        Returns:
            None.
        """
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
        """
        Publish the descriptor-owned overview record for one authored frame.

        Purpose:
            Mirror the new authored frame into the passive descriptor layer so
            viewer and inventory surfaces can inspect the rooted frame
            immediately after creation.

        Args:
            frame_name:
                Managed frame name being published.
            config_origin_spellbook_id:
                Optional originating spellbook id when one exists.

        Returns:
            None.
        """
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

    def _validate_frame_budget(
            self,
            frame_names: Tuple[str, ...],
    ) -> None:
        """
        Validate manager-owned frame budget before authored creation.

        Purpose:
            Enforce `max_nexus_frame_count` directly from the authoritative
            manager registry now that the legacy descriptor-owned Nexus frame
            record path has been removed.

        Args:
            frame_names:
                Candidate authored frame names being added.

        Returns:
            None.

        Raises:
            ValueError:
                If the configured Nexus-managed frame budget would be
                exceeded.
        """
        unique_new_frame_names = []
        for frame_name in frame_names:
            if frame_name in self._frames_by_name:
                continue
            if frame_name in unique_new_frame_names:
                continue
            unique_new_frame_names.append(frame_name)
        if not unique_new_frame_names:
            return
        if len(self._frames_by_name) + len(unique_new_frame_names) > self._nexus._configuration.get_property(
                "max_nexus_frame_count"
        ):
            raise ValueError("Nexus internal frame cap has been reached.")

    @staticmethod
    def _validate_configuration_contract(
            configuration: NexusFrameConfiguration,
    ) -> None:
        """
        Validate the fixed Nexus-managed frame posture contract.

        Purpose:
            Enforce the agent-usable Nexus frame posture at manager ingress so
            manually constructed or later-mutated authored configurations cannot
            enter the authoritative frame registry in an invalid state.

        Args:
            configuration:
                Authored Nexus frame configuration being realized.

        Returns:
            None.

        Raises:
            ValueError:
                If the authored frame posture is not dynamic, AI-native, and
                Rift-enabled.
        """
        if configuration.system_state != SystemState.dynamic:
            raise ValueError(
                "Nexus-managed frames must use system_state=SystemState.dynamic."
            )
        if configuration.ai_native_enabled is not True:
            raise ValueError(
                "Nexus-managed frames must set ai_native_enabled=True."
            )
        if configuration.rift_enabled is not True:
            raise ValueError(
                "Nexus-managed frames must set rift_enabled=True."
            )

    def _conjure_root_conduit_for_configuration(
            self,
            configuration: NexusFrameConfiguration,
    ) -> IConduit:
        """
        Conjure the required root conduit for one Nexus-managed frame.

        Purpose:
            Use the public `Spellbook` API so Nexus-managed creation follows the
            same runtime grammar as the rest of the repo: configuration through
            `Spellbook`, then rooted conduit creation through
            `Spellbook.conjure(...)`.

        Args:
            configuration:
                Authored configuration that drives rooted creation.

        Returns:
            IConduit: Newly created root conduit.
        """
        from melder.aether.conduit.conduit import Conduit
        from melder.spellbook.spellbook import Spellbook

        Spellbook._aether = self._nexus._aether
        Conduit._aether = self._nexus._aether
        frame = Spellbook._aether._ensure_frame(configuration.frame_name)
        frame.bind_frame_configuration(
            configuration.to_aetheric_frame_configuration()
        )
        spellbook_configuration = configuration.to_spellbook_configuration()
        spellbook = Spellbook(
            aetheric_frame=configuration.frame_name,
            configuration=spellbook_configuration,
        )
        return spellbook.conjure(
            name=configuration.root_conduit_name,
            automatic=False,
        )

    def _get_required_root_conduit_for_frame(
            self,
            frame_name: str,
            *,
            root_conduit_name: str = "root",
    ) -> IConduit:
        """
        Return the required root conduit for an already managed frame.

        Purpose:
            Support getter-only rooted-conduit recovery for the Rift-facing
            Nexus access path without returning the frame object.

        Args:
            frame_name:
                Managed frame name whose root conduit should be returned.
            root_conduit_name:
                Preferred root conduit name.

        Returns:
            IConduit: Matching root conduit for the frame.
        """
        with self._lock:
            frame = self._frames_by_name.get(frame_name)
        if frame is None:
            raise ValueError(
                "Nexus managed frame '{0}' was not found.".format(frame_name)
            )
        if not frame._conduits:
            raise ValueError(
                "Nexus managed frame '{0}' has no root conduit.".format(
                    frame_name
                )
            )
        for conduit in frame._conduits.values():
            if conduit is not None and conduit.name == root_conduit_name:
                return conduit
        if len(frame._conduits) == 1:
            return next(iter(frame._conduits.values()))
        raise ValueError(
            "Nexus managed frame '{0}' has no root conduit named '{1}'.".format(
                frame_name,
                root_conduit_name,
            )
        )

    def _frame_is_in_active_rift_use(self, frame_name: str) -> bool:
        """
        Return whether any live Rift can still access the frame.

        Purpose:
            Guard removal of manager-owned frames without maintaining a second
            attachment registry by deriving live usage from the current Rift
            registry and topology rules.

        Args:
            frame_name:
                Managed frame name being considered for removal.

        Returns:
            bool: True when at least one active Rift can still reach the
            frame.
        """
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
