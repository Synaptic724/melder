"""
TIER: expert (29)
GOAL: THE CRYSTAL WELL - reading the code your world RECORDED, at four
      grains, and the one comparison law that makes any of it
      trustworthy. Expert 04 said diffs are derived, never stored. This
      is what they are derived FROM.

      THE FOUR GRAINS, WIDEST TO NARROWEST
        research_source(spell_id)               the whole module WORLD
        research_module(spell_id, module_name)  ONE module, full dossier
        research_parts(spell_id)                every part, with code
        research_part(spell_id, part_name)      ONE named class/function

      They are not four ways to do one thing. `research_parts` is the
      INVENTORY - it needs no names up front, which is exactly what you
      want before you know what is in there. `research_part` is the
      lookup for when you do. `research_module` is the one-call dossier:
      text, fingerprint, path, dependencies BOTH ways, export surface and
      drift together, because separately fetching those is five calls and
      a join.

      THE COMPARISON LAW, AND IT IS THE POINT
      `research_part_diff(left, right, part)` compares RECORDED MATERIAL
      ONLY and never the live disk. That refusal is correctness, not
      caution: both sides of a version comparison would read the SAME
      present-day file, so a disk-backed diff would report "no change"
      between two genuinely different versions and be confidently wrong
      about both. The record is the only place where two versions exist
      at the same time. Diff material drinks BOTH carriers - synthetic
      first, user-retained filling the gaps - so it speaks the full
      module whether the code was generated or hand-written.

      IMPACT STAYS MODULE-GRAIN ON PURPOSE. A part's honest blast radius
      IS its module's radius, because nothing imports half a file. A
      part-grain number would be smaller and mean nothing.

      CUSTODY IS REQUIRED AND THE REFUSAL IS LOUD. These read from the
      recorded world, so an absent or inactive crystallizer raises rather
      than returning empty - a silent empty read is indistinguishable
      from "this world has no code", which is never true. This lesson
      catches that refusal and says so rather than pretending every
      environment can serve it.
SURFACE EXERCISED: research_source / research_module / research_parts /
                   research_part / research_part_diff /
                   research_module_graph / research_source_drift /
                   research_impact / research_residency /
                   research_history / research_recent
VERIFY: rides the owner's 3.14t harness; asserts are the contract.
"""
import importlib

import melder as md


FRAME = "well-world"
MODULE_V1 = "well_pricing_v1"
MODULE_V2 = "well_pricing_v2"

# TWO GENERATED MODULE WORLDS, so the comparison below has two genuinely
# different recorded texts to read. Two classes typed into THIS file would
# share one module and one snapshot - both sides of every diff would be
# the same bytes, and the comparison law would demonstrate nothing.
# Generated source is also the RELIABLE lane here: synthetic module
# sources are ALWAYS harvested, while user module text rides the opt-in
# retention lane.
SOURCE_V1 = '''"""Recorded pricing, first version."""


class Pricing:
    def __init__(self) -> None:
        self.rate = 10


def quote(units: int) -> int:
    return 10 * units
'''

SOURCE_V2 = '''"""Recorded pricing, second version."""


class Pricing:
    def __init__(self) -> None:
        self.rate = 25
        self.surcharge = 5


def quote(units: int) -> int:
    return (25 * units) + 5
'''


def _show(label: str, value: object) -> None:
    """Print a read's shape without pretending to know its schema."""
    if isinstance(value, dict):
        print("  %-22s -> dict, keys: %s" % (label, sorted(value)[:5]))
    elif isinstance(value, list):
        print("  %-22s -> list, %d row(s)" % (label, len(value)))
    else:
        print("  %-22s -> %s" % (label, type(value).__name__))


