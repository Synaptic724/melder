from __future__ import annotations
from threading import RLock
from typing import Any, MutableMapping, Optional, Sequence
# Melder Imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.init_helpers import InitHelpers
from melder.utilities.logger.safe_logger import SafeLogger
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent
from melder.utilities.interfaces.interfaces import ISpell
from melder.spellbook.spell_crafter.dag.resolution_frame.resolution_frame import (
    ResolutionFrame,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


class MeldEngine(Cleanable):
    """
    Per-meld-call execution engine.

    This class is responsible for turning a **validated spell + context**
    into a **concrete Python instance**. In the full design it will:

        * Walk the `DirectedAcyclicWorkGraph` produced by SpellCrafter.
        * Build constructor arguments from:
            - `SpellRequirements`
            - Node dependencies
            - Per-call overrides
        * Reuse instances according to Existence/Creations policy.
        * Store per-node results into a `ResolutionFrame`.

    Current MVP behavior
    --------------------

    For now, the engine implements a **minimal, safe subset**:

        * It assumes a **single-node** graph (no dependencies) and
          simply invokes the root spell's target with overrides.
        * If `root_spell.dependencies` is non-empty, we raise a
          `MeldExecutionError` indicating that DAG-based DI is not yet
          wired up.

    This keeps the shape and contracts stable while we incrementally
    plug in the DAG/requirements semantics.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_context",
        "_root_spell",
        "_dag",
        "_resolution_frame",
        "_requirements",
        "_frame",
        "_logger",
    ]

    def __init__(
            self,
            *,
            context: 'MeldContext',
            root_spell: ISpell,
            dag: Any,
            resolution_frame: Any,
            requirements: Any,
            frame: ResolutionFrame,
            logger: Optional[Any] = None,
    ) -> None:
        super().__init__()

        if context is None:
            raise ValueError("context cannot be None.")
        if root_spell is None:
            raise ValueError("root_spell cannot be None.")
        if frame is None:
            raise ValueError("frame cannot be None.")

        self._lock: RLock = RLock()
        self._context: 'MeldContext' = context
        self._root_spell: ISpell = root_spell
        self._dag: Any = dag
        self._resolution_frame: Any = resolution_frame
        self._requirements: Any = requirements
        self._frame: ResolutionFrame = frame
        self._logger: Optional[SafeLogger] = (
            InitHelpers.resolve_safe_logger(logger)
            if logger is not None
            else None
        )


    # ------------------------------------------------------------------ #
    # Cleanup
    # ------------------------------------------------------------------ #

    def cleanup(self) -> None:
        """
        Deterministically clear references held by this engine.

        The runtime owns the lifetime of the engine; after `run()` has
        completed (success or error), it is responsible for calling
        `cleanup()` to drop references to the context, spell, DAG, and
        frame so they are eligible for GC.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._context = None  # type: ignore[assignment]
            self._root_spell = None  # type: ignore[assignment]
            self._dag = None
            self._resolution_frame = None
            self._requirements = None
            self._frame = None  # type: ignore[assignment]
            self._logger = None

            self._cleaned = True


    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def context(self) -> 'MeldContext':
        """Per-call `MeldContext` associated with this engine."""
        return self._context

    @property
    def root_spell(self) -> ISpell:
        """Root spell being activated."""
        return self._root_spell

    @property
    def frame(self) -> ResolutionFrame:
        """ResolutionFrame holding overrides and node results."""
        return self._frame

    # ------------------------------------------------------------------ #
    # Core execution
    # ------------------------------------------------------------------ #

    def run(self) -> Any:
        """
        Execute the meld call and return the constructed root instance.

        MVP semantics:

            * If the root spell has **no dependencies**, we treat the
              graph as a single-node and call `_construct_root_only()`.
            * If dependencies are present, we fail fast with a
              `MeldExecutionError` explaining that DAG-based DI is not
              wired up yet.

        Cancellation:
            If the context carries a `CancellationEvent`, it is checked
            once before execution. Future versions can check it at each
            node step.
        """
        self.check_cleaned()

        cancel_event: Optional[CancellationEvent] = self._context.cancel_event
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        spell = self._root_spell

        # For now, we only support a single-node spell (no dependencies).
        if spell.dependencies:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=(
                    "MeldEngine only supports root spells with no DI "
                    "dependencies in the current MVP. The spell has "
                    f"{len(spell.dependencies)} dependencies; DAG-based "
                    "DI execution must be implemented before it can be "
                    "melded."
                ),
            )

        instance = self._construct_root_only()

        # Best-effort: if ResolutionFrame exposes a mutable node_results
        # mapping, store the root instance under its spell_id.
        try:
            node_results = self._frame.node_results  # type: ignore[attr-defined]
            if isinstance(node_results, MutableMapping):
                node_results[spell.spell_index.current] = instance
        except Exception:
            # Diagnostics should never break execution.
            pass

        return instance

    def _construct_root_only(self) -> Any:
        """
        Construct the root spell instance using only override metadata.

        This path is used when we either have no DAG yet or the DAG is
        effectively a single node with no dependencies.

        Resolution logic (MVP):

            * For EXISTING_CREATION* spells:
                - Return `spell.user_created_object` if available.
            * For class/method/lambda spells:
                - Use overrides from `ResolutionFrame.overrides`:
                    - `__args__` (list/tuple) → positional args
                    - other keys → keyword args
                - Invoke `spell.spell(*args, **kwargs)`.
            * For anything else:
                - Return `spell.spell` as-is (value spell).

        Any exception raised by the underlying callable is wrapped in a
        `MeldExecutionError` with the root spell's identity attached.
        """
        spell = self._root_spell

        # Existing creation spells should never reach here in the typical
        # pipeline, but we support them defensively.
        if spell.is_existing_creation:
            if not spell.has_existing_object:
                raise MeldExecutionError(
                    spell_id=spell.spell_index.current,
                    spell_name=spell.spell_name,
                    message=(
                        "Existing-creation spell has no "
                        "`user_created_object` attached."
                    ),
                )
            return spell.user_created_object

        target = spell.spell

        # Only factory-like spells are expected here.
        if not (spell.is_class_spell or spell.is_method_spell or spell.is_lambda_spell):
            # Treat everything else as a value spell.
            return target

        overrides = self._frame.overrides  # type: ignore[attr-defined]
        if overrides is None:
            overrides = {}

        # Positional overrides
        raw_args = overrides.get("__args__")
        if isinstance(raw_args, Sequence) and not isinstance(raw_args, (str, bytes)):
            args = list(raw_args)
        else:
            args = []

        # Keyword overrides (all keys except "__args__")
        kwargs = {
            key: value
            for key, value in overrides.items()
            if key != "__args__"
        }

        try:
            instance = target(*args, **kwargs)
        except Exception as exc:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=f"Error invoking spell target {spell.spell_name!r}.",
                inner=exc,
            ) from exc

        return instance