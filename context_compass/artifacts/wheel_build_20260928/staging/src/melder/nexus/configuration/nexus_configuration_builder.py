import threading
from typing import Optional

from melder.nexus.configuration.nexus_configuration import NexusConfiguration
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class NexusConfigurationBuilder(Cleanable):
    """
    One-shot ownership helper for Nexus configuration authoring.

    Purpose:
        Give callers and agents an explicit handoff boundary around one mutable
        `NexusConfiguration`, exactly as `CrystallizerConfigurationBuilder` and
        `MutationResearchConfigurationBuilder` already do for their subsystems.
        Nexus was the one root of four with no builder at all, so its callers
        had to construct the configuration directly while every other root
        handed one over.

    Guidance:
        `with_defaults()` covers the common starting posture. `build()` returns
        the still-mutable configuration so the caller can apply the wider
        `with_*` surface `NexusConfiguration` carries; `finalize()` returns
        frozen policy; `activate()` returns policy ready for
        `Nexus.activate(...)`.

    Contract:
        - Owns exactly one configuration until handoff or cleanup.
        - `build()`, `finalize()`, and `activate()` are one-shot ownership
          transfers and consume the builder.
        - Cleanup destroys only a configuration that was not handed off.
        - THE EXITS ARE DIFFERENT RUNGS. `finalize()` freezes; `activate()`
          freezes AND marks the policy ready. Neither turns the Nexus on -
          that is still a separate `Nexus.activate(configuration)` call.

    Threading:
        One `RLock` protects ownership transfer and cleanup. Fluent authoring
        is intended for one builder thread.

    Lifecycle / Cleanup:
        Short-lived by design. After handoff, the caller owns the returned
        configuration and the builder is terminal.

    Registration:
        MELDER KERNEL - guarded (internal manifest). access=public: a user
        constructs and drives the builder, then it hands the configuration
        off; it is never a bind target.

    Subsystem Context:
        The one-shot ownership helper for `NexusConfiguration` authoring in the
        Rift domain. It owns exactly one mutable configuration until `build()` /
        `finalize()` / `activate()` transfers ownership and consumes the
        builder - a companion to the direct configuration fluents when an
        explicit ownership wrapper is useful.

    System Context:
        Nexus layer of the boot order. It exists to give one explicit ownership
        boundary around the pre-activation policy object, so the configuration
        handed to `Nexus.activate(...)` has exactly one owner at each step.
    """

    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_configuration",
    ]

    def __init__(self) -> None:
        """
        Initialize one builder with a fresh empty configuration.

        Contract:
            The wrapped configuration has no defaults yet; call
            `with_defaults()` before a finalize/activate handoff or the
            configuration will not freeze.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._configuration: Optional[NexusConfiguration] = NexusConfiguration()

    def cleanup(self) -> None:
        """
        Idempotently cleanup the builder and any still-owned configuration.

        Contract:
            - Idempotent and terminal.
            - Cleans the wrapped configuration only while ownership has not
              transferred; handed-off policy is never reclaimed here.
            - Deletes builder identity and lock state after child cleanup.

        Threading:
            Serialized by the builder lock.

        Lifecycle / Cleanup:
            Safe in `finally`; ownership state determines whether the child is
            cleaned or deliberately left with the caller.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if self._configuration is not None:
                self._configuration.cleanup()
            del self._configuration
            del self._id
        del self._lock

    @property
    def id(self) -> str:
        """
        Return the stable builder id.

        Threading:
            Unsynchronized read; a snapshot only.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the builder has been cleaned.

        Returns:
            str: Builder identity.
        """
        self.check_cleaned()
        return self._id

    def with_defaults(self) -> "NexusConfigurationBuilder":
        """
        Load the complete default Nexus policy set onto the wrapped object.

        Contract:
            - Mutates the WRAPPED configuration and returns THIS builder for
              chaining; it does not copy and does not hand off.

        Raises:
            RuntimeError: If the builder has been cleaned or no longer owns a
                configuration.

        Returns:
            NexusConfigurationBuilder: This builder, for fluent chaining.
        """
        self.check_cleaned()
        if self._configuration is not None:
            self._configuration.with_defaults()
        return self

    def with_rift_creation_enabled(
            self,
            enabled: bool = True,
    ) -> "NexusConfigurationBuilder":
        """
        Set the Rift-creation gate on the wrapped configuration.

        Purpose:
            The one knob almost every caller sets immediately after defaults,
            surfaced on the builder so the common path is a single chain.

        Args:
            enabled:
                Whether Rift creation is permitted.

        Raises:
            RuntimeError: If the builder has been cleaned.

        Returns:
            NexusConfigurationBuilder: This builder, for fluent chaining.
        """
        self.check_cleaned()
        if self._configuration is not None:
            self._configuration.with_rift_creation_enabled(enabled)
        return self

    def build(self) -> NexusConfiguration:
        """
        Transfer the wrapped mutable configuration to the caller.

        Contract:
            - Ownership moves to the caller and the builder is consumed.
            - The returned configuration remains MUTABLE. This is the handoff
              to choose when the caller still needs the wider `with_*` surface
              that `NexusConfiguration` carries and the builder does not
              mirror.

        Raises:
            RuntimeError: If the builder has been cleaned or already handed off.

        Returns:
            NexusConfiguration: Wrapped configuration instance.
        """
        self.check_cleaned()
        return self._handoff_configuration()

    def finalize(self) -> NexusConfiguration:
        """
        Finalize and transfer the wrapped configuration to the caller.

        Contract:
            - Validates and freezes the wrapped configuration first.
            - Ownership moves to the caller and the builder is consumed.
            - The returned policy is FROZEN BUT NOT ACTIVATED. That is a real
              rung, not a technicality - `activate()` below is what marks it
              ready.

        Raises:
            RuntimeError: If the builder has been cleaned or already handed off.
            ValueError: If the wrapped configuration fails validation.

        Returns:
            NexusConfiguration: Frozen configuration instance.
        """
        self.check_cleaned()
        if self._configuration is not None:
            self._configuration.finalize()
        return self._handoff_configuration()

    def activate(self) -> NexusConfiguration:
        """
        Activate and transfer the wrapped configuration to the caller.

        Contract:
            - Validates, freezes, and marks the wrapped configuration active.
            - Ownership moves to the caller and the builder is consumed.
            - The caller must still pass it to `Nexus.activate(...)`; builder
              activation does not activate the singleton itself. Two objects,
              two bits.

        Raises:
            RuntimeError: If the builder has been cleaned or already handed off.
            ValueError: If the wrapped configuration fails validation.

        Returns:
            NexusConfiguration: Activated configuration instance.
        """
        self.check_cleaned()
        if self._configuration is not None:
            self._configuration.activate()
        return self._handoff_configuration()

    def _handoff_configuration(self) -> NexusConfiguration:
        """
        Internal

        Transfer builder-owned configuration ownership to the caller.

        Returns:
            NexusConfiguration: The configuration previously owned by this
            builder.

        Raises:
            RuntimeError: If the configuration has already been handed off or
                cleaned.
        """
        with self._lock:
            if self._configuration is None:
                raise RuntimeError(
                    "NexusConfigurationBuilder no longer owns a configuration."
                )
            configuration = self._configuration
            self._configuration = None
            self.cleanup()
        return configuration
