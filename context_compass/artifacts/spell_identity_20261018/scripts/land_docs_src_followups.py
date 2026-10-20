"""S1's source follow-ups into src_architecture and src_components (melder_0, 2026-10-18; documentation only).

src_architecture: the identity invariant records the build parity and the -O rule, the Unknowns gain the
patch-release question, and the managed release's failure mode is corrected (a release after the root's teardown
raises the not-managed ValueError; the torn-down RuntimeError comes from the pool through a lease or a release that
resolved it first). src_components: the Binding Pipeline gains decision B's lookup rule (installed third-party code
named by distribution version) and the Managed Spell Pools failure mode gets the same correction. Both handoffs say
so. One all-or-nothing pass; `--write` flushes and regenerates both indexes.
"""
import subprocess
import sys

from docs_common import DocsRecord


class SrcFollowUps(DocsRecord):
    """The two source documents' follow-ups."""

    def edit(self, rel: str, old: str, new: str, label: str) -> None:
        self.stage(rel, self.once(self.read(rel), old, new, label))

    def architecture(self) -> None:
        unknown = self.wrap(
            "UNKNOWN: whether two patch releases of one Python minor give a class one spell_id. The digest reads "
            "instruction streams, constant and name tables and, for a class that holds one, a standard-library "
            "function's code, and the interpreter's cache tag names the minor only (cpython-314), so two patch releases "
            "agree exactly when they compile the same instructions for the code the digest reads. Measured on one "
            "release: 3.14.7's free-threaded build with the GIL off and on and its GIL build agree byte for byte over "
            "788 targets (every class and plain function of `src/melder`'s importable modules and four user-like "
            "classes), and -O moves 8 of them (code that asserts). Why it matters: a creation cache or a record keyed "
            "by a spell_id goes cold, or a restore maps every id, when a patch release changes the compiled code. "
            "Where to investigate: `src/melder/aether/spellbook/bind/spell_code_digest.py:SpellCodeDigest._code_digest` "
            "with the same targets digested on two patch releases. Current status: uninvestigated (one patch release "
            "installed).", "- ", "  ")
        self.edit(self.ARCH, "  `STORY-2026-02-13-mutation-research-runtime-wiring`).\n\n## System Context (C4)\n",
                  "  `STORY-2026-02-13-mutation-research-runtime-wiring`).\n\n" + unknown + "\n\n## System Context (C4)\n",
                  "arch unknown")
        parity = self.wrap(
            "Parity: one release's builds and GIL modes give one spell_id (3.14.7's free-threaded build with the GIL off "
            "and on and its GIL build: 788 targets byte-identical); -O is an input wherever the code the digest reads "
            "holds an `assert` - `Nexus.__new__`, and the standard library's `typing._namedtuple_mro_entries`, which "
            "every `typing.NamedTuple` class holds through `__orig_bases__` - and two patch releases are UNKNOWN (see "
            "Unknowns).", "  ", "  ")
        self.edit(self.ARCH,
                  "conjure and melds unchanged.\n  Open: a rebind under another slotted existence keeps its spell_id,",
                  "conjure and melds unchanged.\n" + parity + "\n  Open: a rebind under another slotted existence keeps "
                  "its spell_id,", "arch parity")
        old = ("  matches; and TypeError for a filter of the wrong type (0.2.8244). A release after the pool's root was "
               "torn down\n"
               "  raises RuntimeError \"The pool of managed spell '<name>' was torn down with its root conduit; the "
               "object is yours to\n"
               "  dispose.\" A reset that raises destroys the object (its disposal methods and recorded children run), "
               "frees its\n")
        new = ("  matches; and TypeError for a filter of the wrong type (0.2.8244). A release after the pool's root was "
               "torn down\n"
               "  raises the not-managed ValueError, because the root's store unregisters its pools before it cleans "
               "them, so no\n"
               "  live root pools the class (corrected 2026-10-18: this said RuntimeError). RuntimeError \"The pool of "
               "managed spell\n"
               "  '<name>' was torn down with its root conduit; the object is yours to dispose.\" comes from the pool "
               "itself: a\n"
               "  `ManagedSpellLease.release` after the teardown, or a release that resolved the pool before the "
               "teardown cleaned\n"
               "  it. A reset that raises destroys the object (its disposal methods and recorded children run), frees "
               "its\n")
        self.edit(self.ARCH, old, new, "arch release failure")
        self.edit(self.ARCH,
                  "  EVIDENCE: `src/melder/aether/conduit/creations/release_managed_spell.py:ReleaseManagedSpell._resolve_pool` "
                  "and\n  `src/melder/aether/conduit/creations/managed_spell_quantity.py:ManagedSpellQuantity.put_back`.\n"
                  "- Bind refuses a managed binding before any registry change (0.2.8242)",
                  "  EVIDENCE: `src/melder/aether/conduit/creations/release_managed_spell.py:ReleaseManagedSpell._resolve_pool`,\n"
                  "  `src/melder/aether/conduit/creations/managed_spell_quantity.py:ManagedSpellQuantity.put_back`,\n"
                  "  `src/melder/aether/conduit/creations/creations.py:Creations.cleanup` and\n"
                  "  `src/melder/aether/conduit/creations/managed_spell_lease.py:ManagedSpellLease.release`.\n"
                  "- Bind refuses a managed binding before any registry change (0.2.8242)", "arch release evidence")
        handoff = self.wrap(
            "2026-10-18 follow-ups to the identity landing (documentation only): the identity invariant records the "
            "build parity and the -O rule; the Unknowns gain the patch-release question; the managed release's failure "
            "mode is corrected - a `ReleaseManagedSpell` release after the root's teardown raises the not-managed "
            "ValueError, because the store unregisters its pools first, and the torn-down RuntimeError comes from the "
            "pool through a lease or a release that resolved it before the teardown. Checked against "
            "`Creations.cleanup`, `ReleaseManagedSpell._resolve_pool`, `ManagedSpellQuantity.put_back` and "
            "`ManagedSpellLease.release`.", "", "")
        self.edit(self.ARCH, "## Context / Handoff Summary\n\n", "## Context / Handoff Summary\n\n" + handoff + "\n\n",
                  "arch handoff")

    def components(self) -> None:
        rule = self.wrap(
            "Installed third-party code (decision B, 2026-10-18, 0.2.8257): the digest names, never digests, a class or "
            "plain function whose module is installed third-party - not standard library (its top-level name in "
            "`sys.stdlib_module_names`, or `builtins`), loaded in `sys.modules` with a `__file__` under one of the "
            "interpreter's site-packages roots (`sysconfig`'s purelib and platlib, `site.getsitepackages()` and "
            "`site.getusersitepackages()`) - as `<qualified name> <distribution>==<version>`: `importlib.metadata."
            "version` of the top-level name, else the first distribution in sorted order that `packages_distributions()` "
            "maps it to, else `?==?`; an object of such a class is its type, that version and its repr. A module that "
            "is not loaded, or has no file, is application code and is digested; so is an editable install of the "
            "project, whose files are not under a site-packages root. An upgrade of an installed distribution "
            "therefore moves the spell_id of every class over its code, and a namespace package that several "
            "distributions install is named by the first in sorted order. The third-party verdict is memoized per "
            "module name and the version per top-level name, in the digest instance (one per Bind; "
            "`Bind.spell_id_inspector` builds a fresh one per call).", "", "")
        evidence = ("EVIDENCE: `src/melder/aether/spellbook/bind/spell_code_digest.py:SpellCodeDigest._is_third_party_module`,\n"
                    "`SpellCodeDigest._discover_site_roots`, `SpellCodeDigest._named`, `SpellCodeDigest._version` and\n"
                    "`SpellCodeDigest._external`.")
        self.edit(self.COMP,
                  "Spell.binding_manifest`, `Spell.binding_hash`.\n\nManaged options (2026-10-15, 0.2.8242):",
                  "Spell.binding_manifest`, `Spell.binding_hash`.\n\n" + rule + "\n" + evidence +
                  "\n\nManaged options (2026-10-15, 0.2.8242):", "comp decision B")
        self.edit(self.COMP,
                  "- RuntimeError \"The pool of managed spell '<name>' was torn down with its root conduit; ...\" from a "
                  "release, a\n  reserve or an adopt after teardown (a woken queue waiter included).\n",
                  "- RuntimeError \"The pool of managed spell '<name>' was torn down with its root conduit; ...\" from the "
                  "pool's\n  put_back, reserve or adopt after teardown - a `ManagedSpellLease.release` kept past it, a "
                  "release that resolved\n  the pool before the teardown cleaned it, or a woken queue waiter. A "
                  "`ReleaseManagedSpell().release(obj)` after the\n  teardown raises the not-managed ValueError instead: "
                  "the root's store unregisters its pools before it cleans\n  them (corrected 2026-10-18: this named a "
                  "release among the RuntimeError's sources).\n", "comp release failure")
        handoff = self.wrap(
            "2026-10-18 follow-ups to the identity landing (documentation only): the Binding Pipeline records decision "
            "B's lookup rule - what counts as installed third-party code, how it is named by distribution version, "
            "and what an editable install, an upgrade and a namespace package do to a spell_id; the Managed Spell "
            "Pools failure mode is corrected - a `ReleaseManagedSpell` release after the root's teardown raises the "
            "not-managed ValueError, and the torn-down RuntimeError comes from the pool through a lease or a release "
            "that resolved it before the teardown.", "", "")
        self.edit(self.COMP, "## Context / Handoff Summary\n\n", "## Context / Handoff Summary\n\n" + handoff + "\n\n",
                  "comp handoff")


def main() -> None:
    record = SrcFollowUps("src_followups")
    record.architecture()
    record.components()
    for rel in (record.ARCH, record.COMP):
        if "\r" in record.read(rel):
            sys.exit(f"CR in {rel}")
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()
    for rel in (record.ARCH, record.COMP):
        subprocess.run([sys.executable, str(record.ROOT / "tools/system_documents/index_document.py"), "--doc",
                        str(record.ROOT / rel)], check=True)


if __name__ == "__main__":
    main()
