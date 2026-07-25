from typing import Protocol, runtime_checkable

@runtime_checkable
class ICleanable(Protocol):
    """
    Protocol definition for Cleanable.

    This protocol mirrors the public API of the Cleanable
    abstract base class.

    Purpose:
        Let a caller depend on the CLEANUP CONTRACT structurally, without
        inheriting `Cleanable` or importing it at runtime.

    WHY A PROTOCOL EXISTS BESIDE THE ABC:
        `Cleanable` is the ABC every Melder object actually inherits. This is
        the structural mirror of its public surface, for the two cases the ABC
        cannot serve:
        - Typing-only positions where importing the concrete base would create
          runtime import pressure for no benefit.
        - Foreign objects that implement the same shape without being part of
          Melder's inheritance chain.

        Per the repository interface rule, prefer the concrete `Cleanable` type
        with a `TYPE_CHECKING` import when you simply need the name. Reach for
        this Protocol only when the STRUCTURE genuinely is the contract.

        The two must stay in lockstep: a method added to `Cleanable`'s public
        surface and not mirrored here makes this Protocol quietly wrong, and
        structural checks against it will accept objects that cannot actually
        satisfy callers.

    Owned State:
        None. Protocols carry no state and are never instantiated.

    Threading:
        Not applicable. Any concurrency contract belongs to the implementing
        class, not to the shape.

    Lifecycle / Cleanup:
        Describes a cleanup contract; does not have one.

    Registration:
        `Bind` rejects Protocols as concrete spells outright. User types that
        satisfy this shape bind normally.

    Subsystem Context:
        One of two Protocols in `utilities/interfaces/`, beside
        `IChannelLogger`. Both exist to describe a shape the runtime depends on
        without forcing an inheritance or import relationship.

    System Context:
        The cleanup contract it mirrors is the most widely implemented in the
        system - teardown ordering across Spellbook, Conduit, Aether, and the
        Nexus surfaces is all expressed through it. This Protocol is how that
        contract can be referenced from positions that must not pull the ABC in.
    """

    _cleaned: bool

    @property
    def cleaned(self) -> bool:
        """
        Return whether the object has already been cleaned.

        Contract:
            - Structural mirror of `Cleanable.cleaned`: a monotonic latch that
              only moves False -> True.

        Returns:
            bool: True when the object has been cleaned.
        """
        ...

    @property
    def is_cleaned(self) -> bool:
        """
        Alias for `cleaned`.

        Contract:
            - Structural mirror of `Cleanable.is_cleaned`: reads the same
              cleaned-state as `cleaned`.

        Returns:
            bool: Current cleaned-state flag.
        """
        ...

    def check_cleaned(self) -> None:
        """
        Check if the object has been cleaned.

        Raises:
            RuntimeError: If the object has already been cleaned.

        Returns:
            None.
        """
        ...

    def cleanup(self) -> None:
        """
        Dispose must be implemented by subclasses.

        Must:
        -----
        - Release all resources.
        - Deregister or finalize any allocations.
        - Be idempotent (safe to call multiple times).

        Returns:
            None.
        """
        ...

    async def async_cleanup(self) -> None:
        """
        Dispose must be implemented by subclasses.

        Must:
        -----
        - Release all resources.
        - Deregister or finalize any allocations.
        - Be idempotent (safe to call multiple times).

        Returns:
            None.
        """
        ...

