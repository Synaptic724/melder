

from typing import Dict, Optional

from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class CrystallizerCrystal(Cleanable):
    """
    Pure-data digital twin of the crystallizer's own configured surface.

    Purpose:
        Carry the persistable configuration truth of the recording system
        itself (source-root policy, retention caps, checkpoint cadence,
        flush posture) inside one PersistenceProfile. A cached world can
        then reboot its crystallizer FROM the record before unfolding the
        rest of the world - the recorder's policy is part of the recorded
        truth, not ambient process state.

    Guidance:
        This twin answers which recording policy produced a sealed world. It is
        not permission to replace policy on an already-active crystallizer
        during restore. Bootstrap code that intends to reproduce recorded policy
        should load its `configuration_payload` into a fresh
        `CrystallizerConfiguration` before activating the root; the restore
        engine otherwise reports the recorded policy as boot-time context.

    Contract:
        - Value payload only: no live objects, no callables, no locks.
        - Immutable after construction; profiles replace the whole twin on
          re-emission (replace-on-emit), they never mutate it in place.
        - Self-emitted by the crystallizer at its own activation (the one
          configured moment); restore treats it as BOOT-TIME truth - the
          engine never swaps a live crystallizer's configuration mid-
          restore, it reports the recorded policy instead.

    Threading:
        Immutable-after-init; safe to share across threads without locking.
        The owning PersistenceProfile serializes replacement.

    Lifecycle / Cleanup:
        Owned by exactly one `PersistenceProfile`. Cleanup releases the recorded
        policy document only; it neither reconfigures nor deactivates the live
        crystallizer.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Pure-data digital twin of the crystallizer's own configured surface. "
        "Melder kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_configuration_payload",
    ]

    def __init__(
            self,
            configuration_payload: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize the crystallizer twin from one emitted configuration
        payload.

        Args:
            configuration_payload:
                Value-typed mapping of the crystallizer configuration as
                emitted (property name -> value; collections arrive as
                lists of strings per the emission scalar filter). None is
                treated as an empty payload.

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

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._configuration_payload

    @property
    def configuration_payload(self) -> Dict[str, object]:
        """
        Return a detached copy of the recorded crystallizer configuration.

        Returns:
            Dict[str, object]:
                Detached mapping of configured property name -> value.

        Raises:
            RuntimeError:
                If the twin has already been cleaned.
        """
        self.check_cleaned()
        return dict(self._configuration_payload)

    def describe(self) -> Dict[str, object]:
        """
        Return a detached, serialization-ready snapshot of this twin.

        Returns:
            Dict[str, object]:
                Plain-value payload (the cached-item form for this twin).
        """
        self.check_cleaned()
        return {
            "twin_kind": "crystallizer",
            "configuration_payload": dict(self._configuration_payload),
        }
