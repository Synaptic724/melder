"""
TIER: intermediate (24)
GOAL: The ConduitCloud - the world's phone book for dynamic NAMED
      roots. Reached publicly from any conduit; look peers up by name
      instead of passing references around.
SURFACE EXERCISED: Conduit.get_conduit_cloud, has_conduit_name, get_conduit
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # local helper (see _dynamic_world)
from _dynamic_world import dynamic_spellbook

import melder as md


class Anchor:
    pass


def main() -> None:
    alpha_book = dynamic_spellbook()
    alpha_book.bind(spell=Anchor, existence="unique")
    alpha = alpha_book.conjure(dynamic=True, name="alpha")
    beta = dynamic_spellbook().conjure(dynamic=True, name="beta")

    cloud = alpha.get_conduit_cloud()
    assert cloud.has_conduit_name("alpha") and cloud.has_conduit_name("beta")
    found = cloud.get_conduit("beta")
    assert found is beta
    print("phone book works: looked beta up by name, got the live conduit")


if __name__ == "__main__":
    main()
