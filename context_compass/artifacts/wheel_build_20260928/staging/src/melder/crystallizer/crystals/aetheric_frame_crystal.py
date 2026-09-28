

from typing import Dict, Optional

from melder.utilities.general_base.cleanable import Cleanable


class AethericFrameCrystal(Cleanable):
    """
    Pure-data digital twin of one AethericFrame's configured surface.

    Purpose:
        Carry the persistable truth of one frame: its identity, its posture
        (the feature-gating trio: system_state / rift_enabled / ai_native),
        and its dev-ops configuration surface. Frames are the posture owners
        in the runtime, so this twin is where the dynamic-lane gate reads its
        recorded truth during restore.

    Guidance:
        Use this twin to recover frame posture and as the parent coordinate for
        spellbook twins. Its absence is not proof that no such live frame
        existed: automatic-posture frames are intentionally outside the dynamic
        recording lane. `frame_name` is the stable reconstruction coordinate;
        restore never reuses a frame runtime identity from this payload.

    Contract:
        - Value payload only; immutable after construction (replace-on-emit).
        - Only DYNAMIC-posture frames are emitted (dynamic-lane hard gate);
          automatic frames never appear in a profile.
        - Child twins (spellbooks) reference this frame by `frame_name`;
          composition is flat-maps-plus-edges, never nested objects.

    Threading:
        Immutable-after-init; the owning PersistenceProfile serializes
        replacement.

    Lifecycle / Cleanup:
        Owned by exactly one `PersistenceProfile`. Cleanup releases recorded
        posture/configuration values only and never disposes the live frame or
        its spellbooks.

    Registration:
        MELDER KERNEL - guarded. Emitted by the crystallizer's builders from live
        runtime truth and owned by one `PersistenceProfile`; never
        user-constructed or bound.

    Subsystem Context:
        One member of the crystal-twin family and the top parent coordinate for
        spellbook twins. It carries a frame's identity, its posture (the
        feature-gating trio system_state / rift_enabled / ai_native), and its
        dev-ops configuration. Because frames own posture in the runtime, this is
        where the restore engine's dynamic-lane gate reads its recorded truth;
        child spellbook twins reference it by `frame_name`.

    System Context:
        One node of the V3 crystallizer's serialize-then-restore model, and the
        clearest example of the record's SELECTIVE-capture law: only
        DYNAMIC-posture frames are emitted (a hard gate), because automatic-posture
        frames are reconstructable defaults, not durable state worth recording. So
        a missing frame twin is NOT proof no live frame existed - it means the
        frame was outside the recording lane. Flat maps-plus-edges composition
        (child twins reference this frame by name, never nest under it) is what
        keeps the record a value graph restore can rebuild in dependency order
        rather than a deep object snapshot.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Pure-data digital twin of one AethericFrame's configured surface.
        Melder kernel machinery: read it to understand the runtime, do not drive it directly.
    """

    __slots__ = Cleanable.__slots__ + [
        "_frame_name",
        "_system_state_name",
        "_rift_enabled",
        "_ai_native_enabled",
        "_dev_ops_payload",
    ]

    def __init__(
            self,
            frame_name: str,
            system_state_name: str,
            rift_enabled: bool,
            ai_native_enabled: bool,
            dev_ops_payload: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize one frame twin from emitted frame posture + dev-ops config.

        Args:
            frame_name:
                Canonical frame name (the parent edge used by child twins).
            system_state_name:
                Recorded SystemState name ("dynamic" expected; the emit gate
                excludes automatic frames).
            rift_enabled:
                Recorded AR/Rift eligibility posture for the frame.
            ai_native_enabled:
                Recorded AI-native posture for the frame.
            dev_ops_payload:
                Value-typed mapping of the frame's dev-ops configured surface.
                None is treated as an empty payload.

        Returns:
            None.

        Raises:
            ValueError:
                If `frame_name` is empty.
        """
        super().__init__()
        if not frame_name:
            raise ValueError(
                "AethericFrameCrystal requires a non-empty frame_name; "
                "an unnamed frame cannot anchor child twins."
            )
        self._frame_name: str = frame_name
        self._system_state_name: str = system_state_name
        self._rift_enabled: bool = rift_enabled
        self._ai_native_enabled: bool = ai_native_enabled
        self._dev_ops_payload: Dict[str, object] = (
            dict(dev_ops_payload) if dev_ops_payload else {}
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
        del self._frame_name
        del self._system_state_name
        del self._rift_enabled
        del self._ai_native_enabled
        del self._dev_ops_payload

    @property
    def frame_name(self) -> str:
        """
        Return the canonical frame name this twin mirrors.

        Contract:
            - The stable reconstruction coordinate (a NAME, not a runtime id);
              restore never reuses a frame runtime identity from this payload.

        Returns:
            str:
                The frame name (parent edge key for child twins).
        """
        self.check_cleaned()
        return self._frame_name

    @property
    def system_state_name(self) -> str:
        """
        Return the recorded SystemState name for the frame.

        Contract:
            - Recorded SystemState NAME ("dynamic" expected - the emit gate
              excludes automatic frames); a string, not the enum member.

        Returns:
            str:
                Recorded posture name at emission time.
        """
        self.check_cleaned()
        return self._system_state_name

    @property
    def rift_enabled(self) -> bool:
        """
        Return the recorded rift_enabled posture.

        Contract:
            - Part of the recorded posture trio; drives AR/Rift eligibility on
              restore.

        Returns:
            bool:
                True when the frame allowed AR/Rift attachment at emission.
        """
        self.check_cleaned()
        return self._rift_enabled

    @property
    def ai_native_enabled(self) -> bool:
        """
        Return the recorded ai_native posture.

        Contract:
            - Part of the recorded posture trio; gates AI-native attachment on
              restore.

        Returns:
            bool:
                True when the frame was AI-native at emission.
        """
        self.check_cleaned()
        return self._ai_native_enabled

    @property
    def dev_ops_payload(self) -> Dict[str, object]:
        """
        Return a detached copy of the frame's dev-ops configured surface.

        Contract:
            - A FRESH copy of the frame's dev-ops value surface; mutating it
              never touches the twin.

        Returns:
            Dict[str, object]:
                Detached mapping of dev-ops property name -> value.
        """
        self.check_cleaned()
        return dict(self._dev_ops_payload)

    def describe(self) -> Dict[str, object]:
        """
        Return a detached, serialization-ready snapshot of this twin.

        Contract:
            - Detached, plain-value cached-item form; carries `twin_kind:
              "frame"` for persistence-layer dispatch.

        Returns:
            Dict[str, object]:
                Plain-value payload (the cached-item form for this twin).
        """
        self.check_cleaned()
        return {
            "twin_kind": "frame",
            "frame_name": self._frame_name,
            "system_state_name": self._system_state_name,
            "rift_enabled": self._rift_enabled,
            "ai_native_enabled": self._ai_native_enabled,
            "dev_ops_payload": dict(self._dev_ops_payload),
        }
