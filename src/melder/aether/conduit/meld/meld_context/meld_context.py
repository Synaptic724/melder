from threading import RLock
from typing import Any, Mapping, MutableMapping, Optional
# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.init_helpers import InitHelpers
from melder.utilities.logger.safe_logger import SafeLogger
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent
from melder.utilities.interfaces.interfaces import ISpell
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class MeldContext(Cleanable):
    """
    Per-meld-call orchestration context for the Meld runtime.

    This object is created for **each individual `meld(...)` call** and
    captures everything the runtime/engine need to execute that call:

        * The **root spell** being activated.
        * The **owner creations container** for shared existences.
        * The **caller creations container** for per-conduit existences.
        * Whether the caller creations lock is already held for this call.
        * Normalized **per-call overrides** (from `spell_override`).
        * Optional **cancellation** signal.
        * Optional **logger** (wrapped as a `SafeLogger`).
        * Optional **conduit identity** and **aetheric frame** metadata.

    Design goals
    ------------

    * **Per-call only** – instances are never reused across meld calls.
    * **No global state** – everything needed for this execution is
      passed in at construction time.
    * **Deterministic cleanup** – references are dropped on `cleanup()`
      so long-lived conduits don't leak references through contexts.

    Typical lifecycle
    -----------------

    1. `Meld.meld(...)` decides a new root instance is required.
    2. `Meld` creates a `MeldContext` with:
           - `root_spell`
           - caller creations (current Conduit scope)
           - owner creations (spell owner Conduit scope)
           - Normalized overrides map
           - (optionally) cancel event, logger, conduit metadata
    3. `MeldRuntime.execute(context)` is called.
    4. After execution returns, `Meld` / `MeldRuntime` call
       `context.cleanup()`.

    This class does **not** perform any DI or DAG work itself – it is
    purely a container for per-call configuration and wiring.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_root_spell",
        "_creations",
        "_owner_creations",
        "_caller_creations",
        "_caller_creations_lock_held",
        "_overrides",
        "_cancel_event",
        "_logger",
        "_conduit_id",
        "_conduit_name",
        "_aetheric_frame",
    ]

    def __init__(
            self,
            *,
            root_spell: ISpell,
            overrides: Optional[Mapping[str, Any]] = None,
            cancel_event: Optional[CancellationEvent] = None,
            logger: Optional[Any] = None,
            caller_creations: Optional[Any] = None,
            caller_creations_lock_held: bool = False,
    ) -> None:
        """
        Initialize a per-call context for Meld runtime execution.

        Purpose:
            Capture all per-call data needed by the runtime/engine,
            including the root spell, creations scopes, and overrides.

        Contract:
            - root_spell must not be None.
            - owner creations are sourced from root_spell._owner_creations.
            - caller creations default to owner creations when not provided.
            - caller_creations_lock_held indicates whether the caller creations
              lock is already held by the calling thread when the runtime runs.
            - overrides are copied into a mutable mapping for this call.
            - cleanup() must deterministically drop all references.

        Args:
            root_spell:
                The root ISpell being activated for this meld call.
            overrides:
                Optional per-call override mapping (keyword overrides or
                "__args__" positional overrides).
            cancel_event:
                Optional CancellationEvent to support cooperative cancellation.
            logger:
                Optional logger object; normalized to SafeLogger when provided.
            caller_creations:
                Optional creations container representing the current Conduit
                scope that initiated the meld call.
            caller_creations_lock_held:
                True if the caller creations lock is already held by the
                invoking thread for the duration of this context. This allows
                the engine to avoid lock inversion when resolving shared
                existences under a caller-scoped lock.

        Raises:
            ValueError: If root_spell is None.
        """
        super().__init__()

        if root_spell is None:
            raise ValueError("root_spell cannot be None.")

        self._lock: RLock = RLock()
        self._root_spell: ISpell = root_spell
        self._owner_creations: Any = self._root_spell._owner_creations
        self._caller_creations: Any = (
            caller_creations
            if caller_creations is not None
            else self._owner_creations
        )
        self._creations: Any = self._owner_creations
        self._caller_creations_lock_held: bool = bool(caller_creations_lock_held)

        # Normalized, per-call override map (never mutated in place by
        # the runtime; callers may mutate the dict they get back).
        self._overrides: MutableMapping[str, Any] = (
            dict(overrides) if overrides is not None else {}
        )

        self._cancel_event: Optional[CancellationEvent] = cancel_event

        # Logger is optional; when provided we normalize to SafeLogger
        # so the engine/runtime can safely call .debug/.error without
        # worrying about the concrete logger type.
        self._logger: Optional[SafeLogger] = (
            InitHelpers.resolve_safe_logger(logger)
            if logger is not None
            else None
        )

        self._conduit_id: Optional[str] = self._root_spell._owner_conduit_id
        self._conduit_name: Optional[str] = self._root_spell._owner_conduit_name
        self._aetheric_frame: Optional[str] = self._root_spell.aetheric_frame

    # ------------------------------------------------------------------ #
    # Cleanup
    # ------------------------------------------------------------------ #

    def cleanup(self) -> None:
        """
        Deterministically clear all references held by this context.

        This is called by the runtime once a meld call has completed
        (successfully or with an error). It:

        * Drops references to the spell, creations, overrides, logger,
          and metadata.
        * Marks this object as cleaned via `Cleanable`.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._root_spell = None
            self._creations = None
            self._owner_creations = None
            self._caller_creations = None
            self._caller_creations_lock_held = False
            self._overrides.clear()
            self._cancel_event = None
            self._logger = None
            self._conduit_id = None
            self._conduit_name = None
            self._aetheric_frame = None

            self._cleaned = True


    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def root_spell(self) -> ISpell:
        """The root spell being activated for this meld call."""
        return self._root_spell

    @property
    def creations(self) -> Any:
        """
        The owner creations container for this meld call.

        This is typically a `Creations` or `LesserCreations` instance and
        is treated as an opaque handle by the runtime/engine.

        For per-conduit lifetimes, use :meth:`caller_creations` instead.
        """
        return self._creations

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

        This is used by the engine to avoid lock inversion when a caller-scoped
        lock wraps runtime execution and shared existences resolve against the
        same creations container.
        """
        return self._caller_creations_lock_held

    @property
    def overrides(self) -> MutableMapping[str, Any]:
        """
        The normalized override map for this meld call.

        Semantics (matching `_normalize_spell_override`):

            * `{"param": value}` – keyword argument overrides.
            * `{"__args__": [a0, a1, ...]}` – positional overrides.
            * A combination of both is allowed.

        The runtime/engine read from this mapping but do not replace it
        wholesale; callers are free to mutate it if they need to.
        """
        return self._overrides

    @property
    def cancel_event(self) -> Optional[CancellationEvent]:
        """
        Optional cancellation token for this meld call.

        If provided, the runtime/engine should periodically call
        `cancel_event.throw_if_set()` to abort long-running operations.
        """
        return self._cancel_event

    @property
    def logger(self) -> Optional[SafeLogger]:
        """
        Optional SafeLogger associated with this context.

        May be None. Runtime/engine users must always check for None
        before emitting log messages.
        """
        return self._logger

    @property
    def conduit_id(self) -> Optional[str]:
        """Optional unique identifier of the owning Conduit."""
        return self._conduit_id

    @property
    def conduit_name(self) -> Optional[str]:
        """Optional human-readable name of the owning Conduit."""
        return self._conduit_name

    @property
    def aetheric_frame(self) -> Optional[str]:
        """
        Optional aetheric frame name or identifier associated with the
        Conduit / spell context for this meld call.
        """
        return self._aetheric_frame
