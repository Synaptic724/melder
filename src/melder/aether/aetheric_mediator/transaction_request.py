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
from types import MappingProxyType
from typing import Any, Dict, Mapping, Tuple

from melder.aether.aetheric_mediator.claim_mode import ClaimMode
from melder.aether.aetheric_mediator.identity import Identity
from melder.aether.aetheric_mediator.transaction_type import TransactionType


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
              same way. `@dataclass(frozen=True)` only blocks REBINDING a
              field; it does nothing about `record.metadata["k"] = v`. A plain
              `Dict` field therefore leaves a record that advertises itself as
              immutable, safe to log, and safe to retain, while any holder can
              quietly edit it. Freezing here makes the promise true instead of
              aspirational.
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
    # A READ-ONLY mapping, not a `Dict`. `frozen=True` stops the field being
    # rebound; it does not stop a holder mutating the dict the field points
    # at. `MetadataPolicy.normalize` returns a deeply frozen structure - proxy
    # mappings and tuples all the way down - so this annotation describes what
    # the field can actually do. `Any` remains because the permitted value
    # domain is recursive; `MetadataPolicy` defines and ENFORCES it.
    metadata: Mapping[str, Any] = field(default_factory=MetadataPolicy.empty)

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
