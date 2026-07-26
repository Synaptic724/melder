from collections.abc import Sequence as SequenceABC
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type, Union

from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class CrystallizerConfiguration(Cleanable):
    """
    Authoring surface for crystallizer capture and durability policy.

    Purpose:
        Tell the public `Crystallizer` how to recognize user-owned modules, how
        much source custody to retain, when to seal checkpoints, how much
        in-process/local history to keep, and whether automatic seals should be
        shipped to durable assets. These are world-recording decisions, so they
        belong here rather than on individual `SpellCrystal` objects.

    Guidance:
        Start with `with_defaults()` unless restoring recorded policy. Override
        only deployment-specific decisions, then call `activate()` and pass the
        result to `Crystallizer.activate(...)`. Common choices are:

        - `with_user_source_root_paths(...)`: classify application source roots.
        - `with_retain_user_sources(True)`: permit fresh-host source rebuilding.
        - `with_auto_flush_checkpoints(True)`: ship cadence seals to assets.
        - `with_max_persistence_crystals(...)`: bound rolling history.

        Source retention can preserve sensitive or large code text; it is
        deliberately off by default. Root paths classify authority only?they do
        not modify `sys.path`, import modules, or grant filesystem access.

    Contract:
        - Mutable until `freeze()`, `finalize()`, or `activate()`.
        - `with_defaults()` produces a complete, valid baseline.
        - `finalize()` freezes without marking the configuration active;
          `activate()` freezes and marks it ready for the crystallizer root.
        - Recorded-policy reload uses a fresh instance and freezes it after
          applying recorded values over the compatibility defaults.

    Threading:
        One instance `RLock` serializes authoring and state transitions. Frozen
        instances are read-only and may be shared with the hosted root.

    Lifecycle / Cleanup:
        The caller owns the configuration until installation; the
        `Crystallizer` owns it afterwards and cleans it during root teardown.
        Callers must not independently clean an installed configuration because
        the live root continues to read policy from it.

    Registration:
        MELDER KERNEL - guarded (internal manifest). access=public because a
        user CONSTRUCTS one, sets policy fluently, and hands it to `Crystallizer.activate(...)`.
        Guarding and being user-constructed are orthogonal: the guard only refuses it as a
        bind target (Melder never injects a configuration); the user still holds and drives it.

    Subsystem Context:
        The capture/durability POLICY surface of the crystallizer subsystem. It carries
        source-classification and checkpoint policy (world-recording decisions) so
        individual `SpellCrystal` objects do not; `Crystallizer.activate(...)` installs it,
        and the record/asset children read policy from it (retain_user_sources, checkpoint
        cadence, max rolling history, auto-flush). Paired with
        `CrystallizerConfigurationBuilder` (the ownership-wrapped authoring path).

    System Context:
        Crystallizer layer of the boot order (position 2, after Aether|AetherUtilitySystem).
        It is the world-recording contract that must be settled BEFORE the crystallizer
        activates: `with_defaults()` is complete easy mode (only `user_source_root_paths` is
        hard-required), and a recorded-policy reload freezes a fresh instance over
        compatibility defaults so a restored world records under the SAME policy that sealed
        it.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. Capture and durability policy. with_defaults() is complete easy mode;
        only user_source_root_paths is hard-required. Set retain_user_sources for opt-in
        physical custody and checkpoint_interval_minutes for automatic cadence.
    """

    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_frozen",
        "_activated",
        "_properties",
        "available_properties",
    ]

    def __init__(self) -> None:
        """
        Initialize one empty crystallizer configuration.

        Contract:
            No policy key is populated. In particular,
            `user_source_root_paths` is required before validation; call
            `with_defaults()` for the normal complete baseline.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._frozen: bool = False
        self._activated: bool = False
        self._properties: Dict[str, object] = {}
        self.available_properties: Dict[str, Union[Type, Tuple[Type, ...]]] = {
            "user_source_root_paths": tuple,
            "retain_user_sources": bool,
            "remove_inactive_synthmodules": bool,
            "checkpoint_interval_minutes": int,
            "max_persistence_crystals": int,
            "auto_flush_checkpoints": bool,
            # Restore-lane scheduler policy (parallel_restore_ulid_identity
            # S2/S4): the loader-owned PhaseScheduler's explicit
            # construction values plus the driver selector (owner ruling
            # 2026-07-19: parallel IS the driver; False selects the
            # sequential fallback). Old records backfill all three through
            # the reload lane's defaults floor (reported, never silent).
            "restore_scheduler_workers": int,
            "restore_scheduler_barrier_timeout_milliseconds": int,
            "restore_parallel_enabled": bool,
            # Analysis IO economy (crystallizer_analysis_io_cache lane,
            # 2026-07-19): descent policy for installed third-party
            # packages during the bind-time module-world walk. Default
            # False - site-package nodes record as provenance-carrying
            # leaves; True restores the interior walk wholesale. Old
            # records backfill False through the reload lane's floor.
            "site_package_dependency_descent": bool,
        }

    def cleanup(self) -> None:
        """
        Idempotently clear configuration state.

        Contract:
            Terminal for this object. Marks it frozen/inactive, clears every
            policy value, and deletes identity/schema fields and the lock. It
            does not clean the crystallizer or remove persisted artifacts.
            Once installed, only the owning crystallizer should call cleanup;
            external cleanup would violate the live root's ownership contract.

        Returns:
            None.

        Threading:
            Serialized by the configuration lock; authoring must be quiescent.

        Lifecycle / Cleanup:
            The current owner?caller, builder, or crystallizer?cleans it when
            the policy object is no longer needed.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._frozen = True
            self._activated = False
            self._properties.clear()

            del self._properties
            del self.available_properties
            del self._id
        del self._lock

    @property
    def id(self) -> str:
        """
        Return the stable configuration id.

        Contract:
            - Identifies THIS CONFIGURATION OBJECT, not the crystallizer singleton it
              configures. Assigned at construction and stable for its life.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            str: Stable configuration id.
        """
        self.check_cleaned()
        return self._id

    @property
    def frozen(self) -> bool:
        """
        Return whether the configuration is frozen.

        Contract:
            - True once the configuration is sealed, meaning PROPERTY MUTATION IS
              CLOSED. It does not mean the policy is in force - that requires
              installing it on the crystallizer root.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            bool: True when property mutation is closed.
        """
        self.check_cleaned()
        return self._frozen

    @property
    def activated(self) -> bool:
        """
        Return whether the configuration has been activated.

        Contract:
            - Marks THIS POLICY OBJECT as ready, NOT the crystallizer. Activating a
              configuration does not activate the singleton; `Crystallizer.activate(
              configuration)` is the step that installs it.
            - Activation implies frozen; frozen does NOT imply activated.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            bool: True when the config is validated, frozen, and marked ready
            for the crystallizer root.
        """
        self.check_cleaned()
        return self._activated

    def set_property(self, key: str, value: object) -> None:
        """
        Set one configuration property before freeze/activation.

        Args:
            key:
                Property name.
            value:
                Candidate property value.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the configuration is already frozen.
            ValueError:
                If the property name is unknown.
            TypeError:
                If the supplied value does not satisfy the declared type.
        """
        self.check_cleaned()
        if self._frozen:
            raise RuntimeError(
                "Cannot modify CrystallizerConfiguration after freeze()."
            )
        if key not in self.available_properties:
            raise ValueError(
                "Unknown CrystallizerConfiguration property: '{0}'.".format(key)
            )

        expected_types = self.available_properties[key]
        normalized_value = self._convert_property_value_if_needed(key, value)

        if isinstance(expected_types, tuple):
            if not isinstance(normalized_value, expected_types):
                raise TypeError(
                    "CrystallizerConfiguration property '{0}' must be one of: {1}.".format(
                        key,
                        ", ".join(
                            expected.__name__
                            for expected in expected_types
                        ),
                    )
                )
        elif not isinstance(normalized_value, expected_types):
            raise TypeError(
                "CrystallizerConfiguration property '{0}' must be one of: {1}.".format(
                    key,
                    expected_types.__name__,
                )
            )

        with self._lock:
            if self._frozen:
                raise RuntimeError(
                    "Cannot modify CrystallizerConfiguration after freeze()."
                )
            self._properties[key] = normalized_value

    def get_property(self, key: str) -> object:
        """
        Return one stored configuration property.

        Args:
            key:
                Property name.

        Returns:
            object: Stored property value.

        Raises:
            KeyError:
                If the property has not been set.
        """
        self.check_cleaned()
        return self._properties[key]

    @property
    def retain_user_sources(self) -> bool:
        """
        Return whether user-owned module SOURCE TEXT is retained at seal.

        Contract:
            - Default FALSE (opt-in only; S2 physical custody): user code
              may be large or sensitive, so retention is a deliberate
              policy choice - False is byte-identical to the pre-S2
              record at every surface.
            - True: every module classified as user source retains text,
              SHA256, path, and package posture inside the `SpellCrystal`. On a
              fresh host, an absent file may rebuild through the synthetic
              module lane. Retained text never overrides a live file; drift is
              reported and the live file remains authoritative.

        Returns:
            bool: The configured knob, default False.
        """
        self.check_cleaned()
        value = self._properties.get("retain_user_sources", False)
        return bool(value)

    @property
    def site_package_dependency_descent(self) -> bool:
        """
        Return whether the analysis walk descends INTO installed packages.

        Contract:
            - Defaulted-optional (schema default False): when the key is
              absent, the walk records site-package modules as
              provenance-carrying LEAVES - distribution name/version and
              file identity still capture, but their source is never read
              and their dependencies never enqueue. Bind latency stays
              proportional to the USER world, not the installed one.
            - True restores the pre-lane interior walk wholesale (module
              inventories of third-party packages re-enter the record).
            - Site packages make no fingerprint claims either way (S1
              law), so drift and restore surfaces are unaffected.

        Returns:
            bool: The configured knob, default False.
        """
        self.check_cleaned()
        value = self._properties.get("site_package_dependency_descent", False)
        return bool(value)

    @property
    def remove_inactive_synthmodules(self) -> bool:
        """
        Return whether inactive spells' synthetic modules are unpublished.

        Contract:
            - Default False: parking changes recorded custody but leaves
              the synthetic root module published for maximum runtime
              continuity.
            - True: parking may unpublish that root while retaining registry
              and custody state, making promotion reversible. A module with
              live published synthetic dependents stays resident under the
              reverse-edge safety check. Existing Python references remain live
              even after unpublication; this knob controls import visibility,
              not object destruction.

        Returns:
            bool: The configured knob, default False.
        """
        self.check_cleaned()
        value = self._properties.get("remove_inactive_synthmodules", False)
        return bool(value)

    @property
    def checkpoint_interval_minutes(self) -> int:
        """
        Return the automatic-checkpoint cadence in minutes.

        Contract:
            - Default 60 (one hour): while the crystallizer is activated,
              the emit path seals a new PersistenceCrystal once at least
              this many minutes have passed since the previous automatic
              checkpoint. Cadence is activity-driven (checked at emit
              time), so a quiet world mints nothing - there is no
              background timer thread.
            - Must be a positive int when set explicitly.

        Returns:
            int: The configured cadence, default 60.

        Raises:
            ValueError:
                If the stored value is not a positive int.
        """
        self.check_cleaned()
        value = self._properties.get("checkpoint_interval_minutes", 60)
        self._require_positive_int("checkpoint_interval_minutes", value)
        return int(value)

    @property
    def max_persistence_crystals(self) -> int:
        """
        Return the checkpoint-ledger retention cap.

        Contract:
            - Default 100: when a new `PersistenceCrystal` would exceed
              the cap, the oldest ledger entry by exact insertion order drops
              and cleans first. Local cache retention follows recorded
              checkpoint numbers, avoiding ambiguous same-millisecond ULID
              tails. External retention is a separate opt-in operation.
            - Must be a positive int when set explicitly.

        Returns:
            int: The configured cap, default 100.

        Raises:
            ValueError:
                If the stored value is not a positive int.
        """
        self.check_cleaned()
        value = self._properties.get("max_persistence_crystals", 100)
        self._require_positive_int("max_persistence_crystals", value)
        return int(value)

    @property
    def auto_flush_checkpoints(self) -> bool:
        """
        Return whether automatic checkpoints also flush to the local cache.

        Contract:
            - Default False: cadence seals remain in the in-process ledger
              until a caller explicitly flushes them.
            - True: every automatic seal runs the normal asset flush?local
              atomic cache write first, followed by the optional external mesh
              write when a manager is attached and uploads are enabled.

        Returns:
            bool: The configured knob, default False.
        """
        self.check_cleaned()
        value = self._properties.get("auto_flush_checkpoints", False)
        return bool(value)

    def with_auto_flush_checkpoints(
            self,
            enabled: bool,
    ) -> "CrystallizerConfiguration":
        """
        Set whether automatic checkpoints also flush to the local cache.

        Args:
            enabled:
                True = every cadence seal ships its cached-item to disk.

        Contract:
            - COERCES with `bool(...)` rather than type-checking, so any truthy value
              is accepted and silently converted. That is looser than the strict
              `isinstance` setters elsewhere in this class.
            - True makes every cadence seal ship its cached item to disk, trading
              throughput for durability.
            - Refused once frozen.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            CrystallizerConfiguration: This configuration instance.
        """
        self.set_property("auto_flush_checkpoints", bool(enabled))
        return self

    @property
    def restore_parallel_enabled(self) -> bool:
        """
        Return whether checkpoint restore runs the parallel driver.

        Contract:
            - Default True (owner ruling 2026-07-19: parallel IS the
              driver): the loader owns a PhaseScheduler pool and the
              RestoreEngine executes graph-derived levels as phases.
            - False selects the sequential fallback driver - the canon
              single-thread stage chain, byte-identical to the
              pre-parallel engine. The same knob is the rollback lane.

        Returns:
            bool: The configured driver selector, default True.
        """
        self.check_cleaned()
        value = self._properties.get("restore_parallel_enabled", True)
        return bool(value)

    @property
    def restore_scheduler_workers(self) -> int:
        """
        Return the restore scheduler's worker-thread count.

        Contract:
            - Default 4: the loader-owned PhaseScheduler pool width for
              per-entity replay units inside each plan level.
            - Must be a positive int when set explicitly.

        Returns:
            int: The configured worker count, default 4.

        Raises:
            ValueError:
                If the stored value is not a positive int.
        """
        self.check_cleaned()
        value = self._properties.get("restore_scheduler_workers", 4)
        self._require_positive_int("restore_scheduler_workers", value)
        return int(value)

    @property
    def restore_scheduler_barrier_timeout_milliseconds(self) -> int:
        """
        Return the restore scheduler's per-phase barrier timeout.

        Contract:
            - Default 60000 (one minute): restore units import and bind
              real code, so spellbook-scale phase timeouts would abort
              large-world loads.
            - Must be a positive int (milliseconds) when set explicitly.

        Returns:
            int: The configured barrier timeout in ms, default 60000.

        Raises:
            ValueError:
                If the stored value is not a positive int.
        """
        self.check_cleaned()
        value = self._properties.get(
            "restore_scheduler_barrier_timeout_milliseconds", 60000
        )
        self._require_positive_int(
            "restore_scheduler_barrier_timeout_milliseconds", value
        )
        return int(value)

    @staticmethod
    def _require_positive_int(key: str, value: object) -> None:
        """
        Reject non-int (including bool) or non-positive knob values.

        Args:
            key:
                Property name being validated.
            value:
                Candidate stored value.

        Returns:
            None.

        Raises:
            ValueError:
                If the value is a bool, not an int, or not positive.
        """
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(
                "CrystallizerConfiguration property '{0}' must be a "
                "positive int (got {1!r}). Example: "
                "configuration.set_property('{0}', 60).".format(key, value)
            )

    def has_property(self, key: str) -> bool:
        """
        Return whether one property is currently defined.

        Args:
            key:
                Property name.

        Contract:
            - Tests whether the key has been SET, not whether it is a legal key. An
              unknown key returns False rather than raising, so this cannot validate
              a property name against the schema.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            bool: True when the property has been set.
        """
        self.check_cleaned()
        return key in self._properties

    def validate(self) -> bool:
        """
        Validate that the crystallizer policy bag is complete and coherent.

        Contract:
            - `user_source_root_paths` is the only hard-required property.
            - `retain_user_sources` (False),
              `remove_inactive_synthmodules` (False),
              `checkpoint_interval_minutes` (60),
              `max_persistence_crystals` (100),
              `auto_flush_checkpoints` (False),
              `restore_parallel_enabled` (True),
              `restore_scheduler_workers` (4), and
              `restore_scheduler_barrier_timeout_milliseconds` (60000)
              carry defaults and are only semantically checked when set
              explicitly.

        Returns:
            bool: True when the configuration is valid.

        Raises:
            ValueError:
                If a required property is missing or semantically invalid.
        """
        self.check_cleaned()
        if "user_source_root_paths" not in self._properties:
            raise ValueError(
                "Missing required crystallizer configuration property: "
                "'user_source_root_paths'. Set it explicitly or start from "
                "CrystallizerConfiguration().with_defaults()."
            )
        if len(self.user_source_root_paths) == 0:
            raise ValueError(
                "user_source_root_paths must contain at least one configured root."
            )
        # Defaulted knobs are optional; when set explicitly they must be
        # semantically valid (the getters re-check on every read).
        for knob in (
                "checkpoint_interval_minutes",
                "max_persistence_crystals",
                "restore_scheduler_workers",
                "restore_scheduler_barrier_timeout_milliseconds",
        ):
            if knob in self._properties:
                self._require_positive_int(knob, self._properties[knob])
        return True

    def freeze(self) -> None:
        """
        Validate and freeze the configuration without activating it.

        Contract:
            Idempotent. After success, all authoring methods refuse mutation;
            the configuration is suitable for inspection or later activation.

        Returns:
            None.
        """
        self.check_cleaned()
        if self._frozen:
            return
        if not self.validate():
            raise ValueError("CrystallizerConfiguration validation failed.")
        with self._lock:
            self._frozen = True

    def finalize(self) -> "CrystallizerConfiguration":
        """
        Validate and freeze the configuration, then return it.

        Guidance:
            Choose this when another owner should decide when activation occurs.
            Use `activate()` when the next step is installation on the live
            crystallizer root.

        Contract:
            - `freeze()` plus `return self`: seals WITHOUT marking the policy ready.
            - Choose it when a DIFFERENT owner will decide when activation happens;
              choose `activate()` when installation on the crystallizer root is the
              next step.
            - Idempotent, inheriting freeze's early return.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            CrystallizerConfiguration: This configuration instance.
        """
        self.freeze()
        return self

    def activate(self) -> "CrystallizerConfiguration":
        """
        Validate, freeze, and mark the configuration active.

        Guidance:
            This is the normal final authoring step before
            `Crystallizer.activate(configuration)`. It changes only this policy
            object's readiness; it does not activate the singleton by itself.

        Contract:
            - Freezes and marks this policy object ready. UNLIKE the Aether and
              mutation-research configurations, it EMITS NOTHING - there is no
              activation record here, because this object configures the recorder
              itself.
            - It does NOT activate the crystallizer singleton; that is a separate
              `Crystallizer.activate(configuration)` call.
            - Safe to call more than once: freeze is idempotent and the flag is a
              plain set with no side effect attached.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            CrystallizerConfiguration: This activated configuration instance.
        """
        self.freeze()
        with self._lock:
            self._activated = True
        return self

    def with_defaults(self) -> "CrystallizerConfiguration":
        """
        Load the complete default crystallizer policy set (easy mode).

        Purpose:
            One-call default posture, mirroring the AethericFrame
            configuration builder style: chain it, then `activate()`.
            `CrystallizerConfiguration().with_defaults().activate()` is a
            fully valid configuration.

        Contract:
            - `user_source_root_paths`: resolved current working directory.
            - `retain_user_sources`: False (fingerprints/paths, no source text).
            - `remove_inactive_synthmodules`: False (keep imports resident).
            - `checkpoint_interval_minutes`: 60 activity-driven minutes.
            - `max_persistence_crystals`: 100-entry rolling ledger/cache cap.
            - `auto_flush_checkpoints`: False (manual durability flush).
            - `restore_scheduler_workers`: 4 (loader-owned PhaseScheduler
              pool size for parallel restore phases).
            - `restore_scheduler_barrier_timeout_milliseconds`: 60000
              (generous per-level barrier bound: restore units import and
              bind real code, so short spellbook-style timeouts would abort
              legitimate large-world loads).
            - `restore_parallel_enabled`: True (owner ruling 2026-07-19:
              parallel is THE restore driver; False selects the sequential
              fallback driver).
            - `site_package_dependency_descent`: False (analysis walks stop
              AT installed third-party packages; provenance still captures).

        Returns:
            CrystallizerConfiguration: This configuration instance.
        """
        self.with_user_source_root_paths((Path.cwd().resolve(),))
        self.set_property("retain_user_sources", False)
        self.set_property("remove_inactive_synthmodules", False)
        self.set_property("checkpoint_interval_minutes", 60)
        self.set_property("max_persistence_crystals", 100)
        self.set_property("auto_flush_checkpoints", False)
        self.set_property("restore_scheduler_workers", 4)
        self.set_property(
            "restore_scheduler_barrier_timeout_milliseconds", 60000
        )
        self.set_property("restore_parallel_enabled", True)
        self.set_property("site_package_dependency_descent", False)
        return self

    def load_recorded_dictionary(
            self,
            recorded_properties: Dict[str, Any],
    ) -> Dict[str, List[str]]:
        """
        Reload lane: apply one RECORDED property payload as configuration
        truth and seal.

        Purpose:
            The cache-boot counterpart to `with_defaults`. When a world
            reboots from cached checkpoints, the crystallizer's own policy
            (source roots, retention, cadence, flush posture) is part of
            the recorded truth - it reloads from the CrystallizerCrystal
            payload, never from present-day defaults, and the lane loads
            and freezes in one motion.

        Contract:
            - Defaults land first as the backfill floor (`with_defaults`),
              then every recorded key OVERWRITES its default (recorded
              truth wins); registry keys the record did not carry are
              returned under "backfilled" so nothing defaults silently.
            - user_source_root_paths recorded as a list (the emission
              scalar filter's collection form) re-tuples on the way in.
            - A recorded value the property system refuses is skipped and
              returned under "rejected" as "key: reason" (documented
              best-effort collection for the caller's reporting).
            - LOADS AND FREEZES in one motion: the returned state is
              sealed. The freeze emits nothing; the crystallizer twin
              emits at `Crystallizer.activate`, the configured moment.

        Args:
            recorded_properties:
                Property name -> recorded value mapping (one sealed,
                JSON-safe CrystallizerCrystal configuration_payload).

        Returns:
            Dict[str, List[str]]:
                {"rejected": ["key: reason", ...],
                 "backfilled": [key, ...]}.

        Raises:
            RuntimeError: If the configuration is cleaned or already
                frozen.
            ValueError: If the reloaded property set fails validation at
                the internal freeze.
        """
        self.check_cleaned()
        if self._frozen:
            raise RuntimeError(
                "CrystallizerConfiguration is already frozen; the reload "
                "lane requires a fresh configuration object."
            )
        self.with_defaults()
        rejected: List[str] = []
        applied: List[str] = []
        for key, value in dict(recorded_properties).items():
            candidate = value
            if key == "user_source_root_paths" and isinstance(value, list):
                # Emission records collections as lists of strings; the
                # registry types this key as a tuple.
                candidate = tuple(value)
            try:
                self.set_property(key, candidate)
                applied.append(key)
            except Exception as error:
                # Best-effort collection by contract: the refusal reason
                # rides back to the caller for shortfall reporting.
                rejected.append("{0}: {1}".format(key, error))
        backfilled = sorted(
            key for key in self.available_properties.keys()
            if key not in applied
        )
        # Reload seals: load it in, freeze it - the reload lane never
        # hands back a mutable configuration.
        self.freeze()
        return {"rejected": rejected, "backfilled": backfilled}

    def with_checkpoint_interval_minutes(
            self,
            minutes: int,
    ) -> "CrystallizerConfiguration":
        """
        Set the automatic-checkpoint cadence in minutes.

        Args:
            minutes:
                Positive minute count between automatic checkpoints
                (1 = every minute, 60 = hourly).

        Returns:
            CrystallizerConfiguration: This configuration instance.

        Raises:
            ValueError:
                If `minutes` is a bool, not an int, or not positive.
        """
        self._require_positive_int("checkpoint_interval_minutes", minutes)
        self.set_property("checkpoint_interval_minutes", minutes)
        return self

    def with_max_persistence_crystals(
            self,
            max_crystals: int,
    ) -> "CrystallizerConfiguration":
        """
        Set the checkpoint-ledger retention cap.

        Args:
            max_crystals:
                Positive maximum ledger size; the oldest crystal drops out
                when a new checkpoint would exceed it.

        Returns:
            CrystallizerConfiguration: This configuration instance.

        Raises:
            ValueError:
                If `max_crystals` is a bool, not an int, or not positive.
        """
        self._require_positive_int("max_persistence_crystals", max_crystals)
        self.set_property("max_persistence_crystals", max_crystals)
        return self

    def with_retain_user_sources(
            self,
            retain: bool,
    ) -> "CrystallizerConfiguration":
        """
        Set the opt-in user-source TEXT retention policy (S2 custody).

        Args:
            retain:
                True retains user-owned module source text inside sealed
                SpellCrystals for fresh-pod rebuilds; False (default)
                records paths and fingerprints only.

        Contract:
            - OPT-IN CUSTODY DECISION, and it defaults to FALSE for good reason: when
              True, USER-OWNED MODULE SOURCE TEXT IS RETAINED INSIDE SEALED
              CRYSTALS. With it False only paths and fingerprints are recorded.
            - Enable it only when fresh-pod rebuilds genuinely require the source,
              and only when the crystal store is a trusted location - it changes
              what a crystal CONTAINS, not merely what it references.
            - Refused once frozen.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            CrystallizerConfiguration: This configuration instance.
        """
        self.set_property("retain_user_sources", retain)
        return self

    def with_user_source_root_paths(
            self,
            root_paths: Sequence[Union[str, Path]],
    ) -> "CrystallizerConfiguration":
        """
        Set the user-owned source roots used for module classification.

        Purpose:
            Distinguish application code from site packages and unknown/binary
            authority during crystal analysis. Inputs resolve to absolute,
            deduplicated `Path` values at authoring time.

        Contract:
            This policy does not require the roots to exist immediately, does
            not add them to `sys.path`, and does not read their contents. It is
            a classification boundary consumed later by analysis.

        Args:
            root_paths:
                Sequence of filesystem roots that should count as user-owned
                source authority during crystal dependency classification.

        Returns:
            CrystallizerConfiguration: This configuration instance.
        """
        self.set_property("user_source_root_paths", root_paths)
        return self

    @property
    def user_source_root_paths(self) -> Tuple[Path, ...]:
        """
        Return the normalized user-source root tuple.

        Contract:
            - DEFENSIVE READ: the value must remain a tuple of `Path` entries, and a
              drifted element raises `TypeError` rather than being returned. That
              guards against direct tampering with the property bag.
            - Returns NORMALIZED, resolved paths rather than the raw strings that
              may have been supplied.

        Threading:
            State transitions are applied under the configuration lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            Tuple[Path, ...]: Configured source roots as resolved paths.
        """
        self.check_cleaned()
        value = self.get_property("user_source_root_paths")
        if not isinstance(value, tuple):
            raise TypeError(
                "user_source_root_paths must remain a tuple of Path values."
            )
        for entry in value:
            if not isinstance(entry, Path):
                raise TypeError(
                    "user_source_root_paths entries must remain Path values."
                )
        return value

    @staticmethod
    def _convert_property_value_if_needed(key: str, value: object) -> object:
        """
        Normalize property values before storage.

        Args:
            key:
                Property name being assigned.
            value:
                Candidate property value.

        Returns:
            object: Normalized property value.
        """
        if key != "user_source_root_paths":
            return value

        if isinstance(value, (str, Path)):
            candidates: Sequence[Union[str, Path]] = (value,)
        elif isinstance(value, SequenceABC):
            candidates = value
        else:
            raise TypeError(
                "user_source_root_paths must be a sequence of str/Path values."
            )

        normalized_paths: List[Path] = []
        seen_paths = set()
        for candidate in candidates:
            if not isinstance(candidate, (str, Path)):
                raise TypeError(
                    "user_source_root_paths entries must be str or Path values."
                )
            resolved_path = Path(candidate).resolve()
            if resolved_path in seen_paths:
                continue
            seen_paths.add(resolved_path)
            normalized_paths.append(resolved_path)
        return tuple(normalized_paths)
