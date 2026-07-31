"""
Claimant identity for the AethericMediator plane.

Dependency-free beyond the standard library by design: the plane is constructed
before any `AethericFrame` exists, so nothing here may import `melder.aether`.

Identity is the pivot the whole plane turns on. Sessions are keyed per identity,
which is what allows a holder to re-enter its own span (a join) instead of
deadlocking against itself, and what lets blocking evidence name a real culprit
rather than a bare thread id.
"""

from typing import Optional


class AethericIdentity:
    """
    The immutable identity of one claimant on the AethericMediator plane.

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
        - Not `Cleanable`: this owns no resource and has no teardown. It is
          a value, and giving it a lifecycle would imply an ownership it
          does not have.

    Owned State:
        Three immutable strings plus one optional integer. No collections,
        no references to runtime objects.

    Threading:
        Safe to share freely. Immutability is the whole thread-safety
        story; no lock is needed or provided.

    Registration:
        MELDER KERNEL - guarded. Constructed by plane callers; never bound
        as a spell.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Immutable identity of one claimant on the aetheric
        plane. Sessions key on it and blocking evidence names it.
    """

    __slots__ = ["_kind", "_identity_id", "_label", "_thread_ident"]

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
                "AethericIdentity requires a non-empty 'kind'; an unnamed "
                "claimant cannot be reported as a blocking holder."
            )
        if not identity_id or not identity_id.strip():
            raise ValueError(
                "AethericIdentity requires a non-empty 'identity_id'; a blank "
                "id would make unrelated claimants compare equal."
            )
        self._kind: str = kind
        self._identity_id: str = identity_id
        self._label: Optional[str] = label
        self._thread_ident: Optional[int] = thread_ident

    @property
    def kind(self) -> str:
        """
        Return the subsystem family this claimant belongs to.

        Returns:
            str: The stable lowercase family name.
        """
        return self._kind

    @property
    def identity_id(self) -> str:
        """
        Return the stable id of this claimant within its family.

        Returns:
            str: The identity id.
        """
        return self._identity_id

    @property
    def label(self) -> Optional[str]:
        """
        Return the optional diagnostic label, if one was supplied.

        Returns:
            Optional[str]: The label, or None when none was given.
        """
        return self._label

    @property
    def thread_ident(self) -> Optional[int]:
        """
        Return the originating thread id carried as diagnostic evidence.

        Contract:
            This is NOT part of identity and never participates in equality.

        Returns:
            Optional[int]: The thread id, or None when none was supplied.
        """
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
        """
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
                True when `other` is an `AethericIdentity` with the same
                kind and id. `NotImplemented` is returned for foreign types
                so Python can fall back to the reflected comparison.
        """
        if not isinstance(other, AethericIdentity):
            return NotImplemented
        return (
            self._kind == other._kind
            and self._identity_id == other._identity_id
        )

    def __hash__(self) -> int:
        """
        Hash on `(kind, identity_id)`, matching equality exactly.

        Returns:
            int: The hash of the identity pair.
        """
        return hash((self._kind, self._identity_id))

    def __repr__(self) -> str:
        """
        Return an unambiguous developer-facing rendering.

        Returns:
            str: A repr carrying the identity pair.
        """
        return "AethericIdentity(kind={0!r}, identity_id={1!r})".format(
            self._kind, self._identity_id
        )
