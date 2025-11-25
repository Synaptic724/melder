from __future__ import annotations
from threading import RLock
from typing import Any, Optional

from melder.aether.conduit.meld.meld_engine.meld_engine import MeldEngine
# Melder Imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.init_helpers import InitHelpers
from melder.utilities.logger.safe_logger import SafeLogger
from melder.spellbook.spell import Spell  # For type clarity; interface is ISpell-like
from melder.spellbook.spell_crafter.dag.resolution_frame.resolution_frame import (
    ResolutionFrame,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


class MeldRuntime(Cleanable):
    """
    Orchestration façade for meld execution.

    `MeldRuntime` sits between the Conduit-level `Meld` façade and the
    low-level `MeldEngine`. It owns **no spell-specific state** and can
    be:

        * Constructed per-Conduit, or
        * Shared across multiple conduits (if desired later).

    Responsibilities
    ----------------

    * Perform **pre-flight checks** on the root spell:

        - Must not be broken (`spell.is_broken`).
        - Should be validated (`spell.validated`).
        - May have a dependency graph / resolution frame attached.

    * Create a **ResolutionFrame** per execution, initialized with
      per-call overrides from `MeldContext`.

    * Construct and invoke a **MeldEngine** to actually create the
      instance.

    * Ensure deterministic cleanup of the engine and frame after
      execution.

    This class deliberately does **not** know anything about Creations
    or Existence semantics; those remain in `Meld`. The runtime only
    focuses on "given this spell and this context, build me the object".
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_logger",
    ]

    def __init__(self, logger: Optional[Any] = None) -> None:
        """
        Initialize a new `MeldRuntime`.

        Args:
            logger:
                Optional logger instance. If provided, it is normalized
                to a `SafeLogger` via `InitHelpers.resolve_safe_logger`.
                May be None for silent operation.
        """
        super().__init__()
        self._lock: RLock = RLock()
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
        Deterministically clear references held by this runtime.

        The runtime is typically owned by a Conduit or Spellbook. This
        method drops the logger reference and marks the runtime as
        cleaned; subsequent calls to `execute` will fail via
        `check_cleaned()`.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._logger = None
            self._cleaned = True


    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def logger(self) -> Optional[SafeLogger]:
        """Optional `SafeLogger` attached to this runtime."""
        return self._logger

    # ------------------------------------------------------------------ #
    # Core API
    # ------------------------------------------------------------------ #

    def execute(self, context: "MeldContext") -> Any:
        """
        Execute a single meld call described by `context`.

        This method is the **primary entrypoint** that `Meld` should
        call when it needs to construct a new root instance.

        Flow:
            1. Validate the runtime and context.
            2. Perform basic spell invariants:
                 - not broken
                 - validated
            3. Snapshot build-time artifacts from the spell:
                 - dependency graph
                 - requirements
                 - resolution frame (if any)
            4. Create a `ResolutionFrame` initialized with the normalized
               overrides from the context.
            5. Instantiate `MeldEngine` and delegate to `engine.run()`.
            6. Clean up engine and frame.
            7. Sanity-check the result for factory-style spells.

        Returns:
            The constructed root instance.

        Raises:
            MeldExecutionError:
                If the spell is broken or has not been validated, or if
                the engine fails with a DI-related error, or if a
                factory-style spell yields no instance.
            ValueError:
                If the context is None or missing a root spell.
        """
        self.check_cleaned()

        if context is None:
            raise ValueError("context cannot be None.")

        spell_obj = context.root_spell
        if spell_obj is None:
            raise ValueError("context.root_spell cannot be None.")

        # Work with the concrete Spell facade type when available.
        spell: Spell = spell_obj  # type: ignore[assignment]

        # --- Invariants from the SpellCrafter / validation pipeline ----
        if spell.is_broken:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message="Cannot execute meld runtime for a broken spell.",
            )

        if not spell.validated:
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=(
                    "Spell has not been validated. Run the SpellCrafter "
                    "phases before attempting to meld this spell."
                ),
            )

        # Snapshot build-time artifacts. These may be None depending on
        # how far the SpellCrafter pipeline has run; the engine can decide
        # how much it needs for the current MVP.
        dag = spell.dependency_graph
        requirements = spell.requirements
        resolution_frame = spell.resolution_frame

        if self._logger is not None:
            self._logger.debug(
                f"MeldRuntime.execute: spell={spell.spell_name} "
                f"({spell.spell_index.current})",
                "MeldRuntime",
            )

        # Per-execution ResolutionFrame seeded with per-call overrides.
        frame = ResolutionFrame(overrides=context.overrides)

        engine = MeldEngine(
            context=context,
            root_spell=spell,
            dag=dag,
            resolution_frame=resolution_frame,
            requirements=requirements,
            frame=frame,
            logger=self._logger,
        )

        result = None
        try:
            result = engine.run()
        finally:
            # Always tear down engine + frame to avoid leaks.
            try:
                engine.cleanup()
            except Exception:
                pass

            try:
                frame.cleanup()
            except Exception:
                pass

        # ------------------------------------------------------------------
        # Sanity check: factory-style spells must produce an instance.
        #
        # For EXISTING_CREATION spells, reuse is handled earlier in Meld
        # (via _get_existing_creation). For class/method/lambda spells,
        # a `None` result usually indicates a bug in the engine or the
        # callable, so we surface it as a deterministic MeldExecutionError.
        # ------------------------------------------------------------------
        if (
                result is None
                and (spell.is_class_spell or spell.is_method_spell or spell.is_lambda_spell)
        ):
            raise MeldExecutionError(
                spell_id=spell.spell_index.current,
                spell_name=spell.spell_name,
                message=(
                    "MeldEngine returned None for a factory-style spell. "
                    "This usually indicates a bug in the DI pipeline or the "
                    "spell's constructor."
                ),
            )

        return result
