from melder.aether.nexus.rift.rift_space.command_system.command_system import (
    CommandSystem,
)


class CodegenCommandSystem(CommandSystem):
    """
    Internal

    Codegen-room command surface.

    Purpose:
        Preserve the shared broad runtime command behavior for
        `CodegenRiftSpace`.

    Contract:
        - Inherits all shared selected-target, ACL, and workstation behavior
          from `CommandSystem`.
        - Does not narrow raw runtime-object access beyond the shared ACL
          checks already enforced by the base class.
    """
