from melder.aether.nexus.rift.command_system.command_system import (
    CommandSystem,
)


class CapabilityCommandSystem(CommandSystem):
    """
    Internal

    Capability-room command surface.

    Purpose:
        Keep the shared command API while opening broad manual runtime access
        for `CapabilityRiftSpace`.

    Contract:
        - Inherits all shared selected-target, ACL, and workstation behavior
          from `CommandSystem`.
        - Allows the shared broad runtime-object getters and manual object
          work surface.
        - Does not add codegen behavior; it only stops denying the existing
          manual runtime surface.
        - Still relies on the underlying Melder frame/runtime to reject
          dynamic-only operations when the target frame is automatic.
        - Leaves already-bound workstation objects outside post-bind policing.
    """

    def _assert_raw_runtime_object_access_allowed(
            self,
            method_name: str,
    ) -> None:
        """
        Allow raw runtime-object access in capability rooms.

        Args:
            method_name:
                Public command-system method attempting raw runtime-object
                exposure.

        Returns:
            None.
        """
        _ = method_name
