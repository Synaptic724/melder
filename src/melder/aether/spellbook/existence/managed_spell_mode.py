from enum import Enum, auto


class ManagedSpellMode(Enum):
    """
    How a managed spell's pool answers a lease when no idle object is waiting.

    `ManagedSpellMode` is chosen at bind, beside `Existence.managed_spell_quantity`, through the
    `managed_spell_mode` option (the member or its name). It decides what a miss does - build, refuse or wait -
    and what `managed_spell_limit` means; a hit (an idle object is waiting) is the same in every mode: the
    object is taken and handed to the holder.

    Contract:
    - The enum performs nothing by itself; Bind validates the options it implies and records them on the Spell,
      and the spell's pool in the owning root's store interprets them.
    - `elastic`: a miss always builds. `managed_spell_limit` is the most idle objects kept (default 256); idle
      objects beyond what demand needs are trimmed the way Melder's own SpellSpace and lesser-conduit pools trim
      theirs. Never refuses.
    - `limited_quantity`: `managed_spell_limit` (required) is the most objects alive at once - idle plus out.
      A miss builds below the limit and refuses at it, before building anything.
    - `queue`: like `limited_quantity`, but a miss at the limit waits for a release, up to
      `managed_spell_timeout_seconds` (required), and refuses at that deadline. A release serves a waiting
      lease with the released object.
    - `managed_spell_timeout_seconds` applies to `queue` only; Bind refuses it on the other two modes.

    Threading:
        Immutable enum members; safe to read from any thread.

    Registration:
        MELDER KERNEL - guarded, readable by value. Users pass it, or its name, into `Spellbook.bind(...)`,
        `Conduit.bind(...)`, `SpellBinder.as_managed_spell_quantity(...)` or `scan_bind(...)`.

    Subsystem Context:
        The per-binding policy half of `Existence.managed_spell_quantity`. `Existence` says objects are leased
        from a root-owned pool and released back; this enum says what the pool does when it has nothing idle.

    System Context:
        The mode is a setting of the spell, not identity data: it is not part of the spell id (nor are the
        limit, the timeout and the reset names; owner ruling 2026-10-17, 0.2.8254), so one class bound managed
        at one address is one spell whatever its mode. It is recorded by the crystallizer and replayed by
        restore and graft. To change it, `cleanup_spell` the spell and bind it again: the spell keeps its spell
        id and its pool takes the new settings.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. Pool policy of a managed spell, chosen at bind: elastic (always builds, keeps idle
        objects up to the limit, default 256), limited_quantity (at most N alive, refuses at N), queue (at most N
        alive, waits up to a timeout for a release, then refuses). Pass it or its name as managed_spell_mode.
    """
    elastic = auto()
    """
    A miss **always builds**; idle objects are kept up to `managed_spell_limit` (default 256).

    - Never refuses a lease.
    - Keeps what a burst needed and trims back when demand falls, like Melder's own pools.
    - Takes no timeout.
    """

    limited_quantity = auto()
    """
    At most `managed_spell_limit` objects **alive at once** (idle plus out).

    - A miss below the limit builds; at the limit the lease is refused before anything is built.
    - The limit is required; the mode takes no timeout.
    """

    queue = auto()
    """
    At most `managed_spell_limit` objects alive at once; at the limit a lease **waits** for a release.

    - The wait ends when a release hands the waiter the released object, or at
      `managed_spell_timeout_seconds`, when the lease is refused.
    - The limit and the timeout are both required.
    """

    def __str__(self) -> str:
        """
        Return the bare member name.

        Contract:
            - Returns the BARE MEMBER NAME (`"queue"`), not the enum repr (`"ManagedSpellMode.queue"`), as
              `Existence` does, so a mode written into a record or a log reads back through the enum by name.

        Threading:
            Pure computation over immutable fields; safe from any thread.

        Returns:
            str: The member name.
        """
        return self.name
