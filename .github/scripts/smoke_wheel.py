"""Exercise the installed wheel's packaged documents from an isolated interpreter."""

import sysconfig


def main() -> None:
    """Require the installed package and its document assets to work without checkout imports.

    Run with the wheel virtual environment's Python and -I. Check the import path
    before exercising runtime documents so an editable/source checkout cannot
    accidentally satisfy this distribution-level test.
    """
    import pathlib
    import melder
    from melder._build_assets._agent_documentation.manifest.agent_documentation_manifest import MARKED_COUNT
    from melder._build_assets._bind_guard.manifest.bind_guard_manifest import ENTRY_COUNT
    from melder._build_assets._system_documents.manifest.system_documents_manifest import DOCUMENT_COUNT

    installed = pathlib.Path(sysconfig.get_path("purelib")).resolve()
    if not pathlib.Path(melder.__file__).resolve().is_relative_to(installed):
        raise RuntimeError("Wheel smoke test imported Melder outside the isolated site-packages.")
    documents = (melder.__architecture__, melder.__components__,
                 melder.__graph_network__, melder.__graph_details__)
    if not all(document.verify() for document in documents):
        raise RuntimeError("Installed wheel contains an invalid packaged runtime document.")
    if MARKED_COUNT <= 0 or ENTRY_COUNT <= 0 or DOCUMENT_COUNT != 4:
        raise RuntimeError("Installed wheel is missing required runtime manifest content.")
    graph = melder.__graph_network__
    if graph.node_count <= 0 or graph.edge_count <= 0:
        raise RuntimeError("Installed graph document is empty.")
    node = graph.node("melder.aether.aether.Aether")
    if graph.details_key(node.node_id) != node.source:
        raise RuntimeError("Installed graph detail lookup disagrees with its node source.")
    print(f"OK: installed Melder {melder.__version__}; four documents and graph lookup verified.")


if __name__ == "__main__":
    main()
