"""
TIER: expert (25)
GOAL: RESEARCH SETS, PLURAL. Everything so far used the default set and
      never said there was a choice. A ResearchSet is a whole INDEPENDENT
      BODY OF HISTORY over the same runtime - its own lanes, its own
      residency, its own journal, its own campaigns.

        research.create_research_set("refactor-2026")
        research.list_research_set_names()
        research.research_set("refactor-2026")

      WHY MORE THAN ONE
      Lanes branch a line of versions. A SET is the thing lanes live in -
      so two sets are two entirely separate investigations that happen to
      be looking at the same world. Expert 23's join can never cross
      them, residency is per set, and a lane name in one set says nothing
      about a lane name in the other. Two agents auditing the same
      runtime for different reasons do not have to agree on a lane
      vocabulary, or even know about each other.

      EVERY RESEARCH VERB TAKES `set_name`, AND IT DEFAULTS
      Root-level reads and writes carry `set_name="default"`. That is why
      the first twenty-odd lessons never mentioned sets: the default was
      doing the work silently. The moment you have two, the argument
      stops being decoration.

      AN UNKNOWN SET NAME RAISES, AND THE ERROR LISTS THE KNOWN ONES
      This is a small thing that matters enormously to an agent. A typo
      does not return an empty set that looks like "no history here" -
      it refuses AND tells you what does exist, so the next call is
      correct instead of being another guess. Compare with a silent
      empty: an agent would conclude the world had no record and act on
      it.

      AND OMITTING THE NAME RESOLVES THE DEFAULT, NOT ALL SETS.
      `research_set()` is "the default one", never "every one" - so the
      cheap call is scoped rather than sweeping, and nothing accidentally
      reports across investigations that were meant to stay apart.

      THE WORLD IS SHARED; THE RECORD IS NOT
      The spells, the frames, the conduits - one runtime, seen by both.
      What differs is what each set has DECLARED about it. A version can
      be resident in one set and unknown to another, and neither is
      wrong: a research set records what an investigation chose to look
      at, not everything that exists.
SURFACE EXERCISED: MutationResearch.create_research_set /
                   list_research_set_names / research_set, per-set lanes
                   and residency, and the set_name argument on the root
                   research verbs
VERIFY: rides the owner's 3.14t harness; asserts are the contract.
"""
import melder as md


FRAME = "many-sets-world"


class Invoice:
    def __init__(self) -> None:
        self.total = 0


def main() -> None:
    crystallizer = md.Crystallizer()
    crystallizer.activate(
        md.CrystallizerConfigurationBuilder().with_defaults().activate(),
    )
    research = md.MutationResearch()
    configuration = research.create_configuration()
    configuration.with_defaults().activate()
    research.activate(configuration)

    # ONE WORLD. Both investigations will look at exactly this.
    # A RECORDED WORLD MUST BE BORN CONFIGURED. With custody active, a
    # dynamic conjure REFUSES if any bind ran before the configuration
    # was finalized - the profile record and default bootstrap would
    # otherwise durably persist binds made against unsettled config.
    spellbook_configuration = (
        md.SpellbookConfiguration(FRAME).with_defaults().finalize()
    )
    book = md.Spellbook(aetheric_frame=FRAME,
                        configuration=spellbook_configuration)
    invoice_id = book.bind(
        spell=Invoice, existence="unique", permissions="create",
        binding_name="sets-invoice",
    )
    book.configure_aether_frame(
        system_state="dynamic",
        disposal=None,
        disposal_method_names=None,
    )
    book.conjure(name="sets-root")
    print("one world, one spell:", invoice_id[:12], "...")

    # THE DEFAULT SET WAS ALWAYS THERE - every earlier lesson used it
    # without naming it.
    names = research.list_research_set_names()
    print()
    print("research sets at start:", names)
    assert "default" in names

    # A SECOND INVESTIGATION. Its own lanes, journal, residency.
    research.create_research_set("refactor-2026")
    research.create_research_set("security-audit")
    names = research.list_research_set_names()
    print("after creating two more:", names)
    assert {"default", "refactor-2026", "security-audit"} <= set(names)

    refactor = research.research_set("refactor-2026")
    audit = research.research_set("security-audit")
    assert refactor is not audit

    # LANE VOCABULARIES DO NOT COLLIDE ACROSS SETS. Both investigations
    # can call a lane "candidate" and mean different things.
    refactor.create_lane("candidate", lane_type="experiment")
    audit.create_lane("candidate", lane_type="test")
    print()
    print("both sets have a lane called 'candidate' - and they are")
    print("different lanes in different histories")

    # DECLARE THE SPELL IN ONE SET ONLY. This is the crux: a version can
    # be resident in one investigation and unknown to another.
    refactor.register_spell(invoice_id, lane="candidate",
                            reason="under refactor review")
    assert refactor.residence_of(invoice_id) is not None
    assert audit.residence_of(invoice_id) is None
    print()
    print("declared in 'refactor-2026'   -> resident")
    print("not declared in 'security-audit' -> residence_of is None")
    print("  neither is wrong. A set records what an investigation chose")
    print("  to look at, not everything that exists")

    # THE SAME QUESTION, ASKED OF EACH SET, GIVES DIFFERENT ANSWERS.
    # `walk(lane)` returns that lane's line of versions plus its ancestry
    # hop - so the same lane NAME in two sets walks two different lines.
    refactor_walk = refactor.walk("candidate")
    audit_walk = audit.walk("candidate")
    assert isinstance(refactor_walk, list)
    print()
    print("walk('candidate') in each set:")
    print("   refactor-2026  ->", len(refactor_walk), "version(s)")
    print("   security-audit ->", len(audit_walk), "version(s)")
    assert len(refactor_walk) == 1 and len(audit_walk) == 0, (
        "the spell was declared in one investigation only"
    )
    # Each node payload carries its lane identity alongside the node
    # fields, so a walked row is self-describing.
    row = refactor_walk[0]
    print("   a walked row carries:", sorted(row)[:5], "...")
    print("  same lane name, two histories, and neither can see the other")

    # A TYPO REFUSES AND NAMES WHAT EXISTS. This is the difference
    # between an agent self-correcting and an agent inventing.
    try:
        research.research_set("refactor-2025")
        raise AssertionError("expected a refusal on an unknown set name")
    except Exception as error:
        message = str(error)
        print()
        print("research_set('refactor-2025') refused -")
        print("  ", message[:130])
        assert "refactor-2026" in message or "default" in message, (
            "the refusal must LIST the known names, or a typo is just a "
            "dead end"
        )
        print("  it listed the real names, so the next call is correct")
        print("  rather than another guess. An empty return here would")
        print("  have read as 'this world has no history'")

    # AND THE BARE CALL IS THE DEFAULT, NEVER ALL OF THEM.
    default_set = research.research_set()
    assert default_set is research.research_set("default")
    print()
    print("research_set() with no name IS the default set - scoped, not")
    print("sweeping, so nothing reports across investigations by accident")

    print()
    print("lanes branch a line; a SET is the world those lanes live in")
    print("one runtime, several independent records of it")


if __name__ == "__main__":
    main()
