

import threading
from typing import Dict, List, Optional, Tuple

from melder.crystallizer.persistence.crystals.aether_crystal import AetherCrystal
from melder.crystallizer.persistence.crystals.aetheric_frame_crystal import AethericFrameCrystal
from melder.crystallizer.persistence.crystals.conduit_crystal import ConduitCrystal
from melder.crystallizer.persistence.crystals.mutation_research_crystal import MutationResearchCrystal
from melder.crystallizer.persistence.crystals.nexus_crystal import NexusCrystal
from melder.crystallizer.persistence.crystals.spell_crystal import SpellCrystal
from melder.crystallizer.persistence.crystals.spellbook_crystal import SpellbookCrystal
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
        - Replace-on-emit: recording a twin REPLACES the prior twin for that
          identity wholesale (the replaced twin is cleaned); twins are never
          mutated in place, so readers can hold a twin without torn state.
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

    Lifecycle:
        Owned by exactly one PersistenceCrystal. `cleanup()` cleans every
        held twin, then deletes owned fields (lock last); idempotent.
    """

    __slots__ = Cleanable.__slots__ + [
        "_profile_name",
        "_lock",
        "_emission_sequence",
        "_emission_log",
        "_last_checkpoint_sequence",
        "_aether_crystal",
        "_nexus_crystal",
        "_mutation_research_crystal",
        "_frame_crystals_by_name",
        "_spellbook_crystals_by_id",
        "_conduit_crystals_by_id",
        "_spell_crystals_by_spell_id",
    ]

    def __init__(self, profile_name: str) -> None:
        """
        Initialize one empty profile store.

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
        self._nexus_crystal: Optional[NexusCrystal] = None
        self._mutation_research_crystal: Optional[MutationResearchCrystal] = None
        self._frame_crystals_by_name: Dict[str, AethericFrameCrystal] = {}
        self._spellbook_crystals_by_id: Dict[str, SpellbookCrystal] = {}
        self._conduit_crystals_by_id: Dict[str, ConduitCrystal] = {}
        self._spell_crystals_by_spell_id: Dict[str, SpellCrystal] = {}

    def cleanup(self) -> None:
        """
        Clean every held twin, then release owned fields (lock last).

        Contract:
            - Idempotent; del posture; lock deleted last.
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
        del self._nexus_crystal
        del self._mutation_research_crystal
        del self._frame_crystals_by_name
        del self._spellbook_crystals_by_id
        del self._conduit_crystals_by_id
        del self._spell_crystals_by_spell_id
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
            elif isinstance(twin, SpellCrystal):
                self._replace_mapped(
                    self._spell_crystals_by_spell_id, twin.id, twin, "spell_crystal"
                )
            else:
                raise TypeError(
                    "PersistenceProfile.record received an unsupported twin "
                    "type: {0}. Supported: the persistence crystal family "
                    "(SpellCrystal is the L3 spell node).".format(
                        type(twin).__name__
                    )
                )

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
                "frame_count": len(self._frame_crystals_by_name),
                "spellbook_count": len(self._spellbook_crystals_by_id),
                "conduit_count": len(self._conduit_crystals_by_id),
                "spell_crystal_count": len(self._spell_crystals_by_spell_id),
            }

    def compose_frame_subtree(self, frame_name: str) -> Dict[str, object]:
        """
        Compose the tree view of one frame subtree (frame -> spellbooks ->
        spell crystals / conduits) from the flat maps.

        Args:
            frame_name:
                Canonical frame name to compose.

        Returns:
            Dict[str, object]:
                Composed subtree payload (restore-engine input shape).

        Raises:
            NotImplementedError:
                Placeholder: composition lands with the restore-engine story.
        """
        self.check_cleaned()
        raise NotImplementedError(
            "compose_frame_subtree is a placeholder; the tree-view composer "
            "lands with the restore-engine story (bootstrap epic)."
        )

    def compose_conduit_subtree(self, conduit_id: str) -> Dict[str, object]:
        """
        Compose the tree view of one conduit subtree (conduit + its
        spellbook's spell crystals) from the flat maps.

        Args:
            conduit_id:
                Conduit identity to compose.

        Returns:
            Dict[str, object]:
                Composed subtree payload (restore-engine input shape).

        Raises:
            NotImplementedError:
                Placeholder: composition lands with the restore-engine story.
        """
        self.check_cleaned()
        raise NotImplementedError(
            "compose_conduit_subtree is a placeholder; the tree-view composer "
            "lands with the restore-engine story (bootstrap epic)."
        )

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
                twin = self._resolve_twin(kind, key)
                if twin is None or twin.cleaned:
                    continue
                payloads.setdefault(kind, {})[key] = twin.describe()
            return (
                payloads,
                segment_entries,
                (sequence_mark + 1, self._emission_sequence),
            )

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
        if kind == "spell_crystal":
            return self._spell_crystals_by_spell_id.get(key)
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
                self._spell_crystals_by_spell_id,
        ):
            for twin in level_map.values():
                if not twin.cleaned:
                    twin.cleanup()
            level_map.clear()
