"""
TIER: expert (16)
GOAL: THE TRANSACTION PLANE - the last big unauthored piece of the BLUE
      charter, and the one that explains why melder can be mutated by
      several agents at once without a global lock.

      START WITH WHAT IS NOT IN IT, BECAUSE THAT IS THE DESIGN

        "Readers (meld paths) NEVER ENTER THIS PLANE; they remain
         protected by validity gating that commits trigger."

      `meld()` takes no transaction, waits on no claim, and appears
      nowhere in the admission vocabulary. The plane serializes
      STRUCTURAL MUTATION only - bind, link, unlink, cluster_link,
      transfer_ownership, notch, index changes. Resolution is not a
      mutation, so resolution does not queue. Almost every system that
      grows a transaction manager eventually drags reads into it and
      discovers its throughput was the lock all along.

      THE PUBLIC DOOR IS A CONTEXT MANAGER
        with conduit.transaction("link", conduits=[borrower, owner]):
            ...
      `Conduit.transaction` / `begin_transaction` / `end_transaction` are
      all marked `Public API`. The context form ends the transaction on
      exit EVEN IF THE BODY RAISES, and it ends it with success=False -
      so an exception aborts rather than silently committing half a
      mutation.

      SCOPE KEYS ARE THE VOCABULARY. SCOPE HASHES ARE A TRAP.
      Both are parameters, one line apart, and only one of them does
      anything. Melder's own docstring is blunt about it:

        scope_hashes: "ADVISORY IDENTITY ONLY - they carry NO claims and
        are NOT checked for conflicts... Supplying hashes declares no
        overlap and buys no isolation; use `scope_keys` to declare
        scope."

      Read that twice, because the failure is silent and it is the
      dangerous kind: you pass hashes, you believe you declared overlap,
      two requests admit in parallel that should not have. A parameter
      that documents its own uselessness is rare and worth trusting.

      THREE CLAIM MODES, AND `ix` IS THE INTERESTING ONE
        x   exclusive   excludes everything
        s   shared      s/s coexist on one scope
        ix  intent      ix/ix coexist on one scope
      Unspecified keys default to exclusive, so the safe reading is the
      default and modes are an opt-in to MORE concurrency.

      Now the part worth stealing. OWNING SPELLBOOKS ARE CLAIMED `ix`,
      NOT `x` - deliberately, so that additive piece-work coexists:
        link:          ix each owning spellbook; conduits/wards x
        bind:          ix owning spellbook;      conduit/ward     x
        cluster_link:  ix each member spellbook; cluster/conduits x
        transfer_ownership: x on everything
      Two agents binding into the same spellbook do NOT block each other,
      because neither is changing what the spellbook IS. An ownership
      transfer takes `x` on the whole spellbook and excludes both. The
      mode is what makes the granularity honest: you are not locking an
      object, you are declaring what you intend to do to it.

      WAITING IS BOUNDED, AND THE REFUSAL NAMES NAMES
      A blocked request retries admission and parks in slices of
      `min(remaining, 1.0)` seconds. The slicing exists because a release
      landing between an attempt and the park would otherwise go unseen
      until the full deadline - so the worst case is one second of
      staleness, not the whole timeout. On expiry it raises WITH THE
      BLOCKING SCOPE KEYS AND THE HOLDER REQUEST IDS. A timeout that
      tells you who you were waiting for is a debuggable timeout.

      ONE KNOB, AND YOU ALREADY KNOW WHERE IT LIVES
        configure_aether_frame(max_transaction_wait_time_in_seconds=...)
      Root admission policy has exactly one dial, on the frame posture
      (advanced 05's map, knob 14). `queue_competing_root_transactions`
      was removed outright rather than left as a second way to say it.

      AND THE POSTURE BRAKES GATE TRANSACTION *TYPES*
      The seven `disable_*` knobs are not decoration - they are consulted
      by `begin_transaction` before admission is even attempted, so a
      braked frame refuses the family by name. Two separate refusals live
      here and they are different sentences:
        not dynamic     -> "Change transactions require dynamic mode."
        braked posture  -> "disabled for the current frame posture."
SURFACE EXERCISED: Conduit.transaction / begin_transaction /
                   end_transaction, scope_keys vs scope_hashes, the
                   dynamic-only families, and the posture brakes
VERIFY: rides the owner's 3.14t run; asserts are the contract.
"""
import melder as md


class Service:
    def __init__(self) -> None:
        self.label = "service"


class Consumer:
    def __init__(self) -> None:
        self.label = "consumer"


