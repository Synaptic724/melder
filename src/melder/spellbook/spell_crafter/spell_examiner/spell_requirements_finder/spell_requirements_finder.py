from __future__ import annotations
import inspect
import threading
from typing import Any, List, Optional, Tuple, Union, get_args, get_origin
# Melder imports
from melder.spellbook.spell import Spell
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
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.contracts.mutation_contract import MutationContract
from melder.utilities.interfaces.interfaces import ISpell
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent
from melder.utilities.general_base.cleanable import Cleanable


class SpellRequirementsFinder(Cleanable):
    """
    Phase 1 **requirements extractor** for a single :class:`Spell`.

    High-level role
    ----------------
    This object is responsible for taking a bound :class:`Spell` and answering a
    *single* question:

        **“According to this spell’s signature, what does it want from DI?”**

    It does this by:

    * Inspecting the spell’s **call target** (class, `__init__`, function, or method).
    * Walking the `inspect.Signature` for the call target.
    * Classifying each parameter into a :class:`SpellParameterRequirement`.
    * Producing a :class:`SpellRequirements` artifact that later phases can consume.

    Design constraints
    ------------------
    * **Per-spell**: one finder per spell per phase run.
    * **Stateless-ish**: once :meth:`build_requirements` is called, you can discard
      this object and keep only the :class:`SpellRequirements`.
    * **No Spellbook access**: this finder does **not** perform lookups or DAG work.
      It does not know about other spells, existence policies, or resolution.

    Identity model
    --------------
    The resulting :class:`SpellRequirements` is keyed by the spell’s *version ID*:

        ``spell.spell_index.current``

    That version string is stored as ``SpellRequirements.spell_id`` and is the
    canonical identity for all Phase 1+ artifacts (requirements, symbolic graphs,
    DAG nodes, etc.).
    """

    __slots__ = Cleanable.__slots__ + [
        "_spell",
        "_requirements",
        "_lock",
    ]

    def __init__(self, spell: ISpell) -> None:
        """
        Initialize a new requirements finder for the given :class:`Spell`.

        Args:
            spell:
                The :class:`Spell` whose call target should be analysed. The Spell is
                treated as read-only; this finder never mutates the Spell.
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
            * Idempotent – safe to call multiple times.
            * If a :class:`SpellRequirements` instance is attached, it is cleaned up.
            * Internal references to the :class:`Spell` and requirements are nulled.

        This is intended to help GC and clearly signal that the finder is no longer
        usable after a resolution cycle.
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
                    # Cleanup must never propagate failures upward.
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

        Returns:
            Spell: The spell instance this finder was constructed with.

        Raises:
            RuntimeError:
                If the finder has been cleaned and is no longer usable.
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

        Semantics
        ---------
        This method is **idempotent**:

        * On first call, it performs the full inspection and constructs a
          :class:`SpellRequirements` instance.
        * On subsequent calls, it returns the previously computed requirements
          object.

        Cancellation
        ------------
        If ``cancel_event`` is provided and is set at any point during processing,
        the method aborts and delegates to ``cancel_event.throw_if_set()`` which
        raises the shared :class:`OperationCancelledError`.

        Returns:
            SpellRequirements:
                A freshly built or cached requirements object for the underlying
                spell. The ``spell_id`` field is always the *versioned* identifier:

                    ``spell.spell_index.current``
        """
        self.check_cleaned()

        if self._requirements is not None:
            return self._requirements

        self._throw_if_cancelled(cancel_event)

        spell = self._spell

        # Existing creation spells have **no constructor DI** – they represent
        # already-instantiated objects, so we only need to project identity +
        # existence. Constructor parameters are irrelevant to DI.
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

        # IMPORTANT:
        # Use the **SpellIndex.current** as the canonical identifier for all
        # phase artifacts. This decouples phase logic from any legacy `spell_id`
        # storage and allows versioning of the spell’s structure.
        version_id: str = spell.spell_index.current

        requirements = SpellRequirements(
            spell_id=version_id,
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
        """
        Helper that checks the cancellation token and throws if set.

        Args:
            cancel_event:
                Optional event; if None, this is a no-op.

        Raises:
            OperationCancelledError:
                If ``cancel_event`` is provided and set.
        """
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

    def _resolve_call_target(self, spell: ISpell) -> Any:
        """
        Determine the **call target** for this spell.

        Rules
        -----
        * Class spells
            → The class object itself (``inspect.signature`` handles mapping to
              ``__init__`` internally).
        * Method / lambda spells
            → The underlying callable stored on ``spell.spell``.
        * Everything else
            → Still returns ``spell.spell``; later phases can decide how to treat it.

        This method does **not** call or mutate the target.

        Args:
            spell:
                The owning :class:`Spell`.

        Returns:
            Any: The object to use as the call target for signature introspection.
        """
        if spell.is_class_spell:
            return spell.spell

        if spell.is_method_spell or spell.is_lambda_spell:
            return spell.spell

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

        This is the **core** of Phase 1 for a single spell: it intersects raw
        Python signatures with Melder's DI heuristics.

        Steps
        -----
        * Obtain an :class:`inspect.Signature` for the call target.
        * Iterate the parameters in order.
        * For each parameter:
            - Compute basic flags (var-positional, var-keyword, keyword-only, etc.).
            - Capture annotation and default.
            - Classify DI shape via :meth:`_classify_parameter`.
            - Construct a :class:`SpellParameterRequirement` that records all
              relevant metadata.

        Args:
            call_target:
                The object to introspect. Typically a class, function or method.
            cancel_event:
                Optional cancellation token.

        Returns:
            list[SpellParameterRequirement]:
                Ordered list of requirements corresponding to the call target's
                parameters.
        """
        try:
            signature = inspect.signature(call_target)
        except (TypeError, ValueError):
            # Some exotic / builtin callables may not expose a usable signature.
            # In that case, we treat them as having no DI-visible parameters.
            return []

        requirements: List[SpellParameterRequirement] = []

        for index, (param_name, parameter) in enumerate(signature.parameters.items()):
            self._throw_if_cancelled(cancel_event)

            is_var_positional = parameter.kind is inspect.Parameter.VAR_POSITIONAL
            is_var_keyword = parameter.kind is inspect.Parameter.VAR_KEYWORD
            is_keyword_only = parameter.kind is inspect.Parameter.KEYWORD_ONLY

            has_default = parameter.default is not inspect.Parameter.empty
            default_value = parameter.default if has_default else None

            has_annotation = parameter.annotation is not inspect.Parameter.empty
            annotation = parameter.annotation if has_annotation else None

            # Non-DI shapes and boilerplate parameters.
            if param_name in ("self", "cls") or is_var_positional or is_var_keyword:
                di_shape = ParameterDIShape.IGNORE
                is_optional = True  # These are never satisfied by DI.
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
        Classify a parameter into a :class:`ParameterDIShape` plus metadata.

        Decision rules
        --------------
        1. **SpellMap default wins**:
           If the default value is a :class:`SpellMap`, this is always classified
           as :data:`ParameterDIShape.SPELLMAP_DEFAULT`. This is the most explicit
           form of DI, and is treated as logically optional (the SpellMap itself
           is the fallback).

        2. **No annotation**:
           If there is no annotation, the parameter is classified as
           :data:`ParameterDIShape.PLAIN`. DI does not attempt to satisfy it;
           caller / defaults must.

        3. **Optional / Union**:
           Optional / Union-with-None shapes are unwrapped via
           :meth:`_unwrap_optional` to determine a "base" annotation and an
           `is_optional` flag.

        4. **list[T] collections**:
           If the base annotation is a parametrized list and the element looks like
           a DI target, the parameter is classified as
           :data:`ParameterDIShape.COLLECTION_BY_ANNOTATION`.

        5. **Bare DI-eligible annotation**:
           If the base annotation itself looks like a DI target (non-builtin class,
           Protocol-like, or string), it is classified as
           :data:`ParameterDIShape.SINGLE_BY_ANNOTATION`.

        6. **Everything else**:
           Classified as :data:`ParameterDIShape.PLAIN`.

        Returns:
            tuple:
                (di_shape, is_optional, collection_element_annotation, spellmap_default)
        """
        # Mutation / contract defaults are explicit sockets controlled by
        # dynamic/mutation flows. They take precedence over normal DI hints.
        if has_default and isinstance(default_value, MutationContract):
            return (
                ParameterDIShape.MUTATION_CONTRACT,
                True,   # logically optional – the contract object itself is fallback
                None,   # no collection element annotation
                None,   # no SpellMap default
            )

        if has_default and isinstance(default_value, SpellContract):
            return (
                ParameterDIShape.SPELL_CONTRACT,
                True,   # logically optional – the contract object itself is fallback
                None,
                None,
            )

        # SpellMap default has top priority among "normal" DI hints: explicit beats implicit.
        if has_default and isinstance(default_value, SpellMap):
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
        return ``(inner_annotation, is_optional)``.

        Supported shapes
        ----------------
        * ``Optional[T]``
        * ``Union[T, None]``
        * ``T | None`` (PEP 604)

        For multi-type unions (e.g. ``Union[A, B, None]``) we still treat the
        overall annotation as optional but keep the union intact as the
        "base" annotation.
        """
        origin = get_origin(annotation)
        args = get_args(annotation)

        # PEP 604 unions (T | None) show up as types.UnionType in 3.11+,
        # but get_origin/get_args still behave like typing.Union.
        if origin is Union and args:
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

        Rules
        -----
        * Builtin scalars (``int``, ``str``, ``float``, ``bool``, ``bytes``,
          etc.) are treated as **non-DI**.
        * User-defined classes and Protocol/interface types (anything not in
          the ``builtins`` module) are treated as DI candidates.
        * String annotations are treated as **potential** DI candidates;
          later phases may resolve them against the Spellbook or a type map.

        Returns:
            bool: True if this annotation is considered a DI target.
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
