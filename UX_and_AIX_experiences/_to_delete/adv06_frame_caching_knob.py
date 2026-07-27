"""
TIER: advanced (06)
GOAL: The frame's CACHING knob through the public door.
      configure_aether_frame(system_caching_enabled=...) stages the
      world's system-caching posture alongside system_state - the
      caching flag governs whether conjure's compiled artifacts may be
      cached and replayed (a full cache hit skips the plan phases on a
      later conjure of the same world shape). Same freeze law as every
      posture knob: decided before the first conjure, locked after.
      (Its sibling system_cache_root_path - WHERE cached artifacts
      live - currently has no public staging door; recorded as a
      finding in the concept map.)
SURFACE EXERCISED: configure_aether_frame(system_caching_enabled=...)
"""
import melder as md


class CachedService:
    pass


def main() -> None:
    book = md.Spellbook(aetheric_frame="caching-world")
    book.bind(spell=CachedService, existence="unique")
    book.configure_aether_frame(system_state="automatic", disposal=None,
                                disposal_method_names=None,
                                system_caching_enabled=True)
    conduit = book.conjure()
    service = conduit.meld(spell=CachedService)
    assert isinstance(service, CachedService)
    print("caching-enabled world conjured and resolved normally")
    print("(semantics identical - caching tunes conjure cost, not behavior)")


if __name__ == "__main__":
    main()
