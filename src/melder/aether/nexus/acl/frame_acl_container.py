import threading
from typing import Dict, List

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable

from melder.aether.nexus.acl.frame_acl_builder import FrameACLBuilder
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.frame_acl_configuration_chain import FrameACLConfigurationChain
from melder.aether.nexus.acl.frame_acl_validator import FrameACLValidator
from melder.utilities.helpers.id_builder import IDBuilder


class FrameACLContainer(Cleanable):
    """
    Purpose:
        Hold all frame-local ACL subsystem objects for one frame in one place.

    Contract:
        - One container exists per frame ACL registration.
        - The container owns one configuration chain, one validator, and one
          builder for the frame.
        - The builder is a stable object-singleton inside the container.
        - The container is the handoff point between manager-level frame
          targeting and chain-level ACL history mechanics.

    Threading:
        Uses one instance `threading.RLock` to serialize cleanup against other
        container-owned operations.

    Lifecycle:
        Cleanup is idempotent and cascades into the builder, validator, and
        configuration chain before dropping references.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_frame_name",
        "_frame_acl_configuration_chain",
        "_named_configurations_by_name",
        "_frame_acl_validator",
        "_frame_acl_builder",
    ]

    def __init__(
            self,
            frame_name: str,
            *,
            history_limit: int = 15,
    ) -> None:
        """
        Initialize one frame ACL container.

        Purpose:
            Create the frame-local ACL subsystem objects and seed the
            configuration chain with its default head/current configuration.

        Contract:
            - `frame_name` must be a non-empty stable frame identifier.
            - `history_limit` must allow at least one retained configuration.
            - Builder, validator, and chain are created eagerly and owned by
              the container from construction onward.

        Args:
            frame_name:
                Stable frame name that owns this ACL container.
            history_limit:
                Maximum number of configuration nodes retained by the owned
                chain.

        Returns:
            None.

        Raises:
            ValueError:
                If `frame_name` is empty or `history_limit` is less than 1.
            TypeError:
                If `history_limit` is not an integer.
        """
        super().__init__()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        if not isinstance(history_limit, int) or history_limit < 1:
            raise ValueError("history_limit must be an integer >= 1.")
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._frame_name: str = frame_name
        self._frame_acl_configuration_chain: FrameACLConfigurationChain = (
            FrameACLConfigurationChain(
                frame_name,
                history_limit=history_limit,
            )
        )
        self._named_configurations_by_name: Dict[str, FrameACLConfiguration] = {}
        self._frame_acl_validator: FrameACLValidator = FrameACLValidator(frame_name)
        self._frame_acl_builder: FrameACLBuilder = FrameACLBuilder(self)
        self._sync_default_named_configuration_to_current()

    def cleanup(self) -> None:
        """
        Idempotently cleanup the container and all owned ACL objects.

        Purpose:
            Tear down the frame-local ACL subsystem in dependency order.

        Contract:
            - Safe to call more than once.
            - Cleans builder, validator, and configuration chain before
              dropping references.
            - Leaves the container unusable after completion.

        Threading:
            Acquires the container lock so teardown does not interleave with
            other container-owned operations.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._frame_acl_builder.cleanup()
            self._frame_acl_validator.cleanup()
            self._frame_acl_configuration_chain.cleanup()
            self._named_configurations_by_name.clear()
            self._frame_acl_builder = None
            self._frame_acl_validator = None
            self._frame_acl_configuration_chain = None
            self._named_configurations_by_name = None
            self._frame_name = None
        self._lock = None

    @property
    def frame_name(self) -> str:
        """
        Return the owning frame name.

        Purpose:
            Expose the stable frame identity that anchors the container.

        Returns:
            str: Owning frame name.
        """
        self.check_cleaned()
        return self._frame_name

    @property
    def frame_acl_builder(self) -> FrameACLBuilder:
        """
        Return the unique builder object for this frame container.

        Purpose:
            Expose the one builder object owned by the container.

        Contract:
            Repeated reads return the same builder object until cleanup.

        Returns:
            FrameACLBuilder: Unique builder object.
        """
        self.check_cleaned()
        return self._frame_acl_builder

    @property
    def frame_acl_configuration(self) -> FrameACLConfiguration:
        """
        Return the current frame ACL configuration.

        Purpose:
            Expose the currently selected configuration node from the owned
            configuration chain.

        Returns:
            FrameACLConfiguration: Current configuration.
        """
        self.check_cleaned()
        return self._frame_acl_configuration_chain.get_current_configuration()

    @property
    def named_configurations_by_name(self) -> Dict[str, FrameACLConfiguration]:
        """
        Return a detached snapshot of named ACL configurations for this frame.

        Purpose:
            Expose the per-frame named contract registry without returning the
            live mutable dictionary.

        Contract:
            - Returns a shallow copy.
            - `"default"` is always present and tracks the current selected
              configuration from the chain.

        Returns:
            Dict[str, FrameACLConfiguration]:
                Detached snapshot of named configurations for this frame.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._named_configurations_by_name)

    @property
    def frame_acl_configuration_chain(self) -> FrameACLConfigurationChain:
        """
        Return the frame-scoped ACL configuration chain.

        Purpose:
            Expose the owned history/current/head mechanics object for the
            frame.

        Returns:
            FrameACLConfigurationChain: Frame-scoped configuration chain.
        """
        self.check_cleaned()
        return self._frame_acl_configuration_chain

    @property
    def frame_acl_validator(self) -> FrameACLValidator:
        """
        Return the frame-scoped ACL validator.

        Purpose:
            Expose the owned validator object that checks configuration/frame
            alignment.

        Returns:
            FrameACLValidator: Frame-scoped validator.
        """
        self.check_cleaned()
        return self._frame_acl_validator

    @property
    def frame_acl_history(self) -> List[FrameACLConfiguration]:
        """
        Return a snapshot of retained configuration history.

        Purpose:
            Provide the non-current retained configuration nodes for inspection
            without exposing chain internals directly.

        Contract:
            - Excludes the current configuration node.
            - Preserves newest-to-oldest ordering from the chain.

        Returns:
            List[FrameACLConfiguration]: Snapshot of prior configurations.
        """
        self.check_cleaned()
        current_configuration_id = (
            self._frame_acl_configuration_chain.current_configuration_id
        )
        return [
            configuration
            for configuration in self._frame_acl_configuration_chain.list_configurations()
            if configuration.configuration_id != current_configuration_id
        ]

    def install_configuration(
            self,
            configuration: FrameACLConfiguration,
    ) -> None:
        """
        Validate and install the next frame ACL configuration revision.

        Purpose:
            Commit a validated configuration node into the owned chain as the
            new head/current node.

        Contract:
            - Validation runs before insertion.
            - Successful installation inserts at the head and selects the new
              node as current.

        Args:
            configuration:
                Locked configuration node to install.

        Returns:
            None.

        Raises:
            TypeError, ValueError:
                Propagated when validation fails or the chain rejects the node.
        """
        self.check_cleaned()
        self._frame_acl_validator.validate_configuration(configuration)
        self._frame_acl_configuration_chain.insert_head_configuration(
            configuration,
            select_as_current=True,
        )
        self._sync_default_named_configuration_to_current()

    def select_current_configuration(
            self,
            configuration_id: str,
    ) -> FrameACLConfiguration:
        """
        Select one existing configuration in the chain as current.

        Purpose:
            Move current selection to one already-owned configuration node.

        Args:
            configuration_id:
                Existing configuration id to make current.

        Returns:
            FrameACLConfiguration: Newly selected current configuration.
        """
        self.check_cleaned()
        selected_configuration = (
            self._frame_acl_configuration_chain.select_current_configuration(
                configuration_id
            )
        )
        self._sync_default_named_configuration_to_current()
        return selected_configuration

    def get_named_configuration(
            self,
            contract_name: str = "default",
    ) -> FrameACLConfiguration:
        """
        Return one named ACL configuration for this frame.

        Purpose:
            Resolve one frame-local named ACL contract.

        Contract:
            - Names are local to this frame.
            - `"default"` always resolves to the current selected chain
              configuration.
            - Fails fast when the requested name is not registered.

        Args:
            contract_name:
                Frame-local contract name to resolve.

        Returns:
            FrameACLConfiguration:
                Registered named configuration for this frame.

        Raises:
            ValueError:
                If `contract_name` is empty.
            KeyError:
                If the name is not registered.
        """
        self.check_cleaned()
        if not contract_name:
            raise ValueError("contract_name cannot be empty.")
        with self._lock:
            try:
                return self._named_configurations_by_name[contract_name]
            except KeyError as exc:
                raise KeyError(
                    "No ACL contract named '{0}' is registered for frame '{1}'.".format(
                        contract_name,
                        self._frame_name,
                    )
                ) from exc

    def list_named_configuration_names(self) -> List[str]:
        """
        Return all registered ACL contract names for this frame.

        Purpose:
            Expose the frame-local named contract registry keys in insertion
            order.

        Returns:
            List[str]:
                Registered contract names for this frame.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._named_configurations_by_name.keys())

    def register_named_configuration(
            self,
            configuration: FrameACLConfiguration,
            *,
            contract_name: str = "default",
    ) -> FrameACLConfiguration:
        """
        Register one additional named ACL configuration for this frame.

        Purpose:
            Add a new frame-local named contract without replacing the current
            chain/history mechanics.

        Contract:
            - `contract_name` must be non-empty.
            - Duplicate names are rejected.
            - `"default"` is reserved by the container and is seeded
              automatically from the current selected configuration.
            - The configuration must target this frame and already be locked.

        Args:
            configuration:
                Locked configuration node to register.
            contract_name:
                Frame-local contract name.

        Returns:
            FrameACLConfiguration:
                Registered configuration node.

        Raises:
            ValueError:
                If the name is empty, already exists, or the configuration is
                unlocked.
            TypeError:
                If `configuration` is not a `FrameACLConfiguration`.
        """
        self.check_cleaned()
        if not contract_name:
            raise ValueError("contract_name cannot be empty.")
        if not isinstance(configuration, FrameACLConfiguration):
            raise TypeError("configuration must be a FrameACLConfiguration.")
        if not configuration.locked:
            raise ValueError(
                "Named ACL configuration must be locked before registration."
            )
        self._frame_acl_validator.validate_configuration(configuration)
        with self._lock:
            if contract_name in self._named_configurations_by_name:
                raise ValueError(
                    "ACL contract '{0}' already exists for frame '{1}'.".format(
                        contract_name,
                        self._frame_name,
                    )
                )
            self._named_configurations_by_name[contract_name] = configuration
            return configuration

    def rollback_to_configuration(
            self,
            configuration_id: str,
    ) -> FrameACLConfiguration:
        """
        Roll current selection back to one historical config.

        Purpose:
            Provide a semantic rollback entrypoint over the underlying
            current-selection mechanics.

        Args:
            configuration_id:
                Historical configuration id to restore as current.

        Returns:
            FrameACLConfiguration: Newly selected current configuration.
        """
        self.check_cleaned()
        rolled_back_configuration = (
            self._frame_acl_configuration_chain.rollback_to_configuration(
                configuration_id
            )
        )
        self._sync_default_named_configuration_to_current()
        return rolled_back_configuration

    def _sync_default_named_configuration_to_current(self) -> None:
        """
        Sync the reserved `"default"` contract to the current chain selection.

        Purpose:
            Preserve backward-compatible behavior where the default named ACL
            contract for a frame tracks the frame's currently selected
            configuration.

        Returns:
            None.
        """
        with self._lock:
            self._named_configurations_by_name["default"] = (
                self._frame_acl_configuration_chain.get_current_configuration()
            )
