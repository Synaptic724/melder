"""Exercise installed package identity, data, and a small public runtime contract in isolation."""

import argparse
import importlib.metadata
import sys
import sysconfig
from collections.abc import Sequence
from typing import Optional


class PackageProbeService:
    """A stateless user service proving that an installed Melder can bind and resolve user code."""

    def greeting(self) -> str:
        """Return a fixed observable result for the package consumer contract."""
        return "installed-melder-ok"


def check_runtime() -> None:
    """Exercise real public binding, unique reuse, and deterministic conduit/book cleanup."""
    import melder

    book = melder.Spellbook()
    try:
        book.bind(spell=PackageProbeService, existence="unique")
        conduit = book.conjure()
        try:
            service = conduit.meld(spell=PackageProbeService)
            if service.greeting() != "installed-melder-ok":
                raise RuntimeError("Installed package failed the public service-resolution contract.")
            if conduit.meld(spell=PackageProbeService) is not service:
                raise RuntimeError("Installed package did not preserve unique existence.")
        finally:
            conduit.cleanup()
    finally:
        book.cleanup()


def main(argv: Optional[Sequence[str]] = None) -> None:
    """Require the installed package and its document assets to work without checkout imports.

    Run with the wheel virtual environment's Python and -I. Check the import path
    before exercising runtime documents so an editable/source checkout cannot
    accidentally satisfy this distribution-level test.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-version")
    args = parser.parse_args(argv)
    import pathlib
    import melder
    from melder._build_assets._agent_documentation.manifest.agent_documentation_manifest import MARKED_COUNT
    from melder._build_assets._bind_guard.manifest.bind_guard_manifest import ENTRY_COUNT
    from melder._build_assets._system_documents.manifest.system_documents_manifest import DOCUMENT_COUNT

    installed = pathlib.Path(sysconfig.get_path("purelib")).resolve()
    if not pathlib.Path(melder.__file__).resolve().is_relative_to(installed):
        raise RuntimeError("Wheel smoke test imported Melder outside the isolated site-packages.")
    if importlib.metadata.version("melder") != melder.__version__:
        raise RuntimeError("Installed distribution metadata disagrees with Melder's runtime version.")
    if args.expected_version is not None and melder.__version__ != args.expected_version:
        raise RuntimeError("Installed Melder version differs from the selected candidate.")
    if sysconfig.get_config_var("Py_GIL_DISABLED") != 1 or sys._is_gil_enabled():
        raise RuntimeError("Package probe requires Python 3.14t with the GIL disabled.")
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
    check_runtime()
    if sys._is_gil_enabled():
        raise RuntimeError("The package consumer scenario unexpectedly enabled the GIL.")
    print(f"OK: installed Melder {melder.__version__}; metadata, documents, graph, and runtime verified.")


if __name__ == "__main__":
    main()
