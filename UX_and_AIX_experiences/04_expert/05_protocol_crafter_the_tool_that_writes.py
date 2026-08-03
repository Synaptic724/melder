"""
TIER: expert (05)
GOAL: THE ONE TOOL THAT WRITES TO DISK. Every surface in this curriculum
      so far reads: viewers read, crystals read, diffs derive, research
      records. ProtocolCrafter is the exception, and its own docstring
      flags that in a heading:

        "IT WRITES TO DISK - the unusual part:
         Most of this codebase READS source; this one MODIFIES it."

      It generates Protocol definitions from a live class or object -
      turning a concrete type into the structural interface that
      describes it - and then maintains those definitions inside your
      interface files.

      WHY THIS EXISTS
      Melder resolves by SHAPE (beginner 17: protocols as shapes). So the
      Protocol is the contract, and hand-writing one for a class you
      already have is transcription - exactly the work a machine should
      do, and exactly the work that silently rots when the class changes
      and the Protocol does not.

      THE DESIGN DECISION WORTH STEALING: BOUNDED UPDATES.

        "its updates are BOUNDED: it rewrites a DELIMITED REGION rather
         than a whole file, so HAND-WRITTEN CODE AROUND THE GENERATED
         BLOCK SURVIVES REGENERATION."

      That single choice is what separates a usable code generator from
      one you run once and then never dare run again. A generator that
      owns whole files forces you to choose between regenerating and
      keeping your own edits. A generator that owns a delimited block
      lets both live in the same file forever.

      It is the same instinct as the withheld-section probe at advanced
      15: be precise about the boundary of your authority, and say where
      it ends.

      THE SURFACE, IN TWO GROUPS
        CRAFT - returns code as a string, touches nothing:
          craft_protocol_code
          craft_protocol_module_code_from_source_file
          craft_joined_protocol_module_code
        WRITE - puts it on disk:
          write_protocol_module_from_source_file
          write_joined_protocol_module
          add_protocol_to_interface_file
          remove_protocol_from_interface_file

      THAT SPLIT IS THE SAFETY FEATURE. Every write verb has a craft
      twin, so you can always see exactly what would land before anything
      lands. "Show me" and "do it" are different verbs, and a tool that
      only offered the second would be one you had to trust blindly.

      THIS LESSON ONLY CRAFTS. It calls nothing that writes - the point
      is to show the tool and the boundary, not to edit your tree.
SURFACE EXERCISED: md.ProtocolCrafter - the craft/write split, bounded
                   block updates (craft lanes only; nothing is written)
VERIFY: rides the owner's 3.14t run; asserts are the contract.
"""
import melder as md


CRAFT_LANES = (
    "craft_protocol_code",
    "craft_protocol_module_code_from_source_file",
    "craft_joined_protocol_module_code",
)

WRITE_LANES = (
    "write_protocol_module_from_source_file",
    "write_joined_protocol_module",
    "add_protocol_to_interface_file",
    "remove_protocol_from_interface_file",
)


class PaymentGateway:
    """A concrete class - the kind of thing you would want a Protocol for."""

    def charge(self, amount: int, currency: str) -> bool:
        return True

    def refund(self, transaction_id: str) -> bool:
        return True


def main() -> None:
    crafter = md.ProtocolCrafter()
    assert isinstance(crafter, md.ProtocolCrafter)
    print("crafter:", crafter.id)

    # THE TWO GROUPS. Every write verb has a craft twin - that is the
    # safety property, not a convenience.
    print()
    print("CRAFT lanes (return code, touch nothing):")
    for lane in CRAFT_LANES:
        assert hasattr(crafter, lane), lane
        print("   ", lane)

    print("WRITE lanes (put it on disk):")
    for lane in WRITE_LANES:
        assert hasattr(crafter, lane), lane
        print("   ", lane)

    # CRAFT A PROTOCOL FROM A LIVE CLASS. Nothing is written; this is a
    # string. Look at it before you let anything near your tree.
    code = crafter.craft_protocol_code(PaymentGateway)
    assert isinstance(code, str) and code.strip()
    print()
    print("crafted from a live class -", len(code), "chars:")
    for line in code.splitlines()[:12]:
        print("   ", line)

    # The generated shape should describe what the class actually offers.
    assert "Protocol" in code
    for method in ("charge", "refund"):
        assert method in code, f"{method} missing from the crafted protocol"
    print()
    print("both public methods appear in the crafted protocol")

    # AND NOTHING WAS WRITTEN. The craft lane is pure - that is the whole
    # reason it exists separately from its write twin.
    print("nothing touched the filesystem - craft is a read-shaped verb")

    print()
    print("bounded updates: it owns a DELIMITED BLOCK, not your file")
    print("every write verb has a craft twin - see it before you land it")


if __name__ == "__main__":
    main()
