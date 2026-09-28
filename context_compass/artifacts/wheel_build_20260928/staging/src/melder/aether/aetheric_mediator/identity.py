"""
Claimant identity for the mediator plane.

Dependency-free beyond the standard library by design: the plane is constructed
before any `AethericFrame` exists, so nothing here may import `melder.aether`.

Identity is the pivot the whole plane turns on. Sessions are keyed per identity,
which is what allows a holder to re-enter its own span (a join) instead of
deadlocking against itself, and what lets blocking evidence name a real culprit
rather than a bare thread id.
"""

from typing import Optional

from melder.utilities.general_base.cleanable import Cleanable


class Identity(Cleanable):
    """
    The immutable identity of one claimant on the mediator plane.

    Purpose:
        Name WHO holds or requests a claim, in a form that is stable across
        the life of a span, hashable enough to key a holder table, and
        legible enough that a timeout message points at something a human
        or agent can act on.

    Contract:
        - IMMUTABLE after construction. Every field is read-only through a
          property; there is no setter and no rebind path.
        - Value equality and hashing are over `(kind, identity_id)` ONLY.
          `label` is presentation and is deliberately excluded, so two
          references to the same claimant compare equal even when one was
          constructed with a friendlier label.
        - `thread_ident` is CARRIED, NOT COMPARED. A span may legitimately
          be entered from more than one thread (an enrolled worker cohort),
          so thread identity is diagnostic evidence rather than part of the
          identity itself.

    Lifecycle / Cleanup:
        `Cleanable`, and CALLER-OWNED. This is the one type here the plane
        does not own: a subsystem constructs its identity, hands it in, and
        keeps it. The plane BORROWS it for the life of a transaction, so
        nothing inside this package ever calls `cleanup()` on one - the same
        rule `AdmissionOrchestrator` follows for the claim table it borrows.
        The contract exists so the OWNING subsystem can release it at ITS end
        of life, which is the only place that knows when that is.

        WHY THIS WAS NOT SAFE UNTIL THE SESSION MAPS WERE REKEYED, recorded
        because it is the trap a future reader would otherwise re-enter: the
        mediator used to key its per-thread session maps on the Identity
        OBJECT. Cleaning one deletes the fields `__hash__` reads, so a cleaned
        identity raises from `__hash__` and every map still holding it as a
        key is corrupt - lookups miss, and the entry can never be removed.
        `Mediator` now keys on `identity_key()`, a plain string captured at
        insertion, so a caller cleaning its own identity can no longer reach
        into the plane's bookkeeping. An earlier revision of this docstring
        said this type "must not" be `Cleanable` for exactly that reason; the
        reason was real, and it was fixed rather than argued with.

        `__eq__` and `__hash__` REFUSE on a cleaned identity rather than
        raising `AttributeError` from a deleted slot. A loud, named failure at
        the point of misuse beats a mangled traceback from inside a dict.

    Owned State:
        Three immutable strings plus one optional integer. No collections,
        no references to runtime objects.

    Threading:
        Safe to share freely. Immutability is the whole thread-safety
        story; no lock is needed or provided. Cleanup is the owning
        subsystem's single terminal act, not concurrent activity.

    Registration:
        MELDER KERNEL - guarded. Constructed by plane callers; never bound
        as a spell.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Immutable identity of one claimant on the aetheric
        plane. Sessions key on it and blocking evidence names it.
    """

    __slots__ = Cleanable.__slots__ + [
        "_kind", "_identity_id", "_label", "_thread_ident",
    ]

    def __init__(
            self,
            *,
            kind: str,
            identity_id: str,
            label: Optional[str] = None,
            thread_ident: Optional[int] = None,
    ) -> None:
        """
        Build one immutable claimant identity.

        Args:
            kind:
                Subsystem family this claimant belongs to, lowercase and
                stable - for example "crystallizer", "nexus",
                "mutation_research". Used as the namespace half of the
                identity and echoed in blocking evidence.
            identity_id:
                Stable id within `kind`. Must be non-empty; a blank id
                would make two unrelated claimants compare equal.
            label:
                Optional human/agent-facing description used only in
                diagnostics. Excluded from equality and hashing.
            thread_ident:
                Optional originating thread id, carried as diagnostic
                evidence. Never part of identity.

        Raises:
            ValueError:
                If `kind` or `identity_id` is empty or whitespace-only,
                because an unnameable claimant cannot be reported in a
                timeout and cannot be safely keyed.

        Returns:
            None.
        """
        if not kind or not kind.strip():
            raise ValueError(
                "Identity requires a non-empty 'kind'; an unnamed "
                "claimant cannot be reported as a blocking holder."
            )
        if not identity_id or not identity_id.strip():
            raise ValueError(
                "Identity requires a non-empty 'identity_id'; a blank "
                "id would make unrelated claimants compare equal."
            )
        super().__init__()
        self._kind: str = kind
        self._identity_id: str = identity_id
        self._label: Optional[str] = label
        self._thread_ident: Optional[int] = thread_ident

    def cleanup(self) -> None:
        """
        Idempotently release this identity's fields.

        Contract:
            CALLED BY THE OWNING SUBSYSTEM, NEVER BY THE PLANE. Nothing inside
            `aetheric_mediator` cleans an identity it was handed - it is
            borrowed for the life of a transaction, and cleaning a borrowed
            object is how one component tears down another's state.

            Clean only once the identity is finished submitting work. A
            cleaned identity refuses equality and hashing, so any claim still
            held under it, and any session still keyed to it, must be
            finalised first.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._kind
        del self._identity_id
        del self._label
        del self._thread_ident

    def identity_key(self) -> str:
        """
        Return the stable string form used to key maps on this identity.

        Purpose:
            Let callers index by identity WITHOUT holding the object as a
            dict key, so a later `cleanup()` cannot corrupt their map.

        Contract:
            `"<kind>:<identity_id>"` - the same pair equality and hashing use,
            so two identities equal under `__eq__` produce the same key. It is
            a plain string: capture it at insertion and the map keeps working
            no matter what happens to the identity afterwards.

            `Mediator` keys its per-thread session maps on this rather than on
            the identity object, which is what makes `Identity` safe to make
            `Cleanable` at all.

        Returns:
            str: The stable map key.

        Raises:
            RuntimeError: If the identity has been cleaned.
        """
        self.check_cleaned()
        return "{0}:{1}".format(self._kind, self._identity_id)

    @property
    def kind(self) -> str:
        """
        Return the subsystem family this claimant belongs to.

        Returns:
            str: The stable lowercase family name.

        Raises:
            RuntimeError: If the identity has been cleaned.
        """
        self.check_cleaned()
        return self._kind

    @property
    def identity_id(self) -> str:
        """
        Return the stable id of this claimant within its family.

        Returns:
            str: The identity id.

        Raises:
            RuntimeError: If the identity has been cleaned.
        """
        self.check_cleaned()
        return self._identity_id

    @property
    def label(self) -> Optional[str]:
        """
        Return the optional diagnostic label, if one was supplied.

        Returns:
            Optional[str]: The label, or None when none was given.

        Raises:
            RuntimeError: If the identity has been cleaned.
        """
        self.check_cleaned()
        return self._label

    @property
    def thread_ident(self) -> Optional[int]:
        """
        Return the originating thread id carried as diagnostic evidence.

        Contract:
            This is NOT part of identity and never participates in equality.

        Returns:
            Optional[int]: The thread id, or None when none was supplied.

        Raises:
            RuntimeError: If the identity has been cleaned.
        """
        self.check_cleaned()
        return self._thread_ident

    def describe(self) -> str:
        """
        Render this identity for a diagnostic message.

        Contract:
            Stable, single-line, and safe to embed in a raised error. Adds
            the label and thread only when present so the common form stays
            short.

        Returns:
            str: A one-line rendering such as
                `crystallizer:checkpoint_load:01J...` optionally followed by
                the label and thread.

        Raises:
            RuntimeError: If the identity has been cleaned.
        """
        self.check_cleaned()
        rendered = "{0}:{1}".format(self._kind, self._identity_id)
        if self._label is not None:
            rendered = "{0} ({1})".format(rendered, self._label)
        if self._thread_ident is not None:
            rendered = "{0} [thread {1}]".format(rendered, self._thread_ident)
        return rendered

    def __eq__(self, other: object) -> bool:
        """
        Compare on `(kind, identity_id)` only.

        Args:
            other:
                The object to compare against.

        Returns:
            bool:
                True when `other` is an `Identity` with the same
                kind and id. `NotImplemented` is returned for foreign types
                so Python can fall back to the reflected comparison.
        """
        if not isinstance(other, Identity):
            return NotImplemented
        # BOTH SIDES ARE GUARDED. Comparing against a cleaned identity would
        # otherwise raise `AttributeError` from a deleted slot, several frames
        # away from the mistake. Refusing here names the actual problem.
        self.check_cleaned()
        other.check_cleaned()
        return (
            self._kind == other._kind
            and self._identity_id == other._identity_id
        )

    def __hash__(self) -> int:
        """
        Hash on `(kind, identity_id)`, matching equality exactly.

        Contract:
            REFUSES on a cleaned identity. A cleaned identity has no stable
            hash - its fields are gone - and silently returning some other
            value would corrupt every map holding it. Callers that need a key
            surviving cleanup use `identity_key()`, which is why the mediator
            does exactly that.

        Returns:
            int: The hash of the identity pair.

        Raises:
            RuntimeError: If the identity has been cleaned.
        """
        self.check_cleaned()
        return hash((self._kind, self._identity_id))

    def __repr__(self) -> str:
        """
        Return an unambiguous developer-facing rendering.

        Returns:
            str: A repr carrying the identity pair.
        """
        return "Identity(kind={0!r}, identity_id={1!r})".format(
            self._kind, self._identity_id
        )
