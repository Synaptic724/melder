"""
TIER: beginner (26)
GOAL: THE ADDRESS LAW (run-proven): every spell lives at exactly one
      (frame_key, binding_key) address - frame_key is your spellframe,
      or the spell's normalized name if you gave none; binding_key is
      your binding_name, or the default slot. The meld forms are just
      three ways to CONSTRUCT that key - so a frameless, nameless bind
      answers to the spell object and to spell_name; a framed+named
      bind answers only at (frame, name).
SURFACE EXERCISED: meld(spell=...), meld(spell_name=...),
                   meld(spellframe=..., binding_name=...)
"""
import melder as md


class BillingService:
    def total(self) -> int:
        return 42


class LedgerService:
    pass


def main() -> None:
    book = md.Spellbook()
    # default address: ("billingservice", default slot)
    book.bind(spell=BillingService, existence="unique")
    # explicit address: ("finance", "ledger")
    book.bind(spell=LedgerService, existence="unique",
              spellframe="finance", binding_name="ledger")
    conduit = book.conjure()

    by_object = conduit.meld(spell=BillingService)
    by_name = conduit.meld(spell_name="BillingService")
    assert by_object is by_name
    print("default-address spell answers both forms:", by_object.total())

    ledger = conduit.meld(spellframe="finance", binding_name="ledger")
    assert isinstance(ledger, LedgerService)
    print("framed spell answers at (frame, name)")

    try:
        conduit.meld(spell_name="LedgerService")
    except KeyError as err:
        print("name-derived key misses a framed bind:", err)

    try:
        conduit.meld(binding_name="ledger")
    except ValueError as err:
        print("binding_name alone refused:", err)


if __name__ == "__main__":
    main()
