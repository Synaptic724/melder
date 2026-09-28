"""
Canonical scope-key construction for the mediator plane.

Dependency-free beyond the standard library.

Scope KEYS are the admission vocabulary - the strings the claim table matches on
- so they must be built one way, in one place. A typo in a hand-written key does
not fail loudly; it silently claims a scope nobody else claims, and the
transaction proceeds believing it is isolated when it is not. That failure mode
is why this helper exists rather than callers formatting their own strings.
"""

from enum import StrEnum


class ScopePrefix(StrEnum):
    """
    The closed vocabulary of scope-key namespaces.

    Purpose:
        Name the LEVELS this plane can isolate at, in one place, as a type
        rather than as three loose class strings.

    Contract:
        - CLOSED. Adding a level means adding a member here and a builder on
          `ScopeKey`. A caller reaching for a prefix that is not a member is
          the signal that a level is missing, not an invitation to format a
          string by hand.
        - `StrEnum`, matching every other vocabulary in this package
          (`ClaimMode`, `TransactionType`, `OutcomePolicy`, `SessionStatus`),
          because these values TRAVEL: they are embedded in the scope keys
          that land in claim tables, admission evidence, and logs, and must
          survive string-oriented APIs without special casing.
        - `WORLD` is a COMPLETE key on its own; the other two are namespaces
          that take a name. That asymmetry is real - there is exactly one
          world - and `ScopeKey` is where it is expressed.

    Threading:
        Stateless enum; safe to share across threads.

    Registration:
        MELDER KERNEL - guarded. Key vocabulary; never bound.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Closed vocabulary of scope-key namespaces - world,
        frame, subsystem. Build keys through `ScopeKey`, never by hand.
    """

    WORLD = "world"
    FRAME = "frame"
    SUBSYSTEM = "subsystem"


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

    Lifecycle / Cleanup:
        NEVER INSTANTIATED, so there is nothing to clean and no `Cleanable`
        contract. This is a namespace of static builders over the
        `ScopePrefix` vocabulary - it holds no instance state, and no code in
        this package or outside it constructs one. Stating that explicitly
        matters: "not `Cleanable`" should always be a reasoned position rather
        than something a reader has to infer from an absence.

    Threading:
        Pure and stateless; safe to call from any thread.

    Registration:
        MELDER KERNEL - guarded. Key vocabulary; never bound.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Canonical builders for plane scope keys. Never
        hand-format a scope key; a typo silently loses isolation.
    """

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
        return ScopePrefix.WORLD.value

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
        return "{0}:{1}".format(ScopePrefix.FRAME.value, frame_name)

    @staticmethod
    def subsystem(subsystem_name: str) -> str:
        """
        Return the scope key for one whole subsystem.

        Contract:
            Used for subsystem-wide transitions - activating or deactivating
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
        return "{0}:{1}".format(ScopePrefix.SUBSYSTEM.value, subsystem_name)

    @staticmethod
    def is_world(scope_key: str) -> bool:
        """
        Report whether `scope_key` is the world root key.

        Args:
            scope_key: The key to test.

        Returns:
            bool: True when the key is the world root.
        """
        return scope_key == ScopePrefix.WORLD.value
