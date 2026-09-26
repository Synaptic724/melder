"""September plan, tests part 1: unskip the September regressions; stubs model the new Spell fields.

Usage: python apply_sept_test_stubs.py <repo_root>
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from patch_util import replace_block

root = pathlib.Path(sys.argv[1])
integration = root / "tests/integration/melder/conduit/test_conduit_integration_concurrency.py"
component = root / "tests/component/melder/aether/conduit/test_shared_context_rebuild_publication.py"
concrete = root / "tests/unit/melder/aether/conduit/meld/test_concrete_meld_subclasses.py"
meld_tests = root / "tests/unit/melder/aether/conduit/meld/test_meld.py"

replace_block(integration,
'''@pytest.mark.skip(
    reason="Deferred by project owner for release; shared-context revalidation investigation remains open."
)
def test_conduit_cluster_concurrent_meld_two_clusters_isolated() -> None:''',
'''def test_conduit_cluster_concurrent_meld_two_clusters_isolated() -> None:''')
replace_block(component,
'''@pytest.mark.skip(
    reason="Deferred by project owner; shared-context rebuild investigation remains open."
)
def test_owner_meld_waits_for_peer_rebuild_before_using_context_inputs(''',
'''def test_owner_meld_waits_for_peer_rebuild_before_using_context_inputs(''')

replace_block(concrete,
'''        self._creation_context = creation_context
        self._creation_context_factory = None
        # fast_state mirrors the real CounterSwitch hot-path slot the meld''',
'''        self._creation_context = creation_context
        self._creation_context_factory = None
        # Mirror the real Spell fields: automatic ownership has no
        # spell-index gate, and no build has failed.
        self._creation_gate = None
        self._creation_context_failure = None
        # fast_state mirrors the real CounterSwitch hot-path slot the meld''')
replace_block(meld_tests,
'''        self._creation_context = creation_context
        self._creation_context_factory = None
        if creation_context is None:''',
'''        self._creation_context = creation_context
        self._creation_context_factory = None
        # Mirror the real Spell fields: automatic ownership has no
        # spell-index gate, and no build has failed.
        self._creation_gate = None
        self._creation_context_failure = None
        if creation_context is None:''')
