import ast
import builtins
import inspect
import threading
import typing
import types
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union, get_args, get_origin, ClassVar
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from mypy_extensions import mypyc_attr

# Melder imports
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_parameter_requirements import (
    SpellParameterRequirement,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_requirements import (
    SpellRequirements,
)
from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.contracts.mutation_contract import MutationContract
from melder.utilities.general_base.cleanable import Cleanable
if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


@mypyc_attr(native_class=True)
class SpellRequirementsFinder(Cleanable):
    """
    Build the Phase 1 requirement artifact for one bound: class: 'Spell`.

    This finder is the boundary between raw Python callable inspection and the
    later SpellCrafter phases that plan or resolve dependencies. Its job is to
    examine the spell's callable surface, decide which parameters look like DI
    sockets, and emit a: class:`SpellRequirements` artifact that downstream
    planning code can trust without re-inspecting the original callable.

    In practical terms, this object answers four questions for one spell:

    * Which callable should Phase 1 inspect?
    * Which parameters are plain Python arguments versus DI-managed sockets?
    * Which sockets are optional, collection-based, or backed by explicit
      contract objects?
    * Which stable spell identity should later phase artifacts use?

    Scope boundaries
    ----------------
    * Inspects signatures and annotations only.
    * Does not query the Spellbook, walk dependency graphs, or resolve
      providers.
    * Copies spell identity and routing metadata into the result, but does not
      interpret resolution policy beyond parameter classification.

    Lifecycle
    ---------
    * Constructed for one spell and typically used for one Phase 1 pass.
    *: meth:`build_requirements 'caches the resulting: class:`SpellRequirements` object for repeat callers.
    * After cleanup, the finder is unusable and releases both the spell
      reference and any cached requirements artifact.

    Identity model
    --------------
    The emitted :class:`SpellRequirements` is keyed by
    "spell.spell_index.current". That versioned spell identifier is the
    canonical Phase 1 identity used by later planning artifacts, so this finder
    intentionally anchors its output to the current spell version rather than
    any legacy unversioned spell id.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_spell",
        "_requirements",
        "_lock",
    ]
    __deletable__ = [
        "_spell",
        "_requirements",
        "_lock",
    ]

    _TYPING_ALIASES: ClassVar[Dict[str, object]] = {
        "Optional": typing.Optional,
        "Union": typing.Union,
        "List": typing.List,
        "Dict": typing.Dict,
        "Set": typing.Set,
        "Tuple": typing.Tuple,
        "FrozenSet": typing.FrozenSet,
        "Iterable": typing.Iterable,
        "Sequence": typing.Sequence,
        "Mapping": typing.Mapping,
    }

    def __init__(self, spell: Spell) -> None:
        """
        Initialize a new requirements finder for the given: class: 'Spell`.

        Args:
            spell:
                The :class: 'Spell` whose call target should be analyzed. The Spell is
                treated as read-only; this finder never mutates the Spell.
        """
        Cleanable.__init__(self)

        if spell is None:
            raise ValueError("spell must not be None.")

        self._lock: threading.RLock = threading.RLock()
        self._spell: Spell = spell
        self._requirements: Optional[SpellRequirements] = None

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def cleanup(self) -> None:
        """
        Deterministically tear down this finder.

        Behaviour:
            * Idempotent - safe to call multiple times.
            * If a: class:`SpellRequirements` instance is attached, it is cleaned up.
            * Internal references to the: class: 'Spell` and requirements are nulled.

        This is intended to help GC and clearly signals that the finder is no longer
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
            self._cleaned = True
            del self._requirements
            del self._spell
        del self._lock

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def spell(self) -> Spell:
        """
        The underlying: class: 'Spell` being analyzed.

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
        Run Phase 1 for the bound spell and return its requirement artifact.

        This is the public entrypoint for the finder. On the first call it
        chooses the spell's inspection target, classifies the visible
        parameters, and builds a: class:`SpellRequirements` object that later
        phases can consume without touching the original callable again. On
        later calls it returns the cached artifact.

        Contract:
            * Idempotent for a live finder instance.
            * Preserves signature order in the emitted parameter list.
            * Copies spell identity, spell type, existence mode, spellframe, and
              binding name into the result.
            * Uses "spell.spell_index.current" as the result's canonical
              "spell_id".

        Special case:
            Existing-creation spell variants intentionally yield an empty
            parameter list. Those spells represent already-instantiated objects,
            so Phase 1 should preserve identity metadata but must not invent
            constructor requirements that no longer participate in DI.

        Cancellation:
            If "cancel_event" is provided and becomes set during processing,
            this method delegates to "cancel_event.throw_if_set()" and aborts
            without finishing a new artifact.

        Returns:
            SpellRequirements:
                The cached or newly-built Phase 1 artifact for this spell.
        """
        self.check_cleaned()

        if self._requirements is not None:
            return self._requirements

        self._throw_if_cancelled(cancel_event)

        spell = self._spell

        # Existing creation spells have **no constructor DI** - they represent
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
        # storage and allows versioning of the spell's structure.
        version_id = spell.spell_index.current
        if version_id is None:
            raise RuntimeError(
                "SpellRequirementsFinder requires a live SpellIndex current id."
            )

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
                If "cancel_event" is provided and set.
        """
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

    def _resolve_call_target(self, spell: Spell) -> Any:
        """
        Determine the **call target** for this spell.

        Rules
        -----
        * Class spells
            -> The class object itself (``inspect.signature`` handles mapping to
              "__init__" internally).
        * Method / lambda spells
            -> The underlying callable stored on "spell.spell".
        * Everything else
            -> Still returns "spell.spell"; later phases can decide how to treat it.

        This method does **not** call or mutate the target.

        Args:
            spell:
                The owning: class: 'Spell`.

        Returns:
            Any: The object to use as the call target for signature introspection.
        """
        if spell.is_class_spell:
            return spell.spell

        if spell.is_method_spell or spell.is_lambda_spell:
            return spell.spell

        return spell.spell

    def _annotation_needs_resolution(self, annotation: Any) -> bool:
        """
        Decide whether a single annotation requires forward-ref resolution.

        Purpose:
            Identify annotations that need evaluation or normalization before
            Phase 1 classification can run safely.
        Contract:
            - Returns True for string and ForwardRef annotations.
            - Returns True when nested generic args include resolvable tokens.
            - Returns False when no resolution is required.
        Args:
            annotation:
                The raw annotation object from a signature or __annotations__.
        Returns:
            bool: True if resolution is required, otherwise False.
        """
        if isinstance(annotation, str):
            return True
        if isinstance(annotation, typing.ForwardRef):
            return True
        origin = get_origin(annotation)
        if origin is None:
            return False
        args = get_args(annotation)
        for arg in args:
            if self._annotation_needs_resolution(arg):
                return True
        return False

    def _should_resolve_annotations(
            self,
            *,
            call_target: Any,
            signature: inspect.Signature,
    ) -> bool:
        """
        Decide whether Phase 1 must resolve annotations for this call target.

        Purpose:
            Avoid unnecessary annotation resolution when the signature does not
            include forward refs or string expressions.
        Contract:
            - Returns True when inspect.get_annotations is custom.
            - Returns True when any parameter annotation needs resolution.
            - Returns False only when all parameter annotations are safe to use as-is.
        Args:
            call_target:
                The callable or class being analyzed.
            signature:
                Signature for the call target.
        Returns:
            bool: True if annotation resolution should run.
        """
        if call_target is None:
            return False

        try:
            get_annotations_fn = inspect.get_annotations
            get_annotations_module = get_annotations_fn.__module__
        except AttributeError:
            get_annotations_module = None

        if get_annotations_module != "inspect":
            return True

        for parameter in signature.parameters.values():
            annotation = parameter.annotation
            if annotation is inspect.Parameter.empty:
                continue
            if self._annotation_needs_resolution(annotation):
                return True

        return False

    def _resolve_parameter_annotations(
            self,
            call_target: Any,
    ) -> Dict[str, Any]:
        """
        Normalize parameter annotations into classifier-friendly runtime values.

        This helper is where Phase 1 bridges Python's flexible annotation model
        into the smaller set of shapes that Melder's requirement classifier
        understands. The goal is not perfect typing evaluation; the goal is to
        turn obvious forward references and generic expressions into stable
        objects when possible so the classifier can make truthful DI decisions.

        Resolution strategy:
            * For class targets, inspect "__init__" annotations because that
              is the callable surface DI will satisfy.
            * Prefer "inspect.get_annotations(..., eval_str=True)" so string
              annotations and forward refs resolve through the target's module
              and local namespace.
            * Fall back to non-evaluated annotations when full evaluation fails.
            * Run a final normalization pass so nested string or generic
              fragments can still be simplified when partial resolution
              succeeded.

        Failure posture:
            Annotation resolution is best-effort. This method intentionally does
            not raise when annotation evaluation fails; unresolved values are
            carried forward so classification can degrade conservatively instead
            of breaking Phase 1.

        Args:
            call_target:
                The class or callable whose parameter annotations should be
                normalized for Phase 1.

        Returns:
            Dict[str, Any]:
                Mapping of a parameter name to the best normalized annotation value
                Phase 1 could derive for that parameter.
        """
        if call_target is None:
            return {}

        is_class_target = inspect.isclass(call_target)
        if is_class_target:
            annotation_target = getattr(call_target, "__init__", call_target)
        else:
            annotation_target = call_target

        raw_annotations: dict[str, Any] | None
        try:
            raw_annotations = dict(annotation_target.__annotations__)
        except AttributeError:
            raw_annotations = None

        try:
            get_annotations_fn = inspect.get_annotations
            get_annotations_module = get_annotations_fn.__module__
        except AttributeError:
            get_annotations_module = None
        use_custom_get_annotations = get_annotations_module != "inspect"

        if not raw_annotations:
            if not use_custom_get_annotations:
                return {}

        if raw_annotations:
            needs_resolution = False
            for annotation in raw_annotations.values():
                if self._annotation_needs_resolution(annotation):
                    needs_resolution = True
                    break

            if not needs_resolution and not use_custom_get_annotations:
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
        for name, value in self._TYPING_ALIASES.items():
            if name not in globalns:
                globalns[name] = value

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

    def _is_simple_annotation_name(self, text: str) -> bool:
        """
        Return True if the annotation string is a simple name or dotted path.

        Purpose:
            Fast-path name-like strings that do not require AST parsing.
        Contract:
            - Rejects expressions containing subscripts, unions, or whitespace.
            - Rejects literal constants like "None", "True", and "False".
            - Accepts dotted identifier paths (e.g. "pkg.TypeName").
        Args:
            text:
                Raw annotation string.
        Returns:
            bool: True if the string is a simple name/path.
        """
        if not text:
            return False
        if text.strip() != text:
            return False
        if text in ("None", "True", "False"):
            return False
        if any(token in text for token in ("[", "]", "|", ",", " ", "(", ")", "{", "}", "=")):
            return False
        parts = text.split(".")
        for part in parts:
            if not part or not part.isidentifier():
                return False
        return True

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
                The resolved object if found, otherwise "None".
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
            - Union via "|" (``Foo | None``).

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
                return list.__class_getitem__(args[0])
            return sentinel

        if container in (set, typing.Set):
            if len(args) == 1:
                return set.__class_getitem__(args[0])
            return sentinel

        if container in (frozenset, typing.FrozenSet):
            if len(args) == 1:
                return frozenset.__class_getitem__(args[0])
            return sentinel

        if container in (dict, typing.Dict):
            if len(args) == 2:
                return dict.__class_getitem__((args[0], args[1]))
            return sentinel

        if container in (tuple, typing.Tuple):
            if len(args) == 2 and args[1] is Ellipsis:
                return tuple.__class_getitem__((args[0], Ellipsis))
            return tuple.__class_getitem__(args)

        if container in (typing.Optional, Optional):
            if len(args) == 1:
                return Union[args[0], type(None)]
            return sentinel

        if container in (typing.Union, Union):
            return Union[args]

        if hasattr(container, "__class_getitem__"):
            try:
                if len(args) == 1:
                    return container.__class_getitem__(args[0])
                return container.__class_getitem__(args)
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
            - "typing.ForwardRef" objects to their underlying names or types.
            - Nested generic arguments where possible (e.g. list[ "Foo"]).

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
            if self._is_simple_annotation_name(annotation):
                resolved = self._resolve_annotation_name(annotation, globalns, localns)
                return resolved if resolved is not None else annotation
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
                The origin type from: func:`typing.get_origin`.
            args:
                Normalized argument tuple.

        Returns:
            Any:
                The rebuilt annotation, or the original if unsupported.
        """
        if not args:
            return annotation

        if origin is list and len(args) == 1:
            return list.__class_getitem__(args[0])

        if origin is set and len(args) == 1:
            return set.__class_getitem__(args[0])

        if origin is frozenset and len(args) == 1:
            return frozenset.__class_getitem__(args[0])

        if origin is dict and len(args) == 2:
            return dict.__class_getitem__((args[0], args[1]))

        if origin is tuple:
            if len(args) == 2 and args[1] is Ellipsis:
                return tuple.__class_getitem__((args[0], Ellipsis))
            return tuple.__class_getitem__(args)

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
        Convert the inspected callable signature into ordered requirement records.

        This is the core Phase 1 transformation for a normal spell. It walks the
        chosen call target once, preserves Python signature order, and emits one: class:`SpellParameterRequirement` per visible parameter so later phases
        can reason about sockets without re-inspecting the callable.

        The emitted records intentionally preserve both Python-level facts and
        Melder-specific classification:

            * Python-level facts: parameter order, kind, default presence, raw
              or normalized annotation, and keyword-only or vararg flags.
            * Melder-level facts: whether the parameter is optional for DI,
              whether it should be ignored by DI, whether it requests a single
              dependency, a collection, or an explicit contract object, and any
              carried "SpellMap" default.

        Non-DI boilerplate parameters such as "self", "cls", "*args", and
        "**kwargs" still produce requirement rows, but they are explicitly
        marked with: data:`ParameterDIShape.IGNORE` so later phases can keep the
        original callable shape without trying to satisfy those parameters from
        DI.

        Args:
            call_target:
                The callable or class surface selected for signature inspection.
            cancel_event:
                Optional cancellation token checked between parameters.

        Returns:
            list[SpellParameterRequirement]:
                Ordered requirement records mirroring the target signature.
        """
        try:
            signature = inspect.signature(call_target)
        except (TypeError, ValueError):
            # Some exotic / builtin callables may not expose a usable signature.
            # In that case, we treat them as having no DI-visible parameters.
            return []

        requirements: List[SpellParameterRequirement] = []
        needs_resolution = self._should_resolve_annotations(
            call_target=call_target,
            signature=signature,
        )
        if needs_resolution:
            resolved_annotations = self._resolve_parameter_annotations(call_target)
        else:
            resolved_annotations = {}

        for index, (param_name, parameter) in enumerate(signature.parameters.items()):
            self._throw_if_cancelled(cancel_event)

            is_var_positional = parameter.kind is inspect.Parameter.VAR_POSITIONAL
            is_var_keyword = parameter.kind is inspect.Parameter.VAR_KEYWORD
            is_keyword_only = parameter.kind is inspect.Parameter.KEYWORD_ONLY

            has_default = parameter.default is not inspect.Parameter.empty
            default_value = parameter.default if has_default else None

            has_annotation = parameter.annotation is not inspect.Parameter.empty
            raw_annotation = parameter.annotation if has_annotation else None
            if needs_resolution:
                annotation = resolved_annotations.get(param_name, raw_annotation)
            else:
                annotation = raw_annotation

            # Non-DI shapes and boilerplate parameters.
            if param_name in ("self", "cls") or is_var_positional or is_var_keyword:
                di_shape = ParameterDIShape.IGNORE
                is_optional = True  # DI never satisfies these.
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
        Classify one parameter into Melder's Phase 1 DI-shape model.

        This method defines the precedence rules that later phases are allowed
        to trust. Its output decides whether a parameter participates in DI at
        all, whether it expects a single provider or a collection, and whether
        an explicit contract or default object overrides normal
        annotation-based inference.

        Precedence order:
            1. "MutationContract" defaults win first because they describe a
               dedicated mutation socket rather than a normal dependency.
            2. "SpellContract" defaults win next for the same reason: the
               parameter is explicitly asking for a spell contract object.
            3. "SpellMap" defaults win over annotations because an explicit
               map is a stronger statement than an inferred type-based lookup.
            4. Missing annotations fall back to: data:`ParameterDIShape.PLAIN`.
            5. Optional wrappers are removed only far enough to inspect the
               underlying dependency shape.
            6. "list[T]" becomes: data:`ParameterDIShape.COLLECTION_BY_ANNOTATION` when "T"
               looks like a DI candidate.
            7. A remaining DI-eligible annotation becomes: data:`ParameterDIShape.SINGLE_BY_ANNOTATION`.
            8. Everything else stays: data:`ParameterDIShape.PLAIN`.

        The returned "is_optional" flag answers a Melder-specific question:
        can Phase 1 treat failure to supply this dependency as acceptable
        because the signature or explicit default already provides a fallback?

        Args:
            param_name:
                Parameter name retained for parity with future diagnostics.
            annotation:
                Raw or normalized annotation chosen for classification.
            has_annotation:
                Whether the parameter has an explicit annotation.
            default_value:
                Raw default object from the Python signature.
            has_default:
                Whether a default value is present.

        Returns:
            tuple:
                "(di_shape, is_optional, collection_element_annotation,
                spellmap_default)" where the extra values carry the additional
                metadata later phases need for collection resolution or explicit
                SpellMap fallback handling.
        """
        # Mutation / contract defaults are explicit sockets controlled by
        # dynamic/mutation flows. They take precedence over normal DI hints.
        if has_default and isinstance(default_value, MutationContract):
            return (
                ParameterDIShape.MUTATION_CONTRACT,
                True,   # logically optional - the contract object itself is fallback
                None,   # no collection element annotation
                None,   # no SpellMap default
            )

        if has_default and isinstance(default_value, SpellContract):
            return (
                ParameterDIShape.SPELL_CONTRACT,
                True,   # logically optional - the contract object itself is fallback
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
        origin = get_origin(annotation)
        args = get_args(annotation)
        (
            base_annotation,
            is_optional,
            base_origin,
            base_args,
        ) = self._unwrap_optional(
            annotation=annotation,
            origin=origin,
            args=args,
        )

        # Detect list[T] collections.
        if base_origin is list and len(base_args) == 1:
            element_annotation = base_args[0]
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

    def _unwrap_optional(
            self,
            *,
            annotation: Any,
            origin: Any,
            args: Tuple[Any, ...],
    ) -> Tuple[Any, bool, Any, Tuple[Any, ...]]:
        """
        Strip the "None" wrapper from optional annotations for classification.

        Phase 1 cares about two separate facts:

            * whether the parameter is optional for DI purposes
            * what the underlying dependency shape looks like once "None" is
              removed from the type expression

        This helper splits those concerns. For simple optional shapes it returns
        the inner dependency annotation plus "is_optional=True". For broader
        multi-type unions it still records the parameter as optional but keeps
        the original union intact so the classifier does not pretend it can
        fully understand or simplify the remaining alternatives.

        Returns:
            Tuple[Any, bool, Any, Tuple[Any, ...]]:
                "(base_annotation, is_optional, base_origin, base_args)" for
                the classifier's next stage.
        """
        base_annotation = annotation
        is_optional = False
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
                is_optional = True
                if len(non_none_args) == 1:
                    base_annotation = non_none_args[0]
                # Multiple non-None types - still optional, but we cannot
                # simplify the union further here.
                else:
                    base_annotation = annotation

        if base_annotation is annotation:
            return base_annotation, is_optional, origin, args

        base_origin = get_origin(base_annotation)
        base_args = get_args(base_annotation)
        return base_annotation, is_optional, base_origin, base_args

    def _looks_like_di_target(self, annotation: Any) -> bool:
        """
        Apply a conservative heuristic for "does this annotation look injectable?"

        This is intentionally a Phase 1 heuristic, not a full-resolution engine.
        The method leans conservative for builtin scalar values and permissive
        for user-defined interfaces or classes because later phases can still
        reject an unsatisfied dependency, but a false negative here would erase
        a socket from the requirements artifact entirely.

        Current policy:
            * "typing.Any" and builtin scalar or object shapes are not treated
              as DI targets.
            * Forward refs and unresolved strings remain eligible because the
              annotation-normalization step may resolve them into user types.
            * Non-builtin classes, ABC-like interfaces, and Protocol-like types
              are treated as DI candidates.

        Returns:
            bool:
                True when Phase 1 should treat the annotation as a possible DI
                socket, otherwise False.
        """
        if annotation is typing.Any:
            return False

        if annotation in (int, float, str, bool, bytes, bytearray, complex, object, type(None)):
            return False

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
            # Typing / Protocol / ABCs / user code - all fair game here.
            return True

        # Anything else - e.g. typing.Any, typing.Callable, etc. - is
        # currently treated as non-DI. We can refine this later if needed.
        return False
