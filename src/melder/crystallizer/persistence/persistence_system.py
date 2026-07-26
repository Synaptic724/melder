

import threading
from typing import Dict, List, Optional

from melder.crystallizer.persistence.persistence_crystal import PersistenceCrystal
from melder.crystallizer.crystals.spell_crystal import SpellCrystal
from melder.crystallizer.persistence.persistence_profile import PersistenceProfile
from melder.crystallizer.crystals.recorded_unit_state import RecordedUnitState
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class PersistenceSystem(Cleanable):
    """
    The crystallizer's RECORD: profiles and the checkpoint ledger.

    Purpose:
        The boring ledger (V3 ledger law): profiles (live recording
        surfaces; guaranteed "default" + named, ONE active selection that
        emissions route to) sit PARALLEL to the checkpoint ledger (N
        PersistenceCrystal snapshots, each capturing what happened in its
        profile since that profile's previous checkpoint). The ledger owns
        IN-PROCESS truth only - disk and DB custody (cache files, formation
        files, the ExternalPersistenceManager seam) live in
        AssetManagementSystem, which reads feedstock from this record and
        feeds reloads back through its insert sink.

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
        - The record never executes a load or constructs a restore engine.
          It detaches value-only checkpoint chains for the loader, whose
          admission pipeline owns folded preflight and runtime replay.

    Threading:
        One instance RLock serializes registry mutation, active selection,
        and checkpoint sealing. Profiles serialize their own content ops.

    Lifecycle / Cleanup:
        Owned by exactly one `Crystallizer`. Borrowing subsystems are cleaned
        first by that root. This record then cleans every profile, followed by
        every ledger crystal, and deletes its lock last. It never cleans the
        asset or loader systems that borrowed it.

    Registration:
        MELDER KERNEL - guarded (internal manifest). The record ledger
        `Crystallizer` constructs and owns; users talk to `Crystallizer` facades only
        and never hold or bind this object. access=internal.

    Subsystem Context:
        THE RECORD - one of the three same-rank children `Crystallizer` owns
        (`PersistenceSystem` the record, `AssetManagementSystem` the bytes-at-rest,
        `CrystalLoaderSystem` the unfold). It owns the named profiles plus the checkpoint
        ledger and is the insert sink; `AssetManagementSystem` reads its feedstock and
        feeds cache/remote reloads back through that sink. EDGE LAW: the record calls
        nobody and constructs no engines - borrowers clean before it.

    System Context:
        Crystallizer layer of the boot order (Aether|AetherUtilitySystem -> Crystallizer
        -> MutationResearch -> Nexus -> AethericFrame -> Spellbook -> Conduit|Ward).
        Passive and in-process only: structural units PUSH twins into the Crystallizer
        emit path, which routes to `record(...)` on the active profile; a crystallizer-off
        world stays byte-identical (the R-A covenant). It holds plain values only
        (callables appear as presence flags), so the ledger can be cached and restored
        without live references.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. The crystallizer's RECORD: profiles and the checkpoint ledger. Melder
        kernel machinery: read it to understand the runtime, do not drive it directly.
    """

    DEFAULT_PROFILE_NAME: str = "default"

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_profiles_by_name",
        "_active_profile_name",
        "_checkpoint_crystals_by_id",
        "_max_persistence_crystals",
    ]

    def __init__(self) -> None:
        """
        Initialize the subsystem with the guaranteed default profile.

        Contract:
            - The default profile exists immediately and is the initial
              active profile; the emit path may record without setup.
            - The checkpoint ledger starts empty. Disk custody (the
              crystallizer cache) is AssetManagementSystem's, not the
              record's (S1-S3 decomposition).

        Returns:
            None.

        Threading:
            Construction is single-threaded; the instance lock guards all
            later registry, selection, and sealing operations.

        Lifecycle / Cleanup:
            The default profile and all future ledger crystals are owned by
            this system. The cache and external mesh are not constructed here.
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
        # Retention cap for the checkpoint ledger; Crystallizer.activate()
        # overrides this from CrystallizerConfiguration.max_persistence_crystals.
        # The asset system reads it live (max_persistence_crystals property)
        # so cache-file retention follows the same cap.
        self._max_persistence_crystals: int = 100

    def cleanup(self) -> None:
        """
        Clean profiles, then ledger crystals (lock last).

        Contract:
            - Idempotent and terminal; later record reads and writes reject.
            - Cleans all profile-owned twins before cleaning sealed ledger
              crystals, then deletes registry fields and the lock.
            - Does not touch cache files, formation files, remote storage, or
              either subsystem that borrowed this record.

        Threading:
            Serialized by the record lock. Borrowers must already be quiescent
            under the root's cleanup order.

        Lifecycle / Cleanup:
            Called by `Crystallizer.cleanup()` after loader and asset teardown.

        Returns:
            None.
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
        del self._profiles_by_name
        del self._active_profile_name
        del self._checkpoint_crystals_by_id
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

    def record(self, twin: Cleanable, profile_name: Optional[str] = None) -> None:
        """
        Record one emitted twin into a profile (the active profile by default).

        Args:
            twin:
                One twin from the persistence crystal family (SpellCrystal is
                the L3 spell node).
            profile_name:
                Target profile; None routes to the active profile. A named
                target lets a profile-scoped seal record its own policy twin
                into that profile instead of leaking it into the active one
                (BUG-158).

        Returns:
            None.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
            KeyError:
                If `profile_name` names no existing profile.
            TypeError:
                If the twin type is unsupported (raised by the profile).
        """
        self.check_cleaned()
        with self._lock:
            profile = (
                self._require_profile(profile_name)
                if profile_name is not None
                else self._profiles_by_name[self._active_profile_name]
            )
        profile.record(twin)

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

    def describe_mutation_research_record(self) -> Optional[Dict[str, object]]:
        """
        Return the ACTIVE profile's recorded MutationResearch twin payload.

        Returns:
            Optional[Dict[str, object]]:
                The recorded twin's `describe()` payload, or None when the
                active profile has never recorded the MR twin.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
        """
        self.check_cleaned()
        return self.active_profile.describe_mutation_research_record()

    def describe_spell_crystals(self) -> Dict[str, Dict[str, object]]:
        """
        Return the ACTIVE profile's custody surface as detached payloads.

        Purpose:
            The impact-engine read seam (S3): active-profile passthrough
            to `PersistenceProfile.describe_spell_crystals`.

        Returns:
            Dict[str, Dict[str, object]]:
                spell_id -> crystal describe() payload + "custody_state".

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
        """
        self.check_cleaned()
        return self.active_profile.describe_spell_crystals()

    def capture_index_graft(self, index_id: str) -> Dict[str, object]:
        """
        Capture one index's graft record from the ACTIVE profile.

        Args:
            index_id:
                The recorded index identity.

        Returns:
            Dict[str, object]: The versioned graft record (see
            PersistenceProfile.capture_index_graft).

        Raises:
            RuntimeError: If the subsystem has been cleaned.
            KeyError: If no index twin is recorded under `index_id`.
        """
        self.check_cleaned()
        return self.active_profile.capture_index_graft(index_id)

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

    # NOTE (S3 decomposition): the cache lanes (flush_checkpoint_to_cache,
    # reload_checkpoint_from_cache, list_cached_checkpoint_ids,
    # reload_profile_from_cache) moved to AssetManagementSystem - the record
    # now exposes FEEDSTOCK (cached_item_form/forms) and the INSERT SINK
    # (insert_cached_items) and never touches disk itself.

    def cached_item_forms(
            self,
            checkpoint_id: Optional[str] = None,
    ) -> List[Dict[str, object]]:
        """
        Return cached-item forms for one or every ledger crystal.

        Purpose:
            Flush feedstock for the asset system: each payload already
            carries `checkpoint_id` and `profile_name`, so the shipping
            side needs exactly one pull per flush (cache write AND remote
            upload reuse the same payloads).

        Args:
            checkpoint_id:
                One ledger ULID, or None for EVERY ledger crystal.

        Returns:
            List[Dict[str, object]]:
                Detached to_cached_item payloads.

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
            return [crystal.to_cached_item() for crystal in targets]

    @property
    def max_persistence_crystals(self) -> int:
        """
        Return the live checkpoint-retention cap.

        Purpose:
            The asset system reads this per flush so cache-file FIFO
            retention follows the SAME cap as the ledger (owner ruling:
            without a DB emitter the cache follows the checkpoint limit;
            durability beyond it is the user's DB opt-in - "its on them").

        Returns:
            int: The current retention cap.

        Raises:
            RuntimeError: If the subsystem has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return self._max_persistence_crystals

    def capture_formation_record(
            self,
            formation_name: str,
            conduit_id: Optional[str] = None,
            frame_name: Optional[str] = None,
            profile_name: Optional[str] = None,
            description: str = "",
    ) -> Dict[str, object]:
        """
        Capture one user-named formation RECORD (owner feature; record
        side of the old save_formation - storage moved to the assets).

        Purpose:
            "If they like a conduit formation... just reload that
            conduit": capture the LIVE slice (conduit scope includes its
            spellbook; frame scope includes the frame subtree) from the
            targeted profile and assemble the storable record. The asset
            system persists it (`AssetManagementSystem.store_formation`).

        Args:
            formation_name:
                The user's name for this formation (filesystem-safe).
            conduit_id:
                Conduit-scope anchor (exactly one scope required).
            frame_name:
                Frame-scope anchor.
            profile_name:
                Profile to capture from; None means the active profile.
            description:
                Optional user note stored on the formation record.

        Returns:
            Dict[str, object]: The assembled formation record.

        Raises:
            RuntimeError: If the subsystem has been cleaned.
            ValueError: If the scope arguments are wrong.
            KeyError: If the profile or the anchor twin does not exist.
        """
        self.check_cleaned()
        with self._lock:
            resolved_name = (
                profile_name
                if profile_name is not None
                else self._active_profile_name
            )
            if resolved_name not in self._profiles_by_name:
                raise KeyError(
                    "No profile named {0!r}.".format(resolved_name)
                )
            payloads = self._profiles_by_name[
                resolved_name
            ].capture_formation_slice(
                conduit_id=conduit_id, frame_name=frame_name
            )
        # Record versioning (owner ruling 2026-07-12): every durable
        # artifact carries the schema stamp; readers gate on the major.
        from melder.crystallizer.persistence.record_version import (
            RecordVersion,
        )

        return RecordVersion.stamp({
            "formation_name": formation_name,
            "profile_name": resolved_name,
            "scope": (
                {"conduit_id": conduit_id}
                if conduit_id is not None
                else {"frame_name": frame_name}
            ),
            "created_at": IDBuilder.create_id(),
            "description": description,
            "payloads": payloads,
        })

    # NOTE (S3 decomposition): load_formation_record and list_formations
    # moved to AssetManagementSystem (formation FILES are bytes at rest);
    # the engine leg below consumes a record the asset system loaded.

    # NOTE (S4 decomposition): restore_formation_record (the formation
    # engine leg, incl. the canonical-kind-order synthetic window minting)
    # moved to LoadAdmission.plan_formation_load (formerly BootMediator;
    # renamed 2026-07-11) + CrystalLoaderSystem.
    # The ledger captures formation records; it never replays them.

    def cached_item_form(self, checkpoint_id: str) -> Dict[str, object]:
        """
        Return one ledger crystal's cached-item form (upload feedstock).

        Purpose:
            The ExternalPersistenceManager (the crystallizer's sibling-
            rank remote transport) uploads cached-item payloads; this
            verb hands them out without exposing the ledger.

        Args:
            checkpoint_id:
                One ledger ULID.

        Returns:
            Dict[str, object]:
                The crystal's to_cached_item payload (detached).

        Raises:
            RuntimeError: If the subsystem has been cleaned.
            KeyError: If `checkpoint_id` names no ledger crystal.
        """
        self.check_cleaned()
        with self._lock:
            return self._require_checkpoint(checkpoint_id).to_cached_item()

    def insert_cached_items(
            self,
            cached_items: List[Dict[str, object]],
    ) -> Dict[str, object]:
        """
        Insert cached-item payloads into the ledger (insert-if-absent).

        Purpose:
            The generic import sink: downloads from the external manager
            (or any cached-item source) land here with the same reload
            semantics as the cache lanes.

        Contract:
            - Insert-if-absent per item; re-running is idempotent.
            - Retention dropout does NOT run here (importing history must
              not evict newer crystals).

        Args:
            cached_items:
                JSON-safe to_cached_item payloads, any order.

        Returns:
            Dict[str, object]:
                {"inserted": [ids], "skipped_existing": [ids]}.

        Raises:
            RuntimeError: If the subsystem has been cleaned.
            KeyError/ValueError: If an item violates the crystal codec.
        """
        self.check_cleaned()
        inserted: List[str] = []
        skipped_existing: List[str] = []
        with self._lock:
            for cached_item in cached_items:
                checkpoint_id = str(cached_item["checkpoint_id"])
                if checkpoint_id in self._checkpoint_crystals_by_id:
                    skipped_existing.append(checkpoint_id)
                    continue
                crystal = PersistenceCrystal.from_cached_item(cached_item)
                self._checkpoint_crystals_by_id[crystal.id] = crystal
                inserted.append(crystal.id)
        return {"inserted": inserted, "skipped_existing": skipped_existing}

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
                counts (each profile's describe), and ledger size. Disk
                truth (cached checkpoint count) is the asset system's;
                the Crystallizer facade enriches its record description
                with it so the facade payload stays complete.

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

    # NOTE (S4 decomposition): load_checkpoint's engine seat moved to
    # CrystalLoaderSystem (crystal_loader_system/) - the ledger now hands
    # out the DETACHED chain below and never constructs engines.

    def detach_profile_chain(self, checkpoint_id: str) -> Dict[str, object]:
        """
        Assemble one checkpoint's detached profile chain (loader feedstock).

        Purpose:
            Resolve the target's profile chain - every ledger crystal
            sealed from the same profile up to and including the target,
            in creation order - fully DETACHED under the subsystem lock so
            the loader's engine can run OUTSIDE it (replay re-enters the
            emit path, which must be free to record the rebuilt world).

        Args:
            checkpoint_id:
                ULID identity of the target checkpoint.

        Returns:
            Dict[str, object]:
                {"profile_name": str, "checkpoint_ids": [ULIDs in
                creation order], "chain": [detached replay_data windows]}.

        Raises:
            RuntimeError:
                If the subsystem has been cleaned.
            KeyError:
                If no checkpoint exists under `checkpoint_id`.
        """
        self.check_cleaned()
        with self._lock:
            target = self._require_checkpoint(checkpoint_id)
            profile_name = target.profile_name
            chain_crystals = [
                crystal
                for crystal in self._checkpoint_crystals_by_id.values()
                if (
                    not crystal.cleaned
                    and crystal.profile_name == profile_name
                    and crystal.checkpoint_number <= target.checkpoint_number
                )
            ]
            chain_crystals.sort(key=lambda crystal: crystal.checkpoint_number)
            return {
                "profile_name": profile_name,
                "checkpoint_ids": [
                    crystal.id for crystal in chain_crystals
                ],
                "chain": [
                    crystal.replay_data() for crystal in chain_crystals
                ],
            }

    def verify_checkpoint_chain(
            self,
            profile_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Report one profile's checkpoint-chain fold-safety (read-only).

        Purpose:
            The chain-integrity verb: before anyone folds a chain (the
            restore engine trusts its shape), answer whether the retained
            ledger run is contiguous - in checkpoint numbers AND in journal
            windows - how much prefix history retention dropped, and whether
            the run can still be folded back to the true world (restorable).

        Contract:
            - Read-only: never mutates the ledger or any profile.
            - Verdicts: "intact" (contiguous from checkpoint 1 with the
              baseline retained), "truncated_prefix" (contiguous run whose
              head was dropped by retention), "broken" (number gap, duplicate
              number, or non-contiguous windows). An empty ledger run reports
              "empty".
            - Restorability (BUG-159): only an "intact" chain is `restorable`.
              Once retention drops the prefix, the evicted baseline may have
              carried live state that no surviving incremental supersedes, and
              this read-only verb cannot prove otherwise from structure alone;
              folding a truncated/broken/empty chain is NOT guaranteed to
              reconstruct the true world, so `restorable` is False. Callers
              must gate any fold on `restorable`, never on structural
              contiguity alone.
            - Empty seal windows (first == last + 1) are legal markers and
              never break the verdict; they are listed for visibility.

        Args:
            profile_name:
                Profile to audit; None means the active profile.

        Returns:
            Dict[str, object]:
                {"profile_name", "ledger_count", "first_checkpoint_number",
                 "last_checkpoint_number", "dropped_prefix_count",
                 "breaks": [evidence rows], "empty_windows": [ids],
                 "restorable": bool, "verdict"} - fully detached.

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
            self._require_profile(resolved_name)
            run = [
                crystal
                for crystal in self._checkpoint_crystals_by_id.values()
                if (
                    not crystal.cleaned
                    and crystal.profile_name == resolved_name
                )
            ]
            run.sort(key=lambda crystal: crystal.checkpoint_number)
            breaks: List[Dict[str, object]] = []
            empty_windows: List[str] = []
            if not run:
                return {
                    "profile_name": resolved_name,
                    "ledger_count": 0,
                    "first_checkpoint_number": None,
                    "last_checkpoint_number": None,
                    "dropped_prefix_count": 0,
                    "breaks": [],
                    "empty_windows": [],
                    "restorable": False,
                    "verdict": "empty",
                }
            previous = None
            for crystal in run:
                first_sequence, last_sequence = crystal.sequence_range
                if first_sequence == last_sequence + 1:
                    empty_windows.append(crystal.id)
                elif first_sequence > last_sequence + 1:
                    breaks.append({
                        "checkpoint_id": crystal.id,
                        "kind": "inverted_window",
                        "detail": "sequence_range {0} is not a legal "
                                  "window".format(list(crystal.sequence_range)),
                    })
                if previous is not None:
                    if crystal.checkpoint_number == previous.checkpoint_number:
                        breaks.append({
                            "checkpoint_id": crystal.id,
                            "kind": "duplicate_checkpoint_number",
                            "detail": "number {0} already held by {1}".format(
                                crystal.checkpoint_number, previous.id
                            ),
                        })
                    elif (
                            crystal.checkpoint_number
                            != previous.checkpoint_number + 1
                    ):
                        breaks.append({
                            "checkpoint_id": crystal.id,
                            "kind": "checkpoint_number_gap",
                            "detail": "number jumps {0} -> {1}".format(
                                previous.checkpoint_number,
                                crystal.checkpoint_number,
                            ),
                        })
                    expected_first = previous.sequence_range[1] + 1
                    if crystal.sequence_range[0] != expected_first:
                        breaks.append({
                            "checkpoint_id": crystal.id,
                            "kind": "window_discontinuity",
                            "detail": "window starts at {0}; previous "
                                      "window ended at {1}".format(
                                          crystal.sequence_range[0],
                                          previous.sequence_range[1],
                                      ),
                        })
                previous = crystal
            dropped_prefix = run[0].checkpoint_number - 1
            # A fully dropped-out profile restarts numbering at 1 while the
            # journal sequence keeps climbing: the first retained window's
            # start position betrays the lost prefix even when the numbers
            # look pristine.
            prefix_history_lost = (
                dropped_prefix > 0 or run[0].sequence_range[0] > 1
            )
            if breaks:
                verdict = "broken"
            elif prefix_history_lost:
                verdict = "truncated_prefix"
            else:
                verdict = "intact"
            # BUG-159 (Critical): a fold only reconstructs the true world when
            # the whole baseline chain survives. A truncated_prefix run is
            # structurally contiguous, but its dropped baseline may have held
            # live state no surviving incremental re-captures - and this verb
            # sees only structure, never payloads, so it cannot prove the loss
            # away. Fail closed: certify restorable ONLY for a fully intact
            # chain; retention truncation, breaks, and emptiness are all
            # unrestorable.
            restorable = verdict == "intact"
            return {
                "profile_name": resolved_name,
                "ledger_count": len(run),
                "first_checkpoint_number": run[0].checkpoint_number,
                "last_checkpoint_number": run[-1].checkpoint_number,
                "dropped_prefix_count": dropped_prefix,
                "breaks": breaks,
                "empty_windows": empty_windows,
                "restorable": restorable,
                "verdict": verdict,
            }

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
                1 + the HIGHEST retained checkpoint number for that profile
                (count-based minting duplicated numbers once retention
                dropout engaged: dropping the head shrank the count while
                the tail kept the dropped numbers; found by the
                chain-integrity verb's duplicate check, 2026-07-07).
        """
        highest = max(
            (
                crystal.checkpoint_number
                for crystal in self._checkpoint_crystals_by_id.values()
                if (
                    not crystal.cleaned
                    and crystal.profile_name == profile_name
                )
            ),
            default=0,
        )
        return highest + 1

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
