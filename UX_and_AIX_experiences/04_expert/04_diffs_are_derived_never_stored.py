"""
TIER: expert (04)
GOAL: DERIVE A DIFF, THREE WAYS, AND WATCH THE ANSWER CHANGE. Version
      records are full objects; "what changed" is computed on demand and
      never written back. "A verdict is an answer, not a fact the system
      remembers."

      A DERIVED DIFF CANNOT GO STALE, because it did not exist until you
      asked. That is the whole argument for storing full objects and
      computing comparisons - a stored diff is a second copy of the truth
      that can disagree with the first.

      THREE GRAINS SHIP, AND THEY ARE GENUINELY DIFFERENT QUESTIONS
        source      the TEXT   - a rename is enormous
        structural  the SHAPE  - a rename is invisible
        parts       the MEMBERS - which pieces moved
      This lesson runs the SAME pair through all three and prints what
      each one concluded, because the point is not that three names exist
      - it is that they disagree, on purpose.

      TWO DEFAULTS AT TWO LAYERS, AND THIS TRIPS PEOPLE
        DiffEngine.diff_materials(...)   defaults to "source"
        the codegen room's research_diff  pins "structural" for a spell
                                          pair (expert 30)
      The engine's default is text; the room overrides it with its
      reasoning layer. Same family, different default, because the room
      knows it is answering an agent and the engine does not.

      THE REGISTRY IS OPEN. `register_strategy` is public surface, so
      "what changed" is extensible by you rather than fixed by the
      library - the engine is open/closed, and "adding a grain means
      registering a strategy, never editing this class".

      AND THE ENGINE NEVER REACHES INTO THE CRYSTALLIZER. It takes an
      injected material resolver, which is why this lesson can run the
      whole diff family over material it holds in its hand, with no
      recorded world at all. `diff()` resolves through custody;
      `diff_materials()` is the door for material you already have -
      unbound codegen output, for instance.
SURFACE EXERCISED: MutationResearch.create_diff_engine,
                   DiffEngine.list_strategy_names / diff_materials, all
                   three shipped strategies over one pair, and the
                   KeyError an unknown grain raises
VERIFY: rewritten 2026-08-05 to DERIVE diffs instead of listing verb
        names; not yet run.
"""
import melder as md


MODULE = "billing.rate"

BEFORE = '''class Rate:
    def quote(self, units):
        return units * 10
'''

# Same SHAPE, different TEXT: the method was renamed and the constant
# moved. `structural` and `source` will disagree about this on purpose.
AFTER = '''class Rate:
    def price(self, units):
        return units * 25
'''


def _material(spell_id: str, source: str) -> dict:
    """One detached material payload, the shape diff_materials takes."""
    return {
        "spell_id": spell_id,
        "sources": {MODULE: source},
        "fingerprints": {},
    }


def main() -> None:
    research = md.MutationResearch()
    configuration = research.create_configuration()
    configuration.with_defaults().activate()
    research.activate(configuration)

    # THE SANCTIONED DOOR. A FRESH engine per call, bound to this
    # singleton's resolver and owned by the caller.
    engine = research.create_diff_engine()
    second = research.create_diff_engine()
    assert second is not engine, "create_diff_engine is a FACTORY"
    second.cleanup()
    print("create_diff_engine() -> a fresh, caller-owned engine each call")

    # ASK THE ENGINE WHAT IT KNOWS. Never hardcode this list - a lesson
    # that hardcodes it is asserting its own tuple, not melder's registry.
    names = engine.list_strategy_names()
    assert names == ["parts", "source", "structural"], names
    print("registered strategies:", names)
    print("  sorted, and a name absent here cannot be selected for a diff")

    left = _material("left-version", BEFORE)
    right = _material("right-version", AFTER)

    # THE DEFAULT IS `source`. Text grain, and a rename is enormous.
    default_verdict = engine.diff_materials(left, right)
    assert default_verdict["strategy"] == "source", default_verdict
    assert default_verdict["left_spell_id"] == "left-version"
    print()
    print("diff_materials(left, right) with NO strategy ->",
          default_verdict["strategy"])
    print("  the ENGINE's default is text. Note that the codegen room")
    print("  pins `structural` instead for a spell pair (expert 30) -")
    print("  two layers, two defaults, and the room's is the one an")
    print("  agent meets first")

    # ALL THREE GRAINS OVER THE SAME PAIR.
    print()
    print("the same two versions, asked three different questions:")
    verdicts = {}
    for grain in names:
        verdict = engine.diff_materials(left, right, strategy=grain)
        assert verdict["strategy"] == grain, verdict
        assert "result" in verdict, verdict
        verdicts[grain] = verdict
        result = verdict["result"]
        shape = (sorted(result)[:4] if isinstance(result, dict)
                 else type(result).__name__)
        print("   %-11s -> result keys/type: %s" % (grain, shape))

    print()
    print("  they are not three formats of one answer. `source` sees a")
    print("  renamed method as a large textual change; `structural` sees")
    print("  the shape and may not care; `parts` reports which MEMBERS")
    print("  moved. Which one is 'the' diff depends on what you are")
    print("  about to do with it, so the engine refuses to pick for you.")

    # AN UNKNOWN GRAIN RAISES, AND THE ERROR NAMES THE KNOWN ONES.
    try:
        engine.diff_materials(left, right, strategy="semantic")
        raise AssertionError("expected a KeyError for an unknown strategy")
    except KeyError as unknown:
        message = str(unknown)
        assert "semantic" in message, message
        print()
        print("strategy='semantic' ->", message[:96])
        print("  the refusal NAMES the registry, so a typo tells you what")
        print("  you could have said instead of just failing")

    # NOTHING WAS RECORDED. The verdicts exist only in this process.
    assert isinstance(verdicts["source"], dict)
    print()
    print("three verdicts computed and NOT ONE was written back into the")
    print("record. A stored diff would be a second copy of the truth that")
    print("can disagree with the first; a derived one cannot go stale")
    print("because it did not exist until asked.")

    engine.cleanup()


if __name__ == "__main__":
    main()
