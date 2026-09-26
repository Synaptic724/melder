"""Apply the door-held root-guard edit to generalized_hydrator.py in a tree (argv[1] = tree root)."""
import pathlib, sys
root = pathlib.Path(sys.argv[1])
p = root / ("src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/"
            "hydration/generalized_hydrator.py")
t = p.read_bytes().decode("utf-8")
crlf = "\r\n" in t
if crlf:
    assert t.count("\r\n") == t.count("\n"), "mixed line endings"
    t = t.replace("\r\n", "\n")

def rep(old: str, new: str) -> None:
    global t
    assert t.count(old) == 1, (t.count(old), old[:100])
    t = t.replace(old, new)

rep("""    3. Build `SitePlanOverrideRuntime` over them (2026-09-26, S2b-2): its
       normal plan (the empty key set) is the inner no-overrides executor, and
       it compiles one plan per override key set at first use.
""", """    3. Build `SitePlanOverrideRuntime` over them (2026-09-26, S2b-2): its
       normal plan (the empty key set) is the inner no-overrides executor, and
       it compiles one plan per override key set at first use. The runtime is
       told the manifest's route key, because every door built in step 4
       holds that route's build lock when it calls the normal plan (0.2.73).
""")
rep("""    site_plan_runtime = _build_site_plan_runtime(
        no_overrides_payload=no_overrides_payload,
        spell_lookup=no_overrides_spell_lookup,
        root_spell=root_spell,
    )
    inner_no_overrides_executor = site_plan_runtime.execute_normal
    fast_transient_no_overrides = (
""", """    site_plan_runtime = _build_site_plan_runtime(
        no_overrides_payload=no_overrides_payload,
        spell_lookup=no_overrides_spell_lookup,
        root_spell=root_spell,
        route_key=route_key,
    )
    inner_no_overrides_executor = site_plan_runtime.execute_normal
    fast_transient_no_overrides = (
""")
rep("""def _build_site_plan_runtime(
        *,
        no_overrides_payload: Dict[str, Any],
        spell_lookup: Dict[str, Any],
        root_spell: Any,
) -> SitePlanOverrideRuntime:
""", """def _build_site_plan_runtime(
        *,
        no_overrides_payload: Dict[str, Any],
        spell_lookup: Dict[str, Any],
        root_spell: Any,
        route_key: str,
) -> SitePlanOverrideRuntime:
""")
rep("""        - The runtime builds its site graph and normal plan at construction
          (first meld); requires phases 1-7 live, which meld's structural gates
          guarantee on every path that reaches hydration.

    Args:
        no_overrides_payload:
            The manifest's `no_overrides` section.
        spell_lookup:
            Live spell per step spell id.
        root_spell:
            Live root spell.
""", """        - The runtime builds its site graph and normal plan at construction
          (first meld); requires phases 1-7 live, which meld's structural gates
          guarantee on every path that reaches hydration.
        - `route_key` is passed as the runtime's `door_route_key`: this family
          calls the normal plan only from its route-keyed doors (no-overrides
          hooks and instance doors, the override door's normal fallback, the
          specializer's deopt), and each holds that route's build lock across
          the call. For "unique_per_conduit" and "spellspace" roots the normal
          plan therefore skips the re-entrant root guard (0.2.73).

    Args:
        no_overrides_payload:
            The manifest's `no_overrides` section.
        spell_lookup:
            Live spell per step spell id.
        root_spell:
            Live root spell.
        route_key:
            The manifest's route key, shared by every door of this root.
""")
rep("""    return SitePlanOverrideRuntime(
        steps=tuple(SitePlanStep.from_generalized_row(row) for row in rows),
        root_spell=root_spell,
        root_instance_key=root_instance_key,
    )
""", """    return SitePlanOverrideRuntime(
        steps=tuple(SitePlanStep.from_generalized_row(row) for row in rows),
        root_spell=root_spell,
        root_instance_key=root_instance_key,
        door_route_key=route_key,
    )
""")
if crlf:
    t = t.replace("\n", "\r\n")
p.write_bytes(t.encode("utf-8"))
print("generalized_hydrator.py edited")
