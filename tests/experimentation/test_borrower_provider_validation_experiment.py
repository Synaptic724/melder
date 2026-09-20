"""Observe provider data, compiled plans and injection across borrower operations.

The integration regressions assert corrected behavior. This experiment records
the present behavior without weakening the original independent-prefix proofs.
"""

import json

import pytest

from tests.integration.melder.spellbook.test_provider_artifact_ownership import (
    ProviderRuntime,
    provider_runtime as provider_runtime,
)


@pytest.mark.parametrize("mode", ("no_validation", "resolution_only", "structural_refresh", "meld_only"))
@pytest.mark.parametrize("borrower_count", (1, 2))
def test_characterize_provider_validation_boundary(
        provider_runtime: ProviderRuntime,
        mode: str,
        borrower_count: int,
) -> None:
    """Observe repeated validation and direct meld without intermediate provider lookups.

    Reading artifact slots is passive. The final provider meld is performed
    once, after borrower cleanup, so it cannot repair earlier observations.
    Successful consumer injection must retain the original provider identity.
    """
    runtime = provider_runtime
    assert runtime.provider_spell._compiler_artifact._spell_codegen_creation is not None
    borrowers = [
        (f"consumer-{index}", runtime.create_borrower(f"consumer-{index}"))
        for index in range(borrower_count)
    ]
    injected = 0
    if mode in ("resolution_only", "structural_refresh"):
        for _ in range(2):
            for _name, borrower in borrowers:
                borrower.validate_resolution(refresh_structural=mode == "structural_refresh")
    if mode != "no_validation":
        for name, borrower in borrowers:
            consumer = borrower.meld(spellframe="consumers", binding_name=name)
            assert consumer.provider is runtime.original
            injected += 1
    report: dict[str, object] = {
        "mode": mode,
        "borrowers": borrower_count,
        "consumer_injections_same_instance": injected,
        "provider_plan_present": runtime.provider_spell._compiler_artifact._spell_codegen_creation is not None,
        "provider_resolution_complete": runtime.provider_spell.resolution_complete,
    }
    for _name, borrower in reversed(borrowers):
        borrower.cleanup()
    assert runtime.original.entries == ["provider-owned"]
    report["provider_data_retained"] = True
    try:
        runtime.assert_provider_usable()
    except RuntimeError as error:
        if "Cannot build CreationContext before spell_codegen_creation exists" not in str(error):
            raise
        report["provider_meld"] = "missing_codegen"
    else:
        report["provider_meld"] = "same_instance"
    if mode == "no_validation":
        assert report["provider_meld"] == "same_instance"
    print(json.dumps(report, sort_keys=True))
