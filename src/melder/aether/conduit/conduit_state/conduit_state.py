from enum import Enum, auto
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class ConduitState(Enum):
    """
    Lifecycle classification for a conduit instance.

    This enum is the compact runtime label used to distinguish whether a
    conduit is a normal/root-visible conduit, a lesser lineage child, or an
    already-cleaned conduit that should no longer participate in runtime work.

    Contract:
        - `normal` means a full conduit that can be registered into the wider
          frame/runtime surfaces.
        - `lesser` means a lineage child conduit that inherits state from a
          parent/root conduit until it is upgraded.
        - `pooled_lesser` means an idle lesser shell retained for reuse and
          not currently attached to an active parent lineage.
        - `cleaned` means teardown has completed and the conduit should be
          treated as unusable.
    """
    __melder_internal__ = _mrg.sentinel
    normal = auto()
    lesser = auto()
    pooled_lesser = auto()
    cleaned = auto()

    def __str__(self) -> str:
        """
        Return the stable lowercase state name used in logs and diagnostics.
        """
        return self.name.lower()

    @staticmethod
    def resolve(value: str | Enum | None) -> "ConduitState":
        """
        Normalize external conduit-state input into a `ConduitState` value.

        Args:
            value:
                Either a lowercase string (`"normal"`, `"lesser"`, etc.), an
                enum member, or `None`.

        Returns:
            ConduitState:
                Resolved conduit state.

        Raises:
            ValueError:
                If the string or enum value does not map to a valid conduit
                state.
        """
        if value is None:
            raise ValueError("value cannot be None")

        resolved_state: ConduitState = EnumHelpers.convert_enum_and_check(
            value=value,
            enum=ConduitState,
        )
        return resolved_state
