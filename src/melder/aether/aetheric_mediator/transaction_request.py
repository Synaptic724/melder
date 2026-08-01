"""
The immutable pre-admission request record for the mediator plane.

Dependency-free beyond the standard library by design.

Mirrors `ChangeControlTransactionRequest`, including the property that makes
admission trustworthy: the request is FROZEN BEFORE ADMISSION, so acquisition
reads a fixed snapshot and one request cannot admit differently depending on
when its fields happen to be read.
"""

import time
from types import MappingProxyType
from typing import Any, Dict, Mapping, Optional, Tuple

from melder.aether.aetheric_mediator.claim_mode import ClaimMode
from melder.aether.aetheric_mediator.identity import Identity
from melder.aether.aetheric_mediator.transaction_type import TransactionType
from melder.utilities.general_base.cleanable import Cleanable


class MetadataPolicy:
    """
    The value-only guard for transaction metadata.

    Purpose:
        Enforce - rather than merely document - the rule that a frozen
        transaction record carries VALUES ONLY, so it stays detached, safe to
        log, safe to ship, and safe to retain after the runtime objects it
        describes are gone.

    Contract:
        - PERMITTED: `None`, `bool`, `int`, `float`, `str` (which covers
          `StrEnum` members), and `tuple`/`list`/`dict` recursively composed of
          those. Dict keys must be `str`.
        - REJECTED: everything else, loudly, at the construction boundary.
        - The rejection is deliberate and it is the whole point. Metadata is
          caller-supplied and typed `Any` in the DevOps plane, which means a
          caller can put a live `Conduit` or `Spellbook` into what is supposed
          to be a detached record. That reference then outlives the object's
          own lifecycle, defeats `describe()`, and turns a loggable payload
          into a liveness leak. Failing at construction costs one traversal of
          a small dict; failing later costs a debugging session.

    Lifecycle / Cleanup:
        NEVER INSTANTIATED, so there is nothing to clean and no `Cleanable`
        contract. Two static methods over caller-supplied mappings; the
        records they validate carry the lifecycle, not this.

    Threading:
        Pure and stateless.

    Registration:
        MELDER KERNEL - guarded. Policy helper; never bound.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Value-only guard for transaction metadata. Rejects
        object references at the construction boundary.
    """

    @staticmethod
    def empty() -> Mapping[str, Any]:
        """
        Return the frozen empty metadata mapping.

        Contract:
            Exists so the dataclass default can be an IMMUTABLE mapping without
            a module-level constant. Cheap: an empty dict and a proxy over it.

        Returns:
            Mapping[str, Any]: A read-only empty mapping.
        """
        return MappingProxyType({})

    @staticmethod
    def normalize(metadata: Mapping[str, Any], owner: str) -> Mapping[str, Any]:
        """
        Return a DEEPLY FROZEN copy of `metadata`, rejecting non-value content.

        Contract:
            - Copies once, at the construction boundary, so a later caller
              mutation cannot reach into a frozen record.
            - Returns a READ-ONLY view, and freezes every nested container the
              same way. A read-only ATTRIBUTE does nothing about
              `record.metadata["k"] = v`: the property refuses to rebind the
              field, and the holder edits the mapping the field points at
              instead. A plain `Dict` therefore leaves a record that
              advertises itself as immutable, safe to log, and safe to retain,
              while any holder can quietly edit it. Freezing here makes the
              promise true instead of aspirational.
              (This reasoning predates the conversion of these records from
              frozen dataclasses to normal classes and survives it unchanged -
              `frozen=True` had exactly the same blind spot, which is why the
              deep freeze was introduced in the first place.)
            - Because the result is genuinely immutable it is SAFE TO SHARE.
              That is what lets `StagedTransaction` carry the request's own
              mapping instead of re-copying it, removing a per-transaction
              allocation whose only purpose was defending against a mutability
              this method no longer permits.

        Args:
            metadata: The caller-supplied mapping.
            owner: What is being built, used in the error message.

        Returns:
            Mapping[str, Any]: A read-only, deeply frozen copy.

        Raises:
            TypeError: If any key is not a `str`, or any value is not a
                permitted value type or a container of them.
        """
        normalized: Dict[str, Any] = {}
        for key, value in metadata.items():
            if not isinstance(key, str):
                raise TypeError(
                    "{0} metadata keys must be str; got {1!r}.".format(owner, key)
                )
            normalized[key] = MetadataPolicy._check_value(value, owner, key)
        return MappingProxyType(normalized)

    @staticmethod
    def _check_value(value: Any, owner: str, path: str) -> Any:
        """
        Validate one metadata value, recursing into containers.

        Contract:
            Containers come back FROZEN, not merely copied: sequences become
            `tuple`, mappings become read-only views. A shallow copy of the top
            level would still hand out mutable nested lists and dicts, so the
            record would only look detached one level down.

        Args:
            value: The value to validate.
            owner: What is being built, for the error message.
            path: The key path reached so far, for the error message.

        Returns:
            Any: The value, frozen when it is a container.

        Raises:
            TypeError: If the value is not a permitted value or container.
        """
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        if isinstance(value, (tuple, list)):
            return tuple(
                MetadataPolicy._check_value(item, owner, "{0}[{1}]".format(path, index))
                for index, item in enumerate(value)
            )
        if isinstance(value, dict):
            nested: Dict[str, Any] = {}
            for nested_key, nested_value in value.items():
                if not isinstance(nested_key, str):
                    raise TypeError(
                        "{0} metadata keys must be str; got {1!r} under "
                        "{2!r}.".format(owner, nested_key, path)
                    )
                nested[nested_key] = MetadataPolicy._check_value(
                    nested_value, owner, "{0}.{1}".format(path, nested_key)
                )
            return MappingProxyType(nested)
        raise TypeError(
            "{0} metadata must be VALUE-ONLY so the frozen record stays "
            "detached and loggable; {1!r} at {2!r} is a {3}. Pass an "
            "identifier (for example a conduit id) rather than the live "
            "object.".format(owner, value, path, type(value).__name__)
        )


