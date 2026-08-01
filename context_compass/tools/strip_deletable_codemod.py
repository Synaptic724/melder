"""
Remove ``__deletable__`` assignments from Python class bodies.

Default mode is dry-run. Use ``--apply`` to write changes.

Examples:
    python codex/context_compass/scripts/strip_deletable_codemod.py src --apply
    python codex/context_compass/scripts/strip_deletable_codemod.py src tests --apply
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

try:
    import libcst as cst
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "This codemod requires libcst. Install it first: pip install libcst"
    ) from exc


TARGET_ATTRIBUTE = "__deletable__"


def _is_target_stmt(stmt: cst.BaseSmallStatement) -> bool:
    if isinstance(stmt, cst.Assign):
        for target in stmt.targets:
            if (
                isinstance(target.target, cst.Name)
                and target.target.value == TARGET_ATTRIBUTE
            ):
                return True
        return False
    if isinstance(stmt, cst.AnnAssign):
        return (
            isinstance(stmt.target, cst.Name)
            and stmt.target.value == TARGET_ATTRIBUTE
        )
    return False


class StripDeletableTransformer(cst.CSTTransformer):
    def __init__(self) -> None:
        self.class_stack: list[str] = []
        self.removed_classes: list[str] = []

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        self.class_stack.append(node.name.value)

    def leave_ClassDef(
        self,
        original_node: cst.ClassDef,
        updated_node: cst.ClassDef,
    ) -> cst.ClassDef:
        qualified_name = ".".join(self.class_stack)
        try:
            new_body, removed_any = self._rewrite_suite(updated_node.body)
            if removed_any:
                self.removed_classes.append(qualified_name)
                return updated_node.with_changes(body=new_body)
            return updated_node
        finally:
            self.class_stack.pop()

    def _rewrite_suite(
        self,
        suite: cst.BaseSuite,
    ) -> tuple[cst.BaseSuite, bool]:
        if isinstance(suite, cst.IndentedBlock):
            body_items: list[cst.BaseStatement] = []
            removed_any = False
            for stmt in suite.body:
                rewritten, removed = self._rewrite_stmt(stmt)
                removed_any = removed_any or removed
                if rewritten is not None:
                    body_items.append(rewritten)
            if not body_items:
                body_items = [cst.SimpleStatementLine(body=[cst.Pass()])]
            return suite.with_changes(body=tuple(body_items)), removed_any

        if isinstance(suite, cst.SimpleStatementSuite):
            kept = [stmt for stmt in suite.body if not _is_target_stmt(stmt)]
            removed_any = len(kept) != len(suite.body)
            if not kept:
                kept = [cst.Pass()]
            return suite.with_changes(body=tuple(kept)), removed_any

        return suite, False

    def _rewrite_stmt(
        self,
        stmt: cst.BaseStatement,
    ) -> tuple[cst.BaseStatement | None, bool]:
        if not isinstance(stmt, cst.SimpleStatementLine):
            return stmt, False

        kept = [small for small in stmt.body if not _is_target_stmt(small)]
        removed_any = len(kept) != len(stmt.body)
        if not kept:
            return None, removed_any
        if removed_any:
            return stmt.with_changes(body=tuple(kept)), True
        return stmt, False


def iter_python_files(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if path.is_file() and path.suffix == ".py":
            yield path
            continue
        if path.is_dir():
            yield from path.rglob("*.py")


def transform_file(path: Path) -> tuple[bool, list[str], str]:
    source = path.read_text(encoding="utf-8-sig")
    module = cst.parse_module(source)
    transformer = StripDeletableTransformer()
    updated = module.visit(transformer)
    changed = updated.code != module.code
    return changed, transformer.removed_classes, updated.code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Remove __deletable__ assignments from Python class bodies."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=[],
        help="Files or directories to scan. Required.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write changes back to disk. Default is dry-run.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print the final summary.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.paths:
        parser.error("at least one file or directory path is required")

    paths = [Path(path).resolve() for path in args.paths]
    files = list(iter_python_files(paths))
    files = [
        path for path in files
        if TARGET_ATTRIBUTE in path.read_text(encoding="utf-8-sig")
    ]

    changed_files = 0
    changed_classes = 0

    for path in files:
        changed, removed_classes, code = transform_file(path)
        if not changed:
            continue

        changed_files += 1
        changed_classes += len(removed_classes)

        if args.apply:
            path.write_text(code, encoding="utf-8", newline="")

        if not args.quiet:
            mode = "APPLY" if args.apply else "DRYRUN"
            print(f"{mode}\t{path}")
            for class_name in removed_classes:
                print(f"  CLASS\t{class_name}")

    remaining = [
        path for path in files
        if TARGET_ATTRIBUTE in path.read_text(encoding="utf-8-sig")
    ]

    if not args.quiet:
        mode = "applied" if args.apply else "would change"
        print(
            f"Summary: {changed_files} file(s) {mode}, "
            f"{changed_classes} class(es) with __deletable__ removed."
        )
        if remaining:
            print("Remaining files still containing __deletable__:")
            for path in remaining:
                print(f"  REMAINING\t{path}")

    if args.apply and remaining:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
