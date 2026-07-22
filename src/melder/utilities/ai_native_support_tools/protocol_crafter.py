import ast
import inspect
import re
import threading
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
    get_args,
    get_origin,
    ClassVar,
)



from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
FunctionNode = Union[ast.FunctionDef, ast.AsyncFunctionDef]


class ProtocolCrafter(Cleanable):
    """

    Purpose:
        Generate protocol code from a target class or object and maintain
        protocol blocks inside interface files.

    IT WRITES TO DISK - the unusual part:
        Most of this codebase reads source; this one MODIFIES it. The
        `write_protocol_module_from_source_file(...)` and bounded block-update
        paths edit interface files in place. That makes it the sharpest tool in
        `utilities/`, and the reason its updates are BOUNDED: it rewrites a
        delimited region rather than a whole file, so hand-written code around
        the generated block survives regeneration.

    Registration:
        MELDER KERNEL - guarded. Melder owns code-generation policy. It is
        nonetheless exported for direct use: guarding and exposure are
        orthogonal, and this is a tool a user calls rather than one Melder
        injects.

    Subsystem Context:
        The only member of `utilities/ai_native_support_tools/`, and one of the
        two AI-native surfaces in `utilities/` alongside
        `ClassSurfaceAstDescriber`. The pairing is natural: the describer READS
        a class surface into a structured answer, this one WRITES a class
        surface out as a Protocol. Same reflection, opposite direction.

    System Context:
        Exported from the package root, so an agent that has `import melder` can
        reach it directly. It serves the interface discipline the repository
        follows - concrete types plus `TYPE_CHECKING` imports by default, with
        Protocols written only where structure genuinely is the contract - by
        making the Protocol half mechanical instead of hand-maintained.

    Contract:
        - Accepts either a class object or a concrete instance as the target.
        - Produces one `@runtime_checkable` protocol block whose name is the
          target class name prefixed with `I`.
        - Mirrors class and method docstrings when present and generates
          fallback docstrings when they are missing.
        - Mirrors attributes from class annotations/class-level values and, for
          object inputs, current instance state.
        - Mirrors methods as protocol stubs with `...` bodies.
        - When `include_inheritance=True`, walks the target MRO and mirrors
          inherited members too.
        - File-update helpers are bounded to append/remove behavior for protocol
          blocks; they do not attempt broad import rewriting or arbitrary file
          refactors.

    Threading:
        Public operations execute under the instance `RLock` so generation and
        file updates remain grouped and deterministic in a nogil runtime.

    Lifecycle:
        Cleanup is idempotent and only releases the crafter's local state.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Generates @runtime_checkable Protocol code from a class/object "
        "(craft_protocol_code) and maintains bounded protocol blocks in interface files "
        "(write_protocol_module_from_source_file). Exported for direct use; guarded, so call "
        "it - do not bind it. It WRITES to disk, editing a delimited region only."
    )
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
    ]
    _TYPING_FAMILY_NAMES: ClassVar[set[str]] = {
        "Any",
        "Optional",
        "Union",
        "List",
        "Dict",
        "Tuple",
        "Set",
        "FrozenSet",
        "Sequence",
        "Mapping",
        "Iterable",
        "Iterator",
        "Callable",
        "Literal",
        "Type",
        "ClassVar",
    }
    _PROTOCOL_MODULE_IMPORT_NAMES: ClassVar[tuple[str, ...]] = (
        "Any",
        "Callable",
        "ClassVar",
        "Dict",
        "FrozenSet",
        "Iterable",
        "Iterator",
        "List",
        "Literal",
        "Mapping",
        "Optional",
        "Protocol",
        "Sequence",
        "Set",
        "Tuple",
        "Type",
        "Union",
        "runtime_checkable",
    )

    def __init__(self) -> None:
        """
        Initialize one protocol crafter utility.

        Contract:
            - STATELESS BEYOND ITS IDENTITY: it holds only an id and a lock. Protocol
              crafting reads source and writes modules without accumulating state, so
              one crafter can serve many unrelated targets.

        Owned State:
            Owns its id and lock; borrows nothing.

        Threading:
            Creates the lock that serializes crafting operations.

        Lifecycle / Cleanup:
            Ready immediately; no configuration step.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        """
        Idempotently clear the protocol crafter state.

        Contract:
            - IDEMPOTENT under double-checked locking.
            - Owns no external resources, so cleanup releases identity only - it does
              not touch any module it previously wrote.

        Threading:
            Double-checked around the crafter lock.

        Lifecycle / Cleanup:
            Safe to call more than once and from more than one thread.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            del self._id
        del self._lock

    @property
    def id(self) -> str:
        """
        Return the stable identifier for this protocol crafter instance.

        Contract:
            - Identifies this crafter instance; stable for its life.

        Threading:
            Reads under `self._lock`, so the result is a coherent snapshot.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

        Returns:
            str: Stable protocol crafter identifier.
        """
        self.check_cleaned()
        with self._lock:
            return self._id

    def craft_protocol_code(
            self,
            target: object,
            *,
            include_inheritance: bool = False,
    ) -> str:
        """
        Generate one protocol code block from a target class or object.

        Args:
            target:
                Target class object or concrete instance to mirror into protocol
                form.
            include_inheritance:
                True to include members from the full non-`object` MRO. False
                to mirror only the direct target class plus current instance
                state when an object instance is provided.

        Returns:
            str: Generated `@runtime_checkable` protocol code block.

        Raises:
            TypeError:
                If `target` is None or cannot be normalized to a class.
        """
        self.check_cleaned()
        with self._lock:
            target_class, target_instance = self._normalize_target(target)
            protocol_name = "I{0}".format(target_class.__name__)
            class_docstring = self._build_docstring_lines(
                inspect.getdoc(target_class),
                fallback="Protocol mirror for {0}.".format(target_class.__name__),
                indent="    ",
            )
            attribute_map = self._collect_attributes(
                target_class,
                target_instance,
                include_inheritance=include_inheritance,
            )
            method_map = self._collect_methods(
                target_class,
                include_inheritance=include_inheritance,
            )

            lines: List[str] = [
                "@runtime_checkable",
                "class {0}(Protocol):".format(protocol_name),
            ]
            lines.extend(class_docstring)

            if not attribute_map and not method_map:
                lines.append("    ...")
                return "\n".join(lines)

            if attribute_map:
                lines.append("")
                for attribute_name, annotation_text in attribute_map.items():
                    lines.append(
                        "    {0}: {1}".format(attribute_name, annotation_text)
                    )

            if method_map:
                for method_name, method_lines in method_map.items():
                    _ = method_name
                    lines.append("")
                    lines.extend(method_lines)

            return "\n".join(lines).rstrip() + "\n"

    def craft_protocol_module_code_from_source_file(
            self,
            source_file_path: Union[str, Path],
            class_name: str,
            *,
            protocol_name: Optional[str] = None,
    ) -> str:
        """
        Build one complete protocol-module string from a source file and class.

        Args:
            source_file_path:
                Path to the Python source file that defines the target class.
            class_name:
                Exact class name to mirror into protocol form.
            protocol_name:
                Optional explicit protocol class name. Defaults to `I<class>`.

        Returns:
            str: Fully formed protocol-module source text.

        Raises:
            ValueError:
                If the file cannot be parsed or the class is not found.
        """
        self.check_cleaned()
        with self._lock:
            source_path = Path(source_file_path)
            class_node = self._load_source_class(source_path, class_name)
            resolved_protocol_name = protocol_name or "I{0}".format(class_name)
            class_docstring = ast.get_docstring(class_node) or (
                "Protocol mirror for {0}.".format(class_name)
            )
            attribute_nodes = self._build_protocol_attributes_from_source(
                class_node,
                class_name,
                resolved_protocol_name,
            )
            method_nodes = self._build_protocol_methods_from_source(
                class_node,
                class_name,
                resolved_protocol_name,
            )
            module_node = self._build_protocol_module_ast(
                resolved_protocol_name,
                class_docstring,
                attribute_nodes,
                method_nodes,
            )
            return self._render_protocol_module_ast(module_node)

    def write_protocol_module_from_source_file(
            self,
            source_file_path: Union[str, Path],
            class_name: str,
            output_directory: Union[str, Path],
            *,
            protocol_name: Optional[str] = None,
    ) -> Path:
        """
        Write one generated protocol module into a chosen directory.

        Args:
            source_file_path:
                Path to the Python source file that defines the target class.
            class_name:
                Exact class name to mirror into protocol form.
            output_directory:
                Directory that will receive the generated protocol module.
            protocol_name:
                Optional explicit protocol class name. Defaults to `I<class>`.

        Contract:
            - DEFAULTS THE PROTOCOL NAME to `I` + the class name when none is supplied,
              so `Foo` becomes `IFoo` unless you override it.
            - WRITES TO DISK: it crafts the module text and then persists it, so this
              is not a pure computation. Use the `craft_...` method when you want the
              text without a file.
            - Overwrites an existing file at the resolved output path.

        Threading:
            Reads under `self._lock`, so the result is a coherent snapshot.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

        Returns:
            Path: Written protocol-module path.
        """
        self.check_cleaned()
        with self._lock:
            resolved_protocol_name = protocol_name or "I{0}".format(class_name)
            module_text = self.craft_protocol_module_code_from_source_file(
                source_file_path,
                class_name,
                protocol_name=resolved_protocol_name,
            )
            output_path = self._write_protocol_module_text(
                module_text,
                output_directory,
                resolved_protocol_name,
            )
            return output_path

    def craft_joined_protocol_module_code(
            self,
            targets: Sequence[Tuple[Union[str, Path], str]],
            protocol_name: str,
    ) -> str:
        """
        Build one protocol module from the shared surface of multiple classes.

        Args:
            targets:
                `(source_file_path, class_name)` tuples to compare.
            protocol_name:
                Protocol class name to emit for the shared surface.

        Returns:
            str: Fully formed shared protocol-module source text.

        Raises:
            ValueError:
                If fewer than two targets are supplied or a class cannot be
                located.
        """
        self.check_cleaned()
        with self._lock:
            if len(targets) < 2:
                raise ValueError("Joined protocol generation requires at least two targets.")
            source_models = self._load_joined_source_models(targets)
            attribute_nodes = self._build_joined_protocol_attributes(
                source_models,
                protocol_name,
            )
            method_nodes = self._build_joined_protocol_methods(
                source_models,
                protocol_name,
            )
            class_names = [item[1] for item in source_models]
            class_docstring = (
                "Common protocol extracted from {0}.".format(
                    ", ".join(class_names)
                )
            )
            module_node = self._build_protocol_module_ast(
                protocol_name,
                class_docstring,
                attribute_nodes,
                method_nodes,
            )
            return self._render_protocol_module_ast(module_node)

    def write_joined_protocol_module(
            self,
            targets: Sequence[Tuple[Union[str, Path], str]],
            protocol_name: str,
            output_directory: Union[str, Path],
    ) -> Path:
        """
        Write one joined protocol module into a chosen directory.

        Args:
            targets:
                `(source_file_path, class_name)` tuples to compare.
            protocol_name:
                Protocol class name to emit for the shared surface.
            output_directory:
                Directory that will receive the generated protocol module.

        Contract:
            - Crafts ONE protocol module covering SEVERAL targets, so the protocol name
              is required rather than derived - there is no single class to derive it
              from.
            - WRITES TO DISK, like its single-source counterpart, and overwrites an
              existing file at the resolved output path.

        Threading:
            Reads under `self._lock`, so the result is a coherent snapshot.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

        Returns:
            Path: Written protocol-module path.
        """
        self.check_cleaned()
        with self._lock:
            module_text = self.craft_joined_protocol_module_code(
                targets,
                protocol_name,
            )
            output_path = self._write_protocol_module_text(
                module_text,
                output_directory,
                protocol_name,
            )
            return output_path

    def add_protocol_to_interface_file(
            self,
            interface_file_path: Union[str, Path],
            protocol_code: str,
    ) -> str:
        """
        Append one generated protocol block into an interface file.

        Args:
            interface_file_path:
                Path to the target interface file.
            protocol_code:
                Generated protocol code block to append.

        Returns:
            str: Updated file contents after the append.

        Raises:
            ValueError:
                If `protocol_code` is empty or the target protocol already
                exists in the file.
        """
        self.check_cleaned()
        with self._lock:
            if not protocol_code or not protocol_code.strip():
                raise ValueError("protocol_code cannot be empty.")
            path = Path(interface_file_path)
            protocol_name = self._extract_protocol_name(protocol_code)
            existing_text = path.read_text(encoding="utf-8") if path.exists() else ""
            if self._contains_protocol(existing_text, protocol_name):
                raise ValueError(
                    "Protocol '{0}' already exists in the interface file.".format(
                        protocol_name
                    )
                )
            stripped_existing_text = existing_text.rstrip()
            stripped_protocol_code = protocol_code.strip()
            if stripped_existing_text:
                updated_text = (
                    stripped_existing_text
                    + "\n\n\n"
                    + stripped_protocol_code
                    + "\n"
                )
            else:
                updated_text = stripped_protocol_code + "\n"
            updated_text = self._normalize_blank_lines(updated_text)
            path.write_text(updated_text, encoding="utf-8")
            return updated_text

    def remove_protocol_from_interface_file(
            self,
            interface_file_path: Union[str, Path],
            protocol_name: str,
    ) -> str:
        """
        Remove one protocol block from an interface file.

        Args:
            interface_file_path:
                Path to the target interface file.
            protocol_name:
                Exact protocol class name to remove.

        Returns:
            str: Updated file contents after removal.

        Raises:
            ValueError:
                If `protocol_name` is empty or the protocol block is not found.
        """
        self.check_cleaned()
        with self._lock:
            if not protocol_name:
                raise ValueError("protocol_name cannot be empty.")
            path = Path(interface_file_path)
            existing_text = path.read_text(encoding="utf-8")
            updated_text = self._remove_protocol_block(existing_text, protocol_name)
            path.write_text(updated_text, encoding="utf-8")
            return updated_text

    def _normalize_target(self, target: object) -> Tuple[type, Optional[object]]:
        """
        Normalize one protocol-crafting target into class and optional instance state.

        Args:
            target:
                Class object or concrete instance supplied to the public
                generation API.

        Returns:
            Tuple[type, Optional[object]]: Target class and optional instance.

        Raises:
            TypeError:
                If `target` is None.
        """
        if target is None:
            raise TypeError("target cannot be None.")
        if inspect.isclass(target):
            return target, None
        return target.__class__, target

    def _collect_attributes(
            self,
            target_class: type,
            target_instance: Optional[object],
            *,
            include_inheritance: bool,
    ) -> Dict[str, str]:
        """
        Collect protocol attribute declarations for the target.

        Args:
            target_class:
                Normalized target class.
            target_instance:
                Optional concrete instance.
            include_inheritance:
                True to walk the full target MRO.

        Returns:
            Dict[str, str]: Attribute name to rendered annotation text.
        """
        attribute_map: Dict[str, str] = {}
        classes_to_scan = self._resolve_classes_to_scan(
            target_class,
            include_inheritance=include_inheritance,
        )
        for current_class in classes_to_scan:
            annotations = getattr(current_class, "__annotations__", {})
            for attribute_name, annotation in annotations.items():
                if self._is_ignored_member_name(attribute_name):
                    continue
                attribute_map[attribute_name] = self._render_annotation(annotation)
            for attribute_name, value in current_class.__dict__.items():
                if self._is_ignored_member_name(attribute_name):
                    continue
                if attribute_name in attribute_map:
                    continue
                if isinstance(value, property):
                    attribute_map[attribute_name] = self._render_annotation(
                        self._get_property_annotation(value)
                    )
                    continue
                if isinstance(value, (staticmethod, classmethod)):
                    continue
                if inspect.isfunction(value):
                    continue
                if inspect.ismethoddescriptor(value):
                    continue
                attribute_map[attribute_name] = self._annotation_from_value(value)
        if target_instance is not None:
            for attribute_name, value in vars(target_instance).items():
                if self._is_ignored_member_name(attribute_name):
                    continue
                if attribute_name not in attribute_map:
                    attribute_map[attribute_name] = self._annotation_from_value(value)
        return attribute_map

    def _collect_methods(
            self,
            target_class: type,
            *,
            include_inheritance: bool,
    ) -> Dict[str, List[str]]:
        """
        Collect protocol method declarations for the target.

        Args:
            target_class:
                Normalized target class.
            include_inheritance:
                True to walk the full target MRO.

        Returns:
            Dict[str, List[str]]: Method name to generated code lines.
        """
        method_map: Dict[str, List[str]] = {}
        classes_to_scan = self._resolve_classes_to_scan(
            target_class,
            include_inheritance=include_inheritance,
        )
        for current_class in classes_to_scan:
            for member_name, value in current_class.__dict__.items():
                if self._is_ignored_method_name(member_name):
                    continue
                function_object = self._unwrap_method_candidate(value)
                if function_object is None:
                    continue
                method_map[member_name] = self._build_method_lines(
                    member_name,
                    function_object,
                )
        return method_map

    def _resolve_classes_to_scan(
            self,
            target_class: type,
            *,
            include_inheritance: bool,
    ) -> List[type]:
        """
        Return the class scan order for attribute and method collection.

        Args:
            target_class:
                Normalized target class.
            include_inheritance:
                True to walk the target MRO.

        Returns:
            List[type]: Classes in base-first order for deterministic override
            behavior.
        """
        if include_inheritance:
            return list(reversed(
                [item for item in target_class.__mro__ if item is not object]
            ))
        return [target_class]

    def _build_method_lines(
            self,
            method_name: str,
            function_object: Callable[..., Any],
    ) -> List[str]:
        """
        Build the generated protocol lines for one mirrored method.

        Args:
            method_name:
                Method name to emit.
            function_object:
                Underlying function object used for signature/docstring
                reflection.

        Returns:
            List[str]: Generated method lines.
        """
        signature_text = self._render_signature(function_object)
        docstring_lines = self._build_docstring_lines(
            inspect.getdoc(function_object),
            fallback="Protocol mirror for `{0}`.".format(method_name),
            indent="        ",
        )
        method_lines = [
            "    def {0}{1}:".format(method_name, signature_text),
        ]
        method_lines.extend(docstring_lines)
        method_lines.append("        ...")
        return method_lines

    def _render_signature(self, function_object: Callable[..., Any]) -> str:
        """
        Render one function signature using protocol-safe annotation text.

        Args:
            function_object:
                Function object to render.

        Returns:
            str: Rendered signature text including the return annotation.
        """
        signature = inspect.signature(function_object)
        parameters = list(signature.parameters.values())
        rendered_parameters: List[str] = []
        saw_var_positional = False
        for index, parameter in enumerate(parameters):
            if (
                    parameter.kind is inspect.Parameter.KEYWORD_ONLY
                    and not saw_var_positional
                    and "*" not in rendered_parameters
            ):
                rendered_parameters.append("*")
            rendered_parameter = self._render_parameter(parameter)
            rendered_parameters.append(rendered_parameter)
            if parameter.kind is inspect.Parameter.VAR_POSITIONAL:
                saw_var_positional = True
            if parameter.kind is inspect.Parameter.POSITIONAL_ONLY:
                next_parameter_is_positional_only = (
                    index + 1 < len(parameters)
                    and parameters[index + 1].kind is inspect.Parameter.POSITIONAL_ONLY
                )
                if not next_parameter_is_positional_only:
                    rendered_parameters.append("/")
        return_annotation = self._render_annotation(signature.return_annotation)
        return "({0}) -> {1}".format(
            ", ".join(rendered_parameters),
            return_annotation,
        )

    def _render_parameter(self, parameter: inspect.Parameter) -> str:
        """
        Render one function parameter for generated protocol output.

        Args:
            parameter:
                Reflected parameter from `inspect.signature(...)`.

        Returns:
            str: Rendered parameter text.
        """
        if parameter.kind is inspect.Parameter.VAR_POSITIONAL:
            parameter_name = "*{0}".format(parameter.name)
        elif parameter.kind is inspect.Parameter.VAR_KEYWORD:
            parameter_name = "**{0}".format(parameter.name)
        else:
            parameter_name = parameter.name

        if parameter.annotation is not inspect._empty:
            parameter_name += ": {0}".format(
                self._render_annotation(parameter.annotation)
            )
        if parameter.default is not inspect._empty:
            parameter_name += " = {0}".format(
                self._render_default_value(parameter.default)
            )
        return parameter_name

    def _render_default_value(self, value: object) -> str:
        """
        Render one default parameter value for generated code.

        Args:
            value:
                Default parameter value.

        Returns:
            str: Rendered default value text.
        """
        if value is None:
            return "None"
        if isinstance(value, (bool, int, float, str, bytes)):
            return repr(value)
        if isinstance(value, tuple):
            return repr(value)
        return "..."

    def _render_annotation(self, annotation: object) -> str:
        """
        Render one annotation into protocol-safe source text.

        Args:
            annotation:
                Annotation object or reflected type hint.

        Returns:
            str: Rendered annotation text.
        """
        if annotation is inspect._empty:
            return "Any"
        if annotation is None or annotation is type(None):
            return "None"
        if isinstance(annotation, str):
            return annotation
        if annotation is Any:
            return "Any"

        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin is Union:
            non_none_args = [item for item in args if item is not type(None)]
            if len(non_none_args) == 1 and len(args) == 2:
                return "Optional[{0}]".format(
                    self._render_annotation(non_none_args[0])
                )
            return "Union[{0}]".format(
                ", ".join(self._render_annotation(item) for item in args)
            )
        if origin in (list, List):
            return "List[{0}]".format(
                self._render_annotation(args[0] if args else Any)
            )
        if origin in (dict, Dict):
            key_annotation = args[0] if len(args) > 0 else Any
            value_annotation = args[1] if len(args) > 1 else Any
            return "Dict[{0}, {1}]".format(
                self._render_annotation(key_annotation),
                self._render_annotation(value_annotation),
            )
        if origin in (tuple, Tuple):
            if len(args) == 2 and args[1] is Ellipsis:
                return "Tuple[{0}, ...]".format(
                    self._render_annotation(args[0])
                )
            return "Tuple[{0}]".format(
                ", ".join(self._render_annotation(item) for item in args)
            )
        if origin is set:
            return "Set[{0}]".format(
                self._render_annotation(args[0] if args else Any)
            )
        if origin is frozenset:
            return "FrozenSet[{0}]".format(
                self._render_annotation(args[0] if args else Any)
            )
        if origin is not None:
            origin_name = getattr(origin, "__name__", None)
            if origin_name == "Sequence":
                return "Sequence[{0}]".format(
                    self._render_annotation(args[0] if args else Any)
                )
            if origin_name == "Mapping":
                key_annotation = args[0] if len(args) > 0 else Any
                value_annotation = args[1] if len(args) > 1 else Any
                return "Mapping[{0}, {1}]".format(
                    self._render_annotation(key_annotation),
                    self._render_annotation(value_annotation),
                )
            if origin_name == "Iterable":
                return "Iterable[{0}]".format(
                    self._render_annotation(args[0] if args else Any)
                )
            if origin_name == "Iterator":
                return "Iterator[{0}]".format(
                    self._render_annotation(args[0] if args else Any)
                )
            if origin_name == "Callable":
                if len(args) != 2:
                    return "Callable[..., Any]"
                callable_args = args[0]
                callable_return = args[1]
                if callable_args is Ellipsis:
                    callable_arguments_text = "..."
                else:
                    callable_arguments_text = "[{0}]".format(
                        ", ".join(
                            self._render_annotation(item)
                            for item in callable_args
                        )
                    )
                return "Callable[{0}, {1}]".format(
                    callable_arguments_text,
                    self._render_annotation(callable_return),
                )

        module_name = getattr(annotation, "__module__", "")
        annotation_name = getattr(annotation, "__name__", None)
        if annotation_name is None:
            return "Any"
        if not isinstance(annotation_name, str):
            return "Any"
        if module_name == "builtins":
            return annotation_name
        if annotation_name in self._TYPING_FAMILY_NAMES:
            return annotation_name
        return "\"{0}\"".format(annotation_name)

    def _annotation_from_value(self, value: object) -> str:
        """
        Infer one attribute annotation from a concrete value.

        Args:
            value:
                Concrete attribute value.

        Returns:
            str: Rendered annotation text.
        """
        if value is None:
            return "Any"
        return self._render_annotation(type(value))

    def _get_property_annotation(self, property_object: property) -> object:
        """
        Return the most useful annotation for one property.

        Args:
            property_object:
                Property descriptor to inspect.

        Returns:
            object: Reflected return annotation or `Any`.
        """
        if property_object.fget is None:
            return Any
        return inspect.signature(property_object.fget).return_annotation

    def _unwrap_method_candidate(
            self,
            value: object,
    ) -> Optional[Callable[..., Any]]:
        """
        Return the underlying function for one method-like class member.

        Args:
            value:
                Raw class member value from `__dict__`.

        Returns:
            Optional[Callable[..., Any]]:
                Underlying function object when the member is a mirrorable
                method, otherwise None.
        """
        if isinstance(value, staticmethod):
            return value.__func__
        if isinstance(value, classmethod):
            return value.__func__
        if inspect.isfunction(value):
            return value
        return None

    def _build_docstring_lines(
            self,
            docstring_text: Optional[str],
            *,
            fallback: str,
            indent: str,
    ) -> List[str]:
        """
        Build one indented triple-quoted docstring block.

        Args:
            docstring_text:
                Source docstring text to mirror when present.
            fallback:
                Fallback docstring text when the source has no docstring.
            indent:
                Leading indentation for each generated line.

        Returns:
            List[str]: Generated docstring lines.
        """
        normalized_text = docstring_text if docstring_text else fallback
        normalized_text = normalized_text.replace('"""', '\\"""').strip()
        lines = normalized_text.splitlines() if normalized_text else [fallback]
        output_lines = [indent + '"""']
        for line in lines:
            output_lines.append(indent + line.rstrip())
        output_lines.append(indent + '"""')
        return output_lines

    def _load_source_class(
            self,
            source_file_path: Path,
            class_name: str,
    ) -> ast.ClassDef:
        """
        Parse one source file and return the requested top-level class.

        Args:
            source_file_path:
                Source file to parse.
            class_name:
                Exact class name to locate.

        Returns:
            ast.ClassDef: Matching top-level class node.

        Raises:
            ValueError:
                If the file does not exist, cannot be parsed, or does not
                define the requested class.
        """
        if not source_file_path.exists():
            raise ValueError(
                "Source file '{0}' does not exist.".format(source_file_path)
            )
        try:
            source_tree = ast.parse(
                source_file_path.read_text(encoding="utf-8"),
                filename=str(source_file_path),
            )
        except SyntaxError as error:
            raise ValueError(
                "Source file '{0}' could not be parsed.".format(source_file_path)
            ) from error
        for node in source_tree.body:
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                return node
        raise ValueError(
            "Class '{0}' was not found in '{1}'.".format(
                class_name,
                source_file_path,
            )
        )

    def _load_joined_source_models(
            self,
            targets: Sequence[Tuple[Union[str, Path], str]],
    ) -> List[Tuple[Path, str, ast.ClassDef]]:
        """
        Resolve multiple `(file, class)` targets into parsed class nodes.

        Args:
            targets:
                `(source_file_path, class_name)` tuples.

        Returns:
            List[Tuple[Path, str, ast.ClassDef]]: Parsed target models.
        """
        models: List[Tuple[Path, str, ast.ClassDef]] = []
        for source_file_path, class_name in targets:
            source_path = Path(source_file_path)
            class_node = self._load_source_class(source_path, class_name)
            models.append((source_path, class_name, class_node))
        return models

    def _build_protocol_attributes_from_source(
            self,
            class_node: ast.ClassDef,
            class_name: str,
            protocol_name: str,
    ) -> List[ast.AnnAssign]:
        """
        Build public protocol attributes from one source class.

        Args:
            class_node:
                Source class node.
            class_name:
                Source class name.
            protocol_name:
                Output protocol name for self-reference rewriting.

        Returns:
            List[ast.AnnAssign]: Protocol attribute nodes.
        """
        attribute_nodes: List[ast.AnnAssign] = []
        for attribute_name, annotation_text in self._collect_public_source_attributes(
                class_node,
                class_name,
                protocol_name,
        ):
            attribute_source = "{0}: {1}".format(attribute_name, annotation_text)
            parsed_attribute = ast.parse(attribute_source).body[0]
            if not isinstance(parsed_attribute, ast.AnnAssign):
                raise ValueError(
                    "ProtocolCrafter generated a non-attribute node for '{0}'.".format(
                        attribute_name,
                    )
                )
            attribute_nodes.append(parsed_attribute)
        return attribute_nodes

    def _build_protocol_methods_from_source(
            self,
            class_node: ast.ClassDef,
            class_name: str,
            protocol_name: str,
    ) -> List[Union[ast.FunctionDef, ast.AsyncFunctionDef]]:
        """
        Build public protocol methods from one source class.

        Args:
            class_node:
                Source class node.
            class_name:
                Source class name.
            protocol_name:
                Output protocol name for self-reference rewriting.

        Returns:
            List[Union[ast.FunctionDef, ast.AsyncFunctionDef]]:
                Protocol method nodes.
        """
        method_nodes: List[Union[ast.FunctionDef, ast.AsyncFunctionDef]] = []
        for function_node in self._collect_public_source_methods(class_node):
            method_nodes.append(
                self._build_protocol_method_from_source(
                    function_node,
                    class_name,
                    protocol_name,
                )
            )
        return method_nodes

    def _collect_public_source_attributes(
            self,
            class_node: ast.ClassDef,
            class_name: str,
            self_protocol_name: str,
    ) -> List[Tuple[str, str]]:
        """
        Collect public attribute declarations from one source class.

        Args:
            class_node:
                Source class node.
            class_name:
                Source class name.
            self_protocol_name:
                Replacement name for self-return/self-attribute references.

        Returns:
            List[Tuple[str, str]]: `(attribute_name, annotation_text)` pairs.
        """
        attribute_items: List[Tuple[str, str]] = []
        for statement in class_node.body:
            if isinstance(statement, ast.AnnAssign) and isinstance(
                    statement.target,
                    ast.Name,
            ):
                attribute_name = statement.target.id
                if not self._is_public_protocol_attribute_name(attribute_name):
                    continue
                annotation_text = self._render_source_annotation_text(
                    statement.annotation,
                    class_name,
                    self_protocol_name,
                )
                attribute_items.append((attribute_name, annotation_text))
                continue
            if isinstance(statement, ast.Assign) and len(statement.targets) == 1:
                target = statement.targets[0]
                if not isinstance(target, ast.Name):
                    continue
                attribute_name = target.id
                if not self._is_public_protocol_attribute_name(attribute_name):
                    continue
                annotation_text = self._infer_source_attribute_annotation_text(
                    statement.value
                )
                attribute_items.append((attribute_name, annotation_text))
        public_instance_attributes = self._collect_public_init_instance_attributes(
            class_node,
            class_name,
            self_protocol_name,
        )
        existing_attribute_names = {item[0] for item in attribute_items}
        for attribute_name, annotation_text in public_instance_attributes:
            if attribute_name in existing_attribute_names:
                continue
            attribute_items.append((attribute_name, annotation_text))
        return attribute_items

    def _collect_public_source_methods(
            self,
            class_node: ast.ClassDef,
    ) -> List[Union[ast.FunctionDef, ast.AsyncFunctionDef]]:
        """
        Collect public source methods suitable for protocol generation.

        Args:
            class_node:
                Source class node.

        Returns:
            List[Union[ast.FunctionDef, ast.AsyncFunctionDef]]:
                Public method definitions in source order.
        """
        method_nodes: List[Union[ast.FunctionDef, ast.AsyncFunctionDef]] = []
        for statement in class_node.body:
            if not isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if self._should_skip_source_method(statement):
                continue
            method_nodes.append(statement)
        return method_nodes

    def _build_joined_protocol_attributes(
            self,
            source_models: Sequence[Tuple[Path, str, ast.ClassDef]],
            protocol_name: str,
    ) -> List[ast.AnnAssign]:
        """
        Build the shared attribute surface across multiple classes.

        Args:
            source_models:
                Parsed target class models.
            protocol_name:
                Output protocol name for self-reference rewriting.

        Returns:
            List[ast.AnnAssign]: Shared protocol attribute nodes.
        """
        if not source_models:
            return []
        placeholder_name = "__SELF_PROTOCOL__"
        attribute_maps: List[Dict[str, str]] = []
        for _, class_name, class_node in source_models:
            attribute_maps.append(
                dict(
                    self._collect_public_source_attributes(
                        class_node,
                        class_name,
                        placeholder_name,
                    )
                )
            )
        common_names = set(attribute_maps[0].keys())
        for attribute_map in attribute_maps[1:]:
            common_names &= set(attribute_map.keys())
        attribute_nodes: List[ast.AnnAssign] = []
        for attribute_name in sorted(common_names):
            annotation_text = attribute_maps[0][attribute_name]
            if all(
                    attribute_map[attribute_name] == annotation_text
                    for attribute_map in attribute_maps[1:]
            ):
                final_annotation_text = annotation_text.replace(
                    placeholder_name,
                    protocol_name,
                )
                attribute_source = "{0}: {1}".format(
                    attribute_name,
                    final_annotation_text,
                )
                parsed_attribute = ast.parse(attribute_source).body[0]
                if not isinstance(parsed_attribute, ast.AnnAssign):
                    raise ValueError(
                        "ProtocolCrafter generated a non-attribute node for shared attribute '{0}'.".format(
                            attribute_name,
                        )
                    )
                attribute_nodes.append(parsed_attribute)
        return attribute_nodes

    def _build_joined_protocol_methods(
            self,
            source_models: Sequence[Tuple[Path, str, ast.ClassDef]],
            protocol_name: str,
    ) -> List[Union[ast.FunctionDef, ast.AsyncFunctionDef]]:
        """
        Build the shared method surface across multiple classes.

        Args:
            source_models:
                Parsed target class models.
            protocol_name:
                Output protocol name for self-reference rewriting.

        Returns:
            List[Union[ast.FunctionDef, ast.AsyncFunctionDef]]:
                Shared protocol method nodes.
        """
        if not source_models:
            return []
        placeholder_name = "__SELF_PROTOCOL__"
        method_maps: List[
            Dict[str, Tuple[str, str, Optional[str], Union[ast.FunctionDef, ast.AsyncFunctionDef]]]
        ] = []
        for _, class_name, class_node in source_models:
            method_map: Dict[
                str,
                Tuple[str, str, Optional[str], Union[ast.FunctionDef, ast.AsyncFunctionDef]]
            ] = {}
            for function_node in self._collect_public_source_methods(class_node):
                method_map[function_node.name] = (
                    self._build_source_method_key(
                        function_node,
                        class_name,
                        placeholder_name,
                    ),
                    class_name,
                    ast.get_docstring(function_node),
                    function_node,
                )
            method_maps.append(method_map)
        common_names = set(method_maps[0].keys())
        for method_map in method_maps[1:]:
            common_names &= set(method_map.keys())
        method_nodes: List[Union[ast.FunctionDef, ast.AsyncFunctionDef]] = []
        for method_name in sorted(common_names):
            first_key, first_class_name, first_docstring, first_function_node = method_maps[0][method_name]
            if all(
                    method_map[method_name][0] == first_key
                    for method_map in method_maps[1:]
            ):
                override_docstring = first_docstring
                normalized_docstrings = {
                    self._normalize_docstring_text(method_map[method_name][2] or "")
                    for method_map in method_maps
                }
                if len(normalized_docstrings) > 1:
                    override_docstring = "Shared protocol member for `{0}`.".format(
                        method_name
                    )
                method_nodes.append(
                    self._build_protocol_method_from_source(
                        first_function_node,
                        first_class_name,
                        protocol_name,
                        override_docstring=override_docstring,
                    )
                )
        return method_nodes

    def _build_protocol_method_from_source(
            self,
            function_node: FunctionNode,
            class_name: str,
            protocol_name: str,
            *,
            override_docstring: Optional[str] = None,
    ) -> FunctionNode:
        """
        Build one protocol method node from one source function node.

        Args:
            function_node:
                Source function node.
            class_name:
                Source class name.
            protocol_name:
                Output protocol name for self-reference rewriting.
            override_docstring:
                Optional explicit docstring text for the generated method.

        Returns:
            Union[ast.FunctionDef, ast.AsyncFunctionDef]:
                Generated protocol method node.
        """
        prefix = "async def" if isinstance(function_node, ast.AsyncFunctionDef) else "def"
        signature_text = self._render_source_function_signature_text(
            function_node,
            class_name,
            protocol_name,
        )
        method_lines: List[str] = []
        method_lines.extend(self._build_supported_decorator_lines(function_node))
        method_lines.append(
            "{0} {1}{2}:".format(
                prefix,
                function_node.name,
                signature_text,
            )
        )
        method_lines.extend(
            self._build_docstring_lines(
                override_docstring if override_docstring is not None else ast.get_docstring(function_node),
                fallback="Protocol mirror for `{0}`.".format(function_node.name),
                indent="    ",
            )
        )
        method_lines.append("    ...")
        parsed_method = ast.parse("\n".join(method_lines)).body[0]
        if not isinstance(parsed_method, (ast.FunctionDef, ast.AsyncFunctionDef)):
            raise ValueError(
                "ProtocolCrafter generated a non-function node for '{0}'.".format(
                    function_node.name,
                )
            )
        return parsed_method

    def _render_source_function_signature_text(
            self,
            function_node: FunctionNode,
            class_name: str,
            self_protocol_name: str,
    ) -> str:
        """
        Render one source function signature for protocol output.

        Args:
            function_node:
                Source function node.
            class_name:
                Source class name.
            self_protocol_name:
                Replacement name for self-return references.

        Returns:
            str: Rendered signature text.
        """
        arguments = function_node.args
        rendered_parameters: List[str] = []
        positional_arguments = list(arguments.posonlyargs) + list(arguments.args)
        default_offset = len(positional_arguments) - len(arguments.defaults)
        for index, parameter in enumerate(arguments.posonlyargs):
            default_node = None
            if index >= default_offset:
                default_node = arguments.defaults[index - default_offset]
            rendered_parameters.append(
                self._render_source_parameter_text(
                    parameter,
                    default_node,
                    class_name,
                    self_protocol_name,
                )
            )
        if arguments.posonlyargs:
            rendered_parameters.append("/")
        for index, parameter in enumerate(arguments.args):
            absolute_index = len(arguments.posonlyargs) + index
            default_node = None
            if absolute_index >= default_offset:
                default_node = arguments.defaults[absolute_index - default_offset]
            rendered_parameters.append(
                self._render_source_parameter_text(
                    parameter,
                    default_node,
                    class_name,
                    self_protocol_name,
                )
            )
        if arguments.vararg is not None:
            rendered_parameters.append(
                self._render_source_parameter_text(
                    arguments.vararg,
                    None,
                    class_name,
                    self_protocol_name,
                    prefix="*",
                )
            )
        elif arguments.kwonlyargs:
            rendered_parameters.append("*")
        for index, parameter in enumerate(arguments.kwonlyargs):
            rendered_parameters.append(
                self._render_source_parameter_text(
                    parameter,
                    arguments.kw_defaults[index],
                    class_name,
                    self_protocol_name,
                )
            )
        if arguments.kwarg is not None:
            rendered_parameters.append(
                self._render_source_parameter_text(
                    arguments.kwarg,
                    None,
                    class_name,
                    self_protocol_name,
                    prefix="**",
                )
            )
        return_annotation = "Any"
        if function_node.returns is not None:
            return_annotation = self._render_source_annotation_text(
                function_node.returns,
                class_name,
                self_protocol_name,
            )
        return "({0}) -> {1}".format(
            ", ".join(rendered_parameters),
            return_annotation,
        )

    def _render_source_parameter_text(
            self,
            parameter: ast.arg,
            default_node: Optional[ast.expr],
            class_name: str,
            self_protocol_name: str,
            *,
            prefix: str = "",
    ) -> str:
        """
        Render one source parameter for protocol output.

        Args:
            parameter:
                Source parameter node.
            default_node:
                Optional default-value node.
            class_name:
                Source class name.
            self_protocol_name:
                Replacement name for self-return references.
            prefix:
                Parameter prefix such as `*` or `**`.

        Returns:
            str: Rendered parameter text.
        """
        parameter_text = "{0}{1}".format(prefix, parameter.arg)
        if parameter.annotation is not None:
            parameter_text += ": {0}".format(
                self._render_source_annotation_text(
                    parameter.annotation,
                    class_name,
                    self_protocol_name,
                )
            )
        if default_node is not None:
            parameter_text += " = {0}".format(
                self._render_source_default_text(default_node)
            )
        return parameter_text

    def _render_source_default_text(self, default_node: ast.expr) -> str:
        """
        Render one source default-value node into safe protocol text.

        Args:
            default_node:
                Source default-value node.

        Returns:
            str: Rendered default value text.
        """
        if isinstance(default_node, ast.Constant):
            if default_node.value is None:
                return "None"
            if isinstance(default_node.value, (bool, int, float, str, bytes)):
                return repr(default_node.value)
            if default_node.value is Ellipsis:
                return "..."
        if isinstance(default_node, ast.Tuple):
            rendered_items: List[str] = []
            for item in default_node.elts:
                if not isinstance(item, ast.Constant):
                    return "..."
                if item.value is Ellipsis:
                    rendered_items.append("...")
                    continue
                if not isinstance(item.value, (bool, int, float, str, bytes, type(None))):
                    return "..."
                rendered_items.append(repr(item.value))
            return "({0})".format(", ".join(rendered_items))
        return "..."

    def _collect_public_init_instance_attributes(
            self,
            class_node: ast.ClassDef,
            class_name: str,
            self_protocol_name: str,
    ) -> List[Tuple[str, str]]:
        """
        Collect public instance attributes assigned in `__init__`.

        Args:
            class_node:
                Source class node.
            class_name:
                Source class name.
            self_protocol_name:
                Replacement name for self-return references.

        Returns:
            List[Tuple[str, str]]: `(attribute_name, annotation_text)` pairs.
        """
        init_node = self._find_source_init_method(class_node)
        if init_node is None:
            return []
        parameter_annotations = self._build_init_parameter_annotation_map(
            init_node,
            class_name,
            self_protocol_name,
        )
        attribute_items: List[Tuple[str, str]] = []
        for statement in init_node.body:
            if isinstance(statement, ast.AnnAssign):
                public_target = self._get_public_self_attribute_target(statement.target)
                if public_target is None:
                    continue
                attribute_items.append(
                    (
                        public_target.attr,
                        self._render_source_annotation_text(
                            statement.annotation,
                            class_name,
                            self_protocol_name,
                        ),
                    )
                )
                continue
            if isinstance(statement, ast.Assign) and len(statement.targets) == 1:
                public_target = self._get_public_self_attribute_target(statement.targets[0])
                if public_target is None:
                    continue
                attribute_items.append(
                    (
                        public_target.attr,
                        self._infer_init_assignment_annotation_text(
                            statement.value,
                            parameter_annotations,
                        ),
                    )
                )
        return attribute_items

    def _find_source_init_method(
            self,
            class_node: ast.ClassDef,
    ) -> Optional[ast.FunctionDef]:
        """
        Return the source `__init__` method when present.

        Args:
            class_node:
                Source class node.

        Returns:
            Optional[ast.FunctionDef]: Matching `__init__` node or None.
        """
        for statement in class_node.body:
            if isinstance(statement, ast.FunctionDef) and statement.name == "__init__":
                return statement
        return None

    def _build_init_parameter_annotation_map(
            self,
            init_node: ast.FunctionDef,
            class_name: str,
            self_protocol_name: str,
    ) -> Dict[str, str]:
        """
        Build a name-to-annotation map for `__init__` parameters.

        Args:
            init_node:
                `__init__` function node.
            class_name:
                Source class name.
            self_protocol_name:
                Replacement name for self-return references.

        Returns:
            Dict[str, str]: Parameter annotation map.
        """
        annotation_map: Dict[str, str] = {}
        positional_arguments = list(init_node.args.posonlyargs) + list(init_node.args.args)
        for parameter in positional_arguments + list(init_node.args.kwonlyargs):
            if parameter.arg == "self":
                continue
            if parameter.annotation is None:
                continue
            annotation_map[parameter.arg] = self._render_source_annotation_text(
                parameter.annotation,
                class_name,
                self_protocol_name,
            )
        if init_node.args.vararg is not None and init_node.args.vararg.annotation is not None:
            annotation_map[init_node.args.vararg.arg] = self._render_source_annotation_text(
                init_node.args.vararg.annotation,
                class_name,
                self_protocol_name,
            )
        if init_node.args.kwarg is not None and init_node.args.kwarg.annotation is not None:
            annotation_map[init_node.args.kwarg.arg] = self._render_source_annotation_text(
                init_node.args.kwarg.annotation,
                class_name,
                self_protocol_name,
            )
        return annotation_map

    def _infer_init_assignment_annotation_text(
            self,
            value_node: ast.expr,
            parameter_annotations: Dict[str, str],
    ) -> str:
        """
        Infer an instance-attribute annotation from one `__init__` assignment.

        Args:
            value_node:
                Assigned value node.
            parameter_annotations:
                Known `__init__` parameter annotations keyed by name.

        Returns:
            str: Inferred annotation text.
        """
        if isinstance(value_node, ast.Name) and value_node.id in parameter_annotations:
            return parameter_annotations[value_node.id]
        return self._infer_source_attribute_annotation_text(value_node)

    @staticmethod
    def _get_public_self_attribute_target(target: ast.expr) -> Optional[ast.Attribute]:
        """
        Return one public `self.<name>` assignment target when present.

        Args:
            target:
                Candidate assignment target.

        Returns:
            Optional[ast.Attribute]:
                The narrowed attribute target when it is a public self
                attribute, otherwise `None`.
        """
        if not isinstance(target, ast.Attribute):
            return None
        if not isinstance(target.value, ast.Name):
            return None
        if target.value.id != "self":
            return None
        if target.attr.startswith("_"):
            return None
        return target

    def _render_source_annotation_text(
            self,
            annotation_node: Optional[ast.expr],
            class_name: str,
            self_protocol_name: str,
    ) -> str:
        """
        Render one source annotation node into repo-style protocol text.

        Args:
            annotation_node:
                Source annotation node.
            class_name:
                Source class name.
            self_protocol_name:
                Replacement name for self-return references.

        Returns:
            str: Rendered annotation text.
        """
        if annotation_node is None:
            return "Any"
        if isinstance(annotation_node, ast.Constant):
            if annotation_node.value is None:
                return "None"
            if isinstance(annotation_node.value, str):
                try:
                    parsed_annotation = ast.parse(
                        annotation_node.value,
                        mode="eval",
                    ).body
                except SyntaxError:
                    return repr(annotation_node.value)
                return self._render_source_annotation_text(
                    parsed_annotation,
                    class_name,
                    self_protocol_name,
                )
        if isinstance(annotation_node, ast.Name):
            return self._render_source_name_annotation(
                annotation_node.id,
                class_name,
                self_protocol_name,
            )
        if isinstance(annotation_node, ast.Attribute):
            if (
                    isinstance(annotation_node.value, ast.Name)
                    and annotation_node.value.id == "typing"
                    and annotation_node.attr in self._TYPING_FAMILY_NAMES
            ):
                return annotation_node.attr
            return repr(ast.unparse(annotation_node))
        if isinstance(annotation_node, ast.Subscript):
            base_text = self._render_source_subscript_base_text(
                annotation_node.value,
                class_name,
                self_protocol_name,
            )
            slice_nodes = self._expand_subscript_slice(annotation_node.slice)
            rendered_arguments = [
                self._render_source_annotation_text(
                    item,
                    class_name,
                    self_protocol_name,
                )
                for item in slice_nodes
            ]
            if base_text.startswith(("'", '"')) and base_text.endswith(("'", '"')):
                unquoted_base = ast.literal_eval(base_text)
                return repr(
                    "{0}[{1}]".format(
                        unquoted_base,
                        ", ".join(rendered_arguments),
                    )
                )
            return "{0}[{1}]".format(
                base_text,
                ", ".join(rendered_arguments),
            )
        if isinstance(annotation_node, ast.BinOp) and isinstance(
                annotation_node.op,
                ast.BitOr,
        ):
            union_members = self._flatten_pep604_union(annotation_node)
            rendered_members = [
                self._render_source_annotation_text(
                    item,
                    class_name,
                    self_protocol_name,
                )
                for item in union_members
            ]
            non_none_members = [
                item for item in rendered_members if item != "None"
            ]
            if len(non_none_members) == 1 and len(rendered_members) == 2:
                return "Optional[{0}]".format(non_none_members[0])
            return "Union[{0}]".format(", ".join(rendered_members))
        if isinstance(annotation_node, ast.Tuple):
            return "Tuple[{0}]".format(
                ", ".join(
                    self._render_source_annotation_text(
                        item,
                        class_name,
                        self_protocol_name,
                    )
                    for item in annotation_node.elts
                )
            )
        return repr(ast.unparse(annotation_node))

    def _render_source_name_annotation(
            self,
            annotation_name: str,
            class_name: str,
            self_protocol_name: str,
    ) -> str:
        """
        Render one source annotation name into repo-style protocol text.

        Args:
            annotation_name:
                Raw annotation name.
            class_name:
                Source class name.
            self_protocol_name:
                Replacement name for self-return references.

        Returns:
            str: Rendered annotation text.
        """
        if annotation_name == class_name:
            return repr(self_protocol_name)
        if annotation_name in self._TYPING_FAMILY_NAMES:
            return annotation_name
        if annotation_name in {
            "Any",
            "None",
            "bool",
            "bytes",
            "dict",
            "float",
            "frozenset",
            "int",
            "list",
            "object",
            "set",
            "str",
            "tuple",
            "type",
        }:
            return annotation_name
        return repr(annotation_name)

    def _render_source_subscript_base_text(
            self,
            base_node: ast.expr,
            class_name: str,
            self_protocol_name: str,
    ) -> str:
        """
        Render one subscript base node into protocol-safe text.

        Args:
            base_node:
                Subscript base expression.
            class_name:
                Source class name.
            self_protocol_name:
                Replacement name for self-return references.

        Returns:
            str: Rendered base text.
        """
        if isinstance(base_node, ast.Name):
            builtin_generic_names = {
                "dict": "Dict",
                "frozenset": "FrozenSet",
                "list": "List",
                "set": "Set",
                "tuple": "Tuple",
                "type": "Type",
            }
            if base_node.id in builtin_generic_names:
                return builtin_generic_names[base_node.id]
        return self._render_source_annotation_text(
            base_node,
            class_name,
            self_protocol_name,
        )

    def _expand_subscript_slice(
            self,
            slice_node: ast.expr,
    ) -> List[ast.expr]:
        """
        Expand one subscript slice into one or more argument nodes.

        Args:
            slice_node:
                Subscript slice node.

        Returns:
            List[ast.expr]: Normalized subscript arguments.
        """
        if isinstance(slice_node, ast.Tuple):
            return list(slice_node.elts)
        return [slice_node]

    def _flatten_pep604_union(
            self,
            annotation_node: ast.expr,
    ) -> List[ast.expr]:
        """
        Flatten one `A | B | C` annotation tree into a linear member list.

        Args:
            annotation_node:
                Annotation node that may contain nested `BitOr` unions.

        Returns:
            List[ast.expr]: Flattened union members.
        """
        if isinstance(annotation_node, ast.BinOp) and isinstance(
                annotation_node.op,
                ast.BitOr,
        ):
            return (
                self._flatten_pep604_union(annotation_node.left)
                + self._flatten_pep604_union(annotation_node.right)
            )
        return [annotation_node]

    def _build_source_method_key(
            self,
            function_node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
            class_name: str,
            self_protocol_name: str,
    ) -> str:
        """
        Build a stable comparison key for one source method.

        Args:
            function_node:
                Source function node.
            class_name:
                Source class name.
            self_protocol_name:
                Replacement name for self-return references.

        Returns:
            str: Stable signature/decorator comparison key.
        """
        signature_text = self._render_source_function_signature_text(
            function_node,
            class_name,
            self_protocol_name,
        )
        decorator_key = "|".join(
            self._extract_supported_decorator_names(function_node)
        )
        async_key = "async" if isinstance(function_node, ast.AsyncFunctionDef) else "sync"
        return "{0}|{1}|{2}".format(async_key, decorator_key, signature_text)

    def _build_protocol_module_ast(
            self,
            protocol_name: str,
            class_docstring: str,
            attribute_nodes: Sequence[ast.AnnAssign],
            method_nodes: Sequence[Union[ast.FunctionDef, ast.AsyncFunctionDef]],
    ) -> ast.Module:
        """
        Assemble one full protocol module AST.

        Args:
            protocol_name:
                Protocol class name to emit.
            class_docstring:
                Docstring for the generated protocol class.
            attribute_nodes:
                Generated attribute nodes.
            method_nodes:
                Generated method nodes.

        Returns:
            ast.Module: Fully assembled protocol module.
        """
        class_body: List[ast.stmt] = [ast.Expr(value=ast.Constant(value=class_docstring))]
        class_body.extend(attribute_nodes)
        class_body.extend(method_nodes)
        if len(class_body) == 1:
            class_body.append(ast.Expr(value=ast.Constant(value=Ellipsis)))
        class_node = ast.ClassDef(
            name=protocol_name,
            bases=[ast.Name(id="Protocol", ctx=ast.Load())],
            keywords=[],
            body=class_body,
            decorator_list=[ast.Name(id="runtime_checkable", ctx=ast.Load())],
        )
        import_names = self._collect_protocol_typing_import_names(class_node)
        module_node = ast.Module(
            body=[
                ast.ImportFrom(
                    module="typing",
                    names=[
                        ast.alias(name=name, asname=None)
                        for name in import_names
                    ],
                    level=0,
                ),
                class_node,
            ],
            type_ignores=[],
        )
        return ast.fix_missing_locations(module_node)

    def _collect_protocol_typing_import_names(
            self,
            class_node: ast.ClassDef,
    ) -> List[str]:
        """
        Collect the minimal ordered typing imports needed by one protocol class.

        Args:
            class_node:
                Generated protocol class node.

        Returns:
            List[str]: Ordered typing-import names required by the class.
        """
        used_names = {"Protocol", "runtime_checkable"}
        for node in ast.walk(class_node):
            if isinstance(node, ast.Name) and node.id in self._PROTOCOL_MODULE_IMPORT_NAMES:
                used_names.add(node.id)
        return [
            name for name in self._PROTOCOL_MODULE_IMPORT_NAMES
            if name in used_names
        ]

    def _render_protocol_module_ast(self, module_node: ast.Module) -> str:
        """
        Render one assembled protocol module AST into source text.

        Args:
            module_node:
                Protocol module AST.

        Returns:
            str: Rendered protocol module text.
        """
        lines: List[str] = []
        for index, statement in enumerate(module_node.body):
            if index > 0:
                lines.append("")
            if isinstance(statement, ast.ImportFrom):
                lines.append(self._render_protocol_import_from(statement))
                continue
            if isinstance(statement, ast.ClassDef):
                lines.extend(self._render_protocol_class(statement))
                continue
        return "\n".join(lines).rstrip() + "\n"

    def _render_protocol_import_from(self, import_node: ast.ImportFrom) -> str:
        """
        Render one `from ... import ...` node for protocol-module output.

        Args:
            import_node:
                Import-from node.

        Returns:
            str: Rendered import line.
        """
        imported_names = ", ".join(alias.name for alias in import_node.names)
        return "from {0} import {1}".format(import_node.module, imported_names)

    def _render_protocol_class(self, class_node: ast.ClassDef) -> List[str]:
        """
        Render one protocol class node into formatted source lines.

        Args:
            class_node:
                Protocol class node.

        Returns:
            List[str]: Rendered class source lines.
        """
        lines: List[str] = []
        for decorator in class_node.decorator_list:
            lines.append("@{0}".format(ast.unparse(decorator)))
        base_text = ", ".join(ast.unparse(base) for base in class_node.bases) or "object"
        lines.append("class {0}({1}):".format(class_node.name, base_text))
        body_lines = self._render_protocol_class_body(class_node.body)
        if body_lines:
            lines.extend(body_lines)
        else:
            lines.append("    ...")
        return lines

    def _render_protocol_class_body(self, body: Sequence[ast.stmt]) -> List[str]:
        """
        Render the body of one generated protocol class.

        Args:
            body:
                Protocol class body nodes.

        Returns:
            List[str]: Rendered body lines with indentation.
        """
        rendered_blocks: List[List[str]] = []
        for statement in body:
            if self._is_string_expr(statement):
                rendered_blocks.append(
                    self._format_docstring_lines(
                        self._extract_string_expr_value(statement),
                        indent="    ",
                    )
                )
                continue
            if isinstance(statement, ast.AnnAssign):
                rendered_blocks.append(
                    [self._render_protocol_attribute_line(statement, indent="    ")]
                )
                continue
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                rendered_blocks.append(
                    self._render_protocol_method_lines(statement, indent="    ")
                )
                continue
            if self._is_ellipsis_expr(statement):
                rendered_blocks.append(["    ..."])
        lines: List[str] = []
        for index, block in enumerate(rendered_blocks):
            if index > 0:
                lines.append("")
            lines.extend(block)
        return lines

    def _render_protocol_attribute_line(
            self,
            attribute_node: ast.AnnAssign,
            *,
            indent: str,
    ) -> str:
        """
        Render one protocol attribute line.

        Args:
            attribute_node:
                Protocol attribute node.
            indent:
                Leading indentation.

        Returns:
            str: Rendered attribute line.
        """
        target_text = ast.unparse(attribute_node.target)
        annotation_text = ast.unparse(attribute_node.annotation)
        return "{0}{1}: {2}".format(indent, target_text, annotation_text)

    def _render_protocol_method_lines(
            self,
            method_node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
            *,
            indent: str,
    ) -> List[str]:
        """
        Render one generated protocol method with stable formatting.

        Args:
            method_node:
                Protocol method node.
            indent:
                Leading indentation for the method block.

        Returns:
            List[str]: Rendered method lines.
        """
        lines: List[str] = []
        for decorator in method_node.decorator_list:
            lines.append("{0}@{1}".format(indent, ast.unparse(decorator)))
        prefix = "async def" if isinstance(method_node, ast.AsyncFunctionDef) else "def"
        signature_text = self._render_ast_function_signature_text(method_node)
        lines.append(
            "{0}{1} {2}{3}:".format(
                indent,
                prefix,
                method_node.name,
                signature_text,
            )
        )
        body_index = 0
        if method_node.body and self._is_string_expr(method_node.body[0]):
            lines.extend(
                self._format_docstring_lines(
                    self._extract_string_expr_value(method_node.body[0]),
                    indent=indent + "    ",
                )
            )
            body_index = 1
        if body_index >= len(method_node.body):
            lines.append(indent + "    ...")
            return lines
        for statement in method_node.body[body_index:]:
            if self._is_ellipsis_expr(statement):
                lines.append(indent + "    ...")
        if lines[-1] != indent + "    ...":
            lines.append(indent + "    ...")
        return lines

    def _render_ast_function_signature_text(
            self,
            function_node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
    ) -> str:
        """
        Render one generated function signature from its AST node.

        Args:
            function_node:
                Generated protocol method node.

        Returns:
            str: Rendered signature text.
        """
        arguments = function_node.args
        rendered_parameters: List[str] = []
        positional_arguments = list(arguments.posonlyargs) + list(arguments.args)
        default_offset = len(positional_arguments) - len(arguments.defaults)
        for index, parameter in enumerate(arguments.posonlyargs):
            default_node = None
            if index >= default_offset:
                default_node = arguments.defaults[index - default_offset]
            rendered_parameters.append(
                self._render_ast_parameter_text(parameter, default_node)
            )
        if arguments.posonlyargs:
            rendered_parameters.append("/")
        for index, parameter in enumerate(arguments.args):
            absolute_index = len(arguments.posonlyargs) + index
            default_node = None
            if absolute_index >= default_offset:
                default_node = arguments.defaults[absolute_index - default_offset]
            rendered_parameters.append(
                self._render_ast_parameter_text(parameter, default_node)
            )
        if arguments.vararg is not None:
            rendered_parameters.append(
                self._render_ast_parameter_text(arguments.vararg, None, prefix="*")
            )
        elif arguments.kwonlyargs:
            rendered_parameters.append("*")
        for index, parameter in enumerate(arguments.kwonlyargs):
            rendered_parameters.append(
                self._render_ast_parameter_text(parameter, arguments.kw_defaults[index])
            )
        if arguments.kwarg is not None:
            rendered_parameters.append(
                self._render_ast_parameter_text(arguments.kwarg, None, prefix="**")
            )
        return_annotation = "Any"
        if function_node.returns is not None:
            return_annotation = ast.unparse(function_node.returns)
        return "({0}) -> {1}".format(", ".join(rendered_parameters), return_annotation)

    def _render_ast_parameter_text(
            self,
            parameter: ast.arg,
            default_node: Optional[ast.expr],
            *,
            prefix: str = "",
    ) -> str:
        """
        Render one generated AST parameter with stable spacing.

        Args:
            parameter:
                Generated parameter node.
            default_node:
                Optional default-value node.
            prefix:
                Prefix such as `*` or `**`.

        Returns:
            str: Rendered parameter text.
        """
        parameter_text = "{0}{1}".format(prefix, parameter.arg)
        if parameter.annotation is not None:
            parameter_text += ": {0}".format(ast.unparse(parameter.annotation))
        if default_node is not None:
            parameter_text += " = {0}".format(self._render_source_default_text(default_node))
        return parameter_text

    def _format_docstring_lines(
            self,
            docstring_text: str,
            *,
            indent: str,
    ) -> List[str]:
        """
        Format one docstring block with stable indentation.

        Args:
            docstring_text:
                Raw docstring text.
            indent:
                Leading indentation for the docstring block.

        Returns:
            List[str]: Rendered docstring lines.
        """
        normalized_text = self._normalize_docstring_text(docstring_text)
        output_lines = [indent + '"""']
        for line in normalized_text.splitlines():
            output_lines.append(indent + line)
        output_lines.append(indent + '"""')
        return output_lines

    def _normalize_docstring_text(self, docstring_text: str) -> str:
        """
        Normalize one docstring for consistent output indentation.

        Args:
            docstring_text:
                Raw docstring text.

        Returns:
            str: Normalized docstring text.
        """
        normalized_text = inspect.cleandoc(docstring_text).replace('"""', '\\"""')
        if not normalized_text:
            return ""
        return normalized_text

    @staticmethod
    def _is_string_expr(statement: ast.stmt) -> bool:
        """
        Return whether one statement is a literal-string expression.

        Args:
            statement:
                Candidate statement.

        Returns:
            bool: True when the statement is a string expression.
        """
        return (
            isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Constant)
            and isinstance(statement.value.value, str)
        )

    @staticmethod
    def _extract_string_expr_value(statement: ast.stmt) -> str:
        """
        Extract the literal string from one string-expression statement.

        Args:
            statement:
                String-expression statement.

        Returns:
            str: Stored string value.
        """
        if not isinstance(statement, ast.Expr):
            raise ValueError("Expected ast.Expr when extracting a string expression.")
        if not isinstance(statement.value, ast.Constant):
            raise ValueError("Expected ast.Constant when extracting a string expression.")
        if not isinstance(statement.value.value, str):
            raise ValueError("Expected string literal when extracting a string expression.")
        return statement.value.value

    @staticmethod
    def _is_ellipsis_expr(statement: ast.stmt) -> bool:
        """
        Return whether one statement is a literal ellipsis expression.

        Args:
            statement:
                Candidate statement.

        Returns:
            bool: True when the statement is `...`.
        """
        return (
            isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Constant)
            and statement.value.value is Ellipsis
        )

    def _write_protocol_module_text(
            self,
            module_text: str,
            output_directory: Union[str, Path],
            protocol_name: str,
    ) -> Path:
        """
        Write rendered protocol-module text into a chosen directory.

        Args:
            module_text:
                Rendered protocol module text.
            output_directory:
                Directory that should receive the generated file.
            protocol_name:
                Protocol class name used to derive the filename.

        Returns:
            Path: Written file path.
        """
        output_directory_path = Path(output_directory)
        output_directory_path.mkdir(parents=True, exist_ok=True)
        output_path = output_directory_path / self._default_protocol_file_name(
            protocol_name
        )
        output_path.write_text(module_text, encoding="utf-8")
        return output_path

    def _default_protocol_file_name(self, protocol_name: str) -> str:
        """
        Build the default output filename for one protocol name.

        Args:
            protocol_name:
                Protocol class name.

        Returns:
            str: Default lowercase interface filename.
        """
        return "{0}.py".format(protocol_name.lower())

    def _extract_supported_decorator_names(
            self,
            function_node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
    ) -> List[str]:
        """
        Return supported decorator names for protocol method generation.

        Args:
            function_node:
                Source function node.

        Returns:
            List[str]: Supported decorator names in source order.
        """
        decorator_names: List[str] = []
        for decorator in function_node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id in {
                "property",
                "classmethod",
                "staticmethod",
            }:
                decorator_names.append(decorator.id)
                continue
            if isinstance(decorator, ast.Attribute) and decorator.attr == "getter":
                decorator_names.append("property")
        return decorator_names

    def _build_supported_decorator_lines(
            self,
            function_node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
    ) -> List[str]:
        """
        Render supported decorators into source lines for one protocol method.

        Args:
            function_node:
                Source function node.

        Returns:
            List[str]: Decorator source lines.
        """
        return [
            "@{0}".format(decorator_name)
            for decorator_name in self._extract_supported_decorator_names(function_node)
        ]

    def _should_skip_source_method(
            self,
            function_node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
    ) -> bool:
        """
        Return whether one source method should be skipped for protocol output.

        Args:
            function_node:
                Source function node.

        Returns:
            bool: True when the method should be skipped.
        """
        if not self._is_public_protocol_method_name(function_node.name):
            return True
        for decorator in function_node.decorator_list:
            if isinstance(decorator, ast.Attribute) and decorator.attr in {
                "setter",
                "deleter",
            }:
                return True
        return False

    def _infer_source_attribute_annotation_text(
            self,
            value_node: ast.expr,
    ) -> str:
        """
        Infer one attribute annotation from a simple source value node.

        Args:
            value_node:
                Source value node.

        Returns:
            str: Inferred annotation text.
        """
        if isinstance(value_node, ast.Constant):
            if value_node.value is None:
                return "Any"
            if isinstance(value_node.value, bool):
                return "bool"
            if isinstance(value_node.value, int):
                return "int"
            if isinstance(value_node.value, float):
                return "float"
            if isinstance(value_node.value, str):
                return "str"
            if isinstance(value_node.value, bytes):
                return "bytes"
        if isinstance(value_node, ast.List):
            return "List[Any]"
        if isinstance(value_node, ast.Dict):
            return "Dict[Any, Any]"
        if isinstance(value_node, ast.Set):
            return "Set[Any]"
        if isinstance(value_node, ast.Tuple):
            return "Tuple[Any, ...]"
        return "Any"

    @staticmethod
    def _is_public_protocol_attribute_name(name: str) -> bool:
        """
        Return whether one attribute name belongs in generated protocols.

        Args:
            name:
                Candidate attribute name.

        Returns:
            bool: True when the attribute should be emitted.
        """
        return not name.startswith("_")

    @staticmethod
    def _is_public_protocol_method_name(name: str) -> bool:
        """
        Return whether one method name belongs in generated protocols.

        Args:
            name:
                Candidate method name.

        Returns:
            bool: True when the method should be emitted.
        """
        return name == "cleanup" or not name.startswith("_")

    def _extract_protocol_name(self, protocol_code: str) -> str:
        """
        Extract the protocol class name from one generated code block.

        Args:
            protocol_code:
                Generated protocol code block.

        Returns:
            str: Extracted protocol class name.

        Raises:
            ValueError:
                If the class name cannot be found.
        """
        match = re.search(
            r"^class\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(",
            protocol_code,
            flags=re.MULTILINE,
        )
        if match is None:
            raise ValueError("Could not determine protocol name from protocol_code.")
        return match.group(1)

    def _contains_protocol(self, interface_file_text: str, protocol_name: str) -> bool:
        """
        Return whether the target interface file already contains the protocol.

        Args:
            interface_file_text:
                Existing interface file contents.
            protocol_name:
                Protocol class name to search for.

        Returns:
            bool: True when the protocol already exists in the file.
        """
        return bool(
            re.search(
                r"^class\s+{0}\s*\(".format(re.escape(protocol_name)),
                interface_file_text,
                flags=re.MULTILINE,
            )
        )

    def _remove_protocol_block(
            self,
            interface_file_text: str,
            protocol_name: str,
    ) -> str:
        """
        Remove one protocol block from interface-file text.

        Args:
            interface_file_text:
                Existing interface file contents.
            protocol_name:
                Exact protocol class name to remove.

        Returns:
            str: Updated interface file text.

        Raises:
            ValueError:
                If the protocol block cannot be found.
        """
        lines = interface_file_text.splitlines(keepends=True)
        class_line_index = None
        for index, line in enumerate(lines):
            stripped_line = line.lstrip()
            if stripped_line.startswith(
                "class {0}(".format(protocol_name)
            ) or stripped_line.startswith(
                "class {0}:".format(protocol_name)
            ):
                class_line_index = index
                break
        if class_line_index is None:
            raise ValueError(
                "Protocol '{0}' was not found in the interface file.".format(
                    protocol_name
                )
            )

        start_index = class_line_index
        while start_index > 0:
            previous_line = lines[start_index - 1].strip()
            if previous_line.startswith("@"):
                start_index -= 1
                continue
            break

        end_index = class_line_index + 1
        while end_index < len(lines):
            stripped_line = lines[end_index].lstrip()
            if (
                    lines[end_index].startswith("class ")
                    or lines[end_index].startswith("@runtime_checkable")
            ):
                break
            end_index += 1

        updated_lines = lines[:start_index] + lines[end_index:]
        return self._normalize_blank_lines("".join(updated_lines))

    def _normalize_blank_lines(self, text: str) -> str:
        """
        Normalize repeated blank lines in generated or updated text.

        Args:
            text:
                Candidate text.

        Returns:
            str: Text with repeated blank runs collapsed to at most two blank
            lines and one trailing newline.
        """
        normalized_text = re.sub(r"\n{4,}", "\n\n\n", text.rstrip() + "\n")
        return normalized_text

    @staticmethod
    def _is_ignored_member_name(name: str) -> bool:
        """
        Return whether one attribute-style member name should be ignored.

        Args:
            name:
                Candidate attribute name.

        Returns:
            bool: True when the name is a dunder member.
        """
        return name.startswith("__") and name.endswith("__")

    @staticmethod
    def _is_ignored_method_name(name: str) -> bool:
        """
        Return whether one method-style member name should be ignored.

        Args:
            name:
                Candidate method name.

        Returns:
            bool: True when the name is a dunder member or `cleanup`.
        """
        if name == "cleanup":
            return False
        return name.startswith("__") and name.endswith("__")
