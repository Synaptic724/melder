"""
TIER: beginner (17)
GOAL: Protocols describe a SHAPE; bindings fill it - two implementations
      of one Protocol, chosen by binding name, called through the shared
      shape. Static duck typing meets dependency injection, gently.
SURFACE EXERCISED: typing.Protocol + named bindings
"""
from typing import Protocol

import melder as md


class Notifier(Protocol):
    def send(self, message: str) -> str: ...


class ConsoleNotifier:
    def send(self, message: str) -> str:
        return "console: " + message


class QuietNotifier:
    def send(self, message: str) -> str:
        return "(logged silently: " + message + ")"


def notify(notifier: Notifier, message: str) -> str:
    return notifier.send(message)  # any object with the right SHAPE works


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=ConsoleNotifier, existence="unique",
              spellframe="notifiers", binding_name="loud")
    book.bind(spell=QuietNotifier, existence="unique",
              spellframe="notifiers", binding_name="quiet")
    conduit = book.conjure()

    loud: Notifier = conduit.meld(spellframe="notifiers", binding_name="loud")
    quiet: Notifier = conduit.meld(spellframe="notifiers", binding_name="quiet")
    print(notify(loud, "deploy finished"))
    print(notify(quiet, "cache warmed"))
    assert notify(loud, "x").startswith("console")
    print("one Protocol shape, two swappable spells")


if __name__ == "__main__":
    main()
