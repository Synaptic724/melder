"""Translate documented code fences into reStructuredText before autodoc renders them.

Melder contains Markdown-style fences, including legacy single-backtick language
fences. This bridge changes presentation only and deliberately preserves content.
"""

import re
import textwrap
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sphinx.application import Sphinx


class DocstringFormatter:
    """Stateless conversion of known code-fence markup; never evaluate documented code."""

    _OPEN = re.compile(r"^(\s*)(`{1,3}|~~~)(python|py|json|bash|shell|text|toml|yaml|powershell)\s*$")

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
        return result

    @classmethod
    def process(cls, app: Sphinx, what: str, name: str, obj: object,
                options: object, lines: list[str]) -> None:
        """Replace the event's mutable presentation lines before Napoleon's formatting pass."""
        lines[:] = cls.normalize(lines, name)


def setup(app: Sphinx) -> dict[str, object]:
    """Register the pure presentation bridge through Sphinx's required extension entrypoint."""
    app.connect("autodoc-process-docstring", DocstringFormatter.process, priority=400)
    return {"version": "1.0", "parallel_read_safe": True, "parallel_write_safe": True}
