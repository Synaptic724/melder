"""Record S1's DECISION to retire test_bind.py's tests of the removed `Bind.sha256_profile` onto their successors
(melder_0, 2026-10-18). One all-or-nothing pass."""
import sys

from cc_record import Record


class RecordBindRetirement(Record):
    MAP = "artifacts/spell_identity_20261018/blast_radius/whole_tree_s1s2/retired_sha256_profile_tests.md"
    TEST_BIND = "tests/unit/melder/spellbook/bind/test_bind.py"
    SESSION_NOTES = Record.SESSION_NOTES + ("2026-10-18T17:51:07Z", "2026-10-18T18:08:26Z", "2026-10-18T18:40:11Z",
                                            "2026-10-18T18:44:16Z")

    def s1(self) -> None:
        ranges = ("365-399", "638-734", "936-966", "1004-1017", "1193-1204", "1269-1282", "1425-1456", "1605-1660",
                  "1715-1728", "1764-1826")
        note = self.note(self.now, "DECISION", [
            "test_bind.py's 44 test functions of `Bind.sha256_profile` (47 cases), read whole, test a function S1",
            "removes. 43 are retired onto the successors that carry their property now (the map names one per",
            "test); the non-bool `resolvable` check (4 cases) moves to public `Bind.bind`, refused before the",
            "target is examined; the inspector test is rewritten - `Bind.spell_id_inspector` equals",
            "`SpellCodeDigest().spell_id`, the same on every call, with no binding profile built. Three successor",
            "cases are added to test_spell_code_digest.py where none existed: methods defined in another order",
            "keep the spell_id, a parameter's kind moves it, and non-ASCII identifiers digest stably. Five of the",
            "retired tests pinned what the owner's design reverses (annotation values and parameter annotations,",
            "the dataclass and decorated flags, the origin file); their successors assert the opposite. Section",
            "comments left without tests are kept and say where their tests went. The owner was told (chat).",
        ], [self.whole(self.MAP)] + [f"{self.TEST_BIND}:{r}" for r in ranges], [
            "test_bind.py's 48 failures close and every property they pinned stays under test, on the digest or",
            "the manifest; the edit list is the batch `bind` of tests_apply_s1_s2.py.",
        ], [
            "tests_edits_bind.py: check, apply to the mirror, run test_bind.py and the digest's tests (GIL off).",
        ], "REQUIRED", 9)
        self.append_notes(self.S1, [note], "s1 decision")
        self.set_field(self.S1, "Updated")


def main() -> None:
    record = RecordBindRetirement("bind_retirement")
    record.s1()
    record.resync()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
