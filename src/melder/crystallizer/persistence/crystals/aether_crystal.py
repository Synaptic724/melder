

from typing import Dict, Optional

from melder.utilities.general_base.cleanable import Cleanable


class AetherCrystal(Cleanable):
    """
    Pure-data digital twin of the Aether root's configured surface.

    Purpose:
        Carry the persistable configuration truth of the process Aether root
        (root logger policy and any future root-level configured properties)
        inside one PersistenceProfile. The Aether twin is deliberately THIN:
        deep Aether state (frames, registries, hosted singletons) is owned by
        the child twins beneath it, so this twin records configuration only.

    Contract:
        - Value payload only: no live objects, no callables, no locks.
        - Immutable after construction; profiles replace the whole twin on
          re-emission (replace-on-emit), they never mutate it in place.
        - Retained whenever the crystallizer is active, regardless of frame
          posture: root configuration sits above the dynamic-lane gate.

    Threading:
        Immutable-after-init; safe to share across threads without locking.
        The owning PersistenceProfile serializes replacement.

    Lifecycle:
        Owned by exactly one PersistenceProfile. `cleanup()` deletes owned
        fields and marks the twin cleaned; idempotent.
    """

    __slots__ = Cleanable.__slots__ + [
        "_configuration_payload",
    ]

    def __init__(
            self,
            configuration_payload: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize the Aether root twin from one emitted configuration payload.

        Args:
            configuration_payload:
                Value-typed mapping of the Aether root configuration as
                emitted (property name -> value). None is treated as an
                empty payload (unconfigured root).

        Returns:
            None.
        """
        super().__init__()
        self._configuration_payload: Dict[str, object] = (
            dict(configuration_payload) if configuration_payload else {}
        )

    def cleanup(self) -> None:
        """
        Release the twin's payload and mark it cleaned.

        Contract:
            - Idempotent; safe to call multiple times.
            - Deletes owned fields (del posture; no tombstones needed).
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._configuration_payload

    @property
    def configuration_payload(self) -> Dict[str, object]:
        """
        Return a detached copy of the recorded root configuration payload.

        Returns:
            Dict[str, object]:
                Detached mapping of configured property name -> value.

        Raises:
            RuntimeError:
                If the twin has already been cleaned.
        """
        self.check_cleaned()
        return dict(self._configuration_payload)
