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

        Contract:
            - NEVER RETURNS False. There is exactly one rule - AI-native
              requires dynamic state - and violating it raises. The `bool`
              return is a convention, not a verdict channel; treat this as an
              assertion, not a predicate.
            - Checks CONSISTENCY BETWEEN posture fields, not the validity of
              any single field. Individual values are already validated by the
              `with_*` setter that accepted them.
            - Called automatically by `freeze()`, so callers rarely need it
              directly; call it early only to fail before building a frame.

        Threading:
            Takes `self._lock` for the read, so it sees a coherent posture
            snapshot rather than a half-applied combination.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. Valid to call before or after freeze;
            it never mutates posture.

        Returns:
            bool: True when the current frame posture is valid.

        Raises:
            ValueError: If AI-native posture is enabled while system state is
                not dynamic.
            RuntimeError: If the configuration has already been cleaned.
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

        Purpose:
            Freeze is the SETTLEMENT POINT for a frame's world. Every `with_*`
            builder refuses after it, and conjure treats an unfrozen posture as
            an unsettled world it is allowed to settle.

        Contract:
            - IDEMPOTENT AND SILENT. A second call returns immediately without
              re-validating, re-stamping, or re-emitting. An
              `origin_spellbook_id` passed to a later call is therefore
              DISCARDED, not applied - only the first freeze can stamp origin.
            - VALIDATES BEFORE FREEZING. `validate()` runs inside the lock, so
              an invalid posture raises and the configuration stays UNFROZEN
              and still mutable. Freeze is all-or-nothing.
            - Emission requires ALL of: `origin_frame_name` supplied, system
              state is `dynamic`, and the crystallizer singleton is both
              initialized and activated. An AUTOMATIC frame therefore never
              records a posture crystal, and neither does a pre-boot freeze.
              Passing `origin_frame_name` is what opts into recording.
            - The recorded payload is FLATTENED for durability: primitives and
              None pass through, `SystemState` becomes its `.name`, and
              anything else is coerced with `str(...)`. Nothing structured
              survives into the crystal.

        Threading:
            Takes `self._lock` for the validate-stamp-freeze step only. The
            crystallizer emission runs OUTSIDE the lock deliberately, so the
            frame is already observably frozen while the record is written and
            a slow recorder cannot stall posture readers.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`. The local crystallizer handle is
            dropped explicitly once emission completes so this call does not
            extend the singleton's reachability.

        Args:
            origin_spellbook_id: Optional spellbook id to stamp as the posture
                origin if one should be recorded at freeze time. Applied only
                on the first freeze.
            origin_frame_name: Frame name to record against. Supplying it is
                what enables crystallizer emission; leaving it None freezes
                silently without recording.

        Returns:
            None.

        Raises:
            ValueError: Propagated from `validate()` when the posture is
                internally inconsistent (AI-native without dynamic state).
            RuntimeError: If the configuration has already been cleaned.
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

        Contract:
            - MUTATES THIS OBJECT and returns `self`. Despite the fluent shape,
              this is not a builder that yields variants: `base.with_...()`
              changes `base`. Two frames that must differ need two
              configuration objects.
            - This is the single most consequential posture field. `dynamic`
              gates linking, severing, transfer of ownership, and
              lesser-to-normal upgrade, and it is also what allows bind/scan to
              continue AFTER conjure - an automatic frame refuses post-conjure
              bind-family entry outright.
            - Accepts the enum or its string name; conversion is checked, so an
              unrecognized name raises rather than silently defaulting.
            - Refused after freeze.

        Threading:
            Conversion and assignment both happen under `self._lock`, so a
            failed conversion cannot leave a half-set state.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            system_state:
                `SystemState.automatic` or `SystemState.dynamic`. Dynamic is
                required for linking, severing, transfer, and lesser-to-normal upgrade.

        Raises:
            RuntimeError: If the configuration is frozen, or already cleaned.
            ValueError: If `system_state` is not a valid `SystemState`.
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

        Contract:
            - REQUIRES DYNAMIC STATE, and the requirement is enforced at
              FREEZE, not here. Setting this on an automatic frame succeeds
              silently and then makes `freeze()` raise `ValueError` - it is the
              single rule `validate()` checks. Pair it with
              `with_system_state(SystemState.dynamic)`.
            - Order does not matter: the two setters can be called in either
              sequence because the consistency check happens at freeze time.
            - MUTATES THIS OBJECT and returns `self`; not a copy. Reset to
              False by `with_defaults()`.
            - Refused after freeze.

        Threading:
            Assignment under `self._lock`; type-checked before the lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            enabled:
                Whether the frame permits AI-native runtime behaviour.

        Raises:
            TypeError: If `enabled` is not a bool.
            RuntimeError: If the configuration is frozen, or already cleaned.
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

        Contract:
            - This is the frame's OPT-IN to being observable. A rift cannot
              attach to a frame that has not enabled it, so leaving this False
              keeps the frame invisible to the AR/viewer surface entirely.
            - Unlike AI-native, this carries NO dynamic requirement - an
              automatic frame may be rift-visible, and `validate()` does not
              check it.
            - MUTATES THIS OBJECT and returns `self`; not a copy. Reset to
              False by `with_defaults()`.
            - Refused after freeze, so a frame's observability is fixed for its
              whole life once it settles.

        Threading:
            Assignment under `self._lock`; type-checked before the lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            enabled:
                Whether Rifts may attach to this frame. Static AR attachment
                requires this to be True.

        Raises:
            TypeError: If `enabled` is not a bool.
            RuntimeError: If the configuration is frozen, or already cleaned.
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

        Contract:
            - Turns spellbook configuration from PER-BOOK into PER-FRAME. With
              this set, the frame owns one rich `SpellbookConfiguration` and
              later books ADOPT that object by reference rather than building
              their own - so a change made through one book is visible to every
              other book on the frame.
            - Consistent with `Spellbook.create_new_preset_spellbook()`, which
              already shares the configuration object rather than copying it;
              this flag is what makes that sharing frame-wide policy instead of
              a per-upgrade detail.
            - Carries no dynamic requirement.
            - MUTATES THIS OBJECT and returns `self`; not a copy. Reset to
              False by `with_defaults()`.
            - Refused after freeze.

        Threading:
            Assignment under `self._lock`; type-checked before the lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            enabled:
                Whether the frame may own one shared rich SpellbookConfiguration
                that later books adopt instead of creating their own.

        Raises:
            TypeError: If `enabled` is not a bool.
            RuntimeError: If the configuration is frozen, or already cleaned.
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

        Contract:
            - DEFAULTS ON, and stays on across resets. `with_defaults()`
              deliberately returns this to True rather than clearing it, so a
              posture reset can never silently disable the system cache. If you
              want caching off you must set it off AFTER any reset.
            - Disabling affects cache use for this frame only; it does not
              disable the crystallizer itself, which still records posture and
              lifecycle crystals.
            - Carries no dynamic requirement.
            - MUTATES THIS OBJECT and returns `self`; not a copy.
            - Refused after freeze.

        Threading:
            Assignment under `self._lock`; type-checked before the lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            enabled:
                Whether the crystallizer cache is active for this frame.

        Raises:
            TypeError: If `enabled` is not a bool.
            RuntimeError: If the configuration is frozen, or already cleaned.
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

        Contract:
            - MUST BE RELATIVE. An absolute path raises `ValueError`. The
              fragment is resolved later against the MELDER PACKAGE ROOT -
              site-packages when installed, `src/melder` in a source checkout -
              so the cache lives with the package, NOT under the working
              directory. You cannot redirect it outside the package with this
              setter.
            - Passing `None` restores the default `__melder_cache__` fragment,
              even though the annotation reads `Union[str, Path]`. The None
              path is supported by the normalizer.
            - Normalization and validation run BEFORE the lock is taken, so a
              rejected path never touches posture state.
            - MUTATES THIS OBJECT and returns `self`; not a copy. Note that a
              later `with_defaults()` silently RECOMPUTES this back to the
              default and discards whatever was set here.
            - Refused after freeze.

        Threading:
            Assignment under `self._lock`; validation outside it.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            root_path:
                Relative directory fragment under which cache profile folders
                are written. None restores the default location.

        Raises:
            TypeError: If `root_path` is not a str or Path.
            ValueError: If `root_path` is absolute.
            RuntimeError: If the configuration is frozen, or already cleaned.
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

        Contract:
            - MUTATES THIS OBJECT and returns `self`; not a copy.
            - MASTER SWITCH, and it is checked BEFORE every per-family flag.
              When set, no per-family flag is consulted at all - bind, link,
              transfer, cluster and mutation are all refused together, so this
              cannot be softened by clearing the narrower toggles.
            - POST-CONJURE ONLY. It is inert before conjure, so a frame with
              this set can still be fully configured and bound; it seals at the
              moment the frame goes live. That is what makes it the
              build-then-lock switch rather than a build-time restriction.
            - Unlike the per-family toggles, this bites on a DYNAMIC frame too.
              It is the only disable that meaningfully restricts an otherwise
              fully dynamic world.
            - Refused after freeze.

        Threading:
            Assignment under `self._lock`; type-checked before the lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            enabled:
                True to refuse every new change-control transaction once the
                frame is live. The hardest of the disable_* gates.

        Raises:
            TypeError: If `enabled` is not a bool.
            RuntimeError: If the configuration is frozen, or already cleaned.
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

        Contract:
            - MUTATES THIS OBJECT and returns `self`; not a copy.
            - Blocks the `MUTATION` transaction family.
            - DEFAULTS TO DISABLED. `with_defaults()` sets this True while
              every other `disable_*` flag resets to False, so mutation is the
              one capability that is opt-IN. Calling
              `with_disable_mutations(False)` is how you enable it, which reads
              like a double negative but is the actual switch.
            - Only subtracts from a DYNAMIC frame; mutation already requires
              dynamic, so on an automatic frame it is refused regardless.
            - Refused after freeze.

        Threading:
            Assignment under `self._lock`; type-checked before the lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            enabled:
                True to refuse mutation entrypoints on this frame.

        Raises:
            TypeError: If `enabled` is not a bool.
            RuntimeError: If the configuration is frozen, or already cleaned.
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

        Contract:
            - MUTATES THIS OBJECT and returns `self`; not a copy.
            - Blocks the `LINK` transaction only. SEVER IS NOT BLOCKED -
              `UNLINK` carries no posture gate at all, so a conduit can always
              detach even on a frame that refuses new links. Entry is
              restricted; exit stays open, the same asymmetry the frame uses
              for elect/unelect.
            - Only subtracts from a DYNAMIC frame. Linking already requires
              dynamic, so on an automatic frame `LINK` is refused whether or
              not this flag is set; setting it there changes nothing.
            - Refused after freeze.

        Threading:
            Assignment under `self._lock`; type-checked before the lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            enabled:
                True to refuse link transactions on this frame. Sever is
                unaffected.

        Raises:
            TypeError: If `enabled` is not a bool.
            RuntimeError: If the configuration is frozen, or already cleaned.
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

        Contract:
            - MUTATES THIS OBJECT and returns `self`; not a copy.
            - Covers the WHOLE bind family, not just `bind`. Setting this
              refuses `Spellbook.scan(...)` as well, at every point in the
              frame's life - unlike the post-conjure restrictions, which only
              bite once conjure has happened.
            - The argument name reads backwards: `enabled=True` means the
              DISABLE is enabled, i.e. bind and scan are refused.
            - Type-checked BEFORE the lock is taken, so a bad argument raises
              `TypeError` without touching posture state or contending for the
              lock. Truthy non-bools are rejected, not coerced.
            - Refused after freeze.

        Threading:
            Assignment happens under `self._lock`; the type check does not need
            it.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            enabled:
                True to refuse bind and scan transactions on this frame.

        Raises:
            TypeError: If `enabled` is not a bool.
            RuntimeError: If the configuration is frozen, or already cleaned.
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

        Contract:
            - MUTATES THIS OBJECT and returns `self`; not a copy.
            - Blocks the `CLUSTER_LINK` transaction only. LEAVING IS NOT
              BLOCKED - `CLUSTER_LEAVE` carries no posture gate, so a member
              can always exit a cluster on a frame that refuses new joins. A
              conduit can never be trapped in a cluster by posture.
            - Only subtracts from a DYNAMIC frame; clustering already requires
              dynamic, so setting this on an automatic frame changes nothing.
            - Refused after freeze.

        Threading:
            Assignment under `self._lock`; type-checked before the lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            enabled:
                True to refuse cluster join transactions. Leaving a cluster is
                unaffected.

        Raises:
            TypeError: If `enabled` is not a bool.
            RuntimeError: If the configuration is frozen, or already cleaned.
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

        Contract:
            - MUTATES THIS OBJECT and returns `self`; not a copy.
            - Blocks the `TRANSFER_OWNERSHIP` transaction family, which is what
              moves a spell's owning conduit. It does not affect binding,
              linking, or clustering.
            - Only subtracts from a DYNAMIC frame; transfer already requires
              dynamic, so setting this on an automatic frame changes nothing.
            - Refused after freeze.

        Threading:
            Assignment under `self._lock`; type-checked before the lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            enabled:
                True to refuse ownership-transfer transactions on this frame.

        Raises:
            TypeError: If `enabled` is not a bool.
            RuntimeError: If the configuration is frozen, or already cleaned.
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

        Contract:
            - Gates DIRECT contract add/remove. Unlike the link, transfer,
              cluster and mutation toggles, this flag is NOT consulted by
              `Conduit._transaction_blocked_for_current_posture` - contract
              mutation is refused on the contract path itself, so the refusal
              surfaces from the contract call rather than from transaction
              admission.
            - Independent of `disable_mutations`: that one gates the MUTATION
              transaction family (spell mutation), this one gates changes to
              conduit contracts. Setting one does not imply the other.
            - MUTATES THIS OBJECT and returns `self`; not a copy. Reset to
              False by `with_defaults()`.
            - Refused after freeze.

        Threading:
            Assignment under `self._lock`; type-checked before the lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            enabled:
                True to refuse direct contract add/remove transactions.

        Raises:
            TypeError: If `enabled` is not a bool.
            RuntimeError: If the configuration is frozen, or already cleaned.
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

        Contract:
            - MUST BE STRICTLY POSITIVE. Zero and negatives raise `ValueError`,
              so there is no "fail immediately" setting and no "wait forever"
              setting; every transaction has a bounded, non-zero admission
              window by construction.
            - BOOLS ARE REJECTED even though `bool` is a subclass of `int`.
              `with_...(True)` raises `TypeError` rather than silently meaning
              one second.
            - Stored as `float` regardless of whether an int was passed.
            - READ LIVE by the transaction mediator rather than captured at
              conjure, so restoring a posture changes the timeout of the
              already-running system.
            - Validation runs BEFORE the lock; a rejected value never touches
              posture state.
            - MUTATES THIS OBJECT and returns `self`; not a copy. Reset to 30.0
              by `with_defaults()`.
            - Refused after freeze.

        Threading:
            Assignment under `self._lock`; validation outside it.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Args:
            timeout:
                How long a root transaction may wait for conflicting scope claims
                before admission times out. Read LIVE by the mediator, so a restored
                posture governs the running system.

        Raises:
            TypeError: If `timeout` is not an int or float, or is a bool.
            ValueError: If `timeout` is not greater than 0.
            RuntimeError: If the configuration is frozen, or already cleaned.
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

        Contract:
            - MUTATES THIS OBJECT and returns `self`; it does not produce a
              fresh configuration. Every field is overwritten, so ANY earlier
              `with_*` call on this object is discarded - including a custom
              `system_cache_root_path`, which is recomputed back to the built
              default rather than preserved.
            - Defaults are automatic, non-AR: `system_state=automatic`,
              AI-native off, rift off, no shared frame-wide spellbook
              configuration, transaction wait 30.0s.
            - CACHING IS DEFAULTED ON, not off. A posture reset must never
              silently disable the system cache, so `system_caching_enabled`
              returns to True.
            - MUTATIONS ARE DEFAULTED OFF. `disable_mutations` resets to True
              while every other `disable_*` flag resets to False - mutation is
              the one capability that is opt-in rather than opt-out.
            - Refused after freeze, like every other builder.

        Threading:
            Applies the whole reset under `self._lock`, so no reader observes a
            partially reset posture.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Raises:
            RuntimeError: If the configuration is frozen, or already cleaned.
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

        Contract:
            - DESTRUCTIVE. This is `with_defaults()` followed by
              `with_system_state(dynamic)`, so it RESETS EVERY posture field
              first. Any earlier `with_*` call on this object is discarded,
              including a custom cache root. Call it FIRST when building a
              posture, never last.
            - Leaves mutations DISABLED, because the reset restores
              `disable_mutations=True`. "Dynamic" here means the transaction
              families are available, not that mutation is on - enable that
              explicitly with `with_disable_mutations(False)`.
            - Dynamic is what allows linking, severing, transfer,
              lesser-to-normal upgrade, and post-conjure bind/scan.
            - MUTATES THIS OBJECT and returns `self`; not a copy.
            - Refused after freeze, via the calls it delegates to.

        Threading:
            Not atomic as a whole - it performs two separately locked steps, so
            a concurrent reader can observe the reset defaults before the
            dynamic state lands. Build postures before publishing them.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()` via its delegates.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Raises:
            RuntimeError: If the configuration is frozen, or already cleaned.
        """
        return self.with_defaults().with_system_state(SystemState.dynamic)

    def automatic_defaults(self) -> "AethericFrameConfiguration":
        """
        Set the default automatic frame posture and return `self`.

        Contract:
            - DESTRUCTIVE. This is `with_defaults()` followed by
              `with_system_state(automatic)`, so it RESETS EVERY posture field
              first. Any earlier `with_*` call on this object is discarded.
              Call it FIRST when building a posture, never last.
            - Equivalent to `with_defaults()` alone, since automatic is already
              the reset state. It exists to state the intent explicitly rather
              than to add behaviour.
            - Automatic already refuses link, transfer, cluster and mutation
              regardless of their individual flags, and refuses bind/scan after
              conjure. Setting the per-family `disable_*` toggles on top of it
              changes nothing.
            - Incompatible with AI-native: enabling that and freezing an
              automatic frame raises from `validate()`.
            - MUTATES THIS OBJECT and returns `self`; not a copy.
            - Refused after freeze, via the calls it delegates to.

        Threading:
            Not atomic as a whole - two separately locked steps.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()` via its delegates.

        Returns:
            AethericFrameConfiguration: This posture object, for fluent chaining.

        Raises:
            RuntimeError: If the configuration is frozen, or already cleaned.
        """
        return self.with_defaults().with_system_state(SystemState.automatic)

    @property
    def id(self) -> str:
        """
        Return the stable posture-object id.

        Contract:
            - Identifies THIS POSTURE OBJECT, not the frame. A frame whose
              posture is rebuilt or restored carries a different id.
            - Assigned at construction and stable for the object's life;
              freezing does not change it.
            - Reflects the settled posture once the frame is frozen; posture cannot
              change after freeze, so a post-freeze read is stable for the frame's
              life.

        Threading:
            Reads under `self._lock`, so the value is a coherent snapshot rather
            than a torn read against a concurrent builder call.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`; raises after the posture is cleaned
            rather than returning a stale value.

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

        Contract:
            - Stamped by the FIRST `freeze()` only. Because freeze is idempotent
              and silent, an `origin_spellbook_id` passed to any later freeze is
              discarded, so this value records who SETTLED the world - not who
              last touched it.
            - `None` means the posture was frozen without an origin, or has not
              been frozen at all.
            - Reflects the settled posture once the frame is frozen; posture cannot
              change after freeze, so a post-freeze read is stable for the frame's
              life.

        Threading:
            Reads under `self._lock`, so the value is a coherent snapshot rather
            than a torn read against a concurrent builder call.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`; raises after the posture is cleaned
            rather than returning a stale value.

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

        Contract:
            - The master capability switch. On `automatic`, the LINK, TRANSFER,
              CLUSTER and MUTATION transaction families are refused regardless of
              their individual `disable_*` flags, and bind/scan are refused once
              the frame has conjured.
            - On `dynamic`, those families are available and the per-family
              `disable_*` flags become the thing that actually decides.
            - Reflects the settled posture once the frame is frozen; posture cannot
              change after freeze, so a post-freeze read is stable for the frame's
              life.

        Threading:
            Reads under `self._lock`, so the value is a coherent snapshot rather
            than a torn read against a concurrent builder call.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`; raises after the posture is cleaned
            rather than returning a stale value.

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

        Contract:
            - Only ever True together with `dynamic` state: the pairing is
              enforced at FREEZE by `validate()`, not when the flag is set, so an
              inconsistent combination is observable here right up until freeze
              raises.
            - Reflects the settled posture once the frame is frozen; posture cannot
              change after freeze, so a post-freeze read is stable for the frame's
              life.

        Threading:
            Reads under `self._lock`, so the value is a coherent snapshot rather
            than a torn read against a concurrent builder call.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`; raises after the posture is cleaned
            rather than returning a stale value.

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

        Contract:
            - The frame's opt-in to being OBSERVABLE. A rift cannot attach to a
              frame with this False, which keeps the frame invisible to the
              AR/viewer surface entirely.
            - Carries no dynamic requirement; an automatic frame may be
              rift-visible.
            - Reflects the settled posture once the frame is frozen; posture cannot
              change after freeze, so a post-freeze read is stable for the frame's
              life.

        Threading:
            Reads under `self._lock`, so the value is a coherent snapshot rather
            than a torn read against a concurrent builder call.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`; raises after the posture is cleaned
            rather than returning a stale value.

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

        Contract:
            - True means spellbook configuration is PER-FRAME rather than
              per-book: the frame owns one rich configuration and later books
              adopt that object BY REFERENCE, so a change through one book is
              visible to every other book on the frame.
            - Reflects the settled posture once the frame is frozen; posture cannot
              change after freeze, so a post-freeze read is stable for the frame's
              life.

        Threading:
            Reads under `self._lock`, so the value is a coherent snapshot rather
            than a torn read against a concurrent builder call.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`; raises after the posture is cleaned
            rather than returning a stale value.

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

        Contract:
            - Defaults True and SURVIVES `with_defaults()`, which deliberately
              restores it rather than clearing it - a posture reset must never
              silently disable the system cache.
            - False disables cache use for this frame only; the crystallizer
              still records posture and lifecycle crystals.
            - Reflects the settled posture once the frame is frozen; posture cannot
              change after freeze, so a post-freeze read is stable for the frame's
              life.

        Threading:
            Reads under `self._lock`, so the value is a coherent snapshot rather
            than a torn read against a concurrent builder call.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`; raises after the posture is cleaned
            rather than returning a stale value.

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

        Contract:
            - A RELATIVE fragment, resolved against the melder PACKAGE root -
              site-packages when installed, `src/melder` in a source checkout.
              It is not relative to the working directory, and absolute paths
              are rejected by the setter.
            - Defaults to `__melder_cache__`, and `with_defaults()` recomputes
              that default rather than preserving a custom fragment.
            - Reflects the settled posture once the frame is frozen; posture cannot
              change after freeze, so a post-freeze read is stable for the frame's
              life.

        Threading:
            Reads under `self._lock`, so the value is a coherent snapshot rather
            than a torn read against a concurrent builder call.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`; raises after the posture is cleaned
            rather than returning a stale value.

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

        Contract:
            - The master disable, checked BEFORE every per-family flag: when True
              no narrower flag is consulted at all.
            - INERT BEFORE CONJURE. A frame carrying this can still be fully
              configured and bound; it seals only once the frame goes live.
            - The only disable that meaningfully restricts a fully dynamic
              world.
            - Reflects the settled posture once the frame is frozen; posture cannot
              change after freeze, so a post-freeze read is stable for the frame's
              life.

        Threading:
            Reads under `self._lock`, so the value is a coherent snapshot rather
            than a torn read against a concurrent builder call.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`; raises after the posture is cleaned
            rather than returning a stale value.

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

        Contract:
            - Gates the MUTATION transaction family (spell mutation), NOT contract
              mutation - that is `disable_contract_mutation`.
            - DEFAULTS TRUE. It is the one capability that is opt-IN, so this
              reads True on a freshly defaulted posture.
            - Redundant on an automatic frame, which refuses mutation anyway.
            - Reflects the settled posture once the frame is frozen; posture cannot
              change after freeze, so a post-freeze read is stable for the frame's
              life.

        Threading:
            Reads under `self._lock`, so the value is a coherent snapshot rather
            than a torn read against a concurrent builder call.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`; raises after the posture is cleaned
            rather than returning a stale value.

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

        Contract:
            - Gates the LINK transaction ONLY. Sever is never posture-gated -
              `UNLINK` has no gate anywhere - so a conduit can always detach from
              a frame that refuses new links.
            - Redundant on an automatic frame, which refuses linking anyway.
            - Reflects the settled posture once the frame is frozen; posture cannot
              change after freeze, so a post-freeze read is stable for the frame's
              life.

        Threading:
            Reads under `self._lock`, so the value is a coherent snapshot rather
            than a torn read against a concurrent builder call.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`; raises after the posture is cleaned
            rather than returning a stale value.

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

        Contract:
            - Gates bind AND scan, at EVERY point in the frame's life. Unlike the
              post-conjure restrictions, this one bites before conjure too.
            - Checked ahead of the post-conjure and dynamic checks, so it is the
              earliest bind-family refusal.
            - Reflects the settled posture once the frame is frozen; posture cannot
              change after freeze, so a post-freeze read is stable for the frame's
              life.

        Threading:
            Reads under `self._lock`, so the value is a coherent snapshot rather
            than a torn read against a concurrent builder call.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`; raises after the posture is cleaned
            rather than returning a stale value.

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

        Contract:
            - Gates the CLUSTER_LINK transaction ONLY. Leaving is never
              posture-gated - `CLUSTER_LEAVE` has no gate - so a member can always
              exit and can never be trapped in a cluster by posture.
            - Redundant on an automatic frame, which refuses clustering anyway.
            - Reflects the settled posture once the frame is frozen; posture cannot
              change after freeze, so a post-freeze read is stable for the frame's
              life.

        Threading:
            Reads under `self._lock`, so the value is a coherent snapshot rather
            than a torn read against a concurrent builder call.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`; raises after the posture is cleaned
            rather than returning a stale value.

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

        Contract:
            - Gates the TRANSFER_OWNERSHIP transaction family, which moves a
              spell's owning conduit. Binding, linking and clustering are
              unaffected.
            - Redundant on an automatic frame, which refuses transfer anyway.
            - Reflects the settled posture once the frame is frozen; posture cannot
              change after freeze, so a post-freeze read is stable for the frame's
              life.

        Threading:
            Reads under `self._lock`, so the value is a coherent snapshot rather
            than a torn read against a concurrent builder call.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`; raises after the posture is cleaned
            rather than returning a stale value.

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

        Contract:
            - NOT consulted by the conduit transaction gate, unlike the other
              `disable_*` flags. Contract mutation is refused on the contract path
              itself, so the refusal surfaces from the contract call rather than
              from transaction admission.
            - Independent of `disable_mutations`; setting one does not imply the
              other.
            - Reflects the settled posture once the frame is frozen; posture cannot
              change after freeze, so a post-freeze read is stable for the frame's
              life.

        Threading:
            Reads under `self._lock`, so the value is a coherent snapshot rather
            than a torn read against a concurrent builder call.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`; raises after the posture is cleaned
            rather than returning a stale value.

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

        Contract:
            - Always strictly positive - the setter rejects zero and negatives - so
              there is no immediate-fail and no wait-forever setting.
            - Read LIVE by the transaction mediator rather than captured at
              conjure, so a restored posture governs the running system.
            - Reflects the settled posture once the frame is frozen; posture cannot
              change after freeze, so a post-freeze read is stable for the frame's
              life.

        Threading:
            Reads under `self._lock`, so the value is a coherent snapshot rather
            than a torn read against a concurrent builder call.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`; raises after the posture is cleaned
            rather than returning a stale value.

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
