"""
TIER: beginner (18)
GOAL: unique_per_conduit_cluster - DECLARED here, LIVED later: clusters are
      groups of linked dynamic conduits (an intermediate-tier feature).
      A beginner can still bind the mode today; the book accepts it and
      the lifecycle activates once clusters exist.
SURFACE EXERCISED: md.Existence.unique_per_conduit_cluster (declaration only)
"""
import melder as md


class ClusterBus:
    pass


def main() -> None:
    book = md.Spellbook()
    spell_id = book.bind(
        spell=ClusterBus,
        existence=md.Existence.unique_per_conduit_cluster,
    )
    assert isinstance(spell_id, str)
    print("cluster-scoped binding accepted at bind time:", spell_id[:8])
    print("NOTE: cluster sharing itself needs linked dynamic conduits -")
    print("      see the intermediate tier; beginner worlds are static.")


if __name__ == "__main__":
    main()
