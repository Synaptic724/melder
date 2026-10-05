"""Add the S9 owner-store-constant variant (and the S11 key-identity fact) to the certification harness."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "lazy_instance_results_20261003"))
from apply_s8 import Editor  # noqa: E402

HARNESS = "tests/experimentation/codegen_strategy_certification.py"


def main(root: pathlib.Path) -> None:
    e = Editor(root, HARNESS)
    e.replace(
        "    S8  lazy instance_results      dict mode only inside the misses: the warm path builds no dict and stores nothing\n",
        "    S8  lazy instance_results      dict mode only inside the misses: the warm path builds no dict and stores nothing\n"
        "    S9  owner-store constants      a unique site's `c = spells[i]._owner_creations` line -> `c` bound in the namespace at\n"
        "                                   hydration (automatic posture: the owner store cannot move after conjure)\n"
        "    S11 key identity               not a variant: the harness checks that every `sid` constant IS the store's key\n"
        "                                   object (the plan is emitted from live steps), and reports it\n",
    )
    e.replace(
        "def transform_prologue(source: str) -> str:\n",
        "def transform_owner_store_constants(source: str, namespace: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:\n"
        '    """S9: drop every `c{i} = spells[i]._owner_creations` line and bind `c{i}` in the namespace instead."""\n'
        "    lines, start = _executor_lines(source)\n"
        "    extra: Dict[str, Any] = {}\n"
        "    out: List[str] = []\n"
        "    for i, line in enumerate(lines):\n"
        "        m = SITE_ALIAS.match(line) if i > start else None\n"
        "        if m:\n"
        '            extra[f"c{m.group(1)}"] = namespace["spells"][int(m.group(2))]._owner_creations\n'
        "            continue\n"
        "        out.append(line)\n"
        '    return "\\n".join(out), extra\n'
        "\n"
        "\n"
        "def key_identity_report(source: str, namespace: Dict[str, Any]) -> str:\n"
        '    """S11: report whether each shared site\'s `sid` constant is the identical object the store keys by."""\n'
        "    verdicts: List[str] = []\n"
        "    for index in site_groups(source):\n"
        '        sid = namespace[f"sid{index}"]\n'
        '        store = namespace["spells"][index]._owner_creations\n'
        "        stored_key = next((key for key in store._creations if key == sid), None)\n"
        '        verdicts.append(f"sid{index}:{\'identical\' if stored_key is sid else \'equal-only\' if stored_key is not None else \'absent\'}")\n'
        '    return ", ".join(verdicts) or "no shared site"\n'
        "\n"
        "\n"
        "def transform_prologue(source: str) -> str:\n",
    )
    e.replace(
        "        if dict_mode:\n"
        '            variants.append(("S8 lazy instance_results", transform_lazy_dict(source), {}))\n',
        "        if dict_mode:\n"
        '            variants.append(("S8 lazy instance_results", transform_lazy_dict(source), {}))\n'
        "        if groups:\n"
        '            s9, x9 = transform_owner_store_constants(source, namespace); variants.append(("S9 owner-store constants", s9, x9))\n',
    )
    e.replace(
        "        extra_all: Dict[str, Any] = {}\n"
        "        if existing_idx:\n"
        "            combined, x = transform_sites(combined, namespace, existing_idx, guarded=False); extra_all.update(x)\n",
        "        extra_all: Dict[str, Any] = {}\n"
        "        if groups:\n"
        "            combined, x = transform_owner_store_constants(combined, namespace); extra_all.update(x)\n"
        "        if existing_idx:\n"
        "            combined, x = transform_sites(combined, namespace, existing_idx, guarded=False); extra_all.update(x)\n",
    )
    e.replace(
        '            variants.append(("ALL (S8+S4+S2a+S2b)", combined, extra_all))\n',
        '            variants.append(("ALL (S8+S4+S9+S2a+S2b)", combined, extra_all))\n',
    )
    e.replace(
        '            all_s1, x = transform_registration(combined, namespace, "trim"); variants.append(("ALL (S8+S4+S2a+S2b+S1)", all_s1, {**extra_all, **x}))\n',
        '            all_s1, x = transform_registration(combined, namespace, "trim"); variants.append(("ALL (S8+S4+S9+S2a+S2b+S1)", all_s1, {**extra_all, **x}))\n',
    )
    e.replace(
        '        rows.append(f"| {shape.name} | reference: conduit.meld(\\"{root_name}\\") | {ref:.0f} | | | |")\n',
        '        rows.append(f"| {shape.name} | reference: conduit.meld(\\"{root_name}\\") | {ref:.0f} | | | |")\n'
        '        rows.append(f"| {shape.name} | S11 key identity: {key_identity_report(source, namespace)} | | | | |")\n',
    )
    e.save()


if __name__ == "__main__":
    main(pathlib.Path(sys.argv[1]).resolve())
