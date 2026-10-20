"""
Install the new test files into a tree with their neighbours' line endings (CRLF here).

Usage: python install_new_tests.py <tree root holding tests/> <newtests dir>
"""
import pathlib
import sys

root, src = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
targets = {
    "test_aetheric_frame_cleanup_race.py": "tests/unit/melder/aether/test_aetheric_frame_cleanup_race.py",
    "test_aether_component_frame_sweep_races.py": "tests/component/melder/aether/test_aether_component_frame_sweep_races.py",
    "test_conduit_component_lock_gaps.py": "tests/component/melder/aether/conduit/test_conduit_component_lock_gaps.py",
}
for name, rel in targets.items():
    dest = root / rel
    neighbour = next(p for p in sorted(dest.parent.glob("test_*.py")) if p.name != dest.name)
    crlf = b"\r\n" in neighbour.read_bytes()
    text = (src / name).read_text(encoding="utf-8").replace("\r\n", "\n")
    if crlf:
        text = text.replace("\n", "\r\n")
    assert not dest.exists() or dest.read_bytes() == text.encode("utf-8"), f"{dest} exists and differs"
    dest.write_bytes(text.encode("utf-8"))
    print(f"{rel} ({'CRLF' if crlf else 'LF'})")
