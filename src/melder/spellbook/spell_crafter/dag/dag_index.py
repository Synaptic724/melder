from dataclasses import dataclass, field
from typing import Dict, List, Iterable, Callable, Sequence, Tuple, Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spell_crafter.dag.target_spec import TargetSpec, TargetSpecKind
from melder.utilities.general_base.cleanable import Cleanable


class PathRegistry(Cleanable):
    """
    Internal

    Intern parameter path segments into stable integer PathIds.

    Purpose:
        Replace per-socket tuple path churn with compact ids that can be
        compared and extended cheaply during Phase 5 and Phase 8 builds.

    Contract:
        - PathIds are stable for the lifetime of the registry.
        - The root path id represents the empty path.
        - extend_path returns the same id for the same (parent, segment) pair.
        - resolve_path_id returns None when any segment is unknown.
        - materialize_path returns a new tuple of path segments for diagnostics.

    Threading:
        - Not thread-safe. Builder-owned only.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_root_path_id",
        "_parent_ids",
        "_segments",
        "_depths",
        "_child_ids",
        "_formatted_path_by_id",
    ]

    def __init__(self) -> None:
        """
        Initialize an empty path registry with the root path pre-seeded.

        Contract:
            - Path id `0` is reserved for the empty/root path.
            - Parent, segment, depth, and child-id tables start aligned to that
              root entry.
        """
        super().__init__()
        self._root_path_id = 0
        self._parent_ids: List[Optional[int]] = [None]
        self._segments: List[Optional[str]] = [None]
        self._depths: List[int] = [0]
        self._child_ids: Dict[Tuple[int, str], int] = {}
        self._formatted_path_by_id: Dict[int, str] = {self._root_path_id: ""}

    def cleanup(self) -> None:
        """
        Deterministically clear the registry contents.

        Contract:
            - Idempotent: safe to call multiple times.
            - Drops all internal lists and maps.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._parent_ids.clear()
        self._segments.clear()
        self._depths.clear()
        self._child_ids.clear()
        self._formatted_path_by_id.clear()
        self._parent_ids = None
        self._segments = None
        self._depths = None
        self._child_ids = None
        self._formatted_path_by_id = None
        self._root_path_id = None

    @property
    def root_path_id(self) -> int:
        """
        Return the root path id representing the empty path.
        """
        self.check_cleaned()
        return self._root_path_id

    def extend_path(self, parent_id: int, segment: str) -> int:
        """
        Extend a parent path id with a single segment.

        Contract:
            - Returns existing ids for repeated (parent_id, segment) pairs.
            - New ids are appended and assigned a depth of parent + 1.

        Args:
            parent_id: PathId of the parent path.
            segment: Path segment to append.

        Returns:
            int: PathId representing parent + segment.
        """
        self.check_cleaned()
        if parent_id is None:
            raise ValueError("parent_id must not be None.")
        if segment is None:
            raise ValueError("segment must not be None.")

        key = (parent_id, segment)
        existing = self._child_ids.get(key)
        if existing is not None:
            return existing

        parent_depth = self._depths[parent_id]
        new_id = len(self._segments)
        self._child_ids[key] = new_id
        self._parent_ids.append(parent_id)
        self._segments.append(segment)
        self._depths.append(parent_depth + 1)
        return new_id

    def resolve_path_id(self, segments: Sequence[str]) -> Optional[int]:
        """
        Resolve a sequence of path segments to a PathId.

        Contract:
            - Returns the root id when segments is empty.
            - Returns None when any segment is unknown.

        Args:
            segments: Path segments to resolve.

        Returns:
            Optional[int]: PathId if resolved; otherwise None.
        """
        self.check_cleaned()
        if segments is None:
            raise ValueError("segments must not be None.")
        current_id = self._root_path_id
        for segment in segments:
            key = (current_id, segment)
            next_id = self._child_ids.get(key)
            if next_id is None:
                return None
            current_id = next_id
        return current_id

    def parent_id(self, path_id: int) -> Optional[int]:
        """
        Return the parent PathId for the provided path id.

        Contract:
            - Returns None for the root path.
        """
        self.check_cleaned()
        if path_id == self._root_path_id:
            return None
        return self._parent_ids[path_id]

    def depth(self, path_id: int) -> int:
        """
        Return the depth (segment count) for the provided path id.
        """
        self.check_cleaned()
        return self._depths[path_id]

    def materialize_path(self, path_id: int) -> Tuple[str, ...]:
        """
        Materialize a path id into a tuple of path segments.

        Contract:
            - Returns a new tuple for each call.
            - Does not mutate the registry.
        """
        self.check_cleaned()
        if path_id == self._root_path_id:
            return ()
        segments: List[str] = []
        current_id = path_id
        while current_id != self._root_path_id:
            segment = self._segments[current_id]
            if segment is None:
                raise RuntimeError("PathRegistry encountered an empty segment.")
            segments.append(segment)
            current_id = self._parent_ids[current_id]
            if current_id is None:
                raise RuntimeError("PathRegistry encountered an empty parent id.")
        segments.reverse()
        return tuple(segments)

    def format_path(self, path_id: int) -> str:
        """
        Format a path id into the canonical 'a>b>c' string.
        """
        self.check_cleaned()
        path_text = self._formatted_path_by_id.get(path_id)
        if path_text is not None:
            return path_text
        path_text = ">".join(self.materialize_path(path_id))
        self._formatted_path_by_id[path_id] = path_text
        return path_text

    def clone(self) -> "PathRegistry":
        """
        Clone the registry to decouple derived blueprints.

        Contract:
            - Returns a new PathRegistry with identical path ids.
            - Copies internal lists/maps to avoid shared mutation.
        """
        self.check_cleaned()
        cloned = PathRegistry()
        cloned._root_path_id = self._root_path_id
        cloned._parent_ids = list(self._parent_ids)
        cloned._segments = list(self._segments)
        cloned._depths = list(self._depths)
        cloned._child_ids = dict(self._child_ids)
        cloned._formatted_path_by_id = dict(self._formatted_path_by_id)
        return cloned


