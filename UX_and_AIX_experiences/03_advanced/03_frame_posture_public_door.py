"""
TIER: advanced (03)
GOAL: Frame POSTURE through the public door. configure_aether_frame()
      is the manual fluent path: set the world's system_state BEFORE
      anyone conjures, and every conjure then INHERITS it - no
      dynamic=True flag needed anywhere (the settle-then-inherit law
      from intermediate 21, driven from the configuration side this
      time). The posture FREEZES at the first conjure: configuring
      after that refuses - a world's mode is decided once.
SURFACE EXERCISED: Spellbook(aetheric_frame=...),
                   configure_aether_frame(system_state=...),
                   plain-conjure inheritance, the freeze law
"""
import melder as md


class OpsService:
    pass


def main() -> None:
    # A named world, postured dynamic through the PUBLIC door -
    # before any conjure has settled anything.
    book = md.Spellbook(aetheric_frame="ops-world")
    book.bind(spell=OpsService, existence="unique")
    book.configure_aether_frame(system_state="dynamic", disposal=None,
                                disposal_method_names=None)

    # Plain conjures INHERIT the configured posture - no flags.
    root = book.conjure(name="ops-root")
    peer = md.Spellbook(aetheric_frame="ops-world").conjure(name="ops-peer")
    assert root.link(peer) is True
    print("configured world: plain conjures inherited dynamic and linked")

    # The mode is decided ONCE. After the first conjure froze the
    # posture, reconfiguring the world refuses.
    try:
        book.configure_aether_frame(system_state="automatic", disposal=None,
                                    disposal_method_names=None)
        print("post-freeze reconfigure unexpectedly succeeded")
    except Exception as err:
        print("post-freeze reconfigure refused:", type(err).__name__)


if __name__ == "__main__":
    main()
