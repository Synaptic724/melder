from typing import TYPE_CHECKING, Callable, Dict, Optional, Protocol, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.icommandsystem import ICommandSystem
from melder.utilities.interfaces.iframeviewer import IFrameViewer
from melder.utilities.interfaces.iriftmemorysystem import IRiftMemorySystem
from melder.utilities.interfaces.iworkstation import IWorkstation

if TYPE_CHECKING:
    from melder.nexus.rift.rift_space.event_system.rift_event_system import RiftEventSystem

@runtime_checkable
class IRiftSpace(ICleanable, Protocol):
    """
    Interface for the base RiftSpace room object.
    """

    @property
    def space_id(self) -> str:
        """
        Return the stable identifier for this RiftSpace instance.
        """
        ...

    @property
    def space_name(self) -> Optional[str]:
        """
        Return the human-readable space name, if one has been assigned.
        """
        ...

    @property
    def owner_rift_id(self) -> str:
        """
        Return the identifier of the Rift that owns this space.
        """
        ...

    @property
    def space_kind(self) -> str:
        """
        Return the kind discriminator used to classify this RiftSpace.
        """
        ...

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Return the metadata mapping associated with this space.
        """
        ...

    @property
    def event_system(self) -> "RiftEventSystem":
        """
        Return the room-local event system.
        """
        ...

    @property
    def memory_system(self) -> IRiftMemorySystem:
        """
        Return the room-local memory sequencing system.
        """
        ...

    @property
    def frame_viewer(self) -> IFrameViewer:
        """
        Return the attached frame-surface viewer.
        """
        ...

    @property
    def workstation(self) -> IWorkstation:
        """
        Return the room-local workstation canvas owned by this space.
        """
        ...

    @property
    def command_system(self) -> ICommandSystem:
        """
        Return the room-local command system owned by this space.
        """
        ...

    def register_action_pre_hook(
            self,
            category: str,
            action_name: str,
            callback: Callable[[], None],
    ) -> str:
        """
        Register one pre-action hook for the selected category and action.
        """
        ...

    def register_action_post_hook(
            self,
            category: str,
            action_name: str,
            callback: Callable[[], None],
    ) -> str:
        """
        Register one post-action hook for the selected category and action.
        """
        ...

    def unregister_action_hook(self, subscription_id: str) -> None:
        """
        Unregister one action-hook subscription by id.
        """
        ...


