import inspect
import threading
from contextlib import contextmanager
from types import TracebackType
from typing import TYPE_CHECKING, List, Any, Tuple, Dict, Iterable, Generator, Type, Optional

from mypy_extensions import mypyc_attr

# Melder Imports
from melder.utilities.synchronization.safeguard import SafeGuard
from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import ContractTypes
from melder.utilities.general_base.cleanable import Cleanable
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.utilities.helpers.general_helpers import EnumHelpers
from melder.utilities.interfaces.iconduit import IConduit
from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
from melder.aether.spellbook.spell import Spell
if TYPE_CHECKING:
    from melder.aether.aetheric_frame.conduit_cloud import ConduitCloud
from melder.utilities.logger.safe_logger import SafeLogger
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.contract.contract import Detail, Contract
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

# TODO: Ensure that links properly connect to the spell and its dependencies not just the spell itself.
# TODO: If a specific policy is set such as blacklist or whitelist, ensure that the spellbook the entire spellbook is managed properly.
# TODO: Please ensure that locking dynamics properly ensure state management between contracts and to use SafeGuard where we need to in order to ensure we grab all the locks to properly manage state

#region ConduitWard
@mypyc_attr(native_class=True)
class ConduitWard(Cleanable):
    """
    Control-plane for a single Conduit: contracts, index, and policy.

    ConduitWard is the **relationship manager** for its owning Conduit. It never
    builds spells itself; instead it coordinates how this conduit relates to
    others and to its own children.

    What it owns
    ------------
    - Contract graph: symmetric links to peer conduits, each represented by a
      `Contract` with per-ward `Detail` maps (spell index + permission).
    - Lineage tree: parent pointer and the set of **lesser conduits** spawned
      by this conduit (pure ownership; no contract semantics here).
    - Root pointer: the **normal conduit** at the top of this lineage tree.
    - Policy state: the active `Policies` enum guiding dynamic/whitelist/block
      behaviors and eligibility to form contracts.

    Core indices (all ward-local)
    -----------------------------
    - `_initiated_index`: outbound links (target_conduit_id -> contract_id).
    - `_received_index`: inbound links (source_conduit_id -> contract_id).
    - `_contracts`: contract_id -> Contract object (symmetric, shared).
    - `_lesser_conduits`: child conduit_id -> Conduit (lineage only).

    Lifecycle
    ---------
    - Link: `_link` / `_create_new_contract` build symmetric contracts and wire
      Spellbook contract buckets on both sides.
    - Sever: `_remove_contract` (via `_sever_link` or bulk `_sever_all_linked_conduits`)
      tears down Spellbook contracted maps and cleans the Contract.
    - Lesser management: `_link_lesser_conduit` attaches children; cleanup tears
      them down best-effort.
    - Cleanup: idempotent, best-effort; severs peer links, cleans lesser tree,
      clears indices, nulls references.

    Threading
    ---------
    - Uses an internal RLock for ward-level critical sections.
    - Contract creation uses sorted lock ordering between wards to avoid deadlock.
    - `_remove_contract` assumes the caller serialized access (e.g., via `_sever_link`).

    Ownership boundaries
    --------------------
    - Spellbook state is updated only through ward helpers (e.g., `_create_link_contract`,
      `_sever_link_contract`) so contract teardown stays consistent with spell maps.
    - Aether/frames are not touched directly; ward concerns are strictly conduit-scope.
    """
    __melder_internal__ = _mrg.sentinel
    def __init__(
            self,
            conduit: IConduit,
            dynamic: bool,
            conduit_type: ConduitState,
            policy: Policies,
            aetheric_frame: AethericFrame,
    ):
        """
        Initialize the ward for one conduit.

        Contract:
            - Binds the ward permanently to one owning conduit id/display.
            - Seeds contract indices, lineage pointers, and policy state for
              that conduit.
            - Resolves the initial policy through `_set_initial_policy(...)`
              so the ward starts from one validated policy value.
            - Does not create any peer contracts or lineage links by itself;
              those are established later through explicit ward operations.

        Args:
            conduit:
                Owning conduit whose links, lineage, and policy this ward
                manages.
            dynamic:
                Whether dynamic link/contract behavior is enabled for this
                conduit.
            conduit_type:
                Current conduit lifecycle state (`normal` or `lesser`).
            policy:
                Initial ward policy to apply.
            aetheric_frame:
                Live frame object used to derive the same-frame cloud lookup
                surface for this ward.
        """
        super().__init__()
        self._lock: threading.RLock  = threading.RLock()

        ## Conduit Ward properties
        self._conduit: IConduit = conduit
        self._conduit_cloud: ConduitCloud = aetheric_frame._conduit_cloud
        self._logger: SafeLogger = conduit._logger
        self._dynamic: bool = dynamic
        self._conduit_type: ConduitState = conduit_type
        self._id = conduit._id
        self._display_name: str = self.__class__.__name__
        self._log_groups = ["spell_management", "spells"]
        self._log_sysgroups = ["conduit"]

        self._policy_set: bool = False
        # Contracts between conduits
        self._initiated_index: Dict[str, str] = {}  # [Target ConduitID] -> [ContractID]
        self._received_index: Dict[str, str] = {}  # [Source ConduitID] -> [ContractID]

        self._contracts: Dict[str, Contract] = {} # [ContractID] -> Contract

        # Lineage Links
        self._parent_conduit: IConduit | None = None
        self._root_conduit: IConduit | None = (
            conduit if conduit_type == ConduitState.normal else None
        )
        self._lesser_conduits: Dict[str, IConduit] = {} # [Lesser ConduitID] -> Lesser Conduit

        try:
            self._policy = self._set_initial_policy(policy)
        except Exception as e:
            self._logger.error(
                f"ConduitWard init failed: {e}",
                method_name="__init__", exc_info=True,
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise

    #region Cleanup
    def cleanup(self) -> None:
        """
        Public API

        Idempotently tear down this ward, its contracts, and lesser lineage.

        Behaviour:
          - Best-effort sever all peer contracts (uses `_remove_contract`, which updates Spellbook maps).
          - Cleanup all lesser conduits and clear lineage references.
          - Null internal state and mark cleaned. Logger metadata is nulled last.

        Returns:
            None
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return

            # Best-effort sever peer contracts (updates Spellbook links)
            self._clean_up_links()

            # Clean up lesser conduits
            self._clean_up_lesser_conduits_links()

            # Clear lineage/contract state
            self._lesser_conduits.clear()
            self._contracts.clear()
            self._initiated_index.clear()
            self._received_index.clear()
            self._conduit_type = self._conduit_type.cleaned
            self._cleaned = True
            self._logger.info(
                "cleanup complete",
                method_name="cleanup",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            del self._parent_conduit
            del self._root_conduit
            del self._policy
            del self._conduit
            del self._conduit_cloud
            del self._dynamic
            
            # Null logger metadata last (outside lock)
            if  hasattr(self._logger, "cleanup"):
                self._logger.cleanup()
            del self._logger


    def _clean_up_lesser_conduits_links(self) -> None:
        """
        Internal

        Recursively clean up and detach all lesser conduits (children).

        Best-effort: errors from child cleanup are logged and do not stop siblings.

        Returns:
            None
        """
        if not self._lesser_conduits:
            return

        for lesser_conduit in list(self._lesser_conduits.values()):
            try:
                lesser_conduit.cleanup()
            except Exception as e:
                self._logger.error(
                    f"cleanup lesser link failed: {e}",
                    method_name="_clean_up_lesser_conduits_links", exc_info=True,
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
        self._lesser_conduits.clear()

    def _clean_up_links(self) -> None:
        """
        Internal

        Best-effort sever of all active external contracts and links.

        Delegates to `_sever_all_linked_conduits`, which handles Spellbook
        contract teardown. No-op if already cleaned.

        Returns:
            None
        """
        self._sever_all_linked_conduits()


    def cleanup_all_lesser_conduits(self) -> None:
        """
        Public API

        Cleans up all lesser conduits (children) linked to this conduit.

        This is typically used when the parent conduit is undergoing a state change,
        like an upgrade to a normal state, or as part of a controlled shutdown.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        with self._lock:
            for conduit in self._lesser_conduits.values():
                try:
                    conduit.cleanup()
                except Exception as e:
                    self._logger.error(
                        f"lesser cleanup failed: {e}",
                        method_name="cleanup_all_lesser_conduits", exc_info=True,
                        owner_id=self._id, owner_display=self._display_name,
                        mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                    )
            self._lesser_conduits.clear()
        self._logger.info(
            "cleanup_all_lesser_conduits complete",
            method_name="cleanup_all_lesser_conduits",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
    #endregion Cleanup

    #region Context Manager
    def __enter__(self) -> ConduitWard:
        """
        Acquire the ward lock and return this ward.

        Contract:
            This is a thin lock-guard convenience only; it does not create any
            transaction or change-control scope on its own.
        """
        self._lock.acquire()
        return self

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType],
    ) -> None:
        """
        Release the ward lock acquired by `__enter__`.

        Contract:
            Any exception from the wrapped block is allowed to propagate; this
            method only handles lock release.
        """
        self._lock.release()

    #endregion Context Manager
    #region Properties
    @property
    def root_conduit(self) -> Optional[IConduit]:
        """
        Return the root (normal) conduit for this lineage.

        For normal conduits, this is the conduit itself. For lesser conduits,
        this is the owning root conduit that defines the root scope.
        """
        self.check_cleaned()
        root_conduit = self._root_conduit
        if root_conduit is None:
            raise RuntimeError("Root conduit is not set for this lineage.")
        if root_conduit._conduit_state != ConduitState.normal:
            raise RuntimeError("Root conduit must be a normal conduit.")
        return root_conduit
    
    #endregion Properties
    #region Change Control
    def begin_transaction(
            self,
            transaction_type: ChangeTransactionType | str,
            *,
            conduit_ids: Optional[Iterable[str]] = None,
            conduits: Optional[Iterable[IConduit]] = None,
            scope_keys: Optional[Iterable[str]] = None,
            scope_hashes: Optional[Iterable[str]] = None,
            binding_keys: Optional[Iterable[Tuple[str, str]]] = None,
            contract_keys: Optional[Iterable[Tuple[str, str, str]]] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Public API

        Begin a change-control transaction through the owning Conduit.

        Purpose:
            Provide a ward-level facade for change-control transactions used by
            link/contract operations.
        Contract:
            - Delegates to the owning Conduit transaction facade.
            - Raises if the conduit is not in a normal state.
        Args:
            transaction_type:
                Transaction type enum or string value (e.g. "link", "bind").
            conduit_ids:
                Optional list of conduits participating in non-link requests.
            conduits:
                Optional list of conduit objects participating in the request.
            scope_keys:
                Optional normalized scope keys for conflict checks.
            scope_hashes:
                Optional normalized scope hashes for conflict checks.
            binding_keys:
                Optional binding keys affected by the request.
            contract_keys:
                Optional contract keys affected by the request.
            metadata:
                Optional structured metadata for diagnostics.
        Returns:
            None.
        Raises:
            RuntimeError: If the ConduitWard is cleaned.
            RuntimeError: If the owning Conduit is not normal.
            RuntimeError: If change-control admission is denied.
            ValueError: If transaction_type is invalid.
            TypeError: If transaction_type has an invalid type.
        """
        self.check_cleaned()
        self._conduit.begin_transaction(
            transaction_type,
            conduit_ids=conduit_ids,
            conduits=conduits,
            scope_keys=scope_keys,
            scope_hashes=scope_hashes,
            binding_keys=binding_keys,
            contract_keys=contract_keys,
            metadata=metadata,
        )

    def end_transaction(
            self,
            transaction_type: ChangeTransactionType | str | None = None,
    ) -> None:
        """
        Public API

        End the active change-control transaction through the owning Conduit.

        Purpose:
            Provide a ward-level facade for terminating change-control requests.
        Contract:
            - Delegates to the owning Conduit transaction facade.
        Args:
            transaction_type:
                Optional transaction type assertion for safety checks.
        Returns:
            None.
        Raises:
            RuntimeError: If the ConduitWard is cleaned.
            RuntimeError: If the owning Conduit is not normal.
            RuntimeError: If no change transaction is active.
            RuntimeError: If transaction_type does not match the active request.
            ValueError: If transaction_type is invalid.
            TypeError: If transaction_type has an invalid type.
        """
        self.check_cleaned()
        self._conduit.end_transaction(transaction_type=transaction_type)

    @contextmanager
    def transaction(
            self,
            transaction_type: ChangeTransactionType | str,
            *,
            conduit_ids: Optional[Iterable[str]] = None,
            conduits: Optional[Iterable[IConduit]] = None,
            scope_keys: Optional[Iterable[str]] = None,
            scope_hashes: Optional[Iterable[str]] = None,
            binding_keys: Optional[Iterable[Tuple[str, str]]] = None,
            contract_keys: Optional[Iterable[Tuple[str, str, str]]] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> Generator[ConduitWard, Any, None]:
        """
        Public API

        Context-managed change-control transaction for this ConduitWard.

        Purpose:
            Provide a safe begin/end wrapper for ward-level change transactions.
        Contract:
            - Begins a change-control transaction on entry.
            - Ends the transaction on exit, even if an exception is raised.
        Args:
            transaction_type:
                Transaction type enum or string value (e.g. "link", "bind").
            conduit_ids:
                Optional list of conduits participating in non-link requests.
            conduits:
                Optional list of conduit objects participating in the request.
            scope_keys:
                Optional normalized scope keys for conflict checks.
            scope_hashes:
                Optional normalized scope hashes for conflict checks.
            binding_keys:
                Optional binding keys affected by the request.
            contract_keys:
                Optional contract keys affected by the request.
            metadata:
                Optional structured metadata for diagnostics.
        Returns:
            ConduitWard: The current ConduitWard instance.
        Raises:
            RuntimeError: If the ConduitWard is cleaned.
            RuntimeError: If the owning Conduit is not normal.
            RuntimeError: If change-control admission is denied.
            ValueError: If transaction_type is invalid.
            TypeError: If transaction_type has an invalid type.
        """
        self.begin_transaction(
            transaction_type,
            conduit_ids=conduit_ids,
            conduits=conduits,
            scope_keys=scope_keys,
            scope_hashes=scope_hashes,
            binding_keys=binding_keys,
            contract_keys=contract_keys,
            metadata=metadata,
        )
        try:
            yield self
        finally:
            self.end_transaction(transaction_type=transaction_type)

    #endregion Change Control

    #region Conduit Ward Configuration
    def _convert_to_normal_conduit(self) -> None:
        """
        Internal

        Converts this Conduit from a `lesser` state to a `normal` state.

        This method is called internally during the conduit upgrade process.
        It detaches the parent link and updates the policy state.

        Raises:
            RuntimeError: If the Conduit is not a lesser conduit.
            RuntimeError: If dynamic environment is not enabled.
            RuntimeError: If no parent conduit link is found (unknown error state).
        """
        self.check_cleaned()
        if self._conduit_type != ConduitState.lesser:
            self._logger.error(
                "convert_to_normal: not a lesser conduit",
                method_name="_convert_to_normal_conduit",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError("Conduit is not a lesser conduit.")
        with self._lock:
            if not self._dynamic:
                self._logger.error(
                    "convert_to_normal: non-dynamic env",
                    method_name="_convert_to_normal_conduit",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise RuntimeError("Dynamic environment is not enabled. Cannot upgrade to normal conduit.")
            if self._parent_conduit is not None and self._conduit_type == ConduitState.lesser and len(self._lesser_conduits) == 0:
                self._parent_conduit = None
                self._root_conduit = self._conduit
                self._conduit_type = ConduitState.normal
                self._policy = Policies.default
                self._logger.info(
                    "convert_to_normal: success",
                    method_name="_convert_to_normal_conduit",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
            else:
                self._logger.error(
                    "convert_to_normal: missing parent link or children present",
                    method_name="_convert_to_normal_conduit",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise RuntimeError("No parent conduit link found. Cannot convert to normal conduit. Unknown error")


    def _set_initial_policy(self, policy: Policies) -> Optional[Policies]:
        """
        Internal

        Set and freeze the ward's initial policy during construction.

        Args:
            policy (Policies): The desired initial policy.

        Returns:
            Optional[Policies]: The set policy.

        Raises:
            TypeError: If `policy` is not an instance of the `Policies` enum.
            RuntimeError: If the policy has already been set.

        Contract:
            This helper is construction-only. After the initial policy is
            accepted, `_policy_set` prevents a second initialization pass from
            silently replacing the ward's starting policy.
        """
        self.check_cleaned()

        if policy is not None:
            if not isinstance(policy, Policies):
                self._logger.error(
                    f"set_initial_policy: wrong type {type(policy).__name__}",
                    owner_id=self._id, owner_display=self._display_name,
                    method_name="_set_initial_policy",
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise TypeError(f"Expected Policies enum instance, got {type(policy).__name__}")
            self._policy_set = True
            return policy

        with self._lock:
            return Policies.default

    def _set_new_policy(self, policy: str | Policies) -> None:
        """
        Internal

        Sets a new operational policy for this Conduit.

        This is restricted to `normal` conduits in dynamic mode.

        Args:
            policy (str | Policies): The new policy to set.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If dynamic environment is not enabled.
            RuntimeError: If the Conduit is a lesser Conduit.
            RuntimeError: If attempting to set to `block_all` or `whitelist_all` while contracts exist.
        """
        self.check_cleaned()
        if not self._dynamic:
            self._logger.error(
                "set_new_policy: non-dynamic env",
                method_name="_set_new_policy",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError("Dynamic environment is not enabled. Cannot set policy.")
        if self._conduit_type == ConduitState.lesser:
            self._logger.error(
                "set_new_policy: on lesser conduit",
                method_name="_set_new_policy",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError("Cannot set policy on a lesser Conduit. Convert to a normal Conduit first.")

        with self._lock:
            new_policy = EnumHelpers.convert_enum_and_check(policy, Policies)
            if (new_policy == Policies.block_all or new_policy == Policies.whitelist_all) and len(self._contracts) > 0:
                self._logger.error(
                    "set_new_policy: block/whitelist with existing contracts",
                    method_name="_set_new_policy",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise RuntimeError("Cannot set policy to 'block_all' or 'whitelist_all' when there are existing contracts.")
            self._policy = new_policy
            self._logger.info(
                f"set_new_policy -> {self._policy.name}",
                method_name="_set_new_policy",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )

    #endregion Conduit Ward Configuration
    #region Link Management
    def _link(self, target_conduit: IConduit) -> bool:
        """
        Internal

        Attempts to establish a link (contract) with another normal Conduit.

        Args:
            target_conduit (IConduit): The target Conduit to link to.

        Returns:
            bool: True if the contract was established or already exists.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If attempting to link to a lesser conduit.
            RuntimeError: If attempting to link a conduit to itself.
            RuntimeError: If attempting to link to a conduit in a different frame.
            RuntimeError: If dynamic environment is not enabled.
            RuntimeError: If policy forbids initiating outbound links or target forbids inbound links.
        """
        self.check_cleaned()
        if target_conduit._conduit_state == ConduitState.lesser:
            self._logger.error(
                "link: target is lesser conduit",
                method_name="_link",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError("Cannot link to a lesser conduit. Use _link_lesser_conduit instead.")
        if target_conduit._id == self._id:
            self._logger.error(
                "link: self-link attempt",
                method_name="_link",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError("Cannot link a conduit to itself.")
        if self._conduit._aetheric_frame_name != target_conduit._aetheric_frame_name:
            self._logger.error(
                "link: target conduit is in a different frame",
                method_name="_link",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError(
                "Cannot link conduits across different AethericFrames: "
                "{0} != {1}".format(
                    self._conduit._aetheric_frame_name,
                    target_conduit._aetheric_frame_name,
                )
            )
        if not self._dynamic:
            self._logger.error(
                "link: non-dynamic env",
                method_name="_link",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError("Dynamic environment is not enabled. Cannot link conduits.")

        # Policy gating for outbound/inbound directions
        if self._policy == Policies.inbound_only:
            self._logger.error(
                "link: outbound link requested while policy=inbound_only",
                method_name="_link",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError("This conduit is inbound_only and cannot initiate outbound links.")

        target_ward = target_conduit._conduit_ward
        if target_ward is not None and target_ward._policy == Policies.outbound_only:
            self._logger.error(
                "link: target rejects inbound links (policy=outbound_only)",
                method_name="_link",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError("Target conduit is outbound_only and rejects inbound link requests.")

        if target_conduit._conduit_state == ConduitState.normal:
            if self._find_contract(target_conduit):
                return True
            return self._create_new_contract(target_conduit)

        self._logger.error(
            "link: target not normal",
            method_name="_link",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        return False


    def _create_new_contract(self, target_conduit: IConduit) -> bool:
        """
        Internal

        Creates a new bidirectional contract (link) with the specified target conduit.

        This method handles simultaneous locking of both wards to prevent deadlocks.

        Args:
            target_conduit (IConduit): The conduit to link with.

        Returns:
            bool: True if the contract was created successfully.
        """
        ward_a = self
        ward_b = target_conduit._conduit_ward
        with SafeGuard(ward_a._lock, ward_b._lock):
            target_id = target_conduit._id
            if self._find_contract(target_conduit):
                return True

            contract = Contract(self, ward_b)
            self._contracts[contract._id] = contract
            ward_b._contracts[contract._id] = contract
            self._initiated_index[target_id] = contract._id
            ward_b._received_index[self._id] = contract._id

            try:
                # Each side needs a contracted-spell bucket keyed by its peer's conduit id.
                self._conduit._spellbook._create_link_contract(target_id)
                ward_b._conduit._spellbook._create_link_contract(self._id)
            except Exception as e:
                self._logger.error(
                    f"spellbook link create failed: {e}",
                    method_name="_create_new_contract", exc_info=True,
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise

            self._logger.info(
                f"create_contract: success id={contract._id} target={target_id}",
                method_name="_create_new_contract",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            return True


    def _find_contract_id(self, target_conduit: IConduit) -> Optional[str]:
        """
        Internal

        Finds a contract ID associated with the specified target conduit.

        Args:
            target_conduit (IConduit): The target conduit to find the contract for.

        Returns:
            Optional[str]: The ID of the found contract or None if not found.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            TypeError: If `target_conduit` is not an `IConduit` instance.
        """
        self.check_cleaned()
        if not isinstance(target_conduit, IConduit):
            self._logger.error(
                f"find_contract_id: target not IConduit ({type(target_conduit).__name__})",
                method_name="_find_contract_id",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise TypeError(f"Expected IConduit instance, got {type(target_conduit).__name__}")
        initiated_contract = self._initiated_index.get(target_conduit._conduit_ward._id, None)
        received_contract = self._received_index.get(target_conduit._conduit_ward._id, None)
        cid = initiated_contract if initiated_contract is not None else received_contract
        return cid

    def _find_contract(self, target_conduit: IConduit) -> Optional[Contract]:
        """
        Internal

        Finds the contract object linked to the given target conduit.

        Args:
            target_conduit (IConduit): The target conduit to find the contract for.

        Returns:
            Optional[Contract]: The contract object if it exists, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            TypeError: If `target_conduit` is not an `IConduit` instance.
        """
        self.check_cleaned()
        if not isinstance(target_conduit, IConduit):
            self._logger.error(
                f"find_contract: target not IConduit ({type(target_conduit).__name__})",
                method_name="_find_contract",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise TypeError(f"Expected IConduit instance, got {type(target_conduit).__name__}")
        peer_id = target_conduit._conduit_ward._id
        contract_id = (
            self._initiated_index.get(peer_id)
            or self._received_index.get(peer_id)
        )
        if contract_id is None:
            return None
        contract = self._contracts.get(contract_id)
        return contract

    def _find_contract_by_id(self, conduit_id: str) -> Optional[Contract]:
        """
        Internal

        Finds a contract by the peer's Conduit ID.

        Args:
            conduit_id (str): The ID of the peer conduit in the contract.

        Returns:
            Optional[Contract]: The found contract object or None if not found.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        check_id = (
            self._initiated_index.get(conduit_id)
            or self._received_index.get(conduit_id)
        )
        if check_id is None:
            return None
        contract = self._contracts.get(check_id)
        return contract

    def _sever_link(self, target_conduit: IConduit) -> bool:
        """
        Internal

        Sever the link (contract) between this Conduit and its target Conduit.

        Args:
            target_conduit (IConduit): The target Conduit to sever the link with.

        Returns:
            bool: True if the link was successfully severed.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If no contract is found to sever.
        """
        self.check_cleaned()
        with SafeGuard(self._lock, target_conduit._conduit_ward._lock):
            if self._find_contract(target_conduit):
                return self._remove_contract(target_conduit)
            self._logger.error(
                "sever_link: no contract found",
                method_name="_sever_link",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError("No contract found to sever with the target conduit.")

    def _remove_contract(self, target_conduit: IConduit) -> bool:
        """
        Internal

        Removes the contract and cleans up internal indices and spellbook links.

        Args:
            target_conduit (IConduit): The conduit whose contract should be removed.

        Returns:
            bool: True if the contract was removed successfully.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        self._check_conduit_id_and_conduit(conduit=target_conduit)

        if (contract := self._find_contract(target_conduit)) is not None:
            with contract._lock:
                id_a = contract._ward_a._id
                id_b = contract._ward_b._id
                try:
                    contract._ward_a._conduit._spellbook._sever_link_contract(id_b)
                    contract._ward_b._conduit._spellbook._sever_link_contract(id_a)
                except Exception as e:
                    self._logger.error(
                        f"remove_contract spellbook sever failed: {e}",
                        method_name="_remove_contract", exc_info=True,
                        owner_id=self._id, owner_display=self._display_name,
                        mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                    )
                    raise

                try:
                    del self._contracts[contract._id]
                    del target_conduit._conduit_ward._contracts[contract._id]
                except Exception as e:
                    self._logger.error(
                        f"remove_contract registry delete failed: {e}",
                        method_name="_remove_contract", exc_info=True,
                        owner_id=self._id, owner_display=self._display_name,
                        mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                    )
                    raise

                if target_conduit._id in self._initiated_index:
                    del self._initiated_index[target_conduit._id]
                    del target_conduit._conduit_ward._received_index[self._id]
                elif target_conduit._id in self._received_index:
                    del self._received_index[target_conduit._id]
                    del target_conduit._conduit_ward._initiated_index[self._id]

                try:
                    contract.cleanup()
                except Exception as e:
                    self._logger.error(
                        f"contract cleanup failed: {e}",
                        method_name="_remove_contract", exc_info=True,
                        owner_id=self._id, owner_display=self._display_name,
                        mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                    )
                self._logger.info(
                    f"remove_contract: success target={target_conduit._id}",
                    method_name="_remove_contract",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                return True
        return False

    def _link_lesser_conduit(self, lesser_conduit: IConduit) -> None:
        """
        Internal

        Links a lesser conduit (child) to this conduit (parent).

        This establishes the parent-child lineage relationship.

        Args:
            lesser_conduit (IConduit): The lesser conduit to link.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        root_conduit: Optional[IConduit]
        if self._conduit_type == ConduitState.normal:
            root_conduit = self._conduit
        else:
            root_conduit = self._root_conduit
        if root_conduit is None:
            raise RuntimeError("Root conduit is not set for this lineage.")
        if root_conduit._conduit_state != ConduitState.normal:
            raise RuntimeError("Root conduit must be a normal conduit.")
        with self._lock:
            self._lesser_conduits[lesser_conduit._id] = lesser_conduit
            try:
                child_ward: Optional[ConduitWard] = lesser_conduit._conduit_ward
            except Exception:
                child_ward = None
            if child_ward is not None:
                child_ward._parent_conduit = self._conduit
                child_ward._root_conduit = root_conduit
        self._logger.info(
            f"link_lesser: {lesser_conduit._id}",
            method_name="_link_lesser_conduit",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )

    def _get_lesser_conduit(self, conduit_id: str) -> Optional[IConduit]:
        """
        Internal

        Recursively searches for a lesser conduit with the given ID within this conduit's hierarchy.

        Args:
            conduit_id (str): The ID of the conduit to retrieve.

        Returns:
            Optional[IConduit]: The matched conduit if found, else None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        for conduit in self._lesser_conduits.values():
            if conduit._id == conduit_id:
                return conduit
            ward: Optional[ConduitWard] = conduit._conduit_ward
            if ward is not None:
                result = ward._get_lesser_conduit(conduit_id)
                if result is not None:
                    return result
        return None

    def _get_links(self) -> List[IConduit]:
        """
        Internal

        Returns a combined list of all peer conduits this conduit has contracts with (both initiated and provider).

        Returns:
            List[IConduit]: A list of all linked peer conduits.
        """
        with self._lock:
            initiated = [self._get_initiated_conduit(cid) for cid in self._initiated_index.keys()]
            received = [self._get_provider_conduit(cid) for cid in self._received_index.keys()]
            result = [c for c in initiated + received if c is not None]
        return result


    def _get_initiated_conduits(self) -> List[IConduit]:
        """
        Internal

        Retrieves all conduits that this conduit has initiated contracts toward (outbound links).

        Returns:
            List[IConduit]: A list of conduits that this conduit has initiated contracts with.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        result = [
            conduit for conduit_id in self._initiated_index.keys()
            if (conduit := self._get_initiated_conduit(conduit_id)) is not None
        ]
        return result


    def _get_provider_conduits(self) -> List[IConduit]:
        """
        Internal

        Retrieves all conduits that have initiated contracts to this conduit (inbound links).

        Returns:
            List[IConduit]: A list of conduits that have linked to this conduit as a provider.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        result = [
            conduit for conduit_id in self._received_index.keys()
            if (conduit := self._get_provider_conduit(conduit_id)) is not None
        ]
        return result

    def _get_initiated_conduit(self, conduit_id: str) -> Optional[IConduit]:
        """
        Internal

        Retrieves the conduit that this conduit has initiated a contract *toward*.

        Args:
            conduit_id (str): The ID of the target conduit this conduit linked to.

        Returns:
            Optional[IConduit]: The target conduit if the link exists, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        if conduit_id in self._initiated_index:
            contract_id = self._initiated_index[conduit_id]
            contract = self._contracts.get(contract_id, None)
            if contract is not None:
                res = contract._ward_b._conduit if conduit_id == contract._ward_b._id else contract._ward_a._conduit
                return res
        return None

    def _get_provider_conduit(self, conduit_id: str) -> Optional[IConduit]:
        """
        Internal

        Retrieves the conduit that initiated a contract *to this* conduit.

        Args:
            conduit_id (str): The ID of the source conduit that linked to this one.

        Returns:
            Optional[IConduit]: The source conduit if the link exists, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        if conduit_id in self._received_index:
            contract_id = self._received_index[conduit_id]
            contract = self._contracts.get(contract_id, None)
            if contract is not None:
                res = contract._ward_b._conduit if conduit_id == contract._ward_b._id else contract._ward_a._conduit
                return res
        return None

    def _sever_all_linked_conduits(self) -> None:
        """
        Internal

        Severs all active peer links (contracts) to conduits. Excludes lesser conduits.

        Strategy:
          - Snapshot peer conduits under the ward lock.
          - Call `_remove_contract` for each peer (Spellbook link maps are updated there).
          - Best-effort: failures are logged and do not stop other peers.

        Returns:
            None
        """
        if self._cleaned:
            return

        # Snapshot peers under lock, then sever contracts one by one.
        peers: list[IConduit] = []
        with self._lock:
            if self._cleaned:
                return
            peers = [
                contract._get_peer(self)._conduit
                for contract in list(self._contracts.values())
                if contract is not None
            ]

        for peer_conduit in peers:
            try:
                self._remove_contract(peer_conduit)
            except Exception as e:
                self._logger.error(
                    f"sever_all_links: failed for peer {getattr(peer_conduit, '_id', 'unknown')}: {e}",
                    method_name="_sever_all_linked_conduits",
                    exc_info=True,
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )


    #endregion Link Management
    #region Spellbinding API
    def _check_spell_id_and_spell(
            self,
            spell: Optional[Spell] = None,
            spell_id: Optional[str] = None,
            aetheric_frame: str = "default"
    ) -> Tuple[str, Spell]:
        """
        Internal

        Validation and resolution helper: ensures both a spell ID and its corresponding spell object are available.

        Contract:
            - If `spell` is an Spell instance, this uses `spell.spell_id` directly.
            - If `spell` is a raw object, the ID is resolved via `inspect_spell`.

        Args:
            spell (Spell, optional): The spell object.
            spell_id (str, optional): The unique ID of the spell.
            aetheric_frame (str): The Aetheric Frame to search within.

        Returns:
            Tuple[str, Spell]: The resolved (spell_id, spell) pair.

        Raises:
            ValueError: If neither `spell` nor `spell_id` is provided.
            TypeError: If types are incorrect.
            RuntimeError: If the spell cannot be resolved or if the provided ID and resolved ID mismatch.
        """
        if spell is None and spell_id is None:
            self._logger.error(
                "check_spell_id_and_spell: neither spell nor spell_id provided",
                method_name="_check_spell_id_and_spell",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise ValueError("Either spell or spell_id must be provided.")

        if spell is None:
            if not isinstance(spell_id, str):
                self._logger.error(
                    f"check_spell_id_and_spell: spell_id wrong type {type(spell_id).__name__}",
                    method_name="_check_spell_id_and_spell",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise TypeError(f"Expected spell_id as str, got {type(spell_id).__name__}")
            spell = self._conduit.get_spell_by_id(spell_id, aetheric_frame)
            if spell is None:
                self._logger.error(
                    f"check_spell_id_and_spell: resolve by id failed ({spell_id})",
                    method_name="_check_spell_id_and_spell",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise RuntimeError(f"Could not resolve spell for spell_id '{spell_id}'.")

        if spell_id is None:
            if not isinstance(spell, Spell):
                self._logger.error(
                    f"check_spell_id_and_spell: spell wrong type {type(spell).__name__}",
                    method_name="_check_spell_id_and_spell",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise TypeError(f"Expected Spell instance, got {type(spell).__name__}")
            resolved_spell_id = spell.spell_id
            spell_id = resolved_spell_id
            if spell_id is None:
                self._logger.error(
                    "check_spell_id_and_spell: spell has no spell_id",
                    method_name="_check_spell_id_and_spell",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise RuntimeError("Could not determine spell_id from spell.")

        if isinstance(spell, Spell):
            inspected_id: Optional[str] = spell.spell_id
            if inspected_id is None:
                self._logger.error(
                    "check_spell_id_and_spell: spell has no spell_id",
                    method_name="_check_spell_id_and_spell",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise RuntimeError("Could not determine spell_id from spell.")
        else:
            inspected_id = self._conduit.inspect_spell(spell, aetheric_frame)
        if spell_id != inspected_id:
            self._logger.error(
                f"check_spell_id_and_spell: mismatch provided={spell_id} inspected={inspected_id}",
                method_name="_check_spell_id_and_spell",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError(f"Provided spell_id '{spell_id}' does not match inspected ID '{inspected_id}'.")
        return spell_id, spell


    def _check_conduit_id_and_conduit(self,
                                      conduit: Optional[IConduit] = None,
                                      conduit_id: Optional[str] = None,
                                      aetheric_frame: str = "default") -> Tuple[str, IConduit]:
        """
        Internal

        Validation and resolution helper: ensures both a conduit ID and its corresponding conduit object are available.

        Args:
            conduit (IConduit, optional): The target conduit object.
            conduit_id (str, optional): The unique ID of the target conduit.
            aetheric_frame (str): The Aetheric Frame to search within.

        Returns:
            Tuple[str, IConduit]: The resolved (conduit_id, conduit) pair.

        Raises:
            ValueError: If neither `conduit` nor `conduit_id` is provided.
            TypeError: If types are incorrect.
            RuntimeError: If the conduit cannot be resolved or if IDs mismatch.
        """
        if conduit is None and conduit_id is None:
            self._logger.error(
                "check_conduit_id_and_conduit: neither provided",
                method_name="_check_conduit_id_and_conduit",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise ValueError("Either conduit or conduit_id must be provided.")

        if conduit is None:
            if not isinstance(conduit_id, str):
                self._logger.error(
                    f"check_conduit_id_and_conduit: conduit_id wrong type {type(conduit_id).__name__}",
                    method_name="_check_conduit_id_and_conduit",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise TypeError(f"Expected conduit_id as str, got {type(conduit_id).__name__}")
            conduit = self._conduit_cloud.get_conduit_by_id(
                conduit_id,
            )
            if conduit is None:
                self._logger.error(
                    f"check_conduit_id_and_conduit: resolve by id failed ({conduit_id})",
                    method_name="_check_conduit_id_and_conduit",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise RuntimeError(f"Could not resolve conduit for conduit_id '{conduit_id}'.")

        if conduit_id is None:
            if not isinstance(conduit, IConduit):
                self._logger.error(
                    f"check_conduit_id_and_conduit: conduit wrong type {type(conduit).__name__}",
                    method_name="_check_conduit_id_and_conduit",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise TypeError(f"Expected IConduit instance, got {type(conduit).__name__}")
            conduit_id = conduit._id
            if conduit_id is None:
                self._logger.error(
                    "check_conduit_id_and_conduit: conduit has no id",
                    method_name="_check_conduit_id_and_conduit",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise RuntimeError("Could not determine conduit_id from conduit.")

        inspected_id = conduit._id
        if conduit_id != inspected_id:
            self._logger.error(
                f"check_conduit_id_and_conduit: mismatch provided={conduit_id} inspected={inspected_id}",
                method_name="_check_conduit_id_and_conduit",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError(
                f"Provided conduit_id '{conduit_id}' does not match conduit internal ID '{inspected_id}'.")
        return conduit_id, conduit

    def _create_detail(
            self,
            spell: Spell,
            permissions: Permissions,
            contract_type: ContractTypes,
            *,
            reason: DetailReason = DetailReason.other,
            root_spell_id: str | None = None,
    ) -> Detail:
        """
        Internal

        Factory for a lineage-aware Detail entry.

        Args:
            spell (Spell): The spell being granted/received.
            permissions (Permissions): The permissions applied to this lineage.
            contract_type (ContractTypes): Role of this Detail from the
                perspective of the ward that will own it.
            reason (DetailReason): Why this detail is being added.
            root_spell_id (str | None): Root spell_id responsible for this detail (tracked in sources).

        Returns:
            Detail: A new Detail instance.
        """
        if not isinstance(permissions, Permissions):
            self._logger.error(
                f"_create_detail: permissions wrong type {type(permissions).__name__}",
                method_name="_create_detail",
                owner_id=self._id,
                owner_display=self._display_name,
                mask=True,
                groups=self._log_groups,
                system_groups=self._log_sysgroups,
            )
            raise TypeError(f"Expected Permissions enum, got {type(permissions).__name__}")

        if not isinstance(contract_type, ContractTypes):
            self._logger.error(
                f"_create_detail: contract_type wrong type {type(contract_type).__name__}",
                method_name="_create_detail",
                owner_id=self._id,
                owner_display=self._display_name,
                mask=True,
                groups=self._log_groups,
                system_groups=self._log_sysgroups,
            )
            raise TypeError(
                f"Expected ContractTypes enum, got {type(contract_type).__name__}"
            )
        if not isinstance(reason, DetailReason):
            self._logger.error(
                f"_create_detail: reason wrong type {type(reason).__name__}",
                method_name="_create_detail",
                owner_id=self._id,
                owner_display=self._display_name,
                mask=True,
                groups=self._log_groups,
                system_groups=self._log_sysgroups,
            )
            raise TypeError(f"Expected DetailReason enum, got {type(reason).__name__}")

        spell_index = spell.spell_index
        spell_id = spell.spell_id  # SHA at the moment of contract creation

        return Detail(
            spell_index=spell_index,
            spell_id=spell_id,
            permissions=permissions,
            contract_type=contract_type,
            reason=reason,
            sources={root_spell_id} if root_spell_id is not None else None,
        )

    def _snapshot_detail(self, detail: Detail) -> Dict[str, Any]:
        """
        Internal

        Capture enough Detail state to rebuild it during rollback.

        Args:
            detail (Detail): Detail instance being removed or mutated.

        Returns:
            Dict[str, Any]: Snapshot of the detail contract state.
        """
        sources = detail.sources
        return {
            "spell_index": detail.spell_index,
            "spell_id": detail.spell_id,
            "permissions": detail.permissions,
            "contract_type": detail.contract_type,
            "reason": detail.reason,
            "sources": set(sources) if sources is not None else None,
        }

    def _restore_detail_snapshot(
            self,
            contract: Contract,
            ward: ConduitWard,
            snapshot: Dict[str, Any],
    ) -> None:
        """
        Internal

        Restore a previously removed Detail back into a contract.

        Args:
            contract (Contract): Contract receiving the restored detail.
            ward (ConduitWard): Ward whose detail map owns the detail.
            snapshot (Dict[str, Any]): Snapshot produced by `_snapshot_detail`.

        Returns:
            None.
        """
        restored_detail = Detail(
            spell_index=snapshot["spell_index"],
            spell_id=snapshot["spell_id"],
            permissions=snapshot["permissions"],
            contract_type=snapshot["contract_type"],
            reason=snapshot["reason"],
            sources=set(snapshot["sources"]) if snapshot["sources"] is not None else None,
        )
        contract._add(ward, restored_detail)

    def _check_spell_if_eligible(self, spell: Spell, conduit: IConduit, permissions: Permissions) -> None:
        """
        Internal

        Checks if the provided spell is eligible for contracting based on policy and spell permissions.

        Args:
            spell (Spell): The spell to check.
            conduit (IConduit): The conduit proposing the contract.
            permissions (Permissions): The permissions requested for the contract.

        Raises:
            RuntimeError: If the conduit policy prevents contracting (`block_all`).
            RuntimeError: If the spell doesn't have the required permissions (`create`, `read`).
            RuntimeError: If the spell is blocked (`Permissions.block`) and policy isn't `whitelist_all`.
            RuntimeError: If the spell is not owned by the proposing conduit.
        """
        spell_permissions = self._get_spell_permissions(spell)
        if conduit._conduit_ward._policy == Policies.block_all:
            self._logger.error(
                "check_spell_if_eligible: policy block_all",
                method_name="_check_spell_if_eligible",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError("Cannot contract spells when policy is set to block_all.")
        if permissions == Permissions.create and spell_permissions != Permissions.create:
            self._logger.error(
                "check_spell_if_eligible: create requested but spell not create",
                method_name="_check_spell_if_eligible",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError(
                f"Spell '{spell.spell_name}' does not have create permissions, cannot contract with create permissions."
            )
        if permissions == Permissions.read and spell_permissions not in (Permissions.read, Permissions.create):
            self._logger.error(
                "check_spell_if_eligible: read requested but spell not read/create",
                method_name="_check_spell_if_eligible",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError(
                f"Spell '{spell.spell_name}' does not have read permissions, cannot contract with read permissions."
            )
        if spell_permissions == Permissions.block and conduit._conduit_ward._policy != Policies.whitelist_all:
            self._logger.error(
                "check_spell_if_eligible: spell blocked and not whitelist_all",
                method_name="_check_spell_if_eligible",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError("Cannot contract spells with block permissions.")
        if spell._owner_conduit_id != conduit._id:
            self._logger.error(
                "check_spell_if_eligible: not owner",
                method_name="_check_spell_if_eligible",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise RuntimeError(
                f"Spell '{spell.spell_name}' is not owned by this conduit, cannot contract it."
            )

    def _add_spell_to_contract(
            self,
            *,
            spell: Optional[Spell] = None,
            spell_id: Optional[str] = None,
            conduit: Optional[IConduit] = None,
            conduit_id: Optional[str] = None,
            permissions: str = "create",
            aetheric_frame: str = "default",
            reason: DetailReason = DetailReason.manual,
            root_spell_id: str | None = None,
            link_dependencies: bool = False,
    ) -> bool | None:
        """
        Internal

        Adds a single spell to an existing contract with a peer conduit.

        This now contracts the **SpellIndex lineage** and uses the spell's
        current version ID only as the initial reference. On mutation, the
        lineage will advance, and lookups will resolve to the new version.
        When a new contract entry is added, cached consumer creations that
        declare a matching SpellContract are invalidated so future melds
        re-resolve dependencies.

        Args:
            spell (Spell, optional): The spell object to contract.
            spell_id (str, optional): The unique version ID of the spell.
            conduit (IConduit, optional): The target peer conduit.
            conduit_id (str, optional): The id of the target peer conduit.
            permissions (str): The permission level granted for this spell.
            aetheric_frame (str): The Aetheric Frame to resolve entities in.

        Returns:
            bool | None: True if the contract was updated, None on internal error.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If no contract exists with the target conduit (link required first).
            RuntimeError: If the spell is already contracted with the same permissions.
            RuntimeError: If the contracted spell binding key collides with existing bindings,
                including dependency collisions when link_dependencies is True.
            ValueError/TypeError/RuntimeError: From internal helper checks.
        """
        self.check_cleaned()

        # Normalize permissions into the enum
        permissions_enum = EnumHelpers.convert_enum_and_check(permissions, Permissions)

        # Resolve spell + spell_id and conduit + conduit_id via your existing helpers
        spell_id, spell = self._check_spell_id_and_spell(spell, spell_id, aetheric_frame)
        conduit_id, conduit = self._check_conduit_id_and_conduit(conduit, conduit_id, aetheric_frame)
        source_root_id = spell_id if root_spell_id is None else root_spell_id

        contract = self._find_contract_by_id(conduit_id)
        if contract is None:
            self._logger.error(
                f"add_spell_to_contract: no contract for {conduit_id}",
                method_name="_add_spell_to_contract",
                owner_id=self._id,
                owner_display=self._display_name,
                mask=True,
                groups=self._log_groups,
                system_groups=self._log_sysgroups,
            )
            raise RuntimeError(
                f"No contract found for conduit ID '{conduit_id}'. "
                f"Please link to this conduit prior to spell contract initiation."
            )

        # We still use the original spell_id for duplicate detection
        existing = contract._check_if_exists(conduit._conduit_ward, spell_id)
        existing_same_perms = contract._check_if_exists_and_permissions(conduit._conduit_ward, spell_id, permissions_enum)
        if existing and not existing_same_perms:
            self._logger.error(
                f"add_spell_to_contract: already exists {spell_id} with different permissions",
                method_name="_add_spell_to_contract",
                owner_id=self._id,
                owner_display=self._display_name,
                mask=True,
                groups=self._log_groups,
                system_groups=self._log_sysgroups,
            )
            raise RuntimeError(
                f"Spell with ID '{spell_id}' is already contracted in this conduit with different permissions."
            )

        # Policy + ownership checks remain unchanged
        self._check_spell_if_eligible(spell, conduit, permissions_enum)

        spellbook = self._conduit._spellbook
        if spellbook is not None:
            contract_key = spellbook._make_spell_key(
                spell.spellframe,
                spell.spell_name,
                spell.binding_name,
            )
            spellbook._assert_lookup_key_available(
                lookup_key=contract_key,
                spell_index=spell.spell_index,
                context="_add_spell_to_contract",
                check_local=False,
                check_contracted=True,
            )

        if link_dependencies:
            self._preflight_contract_dependency_collisions(
                root_spell=spell,
                root_spell_id=source_root_id,
                requested_permissions=permissions_enum,
                aetheric_frame=aetheric_frame,
            )

        # From this ConduitWard's perspective, the peer's Detail represents
        # a spell that the peer has **received** from us.
        contract_type = ContractTypes.received

        added_new_detail = False
        with contract._lock:
            detail = self._create_detail(
                spell,
                permissions_enum,
                contract_type,
                reason=reason,
                root_spell_id=source_root_id,
            )
            added_new_detail = contract._add(conduit._conduit_ward, detail)

        # Inform the peer spellbook about the contracted spell (SpellIndex-based) only when new
        if added_new_detail:
            try:
                peer_conduit = contract._get_peer(conduit._conduit_ward)._conduit
                peer_conduit._spellbook._add_contracted_spell(spell, conduit_id)
            except Exception as e:
                try:
                    with contract._lock:
                        contract._remove_source(
                            conduit._conduit_ward,
                            spell_id,
                            source_root_id,
                        )
                except Exception as rollback_error:
                    self._logger.error(
                        f"add_spell_to_contract: rollback failed after spellbook add error: {rollback_error}",
                        method_name="_add_spell_to_contract",
                        exc_info=True,
                        owner_id=self._id,
                        owner_display=self._display_name,
                        mask=True,
                        groups=self._log_groups,
                        system_groups=self._log_sysgroups,
                    )
                self._logger.error(
                    f"add_spell_to_contract: spellbook add failed: {e}",
                    method_name="_add_spell_to_contract",
                    exc_info=True,
                    owner_id=self._id,
                    owner_display=self._display_name,
                    mask=True,
                    groups=self._log_groups,
                    system_groups=self._log_sysgroups,
                )
                raise
            try:
                invalidate_contract_key: Optional[tuple[str, str]] = None
                spellbook = self._conduit._spellbook
                if spellbook is not None:
                    invalidate_contract_key = spellbook._make_spell_key(
                        spell.spellframe,
                        spell.spell_name,
                        spell.binding_name,
                    )
                self._invalidate_contract_consumers(invalidate_contract_key)
            except Exception:
                pass

        self._logger.info(
            f"add_spell_to_contract: success spell_id={spell_id} conduit_id={conduit_id} perms={permissions_enum.name}",
            method_name="_add_spell_to_contract",
            owner_id=self._id,
            owner_display=self._display_name,
            mask=True,
            groups=self._log_groups,
            system_groups=self._log_sysgroups,
        )

        if link_dependencies:
            try:
                self._link_spell_dependencies(
                    root_spell=spell,
                    root_spell_id=source_root_id,
                    requested_permissions=permissions_enum,
                    aetheric_frame=aetheric_frame,
                )
            except Exception as e:
                try:
                    self._remove_root_from_contracts(root_spell_id=source_root_id)
                except Exception as rollback_error:
                    self._logger.error(
                        f"add_spell_to_contract: rollback failed after dependency link error: {rollback_error}",
                        method_name="_add_spell_to_contract",
                        exc_info=True,
                        owner_id=self._id,
                        owner_display=self._display_name,
                        mask=True,
                        groups=self._log_groups,
                        system_groups=self._log_sysgroups,
                    )
                self._logger.error(
                    f"add_spell_to_contract: dependency linking failed for root {spell_id}: {e}",
                    method_name="_add_spell_to_contract",
                    exc_info=True,
                    owner_id=self._id,
                    owner_display=self._display_name,
                    mask=True,
                    groups=self._log_groups,
                    system_groups=self._log_sysgroups,
                )
                raise
        return True

    def _get_spell_permissions(self, spell: Spell) -> Permissions:
        """
        Internal helper to normalize spell permissions from `spell.permissions`.
        """
        perms = spell.permissions
        if perms is None:
            raise RuntimeError("Spell permissions are undefined.")
        permissions_enum: Permissions = EnumHelpers.convert_enum_and_check(
            perms,
            Permissions,
        )
        return permissions_enum

    def _get_spell_contract_keys(self, spell: Spell) -> set[tuple[str, str]]:
        """
        Internal

        Collect canonical SpellContract keys declared on a spell's call signature.

        This inspects the underlying callable for SpellContract defaults and returns
        their canonical `(frame_key, binding_key)` tuples for matching.

        Args:
            spell (Spell): Spell to inspect for SpellContract defaults.

        Returns:
            set[tuple[str, str]]: Canonical keys for SpellContract defaults. Returns
                an empty set when no contracts are declared or the signature cannot
                be inspected.

        Threading:
            - Read-only; no internal locks are acquired here.

        Raises:
            None. This helper is best-effort and returns an empty set when
            introspection fails.
        """
        try:
            call_target = spell.spell
        except AttributeError:
            return set()
        try:
            signature = inspect.signature(call_target)
        except (TypeError, ValueError):
            return set()

        keys: set[tuple[str, str]] = set()
        for param_name, parameter in signature.parameters.items():
            if param_name in ("self", "cls"):
                continue
            if parameter.kind in (
                    inspect.Parameter.VAR_POSITIONAL,
                    inspect.Parameter.VAR_KEYWORD,
            ):
                continue
            if parameter.default is inspect.Parameter.empty:
                continue
            default_value = parameter.default
            if isinstance(default_value, SpellContract):
                keys.add(default_value.canonical_key)
        return keys

    def _invalidate_contract_consumers(self, contract_key: Optional[tuple[str, str]] = None) -> None:
        """
        Internal

        Clear cached creations for consumer spells that declare SpellContract sockets.

        If `contract_key` is provided, only consumers that declare a SpellContract
        with that canonical key are invalidated. When `contract_key` is None, all
        spells with any SpellContract defaults are invalidated.

        Args:
            contract_key (Optional[tuple[str, str]]):
                Canonical contract key to match, or None to invalidate all
                SpellContract consumers.

        Returns:
            None.

        Threading:
            - Uses SpellSystemStates internal lock to resolve contract dependents.
            - Uses Creations' internal lock via `extract_spell_creations`.

        Raises:
            None. Best-effort; failures are swallowed to avoid blocking contract
            operations.
        """
        conduit = self._conduit
        if conduit is None:
            return
        spellbook = conduit._spellbook
        creations = conduit._creations
        if spellbook is None or creations is None:
            return
        states = spellbook._spell_system_states
        if states is None:
            return

        contract_keys: Optional[Iterable[tuple[str, str]]] = None
        if contract_key is not None:
            contract_keys = (contract_key,)
        try:
            impacted = states.mark_contract_dependents_dirty(
                spellbook_id=spellbook._id,
                contract_keys=contract_keys,
            )
        except Exception:
            impacted = set()

        for lineage_id in impacted:
            state = states.get_by_index_id(lineage_id)
            if state is None:
                continue
            spell_id = state.current_spell_id
            try:
                creations.extract_spell_creations(spell_id)
            except AttributeError:
                return
            except Exception:
                continue

    def _has_local_spell_version(self, spell_id: str) -> bool:
        """
        Check if this conduit already has the given spell version locally.
        """
        book = self._conduit._spellbook
        if book is None or book._spells is None:
            return False
        with book._lock:
            for idx in book._spells.keys():
                versions = idx._versions
                if versions and spell_id in versions:
                    return True
        return False

    def _is_contract_empty(self, contract: Contract) -> bool:
        """
        Determine if a contract has any remaining details on either side.
        """
        return (not contract._details_a) and (not contract._details_b)

    def _remove_root_from_contracts(
            self,
            *,
            root_spell_id: str,
            conduit: Optional[IConduit] = None,
            conduit_id: Optional[str] = None,
            aetheric_frame: str = "default",
    ) -> dict[str, list[str] | dict[str, str]]:
        """
        Internal

        Remove one root-source tag and its dependency-contracted fallout.

        Detail entries can be tagged with `sources` so the ward can tell which
        contracted spells were pulled in transitively for one specific root
        lineage. This helper removes one `root_spell_id` source from matching
        details, drops now-orphaned contracted spells from peer spellbooks, and
        severs any contract that becomes empty afterward.

        This is the rollback/cleanup counterpart to dependency-linked contract
        expansion.
        """
        self.check_cleaned()
        if not isinstance(root_spell_id, str):
            raise TypeError("root_spell_id must be a string.")

        # Resolve a specific contract if conduit is provided, else scan all.
        target_contracts: list[Contract] = []
        target_peers: list[IConduit] = []

        if conduit is not None or conduit_id is not None:
            _, resolved_conduit = self._check_conduit_id_and_conduit(conduit, conduit_id, aetheric_frame)
            contract = self._find_contract(resolved_conduit)
            if contract is not None:
                target_contracts.append(contract)
                target_peers.append(resolved_conduit)
        else:
            with self._lock:
                target_contracts = list(self._contracts.values())
                target_peers = [c._get_peer(self)._conduit for c in target_contracts if c is not None]

        success_contract_ids: list[str] = []
        failed_contract_ids: dict[str, str] = {}
        contracts_to_sever: list[IConduit] = []

        for idx, contract in enumerate(target_contracts):
            peer_conduit = target_peers[idx] if idx < len(target_peers) else None
            try:
                removed_any = False
                with contract._lock:
                    for ward in (contract._ward_a, contract._ward_b):
                        detail_map = contract._get_detail_map(ward)
                        for spell_id, detail in list(detail_map.items()):
                            if detail.sources and root_spell_id in detail.sources:
                                detail_snapshot = self._snapshot_detail(detail)
                                should_delete = detail.remove_source(root_spell_id)
                                if should_delete:
                                    # Remove contracted spell from peer spellbook
                                    try:
                                        contract._get_peer(ward)._conduit._spellbook._remove_contracted_spell(spell_id, ward._id)
                                    except Exception as e:
                                        detail_map.pop(spell_id, None)
                                        try:
                                            self._restore_detail_snapshot(
                                                contract,
                                                ward,
                                                detail_snapshot,
                                            )
                                        except Exception as rollback_error:
                                            self._logger.error(
                                                f"_remove_root_from_contracts: rollback failed for {spell_id}: {rollback_error}",
                                                method_name="_remove_root_from_contracts",
                                                exc_info=True,
                                                owner_id=self._id,
                                                owner_display=self._display_name,
                                                mask=True,
                                                groups=self._log_groups,
                                                system_groups=self._log_sysgroups,
                                            )
                                        self._logger.error(
                                            f"_remove_root_from_contracts: spellbook remove failed for {spell_id}: {e}",
                                            method_name="_remove_root_from_contracts",
                                            exc_info=True,
                                            owner_id=self._id,
                                            owner_display=self._display_name,
                                            mask=True,
                                            groups=self._log_groups,
                                            system_groups=self._log_sysgroups,
                                        )
                                        raise
                                    detail_map.pop(spell_id, None)
                                    detail.cleanup()
                                    removed_any = True
                if self._is_contract_empty(contract):
                    if peer_conduit is not None:
                        contracts_to_sever.append(peer_conduit)
                if removed_any:
                    success_contract_ids.append(contract._id)
            except Exception as e:
                failed_contract_ids[getattr(contract, "_id", "unknown")] = str(e)
                self._logger.error(
                    f"_remove_root_from_contracts: failed for contract {getattr(contract, '_id', 'unknown')}: {e}",
                    method_name="_remove_root_from_contracts",
                    exc_info=True,
                    owner_id=self._id,
                    owner_display=self._display_name,
                    mask=True,
                    groups=self._log_groups,
                    system_groups=self._log_sysgroups,
                )

        for peer in contracts_to_sever:
            if peer is None:
                continue
            try:
                self._remove_contract(peer)
            except Exception as e:
                self._logger.error(
                    f"_remove_root_from_contracts: contract sever failed for peer {getattr(peer, '_id', 'unknown')}: {e}",
                    method_name="_remove_root_from_contracts",
                    exc_info=True,
                    owner_id=self._id,
                    owner_display=self._display_name,
                    mask=True,
                    groups=self._log_groups,
                    system_groups=self._log_sysgroups,
                )

        return {
            "success": success_contract_ids,
            "failed": failed_contract_ids,
        }

    def _link_spell_dependencies(
            self,
            *,
            root_spell: Spell,
            root_spell_id: str,
            requested_permissions: Permissions,
            aetheric_frame: str = "default",
    ) -> None:
        """
        Internal

        Link all transitive dependencies for a root spell by contracting them
        from their owning conduits. Each dependency detail is tagged with
        DetailReason.dependency and source=root_spell_id for reversible teardown.
        """
        deps = getattr(root_spell, "dependencies", None) or []
        if not deps:
            return

        visited: set[str] = set()

        def walk(dep_id: str) -> None:
            """
            Depth-first dependency contracting walk for one root lineage.

            Contract:
                - Skips already-visited dependency versions.
                - Contracts only non-local dependency owners.
                - Recurses through transitive dependency spell ids discovered
                  on each newly contracted dependency spell.
            """
            if dep_id in visited:
                return
            visited.add(dep_id)

            # Already local? nothing to contract.
            if self._has_local_spell_version(dep_id):
                return

            owner_conduit = self._conduit.get_conduit_by_spell_id(dep_id, aetheric_frame)
            if owner_conduit is None:
                raise RuntimeError(f"Dependency '{dep_id}' owner not found for root '{root_spell_id}'.")

            # If we own it (but earlier check missed), skip contracting.
            if owner_conduit._id == self._id:
                return

            # Ensure we have a contract; will honor policy gating inside _link.
            if not self._find_contract(owner_conduit):
                self._link(owner_conduit)
            contract = self._find_contract(owner_conduit)
            if contract is None:
                raise RuntimeError(f"Failed to create contract to owner of dependency '{dep_id}'.")

            dep_spell = owner_conduit.get_spell_by_id(dep_id, aetheric_frame)
            if dep_spell is None:
                raise RuntimeError(f"Dependency '{dep_id}' not found in owner conduit '{owner_conduit._id}'.")

            dep_permissions = self._get_spell_permissions(dep_spell)
            # Choose the safer of requested vs spell's own permissions (never elevate beyond spell).
            if requested_permissions == Permissions.read or dep_permissions == Permissions.read:
                dep_permissions = Permissions.read

            self._check_spell_if_eligible(dep_spell, owner_conduit, dep_permissions)

            added_new_detail = False
            with contract._lock:
                detail = self._create_detail(
                    dep_spell,
                    dep_permissions,
                    ContractTypes.received,
                    reason=DetailReason.dependency,
                    root_spell_id=root_spell_id,
                )
                added_new_detail = contract._add(owner_conduit._conduit_ward, detail)

            if added_new_detail:
                borrower_conduit = contract._get_peer(owner_conduit._conduit_ward)._conduit
                borrower_conduit._spellbook._add_contracted_spell(dep_spell, owner_conduit._id)

            # Recurse through transitive dependencies
            child_deps = getattr(dep_spell, "dependencies", None) or []
            for child_dep in child_deps:
                walk(child_dep)

        for dep in deps:
            walk(dep)

    def _preflight_contract_dependency_collisions(
            self,
            *,
            root_spell: Spell,
            root_spell_id: str,
            requested_permissions: Permissions,
            aetheric_frame: str = "default",
    ) -> None:
        """
        Internal

        Purpose:
            Fail fast by checking contracted-binding collisions for a root spell
            and any transitive dependencies before linking.
        Contract:
            - Raises if any dependency is missing or ineligible for contracting.
            - Raises if any contracted binding key would collide with an existing
              contracted spell or another spell in this preflight batch.
            - Does not mutate contracts or spellbooks.
        Args:
            root_spell: Root spell being contracted.
            root_spell_id: Root spell id for dependency source tagging.
            requested_permissions: Requested permissions for dependency linking.
            aetheric_frame: Aetheric frame for conduit/spell lookups.
        Returns:
            None.
        Raises:
            ValueError: If root_spell or root_spell_id are missing.
            RuntimeError: If dependencies are missing, ineligible, or collide.
        Threading:
            Read-only; no contract locks are acquired.
        """
        self.check_cleaned()

        if root_spell is None:
            raise ValueError("root_spell must not be None.")
        if root_spell_id is None:
            raise ValueError("root_spell_id must not be None.")

        spellbook = self._conduit._spellbook
        if spellbook is None:
            return

        visited: set[str] = set()
        batch_keys: dict[tuple[str, str], Spell] = {}

        def record_spell(spell: Spell, spell_id: str) -> None:
            """
            Record one spell's binding key into the preflight collision set.

            Contract:
                - Raises when two different spells in the same preflight batch
                  would claim the same contracted binding key.
                - Reuses the spellbook's own lookup-key assertion for
                  contracted-key collision checks against current runtime state.
            """
            contract_key = spellbook._make_spell_key(
                spell.spellframe,
                spell.spell_name,
                spell.binding_name,
            )
            existing = batch_keys.get(contract_key)
            if existing is not None and existing is not spell:
                frame_key, bind_key = contract_key
                raise RuntimeError(
                    "Spell binding key collision detected in preflight batch. "
                    f"frame_key='{frame_key}', binding_name='{bind_key}'. "
                    "Use a distinct spellframe or binding_name to disambiguate."
                )
            batch_keys[contract_key] = spell
            spellbook._assert_lookup_key_available(
                lookup_key=contract_key,
                spell_index=spell.spell_index,
                context="_preflight_contract_dependency_collisions",
                check_local=False,
                check_contracted=True,
            )

        visited.add(root_spell_id)
        record_spell(root_spell, root_spell_id)

        try:
            deps = root_spell.dependencies
        except AttributeError:
            deps = []

        if not deps:
            return

        def walk(dep_id: str) -> None:
            """
            Depth-first read-only preflight walk over transitive dependencies.

            Contract:
                - Skips already-visited dependency versions.
                - Resolves each dependency owner/spell and checks contracting
                  eligibility without mutating contracts.
                - Records every reachable dependency into the batch collision
                  set before recursing further.
            """
            if dep_id in visited:
                return
            visited.add(dep_id)

            if self._has_local_spell_version(dep_id):
                return

            owner_conduit = self._conduit.get_conduit_by_spell_id(dep_id, aetheric_frame)
            if owner_conduit is None:
                raise RuntimeError(
                    f"Dependency '{dep_id}' owner not found for root '{root_spell_id}'."
                )

            if owner_conduit._id == self._id:
                return

            dep_spell = owner_conduit.get_spell_by_id(dep_id, aetheric_frame)
            if dep_spell is None:
                raise RuntimeError(
                    f"Dependency '{dep_id}' not found in owner conduit '{owner_conduit._id}'."
                )

            dep_permissions = self._get_spell_permissions(dep_spell)
            if requested_permissions == Permissions.read or dep_permissions == Permissions.read:
                dep_permissions = Permissions.read

            self._check_spell_if_eligible(dep_spell, owner_conduit, dep_permissions)
            record_spell(dep_spell, dep_id)

            try:
                child_deps = dep_spell.dependencies
            except AttributeError:
                child_deps = []
            for child_dep in child_deps or []:
                walk(child_dep)

        for dep in deps:
            walk(dep)


    def _add_spells_to_contract(self, *, spell_ids: Optional[list[str]] = None, conduit: Optional[IConduit] = None, conduit_id: Optional[str] = None,
                                permissions: str = "create", aetheric_frame: str = "default",
                                reason: DetailReason = DetailReason.manual, link_dependencies: bool = False) -> dict[str, list[str] | dict[str, str]]:
        """
        Internal

        Bulk wrapper over `_add_spell_to_contract(...)`.

        This helper does not introduce new contract semantics. It simply
        applies the single-spell lineage-aware add path repeatedly and returns
        a per-spell success/failure report so callers can surface partial
        outcomes without losing the first failure.

        Args:
            spell_ids (list[str], optional): List of spell IDs to contract.
            conduit (IConduit, optional): The target peer conduit.
            conduit_id (str, optional): The id of the target peer conduit.
            permissions (str): The permission level to apply to all spells (default is "create").
            aetheric_frame (str): The Aetheric Frame to resolve entities in.

        Returns:
            dict: A dictionary containing a list of successful spell IDs and a
            mapping of failed spell IDs to error messages.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        success_spell_ids: list[str] = []
        failed_spell_ids: dict[str, str] = {}
        for sid in (spell_ids or []):
            try:
                self._add_spell_to_contract(
                    spell_id=sid,
                    conduit=conduit,
                    conduit_id=conduit_id,
                    permissions=permissions,
                    aetheric_frame=aetheric_frame,
                    reason=reason,
                    root_spell_id=sid,
                    link_dependencies=link_dependencies,
                )
                success_spell_ids.append(sid)
            except Exception as e:
                failed_spell_ids[sid] = str(e)
                self._logger.error(
                    f"add_spells_to_contract: {sid} failed: {e}",
                    method_name="_add_spells_to_contract", exc_info=True,
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
        self._logger.info(
            f"add_spells_to_contract done success={len(success_spell_ids)} failed={len(failed_spell_ids)}",
            method_name="_add_spells_to_contract",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        return {
            "success": success_spell_ids,
            "failed": failed_spell_ids,
        }

    def _remove_spell_from_contract(self, *, spell: Optional[Spell] = None, spell_id: Optional[str] = None, conduit: Optional[IConduit] = None,
                                    conduit_id: Optional[str] = None, root_spell_id: str | None = None, aetheric_frame: str = "default") -> bool | None:
        """
        Internal

        Removes a specific spell from an existing contract.

        When the contract entry is fully removed, cached consumer creations that
        declare a matching SpellContract are invalidated so future melds
        re-resolve dependencies.

        Args:
            spell (Spell, optional): The spell object to remove.
            spell_id (str, optional): The unique ID of the spell to remove.
            conduit (IConduit, optional): The target peer conduit.
            conduit_id (str, optional): The id of the target peer conduit.
            root_spell_id (str, optional): Source root spell_id; if provided, only that source is removed.
            aetheric_frame (str): The Aetheric Frame to resolve entities in.

        Returns:
            bool: True if the spell was successfully removed.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If no contract is found.
            RuntimeError: If the spell ID is not found in the contract.
            ValueError/TypeError/RuntimeError: From internal helper checks.
        """
        self.check_cleaned()
        spell_id, spell = self._check_spell_id_and_spell(spell, spell_id, aetheric_frame)
        conduit_id, conduit = self._check_conduit_id_and_conduit(conduit, conduit_id, aetheric_frame)
        contract = self._find_contract_by_id(conduit_id)
        if contract is not None:
            contract_key = None
            try:
                spellbook = self._conduit._spellbook
                if spellbook is not None:
                    with spellbook._lock:
                        contracted_spell = spellbook._find_contracted_spell_by_id(spell_id, conduit_id)
                    if contracted_spell is not None:
                        contract_key = spellbook._make_spell_key(
                            contracted_spell.spellframe,
                            contracted_spell.spell_name,
                            contracted_spell.binding_name,
                        )
            except Exception:
                contract_key = None
            deleted_detail = False
            detail_snapshot: Optional[Dict[str, Any]] = None
            with contract._lock:
                if contract._check_if_exists(conduit._conduit_ward, spell_id):
                    detail_map = contract._get_detail_map(conduit._conduit_ward)
                    current_detail = detail_map.get(spell_id)
                    if current_detail is not None:
                        detail_snapshot = self._snapshot_detail(current_detail)
                    deleted_detail = contract._remove_source(conduit._conduit_ward, spell_id, root_spell_id)
                else:
                    self._logger.error(
                        f"remove_spell_from_contract: spell not in contract ({spell_id})",
                        method_name="_remove_spell_from_contract",
                        owner_id=self._id, owner_display=self._display_name,
                        mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                    )
                    raise RuntimeError(f"Spell with ID '{spell_id}' does not exist in the contract for conduit ID {conduit_id}.")

            if deleted_detail:
                try:
                    contract._get_peer(conduit._conduit_ward)._conduit._spellbook._remove_contracted_spell(spell_id, conduit_id)
                except Exception as e:
                    if detail_snapshot is not None:
                        try:
                            with contract._lock:
                                detail_map = contract._get_detail_map(conduit._conduit_ward)
                                detail_map.pop(spell_id, None)
                                self._restore_detail_snapshot(
                                    contract,
                                    conduit._conduit_ward,
                                    detail_snapshot,
                                )
                        except Exception as rollback_error:
                            self._logger.error(
                                f"remove_spell_from_contract: rollback failed after spellbook remove error: {rollback_error}",
                                method_name="_remove_spell_from_contract",
                                exc_info=True,
                                owner_id=self._id,
                                owner_display=self._display_name,
                                mask=True,
                                groups=self._log_groups,
                                system_groups=self._log_sysgroups,
                            )
                    self._logger.error(
                        f"remove_spell_from_contract: spellbook remove failed: {e}",
                        method_name="_remove_spell_from_contract", exc_info=True,
                        owner_id=self._id, owner_display=self._display_name,
                        mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                    )
                    raise
                try:
                    self._invalidate_contract_consumers(contract_key)
                except Exception:
                    pass

            if self._is_contract_empty(contract):
                try:
                    self._remove_contract(conduit)
                except Exception as e:
                    self._logger.error(
                        f"remove_spell_from_contract: contract cleanup failed {e}",
                        method_name="_remove_spell_from_contract",
                        owner_id=self._id, owner_display=self._display_name,
                        mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                    )
                    raise

            self._logger.info(
                f"remove_spell_from_contract: success {spell_id}",
                method_name="_remove_spell_from_contract",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            return True
        self._logger.error(
            f"remove_spell_from_contract: no contract for conduit {conduit_id}",
            method_name="_remove_spell_from_contract",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        raise RuntimeError(f"No contract found for conduit ID {conduit_id}")


    def _remove_spells_from_contract(self, *, spell_ids: Optional[list[str]] = None, conduit: Optional[IConduit] = None,
                                     conduit_id: Optional[str] = None, root_spell_id: str | None = None,
                                     aetheric_frame: str = "default") -> dict[str, list[str] | dict[str, str]]:
        """
        Internal

        Bulk wrapper over `_remove_spell_from_contract(...)`.

        This helper applies the single-spell removal path repeatedly and
        returns a per-spell success/failure report. It preserves the same
        lineage/source-aware removal semantics and cleanup behavior as the
        single-item API.

        Args:
            spell_ids (list[str], optional): List of spell IDs to remove.
            conduit (IConduit, optional): The target peer conduit.
            conduit_id (str, optional): The id of the target peer conduit.
            aetheric_frame (str): The Aetheric Frame to resolve entities in.

        Returns:
            dict: A dictionary containing a list of successful spell IDs and a
            mapping of failed spell IDs to error messages.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        success_spell_ids: list[str] = []
        failed_spell_ids: dict[str, str] = {}
        for sid in (spell_ids or []):
            try:
                self._remove_spell_from_contract(
                    spell_id=sid,
                    conduit=conduit,
                    conduit_id=conduit_id,
                    root_spell_id=root_spell_id,
                    aetheric_frame=aetheric_frame,
                )
                success_spell_ids.append(sid)
            except Exception as e:
                failed_spell_ids[sid] = str(e)
                self._logger.error(
                    f"remove_spells_from_contract: {sid} failed: {e}",
                    method_name="_remove_spells_from_contract", exc_info=True,
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
        self._logger.info(
            f"remove_spells_from_contract done success={len(success_spell_ids)} failed={len(failed_spell_ids)}",
            method_name="_remove_spells_from_contract",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        return {
            "success": success_spell_ids,
            "failed": failed_spell_ids,
        }

    def _remove_all_spells_from_contract(self, *, conduit: Optional[IConduit] = None, conduit_id: Optional[str] = None, root_spell_id: str | None = None, aetheric_frame: str = "default") -> bool | None:
        """
        Internal

        Removes ALL spells from the contract associated with the specified peer conduit.

        Cached consumer creations that declare SpellContract sockets are invalidated
        so future melds re-resolve dependencies after the bulk removal.

        Args:
            conduit (IConduit, optional): The target peer conduit.
            conduit_id (str, optional): The id of the target peer conduit.
            aetheric_frame (str): The Aetheric Frame to resolve entities in.

        Returns:
            bool: True if all spells were successfully removed and cleanup performed.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If no contract is found.
            ValueError/TypeError/RuntimeError: From internal helper checks.
        """
        self.check_cleaned()
        conduit_id, conduit = self._check_conduit_id_and_conduit(conduit, conduit_id, aetheric_frame)
        contract = self._find_contract_by_id(conduit_id)
        if contract is not None:
            with contract._lock:
                ward_a = contract._ward_a
                ward_b = contract._ward_b
                try:
                    ward_a._conduit._spellbook._clear_contracted_spells_for_conduit(ward_b._id)
                    ward_b._conduit._spellbook._clear_contracted_spells_for_conduit(ward_a._id)
                except Exception as e:
                    self._logger.error(
                        f"remove_all_spells_from_contract: spellbook clear failed: {e}",
                        method_name="_remove_all_spells_from_contract", exc_info=True,
                        owner_id=self._id, owner_display=self._display_name,
                        mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                    )
                    raise
                contract._clear_contract()
            try:
                self._invalidate_contract_consumers()
            except Exception:
                pass
            self._logger.info(
                f"remove_all_spells_from_contract: success conduit_id={conduit_id}",
                method_name="_remove_all_spells_from_contract",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            return True
        self._logger.error(
            f"remove_all_spells_from_contract: no contract for {conduit_id}",
            method_name="_remove_all_spells_from_contract",
            owner_id=self._id, owner_display=self._display_name,
            mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
        )
        raise RuntimeError(f"No contract found for conduit ID {conduit_id}")

    def _get_all_spells_in_contracts(
            self,
            validate: bool = True,
    ) -> Optional[dict[str, list[Tuple[str, Spell]]]]:
        """
        Internal

        Gather every spell this conduit can currently consume via contracts.

        For each peer conduit, this returns a list of:
            (current_spell_version_id, Spell)

        Semantics:
            * Contracts are anchored on SpellIndex (via Detail.spell_index).
            * Resolution uses Spellbook._find_contracted_spell(spell_index),
              so if the lineage has mutated, we get the **current** spell object.
            * The version ID returned in the tuple is spell.spell_id (head).

        Contract:
            - Optionally validates all contracts first and fails fast if any are
              inconsistent.
            - Returns the current visible version for each contracted lineage,
              not the historical version captured at contract-creation time.
        """
        self.check_cleaned()

        if validate:
            validation = self._validate_contracts_and_define()
            if not all(validation.values()):
                self._logger.error(
                    "get_all_spells_in_contracts: validation failed",
                    method_name="_get_all_spells_in_contracts",
                    owner_id=self._id,
                    owner_display=self._display_name,
                    mask=True,
                    groups=self._log_groups,
                    system_groups=self._log_sysgroups,
                )
                raise RuntimeError(
                    "One or more contracts are invalid. Please validate contracts before retrieving spells."
                )

        spells_in_contracts: dict[str, list[Tuple[str, Spell]]] = {}

        with self._lock:
            for contract_id, contract in self._contracts.items():
                try:
                    peer_ward = contract._get_peer(self)

                    # We want spells the peer has GRANTED to this conduit,
                    # which live in the peer's detail map.
                    detail_map = contract._get_detail_map(peer_ward)
                    if not detail_map:
                        continue

                    spells: list[Tuple[str, Spell]] = []

                    for detail in detail_map.values():
                        # lineage-based resolution
                        spell_index = detail.spell_index
                        try:
                            spell = self._conduit._spellbook._find_contracted_spell(spell_index)
                        except Exception as e:
                            if validate:
                                self._logger.error(
                                    f"_get_all_spells_in_contracts: contracted spell lookup failed "
                                    f"for peer={peer_ward._id}, index={spell_index}: {e}",
                                    method_name="_get_all_spells_in_contracts",
                                    exc_info=True,
                                    owner_id=self._id,
                                    owner_display=self._display_name,
                                    mask=True,
                                    groups=self._log_groups,
                                    system_groups=self._log_sysgroups,
                                )
                                raise
                            continue

                        # Expose the CURRENT version id, not the historical one.
                        if spell is None:
                            if validate:
                                raise RuntimeError(
                                    f"Failed to resolve contracted spell for index {spell_index}."
                                )
                            continue

                        current_id = spell.spell_id
                        spells.append((current_id, spell))

                    if spells:
                        spells_in_contracts[peer_ward._id] = spells

                except Exception as e:
                    if validate:
                        self._logger.error(
                            f"inspect contract {contract_id} failed: {e}",
                            method_name="_get_all_spells_in_contracts",
                            exc_info=True,
                            owner_id=self._id,
                            owner_display=self._display_name,
                            mask=True,
                            groups=self._log_groups,
                            system_groups=self._log_sysgroups,
                        )
                        raise RuntimeError(f"Failed to inspect contract {contract_id}: {e}")

        return spells_in_contracts if spells_in_contracts else None



    def _get_spell_in_contracts(self, spell_id: str) -> Optional[tuple[str, Spell]]:
        """
        Internal

        Resolve one contracted spell version through the contract graph.

        This now behaves in a lineage-aware way:

            * spell_id may be ANY version SHA belonging to the lineage.
            * We search each Detail's SpellIndex using Detail.has_version(spell_id).
            * If matched, we resolve via Spellbook._find_contracted_spell(spell_index)
              and return the **current** spell object (not the historical version).

        Args:
            spell_id (str): The version ID (SHA) to search for.

        Returns:
            Optional[tuple[str, Spell]]: (peer_conduit_id, Spell) if found, else None.

        Contract:
            The returned spell object is the current head for the matched
            lineage, not necessarily the historical version string the caller
            searched with.
        """
        self.check_cleaned()

        with self._lock:
            for contract in self._contracts.values():
                peer_ward = contract._get_peer(self)
                detail_map = contract._get_detail_map(peer_ward)

                if not detail_map:
                    continue

                for detail in detail_map.values():
                    if not detail.has_version(spell_id):
                        continue

                    spell_index = detail.spell_index
                    try:
                        spell = self._conduit._spellbook._find_contracted_spell(spell_index)
                    except Exception as e:
                        self._logger.error(
                            f"_get_spell_in_contracts: contracted spell lookup failed "
                            f"for version={spell_id}, index={spell_index}: {e}",
                            method_name="_get_spell_in_contracts",
                            exc_info=True,
                            owner_id=self._id,
                            owner_display=self._display_name,
                            mask=True,
                            groups=self._log_groups,
                            system_groups=self._log_sysgroups,
                        )
                        return None

                    if spell is None:
                        return None
                    return peer_ward._id, spell

        return None



    def _get_spells_in_contract_by_conduit(self, conduit_id: str) -> dict[str, list[tuple[str, Spell]]] | None:
        """
        Internal

        Retrieves all spells exchanged with a specific conduit by its unique ID.

        - "inbound": spells the peer has granted to this conduit.
        - "outbound": spells this conduit has granted to the peer.

        Args:
            conduit_id (str): The id of the target conduit.

        Returns:
            dict[str, list[tuple[str, Spell]]] | None: A dictionary mapping roles
            ("inbound", "outbound") to lists of (spell_id, Spell) tuples, or None
            if no such conduit is linked. If a contract exists but has no spells,
            the lists are empty.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        with self._lock:
            contract = self._find_contract_by_id(conduit_id)
            if not contract:
                return None

            spells_result: dict[str, list[tuple[str, Spell]]] = {"inbound": [], "outbound": []}

            peer_ward = contract._get_peer(self)

            # Inbound: spells the peer has granted to us (live in peer's detail map).
            received_map = contract._get_detail_map(peer_ward)
            for sid, detail in received_map.items():
                spell = self._conduit.find_contracted_spell(sid)
                if spell:
                    spells_result["inbound"].append((sid, spell))

            # Outbound: spells we have granted to the peer (live in our detail map).
            our_map = contract._get_detail_map(self)
            for sid, detail in our_map.items():
                owned_spell: Optional[Spell] = None
                try:
                    # This is a local spell we own; resolve via SpellIndex-aware get_spell_by_id.
                    owned_spell = self._conduit.get_spell_by_id(sid)
                except Exception:
                    owned_spell = None

                if owned_spell is not None:
                    spells_result["outbound"].append((sid, owned_spell))

        return spells_result


    def _get_spells_in_contract_by_conduit_name(self, conduit_name: str) -> dict[str, list[tuple[str, Spell]]] | None:
        """
        Internal

        Retrieves all spells exchanged with a specific conduit by its declared name.

        Mirrors `_get_spells_in_contract_by_conduit` but performs lookup by name.

        Args:
            conduit_name (str): The name identifier of the target conduit.

        Returns:
            dict[str, list[tuple[str, Spell]]] | None: A dictionary of spells exchanged (inbound/outbound), or None if not found.
            When a contract exists but contains no spells, inbound/outbound lists are empty.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            ValueError: If `conduit_name` is empty or not a string.
        """
        self.check_cleaned()
        if not conduit_name or not isinstance(conduit_name, str):
            self._logger.error(
                "get_spells_in_contract_by_conduit_name: invalid name",
                method_name="_get_spells_in_contract_by_conduit_name",
                owner_id=self._id, owner_display=self._display_name,
                mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
            )
            raise ValueError("Conduit name must be a non-empty string.")

        with self._lock:
            for contract in self._contracts.values():
                peer_ward = contract._get_peer(self)
                peer_conduit = peer_ward._conduit
                if peer_conduit._name == conduit_name:
                    res = self._get_spells_in_contract_by_conduit(peer_ward._id)
                    return res

        return None

    def _get_contracted_conduits(self) -> list[Tuple[str, IConduit]] | None:
        """
        Internal

        Returns all conduits that currently have active spell contracts with this conduit.

        Args:
            None

        Returns:
            list[Tuple[str, IConduit]] | None: A list of (`conduit_id`, `IConduit`) tuples. Returns None if no links exist.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        contracted_conduits = []
        with self._lock:
            for contract_id, contract in self._contracts.items():
                peer_ward = contract._get_peer(self)
                peer_conduit = peer_ward._conduit
                contracted_conduits.append((peer_ward._id, peer_conduit))
        return contracted_conduits if contracted_conduits else None

    #region Ownership Transfer
    def _transfer_spell_ownership(
            self,
            *,
            spell: Spell | str | SpellIndex,
            target_conduit: IConduit,
            move_creations: bool = False,
            include_dependencies: bool = False,
            force_unshare: bool = True,
            invalidate_after_transfer: bool = True,
            mark_dependencies_dirty: bool = False,
    ) -> dict:
        """
        Internal

        Transfer stewardship of a spell to another conduit (dynamic mode only).

        This performs a preflight to summarize borrowers/deps/creations, then executes
        the transfer according to the provided options.

        Args:
            spell: Spell object, spell_id, or SpellIndex to transfer.
            target_conduit: The conduit that will become the new steward.
            move_creations: If True, move creations; else tear them down at source.
            include_dependencies: If True, transfer owned dependencies as well.
            force_unshare: If True, strip all contracts/shares for this spell during transfer.
            invalidate_after_transfer: If True, mark lineage dirty after transfer.
            mark_dependencies_dirty: If True, mark dependency lineages dirty (even if not moved).

        Returns:
            dict: Preflight summary of the transfer plan.
        """
        from melder.aether.conduit.conduit_ward.transfer.transfer_of_ownership import TransferOfOwnership
        if not self._dynamic:
            raise RuntimeError("Ownership transfer requires dynamic mode.")

        resolved_spell: Optional[Spell]
        if isinstance(spell, Spell):
            resolved_spell = spell
        elif isinstance(spell, SpellIndex):
            resolved_spell = self._conduit.get_spell_by_index_id(spell.id)
        else:
            resolved_spell = self._conduit.get_spell_by_id(
                spell,
                self._conduit._aetheric_frame_name,
            )

        if resolved_spell is None:
            raise RuntimeError("Could not resolve spell for ownership transfer.")

        transfer = TransferOfOwnership(
            source_conduit=self._conduit,
            target_conduit=target_conduit,
            spell=resolved_spell,
            move_creations=move_creations,
            include_dependencies=include_dependencies,
            force_unshare=force_unshare,
            invalidate_after_transfer=invalidate_after_transfer,
            mark_dependencies_dirty=mark_dependencies_dirty,
        )
        summary = transfer.preflight()
        transfer.execute()
        return summary
    #endregion Ownership Transfer

    def _describe_contract(self, conduit_id: str) -> dict:
        """
        Internal

        Returns a detailed diagnostic summary of a contract established with a specific peer conduit ID.

        Args:
            conduit_id (str): id of the peer conduit whose contract you wish to examine.

        Returns:
            dict: Dictionary containing contract metadata, including spell list and permissions.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If no contract is found with the given conduit ID.
        """
        self.check_cleaned()
        with self._lock:
            contract = self._find_contract_by_id(conduit_id)
            if not contract:
                self._logger.error(
                    f"_describe_contract: no contract {conduit_id}",
                    method_name="_describe_contract",
                    owner_id=self._id, owner_display=self._display_name,
                    mask=True, groups=self._log_groups, system_groups=self._log_sysgroups,
                )
                raise RuntimeError(f"No contract found with conduit ID: {conduit_id}")

            peer_ward = contract._get_peer(self)
            peer_conduit = peer_ward._conduit
            detail_map = contract._get_detail_map(self)

            result = {
                "contract_id": contract._id,
                "peer_conduit_name": getattr(peer_conduit, "_name", "Unknown"),
                "spell_count": len(detail_map),
                "spells": [
                    {
                        "spell_id": sid,
                        "permissions": detail.permissions.name,
                    }
                    for sid, detail in detail_map.items()
                ]
            }
        return result

    def _validate_contracts_and_define(self) -> dict[str, bool]:
        """
        Internal

        Validate all active contracts attached to this conduit for symmetry and
        contracted-spell integrity.

        This ensures both sides list the same spells and that every referenced
        spell is present in the **peer's contracted spellbook view**. Contract
        validation does not consult local spell registries, because contracted
        spell availability is the authoritative signal for shared usage.

        Args:
            None

        Returns:
            dict[str, bool]: Dictionary mapping contract id to validation results (True/False).

        Contract:
            This is a best-effort integrity pass over the active contract set.
            It does not mutate contracts; it only reports whether each contract
            still resolves coherently through the contracted spellbook view.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        results = {}
        with self._lock:
            for contract_id, contract in self._contracts.items():
                try:
                    valid = True
                    for ward in (contract._ward_a, contract._ward_b):
                        peer = contract._get_peer(ward)
                        peer_book = peer._conduit._spellbook
                        detail_map = contract._get_detail_map(ward)
                        for _sid, detail in detail_map.items():
                            spell = None
                            contracted_lookup_failed = False
                            try:
                                spell = peer_book._find_contracted_spell(detail.spell_index)
                            except Exception:
                                contracted_lookup_failed = True
                            if contracted_lookup_failed:
                                try:
                                    spell = peer_book._find_contracted_spell_by_id(
                                        detail.spell_id,
                                        ward._id,
                                    )
                                except Exception:
                                    spell = None
                            if spell is None:
                                valid = False
                                break
                        if not valid:
                            break
                    results[contract_id] = valid
                except Exception:
                    results[contract_id] = False
        return results


    def _validate_received_contracts(self) -> bool:
        """
        Internal

        Return whether every active contract currently validates cleanly.

        This is the boolean convenience wrapper over
        `_validate_contracts_and_define()`.

        Args:
            None

        Returns:
            bool: True if all active contracts pass validation, False otherwise.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        self.check_cleaned()
        results = self._validate_contracts_and_define()
        ok = all(results.values()) if results else False
        return ok

#endregion Spellbinding API
#endregion ConduitWard
