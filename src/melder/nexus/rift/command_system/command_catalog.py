import annotationlib
import collections.abc
import inspect
import typing
from typing import Callable, ClassVar, Dict, List, Literal, Mapping, Optional, Tuple, Union


class CommandCatalog:
    """
    Internal

    Reads a room command's signature and docstring into help, refusals and a tool schema.

    Purpose:
        Give every room an agent-facing command line derived from what its commands already carry: the catalog
        rows `describe_commands()` answers, the help `describe_command(name)` answers, the bind check and the
        refusals `run_command(name, arguments)` answers, and the `{name, description, input_schema}` tool
        definitions `tool_definitions()` answers (GitHub #339). Nothing is hand-maintained, so none of it can drift
        from the code.

    Contract:
        - Stateless: static methods only, no instance state, no caching. The same command answers the same help and
          schema until its code changes.
        - Signatures are read with `inspect.signature(method, annotation_format=annotationlib.Format.FORWARDREF)`,
          so an annotation naming a typing-only import is never evaluated (it reads as `annotationlib.ForwardRef`);
          annotation and signature TEXT comes from `annotationlib.Format.STRING`, so it reads as the source spells
          it (`Optional[str]`, never the evaluated union's repr).
        - Docstrings are read with `inspect.getdoc`. The summary is its first line. The description is its text
          before the first line that is exactly `Args:`, `Returns:`, `Raises:` or `Yields:`, stripped. An `Args:`
          entry is a line one level inside `Args:` shaped `name:`, `name: text` or `name (Type): text`, plus the
          deeper lines under it, joined with single spaces.
        - One refusal shape: `accepted: False`, `command`, `reason` (`command_not_supported` or
          `command_arguments_invalid`), `message`, then `supported_commands`, or `missing_arguments` and
          `unknown_arguments` (tuples). A refusal's message names the command, the problem and - for arguments -
          the command's signature, so the fix is in the text.
        - JSON Schema per parameter, from its forward-reference annotation: `str` string, `int` integer, `float`
          number, `bool` boolean, `None` null; `Optional[X]` with a `None` default is `X`, otherwise `anyOf` with
          null; `Union` is `anyOf`; `Literal` is `enum`; `list`, `tuple`, `set`, `frozenset`, `Sequence` and their
          typing forms are arrays, with `items` for one element type; `dict` and `Mapping` are objects; anything
          else - `object`, `Any`, a class, an unresolved forward reference - is the empty schema. Each property's
          description is its `Args:` entry, else its annotation text; a `str`, `int`, `float`, `bool` or `None`
          default is recorded as `default`.

    Threading:
        Pure reads of live methods and their docstrings; safe from any thread. It takes no lock: callers decide
        whether a read runs inside their own command action.

    Lifecycle / Cleanup:
        Never constructed; it owns nothing to clean.

    Registration:
        MELDER KERNEL - guarded. Used by `CommandSystem`'s `run_command`, `describe_commands`, `describe_command`
        and `tool_definitions`; never user-constructed or bound.

    Subsystem Context:
        Sits beside the room command family (`CommandSystem` and its static, capability and codegen postures). The
        room decides WHICH names it serves - its command list - and runs the command through the command's own
        gates; this class only reads a command it is handed.

    System Context:
        A room's commands are melder's agent interface. A by-name call with a missing argument used to fail in the
        caller's own dispatch with Python's TypeError, and an agent found a list of names but no help. Reading help,
        refusals and schemas from the signatures and docstrings the commands already carry gives the agent a
        command line that cannot disagree with the code it describes.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Reads room commands' signatures and docstrings into help, refusals and tool schemas.
        Melder kernel machinery: read it to understand the runtime, do not drive it directly.
    """

    COMMAND_NOT_SUPPORTED: ClassVar[str] = "command_not_supported"
    COMMAND_ARGUMENTS_INVALID: ClassVar[str] = "command_arguments_invalid"
    _ARGS_SECTION_HEADER: ClassVar[str] = "Args:"
    _DESCRIPTION_END_HEADERS: ClassVar[Tuple[str, ...]] = ("Args:", "Returns:", "Raises:", "Yields:")
    _SCALAR_JSON_TYPES: ClassVar[Tuple[Tuple[type, str], ...]] = (
        (str, "string"),
        (int, "integer"),
        (float, "number"),
        (bool, "boolean"),
    )
    _ARRAY_TYPES: ClassVar[Tuple[type, ...]] = (list, tuple, set, frozenset, collections.abc.Sequence)
    _OBJECT_TYPES: ClassVar[Tuple[type, ...]] = (dict, collections.abc.Mapping)
    _JSON_DEFAULT_TYPES: ClassVar[Tuple[type, ...]] = (str, int, float, bool)

    @staticmethod
    def read_signature(method: Callable[..., object]) -> inspect.Signature:
        """
        Read a command's signature without evaluating its annotations.

        Contract:
            - `annotationlib.Format.FORWARDREF`: a name the defining module imports only under `TYPE_CHECKING`
              reads as an `annotationlib.ForwardRef`, never raising NameError.
            - A bound method's signature leaves out `self`.

        Args:
            method:
                The command, normally a bound method of a room's command system.

        Returns:
            inspect.Signature: The command's signature with forward-reference annotations.

        Raises:
            TypeError:
                If `method` is not callable.
            ValueError:
                If no signature can be read for `method` (some builtins).
        """
        return inspect.signature(method, annotation_format=annotationlib.Format.FORWARDREF)

    @staticmethod
    def signature_text(command_name: str, method: Callable[..., object]) -> str:
        """
        Return the command's signature as text, named and spelled as the source spells it.

        Contract:
            - `annotationlib.Format.STRING`, rendered without quotes around annotations:
              `run_code(code: str, *, frame_name: Optional[str] = None) -> Dict[str, object]`.
            - Defaults render with `repr`; `*args`, `**kwargs`, `/` and `*` markers and the return annotation are
              kept.

        Args:
            command_name:
                The name the room serves the command under.
            method:
                The command.

        Returns:
            str: `command_name` followed by the signature.

        Raises:
            TypeError:
                If `method` is not callable.
        """
        signature = CommandCatalog._read_text_signature(method)
        return "{0}{1}".format(command_name, signature.format(quote_annotation_strings=False))

    @staticmethod
    def summary(method: Callable[..., object]) -> str:
        """
        Return the first line of the command's docstring.

        Args:
            method:
                The command.

        Returns:
            str: The docstring's first line as `inspect.getdoc` cleans it; "" when the command has no docstring.
        """
        doc_lines = CommandCatalog._doc(method).splitlines()
        if len(doc_lines) == 0:
            return ""
        return doc_lines[0]

    @staticmethod
    def description(method: Callable[..., object]) -> str:
        """
        Return the command's docstring text before its first `Args:`, `Returns:`, `Raises:` or `Yields:` line.

        Contract:
            - A header line counts when, stripped, it is exactly one of the four headers; the description stops at
              whichever comes first, and a docstring with none of them is described whole.
            - The result is stripped; "" when the command has no docstring.

        Args:
            method:
                The command.

        Returns:
            str: The tool description of the command (the owner's decision of 2026-11-22, GitHub #339).
        """
        description_lines: List[str] = []
        for line in CommandCatalog._doc(method).splitlines():
            if line.strip() in CommandCatalog._DESCRIPTION_END_HEADERS:
                break
            description_lines.append(line)
        return "\n".join(description_lines).strip()

    @staticmethod
    def argument_entries(method: Callable[..., object]) -> Dict[str, str]:
        """
        Read the `Args:` section of the command's docstring into one text per parameter name.

        Contract:
            - The section is the first line that is exactly `Args:` (stripped) and the lines indented deeper than
              it; the first line less or equally indented ends it.
            - An entry starts on a line at the section's entry level shaped `name:`, `name: text` or
              `name (Type): text`; `*args:` and `**kwargs:` are keyed by their bare names. Lines deeper than the
              entry level continue the entry. The entry's text is its own text and its deeper lines, each
              stripped, joined with single spaces; the `(Type)` part is not part of it.
            - An entry with no text is left out, so the parameter falls back to its annotation text. A line at the
              entry level that is not an entry ends the current entry.

        Args:
            method:
                The command.

        Returns:
            Dict[str, str]: Parameter name -> entry text, in docstring order; empty without an `Args:` section.
        """
        lines = CommandCatalog._doc(method).splitlines()
        header_index = CommandCatalog._find_args_header(lines)
        if header_index is None:
            return {}
        header_indent = CommandCatalog._indent_of(lines[header_index])
        entries: Dict[str, str] = {}
        entry_indent: Optional[int] = None
        entry_name: Optional[str] = None
        entry_parts: List[str] = []
        for line in lines[header_index + 1:]:
            if not line.strip():
                continue
            indent = CommandCatalog._indent_of(line)
            if indent <= header_indent:
                break
            if entry_indent is None:
                entry_indent = indent
            if indent > entry_indent:
                if entry_name is not None:
                    entry_parts.append(line.strip())
                continue
            CommandCatalog._store_argument_entry(entries, entry_name, entry_parts)
            entry_name, entry_parts = CommandCatalog._parse_argument_entry_start(line.strip())
        CommandCatalog._store_argument_entry(entries, entry_name, entry_parts)
        return entries

    @staticmethod
    def argument_rows(method: Callable[..., object]) -> Tuple[Dict[str, object], ...]:
        """
        Return one row per named parameter of the command, in signature order.

        Contract:
            - Each row: `name`, `type` (the annotation as the source spells it; None when the parameter has no
              annotation), `required` (True when it has no default), and `default` only when it is not required -
              the default value itself.
            - `*args` and `**kwargs` are not rows: `run_command` passes keyword arguments only, and the signature
              text shows them.

        Args:
            method:
                The command.

        Returns:
            Tuple[Dict[str, object], ...]: The argument rows.
        """
        rows: List[Dict[str, object]] = []
        for parameter in CommandCatalog._read_text_signature(method).parameters.values():
            if not CommandCatalog._is_named_parameter(parameter):
                continue
            required = parameter.default is inspect.Parameter.empty
            row: Dict[str, object] = {
                "name": parameter.name,
                "type": CommandCatalog._annotation_text(parameter),
                "required": required,
            }
            if not required:
                row["default"] = parameter.default
            rows.append(row)
        return tuple(rows)

    @staticmethod
    def require_argument_mapping(arguments: Optional[Mapping[str, object]]) -> Mapping[str, object]:
        """
        Check the arguments of a by-name call and return them as the mapping to bind.

        Contract:
            - None stands for no arguments and returns a new empty dict; a mapping is returned as it is.
            - Arguments that are not a mapping, or a key that is not a string, are a caller bug, not an agent's
              call to refuse: they raise TypeError.

        Args:
            arguments:
                Argument name -> value, or None.

        Returns:
            Mapping[str, object]: The arguments to bind.

        Raises:
            TypeError:
                If `arguments` is neither None nor a mapping, or one of its keys is not a string.
        """
        if arguments is None:
            return {}
        if not isinstance(arguments, collections.abc.Mapping):
            raise TypeError(
                "arguments must be a mapping of argument names to values, not {0}.".format(
                    type(arguments).__name__,
                )
            )
        for argument_name in arguments:
            if not isinstance(argument_name, str):
                raise TypeError(
                    "argument names must be strings; got {0!r} ({1}).".format(
                        argument_name,
                        type(argument_name).__name__,
                    )
                )
        return arguments

    @staticmethod
    def binding_problems(
            method: Callable[..., object],
            arguments: Mapping[str, object],
    ) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
        """
        Return the missing and the unknown arguments of a keyword-only call to the command.

        Contract:
            - Missing: every parameter without a default, other than `*args` and `**kwargs`, that was not given -
              in signature order. A positional-only parameter cannot be given by name, so one without a default is
              always missing.
            - Unknown: every given name no keyword-passable parameter takes, in the order given - none when the
              command takes `**kwargs`, which receives them. A name given for a positional-only parameter is
              unknown unless `**kwargs` receives it.
            - Only the bind is checked; argument values are never type-checked.

        Args:
            method:
                The command.
            arguments:
                Argument name -> value, as `require_argument_mapping` returned it.

        Returns:
            Tuple[Tuple[str, ...], Tuple[str, ...]]: (missing argument names, unknown argument names); both empty
            when `method(**arguments)` binds.
        """
        parameters = tuple(CommandCatalog.read_signature(method).parameters.values())
        keyword_names = {
            parameter.name
            for parameter in parameters
            if CommandCatalog._is_keyword_parameter(parameter)
        }
        missing_arguments = tuple(
            parameter.name
            for parameter in parameters
            if CommandCatalog._is_named_parameter(parameter)
            and parameter.default is inspect.Parameter.empty
            and (parameter.kind is inspect.Parameter.POSITIONAL_ONLY or parameter.name not in arguments)
        )
        if any(parameter.kind is inspect.Parameter.VAR_KEYWORD for parameter in parameters):
            return missing_arguments, tuple()
        unknown_arguments = tuple(
            argument_name
            for argument_name in arguments
            if argument_name not in keyword_names
        )
        return missing_arguments, unknown_arguments

    @staticmethod
    def refuse_unsupported_command(
            command_name: str,
            supported_commands: Tuple[str, ...],
    ) -> Dict[str, object]:
        """
        Build the refusal for a command name outside the room's command list.

        Args:
            command_name:
                The name as the caller gave it.
            supported_commands:
                The room's command list, in its order.

        Returns:
            Dict[str, object]: `accepted: False`, `command`, `reason: command_not_supported`, `message` (the name and
            the supported commands) and `supported_commands` (a tuple).
        """
        return {
            "accepted": False,
            "command": command_name,
            "reason": CommandCatalog.COMMAND_NOT_SUPPORTED,
            "message": "Command '{0}' is not in this room's command list. Supported commands: {1}.".format(
                command_name,
                ", ".join(supported_commands),
            ),
            "supported_commands": tuple(supported_commands),
        }

    @staticmethod
    def refuse_invalid_arguments(
            command_name: str,
            method: Callable[..., object],
            missing_arguments: Tuple[str, ...],
            unknown_arguments: Tuple[str, ...],
    ) -> Dict[str, object]:
        """
        Build the refusal for arguments that do not bind to the command's signature.

        Contract:
            - The message reads "Command '<name>' cannot run with these arguments: missing required argument(s)
              ...; unknown argument(s) .... Call it as <signature>." - each part only when its names are present.

        Args:
            command_name:
                The command's name in the room's command list.
            method:
                The command, for its signature text.
            missing_arguments:
                Missing argument names, as `binding_problems` returned them.
            unknown_arguments:
                Unknown argument names, as `binding_problems` returned them.

        Returns:
            Dict[str, object]: `accepted: False`, `command`, `reason: command_arguments_invalid`, `message`,
            `missing_arguments` and `unknown_arguments` (tuples).
        """
        problems: List[str] = []
        if len(missing_arguments) > 0:
            problems.append(
                "missing required {0} {1}".format(
                    "argument" if len(missing_arguments) == 1 else "arguments",
                    CommandCatalog._quote_names(missing_arguments),
                )
            )
        if len(unknown_arguments) > 0:
            problems.append(
                "unknown {0} {1}".format(
                    "argument" if len(unknown_arguments) == 1 else "arguments",
                    CommandCatalog._quote_names(unknown_arguments),
                )
            )
        return {
            "accepted": False,
            "command": command_name,
            "reason": CommandCatalog.COMMAND_ARGUMENTS_INVALID,
            "message": "Command '{0}' cannot run with these arguments: {1}. Call it as {2}.".format(
                command_name,
                "; ".join(problems),
                CommandCatalog.signature_text(command_name, method),
            ),
            "missing_arguments": tuple(missing_arguments),
            "unknown_arguments": tuple(unknown_arguments),
        }

    @staticmethod
    def describe_command_summary(command_name: str, method: Callable[..., object]) -> Dict[str, object]:
        """
        Build one `describe_commands()` row.

        Args:
            command_name:
                The command's name in the room's command list.
            method:
                The command.

        Returns:
            Dict[str, object]: `command`, `signature` (`signature_text`) and `summary` (the docstring's first line).
        """
        return {
            "command": command_name,
            "signature": CommandCatalog.signature_text(command_name, method),
            "summary": CommandCatalog.summary(method),
        }

    @staticmethod
    def describe_command_help(command_name: str, method: Callable[..., object]) -> Dict[str, object]:
        """
        Build the `describe_command(name)` answer for a command in the room's list.

        Args:
            command_name:
                The command's name in the room's command list.
            method:
                The command.

        Returns:
            Dict[str, object]: `accepted: True`, `command`, `signature`, `arguments` (`argument_rows`) and `doc`
            (the full docstring as `inspect.getdoc` reads it; "" when there is none).
        """
        return {
            "accepted": True,
            "command": command_name,
            "signature": CommandCatalog.signature_text(command_name, method),
            "arguments": CommandCatalog.argument_rows(method),
            "doc": CommandCatalog._doc(method),
        }

    @staticmethod
    def tool_definition(command_name: str, method: Callable[..., object]) -> Dict[str, object]:
        """
        Build one tool definition for the command.

        Args:
            command_name:
                The command's name in the room's command list.
            method:
                The command.

        Returns:
            Dict[str, object]: Exactly `name`, `description` (`description`) and `input_schema` (`input_schema`).
        """
        return {
            "name": command_name,
            "description": CommandCatalog.description(method),
            "input_schema": CommandCatalog.input_schema(method),
        }

    @staticmethod
    def input_schema(method: Callable[..., object]) -> Dict[str, object]:
        """
        Build the JSON Schema of the keyword arguments `run_command` can pass to the command.

        Contract:
            - `{"type": "object", "properties": ..., "required": [...], "additionalProperties": <bool>}`.
            - `properties`: one schema per keyword-passable parameter, in signature order (the mapping rows of the
              class contract). `*args` is omitted, and so is a positional-only parameter, which cannot be passed by
              name; one without a default stays in `required`, so the schema refuses what `run_command` refuses
              (no room command declares one).
            - `required`: every parameter without a default other than `*args` and `**kwargs`, in signature order,
              so the schema and `run_command`'s bind agree.
            - `additionalProperties`: True only when the command takes `**kwargs`.

        Args:
            method:
                The command.

        Returns:
            Dict[str, object]: The input schema; JSON-serializable, since only JSON-representable defaults are
            recorded.
        """
        text_parameters = CommandCatalog._read_text_signature(method).parameters
        entries = CommandCatalog.argument_entries(method)
        properties: Dict[str, object] = {}
        required: List[str] = []
        accepts_extra_arguments = False
        for parameter in CommandCatalog.read_signature(method).parameters.values():
            if parameter.kind is inspect.Parameter.VAR_KEYWORD:
                accepts_extra_arguments = True
                continue
            if parameter.kind is inspect.Parameter.VAR_POSITIONAL:
                continue
            if parameter.default is inspect.Parameter.empty:
                required.append(parameter.name)
            if parameter.kind is inspect.Parameter.POSITIONAL_ONLY:
                continue
            properties[parameter.name] = CommandCatalog._parameter_schema(
                parameter,
                CommandCatalog._annotation_text(text_parameters[parameter.name]),
                entries.get(parameter.name),
            )
        return {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": accepts_extra_arguments,
        }

    @staticmethod
    def _read_text_signature(method: Callable[..., object]) -> inspect.Signature:
        """
        Read a command's signature with every annotation as its source text.

        Args:
            method:
                The command.

        Returns:
            inspect.Signature: The signature with `annotationlib.Format.STRING` annotations.

        Raises:
            TypeError:
                If `method` is not callable.
        """
        return inspect.signature(method, annotation_format=annotationlib.Format.STRING)

    @staticmethod
    def _doc(method: Callable[..., object]) -> str:
        """
        Return the command's cleaned docstring.

        Args:
            method:
                The command.

        Returns:
            str: `inspect.getdoc(method)`; "" when the command has no docstring.
        """
        doc = inspect.getdoc(method)
        if doc is None:
            return ""
        return doc

    @staticmethod
    def _is_named_parameter(parameter: inspect.Parameter) -> bool:
        """
        Return whether a parameter is a named one - neither `*args` nor `**kwargs`.

        Args:
            parameter:
                A signature parameter.

        Returns:
            bool: True for positional-only, positional-or-keyword and keyword-only parameters.
        """
        return parameter.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)

    @staticmethod
    def _is_keyword_parameter(parameter: inspect.Parameter) -> bool:
        """
        Return whether a parameter can be passed by keyword.

        Args:
            parameter:
                A signature parameter.

        Returns:
            bool: True for positional-or-keyword and keyword-only parameters.
        """
        return parameter.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)

    @staticmethod
    def _annotation_text(parameter: inspect.Parameter) -> Optional[str]:
        """
        Return a parameter's annotation text from a `Format.STRING` signature.

        Args:
            parameter:
                A parameter of `_read_text_signature`'s signature.

        Returns:
            Optional[str]: The annotation as the source spells it; None when the parameter has no annotation.
        """
        if parameter.annotation is inspect.Parameter.empty:
            return None
        return parameter.annotation

    @staticmethod
    def _find_args_header(lines: List[str]) -> Optional[int]:
        """
        Return the index of the first line that is exactly `Args:` once stripped.

        Args:
            lines:
                The docstring's lines.

        Returns:
            Optional[int]: The header's index; None without an `Args:` section.
        """
        for index, line in enumerate(lines):
            if line.strip() == CommandCatalog._ARGS_SECTION_HEADER:
                return index
        return None

    @staticmethod
    def _indent_of(line: str) -> int:
        """
        Return the number of leading whitespace characters of a line.

        Args:
            line:
                One docstring line.

        Returns:
            int: Its indentation width in characters (`inspect.getdoc` has already expanded tabs).
        """
        return len(line) - len(line.lstrip())

    @staticmethod
    def _parse_argument_entry_start(stripped_line: str) -> Tuple[Optional[str], List[str]]:
        """
        Read one line at the `Args:` entry level as the start of an entry.

        Contract:
            - `name:`, `name: text`, `name (Type): text`, `*args:` and `**kwargs:` start an entry; the name is
              returned without stars and the text after the first colon, when any, is its first part.
            - Any other line starts no entry.

        Args:
            stripped_line:
                The line, stripped.

        Returns:
            Tuple[Optional[str], List[str]]: (the parameter name, the entry's first text parts); (None, []) when
            the line starts no entry.
        """
        head, separator, text = stripped_line.partition(":")
        if not separator:
            return None, []
        name_part, opening, type_part = head.partition("(")
        if opening and not type_part.rstrip().endswith(")"):
            return None, []
        name = name_part.strip().lstrip("*")
        if not name.isidentifier():
            return None, []
        if text.strip():
            return name, [text.strip()]
        return name, []

    @staticmethod
    def _store_argument_entry(
            entries: Dict[str, str],
            entry_name: Optional[str],
            entry_parts: List[str],
    ) -> None:
        """
        Store a finished `Args:` entry when it names a parameter and has text.

        Args:
            entries:
                The entries read so far; updated in place.
            entry_name:
                The finished entry's parameter name; None when the lines read did not start an entry.
            entry_parts:
                The finished entry's text parts.

        Returns:
            None.
        """
        if entry_name is None or len(entry_parts) == 0:
            return
        entries[entry_name] = " ".join(entry_parts)

    @staticmethod
    def _quote_names(names: Tuple[str, ...]) -> str:
        """
        Quote argument names for a refusal message.

        Args:
            names:
                The argument names.

        Returns:
            str: `'a', 'b'`.
        """
        return ", ".join("'{0}'".format(name) for name in names)

    @staticmethod
    def _parameter_schema(
            parameter: inspect.Parameter,
            annotation_text: Optional[str],
            argument_entry: Optional[str],
    ) -> Dict[str, object]:
        """
        Build one property schema of `input_schema`.

        Contract:
            - The schema of the parameter's forward-reference annotation (`_annotation_schema`), told whether the
              default is None so `Optional[X] = None` maps to `X`; the empty schema without an annotation.
            - `description`: the `Args:` entry, else the annotation text; none when the parameter has neither.
            - `default`: the default when it is a `str`, `int`, `float`, `bool` or None.

        Args:
            parameter:
                A keyword-passable parameter of `read_signature`'s signature.
            annotation_text:
                The parameter's annotation as the source spells it; None without one.
            argument_entry:
                The parameter's `Args:` entry; None without one.

        Returns:
            Dict[str, object]: The property schema.
        """
        has_default = parameter.default is not inspect.Parameter.empty
        if parameter.annotation is inspect.Parameter.empty:
            schema: Dict[str, object] = {}
        else:
            schema = CommandCatalog._annotation_schema(
                parameter.annotation,
                none_default=has_default and parameter.default is None,
            )
        description = argument_entry if argument_entry else annotation_text
        if description:
            schema["description"] = description
        if has_default and (
                parameter.default is None or isinstance(parameter.default, CommandCatalog._JSON_DEFAULT_TYPES)
        ):
            schema["default"] = parameter.default
        return schema

    @staticmethod
    def _annotation_schema(annotation: object, *, none_default: bool = False) -> Dict[str, object]:
        """
        Map one forward-reference annotation to its JSON Schema.

        Contract:
            - The mapping rows of the class contract; nested annotations (`Union` members, an array's element type)
              map the same way, never with `none_default`.
            - `Optional[X]` (a `Union` with None) maps to `X` - or `anyOf` of its other members - when
              `none_default` is True, else to `anyOf` of every member, null included.
            - Anything the rows do not name is the empty schema; its description is added by the caller.

        Args:
            annotation:
                The annotation as `annotationlib.Format.FORWARDREF` read it.
            none_default:
                True when the parameter's default is None.

        Returns:
            Dict[str, object]: A new schema dict.
        """
        origin = typing.get_origin(annotation)
        if origin is Union:
            members = typing.get_args(annotation)
            non_none_members = tuple(member for member in members if member is not type(None))
            if none_default and len(non_none_members) < len(members):
                if len(non_none_members) == 1:
                    return CommandCatalog._annotation_schema(non_none_members[0])
                return {"anyOf": [CommandCatalog._annotation_schema(member) for member in non_none_members]}
            return {"anyOf": [CommandCatalog._annotation_schema(member) for member in members]}
        if origin is Literal:
            return {"enum": list(typing.get_args(annotation))}
        if annotation is None or annotation is type(None):
            return {"type": "null"}
        for scalar_type, json_type in CommandCatalog._SCALAR_JSON_TYPES:
            if annotation is scalar_type:
                return {"type": json_type}
        container = origin if origin is not None else annotation
        if container in CommandCatalog._ARRAY_TYPES:
            schema: Dict[str, object] = {"type": "array"}
            element_types = tuple(
                element_type
                for element_type in typing.get_args(annotation)
                if element_type is not Ellipsis
            )
            if len(element_types) == 1:
                schema["items"] = CommandCatalog._annotation_schema(element_types[0])
            return schema
        if container in CommandCatalog._OBJECT_TYPES:
            return {"type": "object"}
        return {}
