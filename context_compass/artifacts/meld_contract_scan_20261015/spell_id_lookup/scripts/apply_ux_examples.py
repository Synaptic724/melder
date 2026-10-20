"""
UX examples for fix #1 (owner, 2026-10-17: "update it all"): the renamed spell_id lookups.

Usage: python apply_ux_examples.py <root> <since_version> <verified_date> [--check]

1. In the ten examples that call them: `find_spell_by_id` -> `find_spell_by_spell_id` and `get_spell_by_id` ->
   `get_spell_by_spell_id` (whole words; a rename of a method reference, nothing else).
2. Experts 17 and 26 taught, and asserted, the old answer - a parked spell_id answered with the index's ACTIVE
   member. Exact-once anchors (on the text after step 1) make the smallest correction that keeps each lesson true:
   the lookup answers the version the spell_id names, and expert 26 shows the staged version is still parked by the
   index's selection instead. Expert 17's VERIFY line takes the date of the run that re-verified it.
`04_expert/_concept_map.txt` is a dated record (its 2026-08-03 retraction quotes the old answer) and is left as
written. Line endings are kept; a file with mixed endings is refused. Nothing is written when an anchor misses, or
with --check.
"""
import pathlib
import re
import sys

FILES = (
    "UX_and_AIX_experiences/02_intermediate/06_spell_metadata_kwargs.py",
    "UX_and_AIX_experiences/02_intermediate/13_spell_ids_and_lookup.py",
    "UX_and_AIX_experiences/02_intermediate/40_bind_lifecycle_hooks.py",
    "UX_and_AIX_experiences/04_expert/17_notch_swapping_a_live_object.py",
    "UX_and_AIX_experiences/04_expert/23_branching_the_record_and_joining_back.py",
    "UX_and_AIX_experiences/04_expert/26_codegen_create_modify_iterate.py",
    "UX_and_AIX_experiences/04_expert/28_the_record_crosses_as_a_json_string.py",
    "UX_and_AIX_experiences/04_expert/29_reading_your_own_recorded_code.py",
    "UX_and_AIX_experiences/04_expert/31_organising_lanes_after_the_fact.py",
    "UX_and_AIX_experiences/04_expert/37_review_agent_bindings.py",
)
FIND = re.compile(r"\bfind_spell_by_id\b")
GET = re.compile(r"\bget_spell_by_id\b")

EXPERT_17 = "UX_and_AIX_experiences/04_expert/17_notch_swapping_a_live_object.py"
EXPERT_26 = "UX_and_AIX_experiences/04_expert/26_codegen_create_modify_iterate.py"

