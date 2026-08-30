"""
TIER: expert (30)
GOAL: THE HALF OF A MERGE THAT JOIN REFUSES TO DO, on code the room
      actually generated. Expert 23 said it outright: "Reconciliation-by-
      content is not a join concern: compose in the codegen workshop,
      register the multi-parent result, then join." This is that
      workshop, and the material is real codegen output - not classes
      typed into this file.

      A record that merged content FOR you would be guessing about your
      source. So melder splits the act in two: you COMPOSE (here), and
      the record BOOKS the outcome (expert 23). Nothing in between.

      THE COMPOSITION VERB
        research_synthesize(base_spell_id, donor_spell_id,
                            take_functions=, take_classes=,
                            stage_ancestry=False)
      Take named top-level functions/classes from the DONOR's root module,
      splice them into the BASE's, and hand back the composed source with
      a full foresight preview. Nothing executes, binds or records - it is
      a candidate, not a version.

      SYNTHESIS IS MODULE-GRAIN. The engine says so itself: it "splices
      ONE version's module world". Each id resolves to its ROOT MODULE
      text, and `take_functions` / `take_classes` name TOP-LEVEL parts of
      that module. A METHOD is not a top-level function. Asking for one
      raises, and the refusal NAMES what the donor actually carries -
      which is how you discover the grain if you guessed wrong.

      WHICH IS WHY THIS LESSON GENERATES ITS TWO MODULES. Two classes
      typed into ONE example file resolve to the SAME module, so every
      selection is a part replaced by itself and "added" is unreachable -
      the splice degenerates into a no-op that proves nothing. Real
      composition needs two module worlds, so the room writes them:
        validate_codegen -> materialize_codegen -> import -> bind
      That is the documented loop - materialize's own contract calls
      binding the class inside the new module the step that "closes the
      codegen -> synthmodule -> bind -> crystal loop".

      AND GENERATED CODE IS THE MORE RELIABLE SOURCE, not the exotic one:
      "synthetic module sources are ALWAYS harvested; user module text
      rides the opt-in retention lane". The material a room wrote is the
      material it can always read back.

      AND THE DIFF DEFAULT IS KIND-AWARE, not a single fallback.
        research_diff(left, right, strategy=None)
      With no strategy the room asks what you handed it. Two SPELLS get
      "structural" - the room's reasoning layer - pinned for them. Two
      COMPOSITIONS get nothing pinned at all: the room passes no strategy
      and the engine's own "members" default answers. One verb, two
      vocabularies, selected by KIND. ("source" is whole-module text,
      "parts" is per-class/function grain; both are always yours by
      asking.)
      A DEFAULT IS A KINDNESS FOR SILENCE, NEVER AN OVERRIDE. Name a
      strategy and it travels down untouched - an unknown one surfaces the
      engine's KeyError rather than being quietly answered by a different
      question than the one asked.

      THE MINT IS A SEPARATE, ONE-SHOT STAMP
        research_stage_ancestry([base, donor])
        research_clear_staged_ancestry()
      Staging says "the next FRESH world entry has these parents". It is
      consumed ONCE and it is ambient, not attached to any particular
      call. A REDISCOVERY DOES NOT CONSUME IT - identical content
      re-entering the world is not the synthesized candidate arriving.
      AND THE STAMP SURVIVES UNTIL USED OR CLEARED. No scope ends it,
      which is why `clear_staged_ancestry` exists: abandon a composition
      and you must clear, or the next unrelated bind inherits parents it
      never had.
SURFACE EXERCISED: validate_codegen / materialize_codegen /
                   research_synthesize / research_stage_ancestry /
                   research_clear_staged_ancestry / research_diff
VERIFY: rides the owner's 3.14t harness; asserts are the contract.
"""
import importlib

import melder as md


FRAME = "workshop-world"
BASE_MODULE = "workshop_generated_base"
DONOR_MODULE = "workshop_generated_donor"

# THE BASE the room writes. One class, one top-level part.
BASE_SOURCE = '''"""Generated base module."""


class ReportBase:
    def __init__(self) -> None:
        self.title = "base"

    def render(self) -> str:
        return "base:" + self.title


def render_header() -> str:
    return "== report =="
'''

