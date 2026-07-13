from collections.abc import Sequence as SequenceABC
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type, Union

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
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
    """

    __melder_internal__ = _mrg.sentinel
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

        Returns:
            str: Stable configuration id.
        """
        self.check_cleaned()
        return self._id

    @property
    def frozen(self) -> bool:
        """
        Return whether the configuration is frozen.

        Returns:
            bool: True when property mutation is closed.
        """
        self.check_cleaned()
        return self._frozen

    @property
    def activated(self) -> bool:
        """
        Return whether the configuration has been activated.

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

        Returns:
            CrystallizerConfiguration: This configuration instance.
        """
        self.set_property("auto_flush_checkpoints", bool(enabled))
        return self

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
              `max_persistence_crystals` (100), and
              `auto_flush_checkpoints` (False) carry defaults and are only
              semantically checked when set explicitly.

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
        for knob in ("checkpoint_interval_minutes", "max_persistence_crystals"):
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

        Returns:
            CrystallizerConfiguration: This configuration instance.
        """
        self.with_user_source_root_paths((Path.cwd().resolve(),))
        self.set_property("retain_user_sources", False)
        self.set_property("remove_inactive_synthmodules", False)
        self.set_property("checkpoint_interval_minutes", 60)
        self.set_property("max_persistence_crystals", 100)
        self.set_property("auto_flush_checkpoints", False)
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
