"""Scope-exit dispose lane, part 6: SpellSpaceMeld docstrings stop promising reset/version/active-scope checks and
the wrong `many` routing. Docstrings only. melder_0, 2026-09-27."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from source_edit import replace_block

ROOT = sys.argv[1]
DOOR = os.path.join(ROOT, "src/melder/aether/conduit/meld/spellspace_meld.py")

print("spellspace_meld.py")
replace_block(DOOR, """
    Lifecycle / Cleanup:
        Bound to one `SpellSpace`; it becomes unusable when that spellspace is
        reset or cleaned. Its stores are torn down by the base.
""", """
    Lifecycle / Cleanup:
        Bound to one `SpellSpace` for that object's whole life: it stays with
        the space across pool leases and is cleaned when the space is
        permanently destroyed. A space released to its pool refuses `meld` and
        `purge` before this door is reached. Its stores are torn down by the
        base.
""")
replace_block(DOOR, """
        Scope is enforced upstream too: `SpellSpace` may only meld while it is
        the ACTIVE spellspace for its conduit, and `reset()` clears
        spellspace-scoped instances and bumps the version rather than reusing
        stale ones.
""", """
        Scope is enforced upstream too: every exit of a `SpellSpace` clears its
        spellspace-scoped instances before the space goes back to its pool, and
        a released space refuses `meld` and `purge`, so a stale handle cannot
        build into an idle shell that the next request would be served.
""")
replace_block(DOOR, """
            - Routes `unique_per_conduit` and `many` through the injected
              owner-conduit creations registry.
""", """
            - Routes `unique_per_conduit` through the injected owner-conduit
              creations registry. A `many` object with disposal methods is
              tracked in this spellspace's scope store (the innermost active
              scope) and disposed at the scope's exit; one without disposal
              methods is not stored.
""")
print("part 6 done")
