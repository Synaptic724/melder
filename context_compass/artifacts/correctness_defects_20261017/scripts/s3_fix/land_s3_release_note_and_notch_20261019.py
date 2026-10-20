"""S3's release-note section and the notch to 0.2.8261 (melder_0, 2026-10-19), with S3's FACT note for the docs,
indexes, graph, release note and notch, the board row and the attention board's notch notice.

The running release note gains the section "Cleaning up a spell takes it out of every contract first" (its example is
probes/probe_release_note_s3.py, run as written: OK on the fixed tree with the GIL off and on; on 0.2.8260 the notch
raises AttributeError) and one Packaging bullet; its header moves to 0.2.8261 and its rebuild line stays for melder_1's
S8 landing, which rebuilds for both (the owner, 2026-10-19). `__version__` is read at the notch and must be 0.2.8260.
All-or-nothing; `--write` flushes.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record


SECTION = '''## Cleaning up a spell takes it out of every contract first

When a lender cleans up a version with `cleanup_spell`, every conduit it shares that version with now lets it go
before it is disposed: a borrower that contracts the version's index with `add_index_to_contract`, and one granted
the version with `add_spell_to_contract`. Until 0.2.8261 the borrower kept its record of the version. An index link
kept a parked version the lender cleaned up, even past the borrower's own `remove_index_from_contract`; a grant kept
the version, parked or active; and a later notch to the same class, staged again, raised `AttributeError` in the
borrower update after the lender had switched, leaving the borrower with no active version:

```python
class Greeter(Protocol):
    def greet(self) -> str: ...


class English:
    def greet(self) -> str:
        return "hello"


class French:
    def greet(self) -> str:
        return "bonjour"


class Banner:
    def __init__(self, greeter: Greeter = md.SpellContract(spellframe=Greeter, binding_name="greeter")) -> None:
        self.text = greeter.greet().upper()


lender_book = md.Spellbook()
borrower_book = md.Spellbook()
english = lender_book.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="many",
                           permissions="create")
borrower_book.bind(spell=Banner, existence="many", permissions="create")
lender = lender_book.conjure(dynamic=True, name="lender")
borrower = borrower_book.conjure(dynamic=True, name="borrower")
lender.link(borrower)
index = lender.get_spell_by_spell_id(english).spell_index
french = lender.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="greeter",
                              existence="many", permissions="create")
borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
assert borrower.meld(spell=Banner).text == "HELLO"

lender.cleanup_spell(spell=lender.get_spell_by_spell_id(french))  # the borrower lets French go as well
french = lender.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="greeter",
                              existence="many", permissions="create")  # staged again: the same spell_id
lender.notch_spell(spell_index=index, spell_id=french)  # raised AttributeError until 0.2.8261
assert borrower.meld(spell=Banner).text == "BONJOUR"
```

- A borrower's meld of a granted version the lender cleaned up raises `KeyError` "[MELD] No spell found with
  spell_id: <spell_id>", as for a version it was never granted; it raised `AttributeError` "... object has no
  attribute '_resolvable'".
- `Spellbook.cleanup_spell` on a conjured Spellbook goes through its root conduit, and `cleanup_spell` through a
  lesser conduit releases the root conduit's contracts: until 0.2.8261 neither reached a borrower, and the
  Spellbook's own call did not tell index-link borrowers when the index went with its last version.
- After such a cleanup the borrower's `remove_index_from_contract` leaves nothing of the lender's versions behind.

What stays the same: what `cleanup_spell` refuses - the active version of an index that holds parked versions -
and a refused cleanup touches no contract; `cleanup_spell` disposes no object a version built; and
`Spellbook.cleanup_and_remove_spell` and a spell's own `cleanup()` release no contract. No public signature changes.

'''

BULLET = '''- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph
  describe the release of a version from every contract before `cleanup_spell` disposes it, and the packaged test
  documents describe the new tests; the code-map extents of `conduit.py`, `spellbook.py` and `conduit_ward.py` are
  remeasured, and their line citations remapped.
'''


class LandS3(Record):
    """The release note, the notch, S3's record and the board."""

    S3 = "tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md"
    NOTE = "../release_docs/next_version_release.md"
    VERSION = "../src/melder/__version__.py"
    RUNS = "artifacts/correctness_defects_20261017/runs/s3_fix"
    SCRIPTS = "artifacts/correctness_defects_20261017/scripts/s3_fix"
    PROBE = "artifacts/correctness_defects_20261017/probes/probe_release_note_s3.py"

    def file_range(self, rel: str) -> str:
        count = len((self.ROOT / rel).read_text(encoding="utf-8").splitlines())
        return f"context_compass/{rel}:1-{count}"

    def staged_lines(self, rel: str, first: str, stop: str) -> str:
        """`<repo path>:a-b` from the line equal to `first` up to the line before `stop` (blank lines trimmed)."""
        lines = self.read(rel).split("\n")
        starts = [i for i, line in enumerate(lines) if line == first]
        if len(starts) != 1:
            sys.exit(f"LINES {rel} {first}: {len(starts)}")
        end = starts[0] + 1
        while end < len(lines) and not lines[end].startswith(stop):
            end += 1
        while lines[end - 1].strip() == "":
            end -= 1
        return f"{rel.replace('../', '')}:{starts[0] + 1}-{end}"

    def notch(self) -> None:
        text = self.read(self.VERSION)
        found = re.findall(r'^__version__ = "([0-9.]+)"$', text, flags=re.M)
        if found != ["0.2.8260"]:
            sys.exit(f"VERSION read at the notch: {found}")
        self.stage(self.VERSION, self.once(text, '__version__ = "0.2.8260"', '__version__ = "0.2.8261"', "notch"))

    def release_note(self) -> None:
        text = self.read(self.NOTE)
        text = self.once(text, "# Melder 0.2.8260\n\n**Unreleased**\n", "# Melder 0.2.8261\n\n**Unreleased**\n",
                         "header")
        text = self.once(text, "\n## Packaging and documentation\n", "\n" + SECTION + "## Packaging and documentation\n",
                         "section")
        last = "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8260.\n"
        if not text.endswith(last):
            sys.exit("REBUILD LINE is not the note's last line")
        text = self.once(text, last, BULLET + last, "packaging bullet")
        self.stage(self.NOTE, text)

    def story(self) -> None:
        section = self.staged_lines(self.NOTE, "## Cleaning up a spell takes it out of every contract first",
                                    "## Packaging and documentation")
        lines = self.read(self.NOTE).split("\n")
        bullet_at = lines.index(BULLET.split("\n")[0])
        bullet = f"release_docs/next_version_release.md:{bullet_at + 1}-{bullet_at + 4}"
        components = self.read("system_docs/src_components.md").split("\n")
        flow = [i for i, line in enumerate(components)
                if line == "### Flow: Conduit.cleanup_spell -> Contracts Released -> Spellbook._dispose_spell"]
        if len(flow) != 1:
            sys.exit(f"FLOW: {len(flow)}")
        flow_end = flow[0] + 1
        while not components[flow_end].startswith("#"):
            flow_end += 1
        while components[flow_end - 1].strip() == "":
            flow_end -= 1
        fact = self.note(self.now, "FACT", [
            "S3's docs, graph, release note and notch are in. System documents (land_s3_docs_20261019.py):",
            "src_architecture gains a first operational invariant (a disposed version leaves every contract first)",
            "and a fixed failure mode, marks the 0.2.8256 invariant's gap fixed, adds the release-first clause to the",
            "0.2.8231 entry and remeasures three code-map extents; src_components carries the Spellbook Core, Conduit",
            "Runtime and ConduitWard contracts and a new flow (Conduit.cleanup_spell -> Contracts Released ->",
            "Spellbook._dispose_spell); tests_components and tests_architecture carry the two test files; nine numeric",
            "citations moved by the edits are remapped (remap_s3_citations.py); all four indexes are regenerated and",
            "--check OK; the bounds recipe flags 2 of 1419 citations, bare file names in an older handoff entry present",
            "at HEAD. Graph: extracted with --strict (0 skipped), prose re-authored for Conduit (31 responsibilities),",
            "Spellbook (29) and ConduitWard (13) (graph_prose_s3.py), Spellbook accepted after its source was read,",
            "assembled and --check OK (593 sections). Conduit and ConduitWard stay SEMANTICS_STALE: they were stale at",
            "HEAD before this lane, and accepting them needs their whole source re-read, which this lane did not do.",
            "Release note: the section \"Cleaning up a spell takes it out of every contract first\" - its example run",
            "as written prints OK on the fixed tree with the GIL off and on, and on 0.2.8260 its notch raises",
            "AttributeError \"... object has no attribute 'spell_index'\" in the borrower fan-out - and one Packaging",
            "bullet; the header reads 0.2.8261 and the rebuild line stays 0.2.8260 for melder_1's S8 landing to set.",
            "Notch: `__version__` read at the notch as 0.2.8260 and set to 0.2.8261; no rebuild (DECISION note of",
            "2026-10-19T11:48:58Z)."],
            [self.doc_block("system_docs/src_architecture.md", "- A disposed version leaves every contract first"),
             self.doc_block("system_docs/src_architecture.md", "- Fixed in 0.2.8261: a lender's `cleanup_spell`"),
             f"context_compass/system_docs/src_components.md:{flow[0] + 1}-{flow_end}",
             self.file_range(f"{self.RUNS}/docs_index_regen.txt"),
             self.file_range(f"{self.RUNS}/docs_citation_bounds.txt"),
             self.file_range(f"{self.RUNS}/graph_extract_0_2_8261.txt"),
             self.file_range(f"{self.RUNS}/graph_prose_0_2_8261.txt"),
             self.file_range(f"{self.RUNS}/graph_accept_0_2_8261.txt"),
             self.file_range(f"{self.RUNS}/graph_assemble_check_0_2_8261.txt"),
             self.file_range(f"{self.SCRIPTS}/land_s3_docs_20261019.py"),
             self.file_range(self.PROBE),
             self.file_range(f"{self.RUNS}/release_note_probe_s3_gil0.txt"),
             self.file_range(f"{self.RUNS}/release_note_probe_s3_gil1.txt"),
             self.file_range(f"{self.RUNS}/release_note_probe_pre_s3_0_2_8260_gil0.txt"),
             section, bullet, "src/melder/__version__.py:12-12"],
            ["S3's change is landed but for the rebuild, which rides melder_1's S8 landing (the owner); the turn-in -",
             "the patch docs archived, the story closed - waits for the owner's word."],
            ["M0-211 hands spellbook.py, conduit.py and conduit_ward.py to melder_1."], "REQUIRED", 9)
        self.append_notes(self.S3, [fact], "s3 fact")
        text = self.read(self.S3)
        text = self.once(
            text,
            "- [ ] Task: the fix with symptom-named regression tests, docs and the notch; the rebuild rides melder_1's S8\n",
            "- [x] Task: the fix with symptom-named regression tests, docs and the notch; the rebuild rides melder_1's S8\n",
            "task")
        text = self.once(
            text,
            "  melder_1's S8 landing, notched above 0.2.8261, rebuilds for both (the owner; DECISION note).\n\n## Artifact Links",
            "  melder_1's S8 landing, notched above 0.2.8261, rebuilds for both (the owner; DECISION note).\n"
            f"- {self.now}: docs, indexes, graph, the release-note section and the notch 0.2.8261 (FACT note).\n"
            "\n## Artifact Links",
            "decision log")
        text = self.once(
            text,
            "  whole tree against 0.2.8260 (MEASURE note of 2026-10-19T12:00:59Z).\n",
            "  whole tree against 0.2.8260 (MEASURE note of 2026-10-19T12:00:59Z). Docs, indexes, graph, the\n"
            f"  release-note section and the notch 0.2.8261 are in (FACT note of {self.now}).\n",
            "state")
        text = self.once(
            text,
            "- Next: (1) the system documents, their indexes, the graph and the release note; (2) the notch to\n"
            "  0.2.8261 with no rebuild - melder_1's S8 landing rebuilds for both (the owner;\n"
            "  DECISION note of 2026-10-19T11:48:58Z); (3) a NOTICE hands spellbook.py and conduit.py to melder_1; turn-in on\n"
            "  the owner's word.\n",
            "- Next: (1) M0-211 hands spellbook.py, conduit.py and conduit_ward.py to melder_1; (2) melder_1's S8\n"
            "  landing rebuilds for both and sets the release note's rebuild line; (3) turn-in on the owner's word.\n",
            "next")
        self.stage(self.S3, text)
        self.set_field(self.S3, "Updated")

    def board(self) -> None:
        text = self.read(self.BOARD)
        rows = re.findall(r"^\| parked_cleanup_contracts \|.*$", text, flags=re.M)
        if len(rows) != 1:
            sys.exit(f"ROW parked_cleanup_contracts: {len(rows)}")
        cells = rows[0].split(" | ")
        cells[6] = ("Hand spellbook.py, conduit.py and conduit_ward.py to melder_1 (M0-211); the rebuild rides S8's "
                    "landing; turn-in on the owner's word.")
        cells[10] = self.now
        text = text.replace(rows[0], " | ".join(cells))
        notice = (
            "### Notch notice (melder_0, 2026-10-19)\n"
            "- melder_0 landed 0.2.8261 (`cleanup_spell` takes a version out of every contract of its Book's root conduit\n"
            "  - index links and version grants - before it disposes it, and the Spellbook's own door goes through the\n"
            "  root conduit; STORY-2026-10-17-parked_cleanup_leaves_borrower_copies). No rebuild, on the owner's word:\n"
            "  melder_1's S8 landing rebuilds for both. Notch above it if you land after.\n")
        text = self.once(text, "### Device VM git hazard (melder_2, 2026-09-26)\n",
                         notice + "### Device VM git hazard (melder_2, 2026-09-26)\n", "notch notice")
        self.stage(self.BOARD, text)

    def run(self) -> None:
        self.notch()
        self.release_note()
        self.story()
        self.board()
        print("S3 FACT", self.note_range(self.S3, f"- DATETIME: {self.now}", "  TYPE: FACT"))


def main() -> None:
    record = LandS3("land_s3_note_notch")
    record.run()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
