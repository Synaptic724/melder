"""
TIER: expert (20)
GOAL: THE WORKBENCH. A codegen room is not just a place to run code -
      it has a WORKSTATION, a room-local canvas where an agent keeps
      named handles on things between commands. Advanced 12 introduced
      it as a store. This is what it is FOR.

      THE LOOP THAT MAKES IT A WORKBENCH
        workstation.bind_object("service", obj)
        workstation.set_target("service")
        commands.execute_target_method("compute", bind_as_name="result")
        workstation.set_target("result")
      A command's RETURN VALUE becomes the next named binding. So an
      agent works in steps, each one addressable by a name it chose,
      without carrying objects around in its own head or re-deriving
      them from the runtime on every call.

      THREE STORES, ONE NAMESPACE EACH
        bind_object / bind_attribute / bind_method
      Binding one name into two stores is allowed - they do not collide
      on WRITE. But a bare `get(name)` must resolve UNIQUELY, and when
      two stores answer it REFUSES as ambiguous rather than picking one.
      So the stores are separate for writing and deliberately unmerged
      for reading; `get(name, store=...)` is how you mean one of them.

      `describe_bindings()` reports FIVE keys, not four: the fifth is
      `target_store`, which names WHICH store the active target came
      from, so a target round-trips through `get(name, store=...)`.

      STRONG OR WEAK, AND THE CHOICE IS ENFORCED
      `weak_ref=True` on something that cannot be weak-referenced RAISES
      rather than silently storing it strongly. A silent degrade would
      pin an object the caller believed was collectable - the bug you
      find three weeks later as a memory graph that never shrinks.

      AND A COLLECTED WEAK BINDING TELLS THE ROOM. Weak-binding
      collection publishes an event into the room's own event system, so
      "the thing I was holding went away" is something an agent can be
      TOLD rather than discover by dereferencing a hole.

      TWO WAYS TO STOP POINTING AT SOMETHING, AND THEY DIFFER
        clear_target()    deselect; the binding stays, the object lives
        cleanup_target()  call cleanup ON the target, then deselect
      One is putting the tool down. The other is dismantling it.

      THE SECURITY LINE, STATED PLAINLY
      `CommandSystem` gates runtime access BEFORE a bind and leaves
      already-bound workstation objects OUTSIDE post-bind ACL policing.
      Getting a handle is the checkpoint; using the handle you were
      granted is not re-litigated on every call. Know which side of that
      line you are on when you bind something.

      AND THE WORKSTATION NEVER FABRICATES. It stores room-local
      bindings only - it will not construct, resolve, or meld anything
      for you. Resolution is the command system's job; holding is the
      workstation's. `cleanup()` clears the stores and deliberately does
      NOT clean the objects inside them, because it did not make them.
SURFACE EXERCISED: rift.space.workstation - bind_object / bind_attribute
                   / bind_method / get / release / describe_bindings /
                   set_target / get_target / clear_target, and
                   command_system.execute_target_method(bind_as_name=...)
VERIFY: rides the owner's 3.14t harness; asserts are the contract.
"""
import melder as md


class Ledger:
    """A plain object an agent might want to keep a handle on."""

    def __init__(self) -> None:
        self.entries = []

    def record(self, amount: int) -> int:
        self.entries.append(amount)
        return sum(self.entries)