MANUAL = {
    EXPERT_17: [
        (
            "      NAME THE VERSION BY ITS SPELL_ID. Every public spell_id->object\n"
            "      lookup (`get_spell_by_spell_id`, `find_spell_by_spell_id`) resolves any\n"
            "      lineage spell_id to the spell AS IT EXISTS NOW - the currently\n"
            "      ACTIVE member - which is documented and correct for what those\n"
            "      verbs are for. So a parked version is never fetched as an\n"
            "      object: `notch_spell` takes its spell_id and resolves the exact\n"
            "      version inside the call. The Spellbook is still not the surface\n",
            "      NAME THE VERSION BY ITS SPELL_ID. A spell_id names one version,\n"
            "      and the public spell_id->object lookups (`get_spell_by_spell_id`,\n"
            "      `find_spell_by_spell_id`) answer exactly that version, active or\n"
            "      parked (owner ruling 2026-10-17; until @@SINCE@@ they answered a\n"
            "      parked spell_id with the ACTIVE member). `notch_spell` takes the\n"
            "      spell_id too and resolves the exact version inside the call. The\n"
            "      Spellbook is still not the surface\n",
        ),
        (
            "VERIFY: RUN GREEN 2026-10-16 on 3.14t, GIL off and on.\n",
            "VERIFY: RUN GREEN @@VERIFIED@@ on 3.14t, GIL off and on.\n",
        ),
        (
            "    # WHY THE NOTCH IS GIVEN A SPELL_ID. A parked spell_id resolves to\n"
            "    # the CURRENT member, because that is what the lookups are for: they\n"
            "    # answer \"what is live for this lineage\", not \"give me the object\n"
            "    # behind this exact version\".\n"
            "    resolved_from_parked_id = conduit.get_spell_by_spell_id(v2_id)\n"
            "    assert resolved_from_parked_id is not None\n"
            "    assert resolved_from_parked_id.spell_id == v1_id\n"
            "    print()\n"
            "    print(\"looking up the PARKED spell_id returned the ACTIVE spell\")\n"
            "    print(\"  so the notch is told the version by its spell_id instead\")\n",
            "    # A SPELL_ID NAMES ONE VERSION. Looking up the parked spell_id answers\n"
            "    # the parked version itself - not the member live for this lineage -\n"
            "    # and the notch below is given that same spell_id.\n"
            "    resolved_from_parked_id = conduit.get_spell_by_spell_id(v2_id)\n"
            "    assert resolved_from_parked_id is not None\n"
            "    assert resolved_from_parked_id.spell_id == v2_id\n"
            "    print()\n"
            "    print(\"looking up the PARKED spell_id returned the PARKED spell\")\n"
            "    print(\"  and the notch is told the same version by the same spell_id\")\n",
        ),
    ],
    EXPERT_26: [
        (
            "    # Promotion is expert 17's lesson: notch_spell(spell_index=...,\n"
            "    # spell_id=staged) makes the staged version active. This lesson keeps\n"
            "    # it parked, and a lookup by its spell_id still answers with the ACTIVE\n"
            "    # member - which is why the notch is given the spell_id itself.\n"
            "    assert conduit.get_spell_by_spell_id(staged).spell_id == v1\n",
            "    # Promotion is expert 17's lesson: notch_spell(spell_index=...,\n"
            "    # spell_id=staged) makes the staged version active. This lesson keeps\n"
            "    # it parked: a lookup by its spell_id answers the staged version itself\n"
            "    # (until @@SINCE@@ it answered the ACTIVE member), and v1 stays selected.\n"
            "    assert conduit.get_spell_by_spell_id(staged).spell_id == staged\n"
            "    assert index.selected_spell_id == v1\n",
        ),
    ],
}


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check = "--check" in sys.argv[1:]
    if (len(args) != 3 or not re.fullmatch(r"\d+\.\d+\.\d+", args[1])
            or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args[2])):
        raise SystemExit(__doc__)
    root = pathlib.Path(args[0]).resolve()
    since, verified = args[1], args[2]
    out = {}
    for rel in FILES:
        raw = (root / rel).read_bytes()
        crlf = raw.count(b"\r\n")
        if crlf and crlf != raw.count(b"\n"):
            raise SystemExit(f"FAIL mixed line endings in {rel}")
        if not crlf and b"\r" in raw:
            raise SystemExit(f"FAIL stray carriage return in {rel}")
        text = raw.decode("utf-8").replace("\r\n", "\n")
        new, n_find = FIND.subn("find_spell_by_spell_id", text)
        new, n_get = GET.subn("get_spell_by_spell_id", new)
        for old, replacement in MANUAL.get(rel, []):
            if new.count(old) != 1:
                raise SystemExit(f"FAIL anchor count {new.count(old)} in {rel}: {old[:80]!r}")
            new = new.replace(old, replacement.replace("@@SINCE@@", since).replace("@@VERIFIED@@", verified))
        if n_find + n_get == 0:
            raise SystemExit(f"FAIL no old name in {rel}")
        out[rel] = (new.replace("\n", "\r\n") if crlf else new).encode("utf-8")
        print(f"ok {rel} find={n_find} get={n_get} manual={len(MANUAL.get(rel, []))} crlf={bool(crlf)}")
    if check:
        print("check only: nothing written")
        return
    for rel, data in out.items():
        (root / rel).write_bytes(data)
    print(f"written {len(out)} files")


if __name__ == "__main__":
    main()
