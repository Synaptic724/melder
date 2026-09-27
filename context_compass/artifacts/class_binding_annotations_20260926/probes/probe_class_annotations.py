"""Print each probe class's binding-profile annotations and spell id (run in a fresh process)."""
import json
import sys


def main() -> None:
    """Build the binding profile of every probe class and dump annotations, keys and id."""
    from melder.aether.spellbook.bind.bind import Bind
    from melder.aether.spellbook.existence.existence import Existence
    from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.general_profile import SpellGeneralProfile
    import probe_class_annotation_shapes as shapes

    rows = {}
    for name, cls in shapes.candidates().items():
        profile = SpellGeneralProfile.create_from_target(cls).binding_profile
        rows[name] = {
            "id": Bind.spell_id_inspector(cls, existence=Existence.unique)[:16],
            "keys": sorted(profile.annotations.keys()),
            "values": {k: repr(v) for k, v in profile.annotations.items()},
        }
    json.dump(rows, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
