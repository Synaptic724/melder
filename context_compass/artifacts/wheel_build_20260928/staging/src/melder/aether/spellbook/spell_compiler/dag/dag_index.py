from typing import (
    Dict,
    List,
    Sequence,
    Tuple,
    Optional,
)

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
        - extend_path returns the same id for the same (parent, segment, member)
          triple; member is None except for collection members (see extend_path).
        - resolve_path_id returns None when any segment is unknown.
        - materialize_path returns a new tuple of path segments for diagnostics.

    Threading:
        - Not thread-safe. Builder-owned only.

    Subsystem Context:
        The path-interning substrate of the `dag` package. Every Phase-5
        `RootResolutionBlueprint` owns one, and Phase 8 mints its occurrence
        paths into it.

    System Context:
        Phase 5 (blueprints) and Phase 8 (occurrence paths) of the conjure pipeline.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Interns param-path segments into stable integer PathIds so Phase-5/8
        builds compare and extend paths cheaply: extend_path / resolve_path_id /
        materialize_path / format_path / clone. Builder-owned, not thread-safe.
    """
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
        self._child_ids: Dict[Tuple[int, str, Optional[str]], int] = {}
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

        del self._parent_ids
        del self._segments
        del self._depths
        del self._child_ids
        del self._formatted_path_by_id
        del self._root_path_id

    @property
    def root_path_id(self) -> int:
        """
        Return the root path id representing the empty path.
        """
        self.check_cleaned()
        return self._root_path_id

    def extend_path(
            self,
            parent_id: int,
            segment: str,
            *,
            member: Optional[str] = None,
    ) -> int:
        """
        Extend a parent path id with a single segment.

        Contract:
            - Returns existing ids for repeated (parent_id, segment, member)
              triples.
            - New ids are appended and assigned a depth of parent + 1.
            - `member` separates the members of one collection parameter. Each
              member gets its own child path id while the stored segment stays
              the parameter name, so paths that differ only by member materialize
              and format to the same string (name-based override keys are
              unchanged) but everything below different members stays a distinct
              occurrence: one `Existence.many` object per member, never one per
              collection. Non-collection edges pass None.

        Args:
            parent_id: PathId of the parent path.
            segment: Path segment (parameter name) to append.
            member: Collection member identity (the member's spell id), or None
                for a non-collection edge.

        Returns:
            int: PathId representing parent + segment (+ member).
        """
        self.check_cleaned()
        if parent_id is None:
            raise ValueError("parent_id must not be None.")
        if segment is None:
            raise ValueError("segment must not be None.")

        key = (parent_id, segment, member)
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
            - Returns the root id when segments are empty.
            - Returns None when any segment is unknown.
            - Follows member-less edges only: a path that exists only below a
              collection member (see extend_path) resolves to None.

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
            key = (current_id, segment, None)
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

        Args:
            path_id:
                Path id whose parent is requested.

        Returns:
            Optional[int]: Parent path id, or None for the root.
        """
        self.check_cleaned()
        if path_id == self._root_path_id:
            return None
        return self._parent_ids[path_id]

    def depth(self, path_id: int) -> int:
        """
        Return the depth (segment count) for the provided path id.

        Args:
            path_id:
                Path id whose depth is requested.

        Returns:
            int: Number of segments from the root to this path.
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
            parent_id = self._parent_ids[current_id]
            if parent_id is None:
                raise RuntimeError("PathRegistry encountered an empty parent id.")
            current_id = parent_id
        segments.reverse()
        return tuple(segments)

    def format_path(self, path_id: int) -> str:
        """
        Format a path id into the canonical 'a>b>c' string.

        Contract:
            Memoized: the formatted string is cached per path id after the first
            call.

        Args:
            path_id:
                Path id to format.

        Returns:
            str: Canonical `>`-joined path string (empty for the root).
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
