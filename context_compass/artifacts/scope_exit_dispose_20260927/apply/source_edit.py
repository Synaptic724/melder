"""Function-level and line-block edits that keep each file's line endings. melder_0, 2026-09-27.

`replace_def` swaps a whole function (located by class path and name through the AST) for new source;
`insert_after_def` adds a function after an existing one; `replace_block` swaps an exact block of lines,
compared without line endings. New lines take the line ending of the first line they replace. Every edit
asserts it matched exactly once, so a changed file fails loudly instead of being half-edited silently.
"""

import ast
import sys
from typing import List, Optional, Sequence

assert sys.version_info >= (3, 14), "run with the 3.14 venv"


def read_lines(path: str) -> List[str]:
    """Return the file's lines with their endings (the target files carry no lone CR or other separators)."""
    with open(path, "rb") as handle:
        return handle.read().decode("utf-8").splitlines(keepends=True)


def write_lines(path: str, lines: List[str]) -> None:
    """Write the lines back byte for byte and check the result still parses."""
    text = "".join(lines)
    ast.parse(text)
    with open(path, "wb") as handle:
        handle.write(text.encode("utf-8"))


def _eol(line: str) -> str:
    """Return the line ending of one line."""
    return "\r\n" if line.endswith("\r\n") else "\n"


def _find_def(tree: ast.Module, class_path: Sequence[str], name: str) -> ast.AST:
    """Find exactly one function `name` directly inside the class nesting `class_path`."""
    body = tree.body
    for class_name in class_path:
        classes = [node for node in body if isinstance(node, ast.ClassDef) and node.name == class_name]
        assert len(classes) == 1, (class_path, class_name, len(classes))
        body = classes[0].body
    matches = [node for node in body
               if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name]
    assert len(matches) == 1, (class_path, name, len(matches))
    return matches[0]


def _new_lines(source: str, eol: str) -> List[str]:
    """Split new source into lines carrying `eol`."""
    return [line + eol for line in source.strip("\n").split("\n")]


def replace_def(path: str, class_path: Sequence[str], name: str, source: str,
                must_contain: Optional[Sequence[str]] = None) -> None:
    """Replace one whole function; `must_contain` lists text the old version must hold."""
    lines = read_lines(path)
    node = _find_def(ast.parse("".join(lines)), class_path, name)
    start = (node.decorator_list[0].lineno if node.decorator_list else node.lineno) - 1
    end = node.end_lineno
    old = "".join(lines[start:end])
    for marker in must_contain or ():
        assert marker in old, (path, name, marker)
    lines[start:end] = _new_lines(source, _eol(lines[start]))
    write_lines(path, lines)
    print(f"  replaced {'.'.join([*class_path, name])}")


def insert_after_def(path: str, class_path: Sequence[str], name: str, source: str) -> None:
    """Insert a new function (preceded by one blank line) right after function `name`."""
    lines = read_lines(path)
    node = _find_def(ast.parse("".join(lines)), class_path, name)
    end = node.end_lineno
    eol = _eol(lines[end - 1])
    lines[end:end] = [eol] + _new_lines(source, eol)
    write_lines(path, lines)
    print(f"  inserted after {'.'.join([*class_path, name])}")


def replace_block(path: str, old: str, new: str) -> None:
    """Replace one exact block of whole lines (compared without endings)."""
    lines = read_lines(path)
    old_lines = old.strip("\n").split("\n")
    hits = [i for i in range(len(lines) - len(old_lines) + 1)
            if all(lines[i + k].rstrip("\r\n") == old_lines[k] for k in range(len(old_lines)))]
    assert len(hits) == 1, (path, old_lines[0], len(hits))
    i = hits[0]
    lines[i:i + len(old_lines)] = _new_lines(new, _eol(lines[i]))
    write_lines(path, lines)
    print(f"  block: {old_lines[0].strip()[:70]}")