# THE DONOR. Same header (so a selection can REPLACE), one EXTRA
# top-level part (so a selection can ADD), and one METHOD that
# take_functions cannot see.
DONOR_SOURCE = '''"""Generated donor module."""


class ReportDonor:
    def __init__(self) -> None:
        self.title = "donor"

    def render(self) -> str:
        return "donor:" + self.title

    def summarise(self) -> str:
        return "a METHOD - invisible to take_functions"


def render_header() -> str:
    return "== donor report =="


def render_footer() -> str:
    return "-- end of report --"
'''


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

    # AN EMPTY FRAME IS A REAL FRAME. `configure_aether_frame` declares the
    # frame's LAW; `conjure` REALIZES it by giving it a root conduit, and
    # that realization is what publishes it to the Nexus. Publication is
    # gated on `rift_enabled` ALONE - the spell loop it runs iterates
    # whatever the book holds, including nothing. So the frame below is
    # conjured EMPTY and is immediately linkable; spells are cargo, not a
    # precondition, and everything bound after this arrives incrementally.
    book.conjure(name="workshop-root")

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

    # THE ROOM WRITES BOTH MODULE WORLDS. Validation gates materialization;
    # a rejected verdict registers and publishes NOTHING.
    print("THE ROOM WRITES ITS OWN MATERIAL:")
    for module_name, source in ((BASE_MODULE, BASE_SOURCE),
                                (DONOR_MODULE, DONOR_SOURCE)):
        verdict = commands.validate_codegen(source, frame_name=FRAME)
        kept = commands.materialize_codegen(
            source, module_name=module_name, frame_name=FRAME,
        )
        assert kept["materialized"] is True, kept
        print("  %-26s validate(%s) -> materialize(ok)"
              % (module_name, type(verdict).__name__))

    # The import hook is installed, so plain import resolves onto the
    # world object. THIS is what gives two spells two module worlds.
    base_module = importlib.import_module(BASE_MODULE)
    donor_module = importlib.import_module(DONOR_MODULE)

    # DISTINCT CLASS NAMES, and that is not cosmetic. These are two
    # INDEPENDENT binds, so both spells are visible at once - and two
    # visible spells sharing a name make `meld("SpellName")` ambiguous,
    # which the structural validator refuses outright. A distinct
    # binding_name alone does NOT settle it; the name itself has to
    # resolve, or the pair needs a spellframe. (Two versions on ONE
    # lineage are exempt - they are one spell, not two.)
    base = book.bind(spell=base_module.ReportBase, existence="unique",
                     permissions="create", binding_name="workshop-base")
    donor = book.bind(spell=donor_module.ReportDonor, existence="unique",
                      permissions="create", binding_name="workshop-donor")
    print("  bound from the generated modules -> custody minted")
    print("  base:", base[:12], " donor:", donor[:12])

    # THE DEFAULT IS KIND-AWARE, not a single fallback. Asked for a diff
    # with no strategy, the room checks whether BOTH sides are
    # compositions. If they are not, it pins "structural" - its reasoning
    # layer - and calls down. If they ARE, it passes NO strategy at all and
    # lets the engine's own "members" default answer. One verb, two
    # vocabularies, chosen by what you handed it.
    print()
    print("DIFF IS DERIVED, and its default is KIND-AWARE:")
    print("  spell pair       -> the room pins `structural`")
    print("  composition pair -> the room stands back; engine says `members`")
    try:
        _show("diff(default)", commands.research_diff(base, donor))
        _show("diff(source)",
              commands.research_diff(base, donor, strategy="source"))
        _show("diff(parts)",
              commands.research_diff(base, donor, strategy="parts"))
    except RuntimeError as custody:
        print("  custody read REFUSED:", str(custody)[:100])
        return
    print("  these two are spells, so `structural` was chosen FOR them")

    # AN EXPLICIT ASK IS NEVER REROUTED. The room pins a default only when
    # you supplied none; the moment you name a strategy it goes down
    # untouched, and an unknown name surfaces the engine's own KeyError
    # rather than being quietly answered by a different question.
    try:
        commands.research_diff(base, donor, strategy="no-such-strategy")
        raise AssertionError("expected the engine's KeyError")
    except KeyError as unknown:
        print("  unknown strategy -> KeyError:", str(unknown)[:70])
        print("  a default is a KINDNESS FOR SILENCE, never an override")

    # THE GRAIN, learned the way the engine teaches it. `summarise` is a
    # METHOD on the donor's Report, not a top-level function.
    print()
    print("THE WORKSHOP - compose, do not merge:")
    try:
        commands.research_synthesize(base, donor,
                                     take_functions=["summarise"])
        raise AssertionError("a method is not a top-level function")
    except ValueError as grain:
        print("  take_functions=['summarise'] REFUSED:")
        print("   ", str(grain)[:112])
        print("  the refusal NAMES the donor's real top-level parts")

    # TWO MODULE WORLDS MEAN BOTH ACTIONS ARE REACHABLE.
    replaced = commands.research_synthesize(
        base, donor, take_functions=["render_header"],
    )
    assert replaced["base_module"] != replaced["donor_module"], (
        "the whole point of generating two modules"
    )
    assert [row["action"] for row in replaced["selections"]] == ["replaced"]
    print("  take_functions=['render_header'] -> REPLACED (base had one)")

    added = commands.research_synthesize(
        base, donor, take_functions=["render_footer"],
    )
    assert [row["action"] for row in added["selections"]] == ["added"]
    assert "render_footer" in str(added["composed_source"])
    _show("synthesize", added)
    print("  take_functions=['render_footer'] -> ADDED (base had none)")
    print("  'added' is only reachable across TWO module worlds, which is")
    print("  why this lesson generates them instead of typing them here")
    print("  composed source + preview returned. NOTHING executed, bound")
    print("  or recorded - a candidate is not a version")

    # THE ANCESTRY STAMP - ambient, one-shot, survives until used.
    print()
    print("THE ANCESTRY STAMP:")
    commands.research_stage_ancestry([base, donor])
    print("  staged [base, donor] for the NEXT fresh world entry")
    commands.research_clear_staged_ancestry()
    print("  cleared without consuming - abandoning a composition without")
    print("  this is how a later, innocent bind acquires false parents")

    staged = commands.research_synthesize(
        base, donor, take_functions=["render_footer"], stage_ancestry=True,
    )
    assert staged["ancestry_staged"] is True
    print("  stage_ancestry=True stages [base, donor] in the same call")
    commands.research_clear_staged_ancestry()

    print()
    print("compose in the workshop; the record books the outcome")
    print("a version-control system that merged your source would be")
    print("guessing, and this one refuses to guess")


if __name__ == "__main__":
    main()
