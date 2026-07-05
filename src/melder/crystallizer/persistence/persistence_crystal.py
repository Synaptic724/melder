

import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional

from melder.crystallizer.persistence.persistence_profile import PersistenceProfile
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.general_base.cleanable import Cleanable


class PersistenceCrystal(Cleanable):
    """
    The crystallizer-owned persistence root: profiles of recorded worlds.

    Purpose:
        Own every PersistenceProfile in the process, following the same model
        Aether uses for AethericFrames: one guaranteed default child plus any
        number of named children, with one ACTIVE selection that operations
        route to. The "default" profile always exists and is the initial
        active profile; users may create additional profiles and default the
        system to them (creation activates the new profile unless told
        otherwise), so emissions always land on the currently active world.

    Contract:
        - "default" always exists; it can be cleared but never deleted.
        - Exactly one profile is ACTIVE at any moment; `record(...)` (the
          single sink entry the Crystallizer emit path calls) targets it.
        - Creating a profile activates it by default (`activate=False` opts
          out); deleting the active profile falls the selection back to
          "default".
        - Saving/hydrating profiles through cached items is deferred
          behavior (stubs below) landing with the bootstrap + persistence
          epics.

    Threading:
        One instance RLock serializes profile-registry mutation and active
        selection. Profile content operations serialize on each profile's
        own lock.

    Lifecycle:
        Owned by exactly one Crystallizer. `cleanup()` cleans every profile,
        then deletes owned fields (lock last); idempotent.
    """

    DEFAULT_PROFILE_NAME: str = "default"

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_profiles_by_name",
        "_active_profile_name",
        "_checkpoints_by_id",
    ]

    def __init__(self) -> None:
        """
        Initialize the persistence root with the guaranteed default profile.

        Contract:
            - The default profile exists immediately after construction and
              is the initial active profile; the crystallizer's emit path may
              record without any setup step.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._profiles_by_name: Dict[str, PersistenceProfile] = {
            PersistenceCrystal.DEFAULT_PROFILE_NAME: PersistenceProfile(
                PersistenceCrystal.DEFAULT_PROFILE_NAME
            ),
        }
        self._active_profile_name: str = PersistenceCrystal.DEFAULT_PROFILE_NAME
        self._checkpoints_by_id: Dict[str, Dict[str, object]] = {}

    def cleanup(self) -> None:
        """
        Clean every profile, then release owned fields (lock last).

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
            self._checkpoints_by_id.clear()
        del self._profiles_by_name
        del self._active_profile_name
        del self._checkpoints_by_id
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
                If the persistence crystal has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return self._profiles_by_name[PersistenceCrystal.DEFAULT_PROFILE_NAME]

    @property
    def active_profile(self) -> PersistenceProfile:
        """
        Return the currently active profile (the emission target).

        Returns:
            PersistenceProfile:
                The profile all `record(...)` calls currently route to.

        Raises:
            RuntimeError:
                If the persistence crystal has been cleaned.
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
                If the persistence crystal has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return self._active_profile_name

    def set_active_profile(self, profile_name: str) -> PersistenceProfile:
        """
        Switch the active emission target to one existing profile.

        Purpose:
            The Aether-style selection switch: after this call, every
            `record(...)` lands on the named profile until switched again.

        Args:
            profile_name:
                Name of an existing profile to activate.

        Returns:
            PersistenceProfile:
                The newly active profile.

        Raises:
            RuntimeError:
                If the persistence crystal has been cleaned.
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

        Purpose:
            The single sink entry for the Crystallizer emit path. Emissions
            follow the active selection ("default" unless the user created or
            switched to another profile).

        Args:
            twin:
                One twin from the persistence crystal family (SpellCrystal is
                the L3 spell node).

        Returns:
            None.

        Raises:
            RuntimeError:
                If the persistence crystal has been cleaned.
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
                If the persistence crystal has been cleaned.
            KeyError:
                If no profile exists under `profile_name`; the message names
                the known profiles so callers can self-correct.
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

        Purpose:
            The user-facing "new world" verb: create a profile and default
            the system to it, so subsequent emissions land there (owner
            model: users can create profiles and we default to the new one).

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
                If the persistence crystal has been cleaned.
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
            The generalized `clear_bootstrap`: clearing "default" resets the
            default bootstrap record; clearing a named profile empties that
            saved world without deleting its slot or changing the active
            selection.

        Args:
            profile_name:
                Name of an existing profile to clear.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the persistence crystal has been cleaned.
            KeyError:
                If no profile exists under `profile_name`.
        """
        self.check_cleaned()
        with self._lock:
            self._require_profile(profile_name).clear()

    def delete_profile(self, profile_name: str) -> None:
        """
        Delete one NAMED profile entirely.

        Contract:
            - "default" is never deletable (clear it instead); the guaranteed
              slot survives for the crystal's whole life.
            - Deleting the currently active profile falls the active
              selection back to "default".

        Args:
            profile_name:
                Name of the named profile to delete.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the persistence crystal has been cleaned.
            ValueError:
                If asked to delete the default profile.
            KeyError:
                If no profile exists under `profile_name`.
        """
        self.check_cleaned()
        if profile_name == PersistenceCrystal.DEFAULT_PROFILE_NAME:
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
                    PersistenceCrystal.DEFAULT_PROFILE_NAME
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
                If the persistence crystal has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return sorted(self._profiles_by_name.keys())

    def save_profile(self, profile_name: str) -> PersistenceProfile:
        """
        Seal the active profile into a named profile (saved world / kit).

        Args:
            profile_name:
                Name for the saved world.

        Returns:
            PersistenceProfile:
                The sealed named profile.

        Raises:
            NotImplementedError:
                Placeholder: the seal-copy (twin duplication + content
                addressing over stable identity) lands with the bootstrap
                epic's snapshot story.
        """
        self.check_cleaned()
        raise NotImplementedError(
            "save_profile is a placeholder; the seal-copy of the active "
            "profile (with content addressing) lands with the bootstrap epic."
        )

    def hydrate_profile(self, profile_name: str) -> None:
        """
        Hydrate one saved profile toward the live system (restore input).

        Args:
            profile_name:
                Name of the saved world to hydrate.

        Returns:
            None.

        Raises:
            NotImplementedError:
                Placeholder: hydration is the restore engine's entry seam
                (bootstrap epic); the CRUD adapter round-trip is the
                persistence epic's story.
        """
        self.check_cleaned()
        raise NotImplementedError(
            "hydrate_profile is a placeholder; the restore engine lands with "
            "the bootstrap epic (adapter round-trip: persistence epic)."
        )


    def create_checkpoint(
            self,
            profile_name: Optional[str] = None,
            description: Optional[str] = None,
    ) -> str:
        """
        Register one checkpoint of a profile and return its ULID identity.

        Purpose:
            Mint the time-ordered checkpoint identity (ULID: ids sort by
            creation time) and register the checkpoint's metadata record.

        Contract:
            - CURRENT DEPTH: metadata registration only. The record carries
              `"twin_custody": "pending"` because the twin seal-copy (content
              addressing over stable identity) lands with the bootstrap
              epic's snapshot story - callers must not treat this checkpoint
              as restorable yet.
            - `profile_name=None` targets the ACTIVE profile.

        Args:
            profile_name:
                Profile to checkpoint; None means the active profile.
            description:
                Optional caller note stored on the record.

        Returns:
            str:
                The new checkpoint's ULID id.

        Raises:
            RuntimeError:
                If the persistence crystal has been cleaned.
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
            checkpoint_id = IDBuilder.create_id()
            self._checkpoints_by_id[checkpoint_id] = {
                "checkpoint_id": checkpoint_id,
                "profile_name": resolved_name,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "description": description,
                "profile_summary": profile.describe(),
                "twin_custody": "pending",
            }
            return checkpoint_id

    def describe_checkpoint(self, checkpoint_id: str) -> Dict[str, object]:
        """
        Return a detached copy of one checkpoint's metadata record.

        Args:
            checkpoint_id:
                ULID identity returned by `create_checkpoint`.

        Returns:
            Dict[str, object]:
                Detached checkpoint record (id, profile, created_at,
                description, profile summary, custody status).

        Raises:
            RuntimeError:
                If the persistence crystal has been cleaned.
            KeyError:
                If no checkpoint exists under `checkpoint_id`; the message
                names the known ids so callers can self-correct.
        """
        self.check_cleaned()
        with self._lock:
            record = self._checkpoints_by_id.get(checkpoint_id)
            if record is None:
                raise KeyError(
                    "No checkpoint with id {0!r}. Known checkpoint ids: "
                    "{1}.".format(
                        checkpoint_id, sorted(self._checkpoints_by_id.keys())
                    )
                )
            return dict(record)

    def list_checkpoint_ids(self) -> List[str]:
        """
        Return all checkpoint ids in creation order.

        Contract:
            - Checkpoint ids are ULIDs, so lexicographic order IS creation
              order; the returned list is chronologically sorted.

        Returns:
            List[str]:
                Sorted (= chronological), detached checkpoint-id list.

        Raises:
            RuntimeError:
                If the persistence crystal has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return sorted(self._checkpoints_by_id.keys())

    def load_checkpoint(self, checkpoint_id: str) -> None:
        """
        Load one checkpoint back toward the live system (restore input).

        Args:
            checkpoint_id:
                ULID identity of the checkpoint to load.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the persistence crystal has been cleaned.
            KeyError:
                If no checkpoint exists under `checkpoint_id` (validated
                BEFORE the depth limit so callers get the right error).
            NotImplementedError:
                Placeholder: checkpoint loading is the restore engine's
                entry seam (bootstrap epic); the cache/save round-trip is
                the persistence epic's story.
        """
        self.check_cleaned()
        with self._lock:
            if checkpoint_id not in self._checkpoints_by_id:
                raise KeyError(
                    "No checkpoint with id {0!r}. Known checkpoint ids: "
                    "{1}.".format(
                        checkpoint_id, sorted(self._checkpoints_by_id.keys())
                    )
                )
        raise NotImplementedError(
            "load_checkpoint is a placeholder; the restore engine lands with "
            "the bootstrap epic (cache/save round-trip: persistence epic)."
        )

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
