"""
The participation vocabulary for the mediator plane.

Dependency-free beyond the standard library.

Owner constraint 6 gates participation on activation: a subsystem takes part in
the plane ONLY when enabled and active, and emits its basic conditions at that
edge. Stated that way the rule is describable but not CHECKABLE, because a store
that records presence and absence can only answer "known" versus "unknown" - and
"unknown" collapses three genuinely different situations into one. A subsystem
that has never announced itself, one that announced but has not been switched
on, and one that ran and was switched off are three distinct facts, and only the
first is actually an absence.

This module is the vocabulary that makes the rule checkable. Four states, each
reachable by exactly ONE edge, and exactly ONE of them emits.
"""

from enum import StrEnum
from typing import Any, Dict, Mapping, Tuple


class ParticipationState(StrEnum):
    """
    The closed set of participation states a subsystem can be in.

    Purpose:
        Let the plane answer "should I care about this subsystem right now"
        with a value rather than an inference, and answer "why not" when the
        answer is no.

    Contract:
        - CLOSED, like every other vocabulary in this package. Adding a member
          means adding the EDGE that writes it. A state nothing can ever write
          is a state nothing can ever be in, which is worse than not having it:
          readers branch on it forever and the branch is dead.
        - EXACTLY ONE MEMBER EMITS. `ENABLED` is the only state for which
          `emits` is True. That is owner constraint 6 expressed as code instead
          of prose, and it is why this is an enum rather than a bool - the bool
          was already there and it could not say WHY a subsystem was silent.
        - `StrEnum`, matching `ClaimMode`, `TransactionType`, `ScopePrefix`,
          `OutcomePolicy` and `SessionStatus`, because these values TRAVEL:
          they land in registry rows, `describe()` output, and logs, and must
          survive string-oriented APIs without special casing.
        - THERE IS NO TRANSITIONAL MEMBER, and that is deliberate. There is no
          `ENABLING`, because the edges that move this value run inside
          `apply_commit_delta`, which runs at commit WHILE the transaction
          still holds `subsystem:<name>` EXCLUSIVE. The state flips atomically
          under that claim, so no reader can observe a half-transition. The
          claim is the transitional marker; duplicating it as a state would
          create a value that could be left behind by a crash.

    Member provenance - the edge that writes each one:
        - REGISTERED: `Mediator.register_participant(...)`. The subsystem has
          announced that it exists and may submit transactions. It has declared
          NO conditions and is not running. This is a roster arrival, not an
          activation, and it deliberately does not emit.
        - CONFIGURED: a `SUBSYSTEM_CONFIGURE` transaction committing. The
          subsystem's basic conditions are recorded and trustworthy, but it is
          still not running. This is the state that separates "we know how it
          would run" from "it is running".
        - ENABLED: a `SUBSYSTEM_ENABLE` transaction committing. Enabled AND
          active. THE ONLY EMITTING STATE.
        - DISABLED: a `SUBSYSTEM_DISABLE` transaction committing. It ran, and
          it stopped. Distinct from absence: absence means the plane has never
          heard of the subsystem, which is a configuration question, while
          DISABLED means it heard and the answer was no. Diagnosing a subsystem
          that is silently doing nothing needs those two apart.

    Threading:
        Stateless enum; safe to share across threads.

    Lifecycle / Cleanup:
        Not `Cleanable`. Enum members are process-lived immutable values with
        nothing to release; stating that is not the same as it being obvious.

    Registration:
        MELDER KERNEL - guarded. Vocabulary in registry rows and logs; never
        bound.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Closed vocabulary of subsystem participation states.
        Only ENABLED emits; check `emits` rather than comparing members by hand.
    """

    REGISTERED = "registered"
    CONFIGURED = "configured"
    ENABLED = "enabled"
    DISABLED = "disabled"

    @property
    def emits(self) -> bool:
        """
        Report whether a subsystem in this state should be emitted for.

        Purpose:
            Be the ONE place the emission rule is written, so a caller never
            has to remember which members count as live.

        Contract:
            True for `ENABLED` and nothing else. Callers must ask this rather
            than comparing members themselves: a hand-written
            `state != DISABLED` reads as correct and silently emits for
            REGISTERED and CONFIGURED subsystems, which is precisely the bug
            this vocabulary exists to prevent.

        Returns:
            bool: True only when this state means enabled and active.
        """
        return self is ParticipationState.ENABLED


class ParticipationConditions:
    """
    The closed vocabulary of basic conditions a subsystem may announce.

    Purpose:
        Bound what a subsystem is allowed to tell the plane about itself, in
        one place, so the bound cannot drift between the edges that write it.

    Contract:
        - THE KEY SET IS CLOSED AND THE PLANE OWNS IT, not the subsystems.
          A subsystem announces conditions by putting them in transaction
          metadata, and metadata is caller-controlled. Without a declared key
          set, a subsystem could widen its own row with arbitrary keys and the
          plane would faithfully store whatever it was handed - which turns a
          bounded fact store into an unbounded scratch space that every reader
          then has to defend against.
        - SELECTION IS SILENT, NOT AN ERROR. Undeclared keys are DROPPED
          rather than refused. Metadata legitimately carries routing values
          this vocabulary has no opinion about - `subsystem_name` itself, for
          one - and refusing a transaction because its metadata contained a key
          this class does not know would make every unrelated metadata addition
          a breaking change.
        - VALUE-ONLY is enforced downstream by the registry, not here.
          Selection decides WHICH keys travel; the store decides what a value
          is allowed to be. Splitting those keeps this class pure.

    Why these five keys:
        They are the conditions the three subsystem surveys found each
        subsystem actually varies at its activation edge - whether it runs work
        in parallel, how many workers, how long it will wait to drain, how many
        units it will hold at once, and which policy revision it is running.
        A reader deciding whether to wait for a subsystem needs those; it does
        not need the subsystem's internal handles, and could not be trusted
        with them.

    Lifecycle / Cleanup:
        NEVER INSTANTIATED, so there is nothing to clean and no `Cleanable`
        contract. This is a namespace of a constant and one pure selector,
        matching `ScopeKey` in the same package.

    Threading:
        Pure and stateless; safe to call from any thread.

    Registration:
        MELDER KERNEL - guarded. Vocabulary; never bound.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Declared key set for subsystem basic conditions plus
        the selector that filters metadata down to it. A subsystem cannot widen
        its own registry row.
    """

    DECLARED_KEYS: Tuple[str, ...] = (
        "parallel_enabled",
        "worker_count",
        "drain_timeout_seconds",
        "max_active_units",
        "policy_version",
    )

    @staticmethod
    def select(metadata: Mapping[str, Any]) -> Dict[str, Any]:
        """
        Return only the declared conditions present in `metadata`.

        Contract:
            PURE. Reads the mapping, returns a fresh dict, mutates nothing.
            An absent key is simply absent from the result - there is no
            defaulting, because a default would be the plane inventing a
            condition the subsystem never announced.

        Args:
            metadata: Caller-supplied transaction metadata.

        Returns:
            Dict[str, Any]: The declared conditions the caller announced, in
                declaration order.
        """
        return {
            key: metadata[key]
            for key in ParticipationConditions.DECLARED_KEYS
            if key in metadata
        }
