import logging
from pathlib import Path
import threading
from typing import Any, Callable, ClassVar, Optional, Union



from melder.aether.aether_configuration import AetherConfiguration
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder



class AetherConfigurationBuilder(Cleanable):
    """
    One-shot builder for Aether root configuration assembly.

    Purpose:
        Mirror the repo's mutable-then-finalize configuration style while
        making ownership explicit for the wrapped `AetherConfiguration`.

    Registration:
        MELDER KERNEL - guarded. Obtained through
        `Aether.create_configuration_builder()`.

    Subsystem Context:
        The fluent front for `AetherConfiguration`, matching the builder pairing
        used by every other configuration lane in the system.

    System Context:
        ONE-SHOT MEANS OWNERSHIP TRANSFERS. The builder owns one mutable
        configuration during assembly and hands it off exactly once; after
        `build()` / `finalize()` / `activate()` it has surrendered it and is not
        a factory that stamps out more.
        That is what makes ownership unambiguous - at every moment exactly one
        object is responsible for the configuration, and there is never a window
        where both the builder and the caller could mutate it.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. Fluent one-shot builder for AetherConfiguration. Assemble, then
        build()/finalize()/activate() - ownership transfers on that call and the builder is
        spent. Obtain via Aether.create_configuration_builder().
    """

    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_configuration",
        "_finalized",
    ]

    def __init__(self) -> None:
        """
        Initialize one builder with a fresh Aether configuration.

        Contract:
            - Constructs and OWNS a fresh `AetherConfiguration`. The builder is a
              lifetime wrapper around exactly one configuration, not a factory that
              can produce several.
            - Starts un-finalized; ownership transfers only at `build()`.

        Owned State:
            Owns its lock, id, and the wrapped configuration until `build()` hands
            it over.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._configuration: AetherConfiguration = AetherConfiguration()
        self._finalized: bool = False

    def cleanup(self) -> None:
        """
        Idempotently cleanup the builder and any still-owned configuration.

        Contract:
            - IDEMPOTENT and OWNERSHIP-AWARE: it cleans the wrapped configuration ONLY
              IF `build()` has not already handed it to a caller. Cleaning a builder
              you never built therefore DESTROYS the configuration; cleaning one you
              did build leaves the caller's configuration intact.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if not self._finalized:
                self._configuration.cleanup()
            del self._configuration
            del self._id

    def with_defaults(self) -> "AetherConfigurationBuilder":
        """
        Apply the default Aether logger policy.

        Contract:
            - Delegates to the wrapped configuration and returns the BUILDER, not the
              configuration - the chain stays at the builder layer.
            - Overwrites anything set earlier, so call it first.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            AetherConfigurationBuilder: This builder.
        """
        self.check_cleaned()
        self._configuration.with_defaults()
        return self

    def with_channel_logger_activation_enabled(
            self,
            enabled: bool,
    ) -> "AetherConfigurationBuilder":
        """
        Set the automatic channel logger activation flag.

        Contract:
            - Delegates to the wrapped configuration and returns the BUILDER.
            - Refused once the wrapped configuration is frozen.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            AetherConfigurationBuilder: This builder.

        Args:
            enabled:
                True to let the utility system activate provider-backed channel
                loggers. Disabled by default so importing melder never activates logging.
        """
        self.check_cleaned()
        self._configuration.with_channel_logger_activation_enabled(enabled)
        return self

    def with_channel_logger_resolver(
            self,
            resolver: Optional[Callable[..., Any]],
    ) -> "AetherConfigurationBuilder":
        """
        Set the channel logger resolver.

        Contract:
            - Delegates to the wrapped configuration and returns the BUILDER.
            - `None` clears the resolver.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            AetherConfigurationBuilder: This builder.

        Args:
            resolver:
                Callable the utility system will use to obtain channel loggers.
                Recorded as a presence flag only - the record never carries code.
        """
        self.check_cleaned()
        self._configuration.with_channel_logger_resolver(resolver)
        return self

    def with_default_logger(
            self,
            logger: Optional[logging.Logger],
    ) -> "AetherConfigurationBuilder":
        """
        Set the stdlib fallback logger.

        Contract:
            - Delegates to the wrapped configuration and returns the BUILDER.
            - `None` clears the default logger.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            AetherConfigurationBuilder: This builder.

        Args:
            logger:
                Fallback logger object used when no channel resolver answers.
        """
        self.check_cleaned()
        self._configuration.with_default_logger(logger)
        return self

    def build(self) -> AetherConfiguration:
        """
        Finalize and transfer ownership of the wrapped configuration.

        Contract:
            - ONE-SHOT AND CONSUMING. It finalizes the configuration, transfers
              ownership to the caller, and then CLEANS THIS BUILDER. The builder is
              dead afterwards and a second `build()` raises.
            - Ownership transfer is the point: after a successful build the caller
              owns the configuration and the builder will never clean it.
            - Returns a FROZEN configuration, not an activated one - call
              `activate()` on the result if it is going live.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            AetherConfiguration: Finalized configuration instance.
        """
        self.check_cleaned()
        self._finalize_configuration()
        return self._handoff_configuration()

    def _handoff_configuration(self) -> AetherConfiguration:
        """
        Transfer builder-owned configuration ownership to the caller.

        Returns:
            AetherConfiguration: The configuration previously owned by this builder.
        """
        with self._lock:
            if self._finalized:
                raise RuntimeError(
                    "AetherConfigurationBuilder no longer owns a configuration."
                )
            configuration = self._configuration
            self._finalized = True
            self.cleanup()
        return configuration

    def _finalize_configuration(self) -> None:
        """
        Run the configuration finalization lifecycle before ownership transfer.
        """
        self._configuration.finalize()
