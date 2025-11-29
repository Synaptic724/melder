from __future__ import annotations
from threading import RLock
from typing import Any, Mapping, MutableMapping, Optional
# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.init_helpers import InitHelpers
from melder.utilities.logger.safe_logger import SafeLogger
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent
from melder.utilities.interfaces.interfaces import ISpell


class MeldContext(Cleanable):
    """
    Per-meld-call orchestration context for the Meld runtime.

    This object is created for **each individual `meld(...)` call** and
    captures everything the runtime/engine need to execute that call:

        * The **root spell** being activated.
        * The **creations container** representing the current Conduit scope.
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
           - Conduit's creations object
           - Normalized overrides map
           - (optionally) cancel event, logger, conduit metadata
    3. `MeldRuntime.execute(context)` is called.
    4. After execution returns, `Meld` / `MeldRuntime` call
       `context.cleanup()`.

    This class does **not** perform any DI or DAG work itself – it is
    purely a container for per-call configuration and wiring.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_root_spell",
        "_creations",
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
    ) -> None:
        super().__init__()

        if root_spell is None:
            raise ValueError("root_spell cannot be None.")

        self._lock: RLock = RLock()
        self._root_spell: ISpell = root_spell
        self._creations: Any = self._root_spell._owner_creations

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
        The Conduit-scope creations container.

        This is typically a `Creations` or `LesserCreations` instance and
        is treated as an opaque handle by the runtime/engine.
        """
        return self._creations

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