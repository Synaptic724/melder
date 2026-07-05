

from typing import Dict, List, Optional

from melder.utilities.general_base.cleanable import Cleanable


class ConduitCrystal(Cleanable):
    """
    Pure-data digital twin of one ROOT conduit's structural surface.

    Purpose:
        Carry the persistable truth of one root conduit: identity, conjure
        posture (name / policy / dynamic), and its peer-link edges. Restore
        replays this twin as the conjure step AFTER the owning spellbook's
        binds (L3 intra-level rule), and applies link edges LAST, once every
        conduit in the profile exists.

    Contract:
        - Value payload only; immutable after construction (replace-on-emit).
        - ROOT conduits only: lesser conduits are ephemeral scope machinery,
          reconstructable at runtime, and never emit (call-site gate).
        - `link_targets` records peer conduit ids as edges, not objects; the
          restore engine resolves them in its final link pass.

    Threading:
        Immutable-after-init; the owning PersistenceProfile serializes
        replacement.

    Lifecycle:
        Owned by exactly one PersistenceProfile; `cleanup()` deletes owned
        fields; idempotent.
    """

    __slots__ = Cleanable.__slots__ + [
        "_conduit_id",
        "_spellbook_id",
        "_conduit_name",
        "_policy_name",
        "_dynamic",
        "_link_targets",
    ]

    def __init__(
            self,
            conduit_id: str,
            spellbook_id: str,
            conduit_name: Optional[str],
            policy_name: str,
            dynamic: bool,
            link_targets: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize one root-conduit twin from emitted conjure-time truth.

        Args:
            conduit_id:
                Stable conduit identity within the profile.
            spellbook_id:
                Owning spellbook's id (parent edge; conjure source).
            conduit_name:
                Optional registered conduit name (None for unnamed roots).
            policy_name:
                Recorded Policies enum name active at conjure.
            dynamic:
                Recorded conjure mode (dynamic-lane worlds emit True by the
                posture gate; recorded for restore fidelity).
            link_targets:
                Peer conduit ids this conduit had initiated links to at
                emission time; replayed in the final link pass.

        Returns:
            None.

        Raises:
            ValueError:
                If `conduit_id` or `spellbook_id` is empty.
        """
        super().__init__()
        if not conduit_id:
            raise ValueError(
                "ConduitCrystal requires a non-empty conduit_id."
            )
        if not spellbook_id:
            raise ValueError(
                "ConduitCrystal requires a non-empty spellbook_id; "
                "the conduit twin anchors under its spellbook."
            )
        self._conduit_id: str = conduit_id
        self._spellbook_id: str = spellbook_id
        self._conduit_name: Optional[str] = conduit_name
        self._policy_name: str = policy_name
        self._dynamic: bool = dynamic
        self._link_targets: List[str] = list(link_targets) if link_targets else []

    def cleanup(self) -> None:
        """
        Release owned fields and mark the twin cleaned.

        Contract:
            - Idempotent; del posture (no tombstones).
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._conduit_id
        del self._spellbook_id
        del self._conduit_name
        del self._policy_name
        del self._dynamic
        del self._link_targets

    @property
    def conduit_id(self) -> str:
        """
        Return the stable conduit identity this twin mirrors.

        Returns:
            str:
                Conduit id within the profile.
        """
        self.check_cleaned()
        return self._conduit_id

    @property
    def spellbook_id(self) -> str:
        """
        Return the owning spellbook's id.

        Returns:
            str:
                Parent spellbook id (conjure source edge).
        """
        self.check_cleaned()
        return self._spellbook_id

    @property
    def conduit_name(self) -> Optional[str]:
        """
        Return the registered conduit name, when one existed.

        Returns:
            Optional[str]:
                Conduit name or None for unnamed roots.
        """
        self.check_cleaned()
        return self._conduit_name

    @property
    def policy_name(self) -> str:
        """
        Return the recorded conjure policy name.

        Returns:
            str:
                Policies enum name at conjure time.
        """
        self.check_cleaned()
        return self._policy_name

    @property
    def dynamic(self) -> bool:
        """
        Return the recorded conjure mode.

        Returns:
            bool:
                True when the conduit was conjured dynamic.
        """
        self.check_cleaned()
        return self._dynamic

    @property
    def link_targets(self) -> List[str]:
        """
        Return a detached copy of recorded peer-link edges.

        Returns:
            List[str]:
                Peer conduit ids; applied in the restore engine's final pass.
        """
        self.check_cleaned()
        return list(self._link_targets)

    def describe(self) -> Dict[str, object]:
        """
        Return a detached, serialization-ready snapshot of this twin.

        Returns:
            Dict[str, object]:
                Plain-value payload (the cached-item form for this twin).
        """
        self.check_cleaned()
        return {
            "twin_kind": "conduit",
            "conduit_id": self._conduit_id,
            "spellbook_id": self._spellbook_id,
            "conduit_name": self._conduit_name,
            "policy_name": self._policy_name,
            "dynamic": self._dynamic,
            "link_targets": list(self._link_targets),
        }
