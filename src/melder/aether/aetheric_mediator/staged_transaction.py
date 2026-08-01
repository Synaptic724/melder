"""
The immutable post-admission record for the mediator plane.

Dependency-free beyond the standard library.

Mirrors `ChangeControlStagedMutation`: the inverse of the pre-admission request.
A request is what was ASKED FOR; a staged transaction is what was GRANTED, and
it is what commit-time hooks adjudicate against.
"""

from dataclasses import dataclass, field
from typing import Any, Mapping, Tuple

from melder.aether.aetheric_mediator.transaction_request import (
    MetadataPolicy,
    TransactionRequest,
)
from melder.aether.aetheric_mediator.transaction_type import TransactionType


@dataclass(frozen=True)
class StagedTransaction:
    """
    The immutable record of one admitted transaction.

    Purpose:
        Give commit-time work a fixed, detached view of what was admitted,
        without handing it the live session or the claim table.

    Contract:
        - IMMUTABLE and VALUE-ONLY, so it is safe to log, ship, retain, or
          hand to a strategy that should not be able to mutate live state.
          `metadata` is carried forward from a `TransactionRequest`, which
          already validated it through `MetadataPolicy`, so it is value-only
          by construction rather than by convention. It is re-copied here so
          the two records never share a mutable dict.
        - It records what was GRANTED, not what was requested. For this plane
          those coincide, because admission is all-or-nothing - a partial
          grant is impossible by construction. Keeping them as separate types
          anyway preserves the distinction for any future admission that
          could narrow a claim set.
        - `granted_scopes` is sorted, matching the request's normalisation, so
          two staged records over the same scopes render identically.

    Threading:
        Immutable; safe to share across threads.

    Registration:
        MELDER KERNEL - guarded. Built at admission; never user-constructed.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Immutable post-admission record of one granted
        transaction, consumed by commit-time hooks and reporting.
    """

    request_id: str
    transaction_type: TransactionType
    submitter_kind: str
    submitter_id: str
    admitted_at: float
    granted_scopes: Tuple[str, ...] = ()
    # Read-only, and the SAME OBJECT the request carries - see `from_request`.
    metadata: Mapping[str, Any] = field(default_factory=MetadataPolicy.empty)

    @staticmethod
    def from_request(
            *,
            request: TransactionRequest,
            admitted_at: float,
    ) -> "StagedTransaction":
        """
        Build the staged record for one admitted request.

        Contract:
            CALLED EXACTLY ONCE PER TRANSACTION, at admission. The result is
            carried on the `TransactionSession`, and commit and failure read it
            from there. Rebuilding it per phase would reallocate the record on
            every call and - worse - restamp `admitted_at` with the time of
            that call, so the field would report the commit moment while
            claiming to report admission.

            The metadata mapping is SHARED WITH THE REQUEST, not copied. It is
            deeply frozen by `MetadataPolicy`, so there is nothing to defend
            against: no holder of either record can mutate it. Copying would
            allocate a second structure per transaction, purely to guard a
            mutability that no longer exists, and would leave two objects for
            the finishing thread to release instead of one.

        Args:
            request: The frozen request that was just admitted.
            admitted_at: Unix timestamp of admission.

        Returns:
            StagedTransaction: The immutable post-admission record.
        """
        return StagedTransaction(
            request_id=request.request_id,
            transaction_type=request.transaction_type,
            submitter_kind=request.submitter_kind,
            submitter_id=request.submitter_id,
            admitted_at=admitted_at,
            granted_scopes=request.scope_keys(),
            metadata=request.metadata,
        )

    def regions(self) -> Tuple[str, ...]:
        """
        Return the fact-record regions this transaction touched.

        Contract:
            Regions ARE the granted scope keys here. DevOps derives regions
            separately (`spellbook:<id>`, `conduit:<id>`) because its scope
            keys carry lock-owner structure that is not one-to-one with the
            things it reports on. This plane's keys already name exactly the
            units it isolates, so the mapping is the identity - and saying so
            explicitly is better than reimplementing a translation that would
            only ever be a no-op.

        Returns:
            Tuple[str, ...]: The regions to stamp at commit.
        """
        return self.granted_scopes

    def describe(self) -> str:
        """
        Render this staged transaction as one diagnostic line.

        Returns:
            str: Type, submitter, request id, and granted scopes.
        """
        return "{0} by {1}:{2} [{3}] granted {4}".format(
            self.transaction_type.value,
            self.submitter_kind,
            self.submitter_id,
            self.request_id,
            ", ".join(self.granted_scopes),
        )