# The five families that REQUIRE dynamic mode. bind, notch and the index
# families are absent on purpose - they are not relationship changes.
DYNAMIC_ONLY = ("link", "transfer_ownership", "mutation", "cluster_link",
                "unlink")


def main() -> None:
    # TWO SPELLBOOKS IN ONE WORLD. This is the shape the `ix` mode exists
    # for: two owners, additive work on each, no reason for them to wait.
    owner_book = md.Spellbook(aetheric_frame="txn-world")
    borrower_book = md.Spellbook(aetheric_frame="txn-world")
    service_id = owner_book.bind(
        spell=Service, existence="unique", permissions="create",
        binding_name="txn-service",
    )
    borrower_book.bind(
        spell=Consumer, existence="unique", permissions="create",
        binding_name="txn-consumer",
    )
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    print("two spellbooks, one frame, both conduits dynamic")

    # THE PUBLIC DOOR. All three spellings are marked `Public API`.
    for verb in ("transaction", "begin_transaction", "end_transaction"):
        assert hasattr(borrower, verb), verb
    print("public door:", ", ".join(
        ("conduit.transaction(...)", "begin_transaction", "end_transaction"),
    ))

    # READERS DO NOT ENTER THE PLANE. No transaction, no claim, no wait -
    # and this is the call the runtime makes constantly.
    resolved = owner.meld(spell=Service, binding_name="txn-service")
    assert resolved.label == "service"
    print()
    print("meld() ran with NO transaction - resolution never queues")
    print("  the plane serializes MUTATION; reading is not mutation")

    # A STRUCTURAL CHANGE, INSIDE THE WINDOW. The link itself is a
    # mutation; changing what the contract carries is another one.
    assert owner.link(borrower) is True
    with borrower.transaction("link", conduits=[borrower, owner]):
        assert borrower.add_spell_to_contract(
            spell_id=service_id,
            conduit=owner,
            permissions="create",
        )
    print()
    print("contract mutated inside a 'link' transaction window")
    print("  conduits=[borrower, owner] is REQUIRED for link - both")
    print("  participants must be named, never inferred")

    # THE CONTEXT FORM ABORTS ON EXCEPTION. It ends the transaction with
    # success=False and re-raises, so a half-applied mutation cannot
    # escape by way of a crash.
    class Boom(Exception):
        pass

    try:
        with borrower.transaction("link", conduits=[borrower, owner]):
            raise Boom("something went wrong mid-mutation")
    except Boom:
        print()
        print("body raised -> transaction ended with success=False")
        print("  the window closes on the way out either way")

    # DYNAMIC IS REQUIRED FOR THE RELATIONSHIP FAMILIES. A static world
    # can still bind; it cannot rewire itself while running.
    static_book = md.Spellbook(aetheric_frame="txn-static")
    static_book.bind(spell=Service, existence="unique",
                     binding_name="txn-static-service")
    static = static_book.conjure(name="static-root")
    try:
        static.begin_transaction("link", conduits=[static])
        raise AssertionError("expected a refusal: link needs dynamic mode")
    except RuntimeError as error:
        assert "dynamic mode" in str(error)
        print()
        print("static world refused a 'link' transaction -")
        print("  ", error)

    # THE POSTURE BRAKES GATE FAMILIES BY NAME. This frame IS dynamic;
    # it has simply been told that linking is not something that happens
    # here. Different reason, different sentence, checked before
    # admission is attempted at all.
    braked_book = md.Spellbook(aetheric_frame="txn-braked")
    braked_book.bind(spell=Service, existence="unique",
                     binding_name="txn-braked-service")
    braked_book.configure_aether_frame(
        system_state="dynamic",
        disposal=None,
        disposal_method_names=None,
        disable_linking=True,
    )
    braked = braked_book.conjure(name="braked-root")
    try:
        braked.begin_transaction("link", conduits=[braked])
        raise AssertionError("expected a refusal: linking is braked")
    except RuntimeError as error:
        assert "posture" in str(error)
        print()
        print("dynamic-but-braked world refused the same call -")
        print("  ", error)
        print("  two refusals, two sentences: WHAT you are is not the")
        print("  same fact as WHAT YOU HAVE BEEN ALLOWED TO DO")

    print()
    print("the five dynamic-only families:", ", ".join(DYNAMIC_ONLY))
    print("  bind / notch / index changes are NOT here - they do not")
    print("  rewire relationships, so they do not need a live world")

    print()
    print("scope_keys DECLARE scope; scope_hashes declare nothing")
    print("ix on the owner lets additive work run side by side, while")
    print("x on a transfer still excludes it - the mode is the grain")
    print("and nothing above ever made a reader wait")


if __name__ == "__main__":
    main()
