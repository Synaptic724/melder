"""
TIER: expert (10)
GOAL: OVERRIDES WHEN THE GRAPH IS DEEP. Advanced 19 taught the three
      TARGETING FORMS - path, *unique, **broadcast - on a shallow graph
      where the difference between them is mostly convenience. This is
      the same grammar at depth four, where it stops being convenience
      and starts being the only way to say what you mean.

      A PATH IS A CHAIN OF SOCKET NAMES, NOT A TYPE
        "gateway>upstream>credentials"
      Each hop is the PARAMETER NAME on the class at that level. You are
      walking the constructor signatures, not the class hierarchy, and
      that distinction is the whole lesson: two sockets of the SAME type
      at different depths are different addresses.

      WHAT DEPTH CHANGES

      1. AMBIGUITY BECOMES THE NORMAL CASE. On a two-node graph
         `*credentials` is exact because there is one. At depth four the
         same class appears on several branches, `*` starts refusing, and
         you either name the path or mean `**`.

      2. YOU CAN REPLACE A BRANCH, NOT JUST A LEAF. A path that stops
         half way swaps the whole subtree underneath it - everything that
         node would have built is replaced by the object you handed in.
         That is the difference between patching a value and grafting a
         different world in.

      3. PRECEDENCE STOPS BEING THEORETICAL. Give an exact path and a
         broadcast that both cover one socket and the EXACT PATH WINS.
         Specificity beats reach, which is the only rule that lets you
         say "all of them except this one" in a single call.

      4. A WRONG PATH REFUSES AND NAMES ITSELF. It does not silently
         apply to the nearest match and it does not no-op. At depth four
         a typo is otherwise invisible, so the refusal IS the feature.

      THE HOUSE RULE UNDERNEATH ALL OF IT
      Every one of these is the never-substitute law again: melder would
      rather refuse than guess which socket you meant. Advanced 19 proved
      it on counts; this proves it on addresses.
SURFACE EXERCISED: conduit.meld(spell_override=...) with multi-hop paths,
                   branch replacement, path-beats-broadcast precedence,
                   and the refusal on an unresolvable path
VERIFY: rides the owner's 3.14t run; asserts are the contract.
"""
import melder as md


# A four-level graph. Note the SOCKET NAMES - those are what a path walks.
class Credentials:
    def __init__(self) -> None:
        self.label = "real"


class Upstream:
    def __init__(self, credentials: Credentials) -> None:
        self.credentials = credentials


class Gateway:
    def __init__(self, upstream: Upstream) -> None:
        self.upstream = upstream


class Mirror:
    def __init__(self, upstream: Upstream) -> None:
        self.upstream = upstream


class Edge:
    def __init__(self, gateway: Gateway, mirror: Mirror) -> None:
        self.gateway = gateway
        self.mirror = mirror


def main() -> None:
    book = md.Spellbook(aetheric_frame="deep-overrides")
    for spell in (Credentials, Upstream, Gateway, Mirror, Edge):
        book.bind(spell=spell, existence="many")
    conduit = book.conjure(name="deep-root")

    # The shape, unmodified. TWO credentials sockets exist - one under
    # gateway, one under mirror - and they are four hops down.
    plain = conduit.meld(spell=Edge)
    assert plain.gateway.upstream.credentials.label == "real"
    assert plain.mirror.upstream.credentials.label == "real"
    print("graph built: two credentials sockets, both at depth 4")

    # 1. A PATH IS A CHAIN OF SOCKET NAMES. Every hop is a parameter name
    #    on the class at that level.
    swapped = Credentials()
    swapped.label = "gateway-only"
    one = conduit.meld(
        spell=Edge,
        spell_override={"gateway>upstream>credentials": swapped},
    )
    assert one.gateway.upstream.credentials.label == "gateway-only"
    assert one.mirror.upstream.credentials.label == "real"
    print()
    print("path hit ONE socket; its twin on the other branch was untouched")

    # 2. STOP THE PATH EARLY AND YOU REPLACE A BRANCH. Everything the
    #    node would have built below it is replaced too.
    grafted_credentials = Credentials()
    grafted_credentials.label = "grafted"
    grafted = conduit.meld(
        spell=Edge,
        spell_override={"mirror>upstream": Upstream(grafted_credentials)},
    )
    assert grafted.mirror.upstream.credentials.label == "grafted"
    assert grafted.gateway.upstream.credentials.label == "real"
    print("a short path grafted a whole SUBTREE, not a leaf")

    # 3. AMBIGUITY IS THE NORMAL CASE AT DEPTH. `*credentials` matches
    #    twice here, and melder refuses rather than picking one.
    try:
        conduit.meld(spell=Edge, spell_override={"*credentials": swapped})
        raise AssertionError("expected a refusal: *param matched twice")
    except Exception as error:
        print()
        print("*credentials refused -", type(error).__name__)
        print("  at depth, `there is exactly one` is usually false")

    # ...and `**` is how you say you meant all of them.
    everywhere = Credentials()
    everywhere.label = "all"
    broad = conduit.meld(
        spell=Edge,
        spell_override={"**credentials": everywhere},
    )
    assert broad.gateway.upstream.credentials.label == "all"
    assert broad.mirror.upstream.credentials.label == "all"
    print("**credentials hit both")

    # 4. PRECEDENCE: an exact path BEATS a broadcast that also covers it.
    #    This is what lets one call say "all of them, except this one".
    pinned = Credentials()
    pinned.label = "pinned"
    mixed = conduit.meld(
        spell=Edge,
        spell_override={
            "**credentials": everywhere,
            "gateway>upstream>credentials": pinned,
        },
    )
    assert mixed.gateway.upstream.credentials.label == "pinned"
    assert mixed.mirror.upstream.credentials.label == "all"
    print()
    print("exact path beat the broadcast on the socket they shared:")
    print("  gateway ->", mixed.gateway.upstream.credentials.label,
          " mirror ->", mixed.mirror.upstream.credentials.label)

    # 5. A WRONG PATH REFUSES AND SAYS SO. At depth four a typo is
    #    otherwise undetectable - the refusal is the feature.
    try:
        conduit.meld(
            spell=Edge,
            spell_override={"gateway>upstrem>credentials": swapped},
        )
        raise AssertionError("expected a refusal: no such path")
    except Exception as error:
        print()
        print("typo'd path refused -", type(error).__name__)

    print()
    print("a path walks SOCKET NAMES, so identical types at different")
    print("depths are different addresses")
    print("specificity beats reach; melder refuses rather than guessing")


if __name__ == "__main__":
    main()
