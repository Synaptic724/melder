"""Restore CRLF line endings on the two test files apply_removal_tests_2026_10_16.py rewrote with LF.

melder_1 (synaptic_python_developer), 2026-10-16. Both files were CRLF on every line before the edit
(test_spellbook_component_contracts.py 749/749, test_spell_index_meld_and_contract_lifecycle.py 173/173); the apply
script wrote them back with LF, which would have changed every line. This converts each back to CRLF on every line.
usage: python fix_crlf_removal_tests_2026_10_16.py <tree root> --check | --apply
"""
import pathlib
import sys

FILES = [
    "tests/component/melder/spellbook/test_spellbook_component_contracts.py",
    "tests/integration/melder/aether/conduit/test_spell_index_meld_and_contract_lifecycle.py",
]


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[2] not in ("--check", "--apply"):
        raise SystemExit("usage: <tree root> --check | --apply")
    root = pathlib.Path(sys.argv[1])
    out = {}
    for rel in FILES:
        raw = (root / rel).read_bytes()
        if b"\r" in raw:
            raise SystemExit(f"{rel} already has CR bytes - refusing")
        new = raw.replace(b"\n", b"\r\n")
        out[rel] = new
        print(rel, "lines", raw.count(b"\n"), "CRLF after", new.count(b"\r\n"))
    if sys.argv[2] == "--check":
        print("check only - nothing written")
        return
    for rel, new in out.items():
        (root / rel).write_bytes(new)
        assert (root / rel).read_bytes() == new
    print("applied and read back")


if __name__ == "__main__":
    main()
