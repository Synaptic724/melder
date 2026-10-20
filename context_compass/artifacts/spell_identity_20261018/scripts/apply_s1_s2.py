"""melder_0, 2026-10-18: apply S1 and S2 of EPIC-2026-10-18-spell_identity_is_the_code to a source root.

    python3 apply_s1_s2.py --root /tmp/m0_mq/wt [--check]     # the /tmp working mirror
    python3 apply_s1_s2.py --root ~/mnt/melder_private --check # the repository, after melder_1's hand-back
"""
import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import edits_bind
import edits_cache
import edits_crystal
import edits_profiles
import edits_spell
import edits_statements
from apply_common import Applier


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--backup", default="/tmp/m0_mq/bak_apply")
    args = parser.parse_args()
    applier = Applier(pathlib.Path(args.root).expanduser(), pathlib.Path(args.backup))
    applier.copy("src/melder/aether/spellbook/bind/spell_code_digest.py")
    applier.copy("src/melder/aether/spellbook/bind/binding_manifest.py")
    edits_spell.apply(applier)
    edits_bind.apply(applier)
    edits_profiles.apply(applier)
    edits_cache.apply(applier)
    edits_crystal.apply(applier)
    edits_statements.apply(applier)
    applier.commit(args.check)


if __name__ == "__main__":
    main()