class TransactionRequest(Cleanable):
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
        - VALUE-ONLY FIELDS, ENFORCED NOT ASSUMED. The submitter is stored as
          its two identity STRINGS rather than as an `Identity` object,
          honouring the repo rule that dataclasses carry values and containers
          of values only. DevOps does the same thing for the same reason - it
          stores `initiator_conduit_id: str`, not a conduit.
          `metadata` DIVERGES from the DevOps field shape, which is a plain
          `Dict[str, Any]`: here it is validated through
          `MetadataPolicy.normalize` at construction and stored as a DEEPLY
          FROZEN read-only mapping. The validation stops `Any` from admitting
          an object reference; the freezing stops a holder from editing a
          record this class promises is detached. A `Dict` field would leave
          both doors open, because `frozen=True` guards rebinding only.
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

    Lifecycle / Cleanup:
        `Cleanable`, and cleaned by ONE owner at ONE moment:
        `TransactionSession.cleanup()`. The session is the per-transaction
        owner and its teardown is this record's genuine end of life.

        WHY NOT THE ORCHESTRATOR, which also holds it: `_in_flight` BORROWS
        this record for the span between admission and release. A borrower
        that cleaned it would tear down state its owner is still publishing -
        the caller can legitimately read `session.request` after commit to
        find out what it just did. `AdmissionOrchestrator.cleanup` therefore
        clears its dict without cleaning the values, the same way it already
        refuses to release claims in the table it borrows.

        NOT CLEANED MID-RUN. Release, commit, and failure are ordinary runtime
        activity; none of them ends this record's life, because the session
        outlives all three and stays readable on purpose.

        `Mediator.cleanup` orders teardown accordingly: BORROWERS FIRST
        (strategy registry, information registry, orchestrator), then the
        sessions that own these records, then the claim table last.

    Threading:
        Immutable after construction; safe to share across threads without
        synchronisation. No lock, deliberately - there is no mutable state to
        guard, and cleanup happens once at the owning session's teardown.

    Registration:
        MELDER KERNEL - guarded. Built from a strategy's start plan by the
        transaction manager; never user-constructed.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Immutable pre-admission transaction record carrying
        the submitter, the transaction type, and the complete scope-claim set.
        Cleanable; cleaned by the owning session at teardown.
    """

    __slots__ = Cleanable.__slots__ + [
        "_request_id",
        "_transaction_type",
        "_submitter_kind",
        "_submitter_id",
        "_created_at",
        "_scope_claims",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            request_id: str,
            transaction_type: TransactionType,
            submitter_kind: str,
            submitter_id: str,
            created_at: float,
            scope_claims: Tuple[Tuple[str, str], ...] = (),
            metadata: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """
        Build one frozen request record.

        Contract:
            Prefer the `build(...)` factory, which normalises the submitter,
            sorts the claims, and validates the metadata. This constructor
            performs no normalisation and exists so `build` has something to
            construct.

            `metadata` defaults to `None` rather than to a shared empty
            mapping so no mutable default is ever shared; the empty case
            resolves to `MetadataPolicy.empty()`, a read-only proxy.

        Args:
            request_id: Unique id for this request.
            transaction_type: The closed-vocabulary operation.
            submitter_kind: The submitter identity's family.
            submitter_id: The submitter identity's id within that family.
            created_at: Unix timestamp of construction.
            scope_claims: Sorted `(scope_key, mode_value)` pairs.
            metadata: Deeply frozen value-only mapping, or None for empty.

        Returns:
            None.
        """
        super().__init__()
        self._request_id: str = request_id
        self._transaction_type: TransactionType = transaction_type
        self._submitter_kind: str = submitter_kind
        self._submitter_id: str = submitter_id
        self._created_at: float = created_at
        self._scope_claims: Tuple[Tuple[str, str], ...] = scope_claims
        # A READ-ONLY mapping, not a `Dict`. `MetadataPolicy.normalize`
        # returns a deeply frozen structure - proxy mappings and tuples all
        # the way down - so this annotation describes what the field can
        # actually do. `Any` remains because the permitted value domain is
        # recursive; `MetadataPolicy` defines and ENFORCES it.
        self._metadata: Mapping[str, Any] = (
            MetadataPolicy.empty() if metadata is None else metadata
        )

    def cleanup(self) -> None:
        """
        Idempotently drop this record's fields at the owning session's teardown.

        Contract:
            Called from `TransactionSession.cleanup()` and from nowhere else.
            After this runs every accessor raises, which is correct: a cleaned
            request describes a transaction whose owner is gone.

            No lock is taken. The record is immutable, so there is no state a
            concurrent reader could catch half-changed, and adding a lock here
            would put one on an object allocated once per transaction purely
            to guard a single teardown that its owner already serialises.

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
        del self._created_at
        del self._scope_claims
        del self._metadata

    @property
    def request_id(self) -> str:
        """
        Return the unique id of this request.

        Returns:
            str: The request id, which is also the reporter identity in fact
                records and admission evidence.

        Raises:
            RuntimeError: If the record has been cleaned.
        """
        self.check_cleaned()
        return self._request_id

    @property
    def transaction_type(self) -> TransactionType:
        """
        Return the closed-vocabulary operation being performed.

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
    def created_at(self) -> float:
        """
        Return when this request was built.

        Contract:
            Construction time, NOT admission time. Admission time lives on
            `StagedTransaction.admitted_at`, and conflating the two is how a
            report starts describing the wrong moment.

        Returns:
            float: Unix timestamp of construction.

        Raises:
            RuntimeError: If the record has been cleaned.
        """
        self.check_cleaned()
        return self._created_at

    @property
    def scope_claims(self) -> Tuple[Tuple[str, str], ...]:
        """
        Return the complete `(scope_key, mode_value)` claim set, sorted.

        Contract:
            COMPLETE and EXPLICIT - every claimed scope carries its own mode
            and there is no implicit default. Stored in string form so the
            record stays value-only; `claim_map()` is the one sanctioned
            conversion back to live `ClaimMode` values.

        Returns:
            Tuple[Tuple[str, str], ...]: Sorted claim pairs.

        Raises:
            RuntimeError: If the record has been cleaned.
        """
        self.check_cleaned()
        return self._scope_claims

    @property
    def metadata(self) -> Mapping[str, Any]:
        """
        Return the deeply frozen, value-only diagnostic metadata.

        Contract:
            READ-ONLY at every depth - proxy mappings and tuples all the way
            down, enforced by `MetadataPolicy` at construction. Safe to share:
            `StagedTransaction` carries this same object rather than copying
            it, because there is no mutability left to defend against.

        Returns:
            Mapping[str, Any]: The frozen metadata mapping.

        Raises:
            RuntimeError: If the record has been cleaned.
        """
        self.check_cleaned()
        return self._metadata

    @staticmethod
    def build(
            *,
            request_id: str,
            transaction_type: TransactionType,
            submitter: Identity,
            scope_claims: Mapping[str, ClaimMode],
            metadata: Mapping[str, Any],
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
                Caller-supplied diagnostic metadata. VALUE-ONLY: validated and
                deep-copied through `MetadataPolicy`, so a later caller
                mutation cannot alter a frozen request and no live object can
                be smuggled into a record that must stay detached.

        Returns:
            TransactionRequest: The frozen request.

        Raises:
            ValueError:
                If `request_id` is empty, or `scope_claims` is empty.
            TypeError:
                If any value in `scope_claims` is not a `ClaimMode`, or if
                `metadata` contains anything other than values and containers
                of values.
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
            metadata=MetadataPolicy.normalize(metadata, "TransactionRequest"),
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
