"""
Claim vocabulary for the AethericMediator plane.

This module is deliberately dependency-free beyond the standard library: the
plane must be constructible before any `AethericFrame` exists, so nothing here
may reach into `melder.aether`.

The vocabulary mirrors the working DevOps change-control plane
(`ChangeControlEmbargoManager`) rather than inventing a new one, because that
matrix is already proven in production under free-threaded 3.14t.
"""

from enum import Enum
from typing import ClassVar, FrozenSet, Tuple


class ClaimMode(Enum):
    """
    The access posture one holder requests over one scope key.

    Purpose:
        Express the difference between "nobody else may touch this",
        "several readers may share this", and "I am doing additive
        piece-work here, so a whole-unit writer must be excluded but my
        peers need not be".

    Contract:
        - Values are the short forms used throughout the DevOps plane and
          its documentation, so evidence written against one plane reads
          correctly against the other.
        - Compatibility is NOT defined here. It lives in
          `ClaimCompatibility` so the matrix can be a real class attribute;
          a mapping declared inside an `Enum` body would be swallowed as a
          member rather than kept as data.

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
        - SHARED vs INTENT is CONSERVATIVELY DENIED. See the note below;
          this is a deliberate, flagged default rather than a derived rule.
        - The matrix is symmetric by construction: every permitted pair is
          stored in both orders so callers never have to normalise.

    SHARED vs INTENT - why denied:
        The DevOps plane documents only three rules: `s`/`s` coexist,
        `ix`/`ix` coexist, and `x` excludes everything. It does not state
        what happens between `s` and `ix`, and `ix` there means "additive
        piece-work on this unit" (a spellbook accepting binds and links)
        while `s` means "reading this unit". Additive work can change what
        a reader observes, so permitting the pair would be a guess that
        fails OPEN - the dangerous direction. Denying it fails CLOSED: the
        worst case is unnecessary serialisation, which is visible and
        fixable, rather than an undetected read of shifting state.
        This must be revisited once the three subsystem surveys land; if a
        real case needs the pair, widen it deliberately and record why.

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
