from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence, Tuple, Dict, List, Optional
# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

@dataclass(frozen=True)
class SpellSocketDescriptor:
    """
    Internal

    Immutable description of a single constructor socket on a spell.

    This is the per-spell, *local* view that Phases 5–7 will stitch together
    into a full system-level blueprint.

    Attributes:
        spell_id:
            The version ID of the spell that owns this socket
            (``spell.spell_index.current``).

        param_name:
            The constructor parameter name (e.g. ``"logger"``).

        position:
            The 0-based index of the parameter in the constructor signature.

        socket_kind:
            The logical kind of socket:

            * NORMAL           – standard DI edge or plain parameter socket.
            * SPELL_CONTRACT   – cross-conduit spell contract socket.
            * MUTATION_CONTRACT – mutation contract socket.

        is_collection:
            True if this socket is a collection DI shape (e.g. list[...]).

        is_optional:
            True if the parameter is optional / has a default.

        target_spell_ids:
            The direct dependency spell version IDs that this socket *actually*
            resolved to during Phase 3, if any.

            For contract / mutation sockets that are not yet resolved, this
            will typically be an empty tuple.
    """
    __melder_internal__ = _mrg.sentinel
    spell_id: str
    param_name: str
    position: int
    socket_kind: SocketKind
    is_collection: bool
    is_optional: bool
    target_spell_ids: Tuple[str, ...]


class SpellLocalTopology(Cleanable):
    """
    Internal

    Local topology view for a single spell's constructor.

    This is intentionally small and immutable-ish. It is produced once
    during SpellCrafter Phase 3 and handed to :class:`SpellSystemStates`
    for aggregation, change-control, and eventual blueprint building.
    """
    __melder_internal__ = _mrg.sentinel
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
        """
        if self._cleaned:
            return
        self._cleaned = True
        for descriptor in self._by_param_name.values():
            descriptor.clear()
        self._by_param_name.clear()
        self._by_param_name = None
        self._sockets = None


    # ------------------------------------------------------------------ #
    # Properties                                                         #
    # ------------------------------------------------------------------ #

    @property
    def spell_id(self) -> str:
        return self._spell_id

    @property
    def sockets(self) -> Tuple[SpellSocketDescriptor, ...]:
        return self._sockets

    def iter_sockets(self) -> Tuple[SpellSocketDescriptor, ...]:
        """
        Convenience accessor to iterate sockets without exposing internals.
        """
        return self._sockets

    def get_sockets_for_param(self, param_name: str) -> Tuple[SpellSocketDescriptor, ...]:
        """
        Return all sockets whose constructor parameter name matches `param_name`.
        """
        sockets = self._by_param_name.get(param_name, ())
        return tuple(sockets)
