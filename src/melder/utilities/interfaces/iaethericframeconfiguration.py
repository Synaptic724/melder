from typing import Any, Dict, Optional, Protocol, Union, runtime_checkable

from melder.spellbook.configuration.system_state import SystemState
from melder.utilities.interfaces.icleanable import ICleanable


@runtime_checkable
class IAethericFrameConfiguration(ICleanable, Protocol):
    """
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

    @property
    def id(self) -> str:
        """
        Return the stable posture-object id.

        Returns:
            str: Stable configuration id.
        """
        ...

    @property
    def origin_spellbook_id(self) -> Optional[str]:
        """
        Return the Spellbook id that first produced this frame posture.

        Returns:
            Optional[str]: Originating Spellbook id, if known.
        """
        ...

    @property
    def system_state(self) -> SystemState:
        """
        Return the frame system state.

        Returns:
            SystemState: Bound frame system state.
        """
        ...

    @property
    def ai_native_enabled(self) -> bool:
        """
        Return whether AI-native behavior is enabled for the frame.

        Returns:
            bool: True when AI-native posture is enabled.
        """
        ...

    @property
    def rift_enabled(self) -> bool:
        """
        Return whether Rift-visible frame behavior is enabled.

        Returns:
            bool: True when Rift-visible posture is enabled.
        """
        ...

    @property
    def shared_framewide_spellbook_configuration(self) -> bool:
        """
        Return whether the frame posture permits one explicit frame-owned
        shared rich `SpellbookConfiguration`.

        Returns:
            bool: True when frame-wide rich-config sharing is permitted.
        """
        ...

    def cleanup(self) -> None:
        """
        Idempotently clear owned posture state.

        Returns:
            None.
        """
        ...

    def validate(self) -> bool:
        """
        Validate the current frame posture values.

        Returns:
            bool: True when the current frame posture is valid.
        """
        ...

    def freeze(self, origin_spellbook_id: Optional[str] = None) -> None:
        """
        Freeze the frame posture so no further mutation is allowed.

        Args:
            origin_spellbook_id:
                Optional spellbook id to stamp as the posture origin.

        Returns:
            None.
        """
        ...

    def with_system_state(
            self,
            system_state: Union[SystemState, str],
    ) -> "IAethericFrameConfiguration":
        """
        Set the frame system state before freeze and return `self`.

        Returns:
            IAethericFrameConfiguration: This posture instance.
        """
        ...

    def with_ai_native(
            self,
            enabled: bool = True,
    ) -> "IAethericFrameConfiguration":
        """
        Set AI-native frame posture before freeze and return `self`.

        Returns:
            IAethericFrameConfiguration: This posture instance.
        """
        ...

    def with_rift_enabled(
            self,
            enabled: bool = True,
    ) -> "IAethericFrameConfiguration":
        """
        Set Rift-visible frame posture before freeze and return `self`.

        Returns:
            IAethericFrameConfiguration: This posture instance.
        """
        ...

    def with_shared_framewide_spellbook_configuration(
            self,
            enabled: bool = True,
    ) -> "IAethericFrameConfiguration":
        """
        Set whether the frame permits explicit shared rich Spellbook config and
        return `self`.

        Returns:
            IAethericFrameConfiguration: This posture instance.
        """
        ...

    def with_defaults(self) -> "IAethericFrameConfiguration":
        """
        Reset frame posture to the default automatic/non-AR posture.

        Returns:
            IAethericFrameConfiguration: This posture instance.
        """
        ...

    def dynamic_defaults(self) -> "IAethericFrameConfiguration":
        """
        Set the default dynamic frame posture and return `self`.

        Returns:
            IAethericFrameConfiguration: This posture instance.
        """
        ...

    def automatic_defaults(self) -> "IAethericFrameConfiguration":
        """
        Set the default automatic frame posture and return `self`.

        Returns:
            IAethericFrameConfiguration: This posture instance.
        """
        ...

    def matches_posture(
            self,
            other: object,
    ) -> bool:
        """
        Compare this posture against another frame-level posture object.

        Args:
            other:
                Other frame posture object to compare.

        Returns:
            bool: True when the AR-relevant posture values are identical.
        """
        ...

    def describe_posture(self) -> Dict[str, Any]:
        """
        Return a detached posture description for logging and diagnostics.

        Returns:
            Dict[str, Any]: Plain posture dictionary.
        """
        ...
