"""
TIER: intermediate (03)
GOAL: Hooks ride the registration, not the call site - pre, activation,
      and post hooks attach through the fluent chain and fire around
      instance creation. The printed order IS the documentation; the
      3.14t run records the exact firing points.
SURFACE EXERCISED: md.SpellBinder.with_pre_hook / with_activation_hook /
                   with_post_hook
"""
import melder as md

EVENTS: list[str] = []


class Engine:
    def __init__(self) -> None:
        EVENTS.append("engine constructed")


def note(stage: str):
    def hook(*args: object, **kwargs: object) -> None:
        EVENTS.append(stage)
    return hook


def main() -> None:
    book = md.Spellbook()
    md.SpellBinder(book).bind(Engine) \
        .as_unique() \
        .with_pre_hook(note("pre")) \
        .with_activation_hook(note("activation")) \
        .with_post_hook(note("post")) \
        .finalize()

    conduit = book.conjure()
    engine = conduit.meld(spell=Engine)
    assert isinstance(engine, Engine)
    assert "engine constructed" in EVENTS
    print("lifecycle event order:", " -> ".join(EVENTS))


if __name__ == "__main__":
    main()
