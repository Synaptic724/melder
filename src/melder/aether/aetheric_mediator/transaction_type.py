"""
The closed transaction vocabulary for the mediator plane.

Dependency-free beyond the standard library by design: the plane is built before
any `AethericFrame` exists, so nothing here may import `melder.aether`.

Mirrors `ChangeTransactionType` in the DevOps plane, including its discipline:
adding a structural operation means adding a member HERE plus a strategy, never
threading a new ad-hoc string through the plane.
"""

from enum import StrEnum


class TransactionType(StrEnum):
    """
    The closed set of top-level operations the mediator plane admits.

    Purpose:
        Name every structural operation that can claim scopes at world level,
        so admission, strategy dispatch, activity indexes, and logs all key on
        one stable vocabulary rather than free strings.

    Contract:
        - CLOSED BY DESIGN. Adding an operation means adding a member here AND
          registering its strategy. If a caller finds itself wanting to pass a
          string that is not a member, that is the signal a strategy is
          missing - not an invitation to widen the type.
        - Values are STABLE. They travel into request payloads, admission
          evidence, activity indexes, and logs; renaming one breaks stored
          evidence and anything grepping for it.
        - `StrEnum` so members pass through string-oriented APIs (logging,
          JSON, dict keys) without special casing, matching DevOps.
        - Read paths are NOT modelled here. Reads never enter this plane, the
          same invariant the DevOps plane holds for meld.

    PROVISIONAL MEMBERSHIP:
        This first set is derived from the operations that actually exist in
        the loader and the two gated subsystems, but it has NOT yet been
        confirmed by the three subsystem surveys. Expect members to be added
        or split as those land. Because the enum is closed and every member
        pairs with a strategy, growing it is a deliberate, reviewable act
        rather than a silent one.

    Member provenance:
        - FRAME_CREATE: `Aether._ensure_frame(...)`. THE FOUNDING CASE. The
          epic exists because this could not be admitted by anything that
          existed: the only admission authority was the frame-local
          `TransactionMediator`, which is owned BY the frame being created, so
          it could never arbitrate its own creation. This member is the first
          transaction in the vocabulary that could not have been written before
          the plane existed.
        - CHECKPOINT_LOAD: `CrystalLoaderSystem.load_checkpoint(...)`, which
          today takes whole-world exclusivity through the `LoadGate`.
        - FORMATION_LOAD: `restore_formation_record(...)`. Formations are
          SINGLE-FRAME by law ("multi-frame windows refuse"), which makes this
          the primary case for frame-scoped parallelism.
        - INDEX_GRAFT: the `GraftRunner` lane. Explicitly user-verb activity
          that takes NO load authority today.
        - SUBSYSTEM_ENABLE / SUBSYSTEM_DISABLE: the activation transitions the
          owner named as the wiring gate - a subsystem participates only when
          enabled and active, and emits its basic conditions at that edge.
        - SUBSYSTEM_CONFIGURE: declaring how a subsystem WOULD run, without
          switching it on. Split from SUBSYSTEM_ENABLE rather than folded into
          it because the two answer different questions and a subsystem can sit
          in the first state indefinitely: "its settings are recorded" is not
          "it is running", and a plane that could not tell them apart would
          report a configured-but-never-started subsystem as either live or
          entirely unknown. Both readings send the reader to the wrong place.
        - AGENT_REPAIR: the leave-broken-for-repair outcome. An agent mending a
          half-built world is doing structural work and must be able to claim
          it, or "leave it for an agent" means "leave it and stop the world".

    Threading:
        Stateless enum; safe to share across threads.

    Registration:
        MELDER KERNEL - guarded. Vocabulary in payloads and logs; never bound.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Closed vocabulary of top-level plane transactions.
        Every member pairs with a registered strategy.
    """

    FRAME_CREATE = "frame_create"
    CHECKPOINT_LOAD = "checkpoint_load"
    FORMATION_LOAD = "formation_load"
    INDEX_GRAFT = "index_graft"
    SUBSYSTEM_CONFIGURE = "subsystem_configure"
    SUBSYSTEM_ENABLE = "subsystem_enable"
    SUBSYSTEM_DISABLE = "subsystem_disable"
    AGENT_REPAIR = "agent_repair"
