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

      THE SPLIT IS NOT A CLEAN 1:1 PAIRING, and the real shape is better
      than a pairing would be. Two of the writes DO have craft twins - the
      ones that generate a whole module from a source file, and the joined
      variant. The two interface-file writes have no twin at all.
      That looks like a gap until you read their signatures:
        add_protocol_to_interface_file(path, PROTOCOL_CODE)
      The crafted code is the ARGUMENT. You cannot add a protocol you have
      not crafted, because the crafted string is what you pass in. The
      preview is not a parallel verb you are trusted to remember to call -
      it is the input, and there is no route to the file that skips it.

      AND THE BOUNDED-BLOCK RULES ARE THE REST OF IT. `add` refuses by
      NAME if that protocol is already present rather than appending a
      second copy, `remove` deletes one named block and leaves the rest of
      your file alone, and both RETURN the updated contents so the result
      is inspectable rather than assumed.
SURFACE EXERCISED: md.ProtocolCrafter.craft_protocol_code (twice, for
                   determinism), add_protocol_to_interface_file including
                   its duplicate refusal, and
                   remove_protocol_from_interface_file - all against a
                   temporary directory that removes itself
VERIFY: rewritten 2026-08-05; the write lanes are now exercised against a
        throwaway file instead of only being named. Not yet run.
"""
import tempfile
from pathlib import Path

import melder as md


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

    # CRAFT A PROTOCOL FROM A LIVE CLASS. Nothing is written; this is a
    # string. Look at it before you let anything near your tree.
    code = crafter.craft_protocol_code(PaymentGateway)
    assert isinstance(code, str) and code.strip()
    print()
    print("crafted from a live class -", len(code), "chars:")
    for line in code.splitlines()[:12]:
        print("   ", line)

    # PURITY, CHECKED RATHER THAN CLAIMED. Craft is a pure read, so the
    # same input must produce byte-identical output and leave no trace.
    again = crafter.craft_protocol_code(PaymentGateway)
    assert again == code, "craft must be deterministic - it is a pure read"
    print()
    print("crafted twice -> byte-identical:", again == code)
    print("  a verb that wrote something, cached something, or consumed")
    print("  state would not survive being called twice")

    # The generated shape should describe what the class actually offers.
    assert "Protocol" in code
    for method in ("charge", "refund"):
        assert method in code, f"{method} missing from the crafted protocol"
    print()
    print("both public methods appear in the crafted protocol")

    # THE WRITE LANES, ON A THROWAWAY FILE. Nothing here goes near your
    # tree - the temporary directory removes itself.
    with tempfile.TemporaryDirectory() as scratch:
        interface_file = Path(scratch) / "interfaces.py"

        # YOU CANNOT WRITE WHAT YOU HAVE NOT CRAFTED, because the crafted
        # code IS the argument. That is a stronger guarantee than a
        # parallel preview verb: there is no path to the file that skips
        # the string you already looked at.
        updated = crafter.add_protocol_to_interface_file(interface_file, code)
        assert "Protocol" in updated
        assert interface_file.exists()
        print()
        print("add_protocol_to_interface_file(path, THE CRAFTED CODE)")
        print("  ->", len(updated), "chars, and it RETURNS the new contents")
        print("  the crafted string is the ARGUMENT, so there is no route")
        print("  to the file that skips the thing you already read")

        # ADDING IT TWICE REFUSES BY NAME. Not a silent second copy.
        try:
            crafter.add_protocol_to_interface_file(interface_file, code)
            raise AssertionError("expected a refusal on a duplicate protocol")
        except ValueError as duplicate:
            print()
            print("adding the same protocol again ->", str(duplicate)[:78])
            print("  it refuses by NAME rather than appending a second copy")

        # AND REMOVAL IS BY NAME, BOUNDED TO THAT BLOCK.
        name = next(line.split()[1].split("(")[0]
                    for line in code.splitlines()
                    if line.startswith("class "))
        after_removal = crafter.remove_protocol_from_interface_file(
            interface_file, name,
        )
        assert name not in after_removal, after_removal
        print()
        print("remove_protocol_from_interface_file(path, %r) -> gone" % name)
        print("  it owns a DELIMITED BLOCK, not your file: the rest of the")
        print("  contents is untouched, which is what makes it safe to")
        print("  point at a file you did not generate")

    print()
    print("craft returns code and touches nothing; the write lanes take")
    print("that code as their argument. The preview is not a parallel")
    print("verb you are trusted to call - it is the input.")


if __name__ == "__main__":
    main()
