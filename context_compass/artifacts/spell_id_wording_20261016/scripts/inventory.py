"""Inventory every live occurrence of "version id" (any case; space, hyphen; singular or plural) with its context.

Run from the repository root:  python inventory.py <out_dir>
Live trees: src/ (no build-asset payloads or manifests), tests/, the four system documents, the graph descriptors and
the running release note. Code identifiers (`version_id`, `_get_spell_by_version_id`, ...) are listed apart: they are
out of scope (the owner declined a blanket rename). Writes occurrences.txt (one block per line holding the term, with
two lines of context each side) and occurrences.json (one record per line: id, path, line, text, held).
"""
import json
import pathlib
import re
import sys

PROSE = re.compile(r"version[ -]ids?\b", re.IGNORECASE)
IDENT = re.compile(r"[A-Za-z_]*version_ids?[A-Za-z_]*")
HELD = {
    "src/melder/aether/spellbook/spellbook.py",
    "src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py",
    "src/melder/aether/conduit/conduit_ward/conduit_ward.py",
    "src/melder/aether/conduit/conduit.py",
    "src/melder/aether/conduit/meld/meld.py",
    "src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py",
    "src/melder/utilities/custom_exceptions/spellbook_validation_error.py",
    "context_compass/system_docs/src_architecture.md",
    "context_compass/system_docs/src_components.md",
    "context_compass/system_docs/tests_architecture.md",
    "context_compass/system_docs/tests_components.md",
    "release_docs/next_version_release.md",
}


def live_files() -> list:
    """Return the live files to scan, sorted."""
    files = []
    for path in pathlib.Path("src").rglob("*.py"):
        parts = path.parts
        if "__pycache__" in parts or "payloads" in parts or "manifest" in parts:
            continue
        files.append(path)
    files += [p for p in pathlib.Path("tests").rglob("*.py") if "__pycache__" not in p.parts]
    docs = pathlib.Path("context_compass/system_docs")
    files += [docs / name for name in ("src_architecture.md", "src_components.md", "tests_architecture.md",
                                       "tests_components.md")]
    files += sorted((docs / "graph").rglob("*.json"))
    files.append(pathlib.Path("release_docs/next_version_release.md"))
    return sorted(set(files), key=str)


def main() -> None:
    """Write the inventory."""
    out = pathlib.Path(sys.argv[1])
    records, blocks, idents = [], [], {}
    for path in live_files():
        lines = path.read_text(encoding="utf-8").splitlines()
        for number, line in enumerate(lines, 1):
            for match in IDENT.finditer(line):
                idents.setdefault(str(path), []).append(number)
            if not PROSE.search(line):
                continue
            rid = "V%03d" % (len(records) + 1)
            held = str(path) in HELD or str(path).startswith("context_compass/system_docs/graph/")
            records.append({"id": rid, "path": str(path), "line": number, "text": line, "held": held})
            start, end = max(1, number - 2), min(len(lines), number + 2)
            context = "\n".join("%s%5d| %s" % (">" if n == number else " ", n, lines[n - 1])
                                for n in range(start, end + 1))
            blocks.append("[%s] %s:%d%s\n%s" % (rid, path, number, "  (HELD/GRAPH)" if held else "", context))
    (out / "occurrences.txt").write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
    (out / "occurrences.json").write_text(json.dumps(records, indent=1) + "\n", encoding="utf-8")
    (out / "identifiers_out_of_scope.json").write_text(json.dumps(idents, indent=1) + "\n", encoding="utf-8")
    per_file = {}
    for record in records:
        per_file[record["path"]] = per_file.get(record["path"], 0) + 1
    print("lines with the term:", len(records), "files:", len(per_file),
          "held/graph lines:", sum(1 for r in records if r["held"]))
    print("identifier files:", len(idents), "uses:", sum(len(v) for v in idents.values()))


if __name__ == "__main__":
    main()
