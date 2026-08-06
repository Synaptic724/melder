"""
TIER: expert (13)
GOAL: ONE CODEGEN ROOM, SEVERAL WORLDS. Expert 11 attached a rift to a
      frame; 12 ran the loop against one. This is the shape you actually
      end up with: a single workshop wired to several frames, each
      holding different objects, with the agent choosing per call which
      world it is writing into.

      THIS IS WHERE `frame_name` STOPS BEING A NUISANCE

      In 12 it looked like ceremony - one room, one frame, why type it.
      Here the room can reach three worlds that hold DIFFERENT bindings,
      and `execute_codegen(code, frame_name=...)` is the only thing
      deciding which one the code lands in. A default would not be a
      convenience, it would be a coin flip with side effects.

      ATTACHMENT IS PER FRAME AND EACH ONE IS ITS OWN DECISION
        rift.create_frame_link("billing")
        rift.create_frame_link("catalog")
      Two calls, two gate checks. A rift does not acquire a world by
      being near it, and there is no "attach to everything" verb -
      because there is no honest way to ask for that.

      AND MULTI-FRAME IS OFF BY DEFAULT, IN TWO SEPARATE KNOBS
        with_allowed_target_frame_names([...])  the observer's policy
        with_multiple_target_frames(True)       may there be more than one
        with_max_target_frame_count(3)          how many, across the Nexus
      The boolean and the count are not redundant: the first decides
      whether the plural case is permitted at all, the second bounds it.
      Shipped defaults are False and 1, so this whole lesson is a
      deliberate opt-in - and the cap is spent NEXUS-WIDE because target
      frames are ref-counted across every rift, not per rift.

      THE FRAMES ARE STILL WALLED. Advanced 02's law does not soften
      because one observer can see several worlds: `billing` and
      `catalog` hold their own bindings, their own singletons, their own
      posture. The workshop is a room with several windows, not a room
      that merged the buildings.

      WHAT THE AGENT ACTUALLY GETS
        rift.list_accessible_non_nexus_frame_names()
      The rift asks which worlds it may target, and the answer runs BOTH
      of expert 11's gates - Nexus allow/deny policy AND per-frame
      posture, filtered by this rift's space type. So it answers exactly
      "what would attach if I tried". An agent does not have to guess and
      does not have to probe by attempting.

      CAVEAT, STATED PLAINLY: that method and its Nexus-level twin are
      both marked `Internal` in their own docstrings. The capability is
      real and it is the best AIX door in the subsystem, but it has no
      public marking yet - recorded as a finding, not taught as surface.

      AND THE POSTURE BAR IS PER FRAME TOO. A codegen room needs
      rift_enabled AND ai_native AND dynamic on EVERY frame it targets.
      One qualifying world does not qualify its neighbours.
SURFACE EXERCISED: several postured frames, the Nexus target-frame policy
                   and budget knobs, one codegen rift with several frame
                   links, validate_codegen / execute_codegen once PER
                   FRAME through the one room, and the accessible-frames
                   enumeration
VERIFY: went RED 2026-08-03 and was fixed the same day; awaiting
        re-run. See the header note for what the failure taught. The
        SURFACE line was corrected 2026-08-05; executable code unchanged.
"""
import melder as md


class Invoice:
    def __init__(self) -> None:
        self.kind = "invoice"


class Product:
    def __init__(self) -> None:
        self.kind = "product"


class AuditTrail:
    def __init__(self) -> None:
        self.kind = "audit"


def _workshop_frame(frame_name: str, spell: type):
    """One AI-native, rift-visible world holding its own object."""
    book = md.Spellbook(aetheric_frame=frame_name)
    # A distinct binding_name per frame: spell_id is process-wide and the
    # frame is NOT in the fingerprint (advanced 02), so identical bindings
    # across worlds would collide.
    book.bind(spell=spell, existence="unique", binding_name=frame_name)
    book.configure_aether_frame(
        system_state="dynamic",
        disposal=None,
        disposal_method_names=None,
        rift_enabled=True,
        ai_native=True,
    )
    # Hand the conduit back. A frame is not a shared pool: a SECOND book
    # in the same frame owns nothing this one bound, so the only way to
    # reach these spells later is to keep this conduit.
    return book.conjure(name=f"{frame_name}-root")


