"""
TIER: beginner (38)
GOAL: Closing the dict-style loop - a small helper melds a whole frame
      family into a plain {name: instance} dict, because the (frame,
      name) address space maps 1:1 onto the dicts users already think in.
SURFACE EXERCISED: frame-family melding, dict-style consumption
"""
import melder as md


class AuthMiddleware:
    pass


class LoggingMiddleware:
    pass


class RetryMiddleware:
    pass


MIDDLEWARE = {"auth": AuthMiddleware, "logging": LoggingMiddleware,
              "retry": RetryMiddleware}


def meld_frame(conduit: md.Conduit, frame: str, names: list[str]) -> dict:
    return {name: conduit.meld(spellframe=frame, binding_name=name)
            for name in names}


def main() -> None:
    book = md.Spellbook()
    for name, cls in MIDDLEWARE.items():
        book.bind(spell=cls, existence="unique",
                  spellframe="middleware", binding_name=name)
    conduit = book.conjure()

    stack = meld_frame(conduit, "middleware", list(MIDDLEWARE))
    assert set(stack) == {"auth", "logging", "retry"}
    assert all(v is not None for v in stack.values())
    print("frame melded as dict:", {k: type(v).__name__ for k, v in stack.items()})


if __name__ == "__main__":
    main()
