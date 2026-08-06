"""
TIER: expert (35)
GOAL: THE ADMISSION GATE, and why it is not a mutex. Expert 16 rewired a
      running world and 17 staged a swap on a live object. Neither said
      what makes those safe. This does.

      MELDER HAS THREE GATES AND THEY EXIST FOR ONE REASON:
        RiftGate       admission to a Rift's guarded paths (here)
        CreationGate   the conduit's meld path
        LoadGate       crystallizer loads
      "All three exist because some operations must wait for READERS
      rather than for other writers." Read that twice. A mutex protects
      writers from each other. These make a writer wait until the last
      READER has left - which is the only way to swap something out from
      under live callers without tearing.

      TICKETS ARE WHAT MAKE DRAINING TRUTHFUL. A caller registers a ticket
      entering guarded work and unregisters on exit, and drain waits for
      the count to hit zero. A boolean "busy" flag would be a guess; "a
      meld holds its ticket across the whole executor, so ticket-zero
      genuinely means no reader is inside".

      TWO CONTROL MODES, AND CONFLATING THEM IS THE BUG.
        BLOCKING is REVERSIBLE. Disable parks new entrants, open() releases
          them. This is what an ACL-driven projection refresh needs: block
          entrants, drain, refresh once, reopen.
        TERMINAL CLOSE is ONE-WAY. It exists for shutdown, "where
          reopening would be wrong".
      One is a door you hold shut; the other is a door you brick up.

      TWO ENTRY MODES, AND THIS ONE IS A POLICY CHOICE ABOUT YOUR AGENTS.
      While a gate is disabled, `admit()` either WAITS or RAISES:
        "wait"   the caller blocks until someone reopens
        "raise"  the caller is told no, immediately
      An agent that blocks is patient; an agent that raises can go do
      something else. Neither is right by default, which is why it is a
      setting rather than a behaviour.

      AND NOW THE HONEST PART, WHICH IS THE REASON THIS LESSON EXISTS.
      NO SINGLE VERB PROVES A RIFT IS EMPTY, and melder says so in its own
      docstrings rather than letting you assume otherwise:
        disable_rift_gate       stops NEW entry. It "does NOT wait for
                                threads already inside".
        close_and_wait_rift     drains - but the timeout BOUNDS the wait,
                                so "a return does not by itself prove the
                                rift is empty".
        count_active_rift_threads
                                tells you the truth, and is "a DIAGNOSTIC,
                                not a synchronization primitive - do not
                                spin on it".
      So quiescence is: close-and-wait (bounded), THEN check the count.
      Most systems ship a `drain()` that implies a guarantee it cannot
      make. This one hands you three verbs and tells you what each one
      does not cover.

      ONE TRAP, STATED PLAINLY: disable/enable SILENTLY NO-OP for an
      unknown rift id. A typo does not raise - it succeeds and changes
      nothing.
SURFACE EXERCISED: Nexus.get_rift_gate / enable_rift_gate /
                   disable_rift_gate / set_rift_gate_entry_mode /
                   count_active_rift_threads /
                   count_active_rift_threads_total / close_and_wait_rift,
                   Rift.id, and a command refused at the closed gate
VERIFY: authored 2026-08-05; not yet run.
"""
import melder as md


FRAME = "gatekeep-world"

SAFE = "result = 2 + 2\n"


class Reader:
    def __init__(self) -> None:
        self.name = "reader"


