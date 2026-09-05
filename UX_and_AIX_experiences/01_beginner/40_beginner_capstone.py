"""
TIER: beginner (40) - capstone
GOAL: Build and use a small application across separate Python modules:
      ordinary objects, one bootstrap, a TYPE_CHECKING consumer, constructor
      injection, shared resources, fresh handlers, and explicit cleanup.
      Each bind manages its own transaction; no outer book lock is needed.
SURFACE EXERCISED: md.Spellbook.bind/conjure, md.Conduit.meld/cleanup,
                  unique/many, constructor injection, disposal_method_names
"""
from typing import TYPE_CHECKING

from capstone_application import run_application
from capstone_bootstrap import build_application

if TYPE_CHECKING:
    from capstone_models import DbPool


def main() -> None:
    """Start the graph, use it, and guarantee shutdown around the application call."""
    book, conduit = build_application()
    try:
        pool: DbPool = conduit.meld(spell="DbPool")
        messages = run_application(conduit)
        assert messages == [
            "orders-service: order 101 = coffee",
            "orders-service: order 102 = tea",
            "orders-service: order 103 = cocoa",
        ]
        for message in messages:
            print(message)
    finally:
        try:
            conduit.cleanup()
        finally:
            book.cleanup()

    assert pool.closed and pool.query_count == 3
    print("pool closed:", pool.closed)
    print("capstone complete: bootstrapped, typed, injected, used, cleaned")


if __name__ == "__main__":
    main()
