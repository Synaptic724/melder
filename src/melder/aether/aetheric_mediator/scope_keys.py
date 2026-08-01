"""
Canonical scope-key construction for the mediator plane.

Dependency-free beyond the standard library.

Scope KEYS are the admission vocabulary - the strings the claim table matches on
- so they must be built one way, in one place. A typo in a hand-written key does
not fail loudly; it silently claims a scope nobody else claims, and the
transaction proceeds believing it is isolated when it is not. That failure mode
is why this helper exists rather than callers formatting their own strings.
"""

from typing import ClassVar


class ScopeKey:
    """
    Builders for every scope key the plane recognises.

    Purpose:
        Make scope keys constructible only one way, so isolation cannot be
        silently lost to a formatting mistake.

    Contract:
        - Keys are FLAT and NAMESPACED: a single string space with a subsystem
          or level prefix. Flat keys keep acquisition O(requested scopes) dict
          operations; a nested structure would require traversal on the hot
          admission path.
        - The HIERARCHY IS EXPRESSED BY MODE, NOT BY KEY SHAPE. `world` is the
          parent of every frame, but that relationship lives in how callers
          claim it - `INTENT` on `world` plus `EXCLUSIVE` on `frame:<name>` -
          not in string nesting. This is the DevOps pattern: `ix` on the owning
          parent, `x` on the participants.
        - Builders REJECT empty names rather than producing a degenerate key
          like `frame:`, which would collide with every other empty-named
          claim and quietly serialise unrelated work.

    Threading:
        Pure and stateless; safe to call from any thread.

    Registration:
        MELDER KERNEL - guarded. Key vocabulary; never bound.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Canonical builders for plane scope keys. Never
        hand-format a scope key; a typo silently loses isolation.
    """

    WORLD: ClassVar[str] = "world"
    FRAME_PREFIX: ClassVar[str] = "frame"
    SUBSYSTEM_PREFIX: ClassVar[str] = "subsystem"

    @staticmethod
    def world() -> str:
        """
        Return the root scope key covering the entire live world.

        Contract:
            Claimed EXCLUSIVE this is the whole-world lock - the behaviour the
            crystallizer's `LoadGate` provides today. Claimed INTENT it is the
            parent marker that lets disjoint frame work proceed beneath it.

        Returns:
            str: The world scope key.
        """
        return ScopeKey.WORLD

    @staticmethod
    def frame(frame_name: str) -> str:
        """
        Return the scope key for one named frame.

        Args:
            frame_name: Canonical frame name.

        Returns:
            str: `frame:<frame_name>`.

        Raises:
            ValueError: If `frame_name` is empty or whitespace-only.
        """
        if not frame_name or not frame_name.strip():
            raise ValueError(
                "ScopeKey.frame requires a non-empty frame name; an empty key "
                "collides with every other empty-named claim."
            )
        return "{0}:{1}".format(ScopeKey.FRAME_PREFIX, frame_name)

    @staticmethod
    def subsystem(subsystem_name: str) -> str:
        """
        Return the scope key for one whole subsystem.

        Contract:
            Used for subsystem-wide transitions - enabling or disabling
            MutationResearch, Nexus, or the Crystallizer - where the unit of
            isolation is the subsystem itself rather than any frame.

        Args:
            subsystem_name: Stable lowercase subsystem name.

        Returns:
            str: `subsystem:<subsystem_name>`.

        Raises:
            ValueError: If `subsystem_name` is empty or whitespace-only.
        """
        if not subsystem_name or not subsystem_name.strip():
            raise ValueError(
                "ScopeKey.subsystem requires a non-empty subsystem name."
            )
        return "{0}:{1}".format(ScopeKey.SUBSYSTEM_PREFIX, subsystem_name)

    @staticmethod
    def is_world(scope_key: str) -> bool:
        """
        Report whether `scope_key` is the world root key.

        Args:
            scope_key: The key to test.

        Returns:
            bool: True when the key is the world root.
        """
        return scope_key == ScopeKey.WORLD
