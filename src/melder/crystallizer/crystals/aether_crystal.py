

from typing import Dict, Optional

from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class AetherCrystal(Cleanable):
    """
    Pure-data digital twin of the Aether root's configured surface.

    Purpose:
        Carry the persistable configuration truth of the process Aether root
        (root logger policy and any future root-level configured properties)
        inside one PersistenceProfile. The Aether twin is deliberately THIN:
        deep Aether state (frames, registries, hosted singletons) is owned by
        the child twins beneath it, so this twin records configuration only.

    Guidance:
        Interpret this twin as root policy, not a snapshot of the complete
        runtime. Frames, spellbooks, Nexus, MutationResearch, and crystallizer
        state have their own twins or state switches. An empty configuration
        payload means the root emitted without installed policy; it does not
        mean the process lacked an `Aether` object.

    Contract:
        - Value payload only: no live objects, no callables, no locks.
        - Immutable after construction; profiles replace the whole twin on
          re-emission (replace-on-emit), they never mutate it in place.
        - Retained whenever the crystallizer is active, regardless of frame
          posture: root configuration sits above the dynamic-lane gate.

    Threading:
        Immutable-after-init; safe to share across threads without locking.
        The owning PersistenceProfile serializes replacement.

    Lifecycle / Cleanup:
        Owned by exactly one `PersistenceProfile`. Replacement or profile
        teardown cleans the displaced twin's value fields only; no live Aether
        root, logger, frame, or hosted subsystem is affected.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Pure-data digital twin of the Aether root's configured surface. Melder "
        "kernel machinery: read it to understand the runtime, do not drive it directly."
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

    def describe(self) -> Dict[str, object]:
        """
        Return a detached, serialization-ready snapshot of this twin.

        Returns:
            Dict[str, object]:
                Plain-value payload (the cached-item form for this twin).
        """
        self.check_cleaned()
        return {
            "twin_kind": "aether",
            "configuration_payload": dict(self._configuration_payload),
        }
