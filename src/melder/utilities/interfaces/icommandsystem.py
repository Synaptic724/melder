from typing import Any, Dict, List, Optional, Protocol, Tuple, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable

@runtime_checkable
class ICommandSystem(ICleanable, Protocol):
    """
    Interface for the room-local command system.
    """

    @property
    def command_system_id(self) -> str:
        """
        Return the stable command-system identifier.
        """
        ...

    @property
    def owner_space_id(self) -> str:
        """
        Return the owning room identifier.
        """
        ...

    def link_frame(self, frame_name: str) -> None:
        """
        Engage one target frame for the owning Rift.
        """
        ...

    def get_nexus_frame(self, frame_name: Optional[str] = None) -> object:
        """
        Return one rooted Nexus-managed conduit through the command surface.
        """
        ...

    def describe_spells_in_conduit(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Return the spell description payloads exposed by one conduit.
        """
        ...

    def get_resolution_state(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return the conduit-scoped resolution state for one conduit.
        """
        ...

    def get_active_spellspace(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return the active spellspace for one conduit, if any.
        """
        ...

    def find_spell_id(
            self,
            conduit_id: str,
            spellframe: str,
            spell_name: str,
            binding_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return the current spell id resolved from logical spell identifiers.
        """
        ...

    def find_spell_key(
            self,
            conduit_id: str,
            spellframe: str,
            spell_name: str,
            binding_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return the spellbook key resolved from logical spell identifiers.
        """
        ...

    def get_spell_permissions(
            self,
            conduit_id: str,
            spell_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return the permissions string for one spell inside one conduit.
        """
        ...

    def snapshot_state(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Return a detached snapshot of one conduit state payload.
        """
        ...

    def get_conduit_by_id(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one live conduit object by id.
        """
        ...

    def get_conduit_by_name(
            self,
            conduit_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one live conduit object by name.
        """
        ...

    def get_spell_by_source_id(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one live spell object using a published spell source id.
        """
        ...

    def get_spell_by_index_id(
            self,
            spell_index_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one live spell object by stable spell index id.
        """
        ...

    def get_spell_by_id(
            self,
            spell_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one live spell object by current spell id.
        """
        ...

    def get_target_attribute(self, attribute_name: str) -> object:
        """
        Return one attribute value from the current workstation target.
        """
        ...

    def get_target_method(self, method_name: str) -> object:
        """
        Return one method/callable from the current workstation target.
        """
        ...

    def execute_target_method(
            self,
            method_name: str,
            *args: Any,
            bind_as_name: Optional[str] = None,
            bind_as_store: str = "objects",
            bind_result_weak_ref: Optional[bool] = None,
            **kwargs: Any
    ) -> object:
        """
        Execute one method on the current workstation target.
        """
        ...

    def list_supported_command_methods(self) -> Tuple[str, ...]:
        """
        Return the public command methods supported by this room surface.
        """
        ...
