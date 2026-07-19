"""
TIER: beginner (26)
GOAL: The three meld address forms (probe-proven): the spell object,
      the spell's NAME string (spell_name), and (spellframe,
      binding_name). binding_name alone is a sub-key, NEVER an address -
      the runtime refuses it with a clear ValueError.
SURFACE EXERCISED: meld(spell=...), meld(spell_name=...),
                   meld(spellframe=..., binding_name=...)
"""
import melder as md


class BillingService:
    def total(self) -> int:
        return 42


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=BillingService, existence="unique",
              spellframe="services", binding_name="billing")
    conduit = book.conjure()

    by_object = conduit.meld(spell=BillingService, spellframe="services",
                             binding_name="billing")
    by_name = conduit.meld(spell_name="BillingService")
    by_address = conduit.meld(spellframe="services", binding_name="billing")
    assert by_object is by_name is by_address
    print("three addresses, one instance:", by_object.total())

    try:
        conduit.meld(binding_name="billing")
    except ValueError as err:
        print("binding_name alone refused:", err)


if __name__ == "__main__":
    main()
