"""
TIER: intermediate (31)
GOAL: SpellbookConfiguration, knob by knob - part 2: the performance
      knob. generalized_singleton_specialization_enabled (bool, default
      False) opts the generalized no-overrides meld lane into its THIRD
      door stage: cold -> hot -> SPECIALIZED.
      What actually happens (source: generalized_hydrator +
      generalized_manifest_no_overrides_compiler): after the FIRST
      successful hot execution, the executor body is REBUILT with the
      owner-store `unique` DEPENDENCY singletons captured directly in
      its closure - so warm melds stop paying the per-dependency store
      lookups when building the graph. Every captured dependency sits
      behind an epoch guard: if that dependency is ever invalidated,
      the guard fails and resolution falls back to the honest path.
      The flag is read ONCE per hydration (missing/unavailable reads as
      OFF - strictly opt-in, zero overhead when off), and semantics are
      IDENTICAL either way - this knob tunes what warm construction
      COSTS, never what it answers.
SURFACE EXERCISED: generalized_singleton_specialization_enabled
"""
import melder as md


class Config:
    pass


class Report:
    def __init__(self, config: Config) -> None:
        self.config = config


def main() -> None:
    book = md.Spellbook()
    book.get_configuration().set_property(
        "generalized_singleton_specialization_enabled", True)

    # The shape this knob exists for: a fresh-per-meld root built over
    # a shared unique dependency. Every warm build of Report needs
    # Config - specialization captures that singleton in the executor
    # body after the first construction instead of looking it up per
    # meld.
    book.bind(spell=Config, existence="unique")
    book.bind(spell=Report, existence="many")
    conduit = book.conjure()

    first = conduit.meld(spell=Report)    # cold: full build, deps resolved
    second = conduit.meld(spell=Report)   # warm: specialized body
    third = conduit.meld(spell=Report)

    # SEMANTICS UNCHANGED - the same assertions hold with the knob off:
    assert first is not second is not third          # many = fresh roots
    assert first.config is second.config is third.config  # one captured dep
    print("fresh reports over one captured singleton:",
          first.config is third.config)
    print("the knob tunes warm-path COST, never the answers")


if __name__ == "__main__":
    main()
