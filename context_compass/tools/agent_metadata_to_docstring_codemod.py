"""
Codemod A: move `__ast_helper_access__` / `__agent_purpose__` into docstrings.

WHAT IT DOES
------------
For every class carrying the legacy markers, append an `AGENT_ACCESS:` /
`AGENT_PURPOSE:` section to the END of its existing docstring, sourced from the
attribute values. It does NOT delete the attributes - that is codemod B, run only
after this pass is verified.

WHY THE ATTRIBUTES SURVIVE THIS PASS
------------------------------------
The harvester is DUAL-SOURCE: docstring first, attribute as fallback. So after
this codemod every class has both, the harvested values are identical either way,
and the generated asset MUST be byte-identical to before. That equality is the
cheapest possible correctness check for a 370-file sweep - any diff in the asset
localises the bug to this script rather than to the migration as a whole.

DESIGN CONSTRAINTS
------------------
- IDEMPOTENT. A class whose docstring already carries `AGENT_ACCESS:` is skipped,
  so re-running is a no-op and the sweep can proceed subtree by subtree.
- TEXT-BASED EDITING, AST-BASED DETECTION. `ast.unparse` would reformat whole
  files and destroy the hand-authored docstrings this repo treats as API. So the
  AST is used only to locate nodes; edits are line insertions.
- BOTTOM-UP. Classes are edited in reverse line order so earlier insertions
  cannot invalidate the line numbers of later ones.
- DRY-RUN BY DEFAULT. Nothing is written without `--apply`.

VERIFIED PRECONDITION
---------------------
All 394 marked classes have MULTI-LINE docstrings; zero are single-line and zero
are missing. That was measured before writing this, which is why only one
docstring shape is handled. The script REFUSES any class that does not match
rather than guessing.

USAGE
-----
    python context_compass/scripts/agent_metadata_to_docstring_codemod.py
    python context_compass/scripts/agent_metadata_to_docstring_codemod.py --apply
    python context_compass/scripts/agent_metadata_to_docstring_codemod.py --apply --path aether/conduit
"""
import argparse
import ast
import pathlib
import sys
import textwrap
from typing import List, Optional, Tuple


class CodemodPolicy:
    """
    Static namespace for the codemod's fixed values.

    Attributes:
        ACCESS_MARKER: Docstring marker carrying the access level.
        PURPOSE_MARKER: Docstring marker opening the purpose block.
        LEGACY_ACCESS_ATTR: Retired class attribute read as the source.
        LEGACY_PURPOSE_ATTR: Retired class attribute read as the source.
        SKIP_DIR_NAMES: Directories excluded from the sweep.
        PURPOSE_WRAP_WIDTH: Column the purpose prose wraps at, chosen to sit
            inside the repo's 120-character hard cap once indented. Wrapping
            MUST disable hyphen and long-word breaking: the default splits
            `lock-free` into `lock- free` and `on-collect` into `on- collect`,
            silently corrupting prose. Caught by the byte-identical asset check.
    """

    ACCESS_MARKER: str = "AGENT_ACCESS:"
    PURPOSE_MARKER: str = "AGENT_PURPOSE:"
    LEGACY_ACCESS_ATTR: str = "__ast_helper_access__"
    LEGACY_PURPOSE_ATTR: str = "__agent_purpose__"
    SKIP_DIR_NAMES = {"__pycache__", "__melder_cache__", "_build_assets"}
    PURPOSE_WRAP_WIDTH: int = 88


def _legacy_values(node: ast.ClassDef) -> Tuple[Optional[str], Optional[str]]:
    """
    Read the legacy marker values off one class.

    Args:
        node: The class definition being inspected.

    Returns:
        Tuple[Optional[str], Optional[str]]: Access and purpose, each `None`
            when absent or not a string literal.
    """
    access: Optional[str] = None
    purpose: Optional[str] = None
    for stmt in node.body:
        name: Optional[str] = None
        value: Optional[ast.expr] = None
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            name, value = stmt.target.id, stmt.value
        elif isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
            name, value = stmt.targets[0].id, stmt.value
        if name is None or value is None:
            continue
        try:
            literal = ast.literal_eval(value)
        except Exception:
            continue
        if not isinstance(literal, str):
            continue
        if name == CodemodPolicy.LEGACY_ACCESS_ATTR:
            access = literal
        elif name == CodemodPolicy.LEGACY_PURPOSE_ATTR:
            purpose = literal
    return access, purpose


