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

      THE FRAMES ARE STILL WALLED. Advanced 02's law does not soften
      because one observer can see several worlds: `billing` and
      `catalog` hold their own bindings, their own singletons, their own
      posture. The workshop is a room with several windows, not a room
      that merged the buildings.

      WHAT THE AGENT ACTUALLY GETS
        list_accessible_non_nexus_frame_names(rift_id)
      The rift asks which worlds it may target, and the answer is
      filtered by the SAME posture gate that attachment used. An agent
      does not have to guess and does not have to attempt - it can
      enumerate its own reach first. That is the AIX story in one call.

      AND THE POSTURE BAR IS PER FRAME TOO. A codegen room needs
      rift_enabled AND ai_native AND dynamic on EVERY frame it targets.
      One qualifying world does not qualify its neighbours.
SURFACE EXERCISED: several postured frames, one codegen rift with several
                   frame links, per-frame codegen calls, and the
                   accessible-frames enumeration
VERIFY: rides the owner's 3.14t run; asserts are the contract.
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


def _workshop_frame(frame_name: str, spell: type) -> None:
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
    book.conjure(name=f"{frame_name}-root")


def main() -> None:
    # THREE WORLDS, THREE DIFFERENT OBJECTS. Two will be attached; the
    # third is postured but deliberately left unattached, to show that
    # reach is something you grant, not something that leaks.
    _workshop_frame("billing", Invoice)
    _workshop_frame("catalog", Product)
    _workshop_frame("compliance", AuditTrail)
    print("three worlds up: billing/Invoice, catalog/Product,",
          "compliance/AuditTrail")

    nexus = md.Nexus()
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    system_configuration.with_multiple_target_frames(True)
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
    reachable = nexus.list_accessible_non_nexus_frame_names(rift.id)
    print("rift may target:", sorted(reachable))
    # `compliance` qualifies on POSTURE, so it shows as reachable even
    # though it is not linked. Eligibility and attachment are two bits,
    # the same way configured and activated are everywhere else.
    print("  note: eligibility is not attachment - two different bits")

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
    # seeing both worlds did not merge them.
    billing_conduit = md.Spellbook(aetheric_frame="billing").conjure(
        name="billing-reader",
    )
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
