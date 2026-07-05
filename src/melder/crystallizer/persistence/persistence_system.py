

import threading
from typing import Dict, List, Optional

from melder.crystallizer.persistence.crystallizer_cache import CrystallizerCache
from melder.crystallizer.persistence.persistence_crystal import PersistenceCrystal
from melder.crystallizer.persistence.crystals.spell_crystal import SpellCrystal
from melder.crystallizer.persistence.persistence_profile import PersistenceProfile
from melder.crystallizer.persistence.recorded_unit_state import RecordedUnitState
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class PersistenceSystem(Cleanable):
    """
    The crystallizer's persistence subsystem: profiles, checkpoints, cache.

    Purpose:
        House all persistence equipment in one concrete subsystem, following
        the Aether/frames ownership model: profiles (live recording surfaces;
        guaranteed "default" + named, ONE active selection that emissions
        route to) sit PARALLEL to the checkpoint ledger (N PersistenceCrystal
        snapshots, each capturing what happened in its profile since that
        profile's previous checkpoint), with the CrystallizerCache as the
        side item that will store/load checkpoint cached-items once the
        cached data structures are formed.

    Contract:
        - "default" always exists; it can be cleared but never deleted.
        - Exactly one profile is ACTIVE; `record(...)` (the sink entry the
          Crystallizer emit path calls) targets it; creating a profile
          activates it by default; deleting the active falls back to
          "default".
        - `create_checkpoint` performs REAL incremental capture: it seals the
          profile's journal segment since the last checkpoint into a new
          PersistenceCrystal (detached plain data), appends it to the
          ledger, and advances the profile's checkpoint mark.
        - `load_checkpoint` is a boot verb by design (restart-lane): live
          world collapse-and-rebuild is not the supported path.

    Threading:
        One instance RLock serializes registry mutation, active selection,
        and checkpoint sealing. Profiles serialize their own content ops.

    Lifecycle:
        Owned by exactly one Crystallizer. `cleanup()` cleans every profile,
        every ledger crystal, then the cache, then deletes owned fields
        (lock last); idempotent.
    """

    DEFAULT_PROFILE_NAME: str = "default"

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_profiles_by_name",
        "_active_profile_name",
        "_checkpoint_crystals_by_id",
        "_crystallizer_cache",
        "_max_persistence_crystals",
    ]

    def __init__(self) -> None:
        """
        Initialize the subsystem with the guaranteed default profile.

        Contract:
            - The default profile exists immediately and is the initial
              active profile; the emit path may record without setup.
            - The checkpoint ledger starts empty; the cache side item is
              constructed (placeholder depth).

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._profiles_by_name: Dict[str, PersistenceProfile] = {
            PersistenceSystem.DEFAULT_PROFILE_NAME: PersistenceProfile(
                PersistenceSystem.DEFAULT_PROFILE_NAME
            ),
        }
        self._active_profile_name: str = PersistenceSystem.DEFAULT_PROFILE_NAME
        self._checkpoint_crystals_by_id: Dict[str, PersistenceCrystal] = {}
        self._crystallizer_cache: CrystallizerCache = CrystallizerCache()
        # Retention cap for the checkpoint ledger; Crystallizer.activate()
        # overrides this from CrystallizerConfiguration.max_persistence_crystals.
        self._max_persistence_crystals: int = 100

    def cleanup(self) -> None:
        """
        Clean profiles, ledger crystals, then the cache (lock last).

        Contract:
            - Idempotent; del posture; lock deleted last.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            for profile in self._profiles_by_name.values():
                if not profile.cleaned:
                    profile.cleanup()
            self._profiles_by_name.clear()
            for crystal in self._checkpoint_crystals_by_id.values():
                if not crystal.cleaned:
                    crystal.cleanup()
            self._checkpoint_crystals_by_id.clear()
            if not self._crystallizer_cache.cleaned:
                self._crystallizer_cache.cleanup()
        del self._profiles_by_name
        del self._active_profile_name
        del self._checkpoint_crystals_by_id
        del self._crystallizer_cache
        del self._max_persistence_crystals
        del self._lock

    @property
    def default_profile(self) -> PersistenceProfile:
        """
        Return the guaranteed default profile.

        Returns:
            PersistenceProfile:
                The "default" profile (never absent while live).

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return self._profiles_by_name[PersistenceSystem.DEFAULT_PROFILE_NAME]

    @property
    def active_profile(self) -> PersistenceProfile:
        """
        Return the currently active profile (the emission target).

        Returns:
            PersistenceProfile:
                The profile all `record(...)` calls currently route to.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return self._profiles_by_name[self._active_profile_name]

    @property
    def active_profile_name(self) -> str:
        """
        Return the name of the currently active profile.

        Returns:
            str:
                Active profile name ("default" unless switched).

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return self._active_profile_name

    def set_active_profile(self, profile_name: str) -> PersistenceProfile:
        """
        Switch the active emission target to one existing profile.

        Args:
            profile_name:
                Name of an existing profile to activate.

        Returns:
            PersistenceProfile:
                The newly active profile.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
            KeyError:
                If no profile exists under `profile_name`.
        """
        self.check_cleaned()
        with self._lock:
            profile = self._require_profile(profile_name)
            self._active_profile_name = profile_name
            return profile

    def record(self, twin: Cleanable) -> None:
        """
        Record one emitted twin into the ACTIVE profile.

        Args:
            twin:
                One twin from the persistence crystal family (SpellCrystal is
                the L3 spell node).

        Returns:
            None.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
            TypeError:
                If the twin type is unsupported (raised by the profile).
        """
        self.check_cleaned()
        self.active_profile.record(twin)

    def record_spell_crystal(self, crystal: SpellCrystal, active: bool) -> None:
        """
        Record one custody crystal into the ACTIVE profile's locations.

        Args:
            crystal:
                The custody crystal to record.
            active:
                Active or inactive location.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
        """
        self.check_cleaned()
        self.active_profile.record_spell_crystal(crystal, active=active)

    def record_spell_activity(self, spell_id: str, active: bool) -> None:
        """
        Mirror one runtime park/promote flip into the ACTIVE profile.

        Args:
            spell_id:
                The spell whose activity flipped.
            active:
                True = promoted; False = parked.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
        """
        self.check_cleaned()
        self.active_profile.record_spell_activity(spell_id, active=active)

    def remove_spell_crystal(self, spell_id: str) -> None:
        """
        Evict one spell's custody from the ACTIVE profile.

        Args:
            spell_id:
                The removed spell's SHA256 identity.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
        """
        self.check_cleaned()
        self.active_profile.remove_spell_crystal(spell_id)

    def remove_spellbook_subtree(self, spellbook_id: str) -> None:
        """
        Evict one spellbook's record subtree from the ACTIVE profile.

        Args:
            spellbook_id:
                The dead spellbook's identity.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
        """
        self.check_cleaned()
        self.active_profile.remove_spellbook_subtree(spellbook_id)

    def remove_cluster_crystal(self, cluster_id: str) -> None:
        """
        Evict one deleted cluster's twin from the ACTIVE profile.

        Args:
            cluster_id:
                The deleted cluster's record-local ULID key.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
        """
        self.check_cleaned()
        self.active_profile.remove_cluster_crystal(cluster_id)

    def remove_contract_crystal(self, contract_id: str) -> None:
        """
        Evict one severed contract's twin from the ACTIVE profile.

        Args:
            contract_id:
                The severed contract's record-local ULID key.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
        """
        self.check_cleaned()
        self.active_profile.remove_contract_crystal(contract_id)

    def remove_spell_index_crystal(self, index_id: str) -> None:
        """
        Evict one destroyed index's twin from the ACTIVE profile.

        Args:
            index_id:
                The destroyed index's record-local ULID key.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
        """
        self.check_cleaned()
        self.active_profile.remove_spell_index_crystal(index_id)

    def remove_frame_crystal(self, frame_name: str) -> None:
        """
        Evict one dead frame's twin (+ leftover book subtrees) from the
        ACTIVE profile.

        Args:
            frame_name:
                The dead frame's canonical name.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
        """
        self.check_cleaned()
        self.active_profile.remove_frame_crystal(frame_name)

    def record_nexus_state(self, state: RecordedUnitState) -> None:
        """
        Flip the ACTIVE profile's recorded Nexus lifecycle switch.

        Args:
            state:
                The new recorded state.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
        """
        self.check_cleaned()
        self.active_profile.record_nexus_state(state)

    def record_mutation_research_state(self, state: RecordedUnitState) -> None:
        """
        Flip the ACTIVE profile's recorded MutationResearch switch.

        Args:
            state:
                The new recorded state.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
        """
        self.check_cleaned()
        self.active_profile.record_mutation_research_state(state)

    def get_spell_crystal(self, spell_id: str) -> SpellCrystal:
        """
        Return the ACTIVE profile's custody crystal for one spell.

        Args:
            spell_id:
                The spell's SHA256 identity.

        Returns:
            SpellCrystal:
                The currently recorded crystal.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
            KeyError:
                If the active profile records no crystal for `spell_id`.
        """
        self.check_cleaned()
        return self.active_profile.get_spell_crystal(spell_id)

    def get_profile(self, profile_name: str) -> PersistenceProfile:
        """
        Return one profile by name.

        Args:
            profile_name:
                Name of an existing profile.

        Returns:
            PersistenceProfile:
                The named profile.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
            KeyError:
                If no profile exists under `profile_name`.
        """
        self.check_cleaned()
        with self._lock:
            return self._require_profile(profile_name)

    def create_profile(
            self,
            profile_name: str,
            activate: bool = True,
    ) -> PersistenceProfile:
        """
        Create one new, empty named profile and (by default) activate it.

        Args:
            profile_name:
                New profile name; must not collide with an existing profile.
            activate:
                When True (default), the new profile becomes the active
                emission target immediately.

        Returns:
            PersistenceProfile:
                The newly created profile.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
            ValueError:
                If `profile_name` is empty or already exists.
        """
        self.check_cleaned()
        if not profile_name:
            raise ValueError("create_profile requires a non-empty profile_name.")
        with self._lock:
            if profile_name in self._profiles_by_name:
                raise ValueError(
                    "Persistence profile {0!r} already exists; profile names "
                    "are unique. Use get_profile, set_active_profile, or "
                    "clear_profile instead.".format(profile_name)
                )
            profile = PersistenceProfile(profile_name)
            self._profiles_by_name[profile_name] = profile
            if activate:
                self._active_profile_name = profile_name
            return profile

    def clear_profile(self, profile_name: str) -> None:
        """
        Reset one profile's recorded content to empty.

        Purpose:
            The generalized clear_bootstrap. Also resets the profile's
            checkpoint mark (its next checkpoint captures from zero); ledger
            crystals already sealed from it remain in the ledger untouched.

        Args:
            profile_name:
                Name of an existing profile to clear.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
            KeyError:
                If no profile exists under `profile_name`.
        """
        self.check_cleaned()
        with self._lock:
            self._require_profile(profile_name).clear()

    def delete_profile(self, profile_name: str) -> None:
        """
        Delete one NAMED profile ("default" is never deletable).

        Contract:
            - Deleting the active profile falls the selection back to
              "default".
            - Ledger crystals sealed from the deleted profile remain in the
              ledger (history survives its source).

        Args:
            profile_name:
                Name of the named profile to delete.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
            ValueError:
                If asked to delete the default profile.
            KeyError:
                If no profile exists under `profile_name`.
        """
        self.check_cleaned()
        if profile_name == PersistenceSystem.DEFAULT_PROFILE_NAME:
            raise ValueError(
                "The default profile is the guaranteed slot and cannot be "
                "deleted; use clear_profile('default') to reset it."
            )
        with self._lock:
            profile = self._profiles_by_name.pop(profile_name, None)
            if profile is None:
                raise KeyError(
                    "No persistence profile named {0!r}. Known profiles: "
                    "{1}.".format(
                        profile_name, sorted(self._profiles_by_name.keys())
                    )
                )
            if self._active_profile_name == profile_name:
                self._active_profile_name = (
                    PersistenceSystem.DEFAULT_PROFILE_NAME
                )
            profile.cleanup()

    def list_profile_names(self) -> List[str]:
        """
        Return the names of all live profiles.

        Returns:
            List[str]:
                Sorted, detached profile-name list.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return sorted(self._profiles_by_name.keys())

    def flush_checkpoint_to_cache(self, checkpoint_id: Optional[str] = None) -> List[str]:
        """
        Flush sealed checkpoint(s) into the local crystallizer cache.

        Purpose:
            The seal-then-ship lane: a ledger crystal's cached-item form
            lands on disk so history survives the process (reload via
            `reload_checkpoint_from_cache`; full world restore stays the
            bootstrap epic's engine).

        Args:
            checkpoint_id:
                One ledger ULID, or None to flush EVERY ledger crystal.

        Returns:
            List[str]:
                The flushed checkpoint ids.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
            KeyError:
                If `checkpoint_id` names no ledger crystal.
        """
        self.check_cleaned()
        with self._lock:
            if checkpoint_id is not None:
                targets = [self._require_checkpoint(checkpoint_id)]
            else:
                targets = list(self._checkpoint_crystals_by_id.values())
            flushed: List[str] = []
            for crystal in targets:
                self._crystallizer_cache.store_cached_item(
                    crystal.id, crystal.to_cached_item()
                )
                flushed.append(crystal.id)
            return flushed

    def reload_checkpoint_from_cache(self, checkpoint_id: str) -> Dict[str, object]:
        """
        Reload one cached checkpoint back into the ledger.

        Purpose:
            History recovery: rebuild the sealed artifact from its cached
            item (e.g. after a fresh boot) so describe/list see it again.

        Contract:
            - Insert-if-absent: an id already in the ledger keeps its live
              crystal (the cache never overwrites live history).
            - Retention dropout does NOT run here - reloading old history
              must not evict newer crystals; the cap applies to new seals.

        Args:
            checkpoint_id:
                ULID of a previously flushed checkpoint.

        Returns:
            Dict[str, object]:
                The (re)loaded crystal's describe() summary.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
            KeyError:
                If no cached item exists for `checkpoint_id`.
        """
        self.check_cleaned()
        with self._lock:
            existing = self._checkpoint_crystals_by_id.get(checkpoint_id)
            if existing is not None:
                return existing.describe()
            cached_item = self._crystallizer_cache.load_cached_item(
                checkpoint_id
            )
            crystal = PersistenceCrystal.from_cached_item(cached_item)
            self._checkpoint_crystals_by_id[crystal.id] = crystal
            return crystal.describe()

    def list_cached_checkpoint_ids(self) -> List[str]:
        """
        Return every checkpoint id present in the local cache.

        Returns:
            List[str]:
                Sorted cached checkpoint ids (empty when nothing flushed).

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return self._crystallizer_cache.list_cached_item_ids()

    def set_checkpoint_retention(self, max_crystals: int) -> None:
        """
        Install the checkpoint-ledger retention cap.

        Purpose:
            Configuration hand-off point: Crystallizer.activate() pushes
            the frozen `max_persistence_crystals` knob down here so the
            ledger enforces it at every seal.

        Args:
            max_crystals:
                Positive maximum ledger size.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
            ValueError:
                If `max_crystals` is a bool, not an int, or not positive.
        """
        self.check_cleaned()
        if (
                isinstance(max_crystals, bool)
                or not isinstance(max_crystals, int)
                or max_crystals <= 0
        ):
            raise ValueError(
                "set_checkpoint_retention requires a positive int "
                "(got {0!r}).".format(max_crystals)
            )
        with self._lock:
            self._max_persistence_crystals = max_crystals

    def create_checkpoint(
            self,
            profile_name: Optional[str] = None,
            description: Optional[str] = None,
    ) -> str:
        """
        Seal one profile's incremental segment into a new PersistenceCrystal.

        Purpose:
            The checkpoint mechanic: capture everything journaled in the
            profile since its previous checkpoint (detached plain data),
            mint the time-ordered ULID identity, append the crystal to the
            ledger, and advance the profile's checkpoint mark.

        Contract:
            - Incremental: the first checkpoint of a profile captures its
              whole record; each later one captures the delta window.
            - An empty window still seals (a marker checkpoint recording
              that nothing changed); the window bounds say so honestly.

        Args:
            profile_name:
                Profile to checkpoint; None means the active profile.
            description:
                Optional caller note stored on the crystal.

        Returns:
            str:
                The new checkpoint's ULID id.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
            KeyError:
                If `profile_name` names no existing profile.
        """
        self.check_cleaned()
        with self._lock:
            resolved_name = (
                profile_name
                if profile_name is not None
                else self._active_profile_name
            )
            profile = self._require_profile(resolved_name)
            mark = profile.last_checkpoint_sequence
            payloads, entries, sequence_range = (
                profile.capture_segment_since(mark)
            )
            crystal = PersistenceCrystal(
                checkpoint_id=IDBuilder.create_id(),
                profile_name=resolved_name,
                checkpoint_number=self._next_checkpoint_number(resolved_name),
                description=description,
                journal_segment=entries,
                captured_payloads=payloads,
                sequence_range=sequence_range,
            )
            self._checkpoint_crystals_by_id[crystal.id] = crystal
            profile.mark_checkpoint(sequence_range[1])
            # FIFO dropout: dict insertion order IS creation order (exact
            # even when several crystals mint within one millisecond, where
            # ULID randomness is not lexicographically ordered); the ledger
            # stays a rolling most-recent window.
            while (
                    len(self._checkpoint_crystals_by_id)
                    > self._max_persistence_crystals
            ):
                oldest_id = next(iter(self._checkpoint_crystals_by_id))
                oldest = self._checkpoint_crystals_by_id.pop(oldest_id)
                if not oldest.cleaned:
                    oldest.cleanup()
            return crystal.id

    def describe_checkpoint(self, checkpoint_id: str) -> Dict[str, object]:
        """
        Return one ledger crystal's detached metadata summary.

        Args:
            checkpoint_id:
                ULID identity returned by `create_checkpoint`.

        Returns:
            Dict[str, object]:
                Checkpoint metadata (time, checkpoint number, window,
                capture counts, custody status).

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
            KeyError:
                If no checkpoint exists under `checkpoint_id`.
        """
        self.check_cleaned()
        with self._lock:
            return self._require_checkpoint(checkpoint_id).describe()

    def describe(self) -> Dict[str, object]:
        """
        Return the whole record's one-shot operational summary.

        Returns:
            Dict[str, object]:
                Active profile name, all profile names, per-profile twin
                counts (each profile's describe), ledger size, and the
                cached checkpoint count on disk.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "active_profile_name": self._active_profile_name,
                "profile_names": sorted(self._profiles_by_name.keys()),
                "profiles": {
                    name: profile.describe()
                    for name, profile in self._profiles_by_name.items()
                },
                "ledger_checkpoint_count": len(
                    self._checkpoint_crystals_by_id
                ),
                "cached_checkpoint_count": len(
                    self._crystallizer_cache.list_cached_item_ids()
                ),
            }

    def checkpoint_replay_data(self, checkpoint_id: str) -> Dict[str, object]:
        """
        Return one ledger checkpoint's detached replay inputs.

        Args:
            checkpoint_id:
                ULID identity returned by `create_checkpoint`.

        Returns:
            Dict[str, object]:
                {"journal": ordered window entries, "payloads": captured
                final states by kind and key} - fully detached.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
            KeyError:
                If no checkpoint exists under `checkpoint_id`.
        """
        self.check_cleaned()
        with self._lock:
            return self._require_checkpoint(checkpoint_id).replay_data()

    def list_checkpoint_ids(self) -> List[str]:
        """
        Return all ledger checkpoint ids in creation order.

        Contract:
            - Insertion order IS creation order (exact even for crystals
              minted within one millisecond, where ULID randomness is not
              lexicographically ordered); ULIDs remain time-sortable across
              millisecond boundaries.

        Returns:
            List[str]:
                Creation-ordered, detached checkpoint-id list.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._checkpoint_crystals_by_id.keys())

    def load_checkpoint(self, checkpoint_id: str) -> None:
        """
        Load one checkpoint back toward the live system (boot verb).

        Contract:
            - Restart-lane by design: intended for unfolding a world at
              fresh boot, not for mutating a running system.

        Args:
            checkpoint_id:
                ULID identity of the checkpoint to load.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
            KeyError:
                If no checkpoint exists under `checkpoint_id` (validated
                BEFORE the depth limit so callers get the right error).
            NotImplementedError:
                Placeholder until the restore engine lands (bootstrap epic;
                cache round-trip: persistence epic).
        """
        self.check_cleaned()
        with self._lock:
            self._require_checkpoint(checkpoint_id)
        raise NotImplementedError(
            "load_checkpoint is a placeholder; the restore engine lands with "
            "the bootstrap epic (cache round-trip: persistence epic)."
        )

    def _next_checkpoint_number(self, profile_name: str) -> int:
        """
        Return the next 1-based checkpoint number for one profile.

        Contract:
            - Caller holds `self._lock`.

        Args:
            profile_name:
                Profile whose chain position is being computed.

        Returns:
            int:
                1 + count of ledger crystals sealed from that profile.
        """
        existing = sum(
            1
            for crystal in self._checkpoint_crystals_by_id.values()
            if not crystal.cleaned and crystal.profile_name == profile_name
        )
        return existing + 1

    def _require_profile(self, profile_name: str) -> PersistenceProfile:
        """
        Return one profile or raise the standard self-correcting KeyError.

        Contract:
            - Caller holds `self._lock`.

        Args:
            profile_name:
                Profile name to resolve.

        Returns:
            PersistenceProfile:
                The resolved profile.

        Raises:
            KeyError:
                If no profile exists under `profile_name`.
        """
        profile = self._profiles_by_name.get(profile_name)
        if profile is None:
            raise KeyError(
                "No persistence profile named {0!r}. Known profiles: "
                "{1}.".format(
                    profile_name, sorted(self._profiles_by_name.keys())
                )
            )
        return profile

    def _require_checkpoint(self, checkpoint_id: str) -> PersistenceCrystal:
        """
        Return one ledger crystal or raise the self-correcting KeyError.

        Contract:
            - Caller holds `self._lock`.

        Args:
            checkpoint_id:
                Checkpoint id to resolve.

        Returns:
            PersistenceCrystal:
                The resolved ledger crystal.

        Raises:
            KeyError:
                If no checkpoint exists under `checkpoint_id`.
        """
        crystal = self._checkpoint_crystals_by_id.get(checkpoint_id)
        if crystal is None:
            raise KeyError(
                "No checkpoint with id {0!r}. Known checkpoint ids: "
                "{1}.".format(
                    checkpoint_id, sorted(self._checkpoint_crystals_by_id.keys())
                )
            )
        return crystal
