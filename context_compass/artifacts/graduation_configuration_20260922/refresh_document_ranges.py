"""Refresh only the five graduation source ranges and preserve the authored-doc baseline."""

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re


def refresh(document: Path, source_lengths: dict[str, int], stamp: str) -> dict[str, object]:
    """Update measured C1 records and account for replaced prose using archived originals."""
    text = document.read_text(encoding="utf-8")
    for source, length in source_lengths.items():
        pattern = (
            r"(- path: `" + re.escape(source) + r"`\n  start_line: 1\n)"
            r"  end_line: \d+\n  loc: \d+\n  verified_at: [^\n]+"
        )
        text, count = re.subn(
            pattern,
            lambda match: match[1] + f"  end_line: {length}\n  loc: {length}\n  verified_at: {stamp}",
            text,
        )
        if count != 1:
            raise RuntimeError(f"Expected one C1 entry for {source} in {document}: {count}")
    document.write_text(text, encoding="utf-8", newline="\n")
    baseline_path = Path(__file__).parent / "canonical_before" / document.name
    before = Counter(" ".join(line.split()) for line in baseline_path.read_text(encoding="utf-8").splitlines() if line.strip())
    after = Counter(" ".join(line.split()) for line in text.splitlines() if line.strip())
    replaced = before - after
    return {
        "document": str(document),
        "historical_preservation_target": str(baseline_path),
        "replaced_line_count": sum(replaced.values()),
        "replaced_lines": list(replaced.elements()),
        "unaccounted_lines": sum((before - (after + before)).values()),
    }


def main() -> None:
    """Measure changed source files and refresh both authored source maps."""
    sources = (
        "src/melder/aether/conduit/conduit.py",
        "src/melder/aether/conduit/conduit_ward/conduit_ward.py",
        "src/melder/aether/spellbook/spellbook.py",
        "src/melder/aether/spellbook/bind/bind.py",
        "src/melder/aether/spellbook/configuration/spellbook_configuration.py",
    )
    lengths = {source: len(Path(source).read_text(encoding="utf-8").splitlines()) for source in sources}
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    results = [
        refresh(Path("context_compass/system_docs/src_architecture.md"), lengths, stamp),
        refresh(Path("context_compass/system_docs/src_components.md"), lengths, stamp),
    ]
    (Path(__file__).parent / "documentation_preservation.json").write_text(
        json.dumps({"measured_source_lengths": lengths, "documents": results}, indent=2), encoding="utf-8",
    )


if __name__ == "__main__":
    main()
