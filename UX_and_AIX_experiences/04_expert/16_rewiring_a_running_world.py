"""
TIER: expert (16)
GOAL: CHANGING THE WIRING WHILE THE WORLD RUNS. A dynamic world can gain
      a relationship after it is built: two conduits link, one pulls a
      spell it does not own into its contract, and the next meld resolves
      through the new edge. Three verbs, no ceremony.

        owner.link(borrower)
        borrower.add_spell_to_contract(spell_id=..., conduit=owner, ...)
        borrower.meld(spell=...)

      EACH VERB IS COMPLETE IN ITSELF. There is no window to open, no
      session to hold, nothing to commit afterwards. A structural verb
      does its own bookkeeping and either finishes or refuses - so the
      only thing a caller has to get right is the ORDER, and the order
      is just dependency order.

      SHARING IS A PULL, AND THE DIRECTION IS THE COMMON MISTAKE
        borrower.add_spell_to_contract(spell_id=S, conduit=owner)
      reads "borrower pulls S from owner", and the conduit NAMED in the
      call must OWN S. An owner trying to PUSH its spell into someone
      else's contract is refused with "not owned by this conduit". The
      receiver asks; the provider does not give.

      THE ORDER OF OPERATIONS, PER DEPENDENCY EDGE
        1. conjure the PROVIDER conduit
        2. conjure the CONSUMER conduit
        3. link() - only after BOTH exist
        4. the consumer pulls the provider's spell into the contract
        5. meld - this completes the late binding for that world
      Chains assemble edge by edge. Skip step 5 on a middle world and its
      consumer constructs with its Python default instead of the melded
      object - that is a usage error with a visible symptom, not a
      runtime gap.

      WHY YOU DO NOT HAVE TO THINK ABOUT CONCURRENCY HERE
      Melder serializes structural change internally, at a grain fine
      enough that independent work overlaps: two agents adding to the
      same spellbook do not wait on each other, while an operation that
      changes what that spellbook IS excludes them both. None of that
      vocabulary belongs in your code. If it ever shows up in a
      traceback you will get the blocking holder named, not a hang.

      AND A WORLD CAN BE TOLD IT DOES NOT DO THIS
      Two refusals live on `link()` and they are different sentences, in
      this order:
        braked posture  -> "Linking is disabled for the current frame
                            posture."
        not dynamic     -> "Dynamic environment is not enabled."
      What a world has been ALLOWED to do is checked before what it IS -
      so a deliberately locked-down dynamic world and an ordinary static
      one fail differently, and the message tells you which you have.
SURFACE EXERCISED: md.Spellbook.bind / conjure / configure_aether_frame,
                   Conduit.link / add_spell_to_contract / meld
VERIFY: rides the owner's 3.14t run; asserts are the contract.
"""
import melder as md


class Service:
    def __init__(self) -> None:
        self.label = "service"


class Consumer:
    def __init__(self) -> None:
        self.label = "consumer"


def _pair(frame_name: str, **posture):
    """An owner and a borrower in one world, each from its own book."""
    owner_book = md.Spellbook(aetheric_frame=frame_name)
    borrower_book = md.Spellbook(aetheric_frame=frame_name)
    service_id = owner_book.bind(
        spell=Service, existence="unique", permissions="create",
        binding_name=f"{frame_name}-service",
    )
    borrower_book.bind(
        spell=Consumer, existence="unique", permissions="create",
        binding_name=f"{frame_name}-consumer",
    )
    if posture:
        owner_book.configure_aether_frame(
            disposal=None, disposal_method_names=None, **posture,
        )
    dynamic = posture.get("system_state") == "dynamic"
    owner = owner_book.conjure(dynamic=dynamic, name=f"{frame_name}-owner")
    borrower = borrower_book.conjure(
        dynamic=dynamic, name=f"{frame_name}-borrower",
    )
    return owner, borrower, service_id


def main() -> None:
    # STEPS 1 AND 2: both conduits exist before anything is wired.
    owner_book = md.Spellbook(aetheric_frame="rewire-world")
    borrower_book = md.Spellbook(aetheric_frame="rewire-world")
    service_id = owner_book.bind(
        spell=Service, existence="unique", permissions="create",
        binding_name="rewire-service",
    )
    borrower_book.bind(
        spell=Consumer, existence="unique", permissions="create",
        binding_name="rewire-consumer",
    )
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    print("two conduits up, nothing wired between them yet")

    # The owner resolves its own spell. This works before any linking -
    # ownership and sharing are different questions.
    assert owner.meld(spell=Service,
                      binding_name="rewire-service").label == "service"
    print("owner melds its own spell -> service")

    # STEP 3: link, now that both ends exist.
    assert owner.link(borrower) is True
    print()
    print("link() -> True")

    # STEP 4: the CONSUMER pulls. Naming `owner` here is not a style
    # choice - the conduit named must own the spell.
    assert borrower.add_spell_to_contract(
        spell_id=service_id,
        conduit=owner,
        permissions="create",
    )
    print("borrower pulled the owner's spell into its contract")
    print("  sharing is a PULL - the named conduit must OWN the spell")

    # STEP 5: meld completes the late binding across the new edge.
    borrowed = borrower.meld(spell=Service, binding_name="rewire-service")
    assert borrowed.label == "service"
    print("borrower melds it ->", borrowed.label)
    print()
    print("the world was rewired while running, in three ordinary calls")

    # A WORLD TOLD NOT TO LINK REFUSES, AND SAYS WHY. This one IS
    # dynamic; it has simply been braked.
    braked_owner, braked_borrower, _ = _pair(
        "rewire-braked", system_state="dynamic", disable_linking=True,
    )
    try:
        braked_owner.link(braked_borrower)
        raise AssertionError("expected a refusal: linking is braked")
    except RuntimeError as error:
        assert "posture" in str(error)
        print()
        print("braked world refused link() -")
        print("  ", error)

    # A STATIC WORLD REFUSES FOR A DIFFERENT REASON. It can still bind;
    # it cannot rewire itself while running.
    static_owner, static_borrower, _ = _pair("rewire-static")
    try:
        static_owner.link(static_borrower)
        raise AssertionError("expected a refusal: link needs dynamic mode")
    except RuntimeError as error:
        assert "ynamic" in str(error)
        print()
        print("static world refused link() -")
        print("  ", error)
        print("  ALLOWED-to-do is checked before WHAT-IT-IS, so the two")
        print("  failures never wear each other's message")

    print()
    print("link, pull, meld - and the order is just dependency order")
    print("nothing here opens, holds, or commits anything by hand")


if __name__ == "__main__":
    main()