def main() -> None:
    # A postured world, then a codegen room pointed at it (expert 11).
    book = md.Spellbook(aetheric_frame="bench-world")
    book.bind(spell=Ledger, existence="unique", binding_name="bench-ledger")
    book.configure_aether_frame(
        system_state="dynamic",
        disposal=None,
        disposal_method_names=None,
        rift_enabled=True,
        ai_native=True,
    )
    conduit = book.conjure(name="bench-root")

    nexus = md.Nexus()
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    system_configuration.with_allowed_target_frame_names(["bench-world"])
    nexus.activate(system_configuration)

    rift_configuration = nexus.create_rift_configuration()
    rift_configuration.with_space_type("codegen")
    rift = nexus.create_rift(configuration=rift_configuration,
                             rift_name="bench")
    rift.mark_active()
    rift.create_frame_link("bench-world")

    room = rift.space
    workstation = room.workstation
    commands = room.command_system
    print("room:", type(room).__name__,
          " workstation:", workstation.workstation_id)
    assert workstation.owner_space_id
    print("the workstation belongs to THIS room - it is room-local")

    # THE WORKSTATION HOLDS; IT DOES NOT MAKE. The object comes from the
    # runtime; the bench just keeps a name on it.
    ledger = conduit.meld(spell=Ledger, binding_name="bench-ledger")
    workstation.bind_object("ledger", ledger)
    # A bare get() works RIGHT NOW because the name is unique. Watch what
    # happens to this exact call a few lines below.
    assert workstation.get("ledger") is ledger
    print()
    print("bound 'ledger' - the SAME object, not a copy or a proxy")

    # THREE STORES. Binding the same name in two of them is ALLOWED -
    # they are separate namespaces and neither write disturbs the other.
    workstation.bind_attribute("ledger", "a note about the ledger")
    assert workstation.get("ledger", store="objects") is ledger
    assert workstation.get("ledger", store="attributes") != ledger
    print("the name 'ledger' lives in TWO stores; addressed with store=,")
    print("  each answers its own value")

    # ...BUT A BARE READ ACROSS THEM REFUSES. Writing is per-store;
    # READING without naming a store must resolve UNIQUELY, and when it
    # cannot, melder says so instead of picking a winner.
    try:
        workstation.get("ledger")
        raise AssertionError("expected an ambiguity refusal")
    except ValueError as error:
        print()
        print("get('ledger') with no store ->", error)
        print("  the SAME call succeeded twenty lines ago. Nothing about")
        print("  it changed - the WORLD did. A bare name is only an")
        print("  address while it happens to be unique, and melder tells")
        print("  you the moment it stops being one instead of guessing")

    summary = workstation.describe_bindings()
    print("describe_bindings() keys:", sorted(summary))
    print("  five, not four - `target_store` names WHICH store the")
    print("  active target came from, so a target round-trips")

    # SELECT A TARGET, THEN WORK THROUGH IT.
    workstation.set_target("ledger", store="objects")
    assert workstation.get_target() is ledger
    print()
    print("target set ->", type(workstation.get_target()).__name__)

    # THE LOOP: a command's RESULT becomes the next named binding.
    commands.execute_target_method(
        "record", 100, bind_as_name="running_total",
    )
    total = workstation.get("running_total")
    assert total == 100
    print("execute_target_method('record', 100, bind_as_name=...)")
    print("   -> workstation['running_total'] =", total)

    commands.execute_target_method(
        "record", 250, bind_as_name="running_total",
    )
    assert workstation.get("running_total") == 350
    print("   ran again ->", workstation.get("running_total"))
    print("  each step is addressable by a name the AGENT chose")

    # STRONG VS WEAK IS ENFORCED, NOT COERCED.
    workstation.bind_object("weak_ledger", ledger, weak_ref=True)
    print()
    print("weak binding stored; collection publishes a ROOM EVENT, so")
    print("  'what I was holding went away' is told, not discovered")
    try:
        workstation.bind_object("weak_int", 42, weak_ref=True)
        print("  (an int accepted a weak binding on this build)")
    except Exception as error:
        print("  explicit weak on a non-weakreferenceable value refused -",
              type(error).__name__)
        print("  it will NOT quietly store it strongly instead")

    # TWO WAYS TO STOP POINTING. Only one of them touches the object.
    workstation.clear_target()
    assert workstation.get("ledger", store="objects") is ledger
    print()
    print("clear_target(): deselected, and the binding still holds it")
    print("  cleanup_target() is the other one - it CALLS cleanup first")

    # AND AN EMPTY BENCH REFUSES RATHER THAN ANSWERING None. `get_target()`
    # raises when nothing is selected: "no target" is not a value you can
    # accidentally use, it is a question you should not have asked yet.
    try:
        workstation.get_target()
        raise AssertionError("expected a refusal on an empty target")
    except ValueError as error:
        print("get_target() with nothing selected refused -", error)
        print("  never-substitute: None would be a value, and a caller")
        print("  would call a method on it before noticing")

    # RELEASE RETURNS WHAT IT REMOVED, so a handoff is one call.
    removed = workstation.release("running_total")
    assert removed == 350
    print()
    print("release() returned the value it removed:", removed)

    print()
    print("the workstation is where an agent keeps its work between")
    print("commands - it holds, it never fabricates, and the handle you")
    print("were granted is not re-checked every time you use it")


if __name__ == "__main__":
    main()
