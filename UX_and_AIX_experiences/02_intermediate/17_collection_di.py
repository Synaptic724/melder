"""
TIER: intermediate (17)
GOAL: Collection DI - annotate list[Shape] and receive EVERY bound
      implementation in registration order. The plugin pattern in one
      annotation; zero matches is a legal empty list.
SURFACE EXERCISED: list[FrameType] collection injection
"""
from typing import Protocol

import melder as md


class Handler(Protocol):
    def handle(self) -> str: ...


class EmailHandler:
    def handle(self) -> str:
        return "email"


class SmsHandler:
    def handle(self) -> str:
        return "sms"


class Dispatcher:
    def __init__(self, handlers: list[Handler]) -> None:
        self.handlers = handlers


def main() -> None:
    book = md.Spellbook()
    # One ACTIVE spell per (spellframe, binding_name) signature per
    # frame - providers sharing a frame need distinct binding names.
    book.bind(spell=EmailHandler, existence="unique", spellframe=Handler,
              binding_name="email")
    book.bind(spell=SmsHandler, existence="unique", spellframe=Handler,
              binding_name="sms")
    book.bind(spell=Dispatcher, existence="unique")
    conduit = book.conjure()

    dispatcher = conduit.meld(spell=Dispatcher)
    results = [h.handle() for h in dispatcher.handlers]
    assert results == ["email", "sms"]
    print("collection DI delivered all implementations:", results)


if __name__ == "__main__":
    main()
