"""S1 and S2's notches and running release-note entry (melder_0, 2026-10-18).

`__version__` 0.2.8256 -> 0.2.8258 (S1 takes 0.2.8257, S2 0.2.8258), the running note's header and rebuild line, a
Breaking section for S1 and a section for S2 before `## Packaging and documentation`, the packaging bullets (the
bind-guard count updated in place, the system documents, the examples and docs) placed above melder_2's chapter
bullet so that bullet stays directly above the rebuild line (M2-19), and the attention board's notch notice. Then the
tickets: S1's FACT note (the graph and the notch), S2's (its notch), the handoffs. All-or-nothing; `--write`
flushes.
"""
import sys
import textwrap
from typing import List

from docs_common import DocsRecord


def para(text: str, first: str = "", rest: str = "") -> str:
    lines = textwrap.wrap(text, width=116 - len(rest), break_long_words=False, break_on_hyphens=False)
    out = [first + lines[0]] + [rest + line for line in lines[1:]]
    for line in out:
        if len(line) > 120:
            sys.exit(f"WIDTH {line}")
    return "\n".join(out)


class NotchAndNote(DocsRecord):
    """The notch, the release note, the board notice and the ticket record."""

    VERSION = "src/melder/__version__.py"
    NOTE = "release_docs/next_version_release.md"

    def __init__(self, label: str) -> None:
        super().__init__(label)
        self.repo_staged = {}

    def repo_read(self, rel: str) -> str:
        return self.repo_staged.get(rel) or (self.REPO / rel).read_text(encoding="utf-8")

    def repo_once(self, rel: str, old: str, new: str, label: str) -> None:
        text = self.repo_read(rel)
        if text.count(old) != 1:
            sys.exit(f"ANCHOR {label}: {text.count(old)}")
        self.repo_staged[rel] = text.replace(old, new)

    def sections(self) -> str:
        s1: List[str] = ["## A spell_id is the SHA256 of the object's code, and one object is one spell", ""]
        s1.append(para(
            "**Breaking change:** every spell_id moves once. A spell_id is now the SHA256 of the registered object's "
            "code - its methods' and constructor's instructions and the constants they load, its class-level values, "
            "its base classes outside the standard library and, for an existing object, its data - and of nothing "
            "from the `bind` call: the spellframe, binding name, existence, disposal methods, `resolvable` and the "
            "managed settings are the spell's binding (next section). Docstrings, comments and line numbers never "
            "move it; any change to the code does, a renamed local variable included. Installed third-party code is "
            "named by its distribution and version instead of being read, so upgrading a library moves the spell_id "
            "of a class built over it. The same code is the same spell_id in every process, hash seed and GIL mode."))
        s1.append("")
        s1.append(para(
            "One object is one spell. Registering an object a second time is refused - under another binding name, "
            "existence or spellframe, in a second Spellbook of the frame (under process-wide spell ids, the default), "
            "or staged again with `bind_inactive`: `bind` and `bind_inactive` raise RuntimeError \"Spell ID collision "
            "detected: this object is already registered as spell_id <id>. ...\", whose text names the rule and the "
            "remedies, and `conjure` refuses a second Spellbook's registration of it. To upgrade: share the spell "
            "already registered instead of binding it twice (meld it, or contract it to another conduit); to change "
            "how it is bound, `cleanup_spell` it and bind it again; to keep two versions of a class, edit it - a new "
            "spell_id - and stage it with `bind_inactive`, then notch. An edited class staged that way is now a new "
            "version even when only a method body changed (it was refused as a collision). Under per-frame spell ids "
            "a class can still be bound once in each frame."))
        s1.append("")
        s1.append(para(
            "Also changed: `Bind.spell_id_inspector(spell)` takes the target alone (the binding keywords it took raise "
            "TypeError), and `Spellbook.inspect_spell` finds a registered object by its code. Creation-cache bundles "
            "are cold once. A Crystallizer record made before this release restores through `bind`, which gives each "
            "spell its new spell_id and maps the old ones; a record that holds one object twice fails at its second "
            "replayed bind."))
        s1.append("")
        s1.append(para(
            "Known limits: `-O` changes the spell_id of code that holds an `assert`, including every "
            "`typing.NamedTuple` class, whose base reads a standard-library function that asserts; whether two patch "
            "releases of one Python version give one spell_id is not yet measured; a namespace package that several "
            "distributions install is named by the first in sorted order; a bind costs 37-55 us more (conjure and "
            "melds are unchanged); a definition rebound under another slotted existence can meet the removed "
            "definition's object at its first meld; and a version alone in an index that `remove_from_spell_index` "
            "minted is missed by the collision check until that index is registered with its frame."))
        s2: List[str] = ["", "## A spell's binding is a manifest with its own hash", ""]
        s2.append(para(
            "`Spell.binding_manifest` and `Spell.binding_hash` (read-only) are how a spell is kept - its spellframe "
            "and kind, address, existence, ordered disposal methods, `resolvable` and managed settings - and the "
            "SHA256 of that record; `BindingManifest.describe()` gives both as plain data. Both creation-cache tiers "
            "key on the binding hash beside the spell_id, so a spell bound another way never replays a plan built "
            "for its old binding. The SpellCrystal records the binding hash (record 4.3.0; 4.x records still read), "
            "and a restore reports each binding it rebuilt differently - under another receiving Spellbook's "
            "disposal order, say - in `RestoreReport.describe()[\"binding_changes\"]`, where the spell_id used to move."))
        return "\n".join(s1 + s2) + "\n\n"

    def packaging(self) -> str:
        bullets = [
            "The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph "
            "describe spell identity: the spell_id as the SHA256 of the object's code (what counts, installed code "
            "named by version, the parity across builds and GIL modes, `-O`), the binding manifest and its hash in "
            "both cache tiers and the record, and the one-object refusals; the packaged test documents describe the "
            "new tests; the code-map extents of the changed files are remeasured. The managed release's failure is "
            "corrected there: `ReleaseManagedSpell().release(obj)` after the root's teardown raises the not-managed "
            "ValueError, and the torn-down RuntimeError comes from a lease or a release that raced the teardown.",
            "The examples teach one object, one spell: the lessons and probes in `UX_and_AIX_experiences/` that bound "
            "one class twice bind a class of their own or a version of it. The glossary defines a Spell ID and says "
            "a frame does not namespace it; the troubleshooting row, the inspection walkthrough, the configuration "
            "guide and the README's \"Frame Boundaries\" section follow, and the configuration guide's disposal "
            "sentence is corrected (every declared method runs; the failures are raised together).",
        ]
        return "\n".join(para(b, "- ", "  ") for b in bullets) + "\n"

    def stage_all(self) -> None:
        self.repo_once(self.VERSION, '__version__ = "0.2.8256"', '__version__ = "0.2.8258"', "version")
        self.repo_once(self.NOTE, "# Melder 0.2.8256\n", "# Melder 0.2.8258\n", "note header")
        self.repo_once(self.NOTE, "\n## Packaging and documentation\n", "\n" + self.sections() +
                       "## Packaging and documentation\n", "note sections")
        self.repo_once(self.NOTE,
                       "- The internal-bind guard manifest holds 628 entries at 0.2.8244 (622 at 0.2.8227): "
                       "`HolderDisposalEntry`, the\n",
                       "- The internal-bind guard manifest holds 630 entries at 0.2.8257 (628 at 0.2.8244, 622 at "
                       "0.2.8227): `SpellCodeDigest` and\n  `BindingManifest` joined at 0.2.8257; `HolderDisposalEntry`, "
                       "the\n", "bind guard")
        self.repo_once(self.NOTE, "- The documentation site's intermediate level gains a chapter on managed spell pools\n",
                       self.packaging() + "- The documentation site's intermediate level gains a chapter on managed "
                       "spell pools\n", "packaging bullets")
        self.repo_once(self.NOTE, "rebuilt for 0.2.8256.", "rebuilt for 0.2.8258.", "rebuild line")
        text = self.repo_read(self.NOTE).split("\n")
        rebuild = [i for i, line in enumerate(text) if line.startswith("- Agent documentation metadata")]
        if len(rebuild) != 1 or "intermediate lessons back it" not in "\n".join(text[rebuild[0] - 6:rebuild[0]]):
            sys.exit("melder_2's bullet is not directly above the rebuild line")
        board = self.read(self.BOARD)
        anchor = ("  STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool, part A). Notch above it if you "
                  "land after.\n")
        notice = para("melder_0 landed 0.2.8257 (a spell_id is the SHA256 of the registered object's code, nothing from "
                      "the bind call; one object is one spell; S1 of EPIC-2026-10-18-spell_identity_is_the_code) and "
                      "0.2.8258 (the binding manifest and its hash in both cache tiers and the SpellCrystal, record "
                      "4.3.0, creation cache generation 23; S2). Notch above it if you land after.", "- ", "  ")
        self.stage(self.BOARD, self.once(board, anchor, anchor + notice + "\n", "board notice"))


def main() -> None:
    record = NotchAndNote("notch_s1s2")
    record.stage_all()
    for rel, text in record.repo_staged.items():
        if "\r" in text:
            sys.exit(f"CR {rel}")
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.repo_staged), sorted(record.staged))
        return
    for rel, text in record.repo_staged.items():
        (record.REPO / rel).write_text(text, encoding="utf-8", newline="\n")
        print("wrote", rel)
    record.flush()


if __name__ == "__main__":
    main()
