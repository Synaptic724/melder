import threading
from pathlib import Path
from typing import Any, Dict, Optional, ClassVar, Union



from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.utilities.general_base.cleanable import Cleanable
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
    """

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
        "_queue_competing_root_transactions",
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
            system_caching_enabled: bool = False,
            system_cache_root_path: Optional[Union[str, Path]] = None,
            disable_all_transactions_after_conjure: bool = False,
            disable_mutations: bool = True,
            disable_linking: bool = False,
            disable_bind: bool = False,
            disable_conduit_cluster: bool = False,
            disable_transfer_of_ownership: bool = False,
            disable_contract_mutation: bool = False,
            queue_competing_root_transactions: bool = False,
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
            queue_competing_root_transactions:
                Whether competing root transactions wait in a pending-start
                queue instead of immediately failing.
            max_transaction_wait_time_in_seconds:
                Maximum seconds a competing root transaction may wait in queue.

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
            (
                "queue_competing_root_transactions",
                queue_competing_root_transactions,
            ),
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
        self._queue_competing_root_transactions: bool = (
            queue_competing_root_transactions
        )
        self._max_transaction_wait_time_in_seconds: float = float(
            max_transaction_wait_time_in_seconds
        )

    @staticmethod
    def _build_default_system_cache_root_path() -> Path:
        """
        Build the default package-relative cache root fragment.

        Returns:
            Path: Relative `__melder_cache__` fragment resolved later against
            the installed `melder` package root.
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
            del self._queue_competing_root_transactions
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

    def freeze(self, origin_spellbook_id: Optional[str] = None) -> None:
        """
        Freeze the frame posture so no further mutation is allowed.

        Args:
            origin_spellbook_id: Optional spellbook id to stamp as the posture
                origin if one should be recorded at freeze time.
        """
        self.check_cleaned()
        with self._lock:
            if self._frozen:
                return
            self.validate()
            if origin_spellbook_id is not None:
                self._origin_spellbook_id = origin_spellbook_id
            self._frozen = True

    def with_system_state(
            self,
            system_state: SystemState | str,
    ) -> "AethericFrameConfiguration":
        """
        Set the frame system state before freeze and return `self`.
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
        """
        self.check_cleaned()
        if not isinstance(enabled, bool):
            raise TypeError("disable_contract_mutation must be a bool.")
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify frame configuration after it is frozen.")
            self._disable_contract_mutation = enabled
        return self

    def with_queue_competing_root_transactions(
            self,
            enabled: bool = True,
    ) -> "AethericFrameConfiguration":
        """
        Set whether competing root transactions queue for their turn and return `self`.
        """
        self.check_cleaned()
        if not isinstance(enabled, bool):
            raise TypeError("queue_competing_root_transactions must be a bool.")
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify frame configuration after it is frozen.")
            self._queue_competing_root_transactions = enabled
        return self

    def with_max_transaction_wait_time_in_seconds(
            self,
            timeout: float,
    ) -> "AethericFrameConfiguration":
        """
        Set the maximum queued-root wait time and return `self`.
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
        """
        self.check_cleaned()
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify frame configuration after it is frozen.")
            self._system_state = SystemState.automatic
            self._ai_native_enabled = False
            self._rift_enabled = False
            self._shared_framewide_spellbook_configuration = False
            self._system_caching_enabled = False
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
            self._queue_competing_root_transactions = False
            self._max_transaction_wait_time_in_seconds = 30.0
        return self

    def dynamic_defaults(self) -> "AethericFrameConfiguration":
        """
        Set the default dynamic frame posture and return `self`.
        """
        return self.with_defaults().with_system_state(SystemState.dynamic)

    def automatic_defaults(self) -> "AethericFrameConfiguration":
        """
        Set the default automatic frame posture and return `self`.
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
        Resolve the cache-root fragment against the installed melder package root.

        Returns:
            Path: Absolute cache root path under the installed `melder` package.
        """
        self.check_cleaned()
        with self._lock:
            fragment = self._system_cache_root_path
        return (
            Path(__file__).resolve().parent.parent.parent / fragment
        ).resolve()

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
    def queue_competing_root_transactions(self) -> bool:
        """
        Return whether competing root transactions queue for their turn.
        """
        self.check_cleaned()
        with self._lock:
            return self._queue_competing_root_transactions

    @property
    def max_transaction_wait_time_in_seconds(self) -> float:
        """
        Return the maximum queued-root wait time in seconds.
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
                and self._queue_competing_root_transactions
                == other._queue_competing_root_transactions
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
                "queue_competing_root_transactions": (
                    self._queue_competing_root_transactions
                ),
                "max_transaction_wait_time_in_seconds": (
                    self._max_transaction_wait_time_in_seconds
                ),
            }
