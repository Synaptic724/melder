"""
TIER: beginner (37)
GOAL: The whole bind vocabulary on one page - every kwarg a beginner
      will meet, printed as a cheatsheet next to a registration that
      uses ALL of them at once.
SURFACE EXERCISED: bind(spell, existence, permissions, spellframe,
                   binding_name, disposal_method_names, profile, **kwargs)
"""
import melder as md


class FullyDressed:
    def close(self) -> None:
        pass


def main() -> None:
    vocabulary = [
        ("spell", "the class/function/instance being registered"),
        ("existence", "where reuse stops (unique / many / per-conduit)"),
        ("permissions", "read / create / block"),
        ("spellframe", "top-level classification key (dict-style)"),
        ("binding_name", "sub-key; (frame, name) is the full address"),
        ("disposal_method_names", "your teardown verbs, called at cleanup"),
        ("profile", "spell profile family (default: general)"),
        ("**kwargs", "hook lists only; unknown keys silently ignored - beware"),
    ]
    for kwarg, meaning in vocabulary:
        print(f"{kwarg:24s} {meaning}")

    book = md.Spellbook()
    book.bind(
        spell=FullyDressed,
        existence=md.Existence.unique,
        permissions=md.Permissions.create,
        spellframe="demo",
        binding_name="fully-dressed",
        disposal_method_names=["close"],
        profile="general",
    )
    instance = book.conjure().meld(
        spell=FullyDressed, spellframe="demo", binding_name="fully-dressed"
    )
    assert isinstance(instance, FullyDressed)
    print("registration using the full vocabulary melded:", type(instance).__name__)


if __name__ == "__main__":
    main()