def main() -> None:
    crystallizer = md.Crystallizer()
    crystallizer.activate(
        md.CrystallizerConfigurationBuilder().with_defaults().activate(),
    )
    research = md.MutationResearch()
    configuration = research.create_configuration()
    configuration.with_defaults().activate()
    research.activate(configuration)

    spellbook_configuration = (
        md.SpellbookConfiguration(FRAME).with_defaults().finalize()
    )
    book = md.Spellbook(aetheric_frame=FRAME,
                        configuration=spellbook_configuration)
    book.configure_aether_frame(
        system_state="dynamic",
        disposal=None,
        disposal_method_names=None,
        rift_enabled=True,
        ai_native=True,
    )
    # AN EMPTY FRAME IS A REAL FRAME. `configure_aether_frame` declares the
    # frame's LAW; `conjure` REALIZES it by giving it a root conduit, and
    # that realization is what publishes it to the Nexus. Publication is
    # gated on `rift_enabled` ALONE - the spell loop it runs iterates
    # whatever the book holds, including nothing. So the frame below is
    # conjured EMPTY and is immediately linkable; spells are cargo, not a
    # precondition, and everything bound after this arrives incrementally.
    conduit = book.conjure(name="well-root")

    nexus = md.Nexus()
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    system_configuration.with_allowed_target_frame_names([FRAME])
    nexus.activate(system_configuration)
    rift_configuration = nexus.create_rift_configuration()
    rift_configuration.with_space_type("codegen")
    rift = nexus.create_rift(configuration=rift_configuration,
                             rift_name="weller")
    rift.mark_active()
    rift.create_frame_link(FRAME)
    commands = rift.space.command_system

    # Now the room can write both module worlds.
    for module_name_to_make, source in ((MODULE_V1, SOURCE_V1),
                                        (MODULE_V2, SOURCE_V2)):
        commands.validate_codegen(source, frame_name=FRAME)
        kept = commands.materialize_codegen(
            source, module_name=module_name_to_make, frame_name=FRAME,
        )
        assert kept["materialized"] is True, kept
    first = importlib.import_module(MODULE_V1)
    second = importlib.import_module(MODULE_V2)

    # TWO VERSIONS ON ONE LINEAGE, FROM TWO MODULE WORLDS - which is what
    # gives the comparison below two genuinely different sides. The first
    # bind lands in the already-conjured frame and publishes incrementally;
    # the second rides its spell_index as a VERSION rather than a second
    # visible spell, which is why two classes named `Pricing` never collide.
    v1 = book.bind(spell=first.Pricing, existence="unique",
                   permissions="create", binding_name="well-pricing")
    v2 = conduit.bind_inactive(
        spell=second.Pricing,
        spell_index=conduit.get_spell_by_id(v1).spell_index,
        existence="unique", permissions="create",
    )
    module_name = MODULE_V1
    print("two versions recorded:", v1[:12], "and", v2[:12])
    print("v1 module:", MODULE_V1, "| v2 module:", MODULE_V2)

    print()
    print("THE FOUR GRAINS, widest to narrowest:")
    try:
        _show("source(world)", commands.research_source(v1))
        _show("source(one module)",
              commands.research_source(v1, module_name=module_name))
        _show("module(dossier)", commands.research_module(v1, module_name))
        _show("parts(inventory)", commands.research_parts(v1))
        _show("part(one lookup)",
              commands.research_part(v1, "Pricing", kind="class"))
    except RuntimeError as custody:
        print("  custody read REFUSED:", str(custody)[:100])
        print("  LOUD is correct: a silent empty read would be")
        print("  indistinguishable from `this world has no code`")
        return

    # PARTS ARE TOP-LEVEL ONLY, and a miss is a VALUE, not an exception.
    # `__init__` is a method, so it is invisible to this grain - and the
    # read says so honestly rather than raising.
    absent = commands.research_part(v1, "NoSuchPartAnywhere")
    method = commands.research_part(v1, "__init__", kind="function")
    assert absent["found"] is False
    assert method["found"] is False, "parts are TOP-LEVEL; __init__ is not"
    _show("part(absent)", absent)
    _show("part(a method)", method)
    print("  absence is a real result when you are exploring a world you")
    print("  do not know - so a miss returns `found: False`, never raises")

    print()
    print("THE COMPARISON LAW - recorded material only, never the disk:")
    function_diff = commands.research_part_diff(v1, v2, "quote",
                                                kind="function")
    class_diff = commands.research_part_diff(v1, v2, "Pricing", kind="class")
    _show("part_diff(function)", function_diff)
    _show("part_diff(class)", class_diff)
    print("  both sides came from DIFFERENT module worlds, so this is a")
    print("  real comparison. Two versions typed into one file would share")
    print("  one snapshot and diff identical bytes - the law would hold and")
    print("  demonstrate nothing")

    print()
    print("THE JOINS - a radius is only useful if you know WHO it hits:")
    _show("module_graph", commands.research_module_graph(v1))
    _show("impact(by spell)", commands.research_impact(spell_id=v1))
    _show("impact(by module)",
          commands.research_impact(module_name=module_name))

    print()
    print("THE RECORD READS - where a version lives, and what happened:")
    _show("residency(v1)", commands.research_residency(v1))
    _show("history(v1)", commands.research_history(v1))
    _show("recent(limit=5)", commands.research_recent(limit=5))
    print("  residency answers WHERE a version lives; history answers WHAT")
    print("  HAPPENED to it; recent is the cold-landing read for an agent")
    print("  that just arrived with no id to start from")

    print()
    _show("source_drift()", commands.research_source_drift())
    print("  recorded-vs-disk for every sealed module, with a radius for")
    print("  each one that moved - how a restore ANNOUNCES divergence")
    print("  before it builds anything")

    print()
    print("four grains: world, module, inventory, part")
    print("comparison drinks the RECORD, never the disk - two versions only")
    print("exist at the same time in one place, and that place is the record")


if __name__ == "__main__":
    main()
