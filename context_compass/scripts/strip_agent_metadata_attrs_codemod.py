"""
Codemod B: delete the retired `__ast_helper_access__` / `__agent_purpose__` attrs.

RUN THIS ONLY AFTER CODEMOD A IS VERIFIED
-----------------------------------------
Codemod A copies both markers into class docstrings. This one deletes the class
attributes. Running B first would destroy 76,200 characters of authored prose
with nothing holding a copy, so the script REFUSES to strip any class whose
docstring does not already carry `AGENT_ACCESS:` or `AGENT_PURPOSE:`.

That refusal is the safety property, not a convenience: it makes running the two
codemods out of order a no-op instead of a catastrophe.

WHY THE ASSET MUST NOT CHANGE
-----------------------------
The harvester is dual-source and every marked class now resolves from its
docstring. Deleting the attribute removes only the FALLBACK, which is no longer
being consulted, so the generated asset must be byte-identical afterwards. Any
diff means a class was relying on the attribute after all - i.e. codemod A missed
it - and that is precisely what we want surfaced loudly.

DESIGN CONSTRAINTS
------------------
- IDEMPOTENT. Nothing to delete is a no-op.
- TEXT-BASED EDITING, AST-BASED DETECTION, matching codemod A. `ast.unparse`
  would reformat whole files and destroy hand-authored docstrings.
- BOTTOM-UP deletion so earlier line numbers stay valid.
- HANDLES MULTI-LINE VALUES. Most `__agent_purpose__` assignments are wrapped in
  parentheses across several lines; the whole statement span is removed, not just
  its first line.
- DRY-RUN BY DEFAULT.

USAGE
-----
    python context_compass/scripts/strip_agent_metadata_attrs_codemod.py
    python context_compass/scripts/strip_agent_metadata_attrs_codemod.py --apply
    python context_compass/scripts/strip_agent_metadata_attrs_codemod.py --apply --path utilities
"""
import argparse
import ast
import pathlib
import sys
from typing import List, Optional, Tuple


class StripPolicy:
    """
    Static namespace for the strip codemod's fixed values.

    Attributes:
        ACCESS_MARKER: Docstring marker proving the access value was preserved.
        PURPOSE_MARKER: Docstring marker proving the purpose was preserved.
        LEGACY_ATTRS: The class attributes this codemod removes.
        SKIP_DIR_NAMES: Directories excluded from the sweep.
    """

    ACCESS_MARKER: str = "AGENT_ACCESS:"
    PURPOSE_MARKER: str = "AGENT_PURPOSE:"
    LEGACY_ATTRS = ("__ast_helper_access__", "__agent_purpose__")
    SKIP_DIR_NAMES = {"__pycache__", "__melder_cache__", "_build_assets"}


def _legacy_statement_spans(node: ast.ClassDef) -> List[Tuple[int, int]]:
    """
    Return 1-based inclusive line spans of the legacy marker assignments.

    Contract:
        Uses `end_lineno` so a parenthesised multi-line value is removed WHOLE.
        Most `__agent_purpose__` assignments span three to six lines; deleting
        only the first would leave dangling string fragments and a syntax error.

    Args:
        node: The class definition being inspected.

    Returns:
        List[Tuple[int, int]]: `(start_line, end_line)` spans to delete.
    """
    spans: List[Tuple[int, int]] = []
    for stmt in node.body:
        name: Optional[str] = None
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            name = stmt.target.id
        elif isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
            name = stmt.targets[0].id
        if name in StripPolicy.LEGACY_ATTRS and stmt.end_lineno is not None:
            spans.append((stmt.lineno, stmt.end_lineno))
    return spans


def _plan_file(path: pathlib.Path) -> Tuple[Optional[str], int, List[str]]:
    """
    Compute the stripped text for one file without writing it.

    Args:
        path: Source file to plan.

    Returns:
        Tuple[Optional[str], int, List[str]]: New text or `None`, the number of
            classes stripped, and any refusals.
    """
    original = path.read_text(encoding="utf-8-sig")
    try:
        tree = ast.parse(original, filename=str(path))
    except SyntaxError as error:
        return None, 0, [f"{path}: unparseable ({error})"]

    lines = original.splitlines()
    refusals: List[str] = []
    delete_spans: List[Tuple[int, int]] = []
    stripped_classes = 0

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        spans = _legacy_statement_spans(node)
        if not spans:
            continue

        docstring = ast.get_docstring(node) or ""
        migrated = (
            StripPolicy.ACCESS_MARKER in docstring
            or StripPolicy.PURPOSE_MARKER in docstring
        )
        if not migrated:
            refusals.append(
                f"{path}:{node.lineno} {node.name}: NOT migrated - run codemod A first"
            )
            continue

        delete_spans.extend(spans)
        stripped_classes += 1

    if not delete_spans:
        return None, 0, refusals

    keep = [
        line
        for index, line in enumerate(lines, start=1)
        if not any(start <= index <= end for start, end in delete_spans)
    ]
    trailing = "\n" if original.endswith("\n") else ""
    return "\n".join(keep) + trailing, stripped_classes, refusals


def main(argv: Optional[List[str]] = None) -> int:
    """
    Run the strip codemod.

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

    stripped = 0
    touched = 0
    all_refusals: List[str] = []

    for path in sorted(scan_root.rglob("*.py")):
        if any(part in StripPolicy.SKIP_DIR_NAMES for part in path.parts):
            continue
        new_text, count, refusals = _plan_file(path)
        all_refusals.extend(refusals)
        if new_text is None or count == 0:
            continue
        stripped += count
        touched += 1
        if args.apply:
            path.write_text(new_text, encoding="utf-8")

    mode = "APPLIED" if args.apply else "DRY RUN"
    print(f"{mode}: stripped {stripped} classes across {touched} files")
    if all_refusals:
        print(f"\nREFUSED {len(all_refusals)} (docstring has no marker):", file=sys.stderr)
        for refusal in all_refusals[:20]:
            print(f"  {refusal}", file=sys.stderr)
        return 1
    if args.apply:
        print(
            "\nNow verify the asset is UNCHANGED - the docstrings already hold every\n"
            "value, so deleting the fallback cannot move it:\n"
            "    python src/melder/_build_assets/_build_asset_runner.py --check"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
