"""Byte-identical device apply of the nested slot-guard change (melder_2).

Checks the device copies of the three src files still equal the validated base (base72), that the two new test
files do not exist yet, backs the device files up, copies the validated work72 files over and verifies sha256.
"""
import hashlib, pathlib, shutil, sys
HOME = pathlib.Path.home()
DEV = HOME / "mnt/melder_private"
BASE = HOME / "work/base72"
WORK = HOME / "work/work72"
BACKUP = HOME / "work/nested/device_before"
SRC = [
    "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py",
    "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtime.py",
    "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py",
]
NEW = [
    "tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_door_held_root.py",
    "tests/integration/melder/conduit/test_conduit_integration_door_held_first_build.py",
]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for rel in SRC:
    if sha(DEV / rel) != sha(BASE / rel):
        sys.exit(f"device changed since the validated base: {rel}")
for rel in NEW:
    if (DEV / rel).exists():
        sys.exit(f"new file already on the device: {rel}")
for rel in SRC:
    target = BACKUP / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(DEV / rel, target)
for rel in SRC + NEW:
    (DEV / rel).write_bytes((WORK / rel).read_bytes())
for rel in SRC + NEW:
    assert sha(DEV / rel) == sha(WORK / rel), rel
    print("applied", sha(DEV / rel)[:16], rel)
