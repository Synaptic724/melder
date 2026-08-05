"""
TIER: expert (30)
GOAL: THE HALF OF A MERGE THAT JOIN REFUSES TO DO. Expert 23 said it
      outright: "Reconciliation-by-content is not a join concern: compose
      in the codegen workshop, register the multi-parent result, then
      join." This is that workshop.

      A record that merged content FOR you would be guessing about your
      source. So melder splits the act in two: you COMPOSE (here), and
      the record BOOKS the outcome (expert 23). Nothing in between.

      THE COMPOSITION VERB
        research_synthesize(base_spell_id, donor_spell_id,
                            take_functions=, take_classes=,
                            stage_ancestry=False)
      Take named top-level functions/classes from the DONOR's root module,
      splice them into the BASE's, and hand back the composed source with
      a full foresight preview. Same-named parts replace, new parts
      append. Nothing executes, binds or records - it is a candidate, not
      a version.

      SYNTHESIS IS MODULE-GRAIN. The engine says so itself: it "splices
      ONE version's module world". Each id resolves to its ROOT MODULE
      text, and `take_functions` / `take_classes` name TOP-LEVEL parts of
      that module. A METHOD is not a top-level function. Asking for one
      raises, and the refusal NAMES what the donor actually carries -
      which is how you discover the grain if you guessed wrong.

      AND THE GRAIN HAS A CONSEQUENCE THIS FILE CANNOT ESCAPE. Two spells
      declared in the SAME module resolve to the SAME text, so every
      selection here is a part being replaced by itself and the composed
      candidate equals the base. That is not a bug and not a limitation
      being apologised for - it is the grain being honest. "added" is
      unreachable while base and donor share a module, and that
      unreachability is the proof that the unit is the module.
      A real composition draws its donor from a DIFFERENT module.

      AND THE MINT IS A SEPARATE, ONE-SHOT STAMP
        research_stage_ancestry([base, donor])
        research_clear_staged_ancestry()
      Staging says "the next FRESH world entry has these parents". It is
      consumed ONCE and it is ambient, not attached to any particular
      call - the campaign pattern. `stage_ancestry=True` on synthesize is
      the convenience that stages [base, donor] for you.

      TWO THINGS THAT LOOK LIKE BUGS AND ARE NOT
      A REDISCOVERY DOES NOT CONSUME THE STAMP. Identical content
      re-entering the world is not the synthesized candidate arriving, so
      the stamp is re-staged untouched and waits for the real thing.
      AND THE STAMP SURVIVES UNTIL USED OR CLEARED. There is no scope
      that ends it, which is why `clear_staged_ancestry` exists: abandon
      a composition and you must clear, or the next unrelated bind
      inherits parents it never had.

      DIFF IS DERIVED, AND THE ROOM PICKS A DEFAULT
        research_diff(left, right, strategy=None)
      For a spell pair the room defaults to "structural" - its reasoning
      layer. "source" is whole-module text, "parts" is per-class/function
      grain. An explicit UNKNOWN strategy surfaces the engine's KeyError
      rather than being quietly rerouted: the room never silently answers
      a different question than the one asked.
SURFACE EXERCISED: research_synthesize / research_stage_ancestry /
                   research_clear_staged_ancestry / research_diff,
                   Conduit.bind_inactive
VERIFY: rides the owner's 3.14t harness; asserts are the contract.
"""
import melder as md


FRAME = "workshop-world"


class ReportBase:
    def __init__(self) -> None:
        self.title = "base"

    def render(self) -> str:
        return "base:%s" % self.title


class ReportDonor:
    def __init__(self) -> None:
        self.title = "donor"

    def render(self) -> str:
        return "donor:%s" % self.title

    def summarise(self) -> str:
        return "the part worth taking"


def render_footer() -> str:
    """A TOP-LEVEL function - the grain synthesis actually works at.

    `ReportDonor.summarise` above is a METHOD and is invisible to
    `take_functions`; this is not.
    """
    return "-- end of report --"


