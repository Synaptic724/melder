from typing import runtime_checkable, Protocol

from melder.utilities.interfaces.assets.icleanable import ICleanable


@runtime_checkable
class IFrameACLConfiguration(ICleanable, Protocol):
    """
    Typed frame ACL root configuration contract.

    Contract:
        - Represents one selected frame-local ACL bundle.
        - Owns the typed child configurations that describe view, command, and
          codegen policy for that bundle.
        - Is the unit selected by named frame ACL contract binding.
    """

    frame_name: str
    configuration_id: str
    locked: bool
    view_configuration: IFrameACLViewConfiguration
    command_configuration: IFrameACLCommandConfiguration
    codegen_configuration: IFrameACLCodegenConfiguration
