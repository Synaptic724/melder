import threading
from typing import Any, Dict, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.spellbook.configuration.system_state import SystemState
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces import IConfiguration
from melder.utilities.synchronization.safeguard import SafeGuard


class AethericFrameConfiguration(Cleanable):
    """
    Internal

    Narrow frame-level runtime posture for AR and Nexus-facing behavior.

    Purpose:
        Hold only the immutable frame posture fields that matter to AR-facing
        systems and later canonical Nexus record hosting.

    Contract:
        - Captures four frame-level posture values:
          `system_state`, `ai_native_enabled`, `rift_enabled`, and
          `overrides_enabled`.
        - Carries provenance via `origin_spellbook_id`.
        - Is immutable by convention after construction; callers bind one
          instance into an `AethericFrame` and later same-frame attempts do not
          overwrite that posture.
        - Equality of posture is defined by the three runtime posture fields,
          not by object identity, object id, or origin spellbook id.
        - Cleanup is idempotent and clears all owned references.

    Lifecycle:
        Created from one Spellbook `Configuration` during conjure and then
        bound into the owning `AethericFrame`.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_origin_spellbook_id",
        "_system_state",
        "_ai_native_enabled",
        "_rift_enabled",
        "_overrides_enabled",
    ]

    def __init__(
            self,
            *,
            origin_spellbook_id: Optional[str],
            system_state: SystemState,
            ai_native_enabled: bool,
            rift_enabled: bool,
            overrides_enabled: bool = True,
    ) -> None:
        """
        Initialize one frame-level posture object.

        Args:
            origin_spellbook_id:
                Spellbook id that first produced this frame posture. May be
                None when built outside normal Spellbook conjure flow.
            system_state:
                Frame system state. Must resolve to a concrete `SystemState`.
            ai_native_enabled:
                Whether the frame allows AI-native runtime behavior.
            rift_enabled:
                Whether the frame allows AI-profile publication / AR-observable
                posture.
            overrides_enabled:
                Whether bound spells default to override-capable runtime posture
                for this frame.

        Returns:
            None.

        Raises:
            TypeError: If the boolean posture flags are not bools.
            ValueError: If `system_state` cannot be normalized into a
                `SystemState`.
        """
        super().__init__()
        normalized_system_state = EnumHelpers.convert_enum_and_check(
            system_state,
            SystemState,
        )
        if not isinstance(ai_native_enabled, bool):
            raise TypeError("ai_native_enabled must be a bool.")
        if not isinstance(rift_enabled, bool):
            raise TypeError("rift_enabled must be a bool.")
        if not isinstance(overrides_enabled, bool):
            raise TypeError("overrides_enabled must be a bool.")

        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._origin_spellbook_id: Optional[str] = origin_spellbook_id
        self._system_state: SystemState = normalized_system_state
        self._ai_native_enabled: bool = ai_native_enabled
        self._rift_enabled: bool = rift_enabled
        self._overrides_enabled: bool = overrides_enabled

    def cleanup(self) -> None:
        """
        Idempotently clear owned posture state.

        Contract:
            - Safe to call multiple times.
            - Clears all owned posture fields and provenance references.
            - Leaves the object permanently cleaned.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._id = None
            self._origin_spellbook_id = None
            self._system_state = None
            self._ai_native_enabled = None
            self._rift_enabled = None
            self._overrides_enabled = None
        self._lock = None

    @classmethod
    def from_spellbook_configuration(
            cls,
            *,
            origin_spellbook_id: Optional[str],
            configuration: IConfiguration,
    ) -> "AethericFrameConfiguration":
        """
        Build one frame-level posture object from a Spellbook configuration.

        Args:
            origin_spellbook_id:
                Spellbook id that is deriving the posture object.
            configuration:
                Source Spellbook configuration. Must expose the three posture
                values required for AR-facing frame state.

        Returns:
            AethericFrameConfiguration: Derived frame-level posture object.

        Raises:
            KeyError: If any required posture field is missing from the source
                configuration.
            TypeError: If any required posture field has an invalid type.
            ValueError: If `system_state` cannot be normalized into a
                `SystemState`.
        """
        if configuration is None:
            raise TypeError("configuration cannot be None.")

        configuration.check_cleaned()
        with configuration._lock:
            system_state = configuration.get_property("system_state")
            ai_native_enabled = configuration.get_property("ai_native_enabled")
            rift_enabled = configuration.get_property("rift_enabled")
            overrides_enabled = configuration.get_property("overrides_enabled")

        return cls(
            origin_spellbook_id=origin_spellbook_id,
            system_state=system_state,
            ai_native_enabled=ai_native_enabled,
            rift_enabled=rift_enabled,
            overrides_enabled=overrides_enabled,
        )

    @property
    def id(self) -> str:
        """
        Return the stable posture-object id.

        Returns:
            str: Stable configuration id.
        """
        self.check_cleaned()
        with self._lock:
            return self._id

    @property
    def origin_spellbook_id(self) -> Optional[str]:
        """
        Return the Spellbook id that first produced this frame posture.

        Returns:
            Optional[str]: Originating Spellbook id, if known.
        """
        self.check_cleaned()
        with self._lock:
            return self._origin_spellbook_id

    @property
    def system_state(self) -> SystemState:
        """
        Return the frame system state.

        Returns:
            SystemState: Bound frame system state.
        """
        self.check_cleaned()
        with self._lock:
            return self._system_state

    @property
    def ai_native_enabled(self) -> bool:
        """
        Return whether AI-native behavior is enabled for the frame.

        Returns:
            bool: True when AI-native posture is enabled.
        """
        self.check_cleaned()
        with self._lock:
            return self._ai_native_enabled

    @property
    def rift_enabled(self) -> bool:
        """
        Return whether AI-profile publication is enabled for the frame.

        Returns:
            bool: True when AI-profile posture is enabled.
        """
        self.check_cleaned()
        with self._lock:
            return self._rift_enabled

    @property
    def overrides_enabled(self) -> bool:
        """
        Return whether override-capable runtime posture is enabled by default
        for this frame.

        Returns:
            bool: True when override-capable posture is enabled.
        """
        self.check_cleaned()
        with self._lock:
            return self._overrides_enabled

    def matches_posture(
            self,
            other: "AethericFrameConfiguration",
    ) -> bool:
        """
        Compare this posture against another frame-level posture object.

        Contract:
            - Compares only the runtime posture fields:
              `system_state`, `ai_native_enabled`, `rift_enabled`, and
              `overrides_enabled`.
            - Ignores provenance metadata such as `origin_spellbook_id`.
            - Returns False when `other` is None.

        Args:
            other:
                Other frame posture object to compare.

        Returns:
            bool: True when the AR-relevant posture values are identical.
        """
        self.check_cleaned()
        if other is None:
            return False
        with SafeGuard(self._lock, other._lock):
            return (
                self._system_state == other._system_state
                and self._ai_native_enabled == other._ai_native_enabled
                and self._rift_enabled == other._rift_enabled
                and self._overrides_enabled == other._overrides_enabled
            )

    def describe_posture(self) -> Dict[str, Any]:
        """
        Return a detached posture description for logging and diagnostics.

        Contract:
            - Returns plain scalar values only.
            - Intended for diagnostics, logging, and conflict reporting rather
              than as a mutable runtime object.

        Returns:
            Dict[str, Any]: Plain posture dictionary.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "origin_spellbook_id": self._origin_spellbook_id,
                "system_state": self._system_state,
                "ai_native_enabled": self._ai_native_enabled,
                "rift_enabled": self._rift_enabled,
                "overrides_enabled": self._overrides_enabled,
            }
