"""
TIER: expert (29)
GOAL: THE CRYSTAL WELL - reading the code your world RECORDED, at four
      grains, and the one comparison law that makes any of it trustworthy.

      Expert 04 said diffs are derived, never stored. This is the other
      half: what they are derived FROM. A recorded world keeps its own
      source, and you can ask it questions at four different sizes.

      THE FOUR GRAINS, WIDEST TO NARROWEST

        research_source(spell_id)              the whole module WORLD
        research_module(spell_id, module_name) ONE module, full dossier
        research_parts(spell_id)               every top-level part, with code
        research_part(spell_id, part_name)     ONE named class/function

      They are not four ways to do one thing. `research_parts` is the
      INVENTORY - it needs no names up front, which is what you want when
      you do not yet know what is in there. `research_part` is the
      lookup, for when you do. `research_module` is the one-call dossier:
      text, fingerprint, path, dependencies BOTH ways, export surface and
      drift together, because those are the facts you always want at once
      and separately fetching them is five calls and a join.

      THE COMPARISON LAW, AND IT IS THE POINT OF THE LESSON
      `research_part_diff(left, right, part)` compares RECORDED MATERIAL
      ONLY. It never reads the live disk, and that refusal is not
      caution - it is correctness. Both sides of a version comparison
      would read the SAME present-day file, so a disk-backed diff would
      report "no change" between two genuinely different versions and be
      confidently wrong about both. The record is the only place where
      two versions exist at the same time.

      DIFF MATERIAL DRINKS BOTH CARRIERS: synthetic sources first,
      user-retained text filling the gaps, so the comparison speaks the
      FULL module whether the code was generated or written by hand.

      AND IMPACT STAYS MODULE-GRAIN ON PURPOSE. `research_impact` answers
      a blast radius joined with research residency - and a PART's honest
      radius IS its module's radius, because nothing imports half a file.
      A part-grain radius would be a smaller number that means nothing.

      CUSTODY IS REQUIRED AND THE REFUSAL IS LOUD. These are custody
      reads: they answer from the recorded world, so an absent or
      inactive crystallizer raises rather than quietly returning empty.
      That is deliberate - a silent empty read is indistinguishable from
      "this world has no code", which is the one answer that is never
      true. This lesson catches that refusal and says so rather than
      pretending every environment can serve it.
SURFACE EXERCISED: research_source / research_module / research_parts /
                   research_part / research_part_diff /
                   research_module_graph / research_source_drift /
                   research_impact / research_residency /
                   research_history / research_recent
VERIFY: NOT RUN by the authoring agent - this sandbox is Python 3.10 and
        melder requires >=3.14. Rides the owner's 3.14t harness.
"""
import melder as md


FRAME = "well-world"


class PricingV1:
    """The version the record will remember first."""

    def __init__(self) -> None:
        self.rate = 10

    def quote(self, units: int) -> int:
        return self.rate * units


class PricingV2:
    """A second version, so there is something to compare against."""

    def __init__(self) -> None:
        self.rate = 25

    def quote(self, units: int) -> int:
        return (self.rate * units) + 5


def _show(label: str, value: object) -> None:
    """Print a read's shape without pretending to know its schema."""
    if isinstance(value, dict):
        print("  %-22s -> dict, keys: %s" % (label, sorted(value)[:6]))
    elif isinstance(value, list):
        print("  %-22s -> list, %d row(s)" % (label, len(value)))
    else:
        print("  %-22s -> %s" % (label, type(value).__name__))


