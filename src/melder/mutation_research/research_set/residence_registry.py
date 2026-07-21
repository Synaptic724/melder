import threading
from typing import Dict, List, Optional, ClassVar

from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class ResidenceRegistry(Cleanable):
    """
    Single-residence partition map for one research set.

    Purpose:
        Enforce the hard invariant that one spell identity (binding-signature
        SHA256) resides in exactly ONE lane across the entire graph network,
        never duplicated. This makes the network a partition of identities
        and gives rediscovery detection for free: rebinding identical content
        produces the same SHA, and the collision points straight at the lane
        already holding it.

    Contract:
        - `claim()` is all-or-nothing: an already-resident SHA raises with the
          holding lane named (the rediscovery signal), even when the claimant
          is the holding lane itself (node dedup happens above this layer).
        - Residence is PERMANENT through archive (owner default): archived
          lanes keep their identities so rediscovery always points somewhere
          true. There is deliberately NO release verb.
        - `transfer()` repoints residencies during `join`; every transferred
          SHA must already be resident.
        - Network restore rebuilds the registry wholesale via
          `from_payload()`; it never edits entries in place.

    Threading:
        Instance `RLock` serializes claims, transfers, and reads.

    Lifecycle:
        Owned by exactly one `ResearchSet`; `cleanup()` deletes owned fields;
        idempotent; lock released last.

    WHY THERE IS NO RELEASE VERB:
        Residence is permanent, including through archive. That looks like a
        missing feature and is the opposite: if an identity could leave the
        partition, rediscovery would start answering "nowhere" for content that
        genuinely did exist somewhere, and the collision signal would degrade
        from a fact into a maybe. Keeping archived lanes' identities resident is
        what makes "this content is already known, and here is where" always
        true.

    Registration:
        MELDER KERNEL - guarded. The partition invariant is the record's to
        enforce; a user never holds one of these directly.

    Subsystem Context:
        One of the four bookkeeping structures a `ResearchSet` owns, beside
        `ResearchJournal` (what happened, in order), `NetworkVersioner` (what
        the organization looked like), and the lanes themselves (where things
        are now). This one answers the narrowest and hardest question: is this
        identity already somewhere.

    System Context:
        The rediscovery mechanism of the whole research model. A spell's
        identity is the SHA256 of its binding signature, so rebinding identical
        content reproduces the same identity - and the claim collision is how
        the system recognizes "you have built this before" without comparing any
        source. That is also why residence claims are rolled back when a lane
        refuses a node: a claim that outlived its failed add would make a
        never-recorded identity permanently unavailable.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Single-residence partition map for one research set. Melder kernel "
        "machinery: read it to understand the runtime, do not drive it directly."
    )
    __melder_internal__: ClassVar[object] = _mrg.sentinel

    __slots__ = Cleanable.__slots__ + [
        "_lane_id_by_spell_id",
        "_lock",
    ]

    def __init__(self) -> None:
        """
        Initialize one empty residence partition.

        Contract:
            - Starts EMPTY: no identity is resident until `claim`ed. A fresh
              registry answers `is_resident` False for everything.
            - Owns a single sha -> lane map and its lock; nothing else.

        Threading:
            Creates the `RLock` that serializes every later claim, transfer and
            read.

        Returns:
            None.
        """
        super().__init__()
        self._lane_id_by_spell_id: Dict[str, str] = {}
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        """
        Release owned fields and mark the registry cleaned.

        Contract:
            - IDEMPOTENT under double-checked locking.
            - DELETE-NOT-NULL, no tombstones; the lock is deleted last, outside
              the guarded block.
            - Clears the partition map only - it holds sha strings, not owned
              objects, so there is no child cascade.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._lane_id_by_spell_id.clear()
            del self._lane_id_by_spell_id
        del self._lock

    def claim(self, spell_id: str, lane_id: str) -> None:
        """
        Claim residence of one identity for one lane.

        Contract:
            - ALL-OR-NOTHING against the single-residence invariant: an identity
              already resident ANYWHERE raises `RuntimeError` naming the holding
              lane. That raise is the REDISCOVERY SIGNAL, not a failure to route
              around - identical content rebinds to the same SHA, and the
              collision is how the system says "you built this before, here."
            - COLLIDES EVEN AGAINST THE SAME LANE. Re-claiming an identity for
              the lane that already holds it still raises; node-level dedup is
              handled one layer up, not here.
            - Empty `spell_id` or `lane_id` raises `ValueError` before the map is
              touched.
            - Success installs exactly one entry; there is no public verb to undo
              it (residence is permanent). The only removal path is the private
              failure-compensation `_rollback_claim`.

        Threading:
            The presence check and the insert happen together under `self._lock`,
            so two threads cannot both claim the same identity.

        Args:
            spell_id:
                Binding-signature SHA256 to claim.
            lane_id:
                Lane taking residence.

        Raises:
            ValueError:
                If either argument is empty.
            RuntimeError:
                If the identity is already resident anywhere - the
                rediscovery signal, naming the holding lane.

        Returns:
            None.
        """
        self.check_cleaned()
        if not isinstance(spell_id, str) or not spell_id:
            raise ValueError("spell_id must be a non-empty string.")
        if not isinstance(lane_id, str) or not lane_id:
            raise ValueError("lane_id must be a non-empty string.")
        with self._lock:
            holder = self._lane_id_by_spell_id.get(spell_id)
            if holder is not None:
                raise RuntimeError(
                    f"Rediscovery: spell identity '{spell_id}' already "
                    f"resides in lane '{holder}'. A spell identity lives in "
                    f"exactly one lane; identical content rebinds to the "
                    f"same SHA256."
                )
            self._lane_id_by_spell_id[spell_id] = lane_id

    def transfer(self, spell_ids: List[str], to_lane_id: str) -> None:
        """
        Repoint residence of the given identities onto one lane.

        Purpose:
            The `join` mechanic: member identities move to the receiving lane
            in one all-or-nothing motion.

        Contract:
            - TWO-PHASE ALL-OR-NOTHING: every identity is checked for residence
              FIRST, and only if all are resident are any repointed. A single
              non-resident identity raises `KeyError` with NOTHING moved, so a
              partial transfer cannot corrupt the partition.
            - REPOINTS, does not add. Each identity must already be resident;
              this changes which lane holds it, never introduces a new residence
              (that is `claim`).
            - Idempotent per identity: repointing to the lane it already resides
              in is a harmless overwrite.
            - Does not change the resident COUNT - identities move between lanes,
              the partition size is unchanged.

        Threading:
            The full check-then-repoint runs under `self._lock`, so no reader
            observes a half-transferred set.

        Args:
            spell_ids:
                Identities to repoint; every one must already be resident.
            to_lane_id:
                Receiving lane id.

        Raises:
            ValueError:
                If to_lane_id is empty.
            KeyError:
                If any identity is not currently resident (nothing is
                repointed in that case).

        Returns:
            None.
        """
        self.check_cleaned()
        if not isinstance(to_lane_id, str) or not to_lane_id:
            raise ValueError("to_lane_id must be a non-empty string.")
        with self._lock:
            for spell_id in spell_ids:
                if spell_id not in self._lane_id_by_spell_id:
                    raise KeyError(
                        f"spell identity '{spell_id}' has no residence to "
                        f"transfer."
                    )
            for spell_id in spell_ids:
                self._lane_id_by_spell_id[spell_id] = to_lane_id

    def _rollback_claim(self, spell_id: str, lane_id: str) -> None:
        """
        Remove one claim as FAILURE COMPENSATION only.

        Purpose:
            Registration is claim-then-hold across two structures; when the
            lane refuses the node AFTER the claim landed (a direct lane-state
            race under real threads), the claim must not strand - a resident
            identity with no held node would corrupt the partition. This is
            the ONLY path that removes a residence, it is private, and it is
            guarded: it only removes a claim that still points at the failed
            lane.

        Contract:
            - The public no-release law stands: residence is permanent for
              every SUCCESSFUL registration.

        Args:
            spell_id:
                Identity whose failed claim is being compensated.
            lane_id:
                The lane the failed registration targeted.

        Returns:
            None.
        """
        with self._lock:
            if self._lane_id_by_spell_id.get(spell_id) == lane_id:
                del self._lane_id_by_spell_id[spell_id]

    def residence_of(self, spell_id: str) -> Optional[str]:
        """
        Return the lane holding one identity, when resident.

        Contract:
            - `None` means NOT RESIDENT in this set - a normal answer, never an
              error. This is the raw partition lookup the set's own
              `residence_of` delegates to.
            - Answers residence only: it does not confirm the holding lane still
              carries the node, nor that the lane is open. Residence is permanent
              through archive, so a resident answer can point at an archived lane.

        Threading:
            Read under `self._lock`; a point-in-time answer.

        Args:
            spell_id:
                Identity to look up.

        Returns:
            Optional[str]:
                Holding lane id or None.
        """
        self.check_cleaned()
        with self._lock:
            return self._lane_id_by_spell_id.get(spell_id)

    def is_resident(self, spell_id: str) -> bool:
        """
        Return whether one identity is resident ANYWHERE in this set.

        Contract:
            - Network-wide test, not lane-scoped: True means the identity resides
              in SOME lane of this set. It is the rediscovery probe the runtime
              seam uses before a `record_world_entry` to decide "already known,
              quiet no-op" versus "fresh, register".
            - Equivalent to `residence_of(spell_id) is not None`, without
              returning the lane.

        Threading:
            Read under `self._lock`.

        Args:
            spell_id:
                Identity to test.

        Returns:
            bool:
                True when resident.
        """
        self.check_cleaned()
        with self._lock:
            return spell_id in self._lane_id_by_spell_id

    @property
    def resident_count(self) -> int:
        """
        Return the number of resident identities.

        Contract:
            - Counts DISTINCT identities in the partition, which equals the total
              node count across all lanes since residence is one-per-identity.
            - Only ever grows through `claim`; `transfer` moves identities
              between lanes without changing this, and there is no release verb,
              so it does not shrink except by rollback of a failed claim.

        Threading:
            Read under `self._lock`.

        Returns:
            int:
                Current residence count.
        """
        self.check_cleaned()
        with self._lock:
            return len(self._lane_id_by_spell_id)

    def describe(self) -> Dict[str, object]:
        """
        Return a detached, serialization-ready residence payload.

        Contract:
            - THE EXACT INVERSE of `from_payload()`: one key,
              `lane_id_by_spell_id`, holding a COPY of the partition map so
              mutating the result cannot alter the registry.
            - Plain sha -> lane strings throughout, so it crosses a JSON boundary
              losslessly.

        Threading:
            The map copy is taken under `self._lock`.

        Returns:
            Dict[str, object]:
                Plain-value payload with the sha -> lane mapping.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "lane_id_by_spell_id": dict(self._lane_id_by_spell_id),
            }

    @classmethod
    def from_payload(cls, payload: Dict[str, object]) -> "ResidenceRegistry":
        """
        Rebuild one registry from a `describe()` payload.

        Contract:
            - Requires a dict payload carrying a dict `lane_id_by_spell_id`;
              either being absent or wrong-typed raises `ValueError`.
            - REBUILDS WHOLESALE into a fresh registry - it never edits an
              existing one in place. This is the network-restore path.
            - COERCES keys and values to `str` on the way in, so a payload that
              round-tripped through JSON (which may have stringified nothing, but
              the coercion makes it defensive) rebuilds cleanly.
            - Does NOT re-run `claim`, so it does not raise on the entries it
              loads - a snapshot is trusted to already satisfy single-residence;
              restore installs it rather than re-validating each claim.

        Threading:
            Entries are loaded under the new registry's own lock; the rebuilt
            object is not shared until this returns.

        Args:
            payload:
                Detached payload produced by `describe()`.

        Returns:
            ResidenceRegistry:
                Reconstructed registry.

        Raises:
            ValueError:
                If the payload shape is invalid.
        """
        if not isinstance(payload, dict):
            raise ValueError("payload must be a dict produced by describe().")
        mapping = payload.get("lane_id_by_spell_id")
        if not isinstance(mapping, dict):
            raise ValueError(
                "payload is missing a valid 'lane_id_by_spell_id' mapping."
            )
        registry = cls()
        with registry._lock:
            for spell_id, lane_id in mapping.items():
                registry._lane_id_by_spell_id[str(spell_id)] = str(lane_id)
        return registry
