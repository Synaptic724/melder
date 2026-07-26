

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

    Guidance:
        Interpret this twin with the profile's Nexus `RecordedUnitState`: the
        twin preserves installed configuration, while the state switch carries
        the later enabled/disabled/cleaned intent. Do not use it to infer Rift
        instances, room state, workstations, or active projections; those are
        session/runtime assets deliberately outside this root twin.

    Contract:
        - Value payload only; immutable after construction (replace-on-emit).
        - Records configuration truth, not Rift registry state (live Rifts
          are session objects, not persistable structure).

    Threading:
        Immutable-after-init; the owning PersistenceProfile serializes
        replacement.

    Lifecycle / Cleanup:
        Owned by exactly one `PersistenceProfile`. Cleanup releases the recorded
        flags/configuration only and does not disable or clean the live Nexus.

    Registration:
        MELDER KERNEL - guarded. Emitted by the crystallizer's builders from live
        runtime truth and owned by one `PersistenceProfile`; never
        user-constructed or bound.

    Subsystem Context:
        One member of the crystal-twin family - the ROOT twin for the process
        Nexus. It records only the Nexus's configured surface (configured/enabled
        + its NexusConfiguration value) and is meant to be read WITH the profile's
        Nexus `RecordedUnitState`: the twin holds installed configuration, the
        state switch holds the later enabled/disabled/cleaned intent. Live Rift
        instances, rooms, and projections are session assets deliberately OUTSIDE
        this twin.

    System Context:
        One node of the V3 crystallizer's serialize-then-restore model, governed
        by the "we twin anything we want to configure/persist" principle. The
        boundary this twin draws - configuration truth IN, live registry state
        OUT - keeps the whole record durable rather than a runtime snapshot: a
        Rift or room is a session object a restored world recreates fresh, so
        persisting it would record transient state that can never be replayed
        faithfully. Pairing a thin config twin with a separate state switch is how
        the record captures "how it was set up" and "what state it was left in"
        without conflating the two.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Pure-data digital twin of the Nexus root's configured surface. Melder
        kernel machinery: read it to understand the runtime, do not drive it directly.
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

        Returns:
            None.
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

        Contract:
            - Records whether a config was installed; pairs with the profile's
              Nexus RecordedUnitState for enabled/disabled/cleaned intent.

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

        Contract:
            - Emission-time enabled flag; the LATER enabled/disabled/cleaned
              intent rides the state switch, not this twin.

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

        Contract:
            - A FRESH copy of the installed configuration surface; empty when
              unconfigured. Mutating it never touches the twin.

        Returns:
            Dict[str, object]:
                Detached mapping of configured property name -> value.
        """
        self.check_cleaned()
        return dict(self._configuration_payload)

    def describe(self) -> Dict[str, object]:
        """
        Return a detached, serialization-ready snapshot of this twin.

        Contract:
            - Detached, plain-value cached-item form; carries `twin_kind:
              "nexus"` for persistence-layer dispatch.

        Returns:
            Dict[str, object]:
                Plain-value payload (the cached-item form for this twin).
        """
        self.check_cleaned()
        return {
            "twin_kind": "nexus",
            "configured": self._configured,
            "enabled": self._enabled,
            "configuration_payload": dict(self._configuration_payload),
        }
