from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from melder.nexus.rift.rift import Rift
    from melder.nexus.rift.command_system.command_system import (
        CommandSystem,
    )

from melder.nexus.rift.command_system.codegen_command_system import (
    CodegenCommandSystem,
)
from melder.nexus.rift.codegen_system.codegen_system import CodegenSystem
from melder.nexus.rift.rift_space.rift_space import RiftSpace
from melder.nexus.rift.rift_gate.rift_gate import RiftGate


class CodegenRiftSpace(RiftSpace):
    """
    Internal

    Purpose:
        Represent the richer concrete room type for codegen/local-construction
        workflows.

    Contract:
        - Inherits all base room behavior.
        - Fixes `space_kind` to `codegen`.
        - Represents the richer room surface intended for local construction,
          mutable room state, and more open-ended workflows.
        - Currently composes a slim selected runtime-helper surface plus the
          placeholder codegen execution seams.
        - Reserved as the codegen-oriented room rather than a duplicate of the
          broad capability manual-runtime posture.

    Owned State:
        One `_codegen_system` - the only room type that owns an internal
        engine, attached to its `CodegenCommandSystem` during room init.

    Registration:
        MELDER KERNEL - guarded. Programmed by `Rift` from
        `RiftSpaceType.codegen`; never constructed directly.

    Subsystem Context:
        The top rung of the room ladder by capability, but deliberately NOT the
        superset of `CapabilityRiftSpace`. It owns one `CodegenSystem` beneath
        a `CodegenCommandSystem` facade.

    System Context:
        The counterintuitive design fact is that codegen is NOT capability plus
        more. This room keeps a SLIM selected runtime-helper subset rather than
        capability parity, and that narrowing is protective: a room that can
        generate and execute code already has the widest reach available, so
        pairing it with the full manual-mutation surface would multiply the ways
        a single mistake reaches the runtime.
        The engine underneath enforces order - validate BEFORE execute, build
        the live namespace only after validation is ACCEPTED, and keep lifecycle
        event publication inside the monitor layer. Codegen rooms also carry the
        full 34-command research family and emit full-source memory records, so
        what was generated is recoverable rather than merely having happened.
    """

    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. The codegen room type - a room that owns an internal CodegenSystem "
        "for validate/execute-code workflows plus a slim runtime-helper surface and the full "
        "research command family. You get it as a Rift's space when space_type=codegen."
    )
    __slots__ = [
        "_codegen_system",
    ]

    def __init__(
            self,
            owner_rift_id: str,
            *,
            rift: Rift,
            space_name: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
            rift_gate: Optional[RiftGate] = None,
            space_id: Optional[str] = None,
    ) -> None:
        """
        Internal

        Initialize a codegen room.

        Args:
            owner_rift_id:
                Canonical owning Rift id.
            rift:
                Owning `Rift` that manages projection-driven asset updates.
            space_name:
                Optional stable room name.
            metadata:
                Extensible room metadata.
            rift_gate:
                Optional Rift-owned gate bound to this room.
            space_id:
                Optional explicit room id.

        Returns:
            None.

        Contract:
            Delegates all storage and lifecycle behavior to `RiftSpace` while
            fixing the room kind to `codegen` and composing the codegen command
            surface.
        """
        super().__init__(
            owner_rift_id,
            rift=rift,
            space_name=space_name,
            space_kind="codegen",
            metadata=metadata,
            rift_gate=rift_gate,
            space_id=space_id,
        )
        self._codegen_system: CodegenSystem = CodegenSystem(
            rift=rift,
            space=self,
        )
        self.command_system.attach_codegen_system(self._codegen_system)

    def _create_command_system(self, rift: Rift) -> CommandSystem:
        """
        Build the codegen room's command system.

        Returns:
            CommandSystem: Codegen-room command surface.
        """
        return CodegenCommandSystem(
            rift=rift,
            space=self,
            workstation=self._workstation,
        )

    @property
    def command_system(self) -> CodegenCommandSystem:
        """
        Return the room-local codegen command system.

        Returns:
            CodegenCommandSystem: Codegen-room command surface owned by this
            room.
        """
        self.check_cleaned()
        return self._command_system

    @property
    def codegen_system(self) -> CodegenSystem:
        """
        Return the room-owned internal codegen system.

        Returns:
            CodegenSystem: Room-owned codegen system.
        """
        self.check_cleaned()
        return self._codegen_system

    def cleanup(self) -> None:
        """
        Internal

        Idempotently cleanup the owned codegen system before base room teardown.

        Returns:
            None.
        """
        if self._cleaned:
            return
        if self._codegen_system is not None:
            self._codegen_system.cleanup()
            del self._codegen_system
        super().cleanup()

