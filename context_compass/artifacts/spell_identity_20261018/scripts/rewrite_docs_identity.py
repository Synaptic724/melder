"""Correct the user docs that teach the retired spell identity rule (melder_0, 2026-10-18; S1's docs sweep).

S1 of EPIC-2026-10-18-spell_identity_is_the_code made a spell_id the SHA256 of the registered object's code, with
nothing from the bind call in it, and S2 put the binding in a manifest with its own hash. Five pages still say a
binding_name or spellframe tells one class apart in two worlds, or that a receiving policy changes a restored
spell's ID: the glossary, the troubleshooting table, the inspection walkthrough, the configuration chapter and the
README's Frame Boundaries section (which the docs site renders as the advanced/worlds chapter). M0-203 named these
files to melder_2, whose S3 holds six other docs/ files.

Usage: python rewrite_docs_identity.py <repository root> [--write] [--diff <path>]

Each edit is an anchored (old, new) pair that must occur exactly once. An anchor is matched with the line ending of
the region it lands in: CRLF first, then LF (README.md mixes both, so each region keeps its own). All-or-nothing;
nothing is written without --write; --diff writes the unified diff of the whole change.
"""
import difflib
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class DocsEdits:
    """The anchored edits, one method per page."""

    def files(self) -> dict[str, list[tuple[str, str]]]:
        """Map each repository-relative path to its edits."""
        return {
            "docs/reference/glossary.md": self.glossary(),
            "docs/reference/troubleshooting.md": self.troubleshooting(),
            "docs/advanced/inspection-walkthrough.md": self.inspection(),
            "docs/intermediate/configuration.md": self.configuration(),
            "README.md": self.readme(),
        }

    def glossary(self) -> list[tuple[str, str]]:
        """The Aetheric frame entry, and a Spell ID entry."""
        frame_old = '''\
   Aetheric frame
      A live world with its own runtime registries, posture, and instance isolation.
      Frame isolation does not make identical binding identities distinct.
'''
        frame_new = '''\
   Aetheric frame
      A live world with its own runtime registries, posture, and instance isolation.
      Frame isolation does not namespace spell identity: a spell ID is the object's code,
      so one class bound in two frames is one spell.
'''
        spell_old = '''\
   Spell
      A bound object's runtime registration metadata, identity, and lifecycle contract.

   SpellContract
'''
        spell_new = '''\
   Spell
      A bound object's runtime registration metadata, identity, and lifecycle contract.

   Spell ID
      The SHA256 of a registered object's code: its methods and constructor, class-level
      values and bases, or an existing object's class and data. Nothing from the bind call
      enters it, so one object registers once; how it is bound has its own binding hash.

   SpellContract
'''
        return [(frame_old, frame_new), (spell_old, spell_new)]

    def troubleshooting(self) -> list[tuple[str, str]]:
        """The world-collision row."""
        old = ("| Identical bindings collide across worlds | Process-wide spell identity; the frame is not part of that "
               "distinction | [World boundaries](../advanced/worlds.md) |\n")
        new = ("| One class is refused in a second world or under a second name | One object is one spell: its spell "
               "ID is its code, unique across the process, with no frame or binding name in it | "
               "[World boundaries](../advanced/worlds.md) |\n")
        return [(old, new)]

    def inspection(self) -> list[tuple[str, str]]:
        """Step 1 follows advanced 02, which now binds a class per world."""
        old = '''\
1. Build two isolated cache worlds with distinct binding identities. Compare the
   instances and verify each world's reuse.
'''
        new = '''\
1. Build two isolated cache worlds, each binding its own cache class at one
   address. Compare the instances and verify each world's reuse.
'''
        return [(old, new)]

    def configuration(self) -> list[tuple[str, str]]:
        """A receiving policy moves the binding hash, never the spell ID."""
        old = '''\
Crystals preserve the resolved order, and replay applies the receiving book's
normal binding policy. A different policy can yield a different content ID.
'''
        new = '''\
Crystals preserve the resolved order, and replay applies the receiving book's
normal binding policy. A different policy keeps the spell ID and changes the
binding hash; the restore report lists that binding under `binding_changes`.
'''
        return [(old, new)]

    def readme(self) -> list[tuple[str, str]]:
        """The Frame Boundaries section: a class per world, and the per-frame regime."""
        old = '''\
Use distinct `binding_name` or `spellframe` values when binding the same class
in both worlds. Spell IDs are unique across the process: an identical binding
fingerprint produces the same ID even in another frame and is refused.
A `unique` spell is a singleton **per frame** — not per process. Two distinct
bindings, two frames, two instances, one interpreter.
'''
        new = '''\
Bind a distinct class in each world — a subclass per tenant is enough. A spell
ID is the SHA256 of the registered object's code (its methods, constructor,
class-level values and bases), with nothing from the bind call in it, and spell
IDs are unique across the process: the same class bound in another frame is the
same spell, and it is refused whatever `binding_name` or `spellframe` it gets.
A `unique` spell is a singleton **per frame** — not per process. Two classes,
two frames, two instances, one interpreter. To register one class in several
worlds instead, turn `process_wide_unique_spell_ids` off in the Aether
configuration before the first frame exists; spell IDs are then unique per frame.
'''
        return [(old, new)]


