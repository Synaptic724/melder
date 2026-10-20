"""S3 closure sync: route the melder_object_pools row to S4, add the S3 closed anchor (cap 12, oldest dropped),
the 0.2.8243 notch notice, and repoint the two S3 patch-doc rows on the artifact board at the epic.
Every anchor must match exactly once or nothing is written."""
import pathlib
import sys

NOW = sys.argv[1]


def apply(path: pathlib.Path, replacements: list) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new in replacements:
        count = text.count(old)
        if count != 1:
            raise SystemExit(f"{path}: anchor matched {count} times, nothing written:\n{old[:200]}")
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")
    print("updated", path)


ATTENTION = [
    (
        "| melder_object_pools | in_progress | implementation | claude | melder_0 | none | S3: read the pool base, "
        "Creations and the Meld store readers whole, write the pool patches and mapping note, then red tests. | "
        "`managed_spell_quantity` built in seven stories (epic Build Specification), one notch per story, rebuild "
        "last. | Every story landed with green tests and the owner accepts, or the owner redirects. | "
        "tickets/stories/2026-10-15_managed_quantity_pool_story.md | 2026-10-15T12:47:47Z | REQUIRED |\n",
        "| melder_object_pools | in_progress | implementation | claude | melder_0 | none | S4: read aether.py's "
        "singleton slot, init, cleanup and reset hook plus one hosted root whole (U11), then the S4 patch and "
        "mapping note. | `managed_spell_quantity` built in seven stories (epic Build Specification), one notch per "
        "story, rebuild last. | Every story landed with green tests and the owner accepts, or the owner redirects. | "
        f"tickets/stories/2026-10-15_release_managed_spell_story.md | {NOW} | REQUIRED |\n",
    ),
    (
        "    - tickets/epics/2026-10-14_managed_spell_quantity_epic.md\n"
        "    - tickets/stories/2026-10-15_managed_quantity_pool_story.md\n",
        "    - tickets/epics/2026-10-14_managed_spell_quantity_epic.md\n"
        "    - tickets/stories/2026-10-15_release_managed_spell_story.md\n",
    ),
    (
        "| many_child_registration | done | melder_1 | tickets/epics/completed/2026-10-14_many_child_follows_holder_epic.md "
        "| 0.2.8235 plus its purge/transfer follow-ups (0.2.8238, slotted lane); turned in by owner directive. Next: "
        "none. | 2026-10-15T01:38:07Z |\n",
        "",
    ),
    (
        "<!-- END USER-DEFINED: closed_anchors -->\n",
        "| managed_quantity_pool | done | melder_0 | tickets/stories/completed/2026-10-15_managed_quantity_pool_story.md "
        "| Landed 0.2.8243 (S3 of EPIC-2026-10-14-managed_spell_quantity: the pool, the exhaustion error, the "
        "Creations pool map, the probes, purge 0). Next: S4 registry. | 2026-10-15T13:54:48Z |\n"
        "<!-- END USER-DEFINED: closed_anchors -->\n",
    ),
    (
        "  managed-only id part, RecordVersion 4.2.0 with restore/graft replay; S2). Notch above it if you land after.\n",
        "  managed-only id part, RecordVersion 4.2.0 with restore/graft replay; S2). Notch above it if you land after.\n"
        "- melder_0 landed 0.2.8243 (the managed pool `ManagedSpellQuantity` in the owning root's Creations,\n"
        "  `ManagedSpellExhaustedError`, the probes' managed answer and purge 0; S3). Notch above it if you land after.\n",
    ),
]

ARTIFACT = [
    (
        "| tickets/stories/2026-10-15_managed_quantity_pool_story.md | system_docs/patches/active/"
        "managed_spell_quantity_2026_10_15/component_patch_managed_quantity_pool.md | patch_doc | active | "
        "promote_to_documentation | S3: the pool (sizes, reserve, put_back, abandon, adopt, destroy, cleanup), the "
        "exhaustion error, the Creations map, ensure, cleanup order, extract/restore rows, purge 0, the probes. | "
        "2026-10-15T12:54:26Z | REQUIRED |\n",
        "| tickets/epics/2026-10-14_managed_spell_quantity_epic.md | system_docs/patches/active/"
        "managed_spell_quantity_2026_10_15/component_patch_managed_quantity_pool.md | patch_doc | active | "
        "promote_to_documentation | S3 (landed 0.2.8243, story closed): the pool (sizes, reserve, put_back, abandon, "
        "adopt, destroy, cleanup), the exhaustion error, the Creations map, ensure, cleanup order, extract/restore "
        f"rows, purge 0, the probes; promote at S7. | {NOW} | REQUIRED |\n",
    ),
    (
        "| tickets/stories/2026-10-15_managed_quantity_pool_story.md | system_docs/patches/active/"
        "managed_spell_quantity_2026_10_15/code_description_patch_managed_quantity_pool.md | patch_doc | active | "
        "promote_to_documentation | S3: the pool's state, control flow per mode, locks, edge semantics and "
        "invariants. | 2026-10-15T12:54:26Z | REQUIRED |\n",
        "| tickets/epics/2026-10-14_managed_spell_quantity_epic.md | system_docs/patches/active/"
        "managed_spell_quantity_2026_10_15/code_description_patch_managed_quantity_pool.md | patch_doc | active | "
        "promote_to_documentation | S3 (landed 0.2.8243, story closed): the pool's state, control flow per mode, "
        f"locks, edge semantics and invariants; promote at S7. | {NOW} | REQUIRED |\n",
    ),
]

apply(pathlib.Path("attention_board.md"), ATTENTION)
apply(pathlib.Path("artifact_board.md"), ARTIFACT)
