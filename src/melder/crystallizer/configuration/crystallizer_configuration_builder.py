import threading
from pathlib import Path
from typing import Optional, Sequence, Union

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class CrystallizerConfigurationBuilder(Cleanable):
    """
    One-shot ownership helper for crystallizer configuration authoring.

    Purpose:
        Give callers and agents an explicit handoff boundary around one mutable
        `CrystallizerConfiguration`. Use the builder when ownership transfer is
        useful to the surrounding construction flow; direct configuration
        fluents remain the simpler choice when no ownership wrapper is needed.

    Guidance:
        `with_defaults()` and `with_user_source_root_paths()` cover the common
        starting posture. `build()` returns the still-mutable configuration so
        the caller can apply advanced knobs such as source retention or
        automatic flushing. `finalize()` returns frozen policy; `activate()`
        returns policy ready for `Crystallizer.activate(...)`.

    Contract:
        - Owns exactly one configuration until handoff or cleanup.
        - `build()`, `finalize()`, and `activate()` are one-shot ownership
          transfers and consume the builder.
        - Cleanup destroys only a configuration that was not handed off.

    Threading:
        One `RLock` protects ownership transfer and cleanup. Fluent authoring is
        intended for one builder thread.

    Lifecycle / Cleanup:
        Short-lived by design. After handoff, the caller owns the returned
        configuration and the builder is terminal.

    Registration:
        MELDER KERNEL - guarded (`__melder_internal__` sentinel). access=public: a user
        constructs and drives the builder, then it hands the configuration off; it is never
        a bind target.

    Subsystem Context:
        The one-shot ownership helper for `CrystallizerConfiguration` authoring in the
        crystallizer subsystem. It owns exactly one mutable configuration until `build()` /
        `finalize()` / `activate()` transfers ownership and consumes the builder - a
        companion to the direct configuration fluents when an explicit ownership wrapper is
        useful.

    System Context:
        Crystallizer layer of the boot order (position 2, after Aether|AetherUtilitySystem).
        It exists to give one explicit ownership boundary around the pre-activation policy
        object - the same settle-before-activate discipline the record depends on - so the
        configuration handed to `Crystallizer.activate(...)` has exactly one owner at each
        step.
    """
    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Fluent one-shot builder for CrystallizerConfiguration. Assemble then "
        "build()/finalize()/activate(); ownership transfers and the builder is spent."
    )

    __melder_internal__ = _mrg.sentinel
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
            `with_defaults()` or set the required source roots before a
            finalize/activate handoff.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._configuration: CrystallizerConfiguration | None = (
            CrystallizerConfiguration()
        )

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

        Contract:
            - Identifies THIS BUILDER, not the configuration it wraps - the two carry
              different ids.

        Threading:
            Unsynchronized read; a snapshot only.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

        Returns:
            str: Stable builder id.
        """
        self.check_cleaned()
        return self._id

    def with_defaults(self) -> "CrystallizerConfigurationBuilder":
        """
        Apply the complete default crystallizer policy.

        Purpose:
            Produce the same valid baseline as
            `CrystallizerConfiguration.with_defaults()`, including source-text,
            inactive-module, checkpoint, retention, and flush defaults.

        Returns:
            CrystallizerConfigurationBuilder: This builder.
        """
        self.check_cleaned()
        if self._configuration is not None:
            self._configuration.with_defaults()
        return self

    def with_user_source_root_paths(
            self,
            root_paths: Sequence[Union[str, Path]],
    ) -> "CrystallizerConfigurationBuilder":
        """
        Set user-owned source roots on the wrapped configuration.

        Args:
            root_paths:
                Sequence of source roots that should count as user-owned code.

        Contract:
            - SILENTLY NO-OPS AFTER HANDOFF. Once the wrapped configuration has been
              handed to a caller the builder holds None, and this method returns
              `self` without applying anything - it does NOT raise. Set properties
              BEFORE building.
            - MUTATES the wrapped configuration and returns the BUILDER, keeping the
              chain at the builder layer.

        Threading:
            Unsynchronized read; a snapshot only.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

        Returns:
            CrystallizerConfigurationBuilder: This builder.
        """
        self.check_cleaned()
        if self._configuration is not None:
            self._configuration.with_user_source_root_paths(root_paths)
        return self

    def build(self) -> CrystallizerConfiguration:
        """
        Transfer the wrapped mutable configuration to the caller.

        Contract:
            - Ownership moves to the caller and the builder is consumed.
            - The returned configuration remains mutable. This is the handoff
              to choose when the caller still needs advanced configuration
              fluents not mirrored by the builder.

        Returns:
            CrystallizerConfiguration: Wrapped configuration instance.
        """
        self.check_cleaned()
        return self._handoff_configuration()

    def finalize(self) -> CrystallizerConfiguration:
        """
        Finalize and transfer the wrapped configuration to the caller.

        Contract:
            - Validates and freezes the wrapped configuration first.
            - Ownership moves to the caller and the builder is consumed.
            - The returned policy is not marked activated.

        Returns:
            CrystallizerConfiguration: Frozen configuration instance.
        """
        self.check_cleaned()
        if self._configuration is not None:
            self._configuration.finalize()
        return self._handoff_configuration()

    def activate(self) -> CrystallizerConfiguration:
        """
        Activate and transfer the wrapped configuration to the caller.

        Contract:
            - Validates, freezes, and marks the wrapped configuration active.
            - Ownership moves to the caller and the builder is consumed.
            - The caller must still pass it to `Crystallizer.activate(...)`;
              builder activation does not activate the singleton itself.

        Returns:
            CrystallizerConfiguration: Activated configuration instance.
        """
        self.check_cleaned()
        if self._configuration is not None:
            self._configuration.activate()
        return self._handoff_configuration()

    def _handoff_configuration(self) -> CrystallizerConfiguration:
        """
        Transfer builder-owned configuration ownership to the caller.

        Returns:
            CrystallizerConfiguration: The configuration previously owned by
            this builder.

        Raises:
            RuntimeError:
                If the configuration has already been handed off or cleaned.
        """
        with self._lock:
            if self._configuration is None:
                raise RuntimeError(
                    "CrystallizerConfigurationBuilder no longer owns a configuration."
                )
            configuration = self._configuration
            self._configuration = None
            self.cleanup()
        return configuration
