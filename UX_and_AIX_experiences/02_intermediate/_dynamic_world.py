"""
Support helper for the dynamic-mode lessons. Since the settle-then-
inherit change (2026-07-20), conjure(dynamic=True) on a fresh world
SETTLES it dynamic - no posture plumbing needed. This helper is now just
a plain configured book; lesson 21 teaches the settlement law itself.
"""
import melder as md


def dynamic_spellbook(frame: str = "default") -> md.Spellbook:
    """A plain book; conjure(dynamic=True) settles the world on first use."""
    configuration = md.SpellbookConfiguration()
    configuration.with_defaults()
    return md.Spellbook(configuration=configuration)
