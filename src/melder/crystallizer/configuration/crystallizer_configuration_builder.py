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
    One-shot builder for crystallizer configuration assembly.

    Purpose:
        Mirror the repo's mutable-then-finalize configuration style while also
        making ownership explicit. The builder owns one mutable wrapped
        configuration until the caller either:
        - hands it off through `build()`, `finalize()`, or `activate()`
        - or discards it through `cleanup()`

    Contract:
        - full concrete file name, not a generic helper path
        - builder owns the wrapped configuration until handoff or cleanup
        - `build()`, `finalize()`, and `activate()` are one-shot transfer
          points
        - after handoff, the builder is consumed and must not be reused

    Lifecycle:
        The builder is a short-lived authoring helper. Cleanup destroys the
        still-owned configuration. Handoff methods transfer configuration
        ownership to the caller and consume the builder.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_configuration",
    ]

    def __init__(self) -> None:
        """
        Initialize one builder with a fresh configuration.

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
            - safe to call more than once
            - cleans the wrapped configuration only while the builder still
              owns it
            - leaves the builder unusable after cleanup

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

        Returns:
            str: Stable builder id.
        """
        self.check_cleaned()
        return self._id

    def with_defaults(self) -> "CrystallizerConfigurationBuilder":
        """
        Apply the first crystallizer defaults.

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
            - ownership moves to the caller
            - the builder is consumed after handoff

        Returns:
            CrystallizerConfiguration: Wrapped configuration instance.
        """
        self.check_cleaned()
        return self._handoff_configuration()

    def finalize(self) -> CrystallizerConfiguration:
        """
        Finalize and transfer the wrapped configuration to the caller.

        Contract:
            - freezes the wrapped configuration first
            - ownership moves to the caller
            - the builder is consumed after handoff

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
            - validates/finalizes/activates the wrapped configuration first
            - ownership moves to the caller
            - the builder is consumed after handoff

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
