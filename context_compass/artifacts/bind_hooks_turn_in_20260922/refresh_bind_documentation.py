"""Refresh the accepted bind documentation's mechanical fields without running package builders."""

from collections import Counter
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import re
import sys


def main() -> None:
    """Refresh five descriptors, four C1 entries and a preservation receipt.

    Contract:
        Uses the repository extractor/merge functions and preserves authored
        semantics. Source files and package assets are read-only. Original
        document text remains in the named historical before-images.
    """
    root = Path.cwd()
    artifacts = Path(__file__).parent
    tool_path = root / "context_compass/tools/system_documents/python/extract_graph.py"
    spec = importlib.util.spec_from_file_location("bind_closeout_extractor", tool_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("The repository graph extractor could not be loaded.")
    extractor = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = extractor
    spec.loader.exec_module(extractor)
    sources = (
        "melder/aether/conduit/conduit.py",
        "melder/aether/spellbook/spellbook.py",
        "melder/aether/spellbook/bind/bind.py",
        "melder/aether/spellbook/configuration/spellbook_configuration.py",
        "melder/utilities/custom_exceptions/hook_execution_error.py",
    )
    refreshed: list[str] = []
    semantic_notes: dict[str, list[str]] = {}
    for relative in sources:
        source = root / "src" / relative
        descriptor = root / "context_compass/system_docs/graph" / Path(relative).with_suffix(".json")
        previous = json.loads(descriptor.read_text(encoding="utf-8"))
        current = extractor.extract(source, root / "src")
        if current is None:
            raise RuntimeError(f"Cannot parse accepted source: {source}")
        for edge in current["edges_out"]:
            edge["to"] = current["imports"][edge["to_label"]]
        merged, notes = extractor.merge(current, previous)
        if any(not note.startswith(("SEMANTICS_STALE", "UNVERIFIED")) for note in notes):
            raise RuntimeError(f"Unexpected descriptor drift in {relative}: {notes}")
        # Preserve honest stale stamps for unrelated portions of these large
        # classes; this bounded hook promotion is not a whole-class re-audit.
        semantic_notes[relative] = notes
        descriptor.write_text(json.dumps(merged, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        refreshed.append(str(descriptor.relative_to(root)))

    lengths = {"src/" + source: len((root / "src" / source).read_text(encoding="utf-8").splitlines())
               for source in sources[:4]}
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    preservation: list[dict[str, object]] = []
    for name in ("src_architecture.md", "src_components.md"):
        document = root / "context_compass/system_docs" / name
        content = document.read_text(encoding="utf-8")
        for source, length in lengths.items():
            pattern = (r"(- path: `" + re.escape(source) + r"`\n  start_line: 1\n)"
                       r"  end_line: \d+\n  loc: \d+\n  verified_at: [^\n]+")
            content, count = re.subn(
                pattern, lambda match: match[1] + f"  end_line: {length}\n  loc: {length}\n  verified_at: {stamp}",
                content,
            )
            if count != 1:
                raise RuntimeError(f"Expected one measured entry for {source} in {name}; found {count}.")
        document.write_text(content, encoding="utf-8", newline="\n")
        original = artifacts / "canonical_before" / name
        before = Counter(" ".join(line.split()) for line in original.read_text(encoding="utf-8").splitlines()
                         if line.strip())
        after = Counter(" ".join(line.split()) for line in content.splitlines() if line.strip())
        replaced = before - after
        preservation.append({"document": name, "historical_target": str(original.relative_to(root)),
                             "replaced_lines_preserved_in_target": list(replaced.elements())})
    (artifacts / "documentation_receipt.json").write_text(json.dumps({
        "updated_at": stamp, "descriptors": refreshed, "measured_lengths": lengths,
        "preservation": preservation, "retained_semantics_stale_notes": semantic_notes,
    }, indent=2), encoding="utf-8")
    sys.stdout.write("Refreshed five descriptors and four C1 entries per source map; prior text retained.\n")


if __name__ == "__main__":
    main()
