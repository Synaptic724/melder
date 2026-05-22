"""
Shared AST-backed class-surface describer for agent-facing object introspection.
"""

import ast
import inspect
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TypedDict, Union, ClassVar



FunctionNode = Union[ast.FunctionDef, ast.AsyncFunctionDef]


class InheritedAgentPurposeDescription(TypedDict):
    """
    Typed inherited-purpose payload for one parent class in the MRO.
    """

    class_name: str
    agent_purpose: str


class ClassMemberDescription(TypedDict):
    """
    Typed method/property payload emitted from one AST-described class member.
    """

    method_name: str
    signature: str
    docstring: str
    summary: str
    decorators: Tuple[str, ...]
    line_number: int
    end_line: int
    is_async: bool
    call_style: str


class ClassSurfaceDescription(TypedDict):
    """
    Typed top-level AST class-surface payload returned by the describer.
    """

    class_name: str
    module: str
    source_file: str
    ast_helper_access: str
    agent_purpose: str
    inherited_agent_purposes: List[InheritedAgentPurposeDescription]
    class_docstring: str
    class_summary: str
    methods: List[ClassMemberDescription]
    properties: List[ClassMemberDescription]


class ClassSurfaceAstDescriber:
    """
    Purpose:
        Provide one shared AST-backed class-surface description utility for
        Melder objects.

    Contract:
        - This class is intentionally static-method only.
        - Callers pass a runtime object and receive source-defined class
          descriptions in minified JSON or structured dict form.
        - Runtime is used only to resolve the concrete class and source file.
        - AST is the canonical source for methods, properties, signatures,
          decorators, and docstrings.
        - Descriptions include only members defined directly on the concrete
          class.
        - Private and dunder members are excluded by default.

    Lifecycle:
        This class is never instantiated. It owns no mutable runtime state and
        allocates no per-object describer instances.
    """

    _SYSTEM_DOC_OBJECT_NAMES: ClassVar[Tuple[str, ...]] = (
        "__architecture__",
        "__components__",
        "__graph_network__",
        "__graph_details__",
    )

    @staticmethod
    def describe_class_surface_ast_json(
            target_object: object,
            *,
            include_private: bool = False,
            include_dunder: bool = False,
    ) -> str:
        """
        Return a minified JSON description of one class surface.

        Args:
            target_object:
                Runtime object whose class surface should be described.
            include_private:
                Whether `_private` class members should be included.
            include_dunder:
                Whether `__dunder__` class members should be included.

        Returns:
            str: Minified JSON description of the target class surface.
        """
        access_level = ClassSurfaceAstDescriber._get_required_access_level(
            target_object
        )
        if access_level == "private":
            raise ValueError("This is a private class and cannot show any data.")
        class_surface = ClassSurfaceAstDescriber.describe_class_surface_ast(
            target_object,
            include_private=include_private,
            include_dunder=include_dunder,
        )
        return json.dumps(class_surface, separators=(",", ":"))

    @staticmethod
    def list_class_method_names_ast_json(
            target_object: object,
            *,
            include_private: bool = False,
            include_dunder: bool = False,
    ) -> str:
        """
        Return a minified JSON list of source-defined class method names.

        Args:
            target_object:
                Runtime object whose class methods should be listed.
            include_private:
                Whether `_private` methods should be included.
            include_dunder:
                Whether `__dunder__` methods should be included.

        Returns:
            str: Minified JSON containing the class name and listed method
            names.
        """
        access_level = ClassSurfaceAstDescriber._get_required_access_level(
            target_object
        )
        if access_level == "private":
            raise ValueError("This is a private class and cannot show any data.")
        class_surface = ClassSurfaceAstDescriber.describe_class_surface_ast(
            target_object,
            include_private=include_private,
            include_dunder=include_dunder,
        )
        methods = class_surface["methods"]
        return json.dumps(
            {
                "class_name": class_surface["class_name"],
                "method_names": [
                    current_method["method_name"]
                    for current_method in methods
                ],
            },
            separators=(",", ":"),
        )

    @staticmethod
    def describe_agent_onboarding_json() -> str:
        """
        Return the shared first-time onboarding hint for Melder agents.

        Returns:
            str: Minified JSON onboarding hint for Melder agents.
        """
        return json.dumps(
            {
                "first_time_hint": (
                    "If this is your first time using Melder, query the "
                    "top-level system-doc objects first for top-down understanding."
                ),
                "recommended_system_objects": (
                    ClassSurfaceAstDescriber._SYSTEM_DOC_OBJECT_NAMES
                ),
            },
            separators=(",", ":"),
        )

    @staticmethod
    def describe_agent_purpose_json(target_object: object) -> str:
        """
        Return the minified JSON agent-purpose surface for one object.

        Args:
            target_object:
                Runtime object whose agent-purpose surface should be described.

        Returns:
            str: Minified JSON agent-purpose surface.
        """
        access_level = ClassSurfaceAstDescriber._get_required_access_level(
            target_object
        )
        return json.dumps(
            {
                "class_name": type(target_object).__name__,
                "access": access_level,
                "agent_purpose": ClassSurfaceAstDescriber._get_agent_purpose(
                    target_object,
                    access_level=access_level,
                ),
                "inherited_agent_purposes": (
                    ClassSurfaceAstDescriber._describe_inherited_agent_purposes(
                        target_object
                    )
                ),
                "recommended_system_objects": (
                    ClassSurfaceAstDescriber._SYSTEM_DOC_OBJECT_NAMES
                ),
            },
            separators=(",", ":"),
        )

    @staticmethod
    def describe_class_surface_ast(
            target_object: object,
            *,
            include_private: bool = False,
            include_dunder: bool = False,
    ) -> ClassSurfaceDescription:
        """
        Build a structured class-surface description from AST.

        Args:
            target_object:
                Runtime object whose class should be described.
            include_private:
                Whether `_private` members should be included.
            include_dunder:
                Whether `__dunder__` members should be included.

        Returns:
            ClassSurfaceDescription: Structured class-surface description.
        """
        access_level = ClassSurfaceAstDescriber._get_required_access_level(
            target_object
        )
        if access_level == "private":
            raise ValueError("This is a private class and cannot show any data.")
        target_class = type(target_object)
        source_file = inspect.getsourcefile(target_class)
        if source_file is None:
            raise ValueError(
                "Class surface source file could not be resolved for '{0}'.".format(
                    target_class.__name__
                )
            )
        source_text = Path(source_file).read_text(encoding="utf-8")
        module_node = ast.parse(source_text, filename=source_file)
        class_node = ClassSurfaceAstDescriber._find_class_node(
            module_node,
            target_class.__name__,
        )
        if class_node is None:
            raise ValueError(
                "Class '{0}' was not found in source file '{1}'.".format(
                    target_class.__name__,
                    source_file,
                )
            )
        methods: List[ClassMemberDescription] = []
        properties: List[ClassMemberDescription] = []
        for current_node in class_node.body:
            if not isinstance(current_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not ClassSurfaceAstDescriber._should_include_member(
                    current_node.name,
                    include_private=include_private,
                    include_dunder=include_dunder,
            ):
                continue
            member_description = ClassSurfaceAstDescriber._describe_function_node(
                current_node
            )
            if ClassSurfaceAstDescriber._is_property_node(current_node):
                properties.append(member_description)
                continue
            methods.append(member_description)
        class_docstring = ast.get_docstring(class_node)
        return {
            "class_name": target_class.__name__,
            "module": target_class.__module__,
            "source_file": source_file,
            "ast_helper_access": access_level,
            "agent_purpose": ClassSurfaceAstDescriber._get_agent_purpose(
                target_object,
                access_level=access_level,
            ),
            "inherited_agent_purposes": (
                ClassSurfaceAstDescriber._describe_inherited_agent_purposes(
                    target_object
                )
            ),
            "class_docstring": class_docstring or "",
            "class_summary": ClassSurfaceAstDescriber._docstring_summary(
                class_docstring
            ),
            "methods": methods,
            "properties": properties,
        }

    @staticmethod
    def _find_class_node(
            module_node: ast.AST,
            class_name: str,
    ) -> Optional[ast.ClassDef]:
        """
        Return the first class node matching one class name.

        Args:
            module_node:
                Parsed module AST.
            class_name:
                Class name to locate.

        Returns:
            Optional[ast.ClassDef]: Matching class node when found.
        """
        for current_node in ast.walk(module_node):
            if isinstance(current_node, ast.ClassDef) and current_node.name == class_name:
                return current_node
        return None

    @staticmethod
    def _should_include_member(
            member_name: str,
            *,
            include_private: bool,
            include_dunder: bool,
    ) -> bool:
        """
        Return whether one class member name should be included.

        Args:
            member_name:
                Candidate class member name.
            include_private:
                Whether `_private` members should be included.
            include_dunder:
                Whether `__dunder__` members should be included.

        Returns:
            bool: True when the member should be included.
        """
        if member_name.startswith("__") and member_name.endswith("__"):
            return include_dunder
        if member_name.startswith("_"):
            return include_private
        return True

    @staticmethod
    def _describe_function_node(
            function_node: FunctionNode,
    ) -> ClassMemberDescription:
        """
        Return the AST-backed description for one method/property node.

        Args:
            function_node:
                Class function node to describe.

        Returns:
            ClassMemberDescription: Method/property description.
        """
        docstring = ast.get_docstring(function_node) or ""
        return {
            "method_name": function_node.name,
            "signature": ClassSurfaceAstDescriber._format_function_signature(
                function_node
            ),
            "docstring": docstring,
            "summary": ClassSurfaceAstDescriber._docstring_summary(docstring),
            "decorators": tuple(
                ClassSurfaceAstDescriber._format_decorator(current_decorator)
                for current_decorator in function_node.decorator_list
            ),
            "line_number": function_node.lineno,
            "end_line": getattr(
                function_node,
                "end_lineno",
                function_node.lineno,
            ),
            "is_async": isinstance(function_node, ast.AsyncFunctionDef),
            "call_style": (
                "attribute"
                if ClassSurfaceAstDescriber._is_property_node(function_node)
                else "method"
            ),
        }

    @staticmethod
    def _is_property_node(function_node: FunctionNode) -> bool:
        """
        Return whether one function node represents a property.

        Args:
            function_node:
                Class function node to inspect.

        Returns:
            bool: True when the node is decorated as a property.
        """
        decorator_names = [
            ClassSurfaceAstDescriber._format_decorator(current_decorator)
            for current_decorator in function_node.decorator_list
        ]
        return any(
            current_name == "property"
            or current_name.endswith(".setter")
            or current_name.endswith(".getter")
            for current_name in decorator_names
        )

    @staticmethod
    def _format_decorator(decorator_node: ast.AST) -> str:
        """
        Return a stable string form for one decorator node.

        Args:
            decorator_node:
                Decorator AST node.

        Returns:
            str: Stable string representation of the decorator.
        """
        return ast.unparse(decorator_node)

    @staticmethod
    def _format_function_signature(
            function_node: FunctionNode,
    ) -> str:
        """
        Return a stable source-level signature string for one method node.

        Args:
            function_node:
                Class function node to format.

        Returns:
            str: Source-level signature string with `self`/`cls` removed.
        """
        args_node = function_node.args
        positional_args = list(args_node.posonlyargs) + list(args_node.args)
        if len(positional_args) > 0 and positional_args[0].arg in {"self", "cls"}:
            positional_args = positional_args[1:]
        parts: List[str] = []
        positional_defaults = list(args_node.defaults)
        positional_default_offset = len(positional_args) - len(positional_defaults)
        for current_index, current_arg in enumerate(positional_args):
            current_default = None
            if current_index >= positional_default_offset:
                current_default = positional_defaults[
                    current_index - positional_default_offset
                ]
            parts.append(
                ClassSurfaceAstDescriber._format_arg(current_arg, current_default)
            )
        if args_node.vararg is not None:
            parts.append(
                "*{0}".format(
                    ClassSurfaceAstDescriber._format_arg(args_node.vararg)
                )
            )
        elif len(args_node.kwonlyargs) > 0:
            parts.append("*")
        for current_kwonly_arg, current_default in zip(
                args_node.kwonlyargs,
                args_node.kw_defaults,
        ):
            parts.append(
                ClassSurfaceAstDescriber._format_arg(
                    current_kwonly_arg,
                    current_default,
                )
            )
        if args_node.kwarg is not None:
            parts.append(
                "**{0}".format(
                    ClassSurfaceAstDescriber._format_arg(args_node.kwarg)
                )
            )
        signature = "({0})".format(", ".join(parts))
        if function_node.returns is not None:
            signature = "{0} -> {1}".format(
                signature,
                ast.unparse(function_node.returns),
            )
        return signature

    @staticmethod
    def _format_arg(
            arg_node: ast.arg,
            default_node: Optional[ast.AST] = None,
    ) -> str:
        """
        Return a stable string form for one argument node.

        Args:
            arg_node:
                Argument node to format.
            default_node:
                Optional default-value node.

        Returns:
            str: Source-level argument string.
        """
        argument_text = arg_node.arg
        if arg_node.annotation is not None:
            argument_text = "{0}: {1}".format(
                argument_text,
                ast.unparse(arg_node.annotation),
            )
        if default_node is not None:
            argument_text = "{0} = {1}".format(
                argument_text,
                ast.unparse(default_node),
            )
        return argument_text

    @staticmethod
    def _docstring_summary(docstring: Optional[str]) -> str:
        """
        Return the first non-empty line of one docstring.

        Args:
            docstring:
                Raw docstring text.

        Returns:
            str: First non-empty summary line when present.
        """
        if docstring is None:
            return ""
        for current_line in docstring.splitlines():
            stripped_line = current_line.strip()
            if not stripped_line:
                continue
            return stripped_line
        return ""

    @staticmethod
    def _get_required_access_level(target_object: object) -> str:
        """
        Return the required AST helper access level for one object or raise.

        Args:
            target_object:
                Runtime object whose AST helper access should be resolved.

        Returns:
            str: Required AST helper access level (`public` or `private`).
        """
        access_level = type(target_object).__dict__.get("_ast_helper_access")
        if access_level is None:
            raise ValueError(
                "AST helper access is missing for class '{0}'.".format(
                    type(target_object).__name__
                )
            )
        if not isinstance(access_level, str):
            raise ValueError(
                "AST helper access '{0}' is invalid for class '{1}'.".format(
                    access_level,
                    type(target_object).__name__,
                )
            )
        if access_level not in {"public", "private"}:
            raise ValueError(
                "AST helper access '{0}' is invalid for class '{1}'.".format(
                    access_level,
                    type(target_object).__name__,
                )
            )
        return access_level

    @staticmethod
    def _get_agent_purpose(
            target_object: object,
            *,
            access_level: str,
    ) -> str:
        """
        Return the agent-purpose string for one object.

        Args:
            target_object:
                Runtime object whose agent-purpose should be resolved.
            access_level:
                Required AST helper access level for the object.

        Returns:
            str: Agent-purpose string for the object.
        """
        agent_purpose = type(target_object).__dict__.get("__agent_purpose__")
        if isinstance(agent_purpose, str) and agent_purpose:
            return agent_purpose
        if access_level == "private":
            raise ValueError(
                "Private class '{0}' must define __agent_purpose__.".format(
                    type(target_object).__name__
                )
            )
        return (
            "access: public. Generic Melder object. Use the class surface and "
            "top-level system-doc objects for deeper orientation."
        )

    @staticmethod
    def _describe_inherited_agent_purposes(
            target_object: object,
    ) -> List[InheritedAgentPurposeDescription]:
        """
        Return parent-class agent-purpose entries for one object.

        Purpose:
            Make inherited semantic context explicit without treating inherited
            purpose strings as the concrete object's own purpose.

        Args:
            target_object:
                Runtime object whose parent-class purposes should be described.

        Returns:
            List[InheritedAgentPurposeDescription]: Parent-class purpose
            entries in MRO order.
        """
        inherited_purposes: List[InheritedAgentPurposeDescription] = []
        for base_class in inspect.getmro(type(target_object))[1:]:
            inherited_purpose = base_class.__dict__.get("__agent_purpose__")
            if not isinstance(inherited_purpose, str) or not inherited_purpose:
                continue
            inherited_purposes.append(
                {
                    "class_name": base_class.__name__,
                    "agent_purpose": inherited_purpose,
                }
            )
        return inherited_purposes
