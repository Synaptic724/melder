import inspect
import linecache
import sys

import pytest

from melder.crystallizer.synthetic_module import SyntheticModule


_SOURCE_V1 = (
    "class Widget:\n"
    "    def greet(self) -> str:\n"
    "        return 'v1'\n"
)
_SOURCE_V2 = (
    "class Widget:\n"
    "    def greet(self) -> str:\n"
    "        return 'v2'\n"
)


def _build(module_name: str, source: str) -> SyntheticModule:
    """
    Build one unregistered synthetic module for introspection tests.

    Args:
        module_name:
            Canonical module name for the test module.
        source:
            Source text the module will execute.

    Returns:
        SyntheticModule: The unmaterialized module object.
    """
    return SyntheticModule(
        module_name=module_name,
        spell_crystal_id="test_crystal",
        source_text=source,
        source_sha256="deadbeef",
        binding_signature="test_binding",
    )


@pytest.fixture()
def widget_module():
    """
    Materialize one synthetic module and tear it down after the test.

    Contract:
        - The module is fully materialized (registered, published, executed,
          importlib metadata attached) before the test body runs.
        - Teardown is unconditional cleanup for isolation.
    """
    module = _build("introspect_probe_mod", _SOURCE_V1)
    module.materialize(install_import_hook=True)
    yield module
    if not module.cleaned:
        module.cleanup()


def test_synthetic_file_identity_is_not_angle_bracketed(widget_module) -> None:
    """
    FIX B contract: the file identity must not use the `<...>` form that
    linecache's guard short-circuits on, and must carry the module name.
    """
    assert not widget_module.__file__.startswith("<")
    assert widget_module.__file__ == "synthetic://introspect_probe_mod.py"


def test_getsource_works_on_a_synthetic_class(widget_module) -> None:
    """
    The M1 regression guard: inspect.getsource on a class defined in a
    materialized synthetic module returns the retained source instead of
    raising OSError (the pre-fix symptom).
    """
    widget_cls = widget_module.__dict__["Widget"]
    source = inspect.getsource(widget_cls)
    assert "return 'v1'" in source


def test_loader_get_source_serves_live_text(widget_module) -> None:
    """
    The loader implements the InspectLoader contract over the registry and
    refuses unregistered names with ImportError.
    """
    loader = widget_module.__loader__
    assert loader.get_source("introspect_probe_mod") == _SOURCE_V1
    with pytest.raises(ImportError):
        loader.get_source("never_registered_mod")


def test_unpublish_clears_the_linecache_entry(widget_module) -> None:
    """
    R12 contract: unpublish withdraws cached source lines so a parked
    module stops serving stale introspection state.
    """
    inspect.getsource(widget_module.__dict__["Widget"])
    assert widget_module.__file__ in linecache.cache
    widget_module.unpublish_from_sys_modules()
    assert widget_module.__file__ not in linecache.cache
    assert "introspect_probe_mod" not in sys.modules


def test_reexec_serves_updated_source_not_v1(widget_module) -> None:
    """
    R12 re-exec contract: after the module's source advances and re-executes
    in place (the proven v1 -> v2 hot path), introspection must see v2 - a
    stale linecache entry must never answer with v1 lines.
    """
    inspect.getsource(widget_module.__dict__["Widget"])
    widget_module.update_source_text(_SOURCE_V2, "cafebabe")
    widget_module.execute_source()
    source = inspect.getsource(widget_module.__dict__["Widget"])
    assert "return 'v2'" in source


def test_cleanup_clears_registry_sys_modules_and_linecache() -> None:
    """
    Hard-teardown contract: cleanup unregisters, unpublishes, and drops the
    cached source lines in one deterministic pass.
    """
    module = _build("introspect_teardown_mod", _SOURCE_V1)
    module.materialize(install_import_hook=True)
    inspect.getsource(module.__dict__["Widget"])
    file_identity = module.__file__
    module.cleanup()
    assert file_identity not in linecache.cache
    assert "introspect_teardown_mod" not in sys.modules
