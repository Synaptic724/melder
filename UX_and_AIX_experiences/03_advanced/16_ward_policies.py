"""
TIER: advanced (16)
GOAL: WARD POLICIES - how permissive a conduit is about contracting with
      other conduits, and the three refusals that come with the door.

      A policy is broader than a visibility flag. It governs THREE
      control surfaces at once:
        - may this conduit initiate OUTBOUND grants?
        - may it accept INBOUND borrowed lineages?
        - are per-spell permission and whitelist checks ENFORCED, or
          bypassed?

      FIVE MODES
        default        both directions allowed, but every spell still has
                       to satisfy its own permission and whitelist rules
        whitelist_all  expose local lineages without per-spell whitelist
                       flags, AND let otherwise-blocked entries through
        block_all      reject dynamic contracting from this ward entirely
        inbound_only   accept borrowed inbound contracts; refuse to
                       initiate outbound ones
        outbound_only  grant outward; refuse inbound borrowing by peers

      THREE REFUSALS, AND THE THIRD IS THE INTERESTING ONE

      1. DYNAMIC MODE ONLY. On an automatic frame the door raises. This
         is not a policy engine that sits idle in automatic mode - wards
         only form and sever contracts at runtime in dynamic mode, so
         outside it the setting would be decoration.

      2. NORMAL CONDUITS ONLY. A lesser conduit cannot hold a policy -
         "Convert to a normal Conduit first". Policy belongs to the thing
         that owns a lineage, not to a borrower of one.

      3. NO RETROACTIVE LOCKDOWN.
         Setting block_all or whitelist_all WHILE CONTRACTS EXIST raises.
         Melder will not silently sever what you already granted, and it
         will not quietly leave the grants standing under a policy that
         says they should not exist. It refuses and makes you tear the
         contracts down yourself.

         That is the never-substitute rule (lessons 06/13/14/17) applied
         to authority: a policy change that cannot be honestly applied is
         an error, never a partial application.
SURFACE EXERCISED: md.Policies, Conduit.set_new_policy, the dynamic-only
                   / normal-only / no-existing-contracts refusals
VERIFY: rides the owner's 3.14t run; asserts are the contract.

FINDINGS (init surface, 2026-08-02):
 1. RESOLVED 2026-08-03 - NO PUBLIC READER. `set_new_policy` was public
    with no public way to ask a conduit what its policy currently IS:
    write-only authority. `Conduit.policy` now answers that. Note the
    deliberate asymmetry - the WRITE is gated on a dynamic frame and a
    normal (non-lesser) conduit, the READ on neither, because an
    automatic conduit still enforces a policy and hiding live behaviour
    behind a mode gate would be worse than the gap was.
 2. RESOLVED 2026-08-03 - THE SIGNATURE UNDER-SOLD THE CODE.
    Conduit.set_new_policy was annotated `policy: str`, but it delegates
    to a ward method that runs EnumHelpers.convert_enum_and_check and has
    always accepted a member OR its string name. A reader trusting the
    public hint would think the exported md.Policies enum was unusable
    here. It is now annotated Union[str, Policies], which also makes
    read-then-write a legal round-trip instead of a type error.
 3. Policies uses auto(), so `.value` is an INT, not the mode name. The
    string form is `.name`. Anyone reaching for `.value` to build the
    string argument gets 3 instead of "block_all".
"""
import melder as md


class Payload:
    """A spell to give the ward something to be a policy about."""


MODES = ("default", "whitelist_all", "block_all",
         "inbound_only", "outbound_only")


