

import threading
from typing import Dict, List, Optional, Tuple

from melder.crystallizer.crystals.aether_crystal import AetherCrystal
from melder.crystallizer.crystals.aetheric_frame_crystal import AethericFrameCrystal
from melder.crystallizer.crystals.conduit_crystal import ConduitCrystal
from melder.crystallizer.crystals.crystallizer_crystal import (
    CrystallizerCrystal,
)
from melder.crystallizer.crystals.mutation_research_crystal import MutationResearchCrystal
from melder.crystallizer.crystals.cluster_crystal import (
    ClusterCrystal,
)
from melder.crystallizer.crystals.contract_crystal import (
    ContractCrystal,
)
from melder.crystallizer.crystals.spell_index_crystal import (
    SpellIndexCrystal,
)
from melder.crystallizer.crystals.recorded_unit_state import RecordedUnitState
from melder.crystallizer.crystals.nexus_crystal import NexusCrystal
from melder.crystallizer.crystals.spell_crystal import SpellCrystal
from melder.crystallizer.crystals.spellbook_crystal import SpellbookCrystal
from melder.utilities.general_base.cleanable import Cleanable


class PersistenceProfile(Cleanable):
    """
    One recorded world: the flat, level-mapped twin store for a single profile.

    Purpose:
        Hold the digital-twin record of one world under one profile name. The
        "default" profile is the live mirror (emissions land on the ACTIVE
        profile, which starts as "default"); named profiles are saved worlds
        (bootstraps / kits). Storage follows the aetheric_frame pattern: flat
        maps per level with parent-reference edges on the twins, never nested
        twin objects. The owner hierarchy is presented at the API:

            AetherCrystal
              -> MutationResearchCrystal & NexusCrystal & AethericFrameCrystal
                -> SpellbookCrystal
                  -> SpellCrystal (bind signatures + module custody)
                     & ConduitCrystal

    Contract:
        - Replace-on-emit: recording a twin replaces the prior twin for
          that identity wholesale and cleans the displaced object. Readers see
          whole-object state rather than in-place mutation, but must fetch
          fresh for each use instead of retaining a long-lived twin reference.
        - The L3 spell node IS the SpellCrystal: it carries both the bind
          signatures (binding_name / spellframe / existence / permissions /
          rebindability) and the module-world custody in one object.
        - Emission sequence: every record is journaled with a monotonically
          increasing sequence number; replay order derives from it.
        - L3 rule (documented for the restore engine): spell crystals replay
          as binds before their spellbook's conduit twin; link edges last.

    Threading:
        One instance RLock serializes all record/clear operations. Twin
        objects themselves are immutable-after-init (SpellCrystal carries its
        own internal lock).

    Lifecycle / Cleanup:
        Owned by exactly one `PersistenceSystem`; checkpoint crystals are
        detached snapshots and never own profiles. Cleanup releases every live
        twin held by this profile, clears journal/state surfaces, and deletes
        the profile lock last.
    """

    __slots__ = Cleanable.__slots__ + [
        "_profile_name",
        "_lock",
        "_emission_sequence",
        "_emission_log",
        "_last_checkpoint_sequence",
        "_aether_crystal",
        "_crystallizer_crystal",
        "_nexus_crystal",
        "_mutation_research_crystal",
        "_nexus_state",
        "_mutation_research_state",
        "_frame_crystals_by_name",
        "_spellbook_crystals_by_id",
        "_conduit_crystals_by_id",
        "_spell_index_crystals_by_index_id",
        "_contract_crystals_by_contract_id",
        "_cluster_crystals_by_cluster_id",
        "_spell_crystals_by_spell_id",
        "_inactive_spell_crystals_by_spell_id",
    ]

    def __init__(self, profile_name: str) -> None:
        """
        Initialize one empty profile store.

        Contract:
            Starts with sequence and checkpoint marks at zero, empty level
            maps, and no singleton state observations. Construction creates no
            twin and performs no disk or remote operation.

        Args:
            profile_name:
                The profile's name ("default" is the initial live mirror;
                any other name is a saved or user-created world).

        Returns:
            None.

        Raises:
            ValueError:
                If `profile_name` is empty.
        """
        super().__init__()
        if not profile_name:
            raise ValueError(
                "PersistenceProfile requires a non-empty profile_name."
            )
        self._profile_name: str = profile_name
        self._lock: threading.RLock = threading.RLock()
        self._emission_sequence: int = 0
        self._emission_log: List[Tuple[int, str, str]] = []
        self._last_checkpoint_sequence: int = 0
        self._aether_crystal: Optional[AetherCrystal] = None
        self._crystallizer_crystal: Optional[CrystallizerCrystal] = None
        self._nexus_crystal: Optional[NexusCrystal] = None
        self._mutation_research_crystal: Optional[MutationResearchCrystal] = None
        # State switches for the two singletons tracked by state instead of
        # eviction (None = never recorded; see RecordedUnitState contract).
        self._nexus_state: Optional[RecordedUnitState] = None
        self._mutation_research_state: Optional[RecordedUnitState] = None
        self._frame_crystals_by_name: Dict[str, AethericFrameCrystal] = {}
        self._spellbook_crystals_by_id: Dict[str, SpellbookCrystal] = {}
        self._conduit_crystals_by_id: Dict[str, ConduitCrystal] = {}
        self._spell_index_crystals_by_index_id: Dict[str, SpellIndexCrystal] = {}
        self._contract_crystals_by_contract_id: Dict[str, ContractCrystal] = {}
        self._cluster_crystals_by_cluster_id: Dict[str, ClusterCrystal] = {}
        self._spell_crystals_by_spell_id: Dict[str, SpellCrystal] = {}
        self._inactive_spell_crystals_by_spell_id: Dict[str, SpellCrystal] = {}

    def cleanup(self) -> None:
        """
        Clean every held twin, then release owned fields (lock last).

        Contract:
            - Idempotent and terminal; cleans every currently held twin.
            - Singleton slots, level maps, state switches, emission journal,
              and checkpoint mark are then deleted; the lock is deleted last.
            - Sealed `PersistenceCrystal` snapshots are not owned here and
              survive profile cleanup in the system ledger.

        Threading:
            Serialized by the profile lock. No record/clear operation may race
            with teardown.

        Lifecycle / Cleanup:
            Invoked by profile deletion, system cleanup, or profile replacement
            ownership paths; displaced twins have already followed the same
            child-cleanup rule individually.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._cleanup_all_twins()
        del self._profile_name
        del self._emission_sequence
        del self._emission_log
        del self._last_checkpoint_sequence
        del self._aether_crystal
        del self._crystallizer_crystal
        del self._nexus_crystal
        del self._mutation_research_crystal
        del self._nexus_state
        del self._mutation_research_state
        del self._frame_crystals_by_name
        del self._spellbook_crystals_by_id
        del self._conduit_crystals_by_id
        del self._spell_index_crystals_by_index_id
        del self._contract_crystals_by_contract_id
        del self._cluster_crystals_by_cluster_id
        del self._spell_crystals_by_spell_id
        del self._inactive_spell_crystals_by_spell_id
        del self._lock

    @property
    def profile_name(self) -> str:
        """
        Return this profile's name.

        Returns:
            str:
                The profile name.
        """
        self.check_cleaned()
        return self._profile_name

    def record(self, twin: Cleanable) -> None:
        """
        Record one emitted twin into this profile (typed dispatch).

        Purpose:
            The single sink entry: dispatch on the twin's concrete type and
            replace-on-emit into the matching level map. This is what
            `Crystallizer.emit(...)` will call for the active profile.

        Contract:
            - Replace-on-emit; the displaced twin (if any) is cleaned.
            - Journals (sequence, kind, key) for replay ordering.
            - Unknown twin types are a caller bug: raises TypeError with the
              received type named.

        Args:
            twin:
                One twin instance from the persistence crystal family
                (SpellCrystal is the L3 spell node).

        Returns:
            None.

        Raises:
            RuntimeError:
                If the profile has been cleaned.
            TypeError:
                If `twin` is not a member of the twin family.
        """
        self.check_cleaned()
        with self._lock:
            if isinstance(twin, AetherCrystal):
                previous_aether = self._aether_crystal
                if previous_aether is not None and not previous_aether.cleaned:
                    previous_aether.cleanup()
                self._aether_crystal = twin
                self._journal("aether", "root")
            elif isinstance(twin, CrystallizerCrystal):
                # The recorder's own policy twin (self-emitted at
                # crystallizer activation); root-singleton semantics.
                previous_crystallizer = self._crystallizer_crystal
                if (
                        previous_crystallizer is not None
                        and not previous_crystallizer.cleaned
                ):
                    previous_crystallizer.cleanup()
                self._crystallizer_crystal = twin
                self._journal("crystallizer", "root")
            elif isinstance(twin, NexusCrystal):
                previous_nexus = self._nexus_crystal
                if previous_nexus is not None and not previous_nexus.cleaned:
                    previous_nexus.cleanup()
                self._nexus_crystal = twin
                self._journal("nexus", "root")
            elif isinstance(twin, MutationResearchCrystal):
                previous_mr = self._mutation_research_crystal
                if previous_mr is not None and not previous_mr.cleaned:
                    previous_mr.cleanup()
                self._mutation_research_crystal = twin
                self._journal("mutation_research", "root")
            elif isinstance(twin, AethericFrameCrystal):
                self._replace_mapped(
                    self._frame_crystals_by_name, twin.frame_name, twin, "frame"
                )
            elif isinstance(twin, SpellbookCrystal):
                self._replace_mapped(
                    self._spellbook_crystals_by_id, twin.spellbook_id, twin, "spellbook"
                )
            elif isinstance(twin, ConduitCrystal):
                self._replace_mapped(
                    self._conduit_crystals_by_id, twin.conduit_id, twin, "conduit"
                )
            elif isinstance(twin, SpellIndexCrystal):
                self._replace_mapped(
                    self._spell_index_crystals_by_index_id,
                    twin.index_id,
                    twin,
                    "spell_index",
                )
            elif isinstance(twin, ContractCrystal):
                self._replace_mapped(
                    self._contract_crystals_by_contract_id,
                    twin.contract_id,
                    twin,
                    "contract",
                )
            elif isinstance(twin, ClusterCrystal):
                self._replace_mapped(
                    self._cluster_crystals_by_cluster_id,
                    twin.cluster_id,
                    twin,
                    "cluster",
                )
            elif isinstance(twin, SpellCrystal):
                self._record_spell_crystal_locked(twin, active=True)
            else:
                raise TypeError(
                    "PersistenceProfile.record received an unsupported twin "
                    "type: {0}. Supported: the persistence crystal family "
                    "(SpellCrystal is the L3 spell node).".format(
                        type(twin).__name__
                    )
                )

    def record_spell_crystal(self, crystal: SpellCrystal, active: bool) -> None:
        """
        Record one custody crystal into the active or inactive location.

        Purpose:
            Mirror the spellbook's own active/parked split: active binds
            record into the active location, staged (bind_inactive) binds
            record into the inactive location.

        Contract:
            - Replace-on-emit across BOTH locations: any prior crystal for
              the spell_id is cleaned wherever it lived.

        Args:
            crystal:
                The custody crystal to record.
            active:
                Which location receives it.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the profile has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self._record_spell_crystal_locked(crystal, active=active)

    def record_spell_activity(self, spell_id: str, active: bool) -> None:
        """
        Move one spell's crystal between the active/inactive locations.

        Purpose:
            The record-side mirror of the runtime park/promote flip
            (`_deactivate_owned_spell` / `_reactivate_owned_spell`).

        Contract:
            - Tolerates missing custody (activity for a spell the record
              never held): the activity is journaled either way so
              checkpoints capture the transition truthfully.

        Args:
            spell_id:
                The spell whose activity flipped.
            active:
                True = promoted to active; False = parked inactive.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the profile has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            if active:
                crystal = self._inactive_spell_crystals_by_spell_id.pop(spell_id, None)
                if crystal is not None:
                    self._spell_crystals_by_spell_id[spell_id] = crystal
            else:
                crystal = self._spell_crystals_by_spell_id.pop(spell_id, None)
                if crystal is not None:
                    self._inactive_spell_crystals_by_spell_id[spell_id] = crystal
            self._journal("spell_activity", spell_id)

    def remove_spell_crystal(self, spell_id: str) -> None:
        """
        Evict one spell's custody from the record entirely.

        Purpose:
            The record-side mirror of true spell removal
            (cleanup_and_remove_spell): custody LEAVES both locations so a
            restore never over-builds a world that shed spells.

        Contract:
            - Tolerates missing custody; journals "spell_removed" either way.

        Args:
            spell_id:
                The removed spell's SHA256 identity.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the profile has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            for location in (
                    self._spell_crystals_by_spell_id,
                    self._inactive_spell_crystals_by_spell_id,
            ):
                crystal = location.pop(spell_id, None)
                if crystal is not None and not crystal.cleaned:
                    crystal.cleanup()
            self._journal("spell_removed", spell_id)

    def remove_spellbook_subtree(self, spellbook_id: str) -> None:
        """
        Evict one spellbook's ENTIRE record subtree.

        Purpose:
            The record-side mirror of whole-spellbook death in a live world
            (root-conduit teardown reaches Spellbook.cleanup(); the frame
            cascade arrives through the same lane). The book twin, every
            conduit twin parented to it, and every spell custody crystal
            assigned to it leave the record together so restore never
            rebuilds a dead book's world.

        Contract:
            - Sweep is by parent-edge match: ConduitCrystal.spellbook_id and
              SpellCrystal.spellbook_id equal to `spellbook_id`, across BOTH
              custody locations.
            - Tolerates a book that never recorded (journals either way).
            - Journals ONE "spellbook_removed" entry; checkpoint replay
              applies the same match as a subtree tombstone.

        Args:
            spellbook_id:
                The dead spellbook's identity.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the profile has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self._remove_spellbook_subtree_locked(spellbook_id)

    def remove_frame_crystal(self, frame_name: str) -> None:
        """
        Evict one dead frame's twin plus any remaining book subtrees.

        Purpose:
            The record-side mirror of frame death in a live world
            (AethericFrame.cleanup detaches the frame from the live Aether).
            The frame's conduits/spellbooks normally evicted themselves
            during the frame's own teardown cascade; the by-frame book
            sweep here is the tolerant net for anything that slipped a
            gated cascade.

        Contract:
            - Tolerates a frame that never recorded (journals either way).
            - Remaining books sweep through the same subtree eviction as
              direct book death, journaling per book, then ONE
              "frame_removed" entry seals the frame itself.

        Args:
            frame_name:
                The dead frame's canonical name.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the profile has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            twin = self._frame_crystals_by_name.pop(frame_name, None)
            if twin is not None and not twin.cleaned:
                twin.cleanup()
            remaining_book_ids = [
                spellbook_id
                for spellbook_id, crystal in (
                    self._spellbook_crystals_by_id.items()
                )
                if crystal.frame_name == frame_name
            ]
            for spellbook_id in remaining_book_ids:
                self._remove_spellbook_subtree_locked(spellbook_id)
            cluster_ids = [
                cluster_id
                for cluster_id, crystal in (
                    self._cluster_crystals_by_cluster_id.items()
                )
                if crystal.frame_name == frame_name
            ]
            for cluster_id in cluster_ids:
                crystal = self._cluster_crystals_by_cluster_id.pop(cluster_id)
                if not crystal.cleaned:
                    crystal.cleanup()
            self._journal("frame_removed", frame_name)

    def record_nexus_state(self, state: RecordedUnitState) -> None:
        """
        Flip the recorded Nexus lifecycle switch (twin retained).

        Purpose:
            Nexus disable/re-enable keeps its installed configuration, so
            its twin stays; this switch is the truth restore reads.

        Args:
            state:
                The new recorded state.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the profile has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self._nexus_state = state
            self._journal("nexus_state", state.name)

    def record_mutation_research_state(self, state: RecordedUnitState) -> None:
        """
        Flip the recorded MutationResearch lifecycle switch (twin retained).

        Args:
            state:
                The new recorded state.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the profile has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self._mutation_research_state = state
            self._journal("mutation_research_state", state.name)

    def remove_spell_index_crystal(self, index_id: str) -> None:
        """
        Evict one destroyed index's membership twin from the record.

        Contract:
            - Tolerates an index that never recorded (journals either way);
              journals ONE "spell_index_removed" entry.

        Args:
            index_id:
                The destroyed index's record-local ULID key.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the profile has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            twin = self._spell_index_crystals_by_index_id.pop(index_id, None)
            if twin is not None and not twin.cleaned:
                twin.cleanup()
            self._journal("spell_index_removed", index_id)

    def remove_contract_crystal(self, contract_id: str) -> None:
        """
        Evict one severed contract's relationship twin from the record.

        Contract:
            - Tolerates a contract that never recorded (journals either
              way); journals ONE "contract_removed" entry.

        Args:
            contract_id:
                The severed contract's record-local ULID key.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the profile has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            twin = self._contract_crystals_by_contract_id.pop(contract_id, None)
            if twin is not None and not twin.cleaned:
                twin.cleanup()
            self._journal("contract_removed", contract_id)

    def remove_cluster_crystal(self, cluster_id: str) -> None:
        """
        Evict one deleted cluster's twin from the record.

        Contract:
            - Tolerates a cluster that never recorded (journals either
              way); journals ONE "cluster_removed" entry.

        Args:
            cluster_id:
                The deleted cluster's record-local ULID key.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the profile has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            twin = self._cluster_crystals_by_cluster_id.pop(cluster_id, None)
            if twin is not None and not twin.cleaned:
                twin.cleanup()
            self._journal("cluster_removed", cluster_id)

    def _remove_spellbook_subtree_locked(self, spellbook_id: str) -> None:
        """
        Internal

        Evict one book subtree under the held lock (see the public verb).

        Contract:
            - Caller holds `self._lock`.
            - Journals the "spellbook_removed" entry itself so frame-level
              sweeps produce the same replay events as direct book death.

        Args:
            spellbook_id:
                The dead spellbook's identity.

        Returns:
            None.
        """
        book = self._spellbook_crystals_by_id.pop(spellbook_id, None)
        if book is not None and not book.cleaned:
            book.cleanup()
        conduit_ids = [
            conduit_id
            for conduit_id, crystal in self._conduit_crystals_by_id.items()
            if crystal.spellbook_id == spellbook_id
        ]
        for conduit_id in conduit_ids:
            crystal = self._conduit_crystals_by_id.pop(conduit_id)
            if not crystal.cleaned:
                crystal.cleanup()
        index_ids = [
            index_id
            for index_id, crystal in (
                self._spell_index_crystals_by_index_id.items()
            )
            if crystal.spellbook_id == spellbook_id
        ]
        for index_id in index_ids:
            crystal = self._spell_index_crystals_by_index_id.pop(index_id)
            if not crystal.cleaned:
                crystal.cleanup()
        # Defense net: contracts touching the swept conduits leave too
        # (the live path evicts via the _remove_contract seam; this covers
        # gated-off cascades so no relationship outlives its endpoints).
        swept_conduit_ids = set(conduit_ids)
        contract_ids = [
            contract_id
            for contract_id, crystal in (
                self._contract_crystals_by_contract_id.items()
            )
            if crystal.conduit_a_id in swept_conduit_ids
            or crystal.conduit_b_id in swept_conduit_ids
        ]
        for contract_id in contract_ids:
            crystal = self._contract_crystals_by_contract_id.pop(contract_id)
            if not crystal.cleaned:
                crystal.cleanup()
        for location in (
                self._spell_crystals_by_spell_id,
                self._inactive_spell_crystals_by_spell_id,
        ):
            spell_ids = [
                spell_id
                for spell_id, crystal in location.items()
                if crystal.spellbook_id == spellbook_id
            ]
            for spell_id in spell_ids:
                crystal = location.pop(spell_id)
                if not crystal.cleaned:
                    crystal.cleanup()
        self._journal("spellbook_removed", spellbook_id)

    def _record_spell_crystal_locked(self, crystal: SpellCrystal, active: bool) -> None:
        """
        Record one crystal under the held lock (shared by record paths).

        Contract:
            - Caller holds `self._lock`.
            - Displaces + cleans any prior crystal from both locations.

        Args:
            crystal:
                The custody crystal to record.
            active:
                Which location receives it.

        Returns:
            None.
        """
        for location in (
                self._spell_crystals_by_spell_id,
                self._inactive_spell_crystals_by_spell_id,
        ):
            previous = location.pop(crystal.id, None)
            if previous is not None and not previous.cleaned:
                previous.cleanup()
        target = (
            self._spell_crystals_by_spell_id
            if active
            else self._inactive_spell_crystals_by_spell_id
        )
        target[crystal.id] = crystal
        self._journal("spell_crystal", crystal.id)

    def get_spell_crystal(self, spell_id: str) -> SpellCrystal:
        """
        Return the custody crystal recorded for one spell.

        Purpose:
            The runtime-facing custody lookup: loaders and MR fetch a
            spell's crystal fresh on each use (the profile is the single
            owner; replace-on-emit cleans displaced crystals, so holders
            must not retain long-lived references).

        Args:
            spell_id:
                The spell's SHA256 identity.

        Returns:
            SpellCrystal:
                The currently recorded crystal for the spell.

        Raises:
            RuntimeError:
                If the profile has been cleaned.
            KeyError:
                If no crystal is recorded under `spell_id`; the message
                reports the recorded count so callers can self-correct.
        """
        self.check_cleaned()
        with self._lock:
            crystal = self._spell_crystals_by_spell_id.get(spell_id)
            if crystal is None:
                crystal = self._inactive_spell_crystals_by_spell_id.get(spell_id)
            if crystal is None:
                raise KeyError(
                    "No spell crystal recorded for spell_id {0!r} in "
                    "profile {1!r} ({2} crystals recorded).".format(
                        spell_id,
                        self._profile_name,
                        len(self._spell_crystals_by_spell_id),
                    )
                )
            return crystal

    def describe_spell_crystals(self) -> Dict[str, Dict[str, object]]:
        """
        Return every recorded custody crystal as a detached payload map.

        Purpose:
            The impact-engine read seam (S3): blast-radius questions need
            the WHOLE custody surface at once, not per-spell lookups.
            Payloads only - no twin object escapes (record law).

        Contract:
            - Covers BOTH custody maps; each payload gains the additive
              "custody_state" key ("active" | "inactive").
            - Detached describe() dicts; mutating them never touches the
              record.

        Returns:
            Dict[str, Dict[str, object]]:
                spell_id -> crystal describe() payload + custody_state.

        Raises:
            RuntimeError: If the profile has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            payloads: Dict[str, Dict[str, object]] = {}
            for spell_id, crystal in (
                    self._spell_crystals_by_spell_id.items()
            ):
                payload = crystal.describe()
                payload["custody_state"] = "active"
                payloads[spell_id] = payload
            for spell_id, crystal in (
                    self._inactive_spell_crystals_by_spell_id.items()
            ):
                payload = crystal.describe()
                payload["custody_state"] = "inactive"
                payloads[spell_id] = payload
            return payloads

    def capture_index_graft(self, index_id: str) -> Dict[str, object]:
        """
        Capture one spell_index's full graft record (S-graft lane).

        Purpose:
            The graft unit is the INDEX (owner ruling): all member spells
            active + parked, their custody payloads, and the selection -
            one versioned, JSON-safe dict the GraftRunner re-integrates
            into a LIVE host book. Storage is the caller's choice (mesh
            handlers, formations, plain files).

        Contract:
            - Detached payloads only (no twin escapes).
            - Members missing custody report under "members_without_
              custody" instead of raising (shortfall honesty; the runner
              refuses those members at graft time).

        Args:
            index_id:
                The recorded index identity.

        Returns:
            Dict[str, object]:
                {record_version, "graft_kind": "spell_index", index_id,
                 "index_payload", "members": {spell_id: {"payload",
                 "custody_state"}}, "members_without_custody": [ids]}.

        Raises:
            RuntimeError: If the profile has been cleaned.
            KeyError: If no index twin is recorded under `index_id`.
        """
        from melder.crystallizer.persistence.record_version import (
            RecordVersion,
        )

        self.check_cleaned()
        with self._lock:
            twin = self._spell_index_crystals_by_index_id.get(index_id)
            if twin is None:
                raise KeyError(
                    "No spell_index crystal recorded under {0!r} "
                    "({1} recorded).".format(
                        index_id,
                        len(self._spell_index_crystals_by_index_id),
                    )
                )
            index_payload = twin.describe()
            members: Dict[str, Dict[str, object]] = {}
            missing: List[str] = []
            for spell_id in list(index_payload.get("member_spell_ids", [])):
                crystal = self._spell_crystals_by_spell_id.get(spell_id)
                custody_state = "active"
                if crystal is None:
                    crystal = self._inactive_spell_crystals_by_spell_id.get(
                        spell_id
                    )
                    custody_state = "inactive"
                if crystal is None:
                    missing.append(str(spell_id))
                    continue
                members[str(spell_id)] = {
                    "payload": crystal.describe(),
                    "custody_state": custody_state,
                }
            return RecordVersion.stamp({
                "graft_kind": "spell_index",
                "index_id": str(index_id),
                "index_payload": index_payload,
                "members": members,
                "members_without_custody": missing,
            })

    def describe_mutation_research_record(self) -> Optional[Dict[str, object]]:
        """
        Return the recorded MutationResearch twin payload, when one exists.

        Purpose:
            The MR hydration read: the root pulls the recorded composition
            (twin `describe()` form) at activation to rebuild its research
            registry from the record. A detached dict is returned - the
            twin object never escapes the profile.

        Returns:
            Optional[Dict[str, object]]:
                The recorded twin's `describe()` payload, or None when the
                profile has never recorded the MR twin.

        Raises:
            RuntimeError:
                If the profile has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            twin = self._mutation_research_crystal
            if twin is None or twin.cleaned:
                return None
            return twin.describe()

    def describe(self) -> Dict[str, object]:
        """
        Return a detached structural summary of this profile.

        Returns:
            Dict[str, object]:
                Profile name, per-level counts, singleton presence flags,
                and the current emission sequence.

        Raises:
            RuntimeError:
                If the profile has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "profile_name": self._profile_name,
                "emission_sequence": self._emission_sequence,
                "has_aether_crystal": self._aether_crystal is not None,
                "has_nexus_crystal": self._nexus_crystal is not None,
                "has_mutation_research_crystal":
                    self._mutation_research_crystal is not None,
                "nexus_state": (
                    self._nexus_state.name
                    if self._nexus_state is not None else None
                ),
                "mutation_research_state": (
                    self._mutation_research_state.name
                    if self._mutation_research_state is not None else None
                ),
                "frame_count": len(self._frame_crystals_by_name),
                "spellbook_count": len(self._spellbook_crystals_by_id),
                "conduit_count": len(self._conduit_crystals_by_id),
                "spell_index_count":
                    len(self._spell_index_crystals_by_index_id),
                "contract_count":
                    len(self._contract_crystals_by_contract_id),
                "cluster_count":
                    len(self._cluster_crystals_by_cluster_id),
                "spell_crystal_count": len(self._spell_crystals_by_spell_id),
                "inactive_spell_crystal_count":
                    len(self._inactive_spell_crystals_by_spell_id),
            }

    # NOTE (2026-07-11, S1 load-scope maturity, owner ruling): the
    # compose_frame_subtree / compose_conduit_subtree NotImplementedError
    # placeholders that lived here were DELETED, not implemented - zero
    # callers tree-wide, and capture_formation_slice is the composer that
    # actually shipped (formation records + the LoadAdmission synthetic
    # window replaced the imagined tree-view shape).

    def clear(self) -> None:
        """
        Clean and drop every held twin, resetting the profile to empty.

        Contract:
            - The profile object itself stays live (reusable); only content
              resets. This is the profile-scoped form of `clear_bootstrap`.
            - Emission journal and sequence reset with the content.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the profile has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self._cleanup_all_twins()
            self._emission_sequence = 0
            self._emission_log = []
            self._last_checkpoint_sequence = 0
            # State switches are recorded content too: a cleared profile
            # must not report a previous world's singleton lifecycle.
            self._nexus_state = None
            self._mutation_research_state = None


    @property
    def last_checkpoint_sequence(self) -> int:
        """
        Return the emission sequence consumed by the most recent checkpoint.

        Returns:
            int:
                Highest journal sequence already captured (0 = never
                checkpointed since creation/clear).

        Raises:
            RuntimeError:
                If the profile has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return self._last_checkpoint_sequence

    def capture_segment_since(
            self,
            sequence_mark: int,
    ) -> Tuple[Dict[str, Dict[str, Dict[str, object]]], List[Tuple[int, str, str]], Tuple[int, int]]:
        """
        Capture the incremental segment journaled after one sequence mark.

        Purpose:
            The checkpoint mechanic: collect every identity journaled after
            `sequence_mark` and detach the CURRENT twin state of each into
            plain-value payloads. Full objects, never diffs - at the twin
            level each entry is the complete final state; incrementality is
            at the world level (only identities that changed appear).

        Contract:
            - Payloads are fully detached (twin.describe() output); the
              returned data is immune to later replace-on-emit cleanup.
            - Identities journaled but since replaced capture their CURRENT
              twin (the final state within the segment window).
            - Does NOT advance the checkpoint mark; callers seal first, then
              `mark_checkpoint(...)` on success.

        Args:
            sequence_mark:
                Capture everything journaled with sequence > this value.

        Returns:
            Tuple[
                Dict[str, Dict[str, Dict[str, object]]],
                List[Tuple[int, str, str]],
                Tuple[int, int],
            ]:
                (payloads by kind -> key -> payload,
                 journal entries in the segment,
                 (first_sequence, last_sequence) of the capture window where
                 first_sequence = sequence_mark + 1 and last_sequence = the
                 profile's current emission sequence).

        Raises:
            RuntimeError:
                If the profile has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            segment_entries: List[Tuple[int, str, str]] = [
                entry for entry in self._emission_log if entry[0] > sequence_mark
            ]
            payloads: Dict[str, Dict[str, Dict[str, object]]] = {}
            for _sequence, kind, key in segment_entries:
                if kind == "frame_removed":
                    payloads.setdefault(kind, {})[key] = {
                        "frame_name": key,
                        "removed": True,
                    }
                    continue
                if kind in ("nexus_state", "mutation_research_state"):
                    # The journal key carries the flipped state; twin stays.
                    payloads.setdefault(kind, {})[key] = {
                        "state": key,
                        "twin_present": (
                            self._nexus_crystal is not None
                            if kind == "nexus_state"
                            else self._mutation_research_crystal is not None
                        ),
                    }
                    continue
                if kind == "cluster_removed":
                    payloads.setdefault(kind, {})[key] = {
                        "cluster_id": key,
                        "removed": True,
                    }
                    continue
                if kind == "contract_removed":
                    payloads.setdefault(kind, {})[key] = {
                        "contract_id": key,
                        "removed": True,
                    }
                    continue
                if kind == "spell_index_removed":
                    payloads.setdefault(kind, {})[key] = {
                        "index_id": key,
                        "removed": True,
                    }
                    continue
                if kind == "spellbook_removed":
                    # Subtree tombstone: replay applies the same
                    # spellbook_id parent-edge match this eviction used.
                    payloads.setdefault(kind, {})[key] = {
                        "spellbook_id": key,
                        "removed": True,
                    }
                    continue
                if kind == "spell_removed":
                    payloads.setdefault(kind, {})[key] = {
                        "spell_id": key,
                        "removed": True,
                    }
                    continue
                if kind == "spell_activity":
                    # Activity transitions have no twin object; capture the
                    # CURRENT truth: which location holds custody now.
                    payloads.setdefault(kind, {})[key] = {
                        "spell_id": key,
                        "active": key in self._spell_crystals_by_spell_id,
                        "custody_present": (
                            key in self._spell_crystals_by_spell_id
                            or key in self._inactive_spell_crystals_by_spell_id
                        ),
                    }
                    continue
                if kind == "spell_crystal":
                    # Capture-gap fix (restore_engine_2026_07_07): custody
                    # that never flips emits no spell_activity entry, so the
                    # window must carry WHICH location holds it now or the
                    # restore engine cannot tell staged members from actives.
                    crystal = self._resolve_twin(kind, key)
                    if crystal is None or crystal.cleaned:
                        continue
                    custody_payload = crystal.describe()
                    custody_payload["custody_location"] = (
                        "active"
                        if key in self._spell_crystals_by_spell_id
                        else "inactive"
                    )
                    payloads.setdefault(kind, {})[key] = custody_payload
                    continue
                twin = self._resolve_twin(kind, key)
                if twin is None or twin.cleaned:
                    continue
                payloads.setdefault(kind, {})[key] = twin.describe()
            return (
                payloads,
                segment_entries,
                (sequence_mark + 1, self._emission_sequence),
            )

    def capture_formation_slice(
            self,
            conduit_id: Optional[str] = None,
            frame_name: Optional[str] = None,
    ) -> Dict[str, Dict[str, Dict[str, object]]]:
        """
        Capture one LIVE formation slice (owner feature: scoped snapshots).

        Purpose:
            Users keep the formations they like: a conduit formation
            (the conduit + its spellbook + that book's custody and
            indexes + contracts touching the conduit) or a frame
            formation (the frame posture + every book subtree on it +
            its clusters). The slice is CURRENT-STATE payloads only - no
            journal window - and restores through a manufactured
            single-window chain.

        Contract:
            - Exactly one scope argument must be supplied.
            - Payloads are fully detached describe() forms; custody
              payloads annotate custody_location from the live maps.
            - Contract/link peers OUTSIDE the slice ride along as
              recorded references (restore shortfalls them; the
              persistence analyzer pre-flights them).

        Args:
            conduit_id:
                Conduit-scope anchor (mutually exclusive with
                frame_name).
            frame_name:
                Frame-scope anchor.

        Returns:
            Dict[str, Dict[str, Dict[str, object]]]:
                {kind: {key: payload}} for the slice.

        Raises:
            RuntimeError: If the profile has been cleaned.
            ValueError: If zero or both scope arguments are supplied.
            KeyError: If the anchor names no recorded twin.
        """
        self.check_cleaned()
        if (conduit_id is None) == (frame_name is None):
            raise ValueError(
                "capture_formation_slice requires exactly one scope: "
                "conduit_id OR frame_name."
            )
        with self._lock:
            payloads: Dict[str, Dict[str, Dict[str, object]]] = {}

            def put(kind: str, key: str, payload: Dict[str, object]) -> None:
                payloads.setdefault(kind, {})[key] = payload

            def capture_book_subtree(spellbook_id: str) -> None:
                book = self._spellbook_crystals_by_id.get(spellbook_id)
                if book is not None and not book.cleaned:
                    put("spellbook", spellbook_id, book.describe())
                for index_id, index in (
                        self._spell_index_crystals_by_index_id.items()
                ):
                    if index.cleaned:
                        continue
                    index_payload = index.describe()
                    if index_payload.get("spellbook_id") == spellbook_id:
                        put("spell_index", index_id, index_payload)
                for location_name, store in (
                        ("active", self._spell_crystals_by_spell_id),
                        ("inactive", self._inactive_spell_crystals_by_spell_id),
                ):
                    for spell_id, custody in store.items():
                        if custody.cleaned:
                            continue
                        custody_payload = custody.describe()
                        if custody_payload.get("spellbook_id") != spellbook_id:
                            continue
                        custody_payload["custody_location"] = location_name
                        put("spell_crystal", spell_id, custody_payload)

            def capture_contracts_touching(conduit_ids: List[str]) -> None:
                for contract_id, contract in (
                        self._contract_crystals_by_contract_id.items()
                ):
                    if contract.cleaned:
                        continue
                    contract_payload = contract.describe()
                    if (
                            contract_payload.get("conduit_a_id") in conduit_ids
                            or contract_payload.get("conduit_b_id")
                            in conduit_ids
                    ):
                        put("contract", contract_id, contract_payload)

            if conduit_id is not None:
                conduit = self._conduit_crystals_by_id.get(conduit_id)
                if conduit is None or conduit.cleaned:
                    raise KeyError(
                        "No recorded conduit twin for id {0!r}; the "
                        "formation anchor must be a recorded conduit "
                        "(check describe_profile()).".format(conduit_id)
                    )
                conduit_payload = conduit.describe()
                put("conduit", conduit_id, conduit_payload)
                capture_book_subtree(
                    str(conduit_payload.get("spellbook_id"))
                )
                capture_contracts_touching([conduit_id])
                return payloads

            frame = self._frame_crystals_by_name.get(str(frame_name))
            if frame is None or frame.cleaned:
                raise KeyError(
                    "No recorded frame twin named {0!r}; frame-scoped "
                    "formations need the frame posture in the record "
                    "(dynamic frames emit at their configuration "
                    "freeze).".format(frame_name)
                )
            put("frame", str(frame_name), frame.describe())
            frame_conduit_ids: List[str] = []
            for spellbook_id, book in (
                    self._spellbook_crystals_by_id.items()
            ):
                if book.cleaned:
                    continue
                if book.describe().get("frame_name") != frame_name:
                    continue
                capture_book_subtree(spellbook_id)
                for cid, conduit in self._conduit_crystals_by_id.items():
                    if conduit.cleaned:
                        continue
                    conduit_payload = conduit.describe()
                    if conduit_payload.get("spellbook_id") == spellbook_id:
                        put("conduit", cid, conduit_payload)
                        frame_conduit_ids.append(cid)
            for cluster_id, cluster in (
                    self._cluster_crystals_by_cluster_id.items()
            ):
                if cluster.cleaned:
                    continue
                cluster_payload = cluster.describe()
                if cluster_payload.get("frame_name") == frame_name:
                    put("cluster", cluster_id, cluster_payload)
            capture_contracts_touching(frame_conduit_ids)
            return payloads

    def mark_checkpoint(self, sequence: int) -> None:
        """
        Advance the checkpoint mark after a successful seal.

        Args:
            sequence:
                Highest journal sequence the sealed checkpoint captured.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the profile has been cleaned.
            ValueError:
                If `sequence` would move the mark backward.
        """
        self.check_cleaned()
        with self._lock:
            if sequence < self._last_checkpoint_sequence:
                raise ValueError(
                    "mark_checkpoint cannot move backward: current mark is "
                    "{0}, received {1}.".format(
                        self._last_checkpoint_sequence, sequence
                    )
                )
            self._last_checkpoint_sequence = sequence

    def _resolve_twin(self, kind: str, key: str):
        """
        Resolve one journaled identity to its current twin, if still held.

        Contract:
            - Caller holds `self._lock`.

        Args:
            kind:
                Journal kind label.
            key:
                Identity key within the kind.

        Returns:
            The current twin for the identity, or None when the identity no
            longer resolves (for example after clear()).
        """
        if kind == "aether":
            return self._aether_crystal
        if kind == "crystallizer":
            return self._crystallizer_crystal
        if kind == "nexus":
            return self._nexus_crystal
        if kind == "mutation_research":
            return self._mutation_research_crystal
        if kind == "frame":
            return self._frame_crystals_by_name.get(key)
        if kind == "spellbook":
            return self._spellbook_crystals_by_id.get(key)
        if kind == "conduit":
            return self._conduit_crystals_by_id.get(key)
        if kind == "spell_index":
            return self._spell_index_crystals_by_index_id.get(key)
        if kind == "contract":
            return self._contract_crystals_by_contract_id.get(key)
        if kind == "cluster":
            return self._cluster_crystals_by_cluster_id.get(key)
        if kind == "spell_crystal":
            crystal = self._spell_crystals_by_spell_id.get(key)
            if crystal is None:
                crystal = self._inactive_spell_crystals_by_spell_id.get(key)
            return crystal
        return None

    def _replace_mapped(
            self,
            target_map: Dict[str, Cleanable],
            key: str,
            twin: Cleanable,
            kind: str,
    ) -> None:
        """
        Replace one keyed twin in a level map under the held lock.

        Contract:
            - Caller holds `self._lock`.
            - The displaced twin (if any) is cleaned before replacement.
            - Journals the emission.

        Args:
            target_map:
                The level map to write into.
            key:
                Identity key within the level.
            twin:
                Replacement twin.
            kind:
                Journal kind label.

        Returns:
            None.
        """
        previous = target_map.get(key)
        if previous is not None and not previous.cleaned:
            previous.cleanup()
        target_map[key] = twin
        self._journal(kind, key)

    def _journal(self, kind: str, key: str) -> None:
        """
        Append one emission-journal entry under the held lock.

        Args:
            kind:
                Twin kind label.
            key:
                Identity key recorded.

        Returns:
            None.
        """
        self._emission_sequence += 1
        self._emission_log.append((self._emission_sequence, kind, key))

    def _cleanup_all_twins(self) -> None:
        """
        Clean every held twin and reset all level containers.

        Contract:
            - Caller holds `self._lock` (or is inside cleanup()).

        Returns:
            None.
        """
        if self._aether_crystal is not None and not self._aether_crystal.cleaned:
            self._aether_crystal.cleanup()
        self._aether_crystal = None
        if (
                self._crystallizer_crystal is not None
                and not self._crystallizer_crystal.cleaned
        ):
            self._crystallizer_crystal.cleanup()
        self._crystallizer_crystal = None
        if self._nexus_crystal is not None and not self._nexus_crystal.cleaned:
            self._nexus_crystal.cleanup()
        self._nexus_crystal = None
        if (
                self._mutation_research_crystal is not None
                and not self._mutation_research_crystal.cleaned
        ):
            self._mutation_research_crystal.cleanup()
        self._mutation_research_crystal = None
        for level_map in (
                self._frame_crystals_by_name,
                self._spellbook_crystals_by_id,
                self._conduit_crystals_by_id,
                self._spell_index_crystals_by_index_id,
                self._contract_crystals_by_contract_id,
                self._cluster_crystals_by_cluster_id,
                self._spell_crystals_by_spell_id,
                self._inactive_spell_crystals_by_spell_id,
        ):
            for twin in level_map.values():
                if not twin.cleaned:
                    twin.cleanup()
            level_map.clear()
