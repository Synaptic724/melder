"""
Re-date this task's two dated entries to the UTC day they landed (2026-10-19) and re-wrap them
(TASK-2026-10-18-document_root_teardown_cleans_only_what_it_holds).

The edits landed at 2026-10-19T00:09Z (UTC, the repository's clock), right below melder_1's 2026-10-19 entries, so
the Operational Invariants entry and the two Context / Handoff Summary entries carry 2026-10-19 and keep the ruling's
own date (2026-10-18). Only text this task wrote is touched: each old block is the exact text apply_root_teardown_docs.py
inserted. Refuses unless each document's hash equals its index's; regenerate both indexes afterwards.

Run from the repository root:
    python context_compass/artifacts/root_teardown_docs_20261018/scripts/redate_root_teardown_entries.py
"""
import hashlib
import importlib.util
import re
import textwrap
from pathlib import Path

LANE = Path("context_compass/artifacts/root_teardown_docs_20261018")
DOCS = Path("context_compass/system_docs")
WIDTH = 116


def load_apply_module():
    """Load the apply script, whose edit lists hold the exact blocks this task inserted."""
    spec = importlib.util.spec_from_file_location("apply_root_teardown_docs", LANE / "scripts/apply_root_teardown_docs.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_consistent(doc: Path) -> str:
    """Return the document's text when its hash and line count equal its index's; else refuse."""
    raw = doc.read_bytes()
    index = doc.with_name(doc.stem + "_index.md").read_text(encoding="utf-8")
    want_lines = int(re.search(r"\| line_count \| (\d+) \|", index).group(1))
    want_digest = re.search(r"\| content_sha256 \| `([0-9a-f]{64})` \|", index).group(1)
    text = raw.decode("utf-8")
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if (len(lines), hashlib.sha256(raw).hexdigest()) != (want_lines, want_digest):
        raise SystemExit(f"{doc}: differs from its index; another writer may be mid-pass. Nothing written.")
    return text


def rewrap(paragraph: str, first: str, rest: str) -> str:
    """Wrap one paragraph at WIDTH with the given indents, never splitting words or hyphenated tokens."""
    return "\n".join(textwrap.wrap(paragraph, width=WIDTH, initial_indent=first, subsequent_indent=rest,
                                   break_long_words=False, break_on_hyphens=False)) + "\n"


def redate_invariant(block: str) -> str:
    """Re-date and re-wrap the Operational Invariants entry, keeping its EVIDENCE lines as they are."""
    body, evidence = block.split("  EVIDENCE: ", 1)
    paragraph = " ".join(line.strip() for line in body.strip("\n").split("\n"))
    assert paragraph.startswith("- ")
    paragraph = paragraph[2:].replace("(2026-10-18; the owner's rule in chat, ", "(2026-10-19; the owner's rule, chat "
                                      "2026-10-18: ", 1)
    assert "(2026-10-19; the owner's rule, chat 2026-10-18: " in paragraph
    return rewrap(paragraph, "- ", "  ") + "  EVIDENCE: " + evidence


def redate_handoff(block: str) -> str:
    """Re-date and re-wrap a Context / Handoff Summary entry (its trailing blank line kept)."""
    paragraph = " ".join(line.strip() for line in block.strip("\n").split("\n"))
    assert paragraph.startswith("2026-10-18 ")
    paragraph = "2026-10-19 " + paragraph[len("2026-10-18 "):]
    paragraph = paragraph.replace("(documentation only; the owner's rule, in chat)",
                                  "(documentation only; the owner's rule, in chat on 2026-10-18)", 1)
    assert "in chat on 2026-10-18)" in paragraph
    return rewrap(paragraph, "", "") + "\n"


def main() -> None:
    """Swap the three blocks for their re-dated versions in both documents, or refuse with nothing written."""
    module = load_apply_module()
    arch_invariant = module.ARCH_EDITS[2][2]
    arch_handoff = module.ARCH_EDITS[6][2]
    comp_handoff = module.COMP_EDITS[4][2]
    plans = []
    for name, swaps in (("src_architecture.md", [(arch_invariant, redate_invariant(arch_invariant)),
                                                  (arch_handoff, redate_handoff(arch_handoff))]),
                        ("src_components.md", [(comp_handoff, redate_handoff(comp_handoff))])):
        doc = DOCS / name
        text = check_consistent(doc)
        for old, new in swaps:
            if text.count(old) != 1:
                raise SystemExit(f"{doc}: block must occur once, found {text.count(old)}. Nothing written.")
            for line in new.split("\n"):
                if len(line) > 120:
                    raise SystemExit(f"{doc}: line over 120 characters: {line[:60]!r}")
            text = text.replace(old, new)
        plans.append((doc, text))
    for doc, text in plans:
        doc.write_text(text, encoding="utf-8", newline="")
        print(f"re-dated: {doc}")


if __name__ == "__main__":
    main()
