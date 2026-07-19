"""
TIER: beginner (12) - the AIX seat
GOAL: An agent's first sixty seconds with melder: read the workflow map
      from help(), read the version, then open the hardcopy system docs
      the package carries about itself. No filesystem, no web - the
      library IS its own documentation.
SURFACE EXERCISED: md.__doc__, md.__version__, md.__all__,
                   md.__architecture__, md.__components__,
                   md.__graph_network__, md.__graph_details__
"""
import melder as md


def main() -> None:
    assert "Workflow map" in md.__doc__
    print("workflow map present in help(melder)")
    print("version:", md.__version__)

    # the four hardcopy documents ride the wheel - an agent reads the
    # system before touching it
    for name in ("__architecture__", "__components__",
                 "__graph_network__", "__graph_details__"):
        doc = getattr(md, name)
        assert doc is not None
        print(name, "->", type(doc).__name__)

    print("public surface advertised:", len(md.__all__), "names")


if __name__ == "__main__":
    main()
