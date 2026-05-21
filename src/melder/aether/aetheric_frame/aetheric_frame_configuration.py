import threading
from typing import Any, Dict, Optional, ClassVar

from mypy_extensions import mypyc_attr

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.synchronization.safeguard import SafeGuard
@mypyc_attr(native_class=True)

class AethericFrameConfiguration(Cleanable):
    """
    Internal

    Narrow frame-level runtime posture for AR and Nexus-facing behavior.

    Purpose:
        Hold only the immutable frame posture fields that matter to AR-facing
        systems and later canonical Nexus record hosting.

    Contract:
        - Captures frame-level posture values:
          `system_state`, `ai_native_enabled`, `rift_enabled`, and
          `shared_framewide_spellbook_configuration`.
        - Carries provenance via `origin_spellbook_id`.
        - Is immutable by convention after construction; callers bind one
          instance into an `AethericFrame` and later same-frame attempts do not
          overwrite that posture.
        - Equality of posture is defined by the frame-posture fields, not by
          object identity, object id, or origin spellbook id.
        - Cleanup is idempotent and clears all owned references.

    Lifecycle:
        Created from one Spellbook `Configuration` during conjure and then
        bound into the owning `AethericFrame`.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_frozen",
        "_origin_spellbook_id",
        "_system_state",
        "_ai_native_enabled",
        "_rift_enabled",
        "_shared_framewide_spellbook_configuration",
    ]
    __deletable__: ClassVar[list[str]] = [
        "_id",
        "_lock",
        "_frozen",
        "_origin_spellbook_id",
        "_system_state",
        "_ai_native_enabled",
        "_rift_enabled",
        "_shared_framewide_spellbook_configuration",
    ]

    def __init__(
            self,
            *,
            origin_spellbook_id: Optional[str],
            system_state: SystemState,
            ai_native_enabled: bool,
            rift_enabled: bool,
            shared_framewide_spellbook_configuration: bool = False,
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
            shared_framewide_spellbook_configuration:
                Whether the frame posture permits one explicit frame-owned
                shared rich `SpellbookConfiguration` object.

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
        if not isinstance(shared_framewide_spellbook_configuration, bool):
            raise TypeError(
                "shared_framewide_spellbook_configuration must be a bool."
            )
        if ai_native_enabled and normalized_system_state != SystemState.dynamic:
            raise ValueError(
                "ai_native_enabled requires system_state to be dynamic."
            )

        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._frozen: bool = False
        self._origin_spellbook_id: Optional[str] = origin_spellbook_id
        self._system_state: SystemState = normalized_system_state
        self._ai_native_enabled: bool = ai_native_enabled
        self._rift_enabled: bool = rift_enabled
        self._shared_framewide_spellbook_configuration: bool = (
            shared_framewide_spellbook_configuration
        )

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
            self._frozen = True
            del self._id
            del self._origin_spellbook_id
            del self._system_state
            del self._ai_native_enabled
            del self._rift_enabled
            del self._shared_framewide_spellbook_configuration
        del self._lock

    def validate(self) -> bool:
        """
        Validate the current frame posture values.

        Returns:
            bool: True when the current frame posture is valid.

        Raises:
            ValueError: If AI-native posture is enabled while system state is
                not dynamic.
        """
        self.check_cleaned()
        with self._lock:
            if self._ai_native_enabled and self._system_state != SystemState.dynamic:
                raise ValueError(
                    "ai_native_enabled requires system_state to be dynamic."
                )
            return True

    def freeze(self, origin_spellbook_id: Optional[str] = None) -> None:
        """
        Freeze the frame posture so no further mutation is allowed.

        Args:
            origin_spellbook_id: Optional spellbook id to stamp as the posture
                origin if one should be recorded at freeze time.
        """
        self.check_cleaned()
        with self._lock:
            if self._frozen:
                return
            self.validate()
            if origin_spellbook_id is not None:
                self._origin_spellbook_id = origin_spellbook_id
            self._frozen = True

    def with_system_state(
            self,
            system_state: SystemState | str,
    ) -> "AethericFrameConfiguration":
        """
        Set the frame system state before freeze and return `self`.
        """
        self.check_cleaned()
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify frame configuration after it is frozen.")
            self._system_state = EnumHelpers.convert_enum_and_check(
                system_state,
                SystemState,
            )
        return self

    def with_ai_native(
            self,
            enabled: bool = True,
    ) -> "AethericFrameConfiguration":
        """
        Set AI-native frame posture before freeze and return `self`.
        """
        self.check_cleaned()
        if not isinstance(enabled, bool):
            raise TypeError("ai_native_enabled must be a bool.")
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify frame configuration after it is frozen.")
            self._ai_native_enabled = enabled
        return self

    def with_rift_enabled(
            self,
            enabled: bool = True,
    ) -> "AethericFrameConfiguration":
        """
        Set Rift-visible frame posture before freeze and return `self`.
        """
        self.check_cleaned()
        if not isinstance(enabled, bool):
            raise TypeError("rift_enabled must be a bool.")
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify frame configuration after it is frozen.")
            self._rift_enabled = enabled
        return self

    def with_shared_framewide_spellbook_configuration(
            self,
            enabled: bool = True,
    ) -> "AethericFrameConfiguration":
        """
        Set whether the frame permits explicit shared rich Spellbook config and
        return `self`.
        """
        self.check_cleaned()
        if not isinstance(enabled, bool):
            raise TypeError(
                "shared_framewide_spellbook_configuration must be a bool."
            )
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify frame configuration after it is frozen.")
            self._shared_framewide_spellbook_configuration = enabled
        return self

    def with_defaults(self) -> "AethericFrameConfiguration":
        """
        Reset frame posture to the default automatic/non-AR posture.
        """
        self.check_cleaned()
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify frame configuration after it is frozen.")
            self._system_state = SystemState.automatic
            self._ai_native_enabled = False
            self._rift_enabled = False
            self._shared_framewide_spellbook_configuration = False
        return self

    def dynamic_defaults(self) -> "AethericFrameConfiguration":
        """
        Set the default dynamic frame posture and return `self`.
        """
        return self.with_defaults().with_system_state(SystemState.dynamic)

    def automatic_defaults(self) -> "AethericFrameConfiguration":
        """
        Set the default automatic frame posture and return `self`.
        """
        return self.with_defaults().with_system_state(SystemState.automatic)

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
    def shared_framewide_spellbook_configuration(self) -> bool:
        """
        Return whether the frame posture permits one explicit frame-owned
        shared rich `SpellbookConfiguration`.

        Returns:
            bool: True when frame-wide rich-config sharing is permitted.
        """
        self.check_cleaned()
        with self._lock:
            return self._shared_framewide_spellbook_configuration

    def matches_posture(
            self,
            other: object,
    ) -> bool:
        """
        Compare this posture against another frame-level posture object.

        Contract:
            - Compares only the frame-posture fields:
              `system_state`, `ai_native_enabled`, `rift_enabled`, and
              `shared_framewide_spellbook_configuration`.
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
        if not isinstance(other, AethericFrameConfiguration):
            return False
        with SafeGuard(self._lock, other._lock):
            return (
                self._system_state == other._system_state
                and self._ai_native_enabled == other._ai_native_enabled
                and self._rift_enabled == other._rift_enabled
                and self._shared_framewide_spellbook_configuration
                == other._shared_framewide_spellbook_configuration
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
                "shared_framewide_spellbook_configuration": (
                    self._shared_framewide_spellbook_configuration
                ),
            }
