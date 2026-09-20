"""Apply only reviewed Melder keyword migrations, preserving every other source byte."""

import argparse
import ast
import hashlib
import json
import sys
from pathlib import Path


def plan_file(root: Path, entry: dict) -> tuple[Path, bytes, bytes, list[dict]]:
    """Validate recorded calls and return a byte-preserving, AST-checked edit plan.

    Args:
        root: Repository root, containing the authorized benchmark directory.
        entry: Reviewed inventory row with exact call locations and expressions.

    Returns:
        Target path, original bytes, patched bytes and the auditable keyword edits.

    Raises:
        ValueError: If a path escapes scope or any recorded call/token has changed.
    """
    path = (root / entry["path"]).resolve()
    if not path.is_relative_to((root / "benchmarks/testing_other_di").resolve()):
        raise ValueError(f"Out-of-scope path: {path}")
    original = path.read_bytes()
    prefix = b"\xef\xbb\xbf" if original.startswith(b"\xef\xbb\xbf") else b""
    body = original[len(prefix):]
    lines = body.splitlines(keepends=True)
    tree = ast.parse(body.decode("utf-8"), filename=str(path))
    expected = {call["line"]: call for group in entry["groups"] for call in group["calls"]}
    found: set[int] = set()
    edits: list[tuple[int, bytes, bytes]] = []
    records: list[dict] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or node.lineno not in expected:
            continue
        record = expected[node.lineno]
        if ast.unparse(node.func) != record["call"]:
            continue
        keyword = next((item for item in node.keywords if item.arg == "spell"), None)
        if keyword is None or ast.unparse(keyword.value) != record["argument"]:
            raise ValueError(f"Recorded selector changed: {path}:{node.lineno}")
        if any(item.arg == "spell_id" for item in node.keywords):
            raise ValueError(f"Conflicting selector: {path}:{node.lineno}")
        found.add(node.lineno)
        migrations = [(keyword, "spell_id")]
        legacy_override = next((item for item in node.keywords if item.arg == "spell_override"), None)
        if legacy_override is not None:
            if path.name not in {"run_codegen_benchmark_deltas.py", "test_overrides_all.py"}:
                raise ValueError(f"Unreviewed override migration: {path}:{node.lineno}")
            if any(item.arg == "override" for item in node.keywords):
                raise ValueError(f"Conflicting override: {path}:{node.lineno}")
            migrations.append((legacy_override, "override"))
        for item, replacement in migrations:
            offset = sum(map(len, lines[:item.lineno - 1])) + item.col_offset
            old = item.arg.encode("ascii")
            if body[offset:offset + len(old)] != old:
                raise ValueError(f"Keyword offset mismatch: {path}:{item.lineno}")
            edits.append((offset, old, replacement.encode("ascii")))
            records.append({"line": item.lineno, "before": item.arg, "after": replacement})
            item.arg = replacement
    if found != set(expected):
        raise ValueError(f"Missing recorded calls in {path}: {set(expected) - found}")
    patched = body
    for offset, old, new in sorted(edits, reverse=True):
        patched = patched[:offset] + new + patched[offset + len(old):]
    actual = ast.parse(patched.decode("utf-8"), filename=str(path))
    if ast.dump(actual, include_attributes=False) != ast.dump(tree, include_attributes=False):
        raise ValueError(f"Unexpected syntax change in {path}")
    return path, original, prefix + patched, records


def main() -> None:
    """Dry-run by default; write only a completely validated and unchanged input plan."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    artifact = Path(__file__).resolve().parent
    root = artifact.parents[2]
    inventory = json.loads((artifact / "call_inventory.json").read_text(encoding="utf-8"))
    plans = [plan_file(root, entry) for entry in inventory]
    for path, original, _patched, _records in plans:
        if path.read_bytes() != original:
            raise ValueError(f"Concurrent edit detected: {path}")
    report = {
        "applied": args.apply,
        "files": [
            {
                "path": path.relative_to(root).as_posix(),
                "before_sha256": hashlib.sha256(original).hexdigest(),
                "after_sha256": hashlib.sha256(patched).hexdigest(),
                "changes": records,
            }
            for path, original, patched, records in plans
        ],
    }
    if args.apply:
        for path, _original, patched, _records in plans:
            path.write_bytes(patched)
    report_name = "codemod_applied.json" if args.apply else "codemod_dry_run.json"
    (artifact / report_name).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    selectors = sum(item["before"] == "spell" for _p, _o, _a, rows in plans for item in rows)
    overrides = sum(item["before"] == "spell_override" for _p, _o, _a, rows in plans for item in rows)
    sys.stdout.write(
        f'{"Applied" if args.apply else "Validated"}: {selectors} ID selectors and '
        f'{overrides} override keywords in {len(plans)} files. Other bytes and AST preserved.\n'
    )


if __name__ == "__main__":
    main()
