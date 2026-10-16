from typing import Optional

from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


class ManagedSpellExhaustedError(MeldExecutionError):
    """

    Purpose:
        Signal that a meld could not lease an object of an `Existence.managed_spell_quantity` spell because its pool
        had no place: a `limited_quantity` pool with every object out, or a `queue` pool that stayed full until its
        timeout. Names the spell, the mode, the numbers and the two ways out, instead of a bare refusal.

    Raised When:
        A managed site misses (no idle object in its pool) and `ManagedSpellQuantity.reserve()` cannot reserve a
        place: `limited_quantity` at `count >= limit` with nothing idle, or `queue` after waiting its
        `managed_spell_timeout_seconds` without a release, a destroy or a failed build freeing a place. Nothing has
        been built when it is raised, and the pool's count is unchanged. `elastic` pools never raise it.

    What To Do About It:
        Give an object back - `ReleaseManagedSpell().release(obj)`, or leave the `with` block of a lease - before
        melding another, or bind the spell with a higher `managed_spell_limit` (and, for `queue`, a longer
        `managed_spell_timeout_seconds`). `ReleaseManagedSpell().describe(cls)` shows each pool's count, idle and
        out objects.

    Contract:
        - A `MeldExecutionError`: code that catches `MeldExecutionError` keeps catching it. `spell_id` and
          `spell_name` name the managed spell; `node_id`, `param_name` and `inner` are None (nothing was called).
        - `mode` is the pool's mode name (`"limited_quantity"` or `"queue"`), `limit` its limit and
          `timeout_seconds` the queue wait (None for `limited_quantity`).
        - Built only through `limited(...)` and `queue(...)`, which own the message texts.

    Owned State:
        - Inherited `spell_id`, `spell_name`, `node_id`, `param_name`, `inner`.
        - `mode`, `limit`, `timeout_seconds`: the refusing pool's policy.

    Registration:
        A public exception type; import, raise and catch freely. Like every Melder class it is refused as a spell
        registration.

    Subsystem Context:
        One of the `utilities/custom_exceptions/` types; the managed-pool form of `MeldExecutionError`. It imports
        nothing from the runtime, so the pool (`ManagedSpellQuantity`, in the conduit creations package) depends on
        it and not the other way round.

    System Context:
        Fires in the resolution layer at meld, from the cold miss of a managed site, before any construction.
        Successful leases never evaluate it.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. Raised at meld when a managed spell's pool has no place: limited_quantity with every
        object out, or queue after its timeout. Release an object (ReleaseManagedSpell().release(obj)) or bind a
        higher managed_spell_limit / managed_spell_timeout_seconds.
    """

    __slots__ = (
        "mode",
        "limit",
        "timeout_seconds",
    )

    def __init__(
            self,
            *,
            spell_id: str,
            spell_name: str,
            message: str,
            mode: str,
            limit: int,
            timeout_seconds: Optional[float] = None,
    ) -> None:
        """
        Construct an exhausted-pool failure.

        Args:
            spell_id:
                Version id of the managed spell.
            spell_name:
                Human-readable name of that spell.
            message:
                Remediation-bearing message; `limited(...)` and `queue(...)` write it.
            mode:
                Name of the refusing pool's mode, `"limited_quantity"` or `"queue"`.
            limit:
                The pool's limit: the most objects alive at once.
            timeout_seconds:
                The queue wait that ran out; None for `limited_quantity`.

        Contract:
            - Preserves every `MeldExecutionError` field; `node_id`, `param_name` and `inner` stay None.

        Returns:
            None.
        """
        super().__init__(
            spell_id=spell_id,
            spell_name=spell_name,
            message=message,
        )
        self.mode: str = mode
        self.limit: int = limit
        self.timeout_seconds: Optional[float] = timeout_seconds

    @classmethod
    def limited(cls, *, spell_id: str, spell_name: str, limit: int) -> ManagedSpellExhaustedError:
        """
        Build the refusal of a `limited_quantity` pool that has every object out.

        Contract:
            - The message names the spell, the mode and the limit, and the two remedies: release an object first,
              or bind a higher `managed_spell_limit`.
            - Pure: builds the error, raises nothing.

        Args:
            spell_id: Version id of the managed spell.
            spell_name: Its display name.
            limit: The pool's limit.

        Returns:
            ManagedSpellExhaustedError: The error, mode `"limited_quantity"`, no timeout.
        """
        return cls(
            spell_id=spell_id,
            spell_name=spell_name,
            message=(
                f"Managed spell '{spell_name}' (limited_quantity, limit {limit}) has all {limit} objects out. "
                f"Release one with ReleaseManagedSpell().release(obj) before melding another, or bind it with a "
                f"higher managed_spell_limit."
            ),
            mode="limited_quantity",
            limit=limit,
        )

    @classmethod
    def queue(
            cls,
            *,
            spell_id: str,
            spell_name: str,
            limit: int,
            timeout_seconds: float,
    ) -> ManagedSpellExhaustedError:
        """
        Build the refusal of a `queue` pool whose wait ran out.

        Contract:
            - The message names the spell, the mode, the limit and the timeout (printed with `:g`, so 2.0 reads
              "2" and 0.25 "0.25"), and the remedies: release an object, or bind a higher `managed_spell_limit`
              or `managed_spell_timeout_seconds`.
            - Pure: builds the error, raises nothing.

        Args:
            spell_id: Version id of the managed spell.
            spell_name: Its display name.
            limit: The pool's limit.
            timeout_seconds: The wait that ran out, in seconds.

        Returns:
            ManagedSpellExhaustedError: The error, mode `"queue"`, with its timeout.
        """
        return cls(
            spell_id=spell_id,
            spell_name=spell_name,
            message=(
                f"Managed spell '{spell_name}' (queue, limit {limit}) had no object free within "
                f"{timeout_seconds:g} s. Release one with ReleaseManagedSpell().release(obj), or bind it with a "
                f"higher managed_spell_limit or managed_spell_timeout_seconds."
            ),
            mode="queue",
            limit=limit,
            timeout_seconds=timeout_seconds,
        )
