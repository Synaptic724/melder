"""
TIER: intermediate (01)
GOAL: Declarative binding - tag classes where they live with @md.scan_bind,
      then register the whole module in one scan() call. The decorator
      stores intent only; nothing binds until scan time.
SURFACE EXERCISED: md.scan_bind, md.Spellbook.scan, md.Existence, md.Permissions
"""
import sys

import melder as md


@md.scan_bind(existence=md.Existence.unique, permissions=md.Permissions.create)
class MetricsHub:
    pass


@md.scan_bind(existence=md.Existence.many, permissions=md.Permissions.create)
class JobTicket:
    pass


def main() -> None:
    book = md.Spellbook()
    bound = book.scan(sys.modules[__name__])
    print("scan bound", len(bound), "spells:", sorted(bound))
    assert len(bound) == 2

    conduit = book.conjure()
    hub_a = conduit.meld(spell=MetricsHub)
    hub_b = conduit.meld(spell=MetricsHub)
    ticket_a = conduit.meld(spell=JobTicket)
    ticket_b = conduit.meld(spell=JobTicket)
    assert hub_a is hub_b and ticket_a is not ticket_b
    print("decorated lifecycles held: unique hub, many tickets")


if __name__ == "__main__":
    main()