@dataclass(frozen=True, slots=True)
class SocketRef:
    """
    Internal

    Identifies a *single* socket on a DAG node in a way that's stable for
    override targeting.

    Attributes:
        node_id:
            The spell version ID owning this socket (e.g. spell.spell_index.current``).

        param_name:
            The parameter name on the constructor (e.g. ``"logger"``).

        param_path_id:
            Interned path id from the RootResolutionBlueprint PathRegistry.

        socket_kind:
            The logical kind of socket – normal DI, SpellContract, MutationContract.
    """
    __melder_internal__ = _mrg.sentinel
    node_id: str
    param_name: str
    param_path_id: int
    socket_kind: SocketKind
    _hash: int = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Precompute the immutable hash used for socket-ref dictionary keys."""
        object.__setattr__(
            self,
            "_hash",
            hash((self.node_id, self.param_name, self.param_path_id, self.socket_kind)),
        )

    def __hash__(self) -> int:
        """Return the precomputed stable hash for this socket reference."""
        return self._hash


class DagIndex(Cleanable):
    """
    Internal

    Lightweight index over :class:`SocketRef` instances, keyed by:

    * exact param path id (interned in a PathRegistry) and
    * param name (``"repo"``).

    This is the shared substrate for `spell_override` and `mutation_override`
    targeting. It is intentionally dumb: no graph logic, no Melder awareness.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_path_registry",
        "_by_exact_path_id",
        "_by_name",
        "_built",
    ]

    def __init__(self, path_registry: Optional[PathRegistry] = None) -> None:
        """
        Initialize an empty socket index.

        Contract:
            - Uses the supplied `PathRegistry` when provided.
            - Otherwise allocates a fresh registry owned by this index.
            - Starts with empty exact-path and name buckets.
        """
        super().__init__()
        self._path_registry: PathRegistry = (
            path_registry if path_registry is not None else PathRegistry()
        )
        self._by_exact_path_id: Dict[int, List[SocketRef]] = {}
        self._by_name: Dict[str, List[SocketRef]] = {}
        self._built: bool = False


    def cleanup(self) -> None:
        """
        Clean up internal references.
        """
        if self._cleaned:
            return

        self._cleaned = True
        if self._path_registry is not None:
            self._path_registry.cleanup()
        self._path_registry = None
        self._by_exact_path_id.clear()
        self._by_exact_path_id = None
        self._by_name.clear()
        self._by_name = None
        self._built = None

    @property
    def path_registry(self) -> PathRegistry:
        """
        Return the PathRegistry used by this index.
        """
        self.check_cleaned()
        return self._path_registry

    @property
    def is_built(self) -> bool:
        """
        Return True when the index maps have been populated.
        """
        self.check_cleaned()
        return bool(self._built)

    def rebuild(self, sockets: Optional[Iterable[SocketRef]]) -> None:
        """
        Rebuild index maps from the provided socket refs.

        Contract:
            - Clears any existing index buckets before rebuilding.
            - Marks the index as built after completion.
        """
        self.check_cleaned()
        self._by_exact_path_id.clear()
        self._by_name.clear()
        if sockets is not None:
            for socket in sockets:
                path_id = socket.param_path_id
                sockets_by_path_id = self._by_exact_path_id.get(path_id)
                if sockets_by_path_id is None:
                    self._by_exact_path_id[path_id] = [socket]
                else:
                    sockets_by_path_id.append(socket)

                param_name = socket.param_name
                sockets_by_name = self._by_name.get(param_name)
                if sockets_by_name is None:
                    self._by_name[param_name] = [socket]
                else:
                    sockets_by_name.append(socket)
        self._built = True

    def add_socket(self, socket: SocketRef) -> None:
        """
        Add a socket reference to the index.
        """
        path_id = socket.param_path_id
        sockets_by_path_id = self._by_exact_path_id.get(path_id)
        if sockets_by_path_id is None:
            self._by_exact_path_id[path_id] = [socket]
        else:
            sockets_by_path_id.append(socket)

        param_name = socket.param_name
        sockets_by_name = self._by_name.get(param_name)
        if sockets_by_name is None:
            self._by_name[param_name] = [socket]
        else:
            sockets_by_name.append(socket)
        self._built = True

    def get_by_exact_path(self, path: Sequence[str]) -> List[SocketRef]:
        """
        Retrieve all sockets that share this exact param path.

        Contract:
            - Returns a defensive copy to prevent external mutation of
              internal index buckets.
        """
        path_id = self._path_registry.resolve_path_id(path)
        if path_id is None:
            return []
        sockets = self._by_exact_path_id.get(path_id)
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
        for sockets in self._by_exact_path_id.values():
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
        """Initialize the targeting engine over one prebuilt `DagIndex`."""
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
        """
        Resolve a PATH target spec against the exact-path bucket.

        Contract:
            - Raises when the path is empty or no eligible sockets match.
            - Applies `filter_fn` after exact-path lookup.
        """
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
        """
        Resolve a UNIQUE target spec and enforce single-match semantics.

        Contract:
            - Raises when the param name is missing.
            - Raises when zero or multiple eligible sockets match.
        """
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
        """
        Resolve a BROADCAST target spec against the name bucket.

        Contract:
            - Raises when the param name is missing.
            - Raises when no eligible sockets match.
            - Returns every eligible socket sharing that parameter name.
        """
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
    spell's constructor sockets (param_path_id represents ``(param_name,)``).

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

            param_path_id -> (socket.param_name,)
        """
        if owner_spell_id is None:
            raise ValueError("owner_spell_id must not be None.")

        index = DagIndex()
        path_registry = index.path_registry
        root_path_id = path_registry.root_path_id
        for socket in sockets:
            # Avoid circular imports by using duck-typing on the descriptor.
            param_name = socket.param_name
            path_id = path_registry.extend_path(root_path_id, param_name)
            ref = SocketRef(
                node_id=owner_spell_id,
                param_name=param_name,
                param_path_id=path_id,
                socket_kind=socket.socket_kind,
            )
            index.add_socket(ref)
        return index
