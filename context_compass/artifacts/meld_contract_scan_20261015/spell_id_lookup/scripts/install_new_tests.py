"""
Install fix #1's new test files into a tree, with the landing version written in.

Usage: python install_new_tests.py <root> <since_version> [--scratch] [--check]
  <root>           a tree holding tests/ (the repository root or a scratch copy)
  <since_version>  the notch this lands as; replaces @@SINCE@@ in the files
  --scratch        a scratch tree: the old component test file is deleted
  --check          print the plan; write nothing

The new component file replaces tests/component/melder/spellbook/test_spellbook_component_find_spell_by_id.py.
Outside --scratch (the repository refuses deletes) the old file is renamed to the new name without overwriting,
then its content is replaced, so the change reads as a rename; with --scratch the old file is deleted.
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent / "tests"
OLD_COMPONENT = "tests/component/melder/spellbook/test_spellbook_component_find_spell_by_id.py"
FILES = {
    "test_spellbook_component_find_spell_by_spell_id.py":
        "tests/component/melder/spellbook/test_spellbook_component_find_spell_by_spell_id.py",
    "test_spell_id_lookup_returns_that_spell_integration.py":
        "tests/integration/melder/aether/conduit/test_spell_id_lookup_returns_that_spell_integration.py",
    "test_command_system_spell_id_lookups.py":
        "tests/unit/melder/aether/test_command_system_spell_id_lookups.py",
    "test_rift_spell_id_lookups_return_that_spell_integration.py":
        "tests/integration/melder/aether/rift/test_rift_spell_id_lookups_return_that_spell_integration.py",
}


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check = "--check" in sys.argv[1:]
    scratch = "--scratch" in sys.argv[1:]
    if len(args) != 2 or not re.fullmatch(r"\d+\.\d+\.\d+", args[1]):
        raise SystemExit(__doc__)
    root = pathlib.Path(args[0]).resolve()
    since = args[1]
    payloads = {}
    for name, rel in FILES.items():
        text = (HERE / name).read_text(encoding="utf-8").replace("@@SINCE@@", since)
        if "@@SINCE@@" in text or "\r" in text:
            raise SystemExit(f"FAIL {name}: placeholder or CR left")
        if not (root / rel).parent.is_dir():
            raise SystemExit(f"FAIL missing directory for {rel}")
        payloads[rel] = text
    old = root / OLD_COMPONENT
    new_component = root / FILES["test_spellbook_component_find_spell_by_spell_id.py"]
    plan = []
    if old.exists():
        if scratch:
            plan.append(f"delete {OLD_COMPONENT}")
        elif new_component.exists():
            raise SystemExit(f"FAIL both {OLD_COMPONENT} and its new name exist; resolve by hand")
        else:
            plan.append(f"rename {OLD_COMPONENT} -> {new_component.relative_to(root).as_posix()}")
    for rel in payloads:
        plan.append(("overwrite " if (root / rel).exists() else "create ") + rel)
    for line in plan:
        print("plan", line)
    if check:
        print("check only: nothing written")
        return
    if old.exists():
        if scratch:
            old.unlink()
        else:
            old.rename(new_component)
    for rel, text in payloads.items():
        (root / rel).write_text(text, encoding="utf-8", newline="\n")
    print(f"installed {len(payloads)} files")


if __name__ == "__main__":
    main()
