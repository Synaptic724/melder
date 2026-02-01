import ast
import builtins
import inspect
import threading
import typing
import types
from typing import Any, Dict, List, Optional, Tuple, Union, get_args, get_origin
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
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

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
    __melder_internal__ = _mrg.sentinel
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

    def _resolve_parameter_annotations(
            self,
            call_target: Any,
    ) -> Dict[str, Any]:
        """
        Resolve parameter annotations for the given call target.

        This performs a best-effort forward-reference evaluation using
        ``inspect.get_annotations(eval_str=True)``. If evaluation fails,
        it falls back to raw annotations and then normalizes any forward
        reference tokens or string expressions it can resolve from the
        available namespaces.
        If no forward references or string annotations are present, this
        returns the raw annotations without eval.

        Args:
            call_target:
                The class or callable whose signature annotations should
                be resolved.

        Returns:
            Dict[str, Any]:
                Mapping of parameter name -> normalized annotation.
        """
        if call_target is None:
            return {}

        is_class_target = inspect.isclass(call_target)
        if is_class_target:
            annotation_target = getattr(call_target, "__init__", call_target)
        else:
            annotation_target = call_target

        try:
            raw_annotations = annotation_target.__annotations__
        except AttributeError:
            raw_annotations = None

        if not raw_annotations:
            return {}

        def _annotation_needs_resolution(annotation: Any) -> bool:
            if isinstance(annotation, str):
                return True
            if isinstance(annotation, typing.ForwardRef):
                return True
            origin = get_origin(annotation)
            if origin is None:
                return False
            args = get_args(annotation)
            for arg in args:
                if _annotation_needs_resolution(arg):
                    return True
            return False

        needs_resolution = False
        for annotation in raw_annotations.values():
            if _annotation_needs_resolution(annotation):
                needs_resolution = True
                break

        if not needs_resolution:
            return raw_annotations

        if is_class_target:
            module = inspect.getmodule(call_target)
            globalns = dict(getattr(module, "__dict__", {}) if module else {})
            localns: Dict[str, Any] = dict(vars(call_target))
        else:
            globalns = dict(getattr(call_target, "__globals__", {}) or {})
            localns = {}

        if "__builtins__" not in globalns:
            globalns["__builtins__"] = builtins

        # Ensure the typing module is accessible for "typing.Any" style annotations.
        if "typing" not in globalns:
            globalns["typing"] = typing
        for name, value in typing.__dict__.items():
            globalns.setdefault(name, value)

        try:
            annotations = inspect.get_annotations(
                annotation_target,
                eval_str=True,
                globals=globalns,
                locals=localns,
            )
        except Exception:
            try:
                annotations = inspect.get_annotations(
                    annotation_target,
                    eval_str=False,
                    globals=globalns,
                    locals=localns,
                )
            except Exception:
                annotations = {}

        normalized: Dict[str, Any] = {}
        for name, annotation in annotations.items():
            normalized[name] = self._normalize_annotation(
                annotation=annotation,
                globalns=globalns,
                localns=localns,
            )

        return normalized

    def _resolve_annotation_name(
            self,
            name: str,
            globalns: Dict[str, Any],
            localns: Dict[str, Any],
    ) -> Optional[Any]:
        """
        Resolve a forward-ref name token against the provided namespaces.

        Args:
            name:
                The forward-ref token (e.g. "MyType" or "pkg.MyType").
            globalns:
                Module-level globals used for resolution.
            localns:
                Local namespace for class-level symbols.

        Returns:
            Optional[Any]:
                The resolved object if found, otherwise ``None``.
        """
        if name in localns:
            return localns[name]

        if name in globalns:
            return globalns[name]

        builtins_obj = globalns.get("__builtins__")
        if isinstance(builtins_obj, dict):
            if name in builtins_obj:
                return builtins_obj[name]
        elif builtins_obj is not None and hasattr(builtins_obj, name):
            return getattr(builtins_obj, name)

        if "." in name:
            root_name, *rest = name.split(".")
            root = self._resolve_annotation_name(root_name, globalns, localns)
            if root is None:
                return None
            current = root
            for attr in rest:
                if not hasattr(current, attr):
                    return None
                current = getattr(current, attr)
            return current

        return None

    def _parse_annotation_expression(
            self,
            text: str,
            globalns: Dict[str, Any],
            localns: Dict[str, Any],
    ) -> Tuple[bool, Any]:
        """
        Parse a string annotation expression into a normalized object.

        This supports a safe subset of expression forms:
            - Name and attribute references (``Foo``, ``typing.List``).
            - Subscripted generics (``list[Foo]``, ``Optional[Foo]``).
            - Union via ``|`` (``Foo | None``).

        Args:
            text:
                The raw annotation string.
            globalns:
                Namespace used for resolution.
            localns:
                Namespace used for resolution.

        Returns:
            Tuple[bool, Any]:
                A tuple of (success, value). If parsing fails, success is False.
        """
        try:
            parsed = ast.parse(text, mode="eval")
        except SyntaxError:
            return False, None

        sentinel = object()
        resolved = self._resolve_annotation_node(
            node=parsed.body,
            globalns=globalns,
            localns=localns,
            sentinel=sentinel,
        )
        if resolved is sentinel:
            return False, None
        return True, resolved

    def _resolve_annotation_node(
            self,
            *,
            node: ast.AST,
            globalns: Dict[str, Any],
            localns: Dict[str, Any],
            sentinel: object,
    ) -> Any:
        """
        Resolve a parsed annotation AST node into a runtime object.

        Args:
            node:
                AST node representing part of the annotation expression.
            globalns:
                Namespace used for resolution.
            localns:
                Namespace used for resolution.
            sentinel:
                Sentinel used to signal unsupported nodes.

        Returns:
            Any:
                The resolved annotation object, or the sentinel if unsupported.
        """
        if isinstance(node, ast.Name):
            resolved = self._resolve_annotation_name(node.id, globalns, localns)
            return resolved if resolved is not None else node.id

        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.Attribute):
            base = self._resolve_annotation_node(
                node=node.value,
                globalns=globalns,
                localns=localns,
                sentinel=sentinel,
            )
            if base is sentinel:
                return sentinel
            if isinstance(base, str):
                return f"{base}.{node.attr}"
            if hasattr(base, node.attr):
                return getattr(base, node.attr)
            return sentinel

        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            left = self._resolve_annotation_node(
                node=node.left,
                globalns=globalns,
                localns=localns,
                sentinel=sentinel,
            )
            right = self._resolve_annotation_node(
                node=node.right,
                globalns=globalns,
                localns=localns,
                sentinel=sentinel,
            )
            if left is sentinel or right is sentinel:
                return sentinel
            return Union[left, right]

        if isinstance(node, ast.Subscript):
            container = self._resolve_annotation_node(
                node=node.value,
                globalns=globalns,
                localns=localns,
                sentinel=sentinel,
            )
            if container is sentinel:
                return sentinel

            slice_node = node.slice
            if isinstance(slice_node, ast.Tuple):
                args_nodes = slice_node.elts
            else:
                args_nodes = [slice_node]

            args: List[Any] = []
            for arg_node in args_nodes:
                arg_value = self._resolve_annotation_node(
                    node=arg_node,
                    globalns=globalns,
                    localns=localns,
                    sentinel=sentinel,
                )
                if arg_value is sentinel:
                    return sentinel
                args.append(arg_value)

            return self._build_subscripted_annotation(
                container=container,
                args=tuple(args),
                sentinel=sentinel,
            )

        return sentinel

    def _build_subscripted_annotation(
            self,
            *,
            container: Any,
            args: Tuple[Any, ...],
            sentinel: object,
    ) -> Any:
        """
        Build a subscripted annotation from a container and args.

        Args:
            container:
                The container type or alias (e.g. list, typing.List).
            args:
                The resolved subscript arguments.
            sentinel:
                Sentinel used to indicate unsupported containers.

        Returns:
            Any:
                The constructed annotation, or the sentinel if unsupported.
        """
        if not args:
            return sentinel

        if container in (list, typing.List):
            if len(args) == 1:
                return list[args[0]]
            return sentinel

        if container in (set, typing.Set):
            if len(args) == 1:
                return set[args[0]]
            return sentinel

        if container in (frozenset, typing.FrozenSet):
            if len(args) == 1:
                return frozenset[args[0]]
            return sentinel

        if container in (dict, typing.Dict):
            if len(args) == 2:
                return dict[args[0], args[1]]
            return sentinel

        if container in (tuple, typing.Tuple):
            if len(args) == 2 and args[1] is Ellipsis:
                return tuple[args[0], Ellipsis]
            return tuple[args]

        if container in (typing.Optional, Optional):
            if len(args) == 1:
                return Union[args[0], None]
            return sentinel

        if container in (typing.Union, Union):
            return Union[args]

        if hasattr(container, "__class_getitem__"):
            try:
                if len(args) == 1:
                    return container[args[0]]
                return container[args]
            except Exception:
                return sentinel

        return sentinel

    def _normalize_annotation(
            self,
            *,
            annotation: Any,
            globalns: Dict[str, Any],
            localns: Dict[str, Any],
    ) -> Any:
        """
        Normalize a single annotation by resolving forward references.

        This resolves:
            - String tokens that map to known globals/locals.
            - ``typing.ForwardRef`` objects to their underlying names or types.
            - Nested generic arguments where possible (e.g. list["Foo"]).

        Args:
            annotation:
                The raw annotation value.
            globalns:
                Namespace used for resolution.
            localns:
                Namespace used for resolution.

        Returns:
            Any:
                The normalized annotation object.
        """
        if annotation is None:
            return None

        if isinstance(annotation, str):
            parsed, resolved_expr = self._parse_annotation_expression(
                annotation,
                globalns,
                localns,
            )
            if parsed:
                if isinstance(resolved_expr, str):
                    resolved = self._resolve_annotation_name(
                        resolved_expr,
                        globalns,
                        localns,
                    )
                    return resolved if resolved is not None else resolved_expr
                return self._normalize_annotation(
                    annotation=resolved_expr,
                    globalns=globalns,
                    localns=localns,
                )
            resolved = self._resolve_annotation_name(annotation, globalns, localns)
            return resolved if resolved is not None else annotation

        if isinstance(annotation, typing.ForwardRef):
            name = annotation.__forward_arg__
            resolved = self._resolve_annotation_name(name, globalns, localns)
            return resolved if resolved is not None else name

        origin = get_origin(annotation)
        if origin is None:
            return annotation

        args = get_args(annotation)
        if not args:
            return annotation

        normalized_args = tuple(
            self._normalize_annotation(
                annotation=arg,
                globalns=globalns,
                localns=localns,
            )
            for arg in args
        )

        return self._rebuild_annotation(
            annotation=annotation,
            origin=origin,
            args=normalized_args,
        )

    def _rebuild_annotation(
            self,
            *,
            annotation: Any,
            origin: Any,
            args: Tuple[Any, ...],
    ) -> Any:
        """
        Attempt to rebuild a parametrized annotation with normalized args.

        If the origin does not support reconstruction, the original
        annotation is returned unchanged.

        Args:
            annotation:
                The original annotation object.
            origin:
                The origin type from :func:`typing.get_origin`.
            args:
                Normalized argument tuple.

        Returns:
            Any:
                The rebuilt annotation, or the original if unsupported.
        """
        if not args:
            return annotation

        if origin is list and len(args) == 1:
            return list[args[0]]

        if origin is set and len(args) == 1:
            return set[args[0]]

        if origin is frozenset and len(args) == 1:
            return frozenset[args[0]]

        if origin is dict and len(args) == 2:
            return dict[args[0], args[1]]

        if origin is tuple:
            if len(args) == 2 and args[1] is Ellipsis:
                return tuple[args[0], Ellipsis]
            return tuple[args]

        if origin is Union or origin is types.UnionType:
            return Union[args]

        return annotation

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
            - Resolve annotations (including forward references) and capture defaults.
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
        resolved_annotations = self._resolve_parameter_annotations(call_target)

        for index, (param_name, parameter) in enumerate(signature.parameters.items()):
            self._throw_if_cancelled(cancel_event)

            is_var_positional = parameter.kind is inspect.Parameter.VAR_POSITIONAL
            is_var_keyword = parameter.kind is inspect.Parameter.VAR_KEYWORD
            is_keyword_only = parameter.kind is inspect.Parameter.KEYWORD_ONLY

            has_default = parameter.default is not inspect.Parameter.empty
            default_value = parameter.default if has_default else None

            has_annotation = parameter.annotation is not inspect.Parameter.empty
            raw_annotation = parameter.annotation if has_annotation else None
            annotation = resolved_annotations.get(param_name, raw_annotation)

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
                    param_name=param_name,
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
            param_name: str,
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

        Args:
            param_name:
                The parameter name for diagnostics.
            annotation:
                The resolved annotation object.
            has_annotation:
                Whether the parameter has an explicit annotation.
            default_value:
                The raw default value from the signature.
            has_default:
                Whether a default value is present.
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

        if origin in (Union, types.UnionType) and args:
            has_none = False
            non_none_args: List[Any] = []
            for arg in args:
                if isinstance(arg, typing.ForwardRef):
                    arg_value = arg.__forward_arg__
                else:
                    arg_value = arg

                if arg_value is type(None):
                    has_none = True
                else:
                    non_none_args.append(arg_value)

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
          Phase 1 attempts to resolve them before classification.

        Returns:
            bool: True if this annotation is considered a DI target.
        """
        if isinstance(annotation, typing.ForwardRef):
            return True

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
