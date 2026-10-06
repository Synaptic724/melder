"""Verify the 0.2.8215 wheel: release checks, members against 0.2.8212, the lane's markers, bytes against the tree.

Usage: python verify_wheel_8215.py <wheel> <previous wheel> <repository root>
"""
import hashlib
import importlib.util
import pathlib
import sys
import zipfile

WHEEL, PREVIOUS, ROOT = (pathlib.Path(value) for value in sys.argv[1:4])
spec = importlib.util.spec_from_file_location("verify_distributions", ROOT / ".github/scripts/verify_distributions.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.verify_wheel(WHEEL, "0.2.8215")
raw = WHEEL.read_bytes()
print(f"verify_wheel OK for 0.2.8215: {WHEEL.name} {len(raw)} bytes")
print(f"sha256 {hashlib.sha256(raw).hexdigest()}")


def package_members(path: pathlib.Path) -> set:
    """Return the archive members outside the dist-info directory."""
    with zipfile.ZipFile(path) as archive:
        return {name for name in archive.namelist() if ".dist-info/" not in name}


new, old = package_members(WHEEL), package_members(PREVIOUS)
with zipfile.ZipFile(WHEEL) as archive:
    names = archive.namelist()
    print(f"members: {len(names)}; package files {len(new)} vs 0.2.8212: {len(old)}")
    print(f"added vs 0.2.8212: {sorted(new - old)}")
    print(f"removed vs 0.2.8212: {sorted(old - new)}")
    for member, marker in (
            ("melder/aether/spellbook/spellbook_creation_system.py", "def flag_dependencies_without_own_plan"),
            ("melder/aether/conduit/meld/meld.py", "def _requires_own_target_pass"),
            ("melder/aether/conduit/meld/meld.py", "def _raise_unless_resolution_valid"),
            ("melder/__version__.py", '__version__ = "0.2.8215"'),
    ):
        present = marker in archive.read(member).decode("utf-8")
        print(f"{member}: {marker!r} present: {present}")
        if not present:
            raise SystemExit("marker missing")
    mismatched = []
    for name in sorted(new):
        if name.endswith("/"):
            continue
        source = ROOT / "src" / name
        if not source.is_file() or source.read_bytes() != archive.read(name):
            mismatched.append(name)
    print(f"package files byte-identical to the device tree: {len(new) - len(mismatched)} of {len(new)}")
    if mismatched:
        raise SystemExit(f"differs from the tree: {mismatched[:10]}")
    print("dist-info:", sorted(name for name in names if ".dist-info/" in name))
