"""
TIER: intermediate (10)
GOAL: The fluent registration hand - SpellBinder reads like a sentence:
      bind(X).as_unique().named("primary").finalize(). finalize() returns
      the spell id string and resets the binder for the next registration.
SURFACE EXERCISED: md.SpellBinder, md.Spellbook, finalize() -> str
"""
import melder as md


class TelemetrySink:
    pass


class AuditTrail:
    pass


def main() -> None:
    book = md.Spellbook()
    binder = md.SpellBinder(book)

    sink_id = binder.bind(TelemetrySink).as_unique().named("sink").finalize()
    audit_id = binder.bind(AuditTrail).as_many().finalize()
    assert isinstance(sink_id, str) and isinstance(audit_id, str)
    print("fluent binds returned spell ids:", sink_id[:8], audit_id[:8])

    conduit = book.conjure()
    sink_a = conduit.meld(spell=TelemetrySink, binding_name="sink")
    sink_b = conduit.meld(spell=TelemetrySink, binding_name="sink")
    audit_a = conduit.meld(spell=AuditTrail)
    audit_b = conduit.meld(spell=AuditTrail)
    assert sink_a is sink_b and audit_a is not audit_b
    print("fluent lifecycles held: unique sink, many audit trails")


if __name__ == "__main__":
    main()
