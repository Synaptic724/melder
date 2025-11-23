from __future__ import annotations
import inspect
import threading
from typing import Any, List, Optional, Tuple, Union, get_args, get_origin

# Melder imports
from melder.utilities.interfaces.interfaces import ISpell
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.spell_parameter_requirements import (
    SpellParameterRequirement,
)
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.spell_requirements import (
    SpellRequirements,
)
from melder.spellbook.spell_types.spell_types import SpellType
from melder.aether.conduit.meld.spellmap.spellmap import SpellMap
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent
from melder.utilities.general_base.cleanable import Cleanable


class SpellRequirementsFinder(Cleanable):
    """
    Phase 1 **requirements extractor** for a single :class:`Spell`.

    Responsibilities
    ----------------

    * Inspect the Spell's **call target** (class constructor or callable).
    * Walk its signature and classify each parameter into a
      :class:`SpellParameterRequirement`.
    * Produce a single :class:`SpellRequirements` instance describing
      everything Phase 2+ need to know about this spell's DI expectations.

    It is:

        * **Per-spell** – one instance per Spell during a Phase 1 pass.
        * **Stateless after build** – once :meth:`build_requirements` is
          called, you can drop this finder and keep only the
          :class:`SpellRequirements` object.
        * **Cleanable** – when you're done with requirements for this cycle,
          call :meth:`cleanup` to null out references and help the GC.

    It is **deliberately dumb** about the Spellbook:

        * No lookups.
        * No resolution.
        * No DAG construction.

    It just answers:

        *“What does this spell *want* injected, according to its signature?”*
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_spell",
        "_requirements",
    ]

    def __init__(self, spell: ISpell) -> None:
        """
        Create a new requirements finder for the given :class:`Spell`.

        Args:
            spell:
                The Spell whose call target should be analysed. The Spell is
                treated as read-only; this finder never mutates it.
        """
        Cleanable.__init__(self)

        if spell is None:
            raise ValueError("spell must not be None.")

        self._lock: threading.RLock = threading.RLock()
        self._spell: ISpell = spell
        self._requirements: Optional[SpellRequirements] = None

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def cleanup(self) -> None:
        """
        Deterministically tear down this finder.

        Behavior:
            * Idempotent.
            * Cleans up the attached :class:`SpellRequirements` if present.
            * Nulls out references to the Spell and requirements.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            if self._requirements is not None:
                try:
                    self._requirements.cleanup()
                except Exception:
                    pass

            self._requirements = None
            self._spell = None
            self._cleaned = True

        self._lock = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def spell(self) -> ISpell:
        """
        The underlying :class:`Spell` being analysed.
        """
        self.check_cleaned()
        return self._spell

    def build_requirements(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> SpellRequirements:
        """
        Execute **Phase 1** for this Spell and return the resulting
        :class:`SpellRequirements`.

        This method is **idempotent**:

            * On first call, it performs the full inspection.
            * On subsequent calls, it returns the previously computed
              requirements object.

        Args:
            cancel_event:
                Optional :class:`CancellationEvent` used for cooperative
                cancellation. If provided and set, this method aborts early
                with :class:`OperationCancelledError`.

        Returns:
            SpellRequirements: A freshly built or cached requirements object
            for the underlying spell.
        """
        self.check_cleaned()

        if self._requirements is not None:
            return self._requirements

        self._throw_if_cancelled(cancel_event)

        spell = self._spell

        # Existing creation spells have **no constructor DI** – we only need
        # to project identity + existence.
        if spell.spell_type in (
                SpellType.EXISTING_CREATION,
                SpellType.EXISTING_CREATION_WITH_SPELLFRAME,
                SpellType.EXISTING_CREATION_WITH_BINDING_NAME_WITH_SPELLFRAME,
        ):
            parameters: List[SpellParameterRequirement] = []
        else:
            call_target = self._resolve_call_target(spell)
            parameters = self._build_parameter_requirements(
                call_target=call_target,
                cancel_event=cancel_event,
            )

        requirements = SpellRequirements(
            spell_id=spell.spell_id,
            spell_type=spell.spell_type,
            existence=spell.existence,
            spellframe=spell.spellframe,
            binding_name=spell.binding_name,
            parameters=parameters,
        )

        self._requirements = requirements
        return requirements

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _throw_if_cancelled(
            self,
            cancel_event: Optional[CancellationEvent],
    ) -> None:
        if cancel_event is not None and cancel_event.is_set:
            # We use the shared OperationCancelledError semantics via the
            # event helper.
            cancel_event.throw_if_set()

    def _resolve_call_target(self, spell: ISpell) -> Any:
        """
        Determine the **call target** for this spell.

        For now, this is simply the underlying ``spell.spell`` attribute:

            * For class-based spells this is the class object itself
              (``inspect.signature`` will look at ``__init__``).
            * For method / lambda spells this is the underlying callable.
            * For any other SpellType we still return ``spell.spell`` and
              let later phases decide how (or if) DI should apply.

        This method does **not** call or mutate the target.
        """
        return spell.spell

    def _build_parameter_requirements(
            self,
            *,
            call_target: Any,
            cancel_event: Optional[CancellationEvent],
    ) -> List[SpellParameterRequirement]:
        """
        Inspect the call target's signature and build a list of
        :class:`SpellParameterRequirement` instances.

        This is the **core** of Phase 1 for a single spell: it performs the
        actual introspection and classification.
        """
        try:
            signature = inspect.signature(call_target)
        except (TypeError, ValueError):
            # Some exotic/builtin callables may not have an inspectable
            # signature; treat them as having no DI requirements.
            return []

        requirements: List[SpellParameterRequirement] = []

        for index, (param_name, parameter) in enumerate(signature.parameters.items()):
            self._throw_if_cancelled(cancel_event)

            # Basic shape flags.
            is_var_positional = parameter.kind is inspect.Parameter.VAR_POSITIONAL
            is_var_keyword = parameter.kind is inspect.Parameter.VAR_KEYWORD
            is_keyword_only = parameter.kind is inspect.Parameter.KEYWORD_ONLY

            has_default = parameter.default is not inspect.Parameter.empty
            default_value = parameter.default if has_default else None

            has_annotation = parameter.annotation is not inspect.Parameter.empty
            annotation = parameter.annotation if has_annotation else None

            # Start classification from the most obviously "non-DI" cases.
            if param_name in ("self", "cls") or is_var_positional or is_var_keyword:
                di_shape = ParameterDIShape.IGNORE
                is_optional = True  # These are never required from DI's POV.
                collection_element_annotation = None
                spellmap_default = None
            else:
                (
                    di_shape,
                    is_optional,
                    collection_element_annotation,
                    spellmap_default,
                ) = self._classify_parameter(
                    annotation=annotation,
                    has_annotation=has_annotation,
                    default_value=default_value,
                    has_default=has_default,
                )

            requirement = SpellParameterRequirement(
                name=param_name,
                position=index,
                kind=parameter.kind,
                annotation=annotation,
                default_value=default_value,
                has_default=has_default,
                is_var_positional=is_var_positional,
                is_var_keyword=is_var_keyword,
                is_keyword_only=is_keyword_only,
                is_optional=is_optional,
                di_shape=di_shape,
                collection_element_annotation=collection_element_annotation,
                spellmap_default=spellmap_default,
            )
            requirements.append(requirement)

        return requirements

    def _classify_parameter(
            self,
            *,
            annotation: Any,
            has_annotation: bool,
            default_value: Any,
            has_default: bool,
    ) -> Tuple[ParameterDIShape, bool, Any, Optional[SpellMap]]:
        """
        Map a raw annotation + default value pair into a high-level
        :class:`ParameterDIShape` plus optional metadata.

        This is intentionally conservative:

            * We only classify as DI when the patterns match our contract
              (SpellMap default, non-builtin types, collection-of-type).
            * Everything else is treated as :data:`ParameterDIShape.PLAIN`.

        Returns:
            Tuple of:

                (di_shape, is_optional, collection_element_annotation, spellmap_default)
        """
        # SpellMap default has top priority: explicit beats implicit.
        if has_default and isinstance(default_value, SpellMap):
            # SpellMap DI is always logically "optional" – the DI system
            # can always fall back to: "just use this SpellMap."
            return (
                ParameterDIShape.SPELLMAP_DEFAULT,
                True,
                None,
                default_value,
            )

        # If there is no annotation at all, we can't infer DI.
        if not has_annotation or annotation is None:
            return ParameterDIShape.PLAIN, has_default, None, None

        # Unwrap Optional[T] / Union[T, None] / T | None first.
        base_annotation, is_optional = self._unwrap_optional(annotation)

        # Detect list[T] collections.
        origin = get_origin(base_annotation)
        args = get_args(base_annotation)
        if origin is list and len(args) == 1:
            element_annotation = args[0]
            # Only treat as DI if the element looks like a DI candidate.
            if self._looks_like_di_target(element_annotation):
                return (
                    ParameterDIShape.COLLECTION_BY_ANNOTATION,
                    is_optional or has_default,
                    element_annotation,
                    None,
                )

        # Single-type DI by annotation (class/Protocol/etc.).
        if self._looks_like_di_target(base_annotation):
            return (
                ParameterDIShape.SINGLE_BY_ANNOTATION,
                is_optional or has_default,
                None,
                None,
            )

        # Everything else is plain.
        return ParameterDIShape.PLAIN, is_optional or has_default, None, None

    def _unwrap_optional(self, annotation: Any) -> Tuple[Any, bool]:
        """
        If the annotation is an Optional/Union-with-None, unwrap it and
        return (inner_annotation, is_optional).

        Supports:

            * Optional[T]
            * Union[T, None]
            * T | None
        """
        origin = get_origin(annotation)
        args = get_args(annotation)

        # PEP 604 unions (T | None) show up as types.UnionType in 3.11+,
        # but get_origin/get_args still behave like typing.Union.
        if origin is Union and args:
            # Check if NoneType is present.
            has_none = False
            non_none_args: List[Any] = []
            for arg in args:
                if arg is type(None):
                    has_none = True
                else:
                    non_none_args.append(arg)

            if has_none:
                if len(non_none_args) == 1:
                    return non_none_args[0], True
                # Multiple non-None types – still optional, but we can't
                # simplify the union further here.
                return annotation, True

        return annotation, False

    def _looks_like_di_target(self, annotation: Any) -> bool:
        """
        Heuristic check to decide if a type annotation is a DI candidate.

        Rules (for now):

            * Builtin scalars (int, str, float, bool, bytes, etc.) are
              treated as **non-DI**.
            * User-defined classes and Protocol/interface types (i.e. not
              from the ``builtins`` module) are treated as DI candidates.
            * String annotations are treated as **potential** DI candidates;
              later phases can resolve them against the Spellbook.
        """
        # String annotations will be resolved later; treat them as potential DI.
        if isinstance(annotation, str):
            return True

        # For things that behave like classes, use module heuristics.
        if inspect.isclass(annotation):
            module_name = getattr(annotation, "__module__", "")
            if module_name == "builtins":
                return False
            # Typing / Protocol / ABCs / user code – all fair game here.
            return True

        # Anything else – e.g. typing.Any, typing.Callable, etc. – is
        # currently treated as non-DI. We can refine this later if needed.
        return False
