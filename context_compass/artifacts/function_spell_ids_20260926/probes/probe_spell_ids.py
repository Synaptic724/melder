"""Print each candidate's spell id and the process-dependent fingerprint inputs (run in a fresh process)."""
import json
import sys

from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.general_profile import SpellGeneralProfile

import probe_user_shapes as shapes

rows = {}
for name, obj in shapes.CANDIDATES.items():
    profile = SpellGeneralProfile.create_from_target(obj).binding_profile
    rows[name] = {
        "id": Bind.spell_id_inspector(obj, existence=Existence.unique)[:16],
        "profile": type(profile).__name__,
        "repr_string": getattr(profile, "repr_string", None),
        "defaults": [p.default_repr for p in (getattr(profile, "parameters", None) or []) if p.default_repr],
    }
json.dump(rows, sys.stdout, indent=1)
