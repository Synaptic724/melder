from dataclasses import dataclass, field
from typing import Dict, List, Iterable, Callable, Sequence, Tuple, Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spell_crafter.dag.target_spec import TargetSpec, TargetSpecKind
from melder.utilities.general_base.cleanable import Cleanable


@dataclass(frozen=True, slots=True)
class SocketRef:
    """
    Internal

    Identifies a *single* socket on a DAG node in a way that's stable for
    override targeting.

    Attributes:
        node_id:
            The spell version ID owning this socket (e.g. ``spell.spell_index.current``).

        param_name:
            The parameter name on the constructor (e.g. ``"logger"``).

        param_path:
            The param path from the root spell (e.g. ``("orchestrator", "order_service", "repo")``).

        socket_kind:
            The logical kind of socket – normal DI, SpellContract, MutationContract.
    """
    __melder_internal__ = _mrg.sentinel
    node_id: str
    param_name: str
    param_path: Tuple[str, ...]
    socket_kind: SocketKind
    _hash: int = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "_hash",
            hash((self.node_id, self.param_name, self.param_path, self.socket_kind)),
        )

    def __hash__(self) -> int:
        return self._hash


class DagIndex(Cleanable):
    """
    Internal

    Lightweight index over :class:`SocketRef` instances, keyed by:

    * exact param path tuple (``("a", "b", "c")``) and
    * param name (``"repo"``).

    This is the shared substrate for `spell_override` and `mutation_override`
    targeting. It is intentionally dumb: no graph logic, no Melder awareness.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + ["_by_exact_path", "_by_name"]

    def __init__(self) -> None:
        super().__init__()
        self._by_exact_path: Dict[Tuple[str, ...], List[SocketRef]] = {}
        self._by_name: Dict[str, List[SocketRef]] = {}


    def cleanup(self) -> None:
        """
        Clean up internal references.
        """
        if self._cleaned:
            return

        self._cleaned = True
        self._by_exact_path.clear()
        self._by_exact_path = None
        self._by_name.clear()
        self._by_name = None

    @staticmethod
    def _path_key(path: Sequence[str]) -> Tuple[str, ...]:
        if isinstance(path, tuple):
            return path
        return tuple(path)

    def add_socket(self, socket: SocketRef) -> None:
        """
        Add a socket reference to the index.
        """
        key = self._path_key(socket.param_path)
        sockets_by_path = self._by_exact_path.get(key)
        if sockets_by_path is None:
            sockets_by_path = []
            self._by_exact_path[key] = sockets_by_path
        sockets_by_path.append(socket)

        sockets_by_name = self._by_name.get(socket.param_name)
        if sockets_by_name is None:
            sockets_by_name = []
            self._by_name[socket.param_name] = sockets_by_name
        sockets_by_name.append(socket)

    def get_by_exact_path(self, path: Sequence[str]) -> List[SocketRef]:
        """
        Retrieve all sockets that share this exact param path.

        Contract:
            - Returns a defensive copy to prevent external mutation of
              internal index buckets.
        """
        key = self._path_key(path)
        sockets = self._by_exact_path.get(key)
        if not sockets:
            return []
        return list(sockets)

    def get_by_name(self, name: str) -> List[SocketRef]:
        """
        Retrieve all sockets whose param name matches the given value.

        Contract:
            - Returns a defensive copy to prevent external mutation of
              internal index buckets.
        """
        sockets = self._by_name.get(name)
        if not sockets:
            return []
        return list(sockets)

    def iter_all_sockets(self) -> Iterable[SocketRef]:
        """
        Iterate all known sockets. Primarily useful for debugging / tests.
        """
        seen: Dict[SocketRef, None] = {}
        for sockets in self._by_exact_path.values():
            for socket in sockets:
                if socket in seen:
                    continue
                seen[socket] = None
                yield socket


class DagTargetingEngine(Cleanable):
    """
    Internal

    Shared targeting core for overrides.

    Given a :class:`DagIndex` and a :class:`TargetSpec`, resolves the set of
    :class:`SocketRef` instances that should be affected by a particular
    override key.

    It does *not* know about Melder, SpellCrafter, or contracts – a caller
    provides a `filter_fn` to constrain which sockets are eligible.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + ["_index",]

    def __init__(self, index: DagIndex) -> None:
        super().__init__()
        if index is None:
            raise ValueError("index must not be None.")
        self._index: DagIndex = index

    def cleanup(self) -> None:
        """
        Clean up internal references.
        """
        if self._cleaned:
            return

        self._cleaned = True
        self._index.cleanup()
        self._index = None

    def resolve(
            self,
            spec: TargetSpec,
            filter_fn: Callable[[SocketRef], bool],
    ) -> List[SocketRef]:
        """
        Resolve a :class:`TargetSpec` to a list of sockets.

        Cardinality guarantees:

        * PATH:
            - 0 matches -> RuntimeError
            - 1+ matches -> valid

        * UNIQUE (*param):
            - 0 matches -> RuntimeError
            - >1 matches -> RuntimeError
            - 1 match -> valid

        * BROADCAST (**param):
            - 0 matches -> RuntimeError
            - 1+ matches -> valid
        """
        if spec is None:
            raise ValueError("spec must not be None.")
        if filter_fn is None:
            raise ValueError("filter_fn must not be None.")

        if spec.kind is TargetSpecKind.PATH:
            return self._resolve_path(spec, filter_fn)
        if spec.kind is TargetSpecKind.UNIQUE:
            return self._resolve_unique(spec, filter_fn)
        if spec.kind is TargetSpecKind.BROADCAST:
            return self._resolve_broadcast(spec, filter_fn)

        raise RuntimeError(f"Unsupported TargetSpecKind: {spec.kind!r}")

    # ------------------------------------------------------------------ #
    # Internal helpers                                                   #
    # ------------------------------------------------------------------ #

    def _resolve_path(
            self,
            spec: TargetSpec,
            filter_fn: Callable[[SocketRef], bool],
    ) -> List[SocketRef]:
        if not spec.path:
            raise RuntimeError("PATH TargetSpec has no path segments.")
        candidates = self._index.get_by_exact_path(spec.path)
        matches = [socket for socket in candidates if filter_fn(socket)]
        if not matches:
            path_str = ">".join(spec.path)
            raise RuntimeError(f"No sockets found for override path '{path_str}'.")
        return matches

    def _resolve_unique(
            self,
            spec: TargetSpec,
            filter_fn: Callable[[SocketRef], bool],
    ) -> List[SocketRef]:
        if not spec.param_name:
            raise RuntimeError("UNIQUE TargetSpec has no param_name.")
        candidates = self._index.get_by_name(spec.param_name)
        matches = [socket for socket in candidates if filter_fn(socket)]
        count = len(matches)
        if count == 0:
            raise RuntimeError(
                f"No sockets found for unique override '*{spec.param_name}'."
            )
        if count > 1:
            raise RuntimeError(
                f"Unique override '*{spec.param_name}' matched {count} sockets; "
                f"expected exactly one."
            )
        return matches

    def _resolve_broadcast(
            self,
            spec: TargetSpec,
            filter_fn: Callable[[SocketRef], bool],
    ) -> List[SocketRef]:
        if not spec.param_name:
            raise RuntimeError("BROADCAST TargetSpec has no param_name.")
        candidates = self._index.get_by_name(spec.param_name)
        matches = [socket for socket in candidates if filter_fn(socket)]
        if not matches:
            raise RuntimeError(
                f"No sockets found for broadcast override '**{spec.param_name}'."
            )
        return matches


class DagIndexBuilder:
    """
    Internal

    Placeholder index builder.

    In this stage we only support building a shallow index for a *single*
    spell's constructor sockets (param_path is just ``(param_name,)``).

    Phases 5–7 will extend this to walk the full system blueprint and assign
    deep param paths (``\"orchestrator>order_service>repo\"`` style).
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = ()
    @staticmethod
    def build_shallow(
            owner_spell_id: str,
            sockets: Sequence["SpellSocketDescriptor"],  # defined in topology module
    ) -> DagIndex:
        """
        Build a shallow :class:`DagIndex` from a spell's local topology.

        Each socket is indexed under a single-segment param path:

            param_path = (socket.param_name,)
        """
        if owner_spell_id is None:
            raise ValueError("owner_spell_id must not be None.")

        index = DagIndex()
        for socket in sockets:
            # Avoid circular imports by using duck-typing on the descriptor.
            param_name = socket.param_name
            path = (param_name,)
            ref = SocketRef(
                node_id=owner_spell_id,
                param_name=param_name,
                param_path=path,
                socket_kind=socket.socket_kind,
            )
            index.add_socket(ref)
        return index
