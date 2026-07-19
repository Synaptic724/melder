"""
TIER: beginner (09)
GOAL: Spellframes are the grouping key above binding names - one frame
      key collects a family of related bindings, and (spellframe,
      binding_name) is the full lookup address.
SURFACE EXERCISED: bind(spellframe=...), meld(spellframe=..., binding_name=...)
"""
import melder as md


class PrimaryStore:
    role = "primary"


class ReplicaStore:
    role = "replica"


class CacheStore:
    role = "cache"


def main() -> None:
    book = md.Spellbook()
    book.bind(spell=PrimaryStore, existence=md.Existence.unique,
              spellframe="storage", binding_name="primary")
    book.bind(spell=ReplicaStore, existence=md.Existence.unique,
              spellframe="storage", binding_name="replica")
    book.bind(spell=CacheStore, existence=md.Existence.unique,
              spellframe="memory", binding_name="cache")
    conduit = book.conjure()

    primary = conduit.meld(spell=PrimaryStore, spellframe="storage",
                           binding_name="primary")
    replica = conduit.meld(spell=ReplicaStore, spellframe="storage",
                           binding_name="replica")
    cache = conduit.meld(spell=CacheStore, spellframe="memory",
                         binding_name="cache")
    assert (primary.role, replica.role, cache.role) == (
        "primary", "replica", "cache")
    print("frame families resolved: storage(primary, replica) + memory(cache)")


if __name__ == "__main__":
    main()
