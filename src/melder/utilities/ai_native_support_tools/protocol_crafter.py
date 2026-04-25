import inspect
import re
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, get_args, get_origin

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class ProtocolCrafter(Cleanable):
    """
    Purpose:
        Generate protocol code from a target class or object and maintain
        protocol blocks inside interface files.

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

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
    ]
    _TYPING_FAMILY_NAMES = {
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
    }

    def __init__(self) -> None:
        """
        Initialize one protocol crafter utility.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        """
        Idempotently clear the protocol crafter state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._id = None
        self._lock = None

    @property
    def id(self) -> str:
        """
        Return the stable identifier for this protocol crafter instance.

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
            function_object: object,
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

    def _render_signature(self, function_object: object) -> str:
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

    def _unwrap_method_candidate(self, value: object) -> Optional[object]:
        """
        Return the underlying function for one method-like class member.

        Args:
            value:
                Raw class member value from `__dict__`.

        Returns:
            Optional[object]: Underlying function object when the member is a
            mirrorable method, otherwise None.
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
