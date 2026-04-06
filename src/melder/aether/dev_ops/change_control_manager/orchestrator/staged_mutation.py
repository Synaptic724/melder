import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)


@dataclass(frozen=True)
class ChangeControlStagedMutation:
    """
    Immutable snapshot of one admitted change-control request.

    `ChangeControlStagedMutation` is the record the orchestrator keeps after a
    request is admitted. It captures the normalized scope, binding, contract,
    and metadata fields that later commit/abort hooks need in order to make
    deterministic decisions without reaching back into mutable request objects.

    Contract:
    - Instances are immutable and safe to share across threads.
    - `staged_at` is captured once and preserved across later updates.
    - Update flows create a new record instead of mutating the old one.
    - `scope_keys`, `binding_keys`, and `contract_keys` represent the
      orchestrator's normalized view of the admitted request at that moment in
      time, not a live pointer back to mutable request state.
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
        Build one staged record from admitted request metadata.

        Caller contract:
        - `scope_keys` should already be normalized for staging/embargo use.
        - tuple inputs are taken as the canonical staged values for this
          snapshot; they are not normalized again here.

        Args:
            request_id: Unique identifier of the admitted request.
            request_type: Transaction type being staged.
            initiator_conduit_id: Conduit id that initiated the request.
            spellbook_id: Optional spellbook id associated with the request.
            conduit_ids: Conduit ids involved in the request.
            scope_keys: Normalized scope keys used for staging and embargo
                bookkeeping.
            binding_keys: Binding keys affected by the admitted request.
            contract_keys: Contract keys affected by the admitted request.
            metadata: Optional metadata copied into the staged snapshot.

        Returns:
            ChangeControlStagedMutation: Immutable staged mutation record for
            the admitted request.
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
        Return a new staged record with selected fields updated.

        This preserves the original request identity and staging time while
        letting the orchestrator refresh scope, binding, contract, or metadata
        fields discovered after admission.

        Contract:
        - `request_id`, `request_type`, and `staged_at` are preserved.
        - `None` keeps the existing field value.
        - incoming metadata merges into the existing metadata map.

        Args:
            scope_keys: Optional replacement scope keys for the staged record.
            binding_keys: Optional replacement binding keys for the staged
                record.
            contract_keys: Optional replacement contract keys for the staged
                record.
            metadata: Optional metadata merged onto the existing metadata map.

        Returns:
            ChangeControlStagedMutation: New immutable snapshot preserving the
            original request identity and stage time.
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
