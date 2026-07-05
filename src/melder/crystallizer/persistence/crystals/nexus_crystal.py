

from typing import Dict, Optional

from melder.utilities.general_base.cleanable import Cleanable


class NexusCrystal(Cleanable):
    """
    Pure-data digital twin of the Nexus root's configured surface.

    Purpose:
        Carry the persistable truth of the process Nexus root: whether it was
        configured/enabled and the value surface of its NexusConfiguration.
        Nexus is in the twin family because its configuration is a configured
        surface worth cloning + remembering (governing principle: we twin
        anything we want to configure/persist).

    Contract:
        - Value payload only; immutable after construction (replace-on-emit).
        - Records configuration truth, not Rift registry state (live Rifts
          are session objects, not persistable structure).

    Threading:
        Immutable-after-init; the owning PersistenceProfile serializes
        replacement.

    Lifecycle:
        Owned by exactly one PersistenceProfile; `cleanup()` deletes owned
        fields; idempotent.
    """

    __slots__ = Cleanable.__slots__ + [
        "_configured",
        "_enabled",
        "_configuration_payload",
    ]

    def __init__(
            self,
            configured: bool,
            enabled: bool,
            configuration_payload: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize the Nexus twin from emitted root AR configuration state.

        Args:
            configured:
                Whether a NexusConfiguration was installed at emission time.
            enabled:
                Whether the Nexus root was enabled at emission time.
            configuration_payload:
                Value-typed mapping of the installed configuration surface.
                None is treated as an empty payload (unconfigured).

        Returns:
            None.
        """
        super().__init__()
        self._configured: bool = configured
        self._enabled: bool = enabled
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
        del self._configured
        del self._enabled
        del self._configuration_payload

    @property
    def configured(self) -> bool:
        """
        Return whether a NexusConfiguration was installed at emission.

        Returns:
            bool:
                Recorded configured flag.
        """
        self.check_cleaned()
        return self._configured

    @property
    def enabled(self) -> bool:
        """
        Return whether the Nexus root was enabled at emission.

        Returns:
            bool:
                Recorded enabled flag.
        """
        self.check_cleaned()
        return self._enabled

    @property
    def configuration_payload(self) -> Dict[str, object]:
        """
        Return a detached copy of the recorded Nexus configuration surface.

        Returns:
            Dict[str, object]:
                Detached mapping of configured property name -> value.
        """
        self.check_cleaned()
        return dict(self._configuration_payload)
