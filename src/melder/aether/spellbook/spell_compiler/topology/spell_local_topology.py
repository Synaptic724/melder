from dataclasses import dataclass
from typing import Sequence, Tuple, Dict, List, Optional, ClassVar



# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


@dataclass(frozen=True, slots=True)
class SpellSocketDescriptor:
    """
    Internal

    Immutable description of a single constructor socket on a spell.

    This is the per-spell, *local* view that Phases 5–7 will stitch together
    into a full system-level blueprint.

    Attributes:
        spell_id:
            The version ID of the spell that owns this socket
            (spell.spell_index.selected_spell_id``).

        param_name:
            The constructor parameter name (e.g. ``"logger"``).

        position:
            The 0-based index of the parameter in the constructor signature.

        socket_kind:
            The logical kind of socket:

            * NORMAL – standard DI edge or plain parameter socket.
            * SPELL_CONTRACT – cross-conduit spell contract socket.

        is_collection:
            True if this socket is a collection DI shape (e.g. list[...]).

        is_optional:
            True if the parameter is optional / has a default.

        target_spell_ids:
            The direct dependency spells version IDs that this socket *actually*
            resolved to during Phase 3, if any.

            For contract / mutation sockets that are not yet resolved, this
            will typically be an empty tuple.

        dependency_key:
            Canonical "(frame_key, binding_key)" for NORMAL DI sockets.
            This is populated for single/collection/SpellMap sockets that
            participate in DI resolution. For collection sockets, the frame
            key is used for targeted revalidation, while the binding key
            remains informational.

        contract_key:
            Canonical "(frame_key, binding_key)" for contract sockets.
            This is populated with SPELL_CONTRACT sockets to support
            system-level contract validation.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    spell_id: str
    param_name: str
    position: int
    socket_kind: SocketKind
    is_collection: bool
    is_optional: bool
    target_spell_ids: Tuple[str, ...]
    dependency_key: Optional[Tuple[str, str]] = None
    contract_key: Optional[Tuple[str, str]] = None


class SpellLocalTopology(Cleanable):
    """
    Local topology view for a single spell's constructor.

    This is intentionally small and immutable-ish. It is produced once
    during SpellCrafter Phase 3 and handed to: class:`SpellSystemStates`
    for aggregation, change-control, and eventual blueprint building.

    Contract:
    - Holds the per-spell socket view produced during local topology analysis.
    - Owns the socket tuple and the parameter-name index derived from it.
    - Is effectively immutable after construction; callers read from it but do
      not mutate it in place.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_spell_id",
        "_sockets",
        "_by_param_name",
    ]

    def __init__(
            self,
            spell_id: str,
            sockets: Sequence[SpellSocketDescriptor],
    ) -> None:
        """
        Initialize one local topology snapshot for a spell.

        Args:
            spell_id: Spell/version id this topology belongs to.
            sockets: Socket descriptors discovered for the spell's constructor.
        Contract:
            - `spell_id` is required.
            - Stores sockets as a tuple to keep the topology stable after
              construction.
            - Builds a parameter-name index for fast grouped lookup.
        """
        super().__init__()

        if spell_id is None:
            raise ValueError("spell_id must not be None.")

        self._spell_id: str = spell_id
        self._sockets: Tuple[SpellSocketDescriptor, ...] = tuple(sockets)
        self._by_param_name: Dict[str, List[SpellSocketDescriptor]] = {}

        for socket in self._sockets:
            self._by_param_name.setdefault(socket.param_name, []).append(socket)


    # ------------------------------------------------------------------ #
    # Cleanup                                                            #
    # ------------------------------------------------------------------ #

    def cleanup(self) -> None:
        """
        Deterministically tear down this topology.

        This is primarily to keep the lifecycle consistent with other Melder
        artifacts and to assist GC in long-running systems.

        Contract:
            - Safe to call more than once.
            - Clears the parameter-name index before dropping references.
            - Leaves future callers to fail through `check_cleaned()`.
        """
        if self._cleaned:
            return
        self._cleaned = True
        for descriptor in self._by_param_name.values():
            descriptor.clear()
        self._by_param_name.clear()

        del self._by_param_name
        del self._sockets


    # ------------------------------------------------------------------ #
    # Properties                                                         #
    # ------------------------------------------------------------------ #

    @property
    def spell_id(self) -> str:
        """
        Return the spell/version id this topology belongs to.

        Returns:
            str: Owning spell id.
        """
        return self._spell_id

    @property
    def sockets(self) -> Tuple[SpellSocketDescriptor, ...]:
        """
        Return the socket tuple for this topology.

        Returns:
            Tuple[SpellSocketDescriptor, ...]: Socket descriptors in stored
            order.
        """
        return self._sockets

    def iter_sockets(self) -> Tuple[SpellSocketDescriptor, ...]:
        """
        Return the socket tuple for iteration.

        Contract:
            Returns the stored tuple directly; callers should treat it as
            read-only.
        """
        return self._sockets

    def get_sockets_for_param(self, param_name: str) -> Tuple[SpellSocketDescriptor, ...]:
        """
        Return all sockets whose constructor parameter name matches `param_name`.

        Contract:
            - Returns an empty tuple when the parameter name is unknown.
            - Returns a detached tuple even though the underlying index stores
              lists.
        """
        sockets = self._by_param_name.get(param_name, ())
        return tuple(sockets)
