"""Refresh only S2 source descriptors using the canonical extractor and authored merge."""

import json
import sys
from pathlib import Path


def main() -> None:
    """Retain authored semantics and regenerate mechanical fields for the four edited source files."""
    root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(root))
    from context_compass.tools.system_documents.python.extract_graph import (
        extract,
        merge,
    )

    paths = (
        "melder/aether/spellbook/bind/bind.py",
        "melder/aether/spellbook/spell.py",
        "melder/aether/spellbook/spellbook.py",
        "melder/aether/conduit/conduit.py",
    )
    for relative in paths:
        descriptor_path = root / "context_compass/system_docs/graph" / Path(relative).with_suffix(".json")
        previous = json.loads(descriptor_path.read_text(encoding="utf-8"))
        current = extract(root / "src" / relative, root / "src")
        if current is None:
            raise RuntimeError(f"Cannot parse {relative}; canonical descriptor unchanged.")
        # All four edited classes inherit only the imported concrete Cleanable.
        # Refuse another shape rather than guessing interface identity without a full extraction.
        for edge in current["edges_out"]:
            target = current["imports"][edge["to_label"]]
            if target != "melder.utilities.general_base.cleanable.Cleanable":
                raise RuntimeError(f"Unexpected base {target}; use the complete extractor.")
            edge["to"] = target
        result, notes = merge(current, previous)
        descriptor_path.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(relative)
        for note in notes:
            print(f"  {note}")


if __name__ == "__main__":
    main()
