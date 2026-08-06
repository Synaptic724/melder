"""
TIER: intermediate (12)
GOAL: Even a lambda is a spell - it MUST carry a binding_name (the law
      the runtime enforces); melds address it by (frame, name) because
      binding_name alone is never an address. Callable = unique.
SURFACE EXERCISED: bind(spell=<lambda>), binding_name, callable-unique law
"""
import melder as md


def main() -> None:
    book = md.Spellbook()
    book.bind(
        spell=lambda: {"feature_flags": {"dark_mode": True}},
        existence="unique",
        spellframe="flags",
        binding_name="flag-factory",
    )
    conduit = book.conjure()
    flags_a = conduit.meld(spellframe="flags", binding_name="flag-factory")
    flags_b = conduit.meld(spellframe="flags", binding_name="flag-factory")
    print("lambda product:", flags_a)

    # The lambda RAN, and what you get back is its product - not the
    # lambda itself. A callable spell is invoked to produce the object.
    assert flags_a == {"feature_flags": {"dark_mode": True}}
    assert not callable(flags_a), "you meld the PRODUCT, not the callable"

    # CALLABLE = UNIQUE. Both melds returned the SAME dict, so the lambda
    # was called once and its product shared. Were this `many`, the second
    # meld would have re-run the lambda and produced an equal-but-separate
    # dict - equality would hold and identity would not.
    assert flags_a is flags_b
    print("unique law: shared product?", flags_a is flags_b)
    print("  same object, so the lambda ran ONCE - `many` would have")
    print("  produced two equal dicts that are not the same object")

    # ADDRESSING IS (frame, name), AND binding_name IS NOT AN ENTRY MODE.
    # meld has four ways in - a spell_id string, a spell object, a
    # spellframe, or a spell_name. `binding_name` is none of them: it is a
    # binding KEY used during resolution, so on its own there is nothing
    # to resolve FROM and the call refuses with ValueError.
    try:
        conduit.meld(binding_name="flag-factory")
        raise AssertionError("binding_name alone must not be an address")
    except ValueError as unaddressed:
        print("meld(binding_name=...) alone -> ValueError:",
              str(unaddressed)[:70])
        print("  that is why the working call above passes spellframe TOO")


if __name__ == "__main__":
    main()
