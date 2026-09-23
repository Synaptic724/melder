"""
TIER: intermediate (40)
GOAL: Observe pre-bind, configure the actual Spell during bind activation,
      and inspect its completed registration in post-bind. Seed a callback
      through configuration, add stages on the Book, then clear and re-add
      through its normal Conduit. These hooks run at bind time, not meld time.
SURFACE EXERCISED: md.SpellbookConfiguration.with_bind_hooks,
                  md.Spellbook.add_bind_hooks / find_spell_by_id,
                  md.Conduit.clear_bind_hooks / add_bind_hooks / bind / meld,
                  md.Spell.metadata / tags
"""
import inspect

import melder as md


class Report:
    """Simple application object whose registration will be annotated by hooks."""

    def render(self) -> str:
        """Return an observable result after normal name-based resolution."""
        return "report ready"


class Metrics:
    """Separate registration used while all bind hooks are cleared."""


class Notifier:
    """Separate registration proving callbacks can be added again after clear."""


def main() -> None:
    """Exercise the three stages and future-bind updates in one dynamic Book.

    Contract:
        Assertions distinguish raw class references, unpublished Spells and
        completed registrations. Final cleanup releases the Book's callbacks.
    """
    events: list[str] = []

    def check_reference(reference: object) -> None:
        """Apply this application's class-only registration policy before reflection."""
        if not inspect.isclass(reference):
            raise TypeError("This example accepts class references only.")
        events.append(f"pre:{reference.__name__}")

    def configure_spell(spell: md.Spell) -> None:
        """Annotate the actual new Spell before it becomes publicly discoverable."""
        assert isinstance(spell, md.Spell)
        assert book.find_spell_by_id(spell.spell_id) is None
        spell.metadata["reviewed_by"] = "application-bind-policy"
        spell.tags.append("reviewed")
        events.append(f"activation:{spell.spell_name}")

    def observe_registration(spell: md.Spell) -> None:
        """Verify the registered Spell is the same object activation annotated."""
        assert book.find_spell_by_id(spell.spell_id) is spell
        assert spell.metadata["reviewed_by"] == "application-bind-policy"
        events.append(f"post:{spell.spell_name}")

    # Configuration seeds are captured when this Book is constructed.
    configuration = md.SpellbookConfiguration().with_defaults()
    configuration.with_bind_hooks(pre=[check_reference])
    book = md.Spellbook(configuration=configuration)
    conduit = None
    try:
        # Runtime setup appends stages to this Book's captured seed callbacks.
        book.add_bind_hooks(activation=[configure_spell], post=[observe_registration])
        report_id = book.bind(spell=Report, existence="unique")
        assert events == ["pre:Report", "activation:Report", "post:Report"]
        registered = book.find_spell_by_id(report_id)
        assert registered is not None
        assert "reviewed" in registered.tags
        print("bind order:", " -> ".join(events))

        conduit = book.conjure(dynamic=True, name="bind-hook-basics")
        assert conduit.meld("Report").render() == "report ready"
        assert events == ["pre:Report", "activation:Report", "post:Report"]
        print("meld returned the Report; bind callbacks did not run again")

        # The normal Conduit facades the same Book-owned bind-hook registry.
        conduit.clear_bind_hooks()
        metrics_id = conduit.bind(spell=Metrics, existence="unique")
        metrics_spell = book.find_spell_by_id(metrics_id)
        assert metrics_spell is not None
        assert metrics_spell.metadata == {}
        assert len(events) == 3
        assert registered.metadata["reviewed_by"] == "application-bind-policy"
        print("clear affected future binds; the earlier Spell kept its metadata")

        conduit.add_bind_hooks(
            pre=[check_reference], activation=[configure_spell], post=[observe_registration],
        )
        conduit.bind(spell=Notifier, existence="unique")
        assert events[3:] == ["pre:Notifier", "activation:Notifier", "post:Notifier"]
        print("re-added hooks:", " -> ".join(events[3:]))
    finally:
        if conduit is not None:
            conduit.cleanup()
        book.cleanup()


if __name__ == "__main__":
    main()
