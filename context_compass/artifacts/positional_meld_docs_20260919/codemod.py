"""Replace only leading meld(spell=...) arguments in public documentation inputs.

Dry-run is the default. Python files must retain exactly the same AST after
normalizing the approved argument spelling and matching documentation strings.
Original bytes, line endings, argument values and unrelated keywords survive.
"""

import argparse
import ast
import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Optional


class PositionalMeldNormalizer(ast.NodeTransformer):
    """Normalize the one approved call/documentation change for AST comparison.

    Only a leading spell keyword on a meld call with no positional arguments
    moves into the first positional slot. Any other keyword arrangement refuses
    the automated change instead of reordering expression evaluation.
    """

    PATTERN = re.compile(r"(?P<opening>\bmeld\s*\(\s*)spell[ \t]*=(?!=)[ \t]*")

    def visit_Call(self, node: ast.Call) -> ast.Call:
        """Normalize a supported call or reject a spell argument needing manual review."""
        self.generic_visit(node)
        is_meld = ((isinstance(node.func, ast.Attribute) and node.func.attr == "meld")
                   or (isinstance(node.func, ast.Name) and node.func.id == "meld"))
        if is_meld and any(keyword.arg == "spell" for keyword in node.keywords):
            if node.args or node.keywords[0].arg != "spell":
                raise ValueError(f"Non-leading meld spell keyword requires review at line {node.lineno}.")
            node.args.append(node.keywords.pop(0).value)
        return node

    def visit_Constant(self, node: ast.Constant) -> ast.Constant:
        """Apply the same spelling change to docstrings, narrated code and codegen strings."""
        if isinstance(node.value, str):
            node.value = self.PATTERN.sub(r"\g<opening>", node.value)
        return node


class PositionalMeldCodemod:
    """Audit explicitly published inputs and apply only verified byte-preserving edits.

    Paths and source snapshots are owned as values; no open files or processes
    survive a method call. Test-only probes and generated outputs are excluded.
    """

    def __init__(self, root: Path) -> None:
        """Resolve the checkout once; all candidates must remain below that root."""
        self.root = root.resolve()

    def candidates(self) -> list[Path]:
        """Select README, guides, architecture prose, catalog lessons/helpers and package quickstart."""
        paths = {self.root / "README.md", self.root / "CONTRIBUTING.md",
                 self.root / "src/melder/__init__.py"}
        for directory in ("docs", "architecture_and_design"):
            for path in (self.root / directory).rglob("*"):
                relative = path.relative_to(self.root / directory)
                if (path.suffix in (".md", ".rst")
                        and not any(part.startswith(("_", ".")) for part in relative.parts)):
                    paths.add(path)
        catalog = tomllib.loads((self.root / "docs/catalog.toml").read_text(encoding="utf-8"))
        for level in catalog["level"]:
            paths.update((self.root / "UX_and_AIX_experiences" / level["directory"]).glob("*.py"))
        for path in paths:
            if not path.resolve().is_relative_to(self.root) or not path.is_file():
                raise ValueError(f"Missing or escaping publication input: {path}")
        return sorted(paths)

    @staticmethod
    def verify_python(path: Path, original: str, changed: str) -> None:
        """Require valid Python and AST equivalence after the exact approved normalization."""
        before = ast.parse(original.lstrip("\ufeff"), filename=str(path))
        after = ast.parse(changed.lstrip("\ufeff"), filename=str(path))
        expected = PositionalMeldNormalizer().visit(before)
        if ast.dump(expected, include_attributes=False) != ast.dump(after, include_attributes=False):
            raise ValueError(f"Change is not limited to approved meld argument spelling: {path}")

    def run(self, apply: bool, check: bool, report: Optional[Path]) -> int:
        """Audit every input before writes, record exact changes, and fail check mode on leftovers."""
        planned: list[tuple[Path, bytes, bytes]] = []
        inventory: list[dict] = []
        candidates = self.candidates()
        for path in candidates:
            original_bytes = path.read_bytes()
            original = original_bytes.decode("utf-8")
            changed, count = PositionalMeldNormalizer.PATTERN.subn(r"\g<opening>", original)
            if path.suffix == ".py":
                self.verify_python(path, original, changed)
            if not count:
                continue
            changed_bytes = changed.encode("utf-8")
            inventory.append({
                "path": path.relative_to(self.root).as_posix(), "replacements": count,
                "before_sha256": hashlib.sha256(original_bytes).hexdigest(),
                "after_sha256": hashlib.sha256(changed_bytes).hexdigest(),
                "lines": [original.count("\n", 0, match.start()) + 1
                          for match in PositionalMeldNormalizer.PATTERN.finditer(original)],
            })
            planned.append((path, original_bytes, changed_bytes))
        if apply:
            for path, original_bytes, _ in planned:
                if path.read_bytes() != original_bytes:
                    raise ValueError(f"Concurrent source edit; refusing application: {path}")
            for path, _, changed_bytes in planned:
                path.write_bytes(changed_bytes)
        payload = {"mode": "apply" if apply else "check" if check else "dry-run",
                   "scanned_files": len(candidates), "changed_files": len(inventory),
                   "replacements": sum(row["replacements"] for row in inventory),
                   "ast_equivalence": "passed", "changes": inventory}
        if report is not None:
            report.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        sys.stdout.write(json.dumps({key: value for key, value in payload.items() if key != "changes"}) + "\n")
        return 1 if check and planned else 0


def main() -> int:
    """Parse the explicit mode; default to a read-only audit rooted at this checkout."""
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    return PositionalMeldCodemod(Path(__file__).resolve().parents[3]).run(
        args.apply, args.check, args.report,
    )


if __name__ == "__main__":
    raise SystemExit(main())