class DocsRewrite:
    """Apply `DocsEdits` to one repository root, all-or-nothing, each region keeping its own line ending."""

    def __init__(self, root: Path) -> None:
        """
        Args:
            root: The repository root (the folder holding docs/ and README.md).
        """
        self._root = root
        self._staged: dict[str, tuple[bytes, bytes]] = {}

    @staticmethod
    def _apply(rel: str, text: str, number: int, old: str, new: str) -> str:
        """Replace `old` once, matched as CRLF or as LF, writing `new` with the ending that matched."""
        crlf_old = old.replace("\n", "\r\n")
        if text.count(crlf_old) == 1:
            return text.replace(crlf_old, new.replace("\n", "\r\n"))
        if text.count(old) == 1:
            return text.replace(old, new)
        sys.exit(f"ANCHOR {rel} #{number}: {text.count(crlf_old)} CRLF and {text.count(old)} LF occurrences of "
                 f"{old.splitlines()[0][:70]!r}")

    def stage(self) -> None:
        """Apply every edit in memory; exit naming the first anchor that does not occur exactly once."""
        for rel, pairs in DocsEdits().files().items():
            raw = (self._root / rel).read_bytes()
            text = raw.decode("utf-8")
            for number, (old, new) in enumerate(pairs, 1):
                text = self._apply(rel, text, number, old, new)
            self._staged[rel] = (raw, text.encode("utf-8"))

    def diff(self) -> str:
        """The unified diff of every staged file, CRs shown as they are written."""
        chunks: list[str] = []
        for rel, (before, after) in self._staged.items():
            old = before.decode("utf-8").splitlines(keepends=True)
            new = after.decode("utf-8").splitlines(keepends=True)
            chunks.extend(difflib.unified_diff(old, new, fromfile="a/" + rel, tofile="b/" + rel))
        return "".join(chunks).replace("\r\n", "\n")

    def summary(self) -> list[str]:
        """One line per staged file: CRLF and LF line counts before and after."""
        lines: list[str] = []
        for rel, (before, after) in self._staged.items():
            counts = []
            for blob in (before, after):
                crlf = blob.count(b"\r\n")
                counts.append(f"{crlf} CRLF/{blob.count(b'\n') - crlf} LF")
            lines.append(f"{rel}: {counts[0]} -> {counts[1]}")
        return lines

    def write(self, backup: Path) -> None:
        """Write every staged file after checking none changed since staging; keep the originals in `backup`."""
        for rel, (before, _) in self._staged.items():
            if (self._root / rel).read_bytes() != before:
                sys.exit(f"CHANGED {rel}: the file moved since staging; nothing written")
        for rel, (before, _) in self._staged.items():
            target = backup / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(before)
        for rel, (_, after) in self._staged.items():
            (self._root / rel).write_bytes(after)
        for rel, (_, after) in self._staged.items():
            if (self._root / rel).read_bytes() != after:
                sys.exit(f"READBACK {rel}: the written bytes differ; originals in {backup}")


def main() -> None:
    """Stage, report, and write only with --write."""
    if len(sys.argv) < 2:
        sys.exit("usage: rewrite_docs_identity.py <repository root> [--write] [--diff <path>]")
    root = Path(sys.argv[1]).resolve()
    rewrite = DocsRewrite(root)
    rewrite.stage()
    diff_path: Optional[str] = None
    if "--diff" in sys.argv:
        diff_path = sys.argv[sys.argv.index("--diff") + 1]
        Path(diff_path).write_text(rewrite.diff(), encoding="utf-8")
    for line in rewrite.summary():
        print(line)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if "--write" not in sys.argv:
        print("CHECK OK", now, root, "diff:", diff_path)
        return
    backup = Path("/tmp/m0_mq/bak_docs_identity") / now.replace(":", "")
    rewrite.write(backup)
    print("WROTE", len(rewrite.summary()), "files under", root, "originals in", backup)


if __name__ == "__main__":
    main()
