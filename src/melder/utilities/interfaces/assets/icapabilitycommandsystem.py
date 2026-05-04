import threading
from threading import RLock
from types import ModuleType
from typing import runtime_checkable, Type, Protocol, Optional, List, Union, Dict, Any, Iterable, Iterator, Callable, \
    Tuple, Mapping, Set, Sequence, Self

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.spellbook.existence.existence import Existence
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


from melder.utilities.interfaces.assets.icommandsystem import ICommandSystem

@runtime_checkable
class ICapabilityCommandSystem(ICommandSystem, Protocol):
    """
    Interface for the capability-room command system.
    """

    def get_conduit_cloud(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return the live conduit cloud for one hosted frame.
        """
        ...

    def list_conduit_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ...]:
        """
        Return the command-enabled published conduit ids for one frame.
        """
        ...

    def list_conduit_names(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ...]:
        """
        Return the command-enabled published conduit names for one frame.
        """
        ...

    def count_conduits(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> int:
        """
        Return the number of command-enabled published conduits for one frame.
        """
        ...

    def has_conduit_id(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> bool:
        """
        Return whether one published command-enabled conduit id exists.
        """
        ...

    def has_conduit_name(
            self,
            conduit_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> bool:
        """
        Return whether one published command-enabled conduit name exists.
        """
        ...

    def find_conduit_id_by_name(
            self,
            conduit_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Optional[str]:
        """
        Return the published command-enabled conduit id for one conduit name.
        """
        ...

    def get_links(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[object, ...]:
        """
        Return the current peer links for one conduit.
        """
        ...

    def create_lesser_conduit(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Create one lesser conduit beneath an existing conduit.
        """
        ...

    def create_cluster(
            self,
            conduit_id: str,
            cluster_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> None:
        """
        Create one cluster through an existing conduit.
        """
        ...

    def delete_cluster(
            self,
            conduit_id: str,
            cluster_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> None:
        """
        Delete one cluster through an existing conduit.
        """
        ...

    def join_cluster(
            self,
            conduit_id: str,
            cluster_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> None:
        """
        Join one conduit to one cluster through the capability command surface.
        """
        ...

    def leave_cluster(
            self,
            conduit_id: str,
            cluster_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> None:
        """
        Remove one conduit from one cluster through the capability command surface.
        """
        ...

    def list_clusters(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ...]:
        """
        Return the cluster names visible from one conduit.
        """
        ...

    def link(
            self,
            source_conduit_id: str,
            target_conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> bool:
        """
        Link two conduits through the capability command surface.
        """
        ...

    def sever_link(
            self,
            source_conduit_id: str,
            target_conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> bool:
        """
        Sever one conduit link through the capability command surface.
        """
        ...

    def meld(
            self,
            conduit_id: str,
            spell_name: Optional[str] = None,
            *,
            spell: Optional[object] = None,
            spellframe: Optional[object] = None,
            binding_name: Optional[str] = None,
            frame_name: Optional[str] = None,
            spell_override: Optional[dict | list | tuple] = None,
    ) -> object:
        """
        Resolve and activate one spell through a command-selected conduit.
        """
        ...

    def meld_existing_spell(
            self,
            conduit_id: str,
            spell_name: Optional[str] = None,
            *,
            spell: Optional[object] = None,
            spellframe: Optional[object] = None,
            binding_name: Optional[str] = None,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one already-live spell runtime object through a selected conduit.
        """
        ...

    def get_lesser_conduit(
            self,
            parent_conduit_id: str,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one lesser conduit linked beneath a parent conduit.
        """
        ...

    def get_initiated_conduit(
            self,
            conduit_id: str,
            peer_conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one outbound linked conduit from a source conduit.
        """
        ...

    def get_provider_conduit(
            self,
            conduit_id: str,
            peer_conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one inbound provider conduit for a source conduit.
        """
        ...

    def get_initiated_conduits(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[object, ...]:
        """
        Return the outbound linked conduits for one conduit.
        """
        ...

    def get_provider_conduits(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[object, ...]:
        """
        Return the inbound provider conduits for one conduit.
        """
        ...

    def get_contracted_conduits(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return the contracted peer conduits for one conduit.
        """
        ...

    def get_spell_in_contracts(
            self,
            conduit_id: str,
            spell_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one contracted spell lookup result from a conduit.
        """
        ...

    def get_spells_in_contract_by_conduit(
            self,
            conduit_id: str,
            peer_conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return contracted spell data keyed by peer conduit id.
        """
        ...

    def get_spells_in_contract_by_conduit_name(
            self,
            conduit_id: str,
            conduit_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return contracted spell data keyed by peer conduit name.
        """
        ...
