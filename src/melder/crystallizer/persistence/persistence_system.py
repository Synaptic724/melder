

import threading
from typing import Dict, List, Optional

from melder.crystallizer.persistence.crystallizer_cache import CrystallizerCache
from melder.crystallizer.persistence.persistence_crystal import PersistenceCrystal
from melder.crystallizer.persistence.persistence_profile import PersistenceProfile
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

    def list_checkpoint_ids(self) -> List[str]:
        """
        Return all ledger checkpoint ids in creation order.

        Contract:
            - Checkpoint ids are ULIDs, so lexicographic order IS creation
              order; the returned list is chronologically sorted.

        Returns:
            List[str]:
                Sorted (= chronological), detached checkpoint-id list.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return sorted(self._checkpoint_crystals_by_id.keys())

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