def _render_section(access: Optional[str], purpose: Optional[str], indent: str) -> List[str]:
    """
    Build the docstring section lines for one class.

    Contract:
        Emits a blank separator line, then the markers, indented to match the
        docstring body. Purpose prose is wrapped so migrated docstrings stay
        inside the repo's line-width standard rather than carrying one 416-char
        line.

    Args:
        access: Access level, or `None` to omit the marker.
        purpose: Purpose prose, or `None` to omit the block.
        indent: Leading whitespace matching the docstring's own indentation.

    Returns:
        List[str]: Lines to insert, without trailing newlines.
    """
    lines: List[str] = [""]
    if access:
        lines.append(f"{indent}{CodemodPolicy.ACCESS_MARKER} {access}")
    if purpose:
        if access:
            lines.append("")
        lines.append(f"{indent}{CodemodPolicy.PURPOSE_MARKER}")
        body_indent = indent + "    "
        for paragraph in purpose.split("\n\n"):
            collapsed = " ".join(paragraph.split())
            if not collapsed:
                continue
            wrapped = textwrap.wrap(
                collapsed,
                width=CodemodPolicy.PURPOSE_WRAP_WIDTH,
                break_on_hyphens=False,
                break_long_words=False,
            )
            lines.extend(f"{body_indent}{w}" for w in wrapped)
    return lines


def _plan_file(path: pathlib.Path) -> Tuple[Optional[str], int, List[str]]:
    """
    Compute the migrated text for one file without writing it.

    Contract:
        Returns `None` text when the file needs no change. Classes are rewritten
        BOTTOM-UP so each insertion leaves earlier line numbers valid.

    Args:
        path: Source file to plan.

    Returns:
        Tuple[Optional[str], int, List[str]]: New text or `None`, the number of
            classes migrated, and any refusals encountered.
    """
    original = path.read_text(encoding="utf-8-sig")
    try:
        tree = ast.parse(original, filename=str(path))
    except SyntaxError as error:
        return None, 0, [f"{path}: unparseable ({error})"]

    lines = original.splitlines()
    refusals: List[str] = []
    edits: List[Tuple[int, List[str]]] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        access, purpose = _legacy_values(node)
        if access is None and purpose is None:
            continue

        docstring = ast.get_docstring(node)
        if docstring is None:
            refusals.append(f"{path}:{node.lineno} {node.name}: markers but no docstring")
            continue
        if CodemodPolicy.ACCESS_MARKER in docstring or CodemodPolicy.PURPOSE_MARKER in docstring:
            continue  # already migrated - idempotent skip

        doc_node = node.body[0]
        if not isinstance(doc_node, ast.Expr):
            refusals.append(f"{path}:{node.lineno} {node.name}: docstring not first statement")
            continue
        end_line = doc_node.end_lineno
        if end_line is None or end_line - 1 >= len(lines):
            refusals.append(f"{path}:{node.lineno} {node.name}: no end position")
            continue

        closing = lines[end_line - 1]
        if closing.strip() not in ('"""', "'''"):
            refusals.append(
                f"{path}:{node.lineno} {node.name}: closing delimiter not on its own line"
            )
            continue

        indent = closing[: len(closing) - len(closing.lstrip())]
        edits.append((end_line - 1, _render_section(access, purpose, indent)))

    if not edits:
        return None, 0, refusals

    for insert_at, section in sorted(edits, key=lambda e: e[0], reverse=True):
        lines[insert_at:insert_at] = section

    trailing = "\n" if original.endswith("\n") else ""
    return "\n".join(lines) + trailing, len(edits), refusals


def main(argv: Optional[List[str]] = None) -> int:
    """
    Run the codemod.

    Args:
        argv: Arguments excluding the program name.

    Returns:
        int: `0` on success, `1` when any class was refused.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    parser.add_argument("--path", default="", help="limit to a subpath below src/melder")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    repo_root = pathlib.Path(__file__).resolve().parent.parent.parent
    scan_root = repo_root / "src" / "melder" / args.path if args.path else repo_root / "src" / "melder"

    migrated_classes = 0
    touched_files = 0
    all_refusals: List[str] = []

    for path in sorted(scan_root.rglob("*.py")):
        if any(part in CodemodPolicy.SKIP_DIR_NAMES for part in path.parts):
            continue
        new_text, count, refusals = _plan_file(path)
        all_refusals.extend(refusals)
        if new_text is None or count == 0:
            continue
        migrated_classes += count
        touched_files += 1
        if args.apply:
            path.write_text(new_text, encoding="utf-8")

    mode = "APPLIED" if args.apply else "DRY RUN"
    print(f"{mode}: {migrated_classes} classes across {touched_files} files")
    if all_refusals:
        print(f"\nREFUSED {len(all_refusals)}:", file=sys.stderr)
        for refusal in all_refusals[:20]:
            print(f"  {refusal}", file=sys.stderr)
        return 1
    if args.apply:
        print(
            "\nNow verify the asset is UNCHANGED - dual-source means it must be:\n"
            "    python src/melder/_build_assets/_build_asset_runner.py --check"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
