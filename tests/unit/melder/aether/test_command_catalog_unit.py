"""
`CommandCatalog`: a room command's help, refusals and tool schema, read from its signature and docstring (GitHub #339).

Purpose:
    Pin the catalog's reading rules on small stand-in commands: the signature text as the source spells it (an
    annotation naming a typing-only import is never evaluated), the docstring's summary, description and `Args:`
    entries in their three forms, the argument rows, the binding check `run_command` applies, the refusal shape and
    its messages, and every JSON Schema mapping row of a tool definition.
"""
import annotationlib
import inspect
import json
import types
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)

import pytest

from melder.nexus.rift.command_system.command_catalog import CommandCatalog

if TYPE_CHECKING:
    from melder.nexus.rift.command_system.codegen_command_system import CodegenCommandSystem


class _Commands:
    """
    Stand-in command surface: methods shaped like room commands, with docstrings in the room's style.

    Contract:
        - Each method exists only to be read by `CommandCatalog`; calling one returns its arguments.
    """

    def run_code(
            self,
            code: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Run one piece of code in a frame.

        Purpose:
            Stand in for `execute_codegen`.

        Args:
            code:
                The source to run.
                Its second line.
            frame_name: The frame to run in; the room's
                default frame when omitted.

        Returns:
            Dict[str, object]: What the run returned.

        Raises:
            ValueError: If `code` is empty.
        """
        return {"code": code, "frame_name": frame_name}

    def documented(
            self,
            plain: str,
            typed: int,
            undocumented: float,
            *,
            empty_entry: bool = False,
    ) -> None:
        """
        Read the `Args:` entry forms.

        Args:
            plain: Plain entry text.
            typed (int): Typed entry text
                that continues deeper.
            empty_entry:

        Returns:
            None.
        """

    def variadic(
            self,
            method_name: str,
            *args: Any,
            bind_as_name: Optional[str] = None,
            **kwargs: Any,
    ) -> object:
        """
        Call a method with extra arguments.

        Args:
            method_name:
                Method to call.
            *args:
                Positional arguments passed on.
            bind_as_name:
                Optional binding name.
            **kwargs:
                Keyword arguments passed on.

        Returns:
            object: The arguments, as given.
        """
        return method_name, args, bind_as_name, kwargs

    def positional(self, first: str, /, second: str = "two") -> Tuple[str, str]:
        """
        Take one positional-only argument.

        Args:
            first: The positional-only argument.
            second: An ordinary argument.

        Returns:
            Tuple[str, str]: Both arguments.
        """
        return first, second

    def positional_with_kwargs(self, first: str, /, **kwargs: Any) -> object:
        """Take one positional-only argument and any keyword arguments."""
        return first, kwargs

    def hidden_room(self, room: CodegenCommandSystem) -> CodegenCommandSystem:
        """
        Take a room typed only under `TYPE_CHECKING`.

        Returns:
            CodegenCommandSystem: The room, as given.
        """
        return room


class _Sections:
    """
    Stand-in commands whose docstrings put a different section first, or none.
    """

    def returns_first(self) -> int:
        """
        Answer a number.

        Returns:
            int: The number.

        Args:
            none: Not a parameter.
        """
        return 1

    def raises_first(self) -> None:
        """
        Refuse always.

        Raises:
            ValueError: Always.
        """
        raise ValueError("always")

    def yields_first(self) -> Iterator[int]:
        """
        Yield one number.

        Yields:
            int: The number.
        """
        yield 1

    def no_sections(self) -> None:
        """
        Do nothing.

        Contract:
            - Nothing happens.
        """


class _SchemaShapes:
    """
    Stand-in command whose keyword-only parameters cover every JSON Schema mapping row.
    """

    def shapes(
            self,
            *,
            text: str,
            count: int,
            ratio: float,
            flag: bool,
            nothing: None,
            optional_with_none: Optional[str] = None,
            optional_required: Optional[str],
            optional_with_value: Optional[int] = 5,
            optional_union_with_none: Optional[Union[int, str]] = None,
            either: Union[int, str],
            choice: Literal["a", "b"],
            int_list: List[int],
            str_list: list[str],
            bare_list: list,
            str_tuple: Tuple[str, ...],
            pair_tuple: Tuple[int, str],
            int_set: Set[int],
            frozen_ints: frozenset[int],
            str_sequence: Sequence[str],
            optional_int_list: List[Optional[int]],
            object_dict: Dict[str, object],
            int_mapping: Mapping[str, int],
            bare_dict: dict,
            anything: object,
            any_value: Any,
            catalog: CommandCatalog,
            room: CodegenCommandSystem,
            text_default: str = "objects",
            int_default: int = 50,
            float_default: float = 0.5,
            bool_default: bool = False,
            tuple_default: Tuple[str, ...] = (),
            object_default: object = object(),
    ) -> object:
        """
        Accept one parameter per schema row.

        Returns:
            object: Nothing.
        """


def test_signature_text_reads_as_the_source_spells_it() -> None:
    """
    Contract: the signature text names the command and spells each annotation as the source does (`Optional[str]`,
    never the evaluated union's repr), with defaults, `*args`, `**kwargs`, `/` and the return annotation.
    """
    commands = _Commands()

    assert CommandCatalog.signature_text("run_code", commands.run_code) == (
        "run_code(code: str, *, frame_name: Optional[str] = None) -> Dict[str, object]"
    )
    assert CommandCatalog.signature_text("variadic", commands.variadic) == (
        "variadic(method_name: str, *args: Any, bind_as_name: Optional[str] = None, **kwargs: Any) -> object"
    )
    assert CommandCatalog.signature_text("positional", commands.positional) == (
        "positional(first: str, /, second: str = 'two') -> Tuple[str, str]"
    )


def test_a_typing_only_annotation_is_read_without_being_evaluated() -> None:
    """
    Contract: a command annotated with a name imported only under `TYPE_CHECKING` is read as a forward reference -
    never evaluated, so no NameError - and its text is the name as written.
    """
    commands = _Commands()

    signature = CommandCatalog.read_signature(commands.hidden_room)

    assert isinstance(signature.parameters["room"].annotation, annotationlib.ForwardRef)
    assert CommandCatalog.signature_text("hidden_room", commands.hidden_room) == (
        "hidden_room(room: CodegenCommandSystem) -> CodegenCommandSystem"
    )
    assert CommandCatalog.input_schema(commands.hidden_room)["properties"]["room"] == {
        "description": "CodegenCommandSystem",
    }


def test_summary_is_the_first_docstring_line() -> None:
    """
    Contract: the summary is the docstring's first line; a command without a docstring has an empty summary.
    """
    commands = _Commands()
    no_docstring: Callable[[int], int] = lambda value: value

    assert CommandCatalog.summary(commands.run_code) == "Run one piece of code in a frame."
    assert CommandCatalog.summary(commands.positional_with_kwargs) == (
        "Take one positional-only argument and any keyword arguments."
    )
    assert CommandCatalog.summary(no_docstring) == ""


def test_description_is_the_text_before_args() -> None:
    """
    Contract: the description is the docstring's text before the first `Args:` line, stripped - here the summary and
    the `Purpose:` section.
    """
    commands = _Commands()

    assert CommandCatalog.description(commands.run_code) == (
        "Run one piece of code in a frame.\n\nPurpose:\n    Stand in for `execute_codegen`."
    )


@pytest.mark.parametrize(
    ("method_name", "expected_description"),
    [
        pytest.param("returns_first", "Answer a number.", id="returns"),
        pytest.param("raises_first", "Refuse always.", id="raises"),
        pytest.param("yields_first", "Yield one number.", id="yields"),
        pytest.param("no_sections", "Do nothing.\n\nContract:\n    - Nothing happens.", id="none"),
    ],
)
def test_description_stops_at_the_first_section_of_any_kind(
        method_name: str,
        expected_description: str,
) -> None:
    """
    Contract: `Returns:`, `Raises:` and `Yields:` end the description as `Args:` does, whichever comes first; a
    docstring with none of them is described whole.
    """
    method = getattr(_Sections(), method_name)

    assert CommandCatalog.description(method) == expected_description


def test_a_command_without_a_docstring_has_no_description_entries_or_doc() -> None:
    """
    Contract: a callable with no docstring is described by nothing - empty description, no `Args:` entries - and its
    parameters fall back to their annotation text, which an unannotated parameter does not have.
    """
    no_docstring: Callable[[int], int] = lambda value: value

    assert CommandCatalog.description(no_docstring) == ""
    assert CommandCatalog.argument_entries(no_docstring) == {}
    assert CommandCatalog.input_schema(no_docstring) == {
        "type": "object",
        "properties": {"value": {}},
        "required": ["value"],
        "additionalProperties": False,
    }
    assert CommandCatalog.argument_rows(no_docstring) == (
        {"name": "value", "type": None, "required": True},
    )


def test_args_entries_are_read_in_all_three_forms() -> None:
    """
    Contract: an `Args:` entry is `name:` with deeper lines, `name: text` (with any deeper continuation) or
    `name (Type): text`, joined with single spaces; an entry with no text is no entry.
    """
    commands = _Commands()

    assert CommandCatalog.argument_entries(commands.run_code) == {
        "code": "The source to run. Its second line.",
        "frame_name": "The frame to run in; the room's default frame when omitted.",
    }
    assert CommandCatalog.argument_entries(commands.documented) == {
        "plain": "Plain entry text.",
        "typed": "Typed entry text that continues deeper.",
    }


def test_args_entries_for_star_parameters_are_keyed_by_their_bare_names() -> None:
    """
    Contract: `*args:` and `**kwargs:` entries are read under the parameters' bare names.
    """
    commands = _Commands()

    assert CommandCatalog.argument_entries(commands.variadic) == {
        "method_name": "Method to call.",
        "args": "Positional arguments passed on.",
        "bind_as_name": "Optional binding name.",
        "kwargs": "Keyword arguments passed on.",
    }


def test_a_property_is_described_by_its_args_entry_else_its_annotation_text() -> None:
    """
    Contract: each property's description is its `Args:` entry; a parameter without one (or with an empty one) is
    described by its annotation text.
    """
    commands = _Commands()

    properties = CommandCatalog.input_schema(commands.documented)["properties"]

    assert properties == {
        "plain": {"type": "string", "description": "Plain entry text."},
        "typed": {"type": "integer", "description": "Typed entry text that continues deeper."},
        "undocumented": {"type": "number", "description": "float"},
        "empty_entry": {"type": "boolean", "description": "bool", "default": False},
    }


def test_argument_rows_follow_the_signature() -> None:
    """
    Contract: one row per named parameter, in signature order - `name`, `type` (the annotation as the source spells
    it), `required`, and `default` only when not required; `*args` and `**kwargs` are not rows.
    """
    commands = _Commands()

    assert CommandCatalog.argument_rows(commands.run_code) == (
        {"name": "code", "type": "str", "required": True},
        {"name": "frame_name", "type": "Optional[str]", "required": False, "default": None},
    )
    assert CommandCatalog.argument_rows(commands.variadic) == (
        {"name": "method_name", "type": "str", "required": True},
        {"name": "bind_as_name", "type": "Optional[str]", "required": False, "default": None},
    )
    assert CommandCatalog.argument_rows(commands.positional) == (
        {"name": "first", "type": "str", "required": True},
        {"name": "second", "type": "str", "required": False, "default": "two"},
    )


@pytest.mark.parametrize(
    ("arguments", "expected_missing", "expected_unknown"),
    [
        pytest.param({"code": "x"}, (), (), id="binds"),
        pytest.param({"code": "x", "frame_name": None}, (), (), id="binds-with-optional"),
        pytest.param({}, ("code",), (), id="missing"),
        pytest.param({"code": "x", "frame": "ops"}, (), ("frame",), id="unknown"),
        pytest.param({"source": "x"}, ("code",), ("source",), id="missing-and-unknown"),
        pytest.param({"zeta": 1, "alpha": 2, "code": "x"}, (), ("zeta", "alpha"), id="unknown-in-given-order"),
    ],
)
def test_binding_problems_name_the_missing_and_unknown_arguments(
        arguments: Dict[str, object],
        expected_missing: Tuple[str, ...],
        expected_unknown: Tuple[str, ...],
) -> None:
    """
    Contract: missing arguments are the parameters without defaults that were not given, in signature order;
    unknown arguments are the given names no parameter takes, in the order given.
    """
    commands = _Commands()

    assert CommandCatalog.binding_problems(commands.run_code, arguments) == (expected_missing, expected_unknown)


def test_binding_with_kwargs_reports_no_unknown_arguments_and_never_args() -> None:
    """
    Contract: a command taking `**kwargs` has no unknown arguments; `*args` is never reported missing.
    """
    commands = _Commands()

    assert CommandCatalog.binding_problems(commands.variadic, {"method_name": "m", "extra": 1}) == ((), ())
    assert CommandCatalog.binding_problems(commands.variadic, {"extra": 1}) == (("method_name",), ())


def test_a_positional_only_parameter_given_by_name_is_unknown_and_missing() -> None:
    """
    Contract: an argument given by name for a positional-only parameter is unknown and the parameter is missing -
    unless the command takes `**kwargs`, which receives the name, so it is only missing.
    """
    commands = _Commands()

    assert CommandCatalog.binding_problems(commands.positional, {"first": "a"}) == (("first",), ("first",))
    assert CommandCatalog.binding_problems(commands.positional_with_kwargs, {"first": "a"}) == (("first",), ())


def test_require_argument_mapping_accepts_none_and_mappings() -> None:
    """
    Contract: None stands for no arguments; any mapping with string keys is accepted as it is.
    """
    arguments = {"code": "x"}
    read_only = types.MappingProxyType({"code": "x"})

    assert CommandCatalog.require_argument_mapping(None) == {}
    assert CommandCatalog.require_argument_mapping(arguments) is arguments
    assert CommandCatalog.require_argument_mapping(read_only) is read_only


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        pytest.param(["code"], "arguments must be a mapping of argument names to values, not list.", id="list"),
        pytest.param("code=x", "arguments must be a mapping of argument names to values, not str.", id="str"),
        pytest.param({1: "x"}, "argument names must be strings; got 1 (int).", id="int-key"),
    ],
)
def test_require_argument_mapping_raises_type_error_for_a_caller_bug(arguments: object, message: str) -> None:
    """
    Contract: arguments that are not a mapping, or a mapping with a key that is not a string, raise TypeError - a
    caller bug, not an agent's call to refuse.
    """
    with pytest.raises(TypeError) as raised:
        CommandCatalog.require_argument_mapping(arguments)

    assert str(raised.value) == message


def test_unsupported_command_refusal_names_the_command_and_the_supported_ones() -> None:
    """
    Contract: the `command_not_supported` refusal carries the command as given, a message listing the supported
    commands, and the supported commands themselves as a tuple.
    """
    refusal = CommandCatalog.refuse_unsupported_command("cleanup", ("run_code", "describe_command"))

    assert refusal == {
        "accepted": False,
        "command": "cleanup",
        "reason": "command_not_supported",
        "message": (
            "Command 'cleanup' is not in this room's command list. Supported commands: run_code, describe_command."
        ),
        "supported_commands": ("run_code", "describe_command"),
    }


@pytest.mark.parametrize(
    ("missing", "unknown", "problem_text"),
    [
        pytest.param(("code",), (), "missing required argument 'code'", id="missing"),
        pytest.param((), ("frame",), "unknown argument 'frame'", id="unknown"),
        pytest.param(("code",), ("source",), "missing required argument 'code'; unknown argument 'source'", id="both"),
        pytest.param(
            ("code", "frame_name"),
            ("a", "b"),
            "missing required arguments 'code', 'frame_name'; unknown arguments 'a', 'b'",
            id="plural",
        ),
    ],
)
def test_invalid_arguments_refusal_names_the_command_the_problem_and_the_signature(
        missing: Tuple[str, ...],
        unknown: Tuple[str, ...],
        problem_text: str,
) -> None:
    """
    Contract: the `command_arguments_invalid` refusal's message names the command, what is wrong and the command's
    signature, and the refusal carries both name tuples.
    """
    commands = _Commands()

    refusal = CommandCatalog.refuse_invalid_arguments("run_code", commands.run_code, missing, unknown)

    assert refusal == {
        "accepted": False,
        "command": "run_code",
        "reason": "command_arguments_invalid",
        "message": (
            "Command 'run_code' cannot run with these arguments: {0}. Call it as run_code(code: str, *, "
            "frame_name: Optional[str] = None) -> Dict[str, object].".format(problem_text)
        ),
        "missing_arguments": missing,
        "unknown_arguments": unknown,
    }


def test_command_summary_row_carries_command_signature_and_summary() -> None:
    """
    Contract: a `describe_commands` row is exactly `command`, `signature` and `summary`.
    """
    commands = _Commands()

    assert CommandCatalog.describe_command_summary("run_code", commands.run_code) == {
        "command": "run_code",
        "signature": "run_code(code: str, *, frame_name: Optional[str] = None) -> Dict[str, object]",
        "summary": "Run one piece of code in a frame.",
    }


def test_command_help_carries_arguments_and_the_full_docstring() -> None:
    """
    Contract: `describe_command` help is `accepted: True`, `command`, `signature`, the argument rows and the full
    docstring as `inspect.getdoc` reads it.
    """
    commands = _Commands()

    assert CommandCatalog.describe_command_help("run_code", commands.run_code) == {
        "accepted": True,
        "command": "run_code",
        "signature": "run_code(code: str, *, frame_name: Optional[str] = None) -> Dict[str, object]",
        "arguments": (
            {"name": "code", "type": "str", "required": True},
            {"name": "frame_name", "type": "Optional[str]", "required": False, "default": None},
        ),
        "doc": inspect.getdoc(commands.run_code),
    }


def test_tool_definition_is_name_description_and_input_schema() -> None:
    """
    Contract: a tool definition is exactly `name`, `description` (the text before `Args:`) and `input_schema`, an
    object schema whose `required` lists the parameters without defaults; it is JSON-serializable.
    """
    commands = _Commands()

    definition = CommandCatalog.tool_definition("run_code", commands.run_code)

    assert definition == {
        "name": "run_code",
        "description": "Run one piece of code in a frame.\n\nPurpose:\n    Stand in for `execute_codegen`.",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "The source to run. Its second line."},
                "frame_name": {
                    "type": "string",
                    "description": "The frame to run in; the room's default frame when omitted.",
                    "default": None,
                },
            },
            "required": ["code"],
            "additionalProperties": False,
        },
    }
    assert json.loads(json.dumps(definition)) == definition


def test_kwargs_allow_additional_properties_and_args_are_omitted() -> None:
    """
    Contract: `**kwargs` makes `additionalProperties` true; `*args` and `**kwargs` are never properties or required.
    """
    commands = _Commands()

    assert CommandCatalog.input_schema(commands.variadic) == {
        "type": "object",
        "properties": {
            "method_name": {"type": "string", "description": "Method to call."},
            "bind_as_name": {"type": "string", "description": "Optional binding name.", "default": None},
        },
        "required": ["method_name"],
        "additionalProperties": True,
    }


def test_a_positional_only_parameter_is_required_but_never_a_property() -> None:
    """
    Contract: `run_command` passes keyword arguments only, so a positional-only parameter is no property; one without
    a default stays required, so the schema refuses what `run_command` refuses.
    """
    commands = _Commands()

    assert CommandCatalog.input_schema(commands.positional) == {
        "type": "object",
        "properties": {"second": {"type": "string", "description": "An ordinary argument.", "default": "two"}},
        "required": ["first"],
        "additionalProperties": False,
    }


@pytest.mark.parametrize(
    ("parameter_name", "expected_schema"),
    [
        pytest.param("text", {"type": "string", "description": "str"}, id="str"),
        pytest.param("count", {"type": "integer", "description": "int"}, id="int"),
        pytest.param("ratio", {"type": "number", "description": "float"}, id="float"),
        pytest.param("flag", {"type": "boolean", "description": "bool"}, id="bool"),
        pytest.param("nothing", {"type": "null", "description": "None"}, id="None"),
        pytest.param(
            "optional_with_none",
            {"type": "string", "description": "Optional[str]", "default": None},
            id="Optional-None-default",
        ),
        pytest.param(
            "optional_required",
            {"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional[str]"},
            id="Optional-no-default",
        ),
        pytest.param(
            "optional_with_value",
            {"anyOf": [{"type": "integer"}, {"type": "null"}], "description": "Optional[int]", "default": 5},
            id="Optional-value-default",
        ),
        pytest.param(
            "optional_union_with_none",
            {"anyOf": [{"type": "integer"}, {"type": "string"}], "description": "Optional[Union[int, str]]",
             "default": None},
            id="Optional-Union-None-default",
        ),
        pytest.param(
            "either",
            {"anyOf": [{"type": "integer"}, {"type": "string"}], "description": "Union[int, str]"},
            id="Union",
        ),
        pytest.param("choice", {"enum": ["a", "b"], "description": "Literal['a', 'b']"}, id="Literal"),
        pytest.param(
            "int_list",
            {"type": "array", "items": {"type": "integer"}, "description": "List[int]"},
            id="List",
        ),
        pytest.param(
            "str_list",
            {"type": "array", "items": {"type": "string"}, "description": "list[str]"},
            id="list-generic",
        ),
        pytest.param("bare_list", {"type": "array", "description": "list"}, id="bare-list"),
        pytest.param(
            "str_tuple",
            {"type": "array", "items": {"type": "string"}, "description": "Tuple[str, ...]"},
            id="Tuple-variadic",
        ),
        pytest.param("pair_tuple", {"type": "array", "description": "Tuple[int, str]"}, id="Tuple-pair"),
        pytest.param(
            "int_set",
            {"type": "array", "items": {"type": "integer"}, "description": "Set[int]"},
            id="Set",
        ),
        pytest.param(
            "frozen_ints",
            {"type": "array", "items": {"type": "integer"}, "description": "frozenset[int]"},
            id="frozenset",
        ),
        pytest.param(
            "str_sequence",
            {"type": "array", "items": {"type": "string"}, "description": "Sequence[str]"},
            id="Sequence",
        ),
        pytest.param(
            "optional_int_list",
            {
                "type": "array",
                "items": {"anyOf": [{"type": "integer"}, {"type": "null"}]},
                "description": "List[Optional[int]]",
            },
            id="List-of-Optional",
        ),
        pytest.param("object_dict", {"type": "object", "description": "Dict[str, object]"}, id="Dict"),
        pytest.param("int_mapping", {"type": "object", "description": "Mapping[str, int]"}, id="Mapping"),
        pytest.param("bare_dict", {"type": "object", "description": "dict"}, id="bare-dict"),
        pytest.param("anything", {"description": "object"}, id="object"),
        pytest.param("any_value", {"description": "Any"}, id="Any"),
        pytest.param("catalog", {"description": "CommandCatalog"}, id="class"),
        pytest.param("room", {"description": "CodegenCommandSystem"}, id="unresolved-forward-reference"),
        pytest.param(
            "text_default",
            {"type": "string", "description": "str", "default": "objects"},
            id="str-default",
        ),
        pytest.param("int_default", {"type": "integer", "description": "int", "default": 50}, id="int-default"),
        pytest.param(
            "float_default",
            {"type": "number", "description": "float", "default": 0.5},
            id="float-default",
        ),
        pytest.param(
            "bool_default",
            {"type": "boolean", "description": "bool", "default": False},
            id="bool-default",
        ),
        pytest.param(
            "tuple_default",
            {"type": "array", "items": {"type": "string"}, "description": "Tuple[str, ...]"},
            id="tuple-default-not-recorded",
        ),
        pytest.param("object_default", {"description": "object"}, id="object-default-not-recorded"),
    ],
)
def test_each_annotation_maps_to_its_json_schema(parameter_name: str, expected_schema: Dict[str, object]) -> None:
    """
    Contract: every JSON Schema mapping row of the patch lane - scalars, None, Optional with and without a None
    default, Union, Literal, the array and object forms, the empty schema for `object`, `Any`, a class and an
    unresolved forward reference, and only JSON-representable defaults recorded.
    """
    properties = CommandCatalog.input_schema(_SchemaShapes().shapes)["properties"]

    assert properties[parameter_name] == expected_schema


def test_required_lists_exactly_the_parameters_without_defaults() -> None:
    """
    Contract: `required` names every parameter without a default, in signature order, and nothing else; a command
    without `**kwargs` refuses additional properties.
    """
    schema = CommandCatalog.input_schema(_SchemaShapes().shapes)

    assert schema["required"] == [
        "text",
        "count",
        "ratio",
        "flag",
        "nothing",
        "optional_required",
        "either",
        "choice",
        "int_list",
        "str_list",
        "bare_list",
        "str_tuple",
        "pair_tuple",
        "int_set",
        "frozen_ints",
        "str_sequence",
        "optional_int_list",
        "object_dict",
        "int_mapping",
        "bare_dict",
        "anything",
        "any_value",
        "catalog",
        "room",
    ]
    assert schema["additionalProperties"] is False
    assert schema["type"] == "object"
