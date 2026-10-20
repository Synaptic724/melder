"""Copy the new 0.2.8230 test files into <root> with their neighbours' line endings."""
import pathlib, sys

ROOT = pathlib.Path(sys.argv[1])
HERE = pathlib.Path(__file__).parent / "newtests"
PLACES = {
    "test_spell_index_cleanup_race.py": ("tests/unit/melder/spellbook/bind", "\r\n"),
    "test_detail_cleaned_index.py": ("tests/unit/melder/aether/conduit/conduit_ward/contract", "\r\n"),
    "test_spellbook_component_spell_map_races.py": ("tests/component/melder/spellbook", "\n"),
}
for name, (folder, eol) in PLACES.items():
    text = (HERE / name).read_text(encoding="utf-8").replace("\r\n", "\n")
    target = ROOT / folder / name
    if target.exists():
        raise SystemExit(f"refusing to overwrite {target}")
    target.write_bytes(text.replace("\n", eol).encode("utf-8"))
    print(f"{folder}/{name} ({'CRLF' if eol == chr(13) + chr(10) else 'LF'})")
