"""Translate documented code fences into reStructuredText before autodoc renders them.

Melder contains Markdown-style fences, including legacy single-backtick language
fences. This bridge changes presentation only and deliberately preserves content.
"""

import ast
import re
import textwrap
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sphinx.application import Sphinx


class DocstringFormatter:
    """Stateless conversion of known code-fence markup; never evaluate documented code."""

    _OPEN = re.compile(r"^(\s*)(`{1,3}|~~~)(python|py|json|bash|shell|text|toml|yaml|powershell)\s*$")
    _SECTION = re.compile(r"^[A-Z][A-Za-z /_`()-]+:\s*$")
    _LIST = re.compile(r"^(\s*)(?:[-*+] |\d+[.)] )")
    _LITERAL = re.compile(r"^(\s*)\.\. (?:code-block|code|sourcecode)::")

    @staticmethod
    def _indented_end(lines: list[str], start: int, indentation: int) -> int:
        """Find the end of a blank/indented block without interpreting its contents."""
        end = start
        while end < len(lines):
            line = lines[end]
            if line.strip() and len(line) - len(line.lstrip()) <= indentation:
                break
            end += 1
        return end

    @classmethod
    def _examples(cls, lines: list[str]) -> list[str]:
        """Mark syntactically valid indented Python examples as code, never as prose lists.

        Only explicit Example sections or prose ending in a colon are candidates.
        Parsing is read-only; incomplete fragments and non-code prose stay unchanged.
        """
        result: list[str] = []
        position = 0
        while position < len(lines):
            line = lines[position]
            literal = cls._LITERAL.match(line)
            if literal:
                end = cls._indented_end(lines, position + 1, len(literal.group(1)))
                result.extend(lines[position:end])
                position = end
                continue
            is_example = line.strip() in ("Example:", "Examples:")
            if line.rstrip().endswith(":") and (is_example or not cls._SECTION.fullmatch(line)):
                indentation = len(line) - len(line.lstrip())
                end = cls._indented_end(lines, position + 1, indentation)
                code = textwrap.dedent("\n".join(lines[position + 1:end])).strip("\n")
                try:
                    parsed = ast.parse(code) if code.strip() else None
                except SyntaxError:
                    parsed = None
                if parsed is not None and parsed.body:
                    prefix = " " * (indentation + 4 if is_example else indentation)
                    result.extend([line, "", prefix + ".. code-block:: python", ""])
                    result.extend(prefix + "    " + item if item else "" for item in code.splitlines())
                    result.append("")
                    position = end
                    continue
            result.append(line)
            position += 1
        return result

    @classmethod
    def _spacing(cls, lines: list[str]) -> list[str]:
        """Separate list/paragraph boundaries while preserving native literal code exactly."""
        result: list[str] = []
        list_indents: list[int] = []
        position = 0
        while position < len(lines):
            line = lines[position]
            literal = cls._LITERAL.match(line)
            if literal:
                end = cls._indented_end(lines, position + 1, len(literal.group(1)))
                result.extend(lines[position:end])
                position = end
                continue
            if line.strip():
                indentation = len(line) - len(line.lstrip())
                item = cls._LIST.match(line)
                boundary = bool(cls._SECTION.fullmatch(line))
                while list_indents and (indentation < list_indents[-1] or
                                       (item is None and indentation == list_indents[-1])):
                    list_indents.pop()
                    boundary = True
                if item is not None and (not list_indents or indentation > list_indents[-1]):
                    list_indents.append(indentation)
                    boundary = True
                if boundary and result and result[-1].strip():
                    result.append("")
            result.append(line)
            position += 1
        return result

    @classmethod
    def normalize(cls, lines: list[str], name: str) -> list[str]:
        """Convert closed language fences, preserving relative code indentation and prose.

        Raises:
            ValueError: A recognized code fence has no matching closing line.
        """
        result: list[str] = []
        position = 0
        while position < len(lines):
            opening = cls._OPEN.fullmatch(lines[position])
            if opening is None:
                result.append(lines[position])
                position += 1
                continue
            indent, fence, language = opening.groups()
            closing = position + 1
            while closing < len(lines) and lines[closing].strip() != fence:
                closing += 1
            if closing == len(lines):
                raise ValueError(f"Unclosed {language} documentation fence in {name}.")
            code = textwrap.dedent("\n".join(lines[position + 1:closing]))
            result.extend(["", f"{indent}.. code-block:: {'python' if language == 'py' else language}", ""])
            result.extend(indent + "    " + line if line else "" for line in code.splitlines())
            result.append("")
            position = closing + 1
        return cls._spacing(cls._examples(result))

    @classmethod
    def process(cls, app: Sphinx, what: str, name: str, obj: object,
                options: object, lines: list[str]) -> None:
        """Replace the event's mutable presentation lines before Napoleon's formatting pass."""
        lines[:] = cls.normalize(lines, name)


def setup(app: Sphinx) -> dict[str, object]:
    """Register the pure presentation bridge through Sphinx's required extension entrypoint."""
    app.connect("autodoc-process-docstring", DocstringFormatter.process, priority=400)
    return {"version": "1.0", "parallel_read_safe": True, "parallel_write_safe": True}
