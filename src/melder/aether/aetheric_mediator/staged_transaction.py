"""
The immutable post-admission record for the mediator plane.

Dependency-free beyond the standard library.

Mirrors `ChangeControlStagedMutation`: the inverse of the pre-admission request.
A request is what was ASKED FOR; a staged transaction is what was GRANTED, and
it is what commit-time hooks adjudicate against.
"""

from typing import Any, Mapping, Optional, Tuple

from melder.aether.aetheric_mediator.transaction_request import (
    MetadataPolicy,
    TransactionRequest,
)
from melder.aether.aetheric_mediator.transaction_type import TransactionType
from melder.utilities.general_base.cleanable import Cleanable


class StagedTransaction(Cleanable):
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

    Lifecycle / Cleanup:
        `Cleanable`, cleaned by ONE owner at ONE moment:
        `TransactionSession.cleanup()`, exactly like the request it was built
        from. The session owns both records for the life of the transaction.

        `InformationRegistry._active` BORROWS this record while the
        transaction is live and drops it at `unregister_activity`, which the
        mediator calls from `_finalize`. A borrower must not clean it: the
        session stays readable after commit so a caller can inspect what it
        just did, and reporting must never be the thing that revokes that.

        ORDERING THIS DEPENDS ON: `Mediator.cleanup` tears down the
        information registry BEFORE the sessions. Cleaning sessions first
        would leave the registry holding cleaned staged records, and a
        concurrent `describe()` during teardown would then raise from inside
        reporting rather than reporting an empty plane.

        NOTE ON THE SHARED MAPPING: `metadata` is the SAME object the request
        carries. Both records clean it, and both are correct - each `del`s its
        own slot; neither mutates the frozen mapping, and whichever runs
        second simply drops the last reference.

    Threading:
        Immutable after construction; safe to share across threads. No lock -
        there is no mutable state, and the single teardown is serialised by
        the owning session.

    Registration:
        MELDER KERNEL - guarded. Built at admission; never user-constructed.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Immutable post-admission record of one granted
        transaction, consumed by commit-time hooks and reporting. Cleanable;
        cleaned by the owning session at teardown.
    """

    __slots__ = Cleanable.__slots__ + [
        "_request_id",
        "_transaction_type",
        "_submitter_kind",
        "_submitter_id",
        "_admitted_at",
        "_granted_scopes",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            request_id: str,
            transaction_type: TransactionType,
            submitter_kind: str,
            submitter_id: str,
            admitted_at: float,
            granted_scopes: Tuple[str, ...] = (),
            metadata: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """
        Build one post-admission record.

        Contract:
            Prefer the `from_request(...)` factory - it is the path that
            guarantees this record is built exactly once per transaction, at
            admission, with an honest `admitted_at`.

        Args:
            request_id: The admitted request's id.
            transaction_type: The closed-vocabulary operation.
            submitter_kind: The submitter identity's family.
            submitter_id: The submitter identity's id within that family.
            admitted_at: Unix timestamp of admission.
            granted_scopes: The sorted scope keys actually granted.
            metadata: The request's deeply frozen mapping, or None for empty.

        Returns:
            None.
        """
        super().__init__()
        self._request_id: str = request_id
        self._transaction_type: TransactionType = transaction_type
        self._submitter_kind: str = submitter_kind
        self._submitter_id: str = submitter_id
        self._admitted_at: float = admitted_at
        self._granted_scopes: Tuple[str, ...] = granted_scopes
        # Read-only, and the SAME OBJECT the request carries - see
        # `from_request` for why it is shared rather than copied.
        self._metadata: Mapping[str, Any] = (
            MetadataPolicy.empty() if metadata is None else metadata
        )

    def cleanup(self) -> None:
        """
        Idempotently drop this record's fields at the owning session's teardown.

        Contract:
            Called from `TransactionSession.cleanup()` and nowhere else. Every
            accessor raises afterwards, which is the honest outcome: a cleaned
            staged record describes a transaction whose owner is gone.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._request_id
        del self._transaction_type
        del self._submitter_kind
        del self._submitter_id
        del self._admitted_at
        del self._granted_scopes
        del self._metadata

    @property
    def request_id(self) -> str:
        """
        Return the admitted request's id.

        Returns:
            str: The request id, used as the reporter in fact records.

        Raises:
            RuntimeError: If the record has been cleaned.
        """
        self.check_cleaned()
        return self._request_id

    @property
    def transaction_type(self) -> TransactionType:
        """
        Return the closed-vocabulary operation that was admitted.

        Returns:
            TransactionType: The vocabulary member.

        Raises:
            RuntimeError: If the record has been cleaned.
        """
        self.check_cleaned()
        return self._transaction_type

    @property
    def submitter_kind(self) -> str:
        """
        Return the submitting identity's family.

        Returns:
            str: The submitter kind string.

        Raises:
            RuntimeError: If the record has been cleaned.
        """
        self.check_cleaned()
        return self._submitter_kind

    @property
    def submitter_id(self) -> str:
        """
        Return the submitting identity's id within its family.

        Returns:
            str: The submitter id string.

        Raises:
            RuntimeError: If the record has been cleaned.
        """
        self.check_cleaned()
        return self._submitter_id

    @property
    def admitted_at(self) -> float:
        """
        Return when admission granted this transaction's claims.

        Contract:
            ADMISSION time, stamped once. It is not restamped at commit or
            failure; a record that moved this field would report the wrong
            moment while appearing authoritative.

        Returns:
            float: Unix timestamp of admission.

        Raises:
            RuntimeError: If the record has been cleaned.
        """
        self.check_cleaned()
        return self._admitted_at

    @property
    def granted_scopes(self) -> Tuple[str, ...]:
        """
        Return the scope keys this transaction actually holds, sorted.

        Returns:
            Tuple[str, ...]: The granted scope keys.

        Raises:
            RuntimeError: If the record has been cleaned.
        """
        self.check_cleaned()
        return self._granted_scopes

    @property
    def metadata(self) -> Mapping[str, Any]:
        """
        Return the deeply frozen, value-only metadata carried from the request.

        Returns:
            Mapping[str, Any]: The frozen metadata mapping.

        Raises:
            RuntimeError: If the record has been cleaned.
        """
        self.check_cleaned()
        return self._metadata

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
