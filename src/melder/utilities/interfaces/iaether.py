import logging
from typing import Any, List, Optional, Protocol, Set, Tuple, Union, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.ichangecontrolmanager import IChangeControlManager
from melder.utilities.interfaces.iaetherconfiguration import IAetherConfiguration
from melder.utilities.interfaces.iaetherconfigurationbuilder import IAetherConfigurationBuilder
from melder.utilities.interfaces.iconduitcloud import IConduitCloud
from melder.utilities.interfaces.iconduit import IConduit
from melder.utilities.interfaces.ichannellogger import IChannelLogger

@runtime_checkable
class IAether(ICleanable, Protocol):
    """
    The interface of global the singleton root that owns all `AethericFrame` instances.

    `Aether` is the top-level runtime host for Melder. It owns the named frame
    registry, the always-present default frame, and the frame-level services
    that other runtime objects resolve through when they need configuration,
    conduit, cluster, spell, or DevOps state.

    Contract:
        - Enforces singleton construction through `__new__`.
        - Owns the lifecycle of registered `AethericFrame` instances.
        - Owns the default frame and ensures it exists while the singleton is live.
        - Hosts singleton-level subsystems such as Nexus, Crystallizer, and the
          utility system.
        - Hosts the singleton MutationResearch root above frame-local runtime
          state.
        - Owns one optional Aether root configuration that applies policy into
          the hosted utility system.
        - Becomes reinitializable only after `cleanup()` fully resets singleton state.

    Threading / Concurrency:
    - Uses the class-level `_lock` to serialize singleton construction and reset.
    - Uses the instance `_lock` to guard cleanup and frame-registry mutation.

    Lifecycle / Cleanup:
    - Cleans registered frames before dropping singleton-level references.
    - Resets `_instance` and `_initialized` so tests or later runtime flows can
      create a fresh singleton after teardown.
    """
    def attach_logger(
            self,
            logger: Optional[Union[IChannelLogger, logging.Logger]],
    ) -> None:
        """
        Attach one real logger after Aether boot.

        Args:
            logger:
                Real logger to attach, or None to detach back to the null
                logger wrapper.

        Returns:
            None.
        """
        ...

    def enable_logging(
            self,
            logger: Optional[Union[IChannelLogger, logging.Logger]] = None,
    ) -> None:
        """
        Enable Aether's own logger after boot.

        Args:
            logger:
                Optional explicit logger override. When omitted, Aether should
                use the hosted automatic channel-logger path, which requires an
                activated Aether root configuration and enabled automatic
                channel logger policy.

        Returns:
            None.
        """
        ...

    def create_configuration(self) -> IAetherConfiguration:
        """
        Create one mutable Aether root configuration.

        Returns:
            IAetherConfiguration:
                Fresh mutable configuration instance.
        """
        ...

    def create_configuration_builder(self) -> IAetherConfigurationBuilder:
        """
        Create one fluent builder for Aether root configuration assembly.

        Returns:
            IAetherConfigurationBuilder:
                New one-shot builder.
        """
        ...

    def configure(self, configuration: IAetherConfiguration) -> None:
        """
        Install one root configuration on Aether.

        Args:
            configuration:
                Root configuration to install.

        Returns:
            None.
        """
        ...

    def activate(
            self,
            configuration: Optional[IAetherConfiguration] = None,
    ) -> None:
        """
        Activate the installed Aether root configuration.

        Args:
            configuration:
                Optional configuration to install before activation.

        Returns:
            None.
        """
        ...

    def _get_change_control_manager(
            self,
            aetheric_frame: str,
    ) -> Optional[IChangeControlManager]:
        """
        Return the frame-owned change-control manager for one frame, if present.

        Args:
            aetheric_frame:
                Frame name whose change-control manager is requested.

        Returns:
            Optional[IChangeControlManager]: Frame-owned change-control manager.
        """
        ...

    def get_conduit_cloud(self, aetheric_frame_name: str = "default") -> IConduitCloud:
        """
        Return the conduit cloud for one frame.
        """
        ...

    def list_conduit_ids(
            self,
            aetheric_frame_name: str = "default",
    ) -> Tuple[str, ...]:
        """
        Return the registered root conduit ids for one frame.
        """
        ...

    def list_conduit_names(
            self,
            aetheric_frame_name: str = "default",
    ) -> Tuple[str, ...]:
        """
        Return the registered root conduit names for one frame.
        """
        ...

    def count_conduits(self, aetheric_frame_name: str = "default") -> int:
        """
        Return the number of registered root conduits for one frame.
        """
        ...

    def has_conduit_id(
            self,
            conduit_id: str,
            aetheric_frame_name: str = "default",
    ) -> bool:
        """
        Return whether one root conduit id exists in one frame.
        """
        ...

    def has_conduit_name(
            self,
            name: str,
            aetheric_frame_name: str = "default",
    ) -> bool:
        """
        Return whether one root conduit name exists in one frame.
        """
        ...

    def find_conduit_id_by_name(
            self,
            name: str,
            aetheric_frame_name: str = "default",
    ) -> Optional[str]:
        """
        Return the conduit id registered under one root conduit name, if present.
        """
        ...

    def get_conduit_by_name(
            self,
            name: str,
            aetheric_frame_name: str = "default",
    ) -> IConduit:
        """
        Return one registered root conduit by name.
        """
        ...

    def get_conduit_by_id(
            self,
            conduit_id: str,
            aetheric_frame_name: str = "default",
    ) -> IConduit:
        """
        Return one registered root conduit by id.
        """
        ...

    def cleanup_aetheric_frames(self) -> None:
        """
        Cleans all aetheric frames and their contents.
        """
        ...
