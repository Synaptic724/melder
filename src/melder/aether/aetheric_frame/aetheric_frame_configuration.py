import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, ClassVar, Tuple, Union



from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.utilities.general_base.cleanable import Cleanable
from melder.crystallizer.crystallizer import Crystallizer
from melder.crystallizer.crystals.aetheric_frame_crystal import AethericFrameCrystal
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.synchronization.safeguard import SafeGuard


class AethericFrameConfiguration(Cleanable):
    """
    Internal

    Narrow frame-level runtime posture for AR and Nexus-facing behavior.

    Purpose:
        Hold only the immutable frame posture fields that matter to AR-facing
        systems and later canonical Nexus record hosting.

    Contract:
        - Captures frame-level posture values:
          `system_state`, `ai_native_enabled`, `rift_enabled`, and
          `shared_framewide_spellbook_configuration`.
        - Captures frame-level change-control posture values:
          `disable_all_transactions_after_conjure`,
          `disable_mutations`,
          `disable_linking`,
          `disable_bind`,
          `disable_conduit_cluster`,
          `disable_transfer_of_ownership`, and
          `disable_contract_mutation`.
        - Carries provenance via `origin_spellbook_id`.
        - Is immutable by convention after construction; callers bind one
          instance into an `AethericFrame` and later same-frame attempts do not
          overwrite that posture.
        - Equality of posture is defined by the frame-posture fields, not by
          object identity, object id, or origin spellbook id.
        - Cleanup is idempotent and clears all owned references.

    Lifecycle:
        Created from one Spellbook `Configuration` during conjure and then
        bound into the owning `AethericFrame`.

    Threading:
        Immutable by convention after construction, so reads need no lock. The
        binding step is what is serialized, not the object.

    Registration:
        MELDER KERNEL - guarded. Derived during conjure from the Spellbook
        configuration; users configure the Spellbook, never this object.

    Subsystem Context:
        The NARROW posture object, deliberately separate from the much richer
        shared `SpellbookConfiguration`. It carries only what AR-facing and
        change-control systems need, which is why `AethericFrame` can hand it
        out freely without exposing the full book configuration surface.

    System Context:
        Two properties make this class do real work rather than just hold
        fields.
        First, POSTURE EQUALITY IS BY VALUE, not identity - equality is defined
        by the frame-posture fields and explicitly ignores object id and
        `origin_spellbook_id`. That is what lets a second book conjure into an
        existing frame and be accepted when its posture MATCHES, instead of
        being rejected merely for being a different object. Provenance is
        carried for diagnostics, never for comparison.
        Second, the `disable_*` fields are LIVE READS by the transaction
        mediator, not values captured once at construction. Under lazy frames
        every restore rebinds posture onto a default-postured frame, so
        `bind_frame_configuration` propagates the canonical
        `max_transaction_wait_time_in_seconds` through `mediator.configure()`
        at both landing branches - closing the captured-once-at-ctor gap. A
        recorded frame posture therefore governs the live mediator after a
        restore, rather than being decoration on a twin.
    """
    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Narrow frame posture (system_state, ai_native_enabled, rift_enabled, and the "
        "disable_* change-control gates). Derived at conjure from your SpellbookConfiguration - "
        "configure the Spellbook, not this. Read it to learn what a frame will allow."
    )

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_frozen",
        "_origin_spellbook_id",
        "_system_state",
        "_ai_native_enabled",
        "_rift_enabled",
        "_shared_framewide_spellbook_configuration",
        "_system_caching_enabled",
        "_system_cache_root_path",
        "_disable_all_transactions_after_conjure",
        "_disable_mutations",
        "_disable_linking",
        "_disable_bind",
        "_disable_conduit_cluster",
        "_disable_transfer_of_ownership",
        "_disable_contract_mutation",
        "_max_transaction_wait_time_in_seconds",
    ]

    def __init__(
            self,
            *,
            origin_spellbook_id: Optional[str],
            system_state: SystemState,
            ai_native_enabled: bool,
            rift_enabled: bool,
            shared_framewide_spellbook_configuration: bool = False,
            system_caching_enabled: bool = True,
            system_cache_root_path: Optional[Union[str, Path]] = None,
            disable_all_transactions_after_conjure: bool = False,
            disable_mutations: bool = True,
            disable_linking: bool = False,
            disable_bind: bool = False,
            disable_conduit_cluster: bool = False,
            disable_transfer_of_ownership: bool = False,
            disable_contract_mutation: bool = False,
            max_transaction_wait_time_in_seconds: float = 30.0,
    ) -> None:
        """
        Initialize one frame-level posture object.

        Args:
            origin_spellbook_id:
                Spellbook id that first produced this frame posture. May be
                None when built outside normal Spellbook conjure flow.
            system_state:
                Frame system state. Must resolve to a concrete `SystemState`.
            ai_native_enabled:
                Whether the frame allows AI-native runtime behavior.
            rift_enabled:
                Whether the frame allows AI-profile publication / AR-observable
                posture.
            shared_framewide_spellbook_configuration:
                Whether the frame posture permits one explicit frame-owned
                shared rich `SpellbookConfiguration` object.
            disable_all_transactions_after_conjure:
                Whether new transactions are blocked once the frame runtime is
                already conjured/live.
            disable_mutations:
                Whether mutation entrypoints are disabled for this frame.
            disable_linking:
                Whether linking entrypoints are disabled for this frame.
            disable_bind:
                Whether bind/scan entrypoints are disabled for this frame.
            disable_conduit_cluster:
                Whether conduit-cluster entrypoints are disabled for this frame.
            disable_transfer_of_ownership:
                Whether ownership-transfer entrypoints are disabled for this
                frame.
            disable_contract_mutation:
                Whether direct contract mutation entrypoints are disabled for
                this frame.
            max_transaction_wait_time_in_seconds:
                Maximum seconds a root transaction may wait for conflicting
                scope claims to release before admission times out.

        Returns:
            None.

        Raises:
            TypeError: If the boolean posture flags are not bools.
            ValueError: If `system_state` cannot be normalized into a
                `SystemState`.
        """
        super().__init__()
        normalized_system_state = EnumHelpers.convert_enum_and_check(
            system_state,
            SystemState,
        )
        if not isinstance(ai_native_enabled, bool):
            raise TypeError("ai_native_enabled must be a bool.")
        if not isinstance(rift_enabled, bool):
            raise TypeError("rift_enabled must be a bool.")
        if not isinstance(shared_framewide_spellbook_configuration, bool):
            raise TypeError(
                "shared_framewide_spellbook_configuration must be a bool."
            )
        for field_name, value in (
            (
                "disable_all_transactions_after_conjure",
                disable_all_transactions_after_conjure,
            ),
            ("disable_mutations", disable_mutations),
            ("disable_linking", disable_linking),
            ("disable_bind", disable_bind),
            ("disable_conduit_cluster", disable_conduit_cluster),
            (
                "disable_transfer_of_ownership",
                disable_transfer_of_ownership,
            ),
            ("disable_contract_mutation", disable_contract_mutation),
            ("system_caching_enabled", system_caching_enabled),
        ):
            if not isinstance(value, bool):
                raise TypeError(f"{field_name} must be a bool.")
        if (
            not isinstance(max_transaction_wait_time_in_seconds, (int, float))
            or isinstance(max_transaction_wait_time_in_seconds, bool)
        ):
            raise TypeError(
                "max_transaction_wait_time_in_seconds must be a float or int."
            )
        if max_transaction_wait_time_in_seconds <= 0:
            raise ValueError(
                "max_transaction_wait_time_in_seconds must be greater than 0."
            )
        if ai_native_enabled and normalized_system_state != SystemState.dynamic:
            raise ValueError(
                "ai_native_enabled requires system_state to be dynamic."
            )

        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._frozen: bool = False
        self._origin_spellbook_id: Optional[str] = origin_spellbook_id
        self._system_state: SystemState = normalized_system_state
        self._ai_native_enabled: bool = ai_native_enabled
        self._rift_enabled: bool = rift_enabled
        self._shared_framewide_spellbook_configuration: bool = (
            shared_framewide_spellbook_configuration
        )
        self._system_caching_enabled: bool = system_caching_enabled
        self._system_cache_root_path: Path = self._normalize_cache_root_path(
            system_cache_root_path
        )
        self._disable_all_transactions_after_conjure: bool = (
            disable_all_transactions_after_conjure
        )
        self._disable_mutations: bool = disable_mutations
        self._disable_linking: bool = disable_linking
        self._disable_bind: bool = disable_bind
        self._disable_conduit_cluster: bool = disable_conduit_cluster
        self._disable_transfer_of_ownership: bool = (
            disable_transfer_of_ownership
        )
        self._disable_contract_mutation: bool = disable_contract_mutation
        self._max_transaction_wait_time_in_seconds: float = float(
            max_transaction_wait_time_in_seconds
        )

    @staticmethod
    def _build_default_system_cache_root_path() -> Path:
        """
        Build the default cache root fragment.

        Returns:
            Path: Relative `__melder_cache__` fragment resolved later against
            the `melder` package root (site-packages when installed,
            `src/melder` in a source checkout).
        """
        return Path("__melder_cache__")

    @staticmethod
    def _normalize_cache_root_path(
            root_path: Optional[Union[str, Path]],
    ) -> Path:
        """
        Normalize and validate a relative cache-root fragment.

        Returns:
            Path: The default fragment when `root_path` is None, otherwise the
            validated relative fragment.

        Raises:
            TypeError: If `root_path` is not str/Path.
            ValueError: If `root_path` is absolute.
        """
        if root_path is None:
            return AethericFrameConfiguration._build_default_system_cache_root_path()
        if not isinstance(root_path, (str, Path)):
            raise TypeError("system_cache_root_path must be a str or Path.")
        normalized_root_path = Path(root_path)
        if normalized_root_path.is_absolute():
            raise ValueError(
                "system_cache_root_path must remain relative to the melder package root."
            )
        return normalized_root_path

    def cleanup(self) -> None:
        """
        Idempotently clear owned posture state.

        Contract:
            - Safe to call multiple times.
            - Clears all owned posture fields and provenance references.
            - Leaves the object permanently cleaned.

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
            del self._id
            del self._origin_spellbook_id
            del self._system_state
            del self._ai_native_enabled
            del self._rift_enabled
            del self._shared_framewide_spellbook_configuration
            del self._system_caching_enabled
            del self._system_cache_root_path
            del self._disable_all_transactions_after_conjure
            del self._disable_mutations
            del self._disable_linking
            del self._disable_bind
            del self._disable_conduit_cluster
            del self._disable_transfer_of_ownership
            del self._disable_contract_mutation
            del self._max_transaction_wait_time_in_seconds
        del self._lock

    def validate(self) -> bool:
        """
        Validate the current frame posture values.

        Returns:
            bool: True when the current frame posture is valid.

        Raises:
            ValueError: If AI-native posture is enabled while system state is
                not dynamic.
        """
        self.check_cleaned()
        with self._lock:
            if self._ai_native_enabled and self._system_state != SystemState.dynamic:
                raise ValueError(
                    "ai_native_enabled requires system_state to be dynamic."
                )
            return True

    def freeze(
            self,
            origin_spellbook_id: Optional[str] = None,
            origin_frame_name: Optional[str] = None,
    ) -> None:
        """
        Freeze the frame posture so no further mutation is allowed.

        Args:
            origin_spellbook_id: Optional spellbook id to stamp as the posture
                origin if one should be recorded at freeze time.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            if self._frozen:
                return
            self.validate()
            if origin_spellbook_id is not None:
                self._origin_spellbook_id = origin_spellbook_id
            self._frozen = True
        # Configuration activation is the emission factor: pull the
        # crystallizer singleton directly (guarding the pre-boot case,
        # where the singleton is not yet initialized and construction
        # requires the hosting Aether), emit when recording, then drop
        # the local handle.
        if (
                origin_frame_name is not None
                and self._system_state is SystemState.dynamic
                and Crystallizer._initialized
        ):
            crystallizer = Crystallizer()
            if crystallizer.activated:
                posture_payload: Dict[str, object] = {}
                for posture_name, posture_value in self.describe_posture().items():
                    if (
                            isinstance(posture_value, (str, int, float, bool))
                            or posture_value is None
                    ):
                        posture_payload[posture_name] = posture_value
                    elif isinstance(posture_value, SystemState):
                        posture_payload[posture_name] = posture_value.name
                    else:
                        posture_payload[posture_name] = str(posture_value)
                crystallizer.emit(
                    AethericFrameCrystal(
                        frame_name=origin_frame_name,
                        system_state_name=self._system_state.name,
                        rift_enabled=self._rift_enabled,
                        ai_native_enabled=self._ai_native_enabled,
                        dev_ops_payload=posture_payload,
                    )
                )
            del crystallizer

    def with_system_state(
            self,
            system_state: SystemState | str,
    ) -> "AethericFrameConfiguration":
        """
        Set the frame system state before freeze and return `self`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            system_state:
                `SystemState.automatic` or `SystemState.dynamic`. Dynamic is
                required for linking, severing, transfer, and lesser-to-normal upgrade.
        """
        self.check_cleaned()
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify frame configuration after it is frozen.")
            self._system_state = EnumHelpers.convert_enum_and_check(
                system_state,
                SystemState,
            )
        return self

    def with_ai_native(
            self,
            enabled: bool = True,
    ) -> "AethericFrameConfiguration":
        """
        Set AI-native frame posture before freeze and return `self`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            enabled:
                Whether the frame permits AI-native runtime behaviour.
        """
        self.check_cleaned()
        if not isinstance(enabled, bool):
            raise TypeError("ai_native_enabled must be a bool.")
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify frame configuration after it is frozen.")
            self._ai_native_enabled = enabled
        return self

    def with_rift_enabled(
            self,
            enabled: bool = True,
    ) -> "AethericFrameConfiguration":
        """
        Set Rift-visible frame posture before freeze and return `self`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            enabled:
                Whether Rifts may attach to this frame. Static AR attachment
                requires this to be True.
        """
        self.check_cleaned()
        if not isinstance(enabled, bool):
            raise TypeError("rift_enabled must be a bool.")
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify frame configuration after it is frozen.")
            self._rift_enabled = enabled
        return self

    def with_shared_framewide_spellbook_configuration(
            self,
            enabled: bool = True,
    ) -> "AethericFrameConfiguration":
        """
        Set whether the frame permits explicit shared rich Spellbook config and
        return `self`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            enabled:
                Whether the frame may own one shared rich SpellbookConfiguration
                that later books adopt instead of creating their own.
        """
        self.check_cleaned()
        if not isinstance(enabled, bool):
            raise TypeError(
                "shared_framewide_spellbook_configuration must be a bool."
            )
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify frame configuration after it is frozen.")
            self._shared_framewide_spellbook_configuration = enabled
        return self

    def with_system_caching_enabled(
            self,
            enabled: bool = True,
    ) -> "AethericFrameConfiguration":
        """
        Set whether spell runtime caching is enabled for the frame and return
        `self`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            enabled:
                Whether the crystallizer cache is active for this frame.
        """
        self.check_cleaned()
        if not isinstance(enabled, bool):
            raise TypeError("system_caching_enabled must be a bool.")
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify frame configuration after it is frozen.")
            self._system_caching_enabled = enabled
        return self

    def with_system_cache_root_path(
            self,
            root_path: Union[str, Path],
    ) -> "AethericFrameConfiguration":
        """
        Set the relative cache-root fragment for the frame and return `self`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            path:
                Directory under which `__crystallizer_cache__` profile folders are
                written. None restores the default location.
        """
        self.check_cleaned()
        normalized_root_path = self._normalize_cache_root_path(root_path)
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify frame configuration after it is frozen.")
            self._system_cache_root_path = normalized_root_path
        return self

    def with_disable_all_transactions_after_conjure(
            self,
            enabled: bool = True,
    ) -> "AethericFrameConfiguration":
        """
        Set whether new transactions are disabled after conjure and return `self`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            enabled:
                True to refuse every new change-control transaction once the
                frame is live. The hardest of the disable_* gates.
        """
        self.check_cleaned()
        if not isinstance(enabled, bool):
            raise TypeError("disable_all_transactions_after_conjure must be a bool.")
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify frame configuration after it is frozen.")
            self._disable_all_transactions_after_conjure = enabled
        return self

    def with_disable_mutations(
            self,
            enabled: bool = True,
    ) -> "AethericFrameConfiguration":
        """
        Set whether mutation entrypoints are disabled and return `self`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            enabled:
                True to refuse mutation entrypoints on this frame.
        """
        self.check_cleaned()
        if not isinstance(enabled, bool):
            raise TypeError("disable_mutations must be a bool.")
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify frame configuration after it is frozen.")
            self._disable_mutations = enabled
        return self

    def with_disable_linking(
            self,
            enabled: bool = True,
    ) -> "AethericFrameConfiguration":
        """
        Set whether linking entrypoints are disabled and return `self`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            enabled:
                True to refuse link and sever transactions on this frame.
        """
        self.check_cleaned()
        if not isinstance(enabled, bool):
            raise TypeError("disable_linking must be a bool.")
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify frame configuration after it is frozen.")
            self._disable_linking = enabled
        return self

    def with_disable_bind(
            self,
            enabled: bool = True,
    ) -> "AethericFrameConfiguration":
        """
        Set whether bind/scan entrypoints are disabled and return `self`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            enabled:
                True to refuse bind and scan transactions on this frame.
        """
        self.check_cleaned()
        if not isinstance(enabled, bool):
            raise TypeError("disable_bind must be a bool.")
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify frame configuration after it is frozen.")
            self._disable_bind = enabled
        return self

    def with_disable_conduit_cluster(
            self,
            enabled: bool = True,
    ) -> "AethericFrameConfiguration":
        """
        Set whether conduit-cluster entrypoints are disabled and return `self`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            enabled:
                True to refuse cluster join, leave, and share transactions.
        """
        self.check_cleaned()
        if not isinstance(enabled, bool):
            raise TypeError("disable_conduit_cluster must be a bool.")
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify frame configuration after it is frozen.")
            self._disable_conduit_cluster = enabled
        return self

    def with_disable_transfer_of_ownership(
            self,
            enabled: bool = True,
    ) -> "AethericFrameConfiguration":
        """
        Set whether ownership-transfer entrypoints are disabled and return `self`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            enabled:
                True to refuse ownership-transfer transactions on this frame.
        """
        self.check_cleaned()
        if not isinstance(enabled, bool):
            raise TypeError("disable_transfer_of_ownership must be a bool.")
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify frame configuration after it is frozen.")
            self._disable_transfer_of_ownership = enabled
        return self

    def with_disable_contract_mutation(
            self,
            enabled: bool = True,
    ) -> "AethericFrameConfiguration":
        """
        Set whether direct contract mutation is disabled and return `self`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            enabled:
                True to refuse direct contract add/remove transactions.
        """
        self.check_cleaned()
        if not isinstance(enabled, bool):
            raise TypeError("disable_contract_mutation must be a bool.")
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify frame configuration after it is frozen.")
            self._disable_contract_mutation = enabled
        return self

    def with_max_transaction_wait_time_in_seconds(
            self,
            timeout: float,
    ) -> "AethericFrameConfiguration":
        """
        Set the maximum scope-acquisition wait time and return `self`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            seconds:
                How long a root transaction may wait for conflicting scope claims
                before admission times out. Read LIVE by the mediator, so a restored
                posture governs the running system.
        """
        self.check_cleaned()
        if not isinstance(timeout, (int, float)) or isinstance(timeout, bool):
            raise TypeError(
                "max_transaction_wait_time_in_seconds must be a float or int."
            )
        if timeout <= 0:
            raise ValueError(
                "max_transaction_wait_time_in_seconds must be greater than 0."
            )
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify frame configuration after it is frozen.")
            self._max_transaction_wait_time_in_seconds = float(timeout)
        return self

    def with_defaults(self) -> "AethericFrameConfiguration":
        """
        Reset frame posture to the default automatic/non-AR posture.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.
        """
        self.check_cleaned()
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify frame configuration after it is frozen.")
            self._system_state = SystemState.automatic
            self._ai_native_enabled = False
            self._rift_enabled = False
            self._shared_framewide_spellbook_configuration = False
            # Caching is enabled by default everywhere: the constructor
            # defaults to True and posture resets must not silently disable
            # the system cache.
            self._system_caching_enabled = True
            self._system_cache_root_path = (
                self._build_default_system_cache_root_path()
            )
            self._disable_all_transactions_after_conjure = False
            self._disable_mutations = True
            self._disable_linking = False
            self._disable_bind = False
            self._disable_conduit_cluster = False
            self._disable_transfer_of_ownership = False
            self._disable_contract_mutation = False
            self._max_transaction_wait_time_in_seconds = 30.0
        return self

    @classmethod
    def from_recorded_posture(
            cls,
            twin_payload: Dict[str, Any],
    ) -> Tuple["AethericFrameConfiguration", List[str]]:
        """
        Reload lane: rebuild one frame posture from its recorded twin
        payload.

        Purpose:
            The restore counterpart to the fluent authoring lane. A sealed
            AethericFrameCrystal payload IS the posture truth; present-day
            constructor defaults must never silently substitute for
            recorded values, so every key the record does not carry is
            returned to the caller for explicit reporting.

        Contract:
            - Reads the posture trio from the payload root
              (system_state_name / ai_native_enabled / rift_enabled) and
              the dev-ops surface from "dev_ops_payload" (the
              describe_posture shape the freeze emission captures).
            - system_state_name is HARD-REQUIRED: a posture without a
              recorded state is not a posture, and the reload lane never
              guesses a frame state.
            - Every other absent key falls back to the constructor's
              documented default AND is returned in the missing-key list
              (schema-evolution tolerance, never silent).
            - LOADS AND FREEZES in one motion: the rebuilt posture is
              sealed truth and validates at the internal freeze. The
              standalone freeze carries no origin identity (no twin
              emission); binding it to a frame copies the values into the
              frame-owned posture, whose own freeze carries identity and
              emits.

        Args:
            twin_payload:
                AethericFrameCrystal.describe() shaped payload (JSON-safe,
                the cached-item shape).

        Returns:
            Tuple[AethericFrameConfiguration, List[str]]:
                (the rebuilt FROZEN posture, sorted key names that fell
                back to constructor defaults).

        Raises:
            ValueError:
                If system_state_name is absent, or names no valid
                SystemState member.
        """
        state_name = twin_payload.get("system_state_name")
        if state_name is None:
            raise ValueError(
                "Recorded frame posture payload carries no "
                "system_state_name; the reload lane refuses to guess a "
                "frame state. Re-seal the world or repair the cached "
                "checkpoint payload."
            )
        dev_ops = dict(twin_payload.get("dev_ops_payload", {}))
        missing: List[str] = []
        # Constructor-documented defaults, keyed by their payload source:
        # the posture trio rides the payload root; the dev-ops surface
        # rides the recorded describe_posture map.
        root_defaults: Dict[str, Any] = {
            "ai_native_enabled": False,
            "rift_enabled": False,
        }
        dev_ops_defaults: Dict[str, Any] = {
            "shared_framewide_spellbook_configuration": False,
            "system_caching_enabled": True,
            "system_cache_root_path": None,
            "disable_all_transactions_after_conjure": False,
            "disable_mutations": True,
            "disable_linking": False,
            "disable_bind": False,
            "disable_conduit_cluster": False,
            "disable_transfer_of_ownership": False,
            "disable_contract_mutation": False,
            "max_transaction_wait_time_in_seconds": 30.0,
        }
        resolved: Dict[str, Any] = {}
        for key, default_value in root_defaults.items():
            if key in twin_payload:
                resolved[key] = twin_payload[key]
            else:
                missing.append(key)
                resolved[key] = default_value
        for key, default_value in dev_ops_defaults.items():
            if key in dev_ops:
                resolved[key] = dev_ops[key]
            else:
                missing.append(key)
                resolved[key] = default_value
        cache_root = resolved["system_cache_root_path"]
        posture = cls(
            origin_spellbook_id=None,
            system_state=EnumHelpers.convert_enum_and_check(
                str(state_name), SystemState
            ),
            ai_native_enabled=bool(resolved["ai_native_enabled"]),
            rift_enabled=bool(resolved["rift_enabled"]),
            shared_framewide_spellbook_configuration=bool(
                resolved["shared_framewide_spellbook_configuration"]
            ),
            system_caching_enabled=bool(
                resolved["system_caching_enabled"]
            ),
            system_cache_root_path=(
                str(cache_root) if cache_root is not None else None
            ),
            disable_all_transactions_after_conjure=bool(
                resolved["disable_all_transactions_after_conjure"]
            ),
            disable_mutations=bool(resolved["disable_mutations"]),
            disable_linking=bool(resolved["disable_linking"]),
            disable_bind=bool(resolved["disable_bind"]),
            disable_conduit_cluster=bool(
                resolved["disable_conduit_cluster"]
            ),
            disable_transfer_of_ownership=bool(
                resolved["disable_transfer_of_ownership"]
            ),
            disable_contract_mutation=bool(
                resolved["disable_contract_mutation"]
            ),
            max_transaction_wait_time_in_seconds=float(
                resolved["max_transaction_wait_time_in_seconds"]
            ),
        )
        # Reload seals: load it in, freeze it - the reload lane never
        # hands back a mutable posture. No origin identity here, so no
        # twin emission; the frame's bind-time freeze carries identity.
        posture.freeze()
        return posture, sorted(missing)

    def dynamic_defaults(self) -> "AethericFrameConfiguration":
        """
        Set the default dynamic frame posture and return `self`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.
        """
        return self.with_defaults().with_system_state(SystemState.dynamic)

    def automatic_defaults(self) -> "AethericFrameConfiguration":
        """
        Set the default automatic frame posture and return `self`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.
        """
        return self.with_defaults().with_system_state(SystemState.automatic)

    @property
    def id(self) -> str:
        """
        Return the stable posture-object id.

        Returns:
            str: Stable configuration id.
        """
        self.check_cleaned()
        with self._lock:
            return self._id

    @property
    def origin_spellbook_id(self) -> Optional[str]:
        """
        Return the Spellbook id that first produced this frame posture.

        Returns:
            Optional[str]: Originating Spellbook id, if known.
        """
        self.check_cleaned()
        with self._lock:
            return self._origin_spellbook_id

    @property
    def system_state(self) -> SystemState:
        """
        Return the frame system state.

        Returns:
            SystemState: Bound frame system state.
        """
        self.check_cleaned()
        with self._lock:
            return self._system_state

    @property
    def ai_native_enabled(self) -> bool:
        """
        Return whether AI-native behavior is enabled for the frame.

        Returns:
            bool: True when AI-native posture is enabled.
        """
        self.check_cleaned()
        with self._lock:
            return self._ai_native_enabled

    @property
    def rift_enabled(self) -> bool:
        """
        Return whether AI-profile publication is enabled for the frame.

        Returns:
            bool: True when AI-profile posture is enabled.
        """
        self.check_cleaned()
        with self._lock:
            return self._rift_enabled

    @property
    def shared_framewide_spellbook_configuration(self) -> bool:
        """
        Return whether the frame posture permits one explicit frame-owned
        shared rich `SpellbookConfiguration`.

        Returns:
            bool: True when frame-wide rich-config sharing is permitted.
        """
        self.check_cleaned()
        with self._lock:
            return self._shared_framewide_spellbook_configuration

    @property
    def system_caching_enabled(self) -> bool:
        """
        Return whether spell runtime caching is enabled for the frame.

        Returns:
            bool: True when frame-level caching is enabled.
        """
        self.check_cleaned()
        with self._lock:
            return self._system_caching_enabled

    @property
    def system_cache_root_path(self) -> Path:
        """
        Return the configured relative cache-root fragment for the frame.

        Returns:
            Path: Package-relative cache root fragment.
        """
        self.check_cleaned()
        with self._lock:
            return self._system_cache_root_path

    def resolve_system_cache_root_path(self) -> Path:
        """
        Resolve the cache-root fragment against the melder package root.

        Contract:
            - The cache always lives under the `melder` package root itself:
              `<site-packages>/melder/<fragment>` for installed runs and
              `src/melder/<fragment>` for source-checkout runs.
            - Never resolves against the caller's working directory, so cache
              placement is independent of where the process is launched from.

        Returns:
            Path: Absolute cache root path under the `melder` package root.
        """
        self.check_cleaned()
        with self._lock:
            fragment = self._system_cache_root_path
        return (
            Path(__file__).resolve().parent.parent.parent / fragment
        ).resolve()

    def resolve_conjure_cache_root_path(self) -> Path:
        """
        Resolve the conjure-cache subsystem root under the shared cache root.

        Contract:
            - The shared cache root (`resolve_system_cache_root_path`) hosts
              one subdirectory per caching subsystem; compiler artifact
              bundles (the conjure cache) live under `__conjure_cache__`.
            - Sibling subsystems own their own fragments (for example the
              crystallizer's `__crystallizer_cache__`); this method never
              returns the shared root itself.

        Returns:
            Path: Absolute conjure-cache root
            (`<melder package root>/__melder_cache__/__conjure_cache__`).
        """
        return self.resolve_system_cache_root_path() / "__conjure_cache__"

    @property
    def disable_all_transactions_after_conjure(self) -> bool:
        """
        Return whether new transactions are disabled after conjure.

        Returns:
            bool: True when post-conjure transactions are disabled.
        """
        self.check_cleaned()
        with self._lock:
            return self._disable_all_transactions_after_conjure

    @property
    def disable_mutations(self) -> bool:
        """
        Return whether mutation entrypoints are disabled.

        Returns:
            bool: True when mutation entrypoints are disabled.
        """
        self.check_cleaned()
        with self._lock:
            return self._disable_mutations

    @property
    def disable_linking(self) -> bool:
        """
        Return whether linking entrypoints are disabled.

        Returns:
            bool: True when linking entrypoints are disabled.
        """
        self.check_cleaned()
        with self._lock:
            return self._disable_linking

    @property
    def disable_bind(self) -> bool:
        """
        Return whether bind/scan entrypoints are disabled.

        Returns:
            bool: True when bind/scan entrypoints are disabled.
        """
        self.check_cleaned()
        with self._lock:
            return self._disable_bind

    @property
    def disable_conduit_cluster(self) -> bool:
        """
        Return whether conduit-cluster entrypoints are disabled.

        Returns:
            bool: True when conduit-cluster entrypoints are disabled.
        """
        self.check_cleaned()
        with self._lock:
            return self._disable_conduit_cluster

    @property
    def disable_transfer_of_ownership(self) -> bool:
        """
        Return whether ownership-transfer entrypoints are disabled.

        Returns:
            bool: True when ownership-transfer entrypoints are disabled.
        """
        self.check_cleaned()
        with self._lock:
            return self._disable_transfer_of_ownership

    @property
    def disable_contract_mutation(self) -> bool:
        """
        Return whether direct contract mutation is disabled.

        Returns:
            bool: True when contract mutation is disabled.
        """
        self.check_cleaned()
        with self._lock:
            return self._disable_contract_mutation

    @property
    def max_transaction_wait_time_in_seconds(self) -> float:
        """
        Return the maximum scope-acquisition wait time in seconds.

        Returns:
            float: Seconds a root transaction may wait for conflicting scope claims
                before admission times out. Read live by the transaction mediator.
        """
        self.check_cleaned()
        with self._lock:
            return self._max_transaction_wait_time_in_seconds

    def matches_posture(
            self,
            other: object,
    ) -> bool:
        """
        Compare this posture against another frame-level posture object.

        Contract:
            - Compares only the frame-posture fields:
              `system_state`, `ai_native_enabled`, `rift_enabled`, and
              `shared_framewide_spellbook_configuration`.
            - Ignores provenance metadata such as `origin_spellbook_id`.
            - Returns False when `other` is None.

        Args:
            other:
                Other frame posture object to compare.

        Returns:
            bool: True when the AR-relevant posture values are identical.
        """
        self.check_cleaned()
        if other is None:
            return False
        if not isinstance(other, AethericFrameConfiguration):
            return False
        with SafeGuard(self._lock, other._lock):
            return (
                self._system_state == other._system_state
                and self._ai_native_enabled == other._ai_native_enabled
                and self._rift_enabled == other._rift_enabled
                and self._shared_framewide_spellbook_configuration
                == other._shared_framewide_spellbook_configuration
                and self._system_caching_enabled
                == other._system_caching_enabled
                and self._system_cache_root_path
                == other._system_cache_root_path
                and self._disable_all_transactions_after_conjure
                == other._disable_all_transactions_after_conjure
                and self._disable_mutations == other._disable_mutations
                and self._disable_linking == other._disable_linking
                and self._disable_bind == other._disable_bind
                and self._disable_conduit_cluster
                == other._disable_conduit_cluster
                and self._disable_transfer_of_ownership
                == other._disable_transfer_of_ownership
                and self._disable_contract_mutation
                == other._disable_contract_mutation
                and self._max_transaction_wait_time_in_seconds
                == other._max_transaction_wait_time_in_seconds
            )

    def describe_posture(self) -> Dict[str, Any]:
        """
        Return a detached posture description for logging and diagnostics.

        Contract:
            - Returns plain scalar values only.
            - Intended for diagnostics, logging, and conflict reporting rather
              than as a mutable runtime object.

        Returns:
            Dict[str, Any]: Plain posture dictionary.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "origin_spellbook_id": self._origin_spellbook_id,
                "system_state": self._system_state,
                "ai_native_enabled": self._ai_native_enabled,
                "rift_enabled": self._rift_enabled,
                "shared_framewide_spellbook_configuration": (
                    self._shared_framewide_spellbook_configuration
                ),
                "system_caching_enabled": self._system_caching_enabled,
                "system_cache_root_path": self._system_cache_root_path,
                "disable_all_transactions_after_conjure": (
                    self._disable_all_transactions_after_conjure
                ),
                "disable_mutations": self._disable_mutations,
                "disable_linking": self._disable_linking,
                "disable_bind": self._disable_bind,
                "disable_conduit_cluster": self._disable_conduit_cluster,
                "disable_transfer_of_ownership": (
                    self._disable_transfer_of_ownership
                ),
                "disable_contract_mutation": (
                    self._disable_contract_mutation
                ),
                "max_transaction_wait_time_in_seconds": (
                    self._max_transaction_wait_time_in_seconds
                ),
            }
