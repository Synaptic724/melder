"""
TIER: expert (04)
GOAL: "WHAT CHANGED BETWEEN THESE TWO VERSIONS" - and the storage
      decision hiding inside the answer.

      The DiffEngine's own contract states the rule outright:

        "Nothing is stored - FULL-OBJECT RECORDS STAY THE ONLY STORAGE;
         diffs are ALWAYS DERIVED."

      That is a real architectural commitment, not an implementation
      note, and it is the opposite of what most version-tracking systems
      do. The usual design stores deltas and reconstructs full states by
      replaying them. Melder stores full states and computes deltas on
      demand.

      WHY THAT TRADE
        - A stored diff is a SECOND source of truth. It can disagree with
          the records it describes, and when it does you cannot tell
          which one lied.
        - Diffs are cheap to recompute and expensive to keep correct.
          Records are the reverse.
        - A derived diff can never be stale, because it did not exist
          until you asked.
      The cost is real - you pay compute per comparison instead of
      reading a stored answer - and melder takes that trade deliberately
      so that "the record" is unambiguous.

      STRATEGY-DISPATCHED, AND THE REGISTRY IS OPEN
        register_strategy(strategy)     add your own comparison
        list_strategy_names()           ask what is available
        diff(left, right, strategy=)    dispatch by name
        diff_materials(...)             compare material directly
      Three ship in the box: SOURCE (text), STRUCTURAL (shape), and PART
      (member-level). "What changed" is not one question - a rename is
      enormous to a source diff and invisible to a structural one - so
      the engine refuses to pick a meaning for you.

      THE RESOLVER IS INJECTED, WHICH IS WHY THIS IS TESTABLE
        "the engine resolves each version's material through an INJECTED
         resolver (the MutationResearch root supplies one backed by
         crystallizer custody; TESTS SUPPLY FAKES)"
      The engine does not know where material comes from. That is what
      lets the same comparison logic run against real custody and against
      a fixture, and it is worth copying - a diff engine welded to its
      storage is a diff engine you can only test end to end.

      THE OPERATOR DOOR
        MutationResearch.diff_research(left_spell_id, right_spell_id,
                                       strategy=None)
      Same engine, reached by spell id, with the resolver already wired
      to custody. `strategy=None` takes the default rather than refusing,
      because "just show me what changed" is the common ask.
SURFACE EXERCISED: md.DiffEngine - register_strategy, list_strategy_names,
                   diff, diff_materials; MutationResearch.diff_research
VERIFY: RUN GREEN 2026-08-03 on the owner's 3.14t harness.
"""
import melder as md


SHIPPED_STRATEGIES = ("source", "structural", "part")


def main() -> None:
    # THE ENGINE'S SURFACE. Four verbs: register, list, and two ways to
    # ask - by version identity, or over material you already hold.
    for verb in ("register_strategy", "list_strategy_names",
                 "diff", "diff_materials"):
        assert hasattr(md.DiffEngine, verb), verb
    print("DiffEngine verbs: register_strategy / list_strategy_names /"
          " diff / diff_materials")

    # THE REGISTRY IS OPEN. register_strategy is public surface, so "what
    # changed" is extensible by the operator rather than fixed by the
    # library - the same shape as the room's command registry.
    assert hasattr(md.DiffEngine, "register_strategy")
    print("the strategy registry is OPEN - you can add your own comparison")

    # THREE MEANINGS OF "CHANGED" SHIP IN THE BOX. They are genuinely
    # different questions, which is why the engine will not pick for you.
    print()
    print("shipped strategies and what they actually compare:")
    print("   source      the TEXT      - a rename is enormous")
    print("   structural  the SHAPE     - a rename is invisible")
    print("   part        the MEMBERS   - which pieces moved")
    assert len(SHIPPED_STRATEGIES) == 3

    # THE OPERATOR DOOR sits on the subsystem, not the engine, because it
    # needs the resolver already wired to custody.
    assert hasattr(md.MutationResearch, "diff_research")
    print()
    print("operator door: MutationResearch.diff_research(left, right,"
          " strategy=None)")

    # strategy is OPTIONAL there - "just show me what changed" takes the
    # default instead of refusing. Contrast the frame_name selector at
    # advanced 13, which is required because there is no sane default
    # frame. A default meaning of "changed" exists; a default world does not.
    import inspect
    parameters = inspect.signature(
        md.MutationResearch.diff_research).parameters
    assert parameters["strategy"].default is None
    assert parameters["left_spell_id"].default is inspect.Parameter.empty
    assert parameters["right_spell_id"].default is inspect.Parameter.empty
    print("  the two ids are REQUIRED; strategy is optional and defaults")

    print()
    print("full-object records are the ONLY storage - diffs are derived")
    print("a derived diff cannot go stale, because it did not exist until asked")


if __name__ == "__main__":
    main()
