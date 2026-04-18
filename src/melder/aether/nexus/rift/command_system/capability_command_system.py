from melder.aether.nexus.rift.command_system.command_system import (
    CommandSystem,
)


class CapabilityCommandSystem(CommandSystem):
    """
    Internal

    Capability-room command surface.

    Purpose:
        Preserve the shared broad runtime command behavior for
        `CapabilityRiftSpace`.

    Contract:
        - Inherits the shared command surface directly without adding new
          runtime-policy overrides.
        - Leaves raw runtime-object access, topology mutation, and spell
          activation enabled under the base command policy.
        - Exists to keep the capability room type explicit even though the
          current behavior matches the base command surface.
    """
