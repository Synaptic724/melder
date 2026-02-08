from typing import Any, Optional
# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import ISpell
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class MeldContext(Cleanable):
    """
    Per-meld-call orchestration context for the Meld runtime.

    This object is created and reused across `meld(...)` calls via the
    Meld-local context pool and
    captures everything the runtime needs to execute that call:

        * The **root spell** being activated.
        * The **owner creations container** for shared existences.
        * The **caller creations container** for per-conduit existences.
        * Whether the caller creations lock is already held for this call.
        * Optional **per-call overrides** (from `spell_override`).

    Design goals
    ------------

    * **Pooled reuse** - instances are reset and reused across calls.
    * **No global state** – everything needed for this execution is
      passed in at construction time.
    * **Deterministic cleanup** – references are dropped on `cleanup()`
      so long-lived conduits don't leak references through contexts.

    Typical lifecycle
    -----------------

    1. `Meld.meld(...)` decides a new root instance is required.
    2. `Meld` acquires or creates a `MeldContext` with:
           - `root_spell`
           - caller creations (current Conduit scope)
           - owner creations (spell owner Conduit scope)
           - Pre-normalized overrides map
    3. Meld's merged runtime execution path is called with the context.
    4. After execution returns, `Meld` calls `context.reset()`
       and returns the context to the local pool.
    5. When `Meld.cleanup()` runs, pooled contexts receive final
       `context.cleanup()` teardown.

    This class does **not** perform any DI or DAG work itself – it is
    purely a container for per-call configuration and wiring.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_root_spell",
        "_owner_creations",
        "_caller_creations",
        "_caller_creations_lock_held",
        "_overrides",
    ]

    def __init__(
            self,
            *,
            root_spell: ISpell,
            overrides: Optional[dict[str, Any]] = None,
            caller_creations: Optional[Any] = None,
            caller_creations_lock_held: bool = False,
    ) -> None:
        """
        Initialize a per-call context for Meld runtime execution.

        Purpose:
            Capture all per-call data needed by the runtime,
            including the root spell, creations scopes, and overrides.

        Contract:
            - root_spell must not be None.
            - owner creations are sourced from root_spell._owner_creations.
            - caller creations are supplied by Meld for the active conduit scope.
            - caller_creations_lock_held indicates whether the caller creations
              lock is already held by the calling thread when the runtime runs.
            - overrides are accepted by reference and assumed to already be
              normalized by Meld entry helpers.
            - overrides are None when no overrides are supplied.
            - cleanup() must deterministically drop all references.

        Args:
            root_spell:
                The root ISpell being activated for this meld call.
            overrides:
                Optional pre-normalized per-call override mapping (keyword
                overrides and optional "__args__" payload). When None, no
                override container is allocated for this context.
            caller_creations:
                Creations container representing the current Conduit scope that
                initiated the meld call.
            caller_creations_lock_held:
                True if the caller creations lock is already held by the
                invoking thread for the duration of this context. This allows
                the runtime to avoid lock inversion when resolving shared
                existences under a caller-scoped lock.
        """
        super().__init__()
        self._root_spell: ISpell = root_spell
        self._owner_creations: Any = self._root_spell._owner_creations
        self._caller_creations: Any = caller_creations
        self._caller_creations_lock_held: bool = bool(caller_creations_lock_held)
        # Pre-normalized, per-call override map (None when no overrides are supplied).
        self._overrides: Optional[dict[str, Any]] = overrides

    # ------------------------------------------------------------------ #
    # Cleanup
    # ------------------------------------------------------------------ #

    def cleanup(self) -> None:
        """
        Deterministically clear all references held by this context.

        This is called during final owner teardown (for example from
        `Meld.cleanup()`) when this context should no longer be reused.
        It:

        * Drops references to the spell, creations, overrides, and metadata.
        * Marks this object as cleaned via `Cleanable`.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._root_spell = None
        self._owner_creations = None
        self._caller_creations = None
        self._caller_creations_lock_held = False
        if self._overrides is not None:
            self._overrides.clear()
        self._overrides = None

    def reset(
            self,
            *,
            root_spell: Optional[ISpell] = None,
            overrides: Optional[dict[str, Any]] = None,
            caller_creations: Optional[Any] = None,
            caller_creations_lock_held: bool = False,
    ) -> None:
        """
        Reset the context either for reuse preparation or pool-idle state.

        Contract:
            - When `root_spell` is provided, prepares an active per-call context.
            - When `root_spell` is None, clears per-call references for pooling.
            - Marks the context as active (not cleaned) for pooled reuse.
        """
        if root_spell is None:
            self._root_spell = None
            self._owner_creations = None
            self._caller_creations = None
            self._caller_creations_lock_held = False
            if self._overrides is not None:
                self._overrides.clear()
            self._overrides = None
            return

        self._root_spell = root_spell
        self._owner_creations = root_spell._owner_creations
        self._caller_creations = caller_creations
        self._caller_creations_lock_held = bool(caller_creations_lock_held)

        if self._overrides is not None and self._overrides is not overrides:
            self._overrides.clear()
        self._overrides = overrides



    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def root_spell(self) -> ISpell:
        """The root spell being activated for this meld call."""
        return self._root_spell

    @property
    def owner_creations(self) -> Any:
        """
        The creations container owned by the root spell's owning Conduit.

        This is the authoritative scope for shared lifetimes such as
        `Existence.unique`, `Existence.unique_per_conduit_cluster`, and
        `Existence.unique_per_conduit_lineage`.
        """
        return self._owner_creations

    @property
    def caller_creations(self) -> Any:
        """
        The creations container for the Conduit that initiated this meld call.

        This is the authoritative scope for per-conduit lifetimes such as
        `Existence.unique_per_conduit`, `Existence.many`, and
        `Existence.unique_per_spell_space`.
        """
        return self._caller_creations

    @property
    def caller_creations_lock_held(self) -> bool:
        """
        Whether the caller creations lock is already held by the invoking thread.

        This is used by the runtime to avoid lock inversion when a caller-scoped
        lock wraps runtime execution and shared existences resolve against the
        same creations container.
        """
        return self._caller_creations_lock_held

    @property
    def overrides(self) -> Optional[dict[str, Any]]:
        """
        The pre-normalized override map for this meld call.

        Semantics (matching `_normalize_spell_override`):

            * `{"param": value}` – keyword argument overrides.
            * `{"__args__": [a0, a1, ...]}` – positional overrides.
            * A combination of both is allowed.

        MeldContext does not copy this payload; it stores the mapping reference
        supplied by Meld.

        Returns:
            Optional[dict[str, Any]]:
                Override payload mapping, or None when no overrides are supplied.
        """
        return self._overrides
