import threading
from typing import Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.mutation_research.mutation_configuration import (
    MutationResearchConfiguration,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class MutationResearchConfigurationBuilder(Cleanable):
    """
    One-shot builder for mutation-research configuration assembly.

    Purpose:
        Mirror the repo's mutable-then-finalize configuration style while
        making ownership explicit.

    Registration:
        MELDER KERNEL - guarded. Obtained through
        `MutationResearch.create_configuration_builder()`.

    ONE-SHOT MEANS OWNERSHIP TRANSFERS:
        The builder owns one mutable configuration during assembly and hands it
        off exactly once. After `build()` / `finalize()` / `activate()`, the
        builder has surrendered its configuration - it is not a factory that can
        be reused to stamp out more. That is what makes ownership unambiguous:
        at any moment exactly one object is responsible for the configuration,
        and there is never a window where both the builder and the caller could
        mutate it.

    Subsystem Context:
        The fluent front for `MutationResearchConfiguration`, matching the
        builder pairing used by the Aether and crystallizer configurations. The
        symmetry is deliberate - an agent that has learned one configuration
        lane can drive all of them.

    System Context:
        Sits at the very start of the mutation-research lifecycle: configure,
        then activate the root, then declare research. Because configuration
        activation is an emission moment, the assembly this builder performs is
        also what determines the first recorded twin of the research subsystem.
    """
    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Fluent one-shot builder for MutationResearchConfiguration; ownership "
        "transfers at build()/finalize()/activate()."
    )

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_configuration",
    ]

    def __init__(self) -> None:
        """
        Initialize one builder with a fresh configuration.

        Contract:
            - Constructs and OWNS a fresh `MutationResearchConfiguration`. The builder
              wraps exactly one configuration; it is not a reusable factory.
            - The wrapped configuration starts EMPTY, so seed both properties before
              any exit method that freezes.

        Owned State:
            Owns its lock, id, and the wrapped configuration until an exit method
            hands it over.

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
        self._configuration: Optional[MutationResearchConfiguration] = (
            MutationResearchConfiguration()
        )

    def cleanup(self) -> None:
        """
        Idempotently cleanup the builder and any still-owned configuration.

        Contract:
            - IDEMPOTENT under double-checked locking, and OWNERSHIP-AWARE: it cleans
              the wrapped configuration ONLY while the builder still owns it.
              Cleaning a builder you never exited DESTROYS the configuration;
              cleaning one you already exited leaves the caller's intact.

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
            if self._configuration is not None:
                self._configuration.cleanup()
            del self._configuration
            del self._id
        del self._lock

    @property
    def id(self) -> str:
        """
        Return the stable builder id.

        Contract:
            - Identifies THIS BUILDER, not the configuration it wraps - the two carry
              different ids.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            str: Stable builder id.
        """
        self.check_cleaned()
        return self._id

    def with_defaults(self) -> "MutationResearchConfigurationBuilder":
        """
        Apply the default mutation-research configuration.

        Contract:
            - Delegates to the wrapped configuration and returns the BUILDER, not the
              configuration, so the chain stays at the builder layer.
            - Overwrites anything set earlier; call it first.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            MutationResearchConfigurationBuilder: This builder.
        """
        self.check_cleaned()
        self._configuration.with_defaults()
        return self

    def with_unrestricted_module_mutations(
            self,
            enabled: bool,
    ) -> "MutationResearchConfigurationBuilder":
        """
        Set the unrestricted-module-mutations posture on the wrapped config.

        Args:
            enabled:
                Whether unrestricted module mutation mode is enabled.

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
            MutationResearchConfigurationBuilder: This builder.
        """
        self.check_cleaned()
        self._configuration.with_unrestricted_module_mutations(enabled)
        return self

    def with_lane_type_enforcement(
            self,
            enabled: bool,
    ) -> "MutationResearchConfigurationBuilder":
        """
        Set the lane-type-enforcement posture on the wrapped config.

        Args:
            enabled:
                Whether type-mixing lane joins require force=True.

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
            MutationResearchConfigurationBuilder: This builder.
        """
        self.check_cleaned()
        self._configuration.with_lane_type_enforcement(enabled)
        return self

    def build(self) -> MutationResearchConfiguration:
        """
        Transfer the wrapped mutable configuration to the caller.

        Contract:
            - HANDS OVER A MUTABLE, UNFROZEN CONFIGURATION. It does NOT freeze, unlike
              `AetherConfigurationBuilder.build()`, which returns a frozen one. Same
              method name, different guarantee - check which builder you hold.
            - ONE-SHOT: it transfers ownership, so a second exit call on this builder
              raises. `build()`, `finalize()` and `activate()` are mutually exclusive
              exits; whichever you call first consumes the builder.
            - After handover the caller owns the configuration and the builder will
              never clean it.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            MutationResearchConfiguration: Wrapped configuration instance.
        """
        self.check_cleaned()
        return self._handoff_configuration()

    def finalize(self) -> MutationResearchConfiguration:
        """
        Finalize and transfer the wrapped configuration to the caller.

        Contract:
            - Freezes the wrapped configuration and THEN hands it over, so the caller
              receives a FROZEN, NOT-YET-ACTIVATED configuration.
            - ONE-SHOT and mutually exclusive with `build()` and `activate()`.
            - Because it freezes, the configuration must be complete first - an
              unseeded bag raises here rather than at handover.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            MutationResearchConfiguration: Frozen configuration instance.
        """
        self.check_cleaned()
        self._configuration.finalize()
        return self._handoff_configuration()

    def activate(self) -> MutationResearchConfiguration:
        """
        Activate and transfer the wrapped configuration to the caller.

        Contract:
            - Activates the wrapped configuration and THEN hands it over, so the caller
              receives an ACTIVATED configuration and the activation record has
              already been emitted.
            - ONE-SHOT and mutually exclusive with `build()` and `finalize()`.
            - Prefer this over calling `activate()` yourself on a built
              configuration: doing both would emit the activation record twice.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            MutationResearchConfiguration: Activated configuration instance.
        """
        self.check_cleaned()
        self._configuration.activate()
        return self._handoff_configuration()

    def _handoff_configuration(self) -> MutationResearchConfiguration:
        """
        Transfer builder-owned configuration ownership to the caller.

        Returns:
            MutationResearchConfiguration: Previously owned configuration.
        """
        with self._lock:
            if self._configuration is None:
                raise RuntimeError(
                    "MutationResearchConfigurationBuilder no longer owns a configuration."
                )
            configuration = self._configuration
            self._configuration = None
            self.cleanup()
        return configuration