def _show(label: str, value: object) -> None:
    if isinstance(value, dict):
        print("  %-24s -> dict, keys: %s" % (label, sorted(value)[:5]))
    elif isinstance(value, list):
        print("  %-24s -> list, %d row(s)" % (label, len(value)))
    else:
        print("  %-24s -> %s" % (label, type(value).__name__))


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
    base = book.bind(spell=ReportBase, existence="unique",
                     permissions="create", binding_name="workshop-base")
    conduit = book.conjure(name="workshop-root")

    # A donor version on the same lineage - two recorded versions is the
    # minimum a composition needs.
    donor = conduit.bind_inactive(
        spell=ReportDonor,
        spell_index=conduit.get_spell_by_id(base).spell_index,
        existence="unique", permissions="create",
    )
    print("base:", base[:12], " donor:", donor[:12])

    nexus = md.Nexus()
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    system_configuration.with_allowed_target_frame_names([FRAME])
    nexus.activate(system_configuration)
    rift_configuration = nexus.create_rift_configuration()
    rift_configuration.with_space_type("codegen")
    rift = nexus.create_rift(configuration=rift_configuration,
                             rift_name="workshop")
    rift.mark_active()
    rift.create_frame_link(FRAME)
    commands = rift.space.command_system

    # DERIVED DIFF FIRST - understand the two sides before composing.
    print()
    print("DIFF IS DERIVED, and the room defaults to `structural`:")
    try:
        _show("diff(default)", commands.research_diff(base, donor))
        _show("diff(source)",
              commands.research_diff(base, donor, strategy="source"))
        _show("diff(parts)",
              commands.research_diff(base, donor, strategy="parts"))
    except RuntimeError as custody:
        print("  custody read REFUSED:", str(custody)[:100])
        print("  these are recorded-material reads; without custody there")
        print("  is nothing to compare. The laws above still hold")
        return

    # AN UNKNOWN STRATEGY IS NOT REROUTED - the room surfaces the engine's
    # KeyError rather than quietly answering a different question.
    try:
        commands.research_diff(base, donor, strategy="no-such-strategy")
        raise AssertionError("expected the engine's KeyError")
    except KeyError as unknown:
        print("  unknown strategy -> KeyError:", str(unknown)[:70])

    # THE COMPOSITION. But first: the grain, learned the way the engine
    # teaches it. `summarise` is a METHOD on ReportDonor, not a top-level
    # function, so this refuses and NAMES what the donor really carries.
    print()
    print("THE WORKSHOP - compose, do not merge:")
    try:
        commands.research_synthesize(base, donor,
                                     take_functions=["summarise"])
        raise AssertionError("a method is not a top-level function")
    except ValueError as grain:
        print("  take_functions=['summarise'] REFUSED:")
        print("   ", str(grain)[:118])
        print("  the refusal NAMES the donor's real top-level parts - that")
        print("  is how you find the grain when you guessed wrong")

    # THE GRAIN'S CONSEQUENCE. Both spells were declared in THIS module,
    # so both resolve to THIS file. Base text and donor text are the same
    # text, which makes every selection a replace and the candidate equal
    # to the base.
    synthesis = commands.research_synthesize(
        base, donor, take_functions=["render_footer"],
    )
    _show("synthesize", synthesis)
    assert synthesis["base_module"] == synthesis["donor_module"], (
        "both spells live in this file, so both resolve to this module"
    )
    actions = [row["action"] for row in synthesis["selections"]]
    assert actions == ["replaced"], actions
    print("  base_module == donor_module -> the SAME text on both sides")
    print("  selection action:", actions[0], "- a part replaced by itself")
    print("  'added' is unreachable while base and donor share a module,")
    print("  and that unreachability IS the proof the unit is the module")
    print("  composed source + preview returned. NOTHING executed, bound")
    print("  or recorded - a candidate is not a version")

    # THE MINT IS A SEPARATE STAMP, and it is ambient + one-shot.
    print()
    print("THE ANCESTRY STAMP - ambient, one-shot, survives until used:")
    commands.research_stage_ancestry([base, donor])
    print("  staged [base, donor] for the NEXT fresh world entry")

    # Abandon the composition and the stamp MUST be cleared, or an
    # unrelated bind inherits parents it never had.
    commands.research_clear_staged_ancestry()
    print("  cleared without consuming - abandoning a composition without")
    print("  this is how a later, innocent bind acquires false parents")

    # The convenience form stages both parents as part of the compose.
    staged_synthesis = commands.research_synthesize(
        base, donor, take_functions=["render_footer"], stage_ancestry=True,
    )
    assert staged_synthesis["ancestry_staged"] is True
    _show("synthesize(staged)", staged_synthesis)
    print("  stage_ancestry=True stages [base, donor] in the same call")
    commands.research_clear_staged_ancestry()

    print()
    print("compose in the workshop; the record books the outcome")
    print("a version-control system that merged your source would be")
    print("guessing, and this one refuses to guess")


if __name__ == "__main__":
    main()
