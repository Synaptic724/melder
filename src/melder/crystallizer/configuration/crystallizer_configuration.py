from collections.abc import Sequence as SequenceABC
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type, Union

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class CrystallizerConfiguration(Cleanable):
    """
    Mutable-to-frozen configuration surface for the crystallizer root.

    Purpose:
        Hold crystallizer-wide policy inputs before the crystallizer root is
        activated. This is the correct home for source-classification policy
        such as `user_source_root_paths`, not the low-level `SpellCrystal`
        constructor.

    Contract:
        - mutable until frozen
        - validates required properties before freeze/activation
        - activation is explicit and implies successful validation/freeze
        - thread-safe mutations are serialized with the instance lock

    Lifecycle:
        The configuration may be created, mutated, validated, frozen, and then
        activated before the singleton crystallizer root accepts it.
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
            "remove_inactive_synthmodules": bool,
            "checkpoint_interval_minutes": int,
            "max_persistence_crystals": int,
        }

    def cleanup(self) -> None:
        """
        Idempotently clear configuration state.

        Returns:
            None.
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
    def remove_inactive_synthmodules(self) -> bool:
        """
        Return whether inactive spells' synthetic modules are unpublished.

        Contract:
            - Default FALSE (insert-only): parking a spell flips its
              crystal to the inactive record location but leaves the
              synthetic module resident in `sys.modules` (validated, low
              hazard). TRUE additionally unpublishes the spell's synthetic
              root module on park (depth-2 removal: reversible, registry
              and custody retained; captured references survive as ghosts
              per the hot-swap law; dependents' deferred imports break on
              their next call until reverse-edge-aware unseed lands).

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
            - Default 100: when a new PersistenceCrystal would grow the
              ledger past this cap, the OLDEST crystal is dropped and
              cleaned first (FIFO dropout; ULID order = age order), so the
              ledger is a rolling window of the most recent checkpoints.
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
            - `remove_inactive_synthmodules` (False),
              `checkpoint_interval_minutes` (60), and
              `max_persistence_crystals` (100) carry defaults and are only
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
        Validate and freeze the configuration.

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

        Returns:
            CrystallizerConfiguration: This configuration instance.
        """
        self.freeze()
        return self

    def activate(self) -> "CrystallizerConfiguration":
        """
        Validate, freeze, and mark the configuration active.

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
            - user_source_root_paths: the resolved current working directory.
            - remove_inactive_synthmodules: False (insert-only).
            - checkpoint_interval_minutes: 60 (one automatic checkpoint per
              hour of recorded activity).
            - max_persistence_crystals: 100 (rolling FIFO ledger window).

        Returns:
            CrystallizerConfiguration: This configuration instance.
        """
        self.with_user_source_root_paths((Path.cwd().resolve(),))
        self.set_property("remove_inactive_synthmodules", False)
        self.set_property("checkpoint_interval_minutes", 60)
        self.set_property("max_persistence_crystals", 100)
        return self

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

    def with_user_source_root_paths(
            self,
            root_paths: Sequence[Union[str, Path]],
    ) -> "CrystallizerConfiguration":
        """
        Set the user-owned source roots used for module classification.

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
