"""
TIER: beginner (40) - capstone
GOAL: Everything the tier taught, as one tiny application: classified
      registrations under a lock batch, mixed lifecycles, a factory and
      a prebuilt instance, disposal, explicit cleanup, error handling.
      No scanning, no decorators, no dynamic worlds.
SURFACE EXERCISED: the full beginner vocabulary in one story
"""
import melder as md

TEARDOWN: list[str] = []


class AppConfig:
    def __init__(self, app_name: str) -> None:
        self.app_name = app_name


class DbPool:
    def close(self) -> None:
        TEARDOWN.append("pool closed")


class RequestHandler:
    served = 0

    def handle(self) -> str:
        RequestHandler.served += 1
        return f"request #{RequestHandler.served}"


def main() -> None:
    book = md.Spellbook()
    with book:  # atomic registration batch under the book lock
        book.bind(spell=AppConfig("orders-service"), existence="unique",
                  spellframe="app", binding_name="config")
        book.bind(spell=DbPool, existence="unique",
                  spellframe="app", binding_name="db",
                  disposal_method_names=["close"])
        book.bind(spell=RequestHandler, existence="many",
                  spellframe="web", binding_name="handler")

    conduit = book.conjure()
    config = conduit.meld(spellframe="app", binding_name="config")
    pool = conduit.meld(spellframe="app", binding_name="db")
    assert config.app_name == "orders-service" and isinstance(pool, DbPool)

    for _ in range(3):
        handler = conduit.meld(spellframe="web", binding_name="handler")
        print(handler.handle())

    try:
        conduit.meld(binding_name="nowhere")
        print("unknown address answered None-style")
    except Exception as err:
        print("unknown address raised:", type(err).__name__)

    conduit.cleanup()
    book.cleanup()
    print("teardown:", TEARDOWN or "(documented by this run)")
    print("capstone complete: classified, melded, disposed, guarded")


if __name__ == "__main__":
    main()
