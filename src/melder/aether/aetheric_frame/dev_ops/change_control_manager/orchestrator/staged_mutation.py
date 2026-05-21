import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING
from mypy_extensions import mypyc_attr
# Melder imports
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
        ChangeTransactionType,
    )

@mypyc_attr(native_class=True)
@dataclass(frozen=True)
class ChangeControlStagedMutation:
    """
    Immutable record describing a staged change-control mutation.

    Purpose:
        Capture the post-admission state that commit, abort, dirty-marking, and
        structural-validation hooks reason about after the original request has
        already passed admission.
    Contract:
        - Instances are immutable.
        - Preserves the admitted request identity plus the normalized scope,
          binding, and contract metadata known at staging time.
        - Serves as the canonical payload shared across commit/abort hook
          boundaries so later lifecycle steps do not need to mutate or re-read
          the original request object.
    Args:
        request_id:
            Unique identifier of the admitted request.
        request_type:
            Change-control transaction type being staged.
        staged_at:
            Unix timestamp (seconds) when staging occurred.
        initiator_conduit_id:
            Conduit id that initiated the transaction.
        spellbook_id:
            Optional spellbook id associated with the mutation.
        conduit_ids:
            Conduit ids involved in the request.
        scope_keys:
            Normalized scope keys derived for staging/embargo checks.
        binding_keys:
            Binding keys affected by the request.
        contract_keys:
            Contract keys affected by the request.
        metadata:
            Optional metadata captured from the request.
    Returns:
        None.
    Raises:
        None.
    Threading:
        Safe to share across threads because instances are immutable.
    Lifecycle:
        Immutable; no cleanup required.
    """
    __melder_internal__ = _mrg.sentinel
    request_id: str
    request_type: ChangeTransactionType
    staged_at: float
    initiator_conduit_id: str
    spellbook_id: Optional[str]
    conduit_ids: Tuple[str, ...]
    scope_keys: Tuple[str, ...]
    binding_keys: Tuple[Tuple[str, str], ...]
    contract_keys: Tuple[Tuple[str, str, str], ...]
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_request(
            cls,
            *,
            request_id: str,
            request_type: ChangeTransactionType,
            initiator_conduit_id: str,
            spellbook_id: Optional[str],
            conduit_ids: Tuple[str, ...],
            scope_keys: Tuple[str, ...],
            binding_keys: Tuple[Tuple[str, str], ...],
            contract_keys: Tuple[Tuple[str, str, str], ...],
            metadata: Optional[Dict[str, Any]] = None,
    ) -> "ChangeControlStagedMutation":
        """
        Build a staged mutation record from request metadata.

        Purpose:
            Normalize admission-time metadata into the immutable payload the
            orchestrator stores for later commit/abort processing.
        Contract:
            - `scope_keys` must already be normalized for staging/embargo use.
            - Captures a new `staged_at` timestamp while preserving the request
              identity fields supplied by the caller.
        Args:
            request_id:
                Unique request identifier.
            request_type:
                Transaction type being staged.
            initiator_conduit_id:
                Conduit id that initiated the transaction.
            spellbook_id:
                Optional spellbook id associated with the request.
            conduit_ids:
                Conduit ids involved in the request.
            scope_keys:
                Normalized scope keys for staging.
            binding_keys:
                Binding keys affected by the request.
            contract_keys:
                Contract keys affected by the request.
            metadata:
                Optional metadata captured from the request.
        Returns:
            ChangeControlStagedMutation:
                Immutable staged mutation record.
        Raises:
            None.
        Threading:
            Thread-safe without locks; no shared state is mutated.
        """
        return cls(
            request_id=request_id,
            request_type=request_type,
            staged_at=time.time(),
            initiator_conduit_id=initiator_conduit_id,
            spellbook_id=spellbook_id,
            conduit_ids=conduit_ids,
            scope_keys=scope_keys,
            binding_keys=binding_keys,
            contract_keys=contract_keys,
            metadata=dict(metadata) if metadata else {},
        )

    def with_updates(
            self,
            *,
            scope_keys: Optional[Tuple[str, ...]] = None,
            binding_keys: Optional[Tuple[Tuple[str, str], ...]] = None,
            contract_keys: Optional[Tuple[Tuple[str, str, str], ...]] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> "ChangeControlStagedMutation":
        """
        Return a new staged mutation with updated metadata.

        Purpose:
            Produce a new immutable staged record that preserves identity and
            staging time while allowing later orchestration steps to refine the
            discovered scope, binding, contract, or metadata fields.
        Contract:
            - `request_id`, `request_type`, and `staged_at` are preserved.
            - None values keep the existing field data.
            - metadata merges into the existing metadata when provided instead
              of replacing it wholesale.
        Args:
            scope_keys:
                Optional replacement scope keys for the staged record.
            binding_keys:
                Optional replacement binding keys for the staged record.
            contract_keys:
                Optional replacement contract keys for the staged record.
            metadata:
                Optional metadata to merge into the staged record.
        Returns:
            ChangeControlStagedMutation:
                A new immutable staged mutation record.
        Raises:
            None.
        Threading:
            Thread-safe without locks; no shared state is mutated.
        """
        merged_metadata = dict(self.metadata)
        if metadata is not None:
            merged_metadata.update(metadata)
        return ChangeControlStagedMutation(
            request_id=self.request_id,
            request_type=self.request_type,
            staged_at=self.staged_at,
            initiator_conduit_id=self.initiator_conduit_id,
            spellbook_id=self.spellbook_id,
            conduit_ids=self.conduit_ids,
            scope_keys=scope_keys if scope_keys is not None else self.scope_keys,
            binding_keys=binding_keys if binding_keys is not None else self.binding_keys,
            contract_keys=contract_keys if contract_keys is not None else self.contract_keys,
            metadata=merged_metadata,
        )
