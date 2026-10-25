"""Probe (melder_1, 2026-10-25; STORY-2026-10-17-notch_moves_signature_by_incoming_key_only): every way of naming a
spell in a meld, before and after a notch. Public calls only, one case per process:

    python probe_meld_identities_across_a_notch.py protocol          # English -> French, both at (Greeter, 'greeter')
    python probe_meld_identities_across_a_notch.py bare_same_name    # ReportService edited: same class name, bound bare
    python probe_meld_identities_across_a_notch.py bare_renamed      # ReportServiceV2 staged bare, at its own name
    python probe_meld_identities_across_a_notch.py bare_renamed_a    # ReportServiceV2 staged at ReportService's address

The owner asked (chat 2026-10-25) whether an index owning the binding signature works for every meld or only some:
melds name a spell by spell_id, by SpellName, by class, by spellframe and binding name, through an annotation, through
a SpellMap, through a contract, and the reuse-only and purge doors take the same names. `unique` everywhere, so each
version's object shows whether versions keep their own objects across notches.
"""
import sys
from typing import Protocol

import melder as md
from melder.aether.conduit.meld.contracts.spell_map import SpellMap


class Greeter(Protocol):
    """The contract the Protocol case's versions implement."""

    def greet(self) -> str: ...


class English:
    """Version 1 of the Protocol case."""

    def greet(self) -> str:
        """Return the English greeting."""
        return "hello"


class French:
    """Version 2 of the Protocol case."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"


class ByProtocol:
    """Injected by a Protocol annotation."""

    def __init__(self, greeter: Greeter) -> None:
        self.held = greeter


class ByClass:
    """Injected by a class annotation naming English."""

    def __init__(self, greeter: English) -> None:
        self.held = greeter


class ByMapAddress:
    """Injected through a SpellMap naming the address (Greeter, 'greeter')."""

    def __init__(self, greeter: Greeter = SpellMap(spellframe=Greeter, binding_name="greeter")) -> None:
        self.held = greeter


class ByMapClass:
    """Injected through a SpellMap naming the class English."""

    def __init__(self, greeter: Greeter = SpellMap(spell=English)) -> None:
        self.held = greeter


class ReportService:
    """Version 1 of the bare cases, bound with no spellframe."""

    def run(self) -> str:
        """Return the version's report."""
        return "v1 report"


class ReportServiceV2:
    """A renamed version 2 of the bare cases."""

    def run(self) -> str:
        """Return the version's report."""
        return "v2 report (renamed class)"


def edited_report_service() -> type:
    """Return version 2 of ReportService as an edited class with the same name."""

    class ReportService:
        """Version 2 of the bare same-name case: the class edited, its name kept."""

        def run(self) -> str:
            """Return the version's report."""
            return "v2 report (same class name)"

    return ReportService


class UsesReport:
    """Injected by a class annotation naming ReportService."""

    def __init__(self, report: ReportService) -> None:
        self.held = report


def show(label: str, call) -> None:
    """Print what `call` returns, or the type and first line of what it raises."""
    try:
        print("  %-58s -> %s" % (label, call()))
    except Exception as error:
        first = str(error).splitlines()[0] if str(error) else ""
        print("  %-58s -> raises %s: %s" % (label, type(error).__name__, first[:170]))


def names(obj) -> str:
    """Name the class of an object, or of what a consumer holds, with the object's id tail."""
    target = obj.held if hasattr(obj, "held") else obj
    text = target.greet() if hasattr(target, "greet") else target.run()
    return "%s %r (object ...%s)" % (type(target).__name__, text, hex(id(target))[-5:])


