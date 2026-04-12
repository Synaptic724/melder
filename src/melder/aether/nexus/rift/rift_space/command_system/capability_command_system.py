from melder.aether.nexus.configuration.rift_space_type import RiftSpaceType
from melder.aether.nexus.rift.rift_space.command_system.command_system import (
    CommandSystem,
)


class CapabilityCommandSystem(CommandSystem):
    """
    Internal

    Capability-room command surface.

    Purpose:
        Keep the shared command API while restricting raw runtime-object
        exposure for `CapabilityRiftSpace` until a dedicated capability handle
        surface exists.

    Contract:
        - Inherits all shared selected-target, ACL, and workstation behavior
          from `CommandSystem`.
        - Rejects raw runtime-object getters so capability rooms do not expose
          naked runtime objects through the generic command surface.
        - Leaves already-bound workstation objects outside post-bind policing.
    """

    def _assert_raw_runtime_object_access_allowed(
            self,
            method_name: str,
    ) -> None:
        """
        Reject raw runtime-object access in capability rooms.

        Args:
            method_name:
                Public command-system method attempting raw runtime-object
                exposure.

        Returns:
            None.

        Raises:
            ValueError:
                Always, because capability rooms do not expose naked runtime
                objects through the generic command getters in this cut.
        """
        raise ValueError(
            "Raw runtime-object access via '{0}' is disabled in {1} RiftSpace. "
            "Use descriptor/record access or bind through an approved dynamic path.".format(
                method_name,
                RiftSpaceType.capability.value,
            )
        )
