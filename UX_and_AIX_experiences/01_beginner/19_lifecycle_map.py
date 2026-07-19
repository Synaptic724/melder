"""
TIER: beginner (19)
GOAL: The whole beginner lifecycle vocabulary on one page. Three modes
      answer one question - where does instance reuse stop? - and three
      is enough to build real things. (Three more exist for bigger
      worlds; they live in the later tiers.)
SURFACE EXERCISED: md.Existence.unique / many / unique_per_conduit
"""
import melder as md


def main() -> None:
    beginner_three = [
        ("unique", "ONE instance, shared everywhere", "app config, registries"),
        ("unique_per_conduit", "one per scope, stable inside it", "sessions, caches"),
        ("many", "fresh construction EVERY meld", "requests, jobs, tickets"),
    ]
    for name, rule, use in beginner_three:
        member = getattr(md.Existence, name)
        print(f"{member.name:20s} {rule:38s} e.g. {use}")

    later = [m.name for m in md.Existence
             if m.name not in {n for n, _, _ in beginner_three}]
    print("later tiers add:", ", ".join(sorted(later)))
    assert len(beginner_three) == 3
    print("three modes, one question: where does reuse stop?")


if __name__ == "__main__":
    main()