def protocol_case() -> None:
    """English -> French at one address, with every meld form, an index-link borrower and a version-grant borrower."""
    lender = md.Spellbook()
    english_id = lender.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="unique",
                             permissions="create")
    consumers = {name: lender.bind(spell=cls, existence="many", permissions="create")
                 for name, cls in (("ByProtocol", ByProtocol), ("ByClass", ByClass),
                                   ("ByMapAddress", ByMapAddress), ("ByMapClass", ByMapClass))}
    world = lender.conjure(dynamic=True, name="world")
    index = world.get_spell_by_spell_id(english_id).spell_index
    french_id = world.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="greeter",
                                    existence="unique", permissions="create")
    linked = md.Spellbook().conjure(dynamic=True, name="index_borrower")
    world.link(linked)
    with linked.transaction("link", conduits=[linked, world]):
        linked.add_index_to_contract(index=index, conduit=world, permissions="create")
    granted = md.Spellbook().conjure(dynamic=True, name="grant_borrower")
    world.link(granted)
    with granted.transaction("link", conduits=[granted, world]):
        granted.add_spell_to_contract(spell_id=english_id, conduit=world, permissions="create")

    def report(when: str) -> None:
        print("[%s]" % when)
        show("lender meld(spell_id=<English>)", lambda: names(world.meld(spell_id=english_id)))
        show("lender meld(spell_id=<French>)", lambda: names(world.meld(spell_id=french_id)))
        show("lender meld(spellframe=Greeter, binding_name='greeter')",
             lambda: names(world.meld(spellframe=Greeter, binding_name="greeter")))
        show("lender meld(spell=English)  (a class)", lambda: names(world.meld(spell=English)))
        show("lender meld('English')  (a SpellName)", lambda: names(world.meld("English")))
        show("lender meld_existing_spell(spell=<English>)  (reuse-only)",
             lambda: names(world.meld_existing_spell(spell=english_id)))
        for name, spell_id in consumers.items():
            show("lender consumer %s" % name, lambda spell_id=spell_id: names(world.meld(spell_id=spell_id)))
        show("index borrower meld at (Greeter, 'greeter')",
             lambda: names(linked.meld(spellframe=Greeter, binding_name="greeter")))
        show("index borrower meld(spell_id=<English>)", lambda: names(linked.meld(spell_id=english_id)))
        show("index borrower meld(spell_id=<French>)", lambda: names(linked.meld(spell_id=french_id)))
        show("grant borrower (English granted) meld at the address",
             lambda: names(granted.meld(spellframe=Greeter, binding_name="greeter")))
        show("grant borrower meld(spell_id=<English>)", lambda: names(granted.meld(spell_id=english_id)))

    report("before: English active, French parked")
    show("notch to French", lambda: world.notch_spell(spell_index=index, spell_id=french_id).spell_name)
    report("after the notch: French active, English parked")
    show("lender has_live_creation(spell=<English>)  (parked)", lambda: world.has_live_creation(spell=english_id))
    show("lender purge(spell_id=<English>)  (parked)", lambda: world.purge(spell_id=english_id))
    show("notch back to English", lambda: world.notch_spell(spell_index=index, spell_id=english_id).spell_name)
    report("after the notch back: English active again")
    for scope in (granted, linked, world):
        scope.cleanup()


def bare_case(style: str) -> None:
    """A class bound bare, then a second version: edited with its name kept, renamed, or renamed at the old address."""
    book = md.Spellbook()
    v1_id = book.bind(spell=ReportService, existence="unique", permissions="create")
    consumer_id = book.bind(spell=UsesReport, existence="many", permissions="create")
    world = book.conjure(dynamic=True, name="world")
    index = world.get_spell_by_spell_id(v1_id).spell_index
    if style == "bare_same_name":
        v2_cls = edited_report_service()
        v2_id = world.bind_inactive(spell=v2_cls, spell_index=index, existence="unique", permissions="create")
    elif style == "bare_renamed":
        v2_cls = ReportServiceV2
        v2_id = world.bind_inactive(spell=v2_cls, spell_index=index, existence="unique", permissions="create")
    else:
        v2_cls = ReportServiceV2
        v2_id = world.bind_inactive(spell=v2_cls, spell_index=index, spellframe="ReportService",
                                    existence="unique", permissions="create")
    print("  v1 address %s/%s; v2 (%s) address %s/%s" % (
        world.get_spell_by_spell_id(v1_id)._key + (v2_cls.__name__,) + world.get_spell_by_spell_id(v2_id)._key))

    def report(when: str) -> None:
        print("[%s]" % when)
        show("meld(spell_id=<v1>)", lambda: names(world.meld(spell_id=v1_id)))
        show("meld(spell_id=<v2>)", lambda: names(world.meld(spell_id=v2_id)))
        show("meld(spell=ReportService)  (v1's class)", lambda: names(world.meld(spell=ReportService)))
        show("meld(spell=<v2's class>)", lambda: names(world.meld(spell=v2_cls)))
        show("meld('ReportService')  (a SpellName)", lambda: names(world.meld("ReportService")))
        show("meld('ReportServiceV2')  (a SpellName)", lambda: names(world.meld("ReportServiceV2")))
        show("consumer injected by the class annotation ReportService",
             lambda: names(world.meld(spell_id=consumer_id)))

    report("before: v1 active, v2 parked")
    show("notch to v2", lambda: world.notch_spell(spell_index=index, spell_id=v2_id).spell_name)
    report("after the notch: v2 active, v1 parked")
    world.cleanup()


def main() -> None:
    """Run the case named on the command line."""
    case = sys.argv[1]
    print("case %s" % case)
    if case == "protocol":
        protocol_case()
    elif case in ("bare_same_name", "bare_renamed", "bare_renamed_a"):
        bare_case(case)
    else:
        raise SystemExit("unknown case %s" % case)


if __name__ == "__main__":
    main()
