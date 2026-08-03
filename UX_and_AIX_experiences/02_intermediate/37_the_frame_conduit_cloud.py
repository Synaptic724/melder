"""
TIER: intermediate (37)
GOAL: THE CONDUIT CLOUD - the frame's shared registry of conduits, and
      the first object in this tier that is owned by the WORLD rather
      than by you.

      You reach it from any conduit:

        cloud = conduit.get_conduit_cloud()

      And here is the sentence that matters, from melder's own contract:

        "Reaches THROUGH the aetheric frame to the frame-owned cloud, so
         the returned object is SHARED BY EVERY CONDUIT ON THE FRAME."

      So `get_conduit_cloud()` is not a factory and not a per-conduit
      view. Two conduits on the same frame hand you THE SAME OBJECT. Ask
      any of them, get the same registry - which is what makes it a
      trustworthy place to answer "what conduits exist here?"

      Frames are worlds (advanced 03), and the cloud is a world-level
      object. Different frame, different cloud - the wall holds here too.

      WHAT IT ANSWERS - all cheap reads over the frame's conduits:
        frame_name              which world am I the registry for
        count_conduits()        how many
        list_conduit_ids()      by id
        list_conduit_names()    by name
        has_conduit_id/name()   membership without fetching
        find_conduit_id_by_name(name) -> id or None
        get_conduit_by_id/name() the actual object

      AND THE CLUSTER HALF, which is dynamic-mode territory:
        list_cloud_names() / has_cluster_name() / get_cluster()
        create_cluster() / delete_cluster()
        add_conduit_to_cluster() / remove_conduit_from_cluster()
        get_clusters_for_conduit() / refresh_cluster_shares_for_conduit()
      Clusters are how conduits share lineage as a group. This lesson
      names that surface and stays on the registry half; the cluster
      lifecycle is its own subject.

      WHY THE READS MATTER MORE THAN THEY LOOK
      `find_conduit_id_by_name` returning Optional rather than raising is
      the honest shape for a lookup that may legitimately miss - and it
      pairs with has_conduit_name() so you can ask the membership question
      without paying for the object. Cheap questions before expensive
      ones, the same discipline as the describe ladder at advanced 16.
SURFACE EXERCISED: md.ConduitCloud via conduit.get_conduit_cloud(),
                   the frame-shared registry law, the read surface
VERIFY: rides the owner's 3.14t run; asserts are the contract.
"""
import melder as md


class Ledger:
    """Something to bind so the frame has real work in it."""


def main() -> None:
    book = md.Spellbook(aetheric_frame="cloud-demo")
    book.bind(spell=Ledger, existence="unique", binding_name="demo")

    root = book.conjure(name="cloud-root")
    cloud = root.get_conduit_cloud()
    assert isinstance(cloud, md.ConduitCloud)
    print("cloud for frame:", cloud.frame_name)
    assert cloud.frame_name == "cloud-demo"

    # THE SHARING LAW. A second conduit on the SAME frame reaches the
    # SAME registry object - not a copy, not a view.
    peer = md.Spellbook(aetheric_frame="cloud-demo").conjure(name="cloud-peer")
    peer_cloud = peer.get_conduit_cloud()
    assert peer_cloud is cloud, "the cloud is frame-owned, not per-conduit"
    print("second conduit reached the same object:", peer_cloud is cloud)

    # Asking the same conduit twice is stable too - it is a reach, not a
    # build, so there is nothing to be inconsistent about.
    assert root.get_conduit_cloud() is cloud

    # A DIFFERENT FRAME IS A DIFFERENT WORLD, and so a different cloud.
    # A DIFFERENT binding_name, because a spell_id does not carry the
    # frame - the same class bound identically in two frames collides
    # process-wide. The CLOUD is still per-frame; identity is not.
    other_book = md.Spellbook(aetheric_frame="cloud-other")
    other_book.bind(spell=Ledger, existence="unique", binding_name="other")
    other_root = other_book.conjure(name="other-root")
    other_cloud = other_root.get_conduit_cloud()
    assert other_cloud is not cloud
    assert other_cloud.frame_name == "cloud-other"
    print("other frame, other cloud:", other_cloud.frame_name)

    # THE READ SURFACE. Counts and lists agree with each other, which is
    # the minimum you should demand of any registry.
    names = cloud.list_conduit_names()
    ids = cloud.list_conduit_ids()
    print()
    print("conduits on this frame:", cloud.count_conduits())
    print("  names:", names)
    assert isinstance(names, tuple) and isinstance(ids, tuple)
    assert cloud.count_conduits() == len(ids)

    # Our two conduits are in there by name.
    for expected in ("cloud-root", "cloud-peer"):
        assert cloud.has_conduit_name(expected), expected
    print("both conduits registered by name")

    # MEMBERSHIP WITHOUT FETCHING. has_* answers the cheap question;
    # find_* returns Optional rather than raising, because a lookup that
    # can legitimately miss should not need a try block.
    found_id = cloud.find_conduit_id_by_name("cloud-root")
    assert found_id is not None
    assert cloud.has_conduit_id(found_id)
    print("find_conduit_id_by_name -> id, and has_conduit_id agrees")

    missing = cloud.find_conduit_id_by_name("no-such-conduit")
    assert missing is None, "a miss is None, not an exception"
    assert cloud.has_conduit_name("no-such-conduit") is False
    print("a miss returns None - no exception for an honest absence")

    # And the object itself, once you have decided you want it.
    fetched = cloud.get_conduit_by_id(found_id)
    assert fetched is root
    assert cloud.get_conduit_by_name("cloud-root") is root
    print("get_conduit_by_id / by_name returned the live conduit")

    # THE CLUSTER SURFACE, named but not exercised here.
    print()
    print("cluster surface on the cloud:")
    for verb in ("list_cloud_names", "has_cluster_name", "get_cluster",
                 "create_cluster", "delete_cluster", "add_conduit_to_cluster",
                 "remove_conduit_from_cluster", "get_clusters_for_conduit"):
        assert hasattr(cloud, verb), verb
        print("   ", verb)

    print()
    print("the cloud is FRAME-owned and shared - ask any conduit, same object")
    print("cheap questions (has_/find_) before expensive ones (get_)")


if __name__ == "__main__":
    main()