def main() -> None:
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
    book.bind(spell=Reader, existence="unique", permissions="create",
              binding_name="gatekeep-reader")
    book.conjure(name="gatekeep-root")

    nexus = md.Nexus()
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    system_configuration.with_allowed_target_frame_names([FRAME])
    nexus.activate(system_configuration)
    rift_configuration = nexus.create_rift_configuration()
    rift_configuration.with_space_type("codegen")
    rift = nexus.create_rift(configuration=rift_configuration,
                             rift_name="gatekeeper")
    rift.mark_active()
    rift.create_frame_link(FRAME)
    commands = rift.space.command_system

    rift_id = rift.id

    # `get_rift_gate` is used here the way `enable_rift_gate`'s own
    # contract prescribes - as an EXISTENCE CHECK, because the enable and
    # disable verbs silently no-op on an unknown id: "a typo'd id looks
    # like success. Confirm with get_rift_gate(...) when the id is not
    # known-good." The gate object itself is kernel machinery and this
    # lesson never drives it; every state change below goes through Nexus.
    assert nexus.get_rift_gate(rift_id) is not None, "this rift has a gate"
    assert nexus.get_rift_gate("no-such-rift-id") is None, (
        "an unknown id must answer None rather than raising"
    )
    print("rift:", rift_id[:14], "... gate registered: True")
    print("  (None for an unknown id is an ANSWER, not an error channel)")

    # NOBODY IS INSIDE. The count is a diagnostic, and right now it is a
    # true one because this thread is not in a guarded call.
    assert nexus.count_active_rift_threads(rift_id) == 0
    assert nexus.count_active_rift_threads_total() == 0
    print("active tickets:", nexus.count_active_rift_threads(rift_id),
          "| across all rifts:", nexus.count_active_rift_threads_total())

    # THE ENTRY MODE IS A POLICY CHOICE. Set it to `raise` BEFORE closing
    # the gate - on a single thread, `wait` mode plus a closed gate is a
    # deadlock, and that is not a melder bug, it is what "wait" means.
    nexus.set_rift_gate_entry_mode(rift_id, "raise")
    print()
    print("entry mode set to 'raise' - a disabled gate will refuse rather")
    print("than park the caller. On one thread, 'wait' here would hang")
    print("forever, and correctly so.")

    # CLOSE THE DOOR. New entry stops immediately.
    nexus.disable_rift_gate(rift_id)
    try:
        commands.validate_codegen(SAFE, frame_name=FRAME)
        raise AssertionError("expected the gate to refuse admission")
    except RuntimeError as refused:
        print()
        print("validate_codegen at a disabled gate ->", str(refused)[:70])
        print("  the command never ran. Admission is checked BEFORE the")
        print("  work, not inside it")

    # AND THE SAME COMMAND WORKS THE MOMENT IT REOPENS. Reversible.
    nexus.enable_rift_gate(rift_id)
    verdict = commands.validate_codegen(SAFE, frame_name=FRAME)
    assert verdict["accepted"] is True
    print()
    print("enable_rift_gate -> the same call now answers:",
          verdict["accepted"])
    print("  blocking mode is REVERSIBLE. That is the whole point: block")
    print("  entrants, drain, refresh the projection once, reopen.")

    # THE SILENT NO-OP. A typo'd rift id does not raise.
    nexus.disable_rift_gate("no-such-rift-id")
    still_open = commands.validate_codegen(SAFE, frame_name=FRAME)
    assert still_open["accepted"] is True, (
        "disabling an unknown rift must not affect a real one"
    )
    print()
    print("disable_rift_gate('no-such-rift-id') -> silently did nothing,")
    print("  and our real gate is still open. A typo here does not raise;")
    print("  it succeeds and changes nothing, which is why the contract")
    print("  tells you to confirm the id with get_rift_gate(...) first -")
    print("  the check at the top of this lesson is that idiom, not a")
    print("  reach into the gate object")

    # QUIESCENCE IS TWO STEPS, NOT ONE.
    nexus.close_and_wait_rift(rift_id, timeout=5.0, interval=0.05)
    remaining = nexus.count_active_rift_threads(rift_id)
    assert remaining == 0, remaining
    print()
    print("close_and_wait_rift returned, and THEN we checked:", remaining,
          "tickets")
    print("  the return alone does not prove empty - the timeout bounds")
    print("  the wait. Melder documents that rather than implying a")
    print("  guarantee it cannot make, which is why quiescence is")
    print("  close-and-wait FOLLOWED BY a count check")

    # TERMINAL CLOSE IS ONE-WAY. The gate does not reopen for new work.
    try:
        commands.validate_codegen(SAFE, frame_name=FRAME)
        raise AssertionError("expected the terminally closed gate to refuse")
    except RuntimeError as closed:
        print()
        print("after close_and_wait ->", str(closed)[:70])
        print("  terminal close is ONE-WAY. Blocking mode is a door you")
        print("  hold shut; this is a door you brick up, and it exists for")
        print("  shutdown where reopening would be wrong")

    print()
    print("a mutex protects writers from each other")
    print("a gate makes a writer wait for the last READER to leave")
    print("that is what lets melder swap a live object without tearing")


if __name__ == "__main__":
    main()
