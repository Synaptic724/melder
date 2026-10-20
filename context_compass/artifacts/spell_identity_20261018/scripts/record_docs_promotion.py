"""Record the src docs promotion, the build parity and the standard-library RISK on S1 (melder_0, 2026-10-18).

Three notes on STORY-2026-10-18-spell_id_hashes_the_object_code: a FACT (S1 and S2 promoted into src_architecture
and src_components, committed by the owner in 5e3800c7a), a MEASURE (the spell_id across 3.14.7's builds, GIL modes
and -O, with the cause of the -O differences) and a RISK (a standard-library function held by a class is digested by
its code). All-or-nothing; `--write` flushes.
"""
import sys

from cc_record import Record


class RecordDocsPromotion(Record):
    """The S1 notes of the docs promotion and the build parity."""

    A = "artifacts/spell_identity_20261018"
    ARCH = "system_docs/src_architecture.md"
    COMP = "system_docs/src_components.md"
    SESSION_NOTES = Record.SESSION_NOTES + (
        "2026-10-18T17:51:07Z", "2026-10-18T18:08:26Z", "2026-10-18T18:40:11Z", "2026-10-18T18:44:16Z",
        "2026-10-18T18:44:20Z", "2026-10-18T18:48:19Z", "2026-10-18T19:11:29Z", "2026-10-18T19:17:19Z",
        "2026-10-18T19:59:24Z", "2026-10-18T20:03:20Z",
    )

    def promotion_note(self) -> str:
        """The FACT note: the source documents carry S1 and S2."""
        return self.note(self.now, "FACT", [
            "S1 and S2 are promoted into the source system documents, all-or-nothing (land_docs_arch.py and",
            "land_docs_comp.py over docs_common.py; remap_s1s2_citations.py remapped the numeric citations into the",
            "changed files line by line from 0.2.8256). src_architecture: the glossary (spell_id, binding manifest),",
            "the boundary list, the guardrail's bind-guard count (630), the bind sequence, a new operational",
            "invariant (the 0.2.8254 entry marked superseded in part), a Breaking failure mode, the capability",
            "diagram, the code map (the changed files remeasured, the two modules added), the sources and the",
            "handoff. src_components: the Binding Pipeline's identity entry, Spellbook Core (generation 23, the",
            "one-object refusals, `inspect_spell`'s exact stage 3), the Crystallizer (record 4.3.0, the restore's",
            "`binding_changes`), Spell Examination Profiles, the bind flow, two subcomponents, the code map, the",
            "inventory, the sources and the handoff. Both indexes were regenerated and `--check` reads them current",
            "now. The owner committed the source, the tests and these documents in 5e3800c7a (0.2.8256 was",
            "dd98c0a59); `__version__` is still 0.2.8256, so the notches remain.",
        ], [
            self.whole(self.A + "/scripts/land_docs_arch.py"),
            self.whole(self.A + "/scripts/land_docs_comp.py"),
            self.whole(self.A + "/scripts/docs_common.py"),
            self.whole(self.A + "/scripts/remap_s1s2_citations.py"),
            self.doc_block(self.ARCH, "- A spell_id is the object's code; its binding is a manifest"),
            self.doc_block(self.ARCH, "2026-10-18 spell identity is the code (0.2.8257-0.2.8258;"),
            self.doc_block(self.COMP, "Spell identity and the binding manifest (2026-10-18, 0.2.8257-0.2.8258;"),
            self.doc_block(self.COMP, "2026-10-18 spell identity is the code (0.2.8257-0.2.8258;"),
        ], [
            "The source half of the docs is done; the tests half, the decision-B lookup rules and the build parity",
            "follow in this pass.",
        ], [
            "The tests system documents (tests_components, tests_architecture) and the source follow-ups.",
        ], "REQUIRED", 8)

    def parity_note(self) -> str:
        """The MEASURE note: one spell_id across the builds and GIL modes; what -O changes and why."""
        return self.note(self.now, "MEASURE", [
            "A spell_id is the same on CPython 3.14.7's free-threaded build with the GIL off and on and on its GIL",
            "build: probe_spell_id_build_parity.py digests 788 targets (every class and plain function of",
            "src/melder's importable modules, `_build_assets` aside, and four user-like classes), each build",
            "reports the cache tag cpython-314, and the three outputs are byte-identical (sha256",
            "a4b971ede29a1629e7a1c083f9df4959297cbd8d787df979d99a4e92fc0ea77d). Under -O 8 of the 788 differ, and",
            "their unhashed encodings show why (probe_o_namedtuple_encoding.py, the hash step replaced by the text it",
            "hashes): `Nexus.__new__` holds an `assert`, which -O removes; the seven others are every",
            "`typing.NamedTuple` class in the corpus, whose `__orig_bases__` holds the standard library's",
            "`NamedTuple` function, encoded by its code - its `__dict__` holds `__mro_entries__`,",
            "`typing._namedtuple_mro_entries`, whose `assert NamedTuple in bases` -O removes, so its instructions",
            "and name table differ. Whether two 3.14 patch releases give one spell_id is UNKNOWN: the cache tag",
            "names the minor only, so they agree exactly when they compile the same instructions for the code the",
            "digest reads, standard-library functions held by a class included.",
        ], [
            self.whole(self.A + "/probes/probe_spell_id_build_parity.py"),
            self.whole(self.A + "/runs/build_parity/ft_gil0.txt"),
            self.whole(self.A + "/runs/build_parity/ft_gil1.txt"),
            self.whole(self.A + "/runs/build_parity/gil_build.txt"),
            self.whole(self.A + "/runs/build_parity/ft_gil0_O.txt"),
            self.whole(self.A + "/runs/build_parity/diff_ft_gil0_O.txt"),
            self.whole(self.A + "/probes/probe_o_namedtuple_encoding.py"),
            self.whole(self.A + "/runs/build_parity/o_encoding_diff.txt"),
            f"context_compass/{self.A}/runs/build_parity/o_encoding_plain_gil0.txt:110-116",
            "src/melder/nexus/nexus.py:156-185",
            "src/melder/aether/spellbook/bind/spell_code_digest.py:602-641",
        ], [
            "Ids are portable across one release's builds and GIL modes; -O is an input wherever the code the",
            "digest reads holds an assert, and so is the standard library's code wherever a class holds one of",
            "its functions (RISK below).",
        ], [
            "The parity, the -O rule and the patch-release UNKNOWN into src_architecture (the identity invariant",
            "and the Unknowns); the RISK to the owner.",
        ], "REQUIRED", 9)

    def stdlib_risk_note(self) -> str:
        """The RISK note: a standard-library function held by a class is digested by its code."""
        return self.note(self.now, "RISK", [
            "A class whose namespace holds a standard-library function - directly, or inside a value such as the",
            "`__orig_bases__` of a `typing.NamedTuple` or `typing.TypedDict` class (each holds the function",
            "`NamedTuple` or `TypedDict`) - has a spell_id that reads that function's code: `SpellCodeDigest._encode`",
            "digests every plain function but an installed third-party one, while it names a standard-library",
            "class. So the spell_id of such a class moves under -O when that code asserts (measured: the seven",
            "NamedTuple classes) and would move with a patch release that changes that code (UNKNOWN whether any",
            "3.14 release does), the class itself unchanged. It is the approved contract (the code-description",
            "patch: functions by code), not a slip of the landing. Naming a standard-library function as a",
            "standard-library class is named (`fn:<qualified>`; the minor is already in the cache tag) would make",
            "those ids follow the class alone, moving each such class's spell_id once. The owner's call, not in",
            "this landing.",
        ], [
            "src/melder/aether/spellbook/bind/spell_code_digest.py:602-641",
            "src/melder/aether/spellbook/bind/spell_code_digest.py:318-355",
            f"context_compass/{self.A}/runs/build_parity/o_encoding_plain_gil0.txt:110-116",
            "src/melder/utilities/ai_native_support_tools/system_document_view.py:83-83",
            "src/melder/utilities/helpers/class_surface_ast_describer.py:74-74",
        ], [
            "A NamedTuple or TypedDict class's spell_id - and a cache keyed by it - follows Python's standard",
            "library: an upgrade within 3.14 that touches that code would make such a spell new to Melder (a",
            "cold cache, a restore mapping its id), never a wrong replay. No other effect is known.",
        ], [
            "Tell the owner with the landing report; a follow-up task under the identity epic if he wants it named.",
        ], "REQUIRED", 8)

    def s1(self) -> None:
        """Append the three notes to S1 and stamp it."""
        self.append_notes(self.S1, [self.promotion_note(), self.parity_note(), self.stdlib_risk_note()],
                          "s1 docs promotion")
        self.set_field(self.S1, "Updated")


def main() -> None:
    record = RecordDocsPromotion("docs_promotion")
    record.s1()
    record.resync()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
