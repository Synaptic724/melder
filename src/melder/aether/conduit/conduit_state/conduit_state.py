from enum import Enum, auto
from melder.utilities.helpers.general_helpers import EnumHelpers

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

    Threading:
        Enum members are immutable and safe to read from any thread. `resolve`
        is a pure static normalizer holding no state.

    Registration:
        MELDER KERNEL - guarded, but readable by value. Users observe conduit
        state; the sentinel only prevents binding the enum CLASS as a spell.

    Subsystem Context:
        The lifecycle vocabulary for `Conduit`, sitting alongside the ward
        vocabularies (`Policies`, `Permissions`) that govern contracting rather
        than lifecycle. `resolve(...)` accepts either a string or an enum member
        so external and recorded inputs normalize through one path and a bad
        value raises instead of silently defaulting.

    System Context:
        These four values are a state MACHINE, not a set of labels, and the
        transitions are one-way. `lesser` may be promoted to `normal` through
        `Conduit.upgrade_to_normal(...)` (dynamic mode only); `pooled_lesser` is
        the idle shell the `ConduitPool` retains for reuse, deliberately
        detached from any active parent lineage so a reused shell cannot inherit
        stale ancestry; and `cleaned` is terminal - nothing transitions out of
        it, which is what makes post-cleanup use a contract violation rather
        than a recoverable state.
        The `normal` / `lesser` distinction is what the rest of the runtime
        branches on: only a normal conduit registers into frame-level surfaces
        and owns the Spellbook lifecycle, so a lesser conduit's teardown can
        never unregister state the root still depends on.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Lifecycle classification for a conduit instance. Melder kernel "
        "machinery: read it to understand the runtime, do not drive it directly."
    )
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
