"""
TIER: advanced (12)
GOAL: THE WORKSTATION - the room's binding canvas, and the last fixture
      in arc B. Every RiftSpace owns one, whatever its kind.

      WHAT IT IS: a room-local scratchpad that holds things across steps.
      WHAT IT IS NOT, and this is the contract that matters:

        "Stores only room-local bindings; it does not discover or resolve
         new targets from Melder/Nexus."

      The workstation is NOT a resolver, NOT a registry, and NOT a second
      spellbook. It holds what you hand it. If you want something out of
      melder you get it through the command system (lesson 11) and then
      park it here. Keeping those two jobs apart is why the canvas can be
      wiped without touching the world.

      THREE LOGICAL STORES, kept separate on purpose:
        objects     bind_object(name, value)
        attributes  bind_attribute(name, value)
        methods     bind_method(name, value)
      Same name can live in two stores without collision, because `get`
      and `release` take a `store=` selector.

      ONE ACTIVE TARGET AT A TIME
        set_target(name, store=...)  select a saved binding as THE target
        get_target()                 read it back
        call_target(*args)           invoke it (optionally re-binding the
                                     result straight back onto the canvas)
        clear_target()               deselect without deleting the binding
      "At most one active target" is a deliberate ceiling. A canvas with
      many simultaneous targets is a canvas where "the target" stops
      meaning anything.

      WEAK BY REQUEST, AND NEVER BY ACCIDENT
        weak_ref=True   force weak storage
        weak_ref=False  force strong storage
        weak_ref=None   use the room-local default captured at creation
      And the rule worth carrying to the rest of the library:

        "Explicit weak binding RAISES when the supplied value cannot be
         weak-referenced; IT NEVER SILENTLY DEGRADES TO STRONG STORAGE."

      That is the same honesty you met at validate() in lesson 06, which
      raises instead of returning False. Melder would rather fail loudly
      than quietly give you something adjacent to what you asked for. A
      silent degrade here would mean an object you believed was
      collectable is pinned for the life of the room - a leak that looks
      like correct code.
SURFACE EXERCISED: md.Workstation via room.workstation - bind_object,
                   bind_method, get, release, describe_bindings,
                   set_target/get_target/clear_target, weak_ref semantics
VERIFY: rides the owner's 3.14t run; asserts are the contract.

DOC DRIFT FOUND AND FIXED (2026-08-02): describe_bindings() used to
document "a FOUR-KEY summary - `objects`, `attributes`, `methods` and
`target_name` - always with all four keys present, so callers can index
them" while RETURNING FIVE; the implementation also emits `target_store`.
That one had teeth, because the docstring explicitly invited callers to
rely on the count. Now documented as five, with `target_store` explained:
it names WHICH store the active target came from, so a caller can
round-trip it back through get(name, store=...).
"""
import melder as md


class Greeter:
    """A weak-referenceable object - unlike an int."""

    def greet(self) -> str:
        return "hello from the canvas"


def main() -> None:
    nexus = md.Nexus()
    system_config = nexus.create_configuration()
    system_config.with_rift_creation_enabled(True)
    nexus.activate(system_config)

    rift_config = nexus.create_rift_configuration()
    rift_config.with_space_type("capability")
    rift = nexus.create_rift(configuration=rift_config, rift_name="bench")
    rift.mark_active()

    workstation = rift.space.workstation
    assert isinstance(workstation, md.Workstation)
    assert workstation.owner_space_id == rift.space.space_id
    print("workstation:", workstation.workstation_id)
    print("owned by room:", workstation.owner_space_id == rift.space.space_id)

    # THREE STORES. The same name in two stores is not a collision.
    greeter = Greeter()
    workstation.bind_object("subject", greeter)
    workstation.bind_method("subject", greeter.greet)
    print("bound 'subject' into two different stores")

    from_objects = workstation.get("subject", store="objects")
    from_methods = workstation.get("subject", store="methods")
    assert from_objects is greeter
    assert from_methods() == "hello from the canvas"
    print("objects['subject'] is the instance; methods['subject'] is callable")

    # THE READ DOOR. Ask the canvas what is on it.
    summary = workstation.describe_bindings()
    print("describe_bindings keys:", sorted(summary))
    for store in ("objects", "attributes", "methods", "target_name"):
        assert store in summary, store
    assert "subject" in summary["objects"]
    assert "subject" in summary["methods"]

    # Five keys, and the docstring now says five. `target_store` names the
    # store the active target came from - enough to round-trip it back
    # through get(name, store=...).
    assert set(summary) == {"objects", "attributes", "methods",
                            "target_name", "target_store"}
    print("keys:", len(summary), "- documented and returned agree")

    # ONE TARGET AT A TIME.
    workstation.set_target("subject", store="methods")
    assert workstation.get_target() is not None
    print("target set from the methods store")

    result = workstation.call_target()
    assert result == "hello from the canvas"
    print("call_target ->", result)

    workstation.clear_target()
    # Clearing deselects; it does not delete the binding underneath.
    assert workstation.get("subject", store="methods") is not None
    print("target cleared; the binding it pointed at is still there")

    # WEAK BY REQUEST. A class instance can be weak-referenced.
    workstation.bind_object("weak_subject", Greeter(), weak_ref=True)
    print("weak binding accepted for a weak-referenceable object")

    # ...and an int cannot. This RAISES rather than quietly storing it
    # strongly, which is the whole point.
    try:
        workstation.bind_object("weak_number", 42, weak_ref=True)
        raise AssertionError(
            "expected a refusal - int cannot be weak-referenced"
        )
    except (TypeError, ValueError, RuntimeError) as error:
        print("explicit weak binding refused:", type(error).__name__)

    # No silent degrade means: it is not on the canvas at all.
    after = workstation.describe_bindings()
    assert "weak_number" not in after["objects"]
    print("refused binding was NOT stored strongly as a fallback")

    # release() takes it back off the canvas and hands it to you.
    released = workstation.release("subject", store="objects")
    assert released is greeter
    assert "subject" not in workstation.describe_bindings()["objects"]
    print("released 'subject' from objects; methods copy untouched:",
          "subject" in workstation.describe_bindings()["methods"])

    print()
    print("the canvas holds; the command system resolves. separate jobs.")
    print("weak when asked, never by accident - refuse instead of degrade")


if __name__ == "__main__":
    main()
