

from typing import Dict, List, Optional

from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class ConduitCrystal(Cleanable):
    """
    Pure-data digital twin of one ROOT conduit's structural surface.

    Purpose:
        Carry the persistable truth of one root conduit: identity, conjure
        posture (name / policy / dynamic), and its peer-link edges. Restore
        replays this twin as the conjure step AFTER the owning spellbook's
        binds (L3 intra-level rule), and applies link edges LAST, once every
        conduit in the profile exists.

    Guidance:
        Read this twin as the root conduit's conjure record plus its outbound
        initiated link edges. It does not contain borrowed spell/lineage detail;
        join it with `ContractCrystal` for contract projections and
        `ClusterCrystal` for cluster membership. During restore, resolve
        `spellbook_id` and `link_targets` through fresh identity translation
        rather than treating record-local conduit ids as reusable.

    Contract:
        - Value payload only; immutable after construction (replace-on-emit).
        - ROOT conduits only: lesser conduits are ephemeral scope machinery,
          reconstructable at runtime, and never emit (call-site gate).
        - `link_targets` records peer conduit ids as edges, not objects; the
          restore engine resolves them in its final link pass.
        - Runtime identities (ULIDs) are RECORD-LOCAL: they express edges
          and log correlation within the recorded session only. Restore
          translates them to fresh identities (never reuses them), and
          seal fingerprinting normalizes them out so identical worlds
          compare identical across boots.

    Threading:
        Immutable-after-init; the owning PersistenceProfile serializes
        replacement.

    Lifecycle / Cleanup:
        Owned by exactly one `PersistenceProfile`. Cleanup releases the conjure
        and edge payload only; conduit disposal remains a live-runtime owner
        responsibility.

    Registration:
        MELDER KERNEL - guarded. Emitted by the crystallizer's builders from live
        runtime truth and owned by one `PersistenceProfile`; never
        user-constructed or bound.

    Subsystem Context:
        One member of the crystal-twin family - the pure-data value objects the
        crystallizer records and the restore engine replays. This twin is the
        root conduit's slice: a builder projects a live root Conduit into it,
        `PersistenceProfile` holds it (replace-on-emit), and restore replays it as
        the conjure step AFTER the owning spellbook's binds, applying its link
        edges LAST once every conduit exists. `ContractCrystal` and
        `ClusterCrystal` carry the borrowed-detail and membership slices it joins
        with.

    System Context:
        One node of the V3 crystallizer's serialize-then-restore model, where a
        live world is recorded as a graph of value twins and rebuilt by replaying
        them in dependency order. Keeping runtime ULIDs RECORD-LOCAL (translated
        to fresh identities on restore, normalized out of seal fingerprints) is
        what lets two structurally-identical worlds compare equal across boots and
        lets restore rebuild the graph without reusing stale ids. Recording ROOT
        conduits only - lessers are ephemeral scope machinery rebuilt at runtime -
        is the boundary that keeps the record the durable structural truth, not a
        snapshot of transient runtime state.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Pure-data digital twin of one ROOT conduit's structural surface. "
        "Melder kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_conduit_id",
        "_spellbook_id",
        "_conduit_name",
        "_policy_name",
        "_dynamic",
        "_link_targets",
        "_configuration_payload",
    ]

    def __init__(
            self,
            conduit_id: str,
            spellbook_id: str,
            conduit_name: Optional[str],
            policy_name: str,
            dynamic: bool,
            link_targets: Optional[List[str]] = None,
            configuration_payload: Optional[Dict[str, object]] = None,
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
            configuration_payload:
                Value-typed conduit configuration surface retained at
                emission (state, lineage root, pool posture). None is
                treated as an empty payload.

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
        del self._conduit_id
        del self._spellbook_id
        del self._conduit_name
        del self._policy_name
        del self._dynamic
        del self._link_targets
        del self._configuration_payload

    @property
    def conduit_id(self) -> str:
        """
        Return the stable conduit identity this twin mirrors.

        Contract:
            - RECORD-LOCAL identity: expresses edges and log correlation within
              the recorded session only; restore translates it to a fresh id.

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

        Contract:
            - The parent (conjure-source) edge, record-local like `conduit_id`;
              restore resolves it through fresh identity translation.

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

        Contract:
            - None for unnamed root conduits; a name is present only when the
              root was registered under one.

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

        Contract:
            - The `Policies` enum NAME recorded at conjure (a string, not the
              enum member), so the record stays value-typed.

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

        Contract:
            - Recorded conjure mode; dynamic-lane worlds emit True by the
              posture gate, kept for restore fidelity.

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

        Contract:
            - A FRESH copy of peer conduit ids as EDGES (not objects); the
              restore engine applies them LAST, once every conduit exists.

        Returns:
            List[str]:
                Peer conduit ids; applied in the restore engine's final pass.
        """
        self.check_cleaned()
        return list(self._link_targets)

    @property
    def configuration_payload(self) -> Dict[str, object]:
        """
        Return a detached copy of the retained conduit configuration.

        Contract:
            - A FRESH copy of the value-typed conduit configuration surface;
              mutating it never touches the twin.

        Returns:
            Dict[str, object]:
                Detached mapping of configuration name -> value.
        """
        self.check_cleaned()
        return dict(self._configuration_payload)

    def describe(self) -> Dict[str, object]:
        """
        Return a detached, serialization-ready snapshot of this twin.

        Contract:
            - Detached, plain-value cached-item form; carries `twin_kind:
              "conduit"` so the persistence layer dispatches it correctly.

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
            "configuration_payload": dict(self._configuration_payload),
        }
