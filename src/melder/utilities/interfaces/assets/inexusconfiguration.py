from typing import Optional, Protocol, Sequence, runtime_checkable
from melder.utilities.interfaces.assets.icleanable import ICleanable

@runtime_checkable
class INexusConfiguration(ICleanable, Protocol):
    """
    Interface for central Nexus configuration.
    """

    @property
    def frozen(self) -> bool:
        """
        Return whether this Nexus configuration has been frozen.
        """
        ...

    @property
    def id(self) -> str:
        """
        Return the stable identifier for this configuration instance.
        """
        ...

    def set_property(self, key: str, value: object) -> None:
        """
        Set one configuration property by key.

        Returns:
            None.
        """
        ...

    def get_property(self, key: str) -> object:
        """
        Return one configuration property value by key.
        """
        ...

    def has_property(self, key: str) -> bool:
        """
        Return whether one configuration property exists.
        """
        ...

    def load_default_dictionary(self) -> None:
        """
        Load the default Nexus configuration dictionary into this instance.

        Returns:
            None.
        """
        ...

    def validate(self) -> bool:
        """
        Validate the current Nexus configuration payload.
        """
        ...

    def freeze(self) -> None:
        """
        Freeze the current configuration so further mutation is disallowed.

        Returns:
            None.
        """
        ...

    def finalize(self) -> "INexusConfiguration":
        """
        Finalize this configuration and return the resulting configuration object.
        """
        ...

    def build(self) -> "INexusConfiguration":
        """
        Build and return the finalized Nexus configuration object.
        """
        ...

    def with_defaults(self) -> "INexusConfiguration":
        """
        Apply the default Nexus configuration values and return this configuration.
        """
        ...

    def with_rift_creation_enabled(self, enabled: bool = True) -> "INexusConfiguration":
        """
        Set whether the Nexus may create new Rift instances and return this configuration.
        """
        ...

    def with_creation_token_required(self, enabled: bool = True) -> "INexusConfiguration":
        """
        Set whether Rift creation requests must supply the configured creation token.
        """
        ...

    def with_creation_token(self, token_value: Optional[str]) -> "INexusConfiguration":
        """
        Set the token value used to authorize Rift creation requests and return this configuration.
        """
        ...

    def with_direct_rift_access(self, enabled: bool = True) -> "INexusConfiguration":
        """
        Set whether callers may access registered Rifts directly through Nexus lookups.
        """
        ...

    def with_rift_access_token_required(self, enabled: bool = True) -> "INexusConfiguration":
        """
        Set whether Rift lookup and access operations require an access token.
        """
        ...

    def with_rift_access_token(self, token_value: Optional[str]) -> "INexusConfiguration":
        """
        Set the token value used to authorize direct Rift access and return this configuration.
        """
        ...

    def with_allow_external_rift_registration(self, enabled: bool = True) -> "INexusConfiguration":
        """
        Set whether externally created Rift instances may be registered with Nexus.
        """
        ...

    def with_allow_nested_rift_creation(self, enabled: bool = True) -> "INexusConfiguration":
        """
        Set whether Rift creation flows may create child or nested Rifts.
        """
        ...

    def with_max_active_rift_count(self, count: int) -> "INexusConfiguration":
        """
        Set the maximum number of concurrently active Rifts and return this configuration.
        """
        ...

    def with_nexus_frame_mode(self, mode: object) -> "INexusConfiguration":
        """
        Set the Nexus frame exposure mode used when Rifts resolve accessible frames.
        """
        ...

    def with_default_nexus_frame_name(self, frame_name: str) -> "INexusConfiguration":
        """
        Set the default Nexus frame name used when Rift operations do not name a frame.
        """
        ...

    def with_auto_create_nexus_frames(self, enabled: bool = True) -> "INexusConfiguration":
        """
        Set whether missing Nexus frames may be created automatically on demand.
        """
        ...

    def with_max_nexus_frame_count(self, count: int) -> "INexusConfiguration":
        """
        Set the maximum number of Nexus frames this configuration will allow.
        """
        ...

    def with_allowed_target_frame_names(self, frame_names: Sequence[str]) -> "INexusConfiguration":
        """
        Set the allow-list of target frame names Rifts may select under this configuration.
        """
        ...

    def with_denied_target_frame_names(self, frame_names: Sequence[str]) -> "INexusConfiguration":
        """
        Set the deny-list of target frame names Rifts must not target.
        """
        ...

    def with_target_frame_override(self, enabled: bool = True) -> "INexusConfiguration":
        """
        Set whether callers may override the configured target-frame selection policy.
        """
        ...

    def with_multiple_target_frames(self, enabled: bool = True) -> "INexusConfiguration":
        """
        Set whether one Rift may target more than one frame at the same time.
        """
        ...

    def with_max_target_frame_count(self, count: int) -> "INexusConfiguration":
        """
        Set the maximum number of target frames one Rift may hold concurrently.
        """
        ...

    def with_projection_refresh_gate(self, enabled: bool = True) -> "INexusConfiguration":
        """
        Set whether ACL-driven projection refresh uses the RiftGate drain barrier.
        """
        ...

    def with_projection_refresh_gate_timeout_seconds(
            self,
            timeout_seconds: object,
    ) -> "INexusConfiguration":
        """
        Set the timeout used while waiting for impacted Rift gates to drain.
        """
        ...

    def with_projection_refresh_gate_poll_interval_seconds(
            self,
            interval_seconds: object,
    ) -> "INexusConfiguration":
        """
        Set the poll interval used while waiting for impacted Rift gates to drain.
        """
        ...

    def with_default_space_type(self, space_type: object) -> "INexusConfiguration":
        """
        Set the default RiftSpace type used when new spaces are created implicitly.
        """
        ...

    def with_default_auto_activate_on_program(self, enabled: bool = True) -> "INexusConfiguration":
        """
        Set whether newly programmed Rifts auto-activate after creation.
        """
        ...

    def with_default_auto_create_space(self, enabled: bool = True) -> "INexusConfiguration":
        """
        Set whether newly programmed Rifts auto-create their default working space.
        """
        ...

    def with_default_validation_mode(self, mode: object) -> "INexusConfiguration":
        """
        Set the default validation mode applied to Rift programming and activation flows.
        """
        ...
