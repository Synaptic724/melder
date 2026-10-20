"""melder_0, 2026-10-18: record S1's SpellCodeDigest and S2's BindingManifest, written and probed in the /tmp
working mirror; correct the code-description patch (exact literals, long ints, eager type-parameter parts, container
reads) and the Binding Pipeline and architecture patches (a Spell has no describe()); row the staged sources."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cc_record import Record  # noqa-free: a sibling script, imported by path

STAGED = "artifacts/spell_identity_20261018/staged"
DIGEST = STAGED + "/src/melder/aether/spellbook/bind/spell_code_digest.py"
MANIFEST = STAGED + "/src/melder/aether/spellbook/bind/binding_manifest.py"
RUNS = STAGED + "/runs"


class Pass(Record):
    """This pass's edits."""

    def cite(self, rel: str, a: int, b: int) -> str:
        return f"context_compass/{rel}:{a}-{b}"

    def patches(self) -> None:
        rel = self.PATCHES + "/code_description_patch_spell_code_digest.md"
        text = self.read(rel)
        text = self.once(
            text,
            "   anything else its `repr()` with \" at 0x...\" addresses removed.\n7. `encode(value, owner)`: the first row of"
            " the table below that matches. A container, class, function or object\n   already on the current path encodes"
            " as `cycle:<kind>`.\n",
            "   a number, string or bytes literal, None, Ellipsis or a bool its exact `repr()` (an integer past the\n"
            "   interpreter's decimal conversion limit as `hex:<digits>`); anything else its `repr()` with \" at 0x...\"\n"
            "   addresses removed.\n7. `encode(value, owner)`: the first row of the table below that matches. A container,"
            " class, function or object\n   already on the current path encodes as `cycle:<kind>`. A container is read"
            " through its builtin base type\n   (`tuple.__iter__`, `dict.items`, ...), copied in one call.\n",
            "cdp constants")
        text = self.once(
            text,
            "`<qualified type>:<repr through the builtin base type>` |",
            "`<qualified type>:<repr through the builtin base type>`; an int past the decimal limit `hex:<digits>` |",
            "cdp scalars")
        text = self.once(
            text,
            "| TypeVar, ParamSpec, TypeVarTuple | `typevar:<kind>, <name>, <variance flags>, <encodings of evaluate_bound"
            " / _constraints / _default>` |\n| TypeAliasType | `alias:<name>, <encode(evaluate_value)>` |",
            "| TypeVar, ParamSpec, TypeVarTuple | `typevar:<kind>|<name>|<variance flags>|<bound>|<constraints>|<default>`:"
            " a part given lazily is its evaluate function's encoding (never called), one given eagerly"
            " `const:<encode(the stored value)>`, an absent one `-` |\n| TypeAliasType | `alias:<name>|<value>`, the"
            " value as a TypeVar part |",
            "cdp typing")
        text = self.once(
            text,
            "- Rollback: none needed - a pure computation whose only state is its memo.",
            "- Refined while writing SpellCodeDigest (2026-10-18; S1's DECISION note), every probe verdict unchanged:\n"
            "  literal constants by exact repr (stripping \" at 0x...\" made a literal such as \"listening at 0x1F\"\n"
            "  equal \"listening\"); an int past the decimal conversion limit in hex (`int.__repr__` raises there);\n"
            "  an eagerly given type-parameter or alias part by its stored value (its `_typing._ConstEvaluator`\n"
            "  would reduce to `ref:`, so a bound change would not move the id); containers through their base type.\n"
            "- Rollback: none needed - a pure computation whose only state is its memo.",
            "cdp refined")
        self.stage(rel, text)
        self.set_field(rel, "Updated")
        rel = self.PATCHES + "/component_patch_binding_pipeline.md"
        text = self.read(rel)
        text = self.once(
            text,
            "  public and read-only by contract, `Spell.binding_hash` returns its hash, `Spell.describe()` adds both, and"
            " both\n  survive cleanup like `spell_id` (value data).",
            "  public and read-only by contract and `Spell.binding_hash` returns its hash (a Spell has no `describe()`;\n"
            "  corrected 2026-10-18); both survive cleanup like `spell_id` (value data).",
            "bpp describe")
        text = self.once(text, "  and with the GIL off and on; `describe()`; a bound,",
                         "  and with the GIL off and on; `BindingManifest.describe()`; a bound,", "bpp validation")
        self.stage(rel, text)
        self.set_field(rel, "Updated")
        rel = self.PATCHES + "/architecture_patch.md"
        text = self.read(rel)
        text = self.once(
            text,
            "their SHA256; `Spell.describe`\n  shows both, and both creation-cache tiers",
            "their SHA256, read-only\n  (`BindingManifest.describe()` gives them as plain data), and both creation-cache"
            " tiers",
            "arch describe")
        self.stage(rel, text)
        self.set_field(rel, "Updated")

    def stories(self) -> None:
        text = self.read(self.S2)
        text = self.once(
            text,
            "(Bind builds it, the Spell carries it, `describe` shows\n  it),",
            "(the Spell builds and carries it, its `describe()`\n  gives it as data),",
            "s2 boundary")
        text = self.once(
            text,
            "- The Spell carries the manifest and its hash; `Spell.describe` shows both.",
            "- The Spell carries the manifest and its hash, read-only (`BindingManifest.describe()` gives them as data).",
            "s2 requirement")
        self.stage(self.S2, text)

    def notes(self) -> None:
        now = self.now
        digest = self.read(DIGEST).rstrip("\n").split("\n")
        s1_measure = self.note(now, "MEASURE", [
            "SpellCodeDigest is written from the code-description patch - src/melder/aether/spellbook/bind/",
            "spell_code_digest.py, staged under the epic's artifacts and copied into the /tmp working mirror (0.2.8255",
            "with S9's E1-E7); nothing in the repository's src. The prototype's probes, re-run against it through a",
            "two-line adapter: the 42 cases E01-E34 give the designed verdicts and D1-D10 too, D6 keeping its recorded",
            "limit (two C objects without Python-visible state collide, as under today's repr rule); every id is",
            "byte-identical across hash seeds 1 and 2 and GIL 0 and 1. The corpus: 783 targets of src/melder digest",
            "without error; per target cold (a fresh digest, site roots found each time) median 0.46 ms, p95 1.7 ms;",
            "warm median 0.12 ms, p95 0.47 ms; today's fingerprint median 0.066 ms. A class over pygments'",
            "PythonLexer, named by version under decision B, costs 0.53 ms cold and 0.013 ms warm (2.6-3.2 ms when it",
            "was digested)."], [
            self.cite(DIGEST, 1, len(digest)),
            self.whole(RUNS + "/src_digest_cases_gil0_seed1.txt"),
            self.whole(RUNS + "/src_digest_cases_gil1_seed2.txt"),
            self.whole(RUNS + "/src_digest_design_edges_gil0_seed1.txt"),
            self.whole(RUNS + "/src_digest_corpus_gil0_seed1.txt"),
            self.whole(RUNS + "/src_digest_stability_md5.txt")], [
            "S1's digest is ready for Bind; the probes' cases become its unit tests (red first, against src)."], [
            "BindingManifest and the Spell's manifest (S2), then Bind wired to the digest in the mirror."],
            "REQUIRED", 9)
        s1_decision = self.note(now, "DECISION", [
            "Four refinements of the code-description contract, made while writing SpellCodeDigest and written into",
            "the patch in this pass; every probe verdict is unchanged. (1) A code constant that is a number, string",
            "or bytes literal, None, Ellipsis or a bool is its exact repr: stripping \" at 0x...\" from every constant",
            "made a literal such as \"listening at 0x1F\" equal \"listening\". (2) An int past the interpreter's decimal",
            "conversion limit is written in hex: `int.__repr__` raises ValueError there, and the digest never raises.",
            "(3) A type-parameter or alias part given eagerly (`TypeVar(\"T\", bound=int)`) is `const:` and its stored",
            "value: its evaluator is a `_typing._ConstEvaluator`, which the `ref:` row reduced to its type, so a bound",
            "change did not move the id; a part given lazily (PEP 695 syntax) stays its evaluate function's code,",
            "never called. (4) Containers are read through their builtin base type in one call (`tuple.__iter__`,",
            "`dict.items`), so a subclass's `__iter__` never runs and a concurrent writer never makes a walk raise."], [
            self.cite(DIGEST, 573, 598),
            self.cite(DIGEST, 687, 700),
            self.cite(DIGEST, 702, 738),
            self.cite(DIGEST, 866, 889),
            self.doc_block(self.PATCHES + "/code_description_patch_spell_code_digest.md", "- Refined while writing")], [
            "The patch stays the exact contract of the code that lands; (1) and (3) close two ways a real change",
            "kept its id, (2) a way the digest could raise at bind."], [
            "Unit tests for the four, beside the probes' cases."], "REQUIRED", 8)
        manifest = self.read(MANIFEST).rstrip("\n").split("\n")
        s2_fact = self.note(now, "FACT", [
            "BindingManifest is written from the S2 section of the Binding Pipeline patch and staged with the digest",
            "(src/melder/aether/spellbook/bind/binding_manifest.py; the mirror too): twelve value fields in hash order,",
            "`binding_hash` the SHA256 of \"v1-binding\" and one `<field>=<repr>` line each, `build(...)` from a Spell's",
            "arguments (enums by name, the spellframe as text, the name sequences as tuples, the queue timeout as a",
            "float, so equal settings written differently hash alike), read-only properties, `describe()` and no",
            "cleanup (a value record). The patches said `Spell.describe()` shows both; a Spell has no `describe()`",
            "(spell.py searched), so the Binding Pipeline and architecture patches and this story say: the Spell",
            "carries `binding_manifest` and `binding_hash` read-only, and `BindingManifest.describe()` gives the data."], [
            self.cite(MANIFEST, 1, len(manifest)),
            "src/melder/aether/spellbook/spell.py:1-1972",
            self.doc_block(self.PATCHES + "/component_patch_binding_pipeline.md", "- `Spell.__init__` builds it last")], [
            "S2's Spell edit is the slot, the build call and the `binding_hash` property; no describe method."], [
            "spell.py's manifest in the mirror; then the creation-cache keys."], "REQUIRED", 8)
        self.append_notes(self.S1, [s1_measure, s1_decision], "s1 notes")
        self.append_notes(self.S2, [s2_fact], "s2 notes")

    def handoffs(self) -> None:
        now = self.now
        text = self.read(self.S1)
        text = self.once(
            text,
            "- Done since: the `__annotate_func__` rule written into the code-description patch (2026-10-18T16:32:46Z).\n",
            "- Done since: the `__annotate_func__` rule written into the code-description patch (2026-10-18T16:32:46Z).\n"
            f"- Done since: SpellCodeDigest written and probed in the mirror; four contract refinements in the\n"
            f"  code-description patch (MEASURE and DECISION notes of {now}).\n",
            "s1 handoff")
        self.stage(self.S1, text)
        text = self.read(self.S2)
        text = self.once(
            text,
            "- Next: S2 built with S1 in a /tmp working mirror; the landing pass once spell.py is back.",
            f"- Done since: BindingManifest written; the patches corrected - a Spell has no `describe()` (FACT note of\n"
            f"  {now}).\n- Next: S2 built with S1 in a /tmp working mirror; the landing pass once spell.py is back.",
            "s2 handoff")
        self.stage(self.S2, text)
        text = self.read(self.EPIC)
        text = self.once(
            text,
            "- Next: (1) S1 and S2 built in a /tmp working mirror while S9 lands;",
            f"- Done since: S1's SpellCodeDigest and S2's BindingManifest written and probed in the mirror (the\n"
            f"  stories' notes of {now}).\n- Next: (1) S1 and S2 built in a /tmp working mirror while S9 lands;",
            "epic handoff")
        self.stage(self.EPIC, text)
        for rel in (self.EPIC, self.S1, self.S2):
            self.set_field(rel, "Updated")

    def boards(self) -> None:
        text = self.read(self.ARTIFACTS)
        old = ("record_blast_radius.py (the blast radius recorded); probes/, runs/ and blast_radius/ are rowed under"
               " S1. | 2026-10-18T16:24:12Z | HELPFUL |")
        new = ("record_blast_radius.py (the blast radius recorded); send_m0_198.py (M0-198), write_crystal_record_patch.py"
               " (S2's record patch), cc_record.py (the shared record helper) and record_s1_s2_mirror_build.py (the"
               " digest and the manifest recorded); probes/, runs/, blast_radius/ and staged/ are rowed under S1. | "
               f"{self.now} | HELPFUL |")
        lines = [line for line in text.split("\n") if old in line]
        if len(lines) != 1:
            sys.exit("ANCHOR artifact scripts row")
        text = self.once(text, lines[0], lines[0].replace(old, new), "artifact scripts row")
        anchor = "| tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md | artifacts/spell_identity_20261018/blast_radius/"
        row = ("| tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md | artifacts/spell_identity_20261018/staged/"
               " | implementation_staging | active | delete_on_close | S1's and S2's new src modules (spell_code_digest.py,"
               " binding_manifest.py) as written for the landing, copied into the /tmp working mirror; runs/ holds the"
               " probes re-run against them (cases, design edges, corpus, stability). Deleted once the modules are in"
               f" src/. | {self.now} | REQUIRED |\n")
        if text.count(anchor) != 1:
            sys.exit("ANCHOR artifact blast row")
        text = text.replace(anchor, row + anchor)
        self.stage(self.ARTIFACTS, text)
        for rel, field in ((self.BOARD, None),):
            pass

    def session(self) -> None:
        path = pathlib.Path(__file__).resolve().parent / "cc_record.py"
        source = path.read_text(encoding="utf-8")
        old = '    SESSION_NOTES = ("2026-10-18T16:18:35Z", "2026-10-18T16:24:12Z")\n'
        new = (f'    SESSION_NOTES = ("2026-10-18T16:18:35Z", "2026-10-18T16:24:12Z", "2026-10-18T16:32:46Z",\n'
               f'                     "{self.now}")\n')
        if source.count(old) != 1:
            sys.exit("ANCHOR cc_record session notes")
        path.write_text(source.replace(old, new), encoding="utf-8", newline="\n")
        print("cc_record SESSION_NOTES +16:32:46Z +" + self.now)


def main() -> None:
    record = Pass("s1s2_build")
    record.patches()
    record.stories()
    record.notes()
    record.handoffs()
    record.boards()
    record.resync()
    record.flush()
    record.session()


if __name__ == "__main__":
    main()
