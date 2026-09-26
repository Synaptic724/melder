"""Confirm shared-path behavior through native Meld without running the slicer.

Only the peer fixture classes and ordinary World setup are reused. No SliceProbe,
uncollapsed graph build, targeting clone or executor mutation occurs here.
Run from the repository root with root and src on PYTHONPATH.
"""

import json
from pathlib import Path

from context_compass.artifacts.override_occurrence_discovery_20260924.graph_slice_probe import (
    Branch,
    PairRoot,
    Token,
    World,
)
from melder.aether.spellbook.existence.existence import Existence
from tests.experimentation.test_melder_creation_overrides_performance import _source_fingerprints


def main() -> None:
    """Record and verify the three native alias failures in isolated unmodified runtimes."""
    directory = Path(__file__).resolve().parent
    repo = directory.parents[2]
    before = _source_fingerprints(repo)
    cases = (
        ("secondary_descendant", {"right>token>value": 91}, 13),
        ("primary_cut_secondary_descendant", {"left": Branch(Token(77)), "right>token>value": 91}, 13),
        ("primary_cut_shadowed_descendant", {"left": Branch(Token(77)), "left>token>value": 91}, 91),
    )
    rows = []
    for label, overrides, expected_current in cases:
        world = World()
        try:
            world.setup_model(label, PairRoot, ((Token, Existence.many), (Branch, Existence.unique_per_conduit)))
            result = world.conduit.meld(spell_id=world.root_id, override=overrides)
            assert result.right.token.value == expected_current
            if "left" in overrides:
                assert result.left is overrides["left"]
            rows.append({
                "case": label, "right_token_value": result.right.token.value,
                "left_right_share": result.left is result.right,
                "supplied_left_preserved": result.left is overrides["left"] if "left" in overrides else None,
            })
        finally:
            world.cleanup()
    after = _source_fingerprints(repo)
    changed = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
    assert not changed, f"Source changed during confirmation: {changed}"
    (directory / "native_alias_confirmation.json").write_text(
        json.dumps({"cases": rows, "source_changed": changed, "source_sha256": before}, indent=2)
        + "\n", encoding="utf-8",
    )


if __name__ == "__main__":
    main()