def main() -> None:
    # 1. CUSTODY FIRST. These are custody reads; a world that was never
    #    recorded has nothing to answer with.
    crystallizer = md.Crystallizer()
    crystallizer.activate(
        md.CrystallizerConfigurationBuilder().with_defaults().activate(),
    )
    research = md.MutationResearch()
    research_configuration = research.create_configuration()
    research_configuration.with_defaults().activate()
    research.activate(research_configuration)
    print("custody recording:", crystallizer.activated)

    # 2. A RECORDED WORLD, born configured, posture before bind.
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
    v1 = book.bind(spell=PricingV1, existence="unique", permissions="create",
                   binding_name="well-pricing")
    conduit = book.conjure(name="well-root")

    # A SECOND VERSION on the same lineage, so the diff has two sides.
    v2 = conduit.bind_inactive(
        spell=PricingV2,
        spell_index=conduit.get_spell_by_id(v1).spell_index,
        existence="unique",
        permissions="create",
    )
    module_name = PricingV1.__module__
    print("two versions recorded:", v1[:12], "and", v2[:12])
    print("both live in module:", module_name)

    # 3. THE ROOM. The research family lives on the codegen room.
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

    # 4. THE FOUR GRAINS. Wrapped once: custody-unavailable refuses LOUD,
    #    and an environment that cannot serve these should say so rather
    #    than have the lesson pretend.
    print()
    print("THE FOUR GRAINS, widest to narrowest:")
    try:
        _show("source(world)", commands.research_source(v1))
        _show("source(one module)",
              commands.research_source(v1, module_name=module_name))
        _show("module(dossier)", commands.research_module(v1, module_name))
        _show("parts(inventory)", commands.research_parts(v1))
        _show("part(one lookup)",
              commands.research_part(v1, "PricingV1", kind="class"))
    except RuntimeError as custody:
        print("  custody read REFUSED:", str(custody)[:110])
        print("  LOUD is correct here: a silent empty read is")
        print("  indistinguishable from `this world has no code`, which is")
        print("  the one answer that is never true")
        print()
        print("the grains and the comparison law still hold - see the")
        print("module docstring; this environment just cannot serve them")
        return

    print("  parts needs NO names up front - it is the inventory you reach")
    print("  for before you know what is in there; part is the lookup for")
    print("  when you do; module is the one-call dossier (text, fingerprint,")
    print("  path, deps BOTH ways, exports, drift) so you stop doing joins")

    # 5. AN HONEST MISS IS A VALUE, NOT AN EXCEPTION.
    missing = commands.research_part(v1, "NoSuchPartAnywhere")
    _show("part(absent)", missing)
    print("  a name that is not there answers honestly rather than raising -")
    print("  absence is a real result when you are exploring a world")

    # 6. THE COMPARISON LAW. Two versions, one named part, recorded
    #    material only.
    print()
    print("THE COMPARISON LAW:")
    _show("part_diff(v1, v2)",
          commands.research_part_diff(v1, v2, "quote", kind="function"))
    _show("part_diff(class)",
          commands.research_part_diff(v1, v2, "PricingV1", kind="class"))
    print("  RECORDED MATERIAL ONLY - never the live disk. Both sides would")
    print("  read the SAME present-day file, so a disk-backed diff would")
    print("  report `no change` between two genuinely different versions")
    print("  and be confidently wrong about both. The record is the only")
    print("  place where two versions exist at the same time")

    # 7. THE JOINS. A radius is only useful if you know WHO it hits.
    print()
    print("THE JOINS:")
    _show("module_graph", commands.research_module_graph(v1))
    _show("impact(by spell)", commands.research_impact(spell_id=v1))
    _show("impact(by module)",
          commands.research_impact(module_name=module_name))
    print("  impact stays MODULE-GRAIN on purpose: a part's honest radius")
    print("  IS its module's radius, because nothing imports half a file.")
    print("  A part-grain number would be smaller and mean nothing")

    # 8. THE RECORD READS - where a version lives and what happened to it.
    print()
    print("THE RECORD READS:")
    _show("residency(v1)", commands.research_residency(v1))
    _show("history(v1)", commands.research_history(v1))
    _show("recent(limit=5)", commands.research_recent(limit=5))
    print("  residency answers WHERE a version lives (declared lane +")
    print("  runtime state + custody); history answers WHAT HAPPENED to it;")
    print("  recent is the cold-landing read - the newest window, for an")
    print("  agent that just arrived and has no id to start from")

    # 9. DRIFT. The record knows what it sealed; the disk may have moved.
    print()
    _show("source_drift()", commands.research_source_drift())
    print("  recorded-vs-disk for every sealed module, with a radius for")
    print("  each one that is not unchanged. This is how a restore ANNOUNCES")
    print("  that your working tree diverged from the sealed world before")
    print("  it builds anything")

    print()
    print("four grains: world, module, inventory, part")
    print("comparison drinks the RECORD, never the disk - two versions only")
    print("exist at the same time in one place, and that place is the record")


if __name__ == "__main__":
    main()
