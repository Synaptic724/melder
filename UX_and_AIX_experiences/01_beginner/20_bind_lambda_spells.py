"""
TIER: beginner (20)
GOAL: Even a lambda is a spell - tiny factories bind inline with a
      binding_name carrying the meaning the lambda lacks.
SURFACE EXERCISED: bind(spell=<lambda>), binding_name
"""
import melder as md


def main() -> None:
    book = md.Spellbook()
    book.bind(
        spell=lambda: {"feature_flags": {"dark_mode": True}},
        existence="many",
        binding_name="flag-factory",
    )
    conduit = book.conjure()
    flags_a = conduit.meld(binding_name="flag-factory")
    flags_b = conduit.meld(binding_name="flag-factory")
    print("lambda factory ran twice:", flags_a is not flags_b)
    print("payload:", flags_a["feature_flags"])


if __name__ == "__main__":
    main()
