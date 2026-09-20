"""Convert published lesson meld targets to verified registered-name strings.

Only argument tokens are rewritten. Local class/function declarations supply
ordinary names; source-reviewed mappings cover instances and generated classes.
Unknown expressions refuse the entire pass. Dry-run is the default.
"""

import argparse
import ast
import hashlib
import json
import sys
import tomllib
from pathlib import Path
from typing import Optional


class MeldNameCodemod:
    """Own a bounded publication-source audit with no retained resource handles.

    Every edit has an exact source span and a source-backed name. Python AST
    comparison rejects any change beyond the planned target replacements.
    """

    REVIEWED_NAMES = {
        "UX_and_AIX_experiences/01_beginner/03_bind_functions_and_instances.py": {
            "prebuilt": "AlreadyBuilt",
        },
        "UX_and_AIX_experiences/02_intermediate/11_permissions_linking_vocabulary.py": {
            "prebuilt": "PublishedConfig",
        },
        "UX_and_AIX_experiences/04_expert/36_an_agent_builds_a_working_system.py": {
            'classes["Tokenizer"]': "Tokenizer",
            'classes["Counter"]': "Counter",
            'classes["Reporter"]': "Reporter",
            "worker_class": "Worker",
        },
    }

    def __init__(self, root: Path) -> None:
        """Keep the resolved checkout root as immutable path data."""
        self.root = root.resolve()

    def files(self) -> list[Path]:
        """Select every Python source/helper in the four published catalog collections."""
        catalog = tomllib.loads((self.root / "docs/catalog.toml").read_text(encoding="utf-8"))
        paths = sorted(path for level in catalog["level"]
                       for path in (self.root / "UX_and_AIX_experiences" / level["directory"]).glob("*.py"))
        if any(not path.resolve().is_relative_to(self.root) for path in paths):
            raise ValueError("A lesson source resolves outside the checkout.")
        return paths

    def registered_name(self, path: Path, expression: str, target: ast.expr,
                        definitions: set[str]) -> str:
        """Resolve a declared target or an explicitly reviewed exceptional binding."""
        names = self.REVIEWED_NAMES.get(path.relative_to(self.root).as_posix(), {})
        if expression in names:
            return names[expression]
        if isinstance(target, ast.Name) and target.id in definitions:
            return target.id
        raise ValueError(f"Unreviewed meld target at {path}:{target.lineno}: {expression}")

    def convert(self, path: Path, raw: bytes) -> tuple[bytes, list[dict]]:
        """Plan exact UTF-8 byte-span edits and prove the resulting AST matches that plan."""
        prefix = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
        body = raw[len(prefix):]
        source = body.decode("utf-8")
        expected = ast.parse(source, filename=str(path))
        definitions = {node.name for node in ast.walk(expected)
                       if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))}
        lines = body.splitlines(keepends=True)
        edits: list[tuple[int, int, bytes]] = []
        records: list[dict] = []
        for node in ast.walk(expected):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "meld" and node.args):
                continue
            target = node.args[0]
            if isinstance(target, ast.Constant) and isinstance(target.value, str):
                continue
            expression = ast.get_source_segment(source, target)
            if expression is None or target.end_lineno is None or target.end_col_offset is None:
                raise ValueError(f"Missing source span for meld target in {path}.")
            name = self.registered_name(path, expression, target, definitions)
            start = sum(len(line) for line in lines[:target.lineno - 1]) + target.col_offset
            end = sum(len(line) for line in lines[:target.end_lineno - 1]) + target.end_col_offset
            replacement = json.dumps(name, ensure_ascii=False).encode("utf-8")
            edits.append((start, end, replacement))
            records.append({"line": target.lineno, "before": expression, "registered_name": name})
            node.args[0] = ast.Constant(value=name)
        changed = body
        for start, end, replacement in sorted(edits, reverse=True):
            changed = changed[:start] + replacement + changed[end:]
        actual = ast.parse(changed.decode("utf-8"), filename=str(path))
        if ast.dump(expected, include_attributes=False) != ast.dump(actual, include_attributes=False):
            raise ValueError(f"Unexpected change beyond planned meld targets: {path}")
        return prefix + changed, sorted(records, key=lambda row: row["line"])

    def run(self, apply: bool, check: bool, report: Optional[Path]) -> int:
        """Audit all files before writes; check mode fails when any target still needs conversion."""
        planned: list[tuple[Path, bytes, bytes]] = []
        inventory: list[dict] = []
        paths = self.files()
        for path in paths:
            original = path.read_bytes()
            changed, records = self.convert(path, original)
            if records:
                planned.append((path, original, changed))
                inventory.append({"path": path.relative_to(self.root).as_posix(), "calls": records,
                                  "before_sha256": hashlib.sha256(original).hexdigest(),
                                  "after_sha256": hashlib.sha256(changed).hexdigest()})
        if apply:
            for path, original, _ in planned:
                if path.read_bytes() != original:
                    raise ValueError(f"Concurrent edit detected; refusing application: {path}")
            for path, _, changed in planned:
                path.write_bytes(changed)
        summary = {"mode": "apply" if apply else "check" if check else "dry-run",
                   "scanned_files": len(paths), "changed_files": len(planned),
                   "target_replacements": sum(len(row["calls"]) for row in inventory),
                   "ast_verification": "passed", "changes": inventory}
        if report is not None:
            report.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        sys.stdout.write(json.dumps({key: value for key, value in summary.items() if key != "changes"}) + "\n")
        return 1 if check and planned else 0


def main() -> int:
    """Expose explicit audit/apply/check modes for the source-reviewed conversion."""
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    return MeldNameCodemod(Path(__file__).resolve().parents[3]).run(args.apply, args.check, args.report)


if __name__ == "__main__":
    raise SystemExit(main())
