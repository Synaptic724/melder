"""
The immutable pre-admission request record for the mediator plane.

Dependency-free beyond the standard library by design.

Mirrors `ChangeControlTransactionRequest`, including the property that makes
admission trustworthy: the request is FROZEN BEFORE ADMISSION, so acquisition
reads a fixed snapshot and one request cannot admit differently depending on
when its fields happen to be read.
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from melder.aether.aetheric_mediator.claim_mode import ClaimMode
from melder.aether.aetheric_mediator.identity import Identity
from melder.aether.aetheric_mediator.transaction_type import TransactionType


@dataclass(frozen=True)
class TransactionRequest:
    """
    The immutable record of one transaction request, frozen before admission.

    Purpose:
        Give admission a fixed snapshot to adjudicate: what is being done, by
        whom, over which scopes, in which modes.

    Contract:
        - IMMUTABLE, and frozen BEFORE admission on purpose. Acquisition reads
          a snapshot, so the same request cannot admit differently depending on
          read timing. This is the property that makes admission deterministic
          and replayable.
        - VALUE-ONLY FIELDS. The submitter is stored as its two identity
          STRINGS rather than as an `Identity` object, honouring the repo rule
          that dataclasses carry values and containers of values only. DevOps
          does the same thing for the same reason - it stores
          `initiator_conduit_id: str`, not a conduit.
        - `scope_claims` IS COMPLETE AND EXPLICIT. Every scope key carries its
          own mode; there is NO implicit default. This DELIBERATELY DIVERGES
          from DevOps, where keys absent from `scope_claims` default to
          exclusive at admission. Implicit defaulting is how a caller silently
          takes a whole-world exclusive claim it never meant to request, which
          is precisely the failure this plane exists to end. Being explicit
          costs one tuple entry and removes a class of accident.
        - NO SCOPE HASHES. DevOps carries them as advisory identity evidence
          that explicitly "carry no claims"; with nothing here consuming them
          they would be dead weight. Add them back only with a real consumer.

    Owned State:
        Values and tuples of values only. Holds no live references.

    Threading:
        Immutable; safe to share across threads without synchronisation.

    Registration:
        MELDER KERNEL - guarded. Built from a strategy's start plan by the
        transaction manager; never user-constructed.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Immutable pre-admission transaction record carrying
        the submitter, the transaction type, and the complete scope-claim set.
    """

    request_id: str
    transaction_type: TransactionType
    submitter_kind: str
    submitter_id: str
    created_at: float
    scope_claims: Tuple[Tuple[str, str], ...] = ()
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def build(
            *,
            request_id: str,
            transaction_type: TransactionType,
            submitter: Identity,
            scope_claims: Mapping[str, ClaimMode],
            metadata: Dict[str, Any],
    ) -> "TransactionRequest":
        """
        Build one frozen request from live inputs.

        Contract:
            Normalises at the construction boundary so everything downstream
            sees one canonical shape: the submitter is flattened to its
            identity strings, and `scope_claims` is stored SORTED BY SCOPE KEY.
            Sorting is not cosmetic - it makes two requests over the same
            scopes render and compare identically in evidence and logs
            regardless of the order the caller happened to build them in.

        Args:
            request_id:
                Unique id for this request. Must be non-empty; it is the
                reporter identity in fact records and evidence.
            transaction_type:
                The closed-vocabulary operation being performed.
            submitter:
                The claimant identity. Flattened to strings on the way in.
            scope_claims:
                COMPLETE mapping of scope key to mode. Must be non-empty: a
                transaction claiming nothing is isolating nothing, and is
                almost certainly a caller bug rather than a legitimate no-op.
            metadata:
                Caller-supplied diagnostic metadata. Copied defensively so a
                later mutation by the caller cannot alter a frozen request.

        Returns:
            TransactionRequest: The frozen request.

        Raises:
            ValueError:
                If `request_id` is empty, or `scope_claims` is empty.
            TypeError:
                If any value in `scope_claims` is not a `ClaimMode`.
        """
        if not request_id or not request_id.strip():
            raise ValueError(
                "TransactionRequest requires a non-empty request_id; it is the "
                "reporter identity in evidence and fact records."
            )
        if not scope_claims:
            raise ValueError(
                "TransactionRequest requires at least one scope claim; a "
                "transaction that claims nothing isolates nothing."
            )
        normalized: list = []
        for scope_key, mode in scope_claims.items():
            if not isinstance(mode, ClaimMode):
                raise TypeError(
                    "scope_claims values must be ClaimMode; scope {0!r} got "
                    "{1!r}.".format(scope_key, mode)
                )
            normalized.append((scope_key, mode.value))
        normalized.sort(key=lambda pair: pair[0])
        return TransactionRequest(
            request_id=request_id,
            transaction_type=transaction_type,
            submitter_kind=submitter.kind,
            submitter_id=submitter.identity_id,
            created_at=time.time(),
            scope_claims=tuple(normalized),
            metadata=dict(metadata),
        )

    def claim_map(self) -> Dict[str, ClaimMode]:
        """
        Rebuild the scope-claim mapping in live `ClaimMode` form.

        Contract:
            The stored tuple form is what makes this record value-only and
            loggable; the claim table needs real modes. This is the one
            sanctioned conversion between the two.

        Returns:
            Dict[str, ClaimMode]: Scope key to mode, ready for the table.
        """
        return {
            scope_key: ClaimMode(mode_value)
            for scope_key, mode_value in self.scope_claims
        }

    def scope_keys(self) -> Tuple[str, ...]:
        """
        Return the claimed scope keys in sorted order.

        Returns:
            Tuple[str, ...]: The scope keys this request claims.
        """
        return tuple(scope_key for scope_key, _mode in self.scope_claims)

    def describe(self) -> str:
        """
        Render this request as one diagnostic line.

        Returns:
            str: The type, submitter, request id, and each scope with its mode.
        """
        claims = ", ".join(
            "{0}={1}".format(scope_key, mode_value)
            for scope_key, mode_value in self.scope_claims
        )
        return "{0} by {1}:{2} [{3}] claiming {4}".format(
            self.transaction_type.value,
            self.submitter_kind,
            self.submitter_id,
            self.request_id,
            claims,
        )
