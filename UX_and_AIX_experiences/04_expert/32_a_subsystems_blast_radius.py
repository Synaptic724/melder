"""
TIER: expert (32)
GOAL: ASK A WHOLE SUBSYSTEM WHAT IT WOULD BREAK. Expert 14 built
      compositions - a set of versions pinned as one unit. This asks the
      two questions you actually have about one: how far does it reach,
      and has the ground moved under it.

        research_group_impact(group_id)   the union blast radius
        research_group_drift(group_id)    recorded-vs-disk, narrowed

      IMPACT IS A UNION WITH CLOSURE MATH, NOT A SUM. It merges every
      member's radius and then splits the result INTERNAL vs OUTBOUND:
      how much of the blast lands back inside the composition, and how
      much escapes it. The closure fraction is the number that matters -
      a subsystem with high closure is one you can change on its own
      terms, and a low one is a subsystem in name only, whose edges are
      really everyone else's problem.
      It also lifts to composition grain: the radius names the other
      compositions it touches (`affected_compositions`), so "what else
      does this subsystem hit" is answerable in subsystem vocabulary
      rather than as a flat list of spells.

      DRIFT IS THE SAME REPORT AS `research_source_drift`, NARROWED TO
      THE FOOTPRINT - and the narrowing is the point. A whole-world drift
      report on a real repository is mostly other people's churn. Asked
      about ONE subsystem, the counts are recomputed over that
      subsystem's modules only, so the answer is about your area rather
      than about the repository's mood.

      COMPOSITIONS ARE INFORMATIONAL, WHICH IS WHY THESE ARE CHEAP TO
      ASK. A composition pins members by reference; it carries no custody
      crystal of its own, gates nothing and never executes. Both of these
      verbs are derived reads over the members' recorded material - there
      is no subsystem-shaped thing at runtime to disturb.

      AND THE FOOTPRINT IS HONEST ABOUT WHAT IT CANNOT SEE. A member
      whose custody is unknown is reported as unknown rather than
      silently contributing nothing - a shadow with a hole in it that
      claimed to be complete would be worse than no shadow.

      EVOLVING ONE IS ADD/REMOVE, NOT REPLACEMENT. `recompose` says it
      outright - "unlisted members are retained" - so dropping a member is
      a one-word ask rather than a re-declaration of the roster. The
      previous composition is untouched by it, because identity is
      content-addressed over the members: a different roster is simply a
      DIFFERENT composition, not an edited one.

      AND IT COMPLETES EXPERT 30'S DIFF LAW. There you met `research_diff`
      on two SPELLS, where the room pins `structural` for you. Hand the
      same verb two COMPOSITIONS and it pins NOTHING - it stands back and
      lets the engine's `members` default answer, because the useful
      question about two subsystems is which MEMBERS changed, not how
      their text reads. One verb, two vocabularies, chosen by kind.
SURFACE EXERCISED: validate_codegen / materialize_codegen,
                   research_group_register / research_group_recompose /
                   research_group_impact / research_group_drift /
                   research_group_footprint / research_group_view /
                   research_group_diff / research_diff
VERIFY: rides the owner's 3.14t harness; asserts are the contract.
"""
import importlib

import melder as md


FRAME = "subsystem-world"

# THREE GENERATED MODULE WORLDS. A subsystem whose members all live in one
# file has a ONE-module footprint, and a union over one module is not a
# union - the internal/outbound split has nothing to split. Generating
# three gives the radius something real to measure.
MEMBERS = (
    ("sub_intake", "Intake", "intake"),
    ("sub_ledger", "Ledger", "ledger"),
    ("sub_report", "Report", "report"),
)

