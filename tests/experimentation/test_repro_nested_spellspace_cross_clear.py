import gc
import inspect
from typing import Any, Dict, List

import pytest
from melder import Aether, Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import (
    configure_frame_posture_for_spellbook_configuration,
)


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_cross_clear_repro() -> None:
    """
    Purpose:
        Ensure this forensic repro starts with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_spellbook() -> Spellbook:
    """
    Purpose:
        Provide a non-dynamic Spellbook matching the failing component test.
    Contract:
        - Non-dynamic posture (the fast meld lane's only build posture).
        - phase_scheduler_workers_per_spellbook is set to 1 for determinism.
    Returns:
        Spellbook: Configured Spellbook instance.
    """
    configuration = SpellbookConfiguration()
    configuration.load_default_dictionary()
    configure_frame_posture_for_spellbook_configuration(
        configuration,
        dynamic=False,
    )
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=configuration)


class _SpaceMarker:
    """
    Purpose:
        unique_per_spell_space marker service for the cross-clear repro.
    Contract:
        - Instances are distinguishable by identity.
        - Carries no disposal methods so spellspace recycle takes the
          lock-free reset lane (the lane under investigation).
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize an identity marker.
        Contract:
            - marker is unique per instance.
        Returns:
            None.
        """
        self.marker = object()


def _describe_referrers(target: Dict[str, Any]) -> List[str]:
    """
    Purpose:
        Describe every live referrer of one inner-storage dict so the layer
        holding a captured alias names itself.
    Contract:
        - Filters interpreter frames (the test's own locals).
        - Enriches container referrers with shape hints (length, key sample)
          so a fast-door registry or store wrapper is recognizable on sight.
        - Pure reads; never mutates the referrer graph.
    Args:
        target: The inner dict whose holders are being identified.
    Returns:
        List[str]: One descriptive line per non-frame referrer.
    """
    lines: List[str] = []
    for referrer in gc.get_referrers(target):
        if inspect.isframe(referrer):
            continue
        type_name = f"{type(referrer).__module__}.{type(referrer).__name__}"
        detail = ""
        if isinstance(referrer, dict):
            key_sample = [str(key)[:24] for key in list(referrer)[:4]]
            detail = f" len={len(referrer)} keys~{key_sample}"
        elif isinstance(referrer, (list, tuple, set)):
            detail = f" len={len(referrer)}"
        lines.append(f"{type_name} id=0x{id(referrer):x}{detail}")
    return lines


def _format_report(
        *,
        case: str,
        depth_referrers: List[str],
        pre_exit_referrers: List[str],
        post_exit_referrers: List[str],
) -> str:
    """
    Purpose:
        Render the forensic report for the cross-clear investigation.
    Args:
        case: Post-exit classification of scope C's storage state.
        depth_referrers: Holders of C's inner dict right after C's meld.
        pre_exit_referrers: Holders right before D's exit.
        post_exit_referrers: Holders right after D's exit.
    Returns:
        str: Multi-line forensic report.
    """
    lines = [
        "NESTED SPELLSPACE CROSS-CLEAR REFERRER FORENSICS",
        f"case: {case}",
        f"--- holders of C's inner dict after C's meld ({len(depth_referrers)}) ---",
        *depth_referrers,
        f"--- holders right before D's exit ({len(pre_exit_referrers)}) ---",
        *pre_exit_referrers,
        f"--- holders right after D's exit ({len(post_exit_referrers)}) ---",
        *post_exit_referrers,
    ]
    return "\n".join(lines)


def test_repro_nested_spellspace_cross_clear() -> None:
    """
    Purpose:
        Reproduce the nested-spellspace store cross-clear WITHOUT mutating
        any storage identity, and name the holder of the captured alias via
        GC referrer snapshots.
    Contract:
        - Mirrors the failing component flow exactly: A -> B -> C melds,
          full depth diagnostics, then a D cycle (meld, warm re-meld, exit).
        - No tracing dicts and no rebinds: the v1 instrumentation made the
          bug vanish by detaching the captured alias, proving the guilty
          clear travels through a non-wrapper reference to C's inner dict.
        - Snapshots `gc.get_referrers` of C's inner dict at three points;
          on marker loss the report classifies the case (in-place clear vs
          wrapper rebind) and lists every holder so the capturing layer is
          identified.
    """
    spellbook = _make_spellbook()
    marker_id = spellbook.bind(
        spell=_SpaceMarker,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        with conduit.enter_spellspace() as scope_a:
            marker_a = scope_a.meld(spell=marker_id)
            with conduit.enter_spellspace() as scope_b:
                marker_b = scope_b.meld(spell=marker_id)
                assert marker_b is not marker_a
                with conduit.enter_spellspace() as scope_c:
                    marker_c = scope_c.meld(spell=marker_id)
                    assert marker_c is not marker_b
                    assert marker_c is not marker_a
                    # Identity-preserving capture of C's inner storage dict.
                    c_inner = scope_c._creations._creations
                    assert c_inner.get(marker_id) is marker_c
                    depth_referrers = _describe_referrers(c_inner)
                    with conduit.enter_spellspace() as scope_d:
                        marker_d = scope_d.meld(spell=marker_id)
                        # Mirror the component test's depth diagnostics
                        # (pure reads, kept so the flow matches exactly).
                        assert (
                            len({id(scope_a), id(scope_b), id(scope_c), id(scope_d)})
                            == 4
                        )
                        assert (
                            len(
                                {
                                    id(scope_a._creations),
                                    id(scope_b._creations),
                                    id(scope_c._creations),
                                    id(scope_d._creations),
                                }
                            )
                            == 4
                        )
                        assert scope_c._creations.get_creation(marker_id) is marker_c
                        assert marker_d is not marker_c
                        assert scope_d.meld(spell=marker_id) is marker_d
                        pre_exit_referrers = _describe_referrers(c_inner)
                    # D exited. Referrer + storage forensics on C.
                    post_exit_referrers = _describe_referrers(c_inner)
                    rebound = scope_c._creations._creations is not c_inner
                    marker_in_original = c_inner.get(marker_id) is marker_c
                    wrapper_read = scope_c._creations.get_creation(marker_id)
                    if rebound:
                        case = (
                            "WRAPPER REBOUND: a clear_all/cleanup-style path ran "
                            "against scope_c's wrapper during scope_d's exit"
                        )
                    elif not marker_in_original:
                        case = (
                            "IN-PLACE CLEAR: scope_c's inner dict was emptied "
                            "through a captured non-wrapper reference"
                        )
                    elif wrapper_read is not marker_c:
                        case = (
                            "LOOKUP DIVERGENCE: inner dict intact but wrapper "
                            "read missed (read-path bug)"
                        )
                    else:
                        case = "NO LOSS: repro did not trigger in this run"
                    report = _format_report(
                        case=case,
                        depth_referrers=depth_referrers,
                        pre_exit_referrers=pre_exit_referrers,
                        post_exit_referrers=post_exit_referrers,
                    )
                    print(report)
                    assert wrapper_read is marker_c, report
                    assert scope_c.meld(spell=marker_id) is marker_c
                assert scope_b.meld(spell=marker_id) is marker_b
            assert scope_a.meld(spell=marker_id) is marker_a
    finally:
        conduit.permanent_cleanup()
