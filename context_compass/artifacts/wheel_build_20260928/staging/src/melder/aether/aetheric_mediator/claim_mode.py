"""
Claim vocabulary for the mediator plane.

This module is deliberately dependency-free beyond the standard library: the
plane must be constructible before any `AethericFrame` exists, so nothing here
may reach into `melder.aether`.

The vocabulary mirrors the working DevOps change-control plane
(`ChangeControlEmbargoManager`) rather than inventing a new one, because that
matrix is already proven in production under free-threaded 3.14t.
"""

from enum import StrEnum
from typing import ClassVar, FrozenSet, Tuple


class ClaimMode(StrEnum):
    """
    The access posture one holder requests over one scope key.

    Purpose:
        Express the difference between "nobody else may touch this",
        "several readers may share this", and "I hold a PARENT scope while
        doing piece-work beneath it, so a whole-unit writer must be excluded
        but my peers need not be".

    Contract:
        - `EXCLUSIVE` ("x"): no other claim of ANY mode may coexist.
        - `SHARED` ("s"): coexists with other `SHARED` claims ONLY.
        - `INTENT` ("ix"): coexists with other `INTENT` claims ONLY. It is
          the HIERARCHICAL PARENT-SCOPE MARKER - hold `ix` on the parent
          while holding `x` on the child, and disjoint children proceed in
          parallel while a whole-parent `x` still excludes every one of them.
        - These are the DevOps plane's semantics VERBATIM, verified against
          `embargo_manager.ClaimMode`, not a parallel invention. Evidence
          written against one plane therefore reads correctly against the
          other.
        - `StrEnum`, matching DevOps, because these values TRAVEL: they land
          in request payloads, admission evidence, and logs, and must survive
          string-oriented APIs without special casing.
        - Compatibility is NOT defined here. It lives in
          `ClaimCompatibility` so the matrix can be a real class attribute;
          a mapping declared inside an enum body would be swallowed as a
          member rather than kept as data.

    The hierarchical pattern this plane is built for:
        A whole-world load claims `world` EXCLUSIVE and excludes everything.
        A frame-scoped load claims `world` INTENT plus `frame:A` EXCLUSIVE.
        A second frame-scoped load claims `world` INTENT plus `frame:B`
        EXCLUSIVE. The two coexist on the parent and never contend on the
        children, so disjoint loads run in parallel - while the whole-world
        load still shuts both out. This is exactly the behaviour the
        crystallizer's global `LoadGate` provides today, re-expressed as
        claims rather than a single global mutex.

    Registration:
        MELDER KERNEL - guarded. Vocabulary only; never bound as a spell.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Access posture for one scope claim - exclusive,
        shared, or intent. Read it to understand admission; do not drive it
        directly.
    """

    EXCLUSIVE = "x"
    SHARED = "s"
    INTENT = "ix"


class ClaimCompatibility:
    """
    The static compatibility matrix between a held claim and a requested one.

    Purpose:
        Answer exactly one question: may `requested` be granted on a scope
        that is already held under `held`?

    Contract:
        - EXCLUSIVE excludes everything, in both directions.
        - SHARED coexists with SHARED.
        - INTENT coexists with INTENT.
        - SHARED vs INTENT is DENIED, matching DevOps exactly. Verified
          against `embargo_manager.ClaimMode`, whose contract states SHARED
          "permits coexistence with other SHARED claims only" and INTENT
          "permits coexistence with other INTENT claims only".
        - The matrix is therefore symmetric AND diagonal: a mode coexists
          only with itself, and EXCLUSIVE not even with that.

    Provenance:
        An earlier revision of this class denied SHARED/INTENT as a
        CONSERVATIVE GUESS, on the reasoning that permitting an undocumented
        pair fails open while denying it fails closed. That guess was
        subsequently checked against `embargo_manager.ClaimMode` and proved
        to match the shipped semantics exactly. The rule is now EVIDENCED
        rather than assumed, and this note is kept so a future reader does
        not "restore" a permissiveness that was never there.

    Lifecycle / Cleanup:
        NEVER INSTANTIATED, so there is nothing to clean and no `Cleanable`
        contract. This is a static policy table: one `ClassVar` frozenset of
        permitted pairs plus two static predicates. No code constructs one.

    Threading:
        Pure and stateless. Safe to call from any thread without
        synchronisation; holds no instance state and mutates nothing.

    Registration:
        MELDER KERNEL - guarded. Policy table; never bound as a spell.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Static compatibility matrix for scope claims.
        Answers whether a requested mode may join a held mode.
    """

    _PERMITTED_PAIRS: ClassVar[FrozenSet[Tuple[ClaimMode, ClaimMode]]] = frozenset(
        {
            (ClaimMode.SHARED, ClaimMode.SHARED),
            (ClaimMode.INTENT, ClaimMode.INTENT),
        }
    )

    @staticmethod
    def permits(held: ClaimMode, requested: ClaimMode) -> bool:
        """
        Report whether `requested` may be granted alongside `held`.

        Args:
            held:
                The mode already granted on the scope key.
            requested:
                The mode being asked for on that same scope key.

        Returns:
            bool:
                True when both may coexist on one scope, False otherwise.

        Raises:
            TypeError:
                If either argument is not a `ClaimMode`.
        """
        if not isinstance(held, ClaimMode) or not isinstance(requested, ClaimMode):
            raise TypeError(
                "ClaimCompatibility.permits requires ClaimMode arguments; "
                "got held={0!r}, requested={1!r}.".format(held, requested)
            )
        return (held, requested) in ClaimCompatibility._PERMITTED_PAIRS

    @staticmethod
    def is_exclusive(mode: ClaimMode) -> bool:
        """
        Report whether `mode` excludes every other claim on its scope.

        Args:
            mode:
                The mode to classify.

        Returns:
            bool:
                True only for `ClaimMode.EXCLUSIVE`.

        Raises:
            TypeError:
                If `mode` is not a `ClaimMode`.
        """
        if not isinstance(mode, ClaimMode):
            raise TypeError(
                "ClaimCompatibility.is_exclusive requires a ClaimMode; "
                "got {0!r}.".format(mode)
            )
        return mode is ClaimMode.EXCLUSIVE
