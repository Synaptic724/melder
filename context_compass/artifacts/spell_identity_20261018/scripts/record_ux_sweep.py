"""Record the examples' sweep on S1 and the release-path reading on the identity epic (melder_0, 2026-10-18).

S1 gets a MEASURE note (what S1 and S2 break in UX_and_AIX_experiences/ and why, the older rows, the text that
teaches the retired rule) and a PLAN note (the rewrite and its validation); the epic gets a FACT note (M2-15's
release-after-teardown correction, read whole in the source). S1's and S2's handoffs say where the landing stands.
All-or-nothing; `--write` flushes.
"""
import re
import sys

from cc_record import Record


class RecordUxSweep(Record):
    """The examples' sweep and the release-path reading."""

    RUNS = "artifacts/spell_identity_20261018/runs/ux_examples"
    UX = "UX_and_AIX_experiences"
    LIFECYCLE = "tickets/stories/completed/2026-10-18_managed_spell_lifecycle_map_story.md"
    ARCH = "system_docs/src_architecture.md"
    COMP = "system_docs/src_components.md"
    CREATIONS = "src/melder/aether/conduit/creations"

    def span(self, rel: str, prefix: str) -> str:
        """`rel:a-b` of the def or class in a repository file whose line starts with `prefix`."""
        lines = (self.REPO / rel).read_text(encoding="utf-8").splitlines()
        starts = [i for i, line in enumerate(lines) if line.startswith(prefix)]
        if len(starts) != 1:
            sys.exit(f"SPAN {rel} {prefix}: {len(starts)}")
        start = starts[0]
        indent = len(lines[start]) - len(lines[start].lstrip())
        end = start + 1
        while end < len(lines):
            line = lines[end]
            stripped = line.lstrip()
            if stripped and len(line) - len(stripped) <= indent and \
                    re.match(r"(def |class |@|if __name__|# -{5})", stripped):
                break
            end += 1
        while lines[end - 1].strip() == "":
            end -= 1
        return f"{rel}:{start + 1}-{end}"

    def lines_of(self, rel: str, first: str, last: str) -> str:
        """`rel:a-b` from the one line containing `first` to the next line containing `last`."""
        lines = (self.REPO / rel).read_text(encoding="utf-8").splitlines()
        starts = [i for i, line in enumerate(lines) if first in line]
        if len(starts) != 1:
            sys.exit(f"LINES {rel} {first}: {len(starts)}")
        end = starts[0]
        while last not in lines[end]:
            end += 1
        return f"{rel}:{starts[0] + 1}-{end + 1}"

    def measure_note(self) -> str:
        """The sweep: the 10 new rows, the 7 older ones, the text that teaches the retired rule."""
        ux = self.UX
        return self.note(self.now, "MEASURE", [
            "The examples' harness (UX_and_AIX_experiences/pytest_examples: each lesson's `main()` and the probes,",
            "every process root reset per test) on the /tmp mirror, GIL off, clean crystallizer caches: 17 failed",
            "and 554 passed with S1 and S2, 7 failed and 564 passed at 0.2.8256 - 10 rows are new, each the",
            "one-object rule meeting an example that registers one class twice: lessons 02_frames_as_worlds and",
            "16_ward_policies (advanced), 11_pointing_a_rift_at_your_own_frame and 16_rewiring_a_running_world",
            "(expert), 31_spellbook_config_defined and 37_the_frame_conduit_cloud (intermediate), and the probes",
            "frames_isolate_instances_but_not_identity, with_book_is_lock_only_not_cleanup, config_definition_laws",
            "and a_different_frame_gets_a_different_cloud. Each binds one class in a second frame or Book under",
            "another binding_name - refused at that bind when the first Book is conjured (\"Spell ID collision",
            "detected\"), else at its conjure (\"Conjure refused\") - or twice in one Book; six say why in text S1",
            "retired (\"binding_name keeps the spell_id distinct\", \"a spell_id is a SHA256 over the BIND",
            "FINGERPRINT\"). The 7 older rows: three contract probes of identity premises S1 answers (same name",
            "with other internals; one class rebound by binding_name, by spellframe), expert probe",
            "two_visible_spells_may_not_share_a_name (names, 0.2.8206), intermediate probe",
            "upgrade_to_normal_keeps_creations_and_registers (KeyError), beginner 39_agent_inventory_pattern",
            "(AssertionError) and expert 37_review_agent_bindings' missing VERIFY header. Passing files teach the",
            "retired rule too: beginner 18, 24 and 30, expert 13 and 26, and the examples' AGENTS.md (its DIVERGENCE",
            "FLAG). Expert 09 and 27 failed only in the mirror's first run: its crystallizer cache in the package",
            "directory held earlier runs' files, so FIFO retention evicted the checkpoint 09 had just flushed; with",
            "the cache cleared both pass.",
        ], [
            self.whole(self.RUNS + "/ux_s1s2_gil0_clean.txt"),
            self.whole(self.RUNS + "/ux_base8256_gil0_clean.txt"),
            self.whole(self.RUNS + "/ux_s1s2_gil0_first_run.txt"),
            "src/melder/aether/spellbook/spellbook.py:5790-5810",
            self.span("src/melder/aether/spellbook/spellbook.py", "    def _spell_id_integrity_checker"),
            self.span(f"{ux}/03_advanced/02_frames_as_worlds.py", "def main"),
            self.span(f"{ux}/03_advanced/16_ward_policies.py", "def main"),
            self.span(f"{ux}/04_expert/11_pointing_a_rift_at_your_own_frame.py", "def _postured_frame"),
            self.span(f"{ux}/04_expert/16_rewiring_a_running_world.py", "def _pair"),
            self.span(f"{ux}/02_intermediate/31_spellbook_config_defined.py", "def main"),
            self.span(f"{ux}/02_intermediate/37_the_frame_conduit_cloud.py", "def main"),
            self.span(f"{ux}/pytest_examples/test_advanced_probes.py",
                      "def test_probe_frames_isolate_instances_but_not_identity"),
            self.span(f"{ux}/pytest_examples/test_contract_probes.py",
                      "def test_probe_with_book_is_lock_only_not_cleanup"),
            self.lines_of(f"{ux}/pytest_examples/test_contract_probes.py", "def _make_potato",
                          "disambiguate the name strategy either"),
            self.span(f"{ux}/pytest_examples/test_intermediate_probes.py", "def test_probe_config_definition_laws"),
            self.span(f"{ux}/pytest_examples/test_intermediate_probes.py",
                      "def test_probe_a_different_frame_gets_a_different_cloud"),
            self.lines_of(f"{ux}/01_beginner/18_bootstrap_pattern.py", "melder worlds do not", "MODULE decides"),
            self.lines_of(f"{ux}/01_beginner/24_same_class_many_names.py", "GOAL:", "what works TODAY"),
            self.lines_of(f"{ux}/01_beginner/30_double_bind_outcome.py", "GOAL:", "SURFACE EXERCISED"),
            self.lines_of(f"{ux}/04_expert/13_one_workshop_many_worlds.py", "A distinct binding_name per frame",
                          "would collide"),
            self.lines_of(f"{ux}/04_expert/26_codegen_create_modify_iterate.py", "AND SINGLE RESIDENCE",
                          "you built this before"),
            self.lines_of(f"{ux}/AGENTS.md", "Spell NAMES are unique per book", "are the working patterns"),
        ], [
            "The examples are documentation the docs site renders, so text that teaches the retired rule misleads as",
            "a red row does: the sweep owns the 10 rows, that text and the three identity probes S1 answers; the",
            "other 4 older rows are not identity's (names, the upgrade, the inventory, a header) and are reported.",
        ], [
            "The rewrite script (PLAN note), then a fresh copy of the repository's examples in the mirror, run with",
            "the GIL off and on.",
        ], "REQUIRED", 9)

    def plan_note(self) -> str:
        """The rewrite and its validation."""
        return self.note(self.now, "PLAN", [
            "The examples' rewrite, all-or-nothing in one script (rewrite_ux_examples.py over the repository or a",
            "mirror root), each file kept CRLF as the working tree holds it. (1) Each world or Book binds its own",
            "class: lesson 02's tenants a subclass each at one address (spellframe \"tenant\", binding_name",
            "\"cache\"), so one address melds each world's own singleton; expert 11's four frames a Ledger subclass",
            "each; 16_ward_policies' dynamic world DynamicPayload; 37's second frame OtherLedger; lesson 31's LAW 4",
            "book BareService; the probes _OtherLedger, a local BarePayload and AfterWith. (2) Expert 16's `_pair`",
            "binds nothing: the posture gate refuses link() before any spell is read. (3) The per-frame spell-id",
            "regime, which lets one class live in several frames, is named in lesson 02's text and pinned by a new",
            "advanced probe row with its own reset; a lesson installs no Aether configuration (advanced 07: lessons",
            "share an interpreter). (4) The three identity contract probes assert S1's contract and are renamed for",
            "it: same name with other internals -> two spells; one class rebound by binding_name or spellframe ->",
            "refused at the second bind. (5) Every comment and lesson text that states the retired rule is",
            "rewritten, never deleted; lesson 02's HISTORY gains a paragraph. (6) The 4 rows outside identity stay",
            "as found. Validation: a fresh copy of the repository's examples (melder_2's files included) in the",
            "mirror, clean caches, the GIL off and on - expected those 4 rows red and every other row green; then",
            "the same script on the repository, and the docs sweep (melder_2 told first).",
        ], [
            self.note_range(self.S1, "- DATETIME: " + self.now, "  TYPE: MEASURE"),
            f"{self.UX}/03_advanced/07_aether_config_two_doors.py:43-49",
        ], [
            "The examples teach S1's contract and the 10 rows go green; a reader of lesson 02 learns both ways",
            "to have one shape in several worlds.",
        ], [
            "Write rewrite_ux_examples.py; check it against the mirror's fresh copy, apply, run.",
        ], "REQUIRED", 8)

    def release_note(self) -> str:
        """The epic's FACT note: the release paths after a root's teardown."""
        c = self.CREATIONS
        return self.note(self.now, "FACT", [
            "M2-15's point (2) holds, read whole: `Creations.cleanup` unregisters its managed pools from",
            "`ReleaseManagedSpell` (`_unregister_managed_quantities`) before it cleans them, and `unregister` drops",
            "a class whose last pool goes (`_drop_pool`). So after a root's teardown `ReleaseManagedSpell().release`",
            "finds no pool for the object's class and `_resolve_pool` raises ValueError \"<Class> is not a managed",
            "spell class in any live root: bind it with existence=Existence.managed_spell_quantity, or its root was",
            "torn down.\" - unless another live root pools the class, whose pool then takes the object (one pool and",
            "no filter is that pool's `put_back`, which trusts the object). The torn-down RuntimeError (\"The pool of",
            "managed spell '<name>' was torn down with its root conduit; the object is yours to dispose.\") is",
            "`put_back` on a cleaned pool: a `ManagedSpellLease` released after the teardown (it holds its pool), or",
            "a registry release that read the pool before the store unregistered it. src_architecture's failure mode",
            "and src_components' Managed Spell Pools failure modes give the RuntimeError for any release after",
            "teardown; this docs pass corrects both. No code changes: routing by class through live roots is the",
            "0.2.8244 design.",
        ], [
            self.span(f"{c}/creations.py", "    def cleanup"),
            self.span(f"{c}/creations.py", "    def _unregister_managed_quantities"),
            self.span(f"{c}/release_managed_spell.py", "    def unregister"),
            self.span(f"{c}/release_managed_spell.py", "    def release(self, obj"),
            self.span(f"{c}/release_managed_spell.py", "    def _resolve_pool"),
            self.span(f"{c}/release_managed_spell.py", "    def _drop_pool"),
            self.span(f"{c}/managed_spell_quantity.py", "    def put_back"),
            self.span(f"{c}/managed_spell_quantity.py", "    def _torn_down_error"),
            self.span(f"{c}/managed_spell_lease.py", "    def release(self) -> None"),
            self.doc_block(self.ARCH, "- `ReleaseManagedSpell().release(obj)` raises ValueError"),
            self.doc_block(self.COMP, "- RuntimeError \"The pool of managed spell '<name>' was torn down with its root"),
            self.whole(self.LIFECYCLE),
        ], [
            "Two documentation corrections in the source follow-ups of this pass; melder_2 hears it with the",
            "rebuild NOTICE.",
        ], [
            "The examples' rewrite (S1's PLAN note).",
        ], "REQUIRED", 8)

    def handoffs(self) -> None:
        """S1's and S2's handoffs: where the landing stands."""
        text = self.read(self.S1)
        text = self.once(text,
                         "- Next: the landing pass with S2 - src and tests into the repository, docs, the notches (read at\n"
                         "  landing, above 0.2.8256), the release note, the rebuild last.\n",
                         "- Done since: S1 and S2 applied to the repository (FACT note of 2026-10-18T20:03:20Z) and committed\n"
                         "  by the owner (5e3800c7a); the source system documents promoted; the build parity measured and\n"
                         "  the standard-library RISK recorded (notes of 2026-10-18T21:51:31Z).\n"
                         f"- Done since: the examples swept - 10 rows S1 breaks, 7 older, the text teaching the retired\n"
                         f"  rule - and the rewrite planned (MEASURE and PLAN notes of {self.now}).\n"
                         "- Next: the examples rewritten and run (GIL off and on), the tests system documents and the\n"
                         "  source follow-ups, the docs sweep, the graph, the notches, the release note, the closure, the\n"
                         "  rebuild last.\n",
                         "s1 handoff")
        self.stage(self.S1, text)
        text = self.read(self.S2)
        text = self.once(text,
                         "- Next: the landing pass with S1 - src and tests into the repository, docs, notches, the rebuild last.\n",
                         "- Done since: applied to the repository with S1 and committed by the owner (5e3800c7a); promoted\n"
                         "  into the source system documents (S1's FACT note of 2026-10-18T21:51:31Z).\n"
                         "- Next: with S1 - the examples rewritten, the tests system documents, the graph, the notches, the\n"
                         "  release note, the closure, the rebuild last.\n",
                         "s2 handoff")
        self.stage(self.S2, text)

    def run(self) -> None:
        """Stage every edit."""
        self.append_notes(self.S1, [self.measure_note()], "s1 measure")
        self.append_notes(self.S1, [self.plan_note()], "s1 plan")
        self.append_notes(self.EPIC, [self.release_note()], "epic note")
        self.handoffs()
        self.set_field(self.S1, "Updated")
        self.set_field(self.S2, "Updated")
        self.set_field(self.EPIC, "Updated")


def main() -> None:
    record = RecordUxSweep("ux_sweep")
    record.run()
    record.resync()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
