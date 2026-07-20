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
    print("unique law: shared product?", flags_a is flags_b)


if __name__ == "__main__":
    main()
