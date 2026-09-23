"""
TIER: beginner (26)
GOAL: THE ADDRESS LAW (run-proven + doc-canon): every spell lives at
      one (frame_key, binding_key) address - frame_key is your spellframe,
      or the spell's normalized name if you gave none; binding_key is
      your binding_name, or the default slot. Human callers use a quoted
      spell name; machine callers use an explicit spell_id. A categorized
      registration also has a complete (spellframe, binding_name) address.
      A name alone does not supply a custom spellframe.
SURFACE EXERCISED: meld("SpellName"), meld(spell_id=...),
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
    spell_id = book.bind(spell=BillingService, existence="unique")
    # explicit address: ("finance", "ledger")
    book.bind(spell=LedgerService, existence="unique",
              spellframe="finance", binding_name="ledger")
    conduit = book.conjure()

    by_name = conduit.meld("BillingService")
    # Explicit machine form: SHA identity never shares the human string slot.
    by_id = conduit.meld(spell_id=spell_id)
    assert by_name is by_id
    print("quoted name and explicit ID resolve the same spell:", by_name.total())

    ledger = conduit.meld(spellframe="finance", binding_name="ledger")
    assert isinstance(ledger, LedgerService)
    print("framed spell answers at (frame, name)")

    try:
        conduit.meld("LedgerService")
    except KeyError as err:
        print("name-derived key misses a framed bind:", err)

    try:
        conduit.meld(binding_name="ledger")
    except ValueError as err:
        print("binding_name alone refused:", err)


if __name__ == "__main__":
    main()
