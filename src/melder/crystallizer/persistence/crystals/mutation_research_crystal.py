

from typing import Dict, Optional

from melder.utilities.general_base.cleanable import Cleanable


class MutationResearchCrystal(Cleanable):
    """
    Pure-data digital twin of the MutationResearch root's configured surface.

    Purpose:
        Carry the persistable truth of the MR root for one profile. Phase A
        records configuration/activation state only; the git-style composition
        (research streams, version records, heads, index associations) rides
        this same twin in Phase B, when MR persistence conveys through the
        CRUD adapter (persistence epic P5).

    Contract:
        - Value payload only; immutable after construction (replace-on-emit).
        - MR is codegen-lane-only at runtime, so this twin appears only in
          profiles emitted from dynamic-lane worlds.
        - Composition fields are deliberately absent in Phase A; extending
          this twin is the P5 seam, not a new object.

    Threading:
        Immutable-after-init; the owning PersistenceProfile serializes
        replacement.

    Lifecycle:
        Owned by exactly one PersistenceProfile; `cleanup()` deletes owned
        fields; idempotent.
    """

    __slots__ = Cleanable.__slots__ + [
        "_activated",
        "_configuration_payload",
    ]

    def __init__(
            self,
            activated: bool,
            configuration_payload: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize the MR twin from emitted root activation/config state.

        Args:
            activated:
                Whether the MR root was activated at emission time.
            configuration_payload:
                Value-typed mapping of the installed MR configuration surface.
                None is treated as an empty payload.

        Returns:
            None.
        """
        super().__init__()
        self._activated: bool = activated
        self._configuration_payload: Dict[str, object] = (
            dict(configuration_payload) if configuration_payload else {}
        )

    def cleanup(self) -> None:
        """
        Release owned fields and mark the twin cleaned.

        Contract:
            - Idempotent; del posture (no tombstones).
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._activated
        del self._configuration_payload

    @property
    def activated(self) -> bool:
        """
        Return whether the MR root was activated at emission.

        Returns:
            bool:
                Recorded activation flag.
        """
        self.check_cleaned()
        return self._activated

    @property
    def configuration_payload(self) -> Dict[str, object]:
        """
        Return a detached copy of the recorded MR configuration surface.

        Returns:
            Dict[str, object]:
                Detached mapping of configured property name -> value.
        """
        self.check_cleaned()
        return dict(self._configuration_payload)
