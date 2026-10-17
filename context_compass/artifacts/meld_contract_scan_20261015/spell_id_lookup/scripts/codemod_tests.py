"""
Test-tree codemod for fix #1 (owner, 2026-10-17): the renamed spell_id lookups.

Usage: python codemod_tests.py <root> <since_version> [--check]

1. Generic, per occurrence, in every tests/**/*.py except the lane's own four new test files and the old
   component test file they replace:
   - `find_spell_by_id` (a whole word) -> `find_spell_by_spell_id` (Spellbook calls, its fakes and mocks);
   - `get_spell_by_id` (a whole word) -> `get_spell_by_spell_id` (Conduit calls, the Rift room command - its calls,
     its name in the advertised command lists and in the JSON testbench scenarios - and their fakes and mocks;
     owner, 2026-10-17: "update it all").
2. Prose that described the old answer is rewritten by exact-once anchors (on the text after step 1), and three
   test names follow the methods.
Nothing is written when an anchor misses, or with --check.
"""
import pathlib
import re
import sys

SKIP = {
    "tests/component/melder/spellbook/test_spellbook_component_find_spell_by_spell_id.py",
    "tests/component/melder/spellbook/test_spellbook_component_find_spell_by_id.py",
    "tests/integration/melder/aether/conduit/test_spell_id_lookup_returns_that_spell_integration.py",
    "tests/unit/melder/aether/test_command_system_spell_id_lookups.py",
    "tests/integration/melder/aether/rift/test_rift_spell_id_lookups_return_that_spell_integration.py",
}
FIND = re.compile(r"\bfind_spell_by_id\b")
GET = re.compile(r"\bget_spell_by_id\b")

MANUAL = {
    "tests/unit/melder/spellbook/test_spell_cleanup_safe_index_read.py": [(
        "Spellbook.find_spell_by_spell_id reads a parked spell's index through this accessor without holding the Book\n"
        "lock, so the read must answer the live index, follow an index move, answer None once the spell is cleaned,\n"
        "and never interleave with a cleanup running under the spell's lock.\n",
        "Readers that hold a Spell and no Book lock read its index through this accessor - the parked branch of\n"
        "Spellbook._find_contracted_spell_by_id and, since @@SINCE@@, the explicit index steps of the ownership\n"
        "transfer and the contract dependency walks (until then the parked branch of Spellbook.find_spell_by_id) - so\n"
        "the read must answer the live index, follow an index move, answer None once the spell is cleaned, and never\n"
        "interleave with a cleanup running under the spell's lock.\n",
    )],
    "tests/integration/melder/conduit/test_conduit_integration_release_managed_spell.py": [(
        "        # find_spell_by_spell_id answers a parked id with the index's live spell; the notch needs the parked one.\n",
        "        # The notch needs the parked version itself, which _get_owned_spell answers (until @@SINCE@@\n"
        "        # find_spell_by_id answered a parked id with the index's live spell).\n",
    )],
    "tests/integration/melder/aether/conduit/test_spell_index_notch_lifecycle.py": [(
        "The parked B object is fetched with `book._get_owned_spell(id_b)` because `find_spell_by_spell_id`\n"
        "only scans the ACTIVE map.\n",
        "The parked B object is fetched with `book._get_owned_spell(id_b)`, the exact owned lookup (until @@SINCE@@\n"
        "`find_spell_by_id` answered a parked id with the index's active member).\n",
    )],
    "tests/component/melder/spellbook/test_spellbook_component_resolvable_registration.py": [(
        "    # Public find_spell_by_spell_id follows the selected member; use the exact parked record here.\n",
        "    # Read the exact parked record (until @@SINCE@@ the public find_spell_by_id answered the selected member).\n",
    )],
    "tests/integration/melder/conduit/test_conduit_integration_notch_revalidation.py": [(
        "    grant takes the parked Spell object, because `get_spell_by_spell_id` answers a parked id with the active member.\n",
        "    grant takes the parked Spell object (until @@SINCE@@ `get_spell_by_id` answered a parked id with the active\n"
        "    member).\n",
    )],
    "tests/unit/melder/aether/test_nexus.py": [
        ("def test_command_system_can_get_spell_by_id(\n",
         "def test_command_system_can_get_spell_by_spell_id(\n"),
        ("            # The owner Book answers the lineage lookup from its id maps (0.2.8230).\n",
         "            # The owner Book answers the spell_id lookup from its id maps (0.2.8230; exact since @@SINCE@@).\n"),
    ],
    "tests/unit/melder/aether/conduit/test_conduit_facade.py": [
        ("def test_get_spell_by_id_returns_none_when_owner_missing(\n",
         "def test_get_spell_by_spell_id_returns_none_when_owner_missing(\n"),
        ("def test_get_spell_by_id_returns_owner_spell(\n",
         "def test_get_spell_by_spell_id_returns_owner_spell(\n"),
    ],
}


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check = "--check" in sys.argv[1:]
    if len(args) != 2 or not re.fullmatch(r"\d+\.\d+\.\d+", args[1]):
        raise SystemExit(__doc__)
    root = pathlib.Path(args[0]).resolve()
    since = args[1]
    out = {}
    totals = [0, 0]
    for path in sorted((root / "tests").rglob("*.py")):
        rel = path.relative_to(root).as_posix()
        if rel in SKIP:
            continue
        raw = path.read_bytes()
        crlf = b"\r\n" in raw
        text = raw.decode("utf-8")
        if crlf:
            text = text.replace("\r\n", "\n")
        new, n_find = FIND.subn("find_spell_by_spell_id", text)
        new, n_get = GET.subn("get_spell_by_spell_id", new)
        for old, replacement in MANUAL.get(rel, []):
            if new.count(old) != 1:
                raise SystemExit(f"FAIL anchor count {new.count(old)} in {rel}: {old[:80]!r}")
            new = new.replace(old, replacement.replace("@@SINCE@@", since))
        if new != text:
            totals[0] += n_find
            totals[1] += n_get
            data = new.replace("\n", "\r\n") if crlf else new
            out[rel] = data.encode("utf-8")
            print(f"ok {rel} find={n_find} get={n_get} manual={len(MANUAL.get(rel, []))}")
    missing = set(MANUAL) - set(out)
    if missing:
        raise SystemExit(f"FAIL manual files untouched: {sorted(missing)}")
    print(f"files={len(out)} find={totals[0]} get={totals[1]}")
    if check:
        print("check only: nothing written")
        return
    for rel, data in out.items():
        (root / rel).write_bytes(data)
    print("written")


if __name__ == "__main__":
    main()