MEMBER_TEMPLATE = '''"""Generated subsystem member."""


class {class_name}:
    def __init__(self) -> None:
        self.name = "{label}"

    def run(self) -> str:
        return "{label}:ok"
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
    book.conjure(name="subsystem-root")

    nexus = md.Nexus()
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    system_configuration.with_allowed_target_frame_names([FRAME])
    nexus.activate(system_configuration)
    rift_configuration = nexus.create_rift_configuration()
    rift_configuration.with_space_type("codegen")
    rift = nexus.create_rift(configuration=rift_configuration,
                             rift_name="subsystem")
    rift.mark_active()
    rift.create_frame_link(FRAME)

    # THE RIFT OWNS EXACTLY ONE SPACE. `RiftSpace` is a type you RECEIVE,
    # never one you construct - which is why the same object comes back
    # every time rather than a fresh space per read.
    assert isinstance(rift.space, md.RiftSpace)
    assert rift.space is rift.space
    commands = rift.space.command_system

    # THREE members, each its own module world, so the footprint is three
    # modules and the union has something to be a union OF.
    member_ids = []
    for module_name, class_name, label in MEMBERS:
        source = MEMBER_TEMPLATE.format(class_name=class_name, label=label)
        commands.validate_codegen(source, frame_name=FRAME)
        kept = commands.materialize_codegen(
            source, module_name=module_name, frame_name=FRAME,
        )
        assert kept["materialized"] is True, kept
        module = importlib.import_module(module_name)
        member_ids.append(book.bind(
            spell=getattr(module, class_name), existence="unique",
            permissions="create", binding_name=module_name.replace("_", "-"),
        ))
    intake, ledger, report = member_ids
    print("three versions declared from three module worlds:",
          intake[:10], ledger[:10], report[:10])

    # PIN THEM AS ONE UNIT. Identity is content-addressed over the
    # canonical member list, so the same roster is the same composition.
    composition = commands.research_group_register(
        [intake, ledger, report],
        reason="the intake -> ledger -> report subsystem",
    )
    # THE TAG IS THE DISPATCH. A payload carrying node_type "group"
    # rehydrates as a composition; an UNTAGGED one is a spell node. That
    # is back-compat by ABSENCE - payloads sealed before compositions
    # existed carry no tag and correctly rebuild as spell nodes.
    assert composition["node_type"] == "group"
    assert set(composition["member_spell_ids"]) == {intake, ledger, report}
    group_id = composition["group_id"]
    print("composition registered:", group_id[:14], "... over 3 members")
    print("  identity is recomputed from the members on rehydration, so a")
    print("  tampered roster cannot enter the record wearing the same id")

    print()
    print("THE TWO QUESTIONS YOU ACTUALLY HAVE:")
    try:
        _show("group_impact", commands.research_group_impact(group_id))
        _show("group_drift", commands.research_group_drift(group_id))
    except RuntimeError as custody:
        print("  custody read REFUSED:", str(custody)[:100])
        print("  both are derived over the members' RECORDED material, so")
        print("  without custody there is nothing to union or compare")
        return

    print("  impact is a UNION with closure math, not a sum: it splits")
    print("  the radius INTERNAL vs OUTBOUND, and the closure fraction is")
    print("  the number that matters - high closure is a subsystem you can")
    print("  change on its own terms, low closure is a subsystem in name")
    print("  only whose edges are everyone else's problem")

    # The supporting reads, for context on what those two are computed over.
    _show("group_footprint", commands.research_group_footprint(group_id))
    _show("group_view", commands.research_group_view(group_id))
    print("  footprint is the PHYSICAL shadow the drift report narrows to,")
    print("  and it is honest about members whose custody it cannot see -")
    print("  a shadow with a hole in it that claimed to be complete would")
    print("  be worse than no shadow at all")

    # EVOLVING ONE IS ADD/REMOVE, NOT REPLACEMENT. `recompose` states this
    # outright: "unlisted members are retained". So dropping one member is
    # a one-word ask, not a re-declaration of the roster - and the original
    # composition is untouched, because a new roster is a NEW identity.
    print()
    print("EVOLVING A SUBSYSTEM:")
    evolved = commands.research_group_recompose(
        group_id, remove=[report], reason="report split out",
    )
    assert evolved["node_type"] == "group"
    evolved_id = evolved["group_id"]
    assert set(evolved["member_spell_ids"]) == {intake, ledger}
    assert evolved_id != group_id, "a different roster is a different id"
    print("  recompose(remove=[report]) ->", evolved_id[:14], "...")
    print("  intake and ledger were never mentioned and were RETAINED")

    # AND THIS IS WHERE THE KIND-AWARE DIFF DEFAULT SHOWS ITS OTHER HALF.
    # Expert 30 met `research_diff` on two SPELLS, where the room pins
    # `structural` for you. Hand it two COMPOSITIONS and it pins nothing -
    # it stands back and lets the engine's own `members` default answer,
    # because the useful question about two subsystems is which MEMBERS
    # changed, not how their text differs.
    _show("diff(compositions)",
          commands.research_diff(group_id, evolved_id))
    _show("group_diff(explicit)",
          commands.research_group_diff(group_id, evolved_id))
    print("  same verb as expert 30, different vocabulary - chosen by KIND")
    print("  `members` answers added/removed plus lane-evidenced version")
    print("  moves; each moved pair descends into the spell grains on your")
    print("  NEXT call, so the subsystem answer stays a subsystem answer")

    print()
    print("a composition is INFORMATIONAL - it pins members by reference,")
    print("carries no custody of its own, gates nothing and never executes")
    print("which is exactly why asking it these questions is cheap")


if __name__ == "__main__":
    main()
