from typing import Dict, Protocol, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable


@runtime_checkable
class IFrameLinkContract(ICleanable, Protocol):
    """
    Rift-local per-frame ACL contract selection surface.

    Purpose:
        Define the minimal contract `Rift` needs for one engaged frame-local
        contract entry without binding the runtime to the concrete
        `FrameLinkContract` implementation.

    Contract:
        - Represents exactly one Rift/frame pairing.
        - Exposes stable contract identity plus the selected view/command/
          codegen contract names for that frame.
        - Exposes only detached metadata snapshots; callers must not mutate the
          underlying runtime object through returned mappings.
    """

    @property
    def contract_id(self) -> str:
        """
        Return the stable identifier for this Rift-local frame contract.
        """
        ...

    @property
    def rift_id(self) -> str:
        """
        Return the owning Rift identifier for this contract.
        """
        ...

    @property
    def frame_name(self) -> str:
        """
        Return the attached frame name for this contract.
        """
        ...

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Return a detached metadata snapshot for this contract.
        """
        ...

    def get_selected_contract_names(self) -> Dict[str, str]:
        """
        Return the selected view/command/codegen contract names for this frame.
        """
        ...

    def get_selected_contract_name(self) -> str:
        """
        Return the selected view contract name for this frame.
        """
        ...

    def describe(self) -> Dict[str, object]:
        """
        Return a detached summary of this per-frame contract.
        """
        ...
