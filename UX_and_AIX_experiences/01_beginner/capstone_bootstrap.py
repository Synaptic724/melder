"""Own registration and startup for the beginner application."""

import melder as md

from capstone_models import AppConfig, DbPool, RequestHandler


def build_application() -> tuple[md.Spellbook, md.Conduit]:
    """Register the graph and return the book/conduit to the entry point that owns shutdown.

    Config and pool are shared; handlers are created per meld. Registration or
    conjure failure cleans the partially configured book and propagates the error.
    """
    book = md.Spellbook()
    try:
        # Each bind manages its own transaction and synchronization.
        book.bind(spell=AppConfig, existence="unique")
        book.bind(spell=DbPool, existence="unique", disposal_method_names=["close"])
        book.bind(spell=RequestHandler, existence="many")
        conduit = book.conjure()
    except Exception:
        book.cleanup()
        raise
    return book, conduit
