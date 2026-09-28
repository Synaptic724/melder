

from copy import deepcopy
from typing import Dict, List, Optional

from melder.utilities.general_base.cleanable import Cleanable


class ConduitCrystal(Cleanable):
    """
    Pure-data twin of one normal root or named lesser conduit's structure.

    Purpose:
        Carry identity, name, policy and structural parent/root relationships.
        Roots replay through conjure after Book binding; named lessers replay
        through their parent's creation API. Required unnamed ancestor values
        travel with the named twin. No prior Creations or application data is held.

    Guidance:
        Read normal twins as conjure records and lesser twins as scope-creation
        records. configuration_payload carries the role and lineage; it contains
        no live borrowed spell or scope reference. For peer relationships,
        join it with `ContractCrystal` for contract projections and
        `ClusterCrystal` for cluster membership. During restore, resolve
        `spellbook_id` and `link_targets` through fresh identity translation
        rather than treating record-local conduit ids as reusable.

    Contract:
        - Value payload only; immutable after construction (replace-on-emit).
        - Normal roots and active named lessers emit. Required unnamed ancestry
          is value-only support inside the named twin, never a separately owned
          runtime or an independently retained unnamed record.
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
        conduit structural slice: its runtime owner pushes detached values,
        `PersistenceProfile` holds them replace-on-emit, and restore rebuilds the
        root and child hierarchy after Book binding. Link edges apply LAST.
        `ContractCrystal` and
        `ClusterCrystal` carry the borrowed-detail and membership slices it joins
        with.

    System Context:
        One node of the V3 crystallizer's serialize-then-restore model, where a
        live world is recorded as a graph of value twins and rebuilt by replaying
        them in dependency order. Keeping runtime ULIDs RECORD-LOCAL (translated
        to fresh identities on restore, normalized out of seal fingerprints) is
        what lets two structurally-identical worlds compare equal across boots and
        lets restore rebuild the graph without reusing stale ids. Named scope
        records preserve hierarchy, not previously created instances. Supporting
        unnamed ancestor snapshots disappear with their last retained named carrier.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Pure-data twin of one normal or named lesser conduit's structure.
        Melder kernel machinery: read it to understand the runtime, do not drive it directly.
    """

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
        Initialize a conduit twin from emitted structural values.

        Args:
            conduit_id:
                Stable conduit identity within the profile.
            spellbook_id:
                Owning root's spellbook id; lessers share that Book.
            conduit_name:
                Recorded root or lesser name; None is retained for legacy roots.
            policy_name:
                Recorded Policies enum name active at conjure.
            dynamic:
                Recorded conjure mode (dynamic-lane worlds emit True by the
                posture gate; recorded for restore fidelity).
            link_targets:
                Peer conduit ids this conduit had initiated links to at
                emission time; replayed in the final link pass.
            configuration_payload:
                Value-only state/root/parent and pool posture. Named lessers also
                carry lineage_ancestors from root to immediate parent, with each
                ancestor's id/name/parent/policy. Nested values are copied so neither
                emitter mutation nor exported views can change this immutable twin.
                None is treated as an empty payload.

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
            deepcopy(configuration_payload) if configuration_payload else {}
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
            - Names identify normal roots or active named lesser scopes. None
              remains readable for legacy root payloads.

        Returns:
            Optional[str]:
                Conduit name, or None for a legacy unnamed root.
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
        return deepcopy(self._configuration_payload)

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
            "configuration_payload": deepcopy(self._configuration_payload),
        }