def main() -> None:
    # Pass the mode NAME. That is the whole API - every setter in melder
    # that takes an enum is typed Union[Enum, str] and normalizes for you.
    print("the five modes:", list(MODES))
    assert {policy.name for policy in md.Policies} == set(MODES)

    # AND HERE IS WHY THE STRING IS THE RIGHT HABIT, not just the shorter
    # one. Policies is built on auto(), so `.value` is an INT - reach for
    # it to build the argument and you pass 3 instead of "block_all". The
    # name is the string form. Use the literal and the trap disappears.
    assert isinstance(md.Policies.block_all.value, int)
    assert md.Policies.block_all.name == "block_all"
    print("Policies.block_all.value is", md.Policies.block_all.value,
          "- an int, not the mode name. pass \"block_all\" instead.")

    # ------------------------------------------------------------------
    # REFUSAL 1 - DYNAMIC MODE ONLY
    # ------------------------------------------------------------------
    # binding_name differs per frame ON PURPOSE. A spell_id is a hash of
    # the BIND FINGERPRINT and the frame is not in it, so the same class
    # bound identically in two frames mints the same id and the second
    # conjure is refused process-wide. Frames isolate instances, not
    # identity - see advanced 02.
    automatic_book = md.Spellbook(aetheric_frame="ward-automatic")
    automatic_book.bind(spell=Payload, existence="unique",
                        binding_name="automatic")
    automatic_root = automatic_book.conjure(name="automatic-root")
    try:
        automatic_root.set_new_policy("block_all")
        raise AssertionError("expected RuntimeError on an automatic frame")
    except RuntimeError as error:
        print()
        print("automatic frame refused set_new_policy:", error)

    # ------------------------------------------------------------------
    # A DYNAMIC WORLD - now the door opens
    # ------------------------------------------------------------------
    book = md.Spellbook(aetheric_frame="ward-dynamic")
    book.bind(spell=Payload, existence="unique", binding_name="dynamic")
    book.configure_aether_frame(system_state="dynamic", disposal=None,
                                disposal_method_names=None)
    root = book.conjure(name="ward-root")
    print()
    print("dynamic frame conjured")

    # Plain strings, like every other enum-shaped argument in melder. The
    # ward normalizes through EnumHelpers.convert_enum_and_check, so the
    # mode NAME is all you ever need to pass.
    root.set_new_policy("outbound_only")
    print("policy -> outbound_only")

    root.set_new_policy("inbound_only")
    print("policy -> inbound_only")

    root.set_new_policy("default")
    print("policy -> default")

    # ------------------------------------------------------------------
    # REFUSAL 2 - NORMAL CONDUITS ONLY
    # ------------------------------------------------------------------
    lesser = root.create_lesser_conduit()
    try:
        lesser.set_new_policy("block_all")
        raise AssertionError("expected RuntimeError on a lesser conduit")
    except RuntimeError as error:
        print()
        print("lesser conduit refused a policy:", error)

    # ------------------------------------------------------------------
    # REFUSAL 3 - NO RETROACTIVE LOCKDOWN
    # ------------------------------------------------------------------
    # With no contracts yet, the restrictive modes are allowed.
    root.set_new_policy("block_all")
    print()
    print("block_all accepted while the ward has no contracts")
    root.set_new_policy("default")

    # Form a contract, and the restrictive modes stop being available -
    # melder refuses rather than severing behind your back.
    peer_book = md.Spellbook(aetheric_frame="ward-dynamic")
    peer = peer_book.conjure(name="ward-peer")
    linked = root.link(peer)
    print("linked to a peer:", linked)

    for restrictive in ("block_all", "whitelist_all"):
        try:
            root.set_new_policy(restrictive)
            raise AssertionError(
                f"expected RuntimeError setting {restrictive} with contracts"
            )
        except RuntimeError as error:
            print(f"{restrictive:14s} refused while contracts exist")

    # The permissive/directional modes are still fine - only the two that
    # would invalidate existing grants are gated.
    root.set_new_policy("outbound_only")
    print("outbound_only still accepted - it does not invalidate grants")

    print()
    print("policy governs direction AND whether per-spell checks apply")
    print("a change that cannot be honestly applied is refused, not partial")


if __name__ == "__main__":
    main()