def main() -> None:
    # THREE WORLDS, THREE DIFFERENT OBJECTS. Two will be attached; the
    # third is postured but deliberately left unattached, to show that
    # reach is something you grant, not something that leaks.
    billing_conduit = _workshop_frame("billing", Invoice)
    _workshop_frame("catalog", Product)
    _workshop_frame("compliance", AuditTrail)
    print("three worlds up: billing/Invoice, catalog/Product,",
          "compliance/AuditTrail")

    nexus = md.Nexus()
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    # THE OBSERVER'S HALF OF THE CONSENT (expert 11, gate A). All three
    # worlds are named here even though only two get attached - because
    # eligibility and attachment are separate bits, and the enumeration
    # below is only interesting if a reachable-but-unattached world exists.
    system_configuration.with_allowed_target_frame_names(
        ["billing", "catalog", "compliance"],
    )
    # BOTH budget knobs, and both are required. The boolean permits more
    # than one target frame at all; the count caps how many. Defaults are
    # False and 1, so a second attachment fails on the boolean and a third
    # would fail on the count.
    system_configuration.with_multiple_target_frames(True)
    system_configuration.with_max_target_frame_count(3)
    nexus.activate(system_configuration)

    rift_configuration = nexus.create_rift_configuration()
    rift_configuration.with_space_type("codegen")
    rift = nexus.create_rift(configuration=rift_configuration,
                             rift_name="workshop")
    rift.mark_active()
    room = rift.space
    commands = room.command_system
    print("codegen workshop up:", type(room).__name__)

    # ATTACH TWO OF THE THREE. Each link is its own decision and its own
    # gate check - there is no attach-to-everything verb.
    rift.create_frame_link("billing")
    rift.create_frame_link("catalog")
    print()
    print("attached: billing, catalog   (compliance deliberately not)")

    # THE AGENT CAN ENUMERATE ITS OWN REACH before attempting anything.
    # The Rift-level form needs no id - it knows which rift it is.
    reachable = rift.list_accessible_non_nexus_frame_names()
    print("rift may target:", sorted(reachable))
    # It applies BOTH of expert 11's gates - the Nexus allow/deny policy
    # AND the per-frame posture, filtered by THIS rift's space type - so
    # the answer is exactly "what would attach if I tried".
    assert "compliance" in reachable, (
        "postured and allow-listed, so eligible - even though unattached"
    )
    # Eligibility is not attachment. Two bits, the same way configured and
    # activated are everywhere else in melder.
    print("  'compliance' is ELIGIBLE and NOT ATTACHED - two different bits")
    # HONESTY NOTE: both this and the Nexus-level
    # `list_accessible_non_nexus_frame_names(rift_id)` are marked
    # `Internal` in their own docstrings. They are the only way an agent
    # can survey its reach instead of probing by attempting, so the
    # capability exists but has no public door yet. Recorded as a finding
    # in _concept_map.txt rather than taught as public surface.

    # PER-FRAME CODEGEN. Same room, same verb, different world - and the
    # ONLY thing that decides is the argument.
    for frame_name in ("billing", "catalog"):
        verdict = commands.validate_codegen(
            "result = 1\n", frame_name=frame_name,
        )
        print()
        print(f"validate into {frame_name!r} ->", verdict)

    outcome = commands.execute_codegen("result = 1\n", frame_name="billing")
    print()
    print("executed into 'billing' ->", type(outcome).__name__)
    print("  the same call with frame_name='catalog' lands somewhere else")
    print("  entirely - which is why there is no default")

    # THE WALL HOLDS. Each frame still owns its own bindings; one observer
    # seeing both worlds did not merge them. Note we meld through the
    # conduit that BOUND these spells - a fresh book in the same frame
    # would own nothing and resolve nothing.
    invoice = billing_conduit.meld(spell=Invoice, binding_name="billing")
    assert invoice.kind == "invoice"
    try:
        billing_conduit.meld(spell=Product, binding_name="catalog")
        raise AssertionError("catalog's object must not resolve in billing")
    except Exception as error:
        print()
        print("billing cannot resolve catalog's object -",
              type(error).__name__)
        print("  a shared observer is not a shared world")

    print()
    print("one workshop, many windows - never one merged building")
    print("frame_name is the steering wheel, not paperwork")


if __name__ == "__main__":
    main()
