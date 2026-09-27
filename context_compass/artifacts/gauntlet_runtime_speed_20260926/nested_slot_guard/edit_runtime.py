"""Apply the door-held root-guard edit to site_plan_override_runtime.py in a tree (argv[1] = tree root)."""
import pathlib, sys
root = pathlib.Path(sys.argv[1])
p = root / "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtime.py"
t = p.read_bytes().decode("utf-8")

def rep(old: str, new: str) -> None:
    global t
    assert t.count(old) == 1, (t.count(old), old[:100])
    t = t.replace(old, new)

rep("""    Contract:
        - Construction builds the site graph from the steps and the live
          Phase-3 topologies and compiles the normal plan, exposed as
          `execute_normal(meld) -> instance`; the family hydrators install it as
          the inner no-overrides executor. Site-graph errors raise unwrapped.
""", """    Contract:
        - Construction builds the site graph from the steps and the live
          Phase-3 topologies and compiles the normal plan, exposed as
          `execute_normal(meld) -> instance`; the family hydrators install it as
          the inner no-overrides executor. Site-graph errors raise unwrapped.
        - `door_route_key` names the route of the CreationContext doors that
          call the normal plan. For "unique_per_conduit" and "spellspace" roots
          of that existence, the normal plan's root build relies on the door's
          slot guard instead of re-taking it (2026-09-26, 0.2.73): every caller
          of `execute_normal` must then hold the root's slot guard of the
          meld's route store, as the no-overrides doors, the override door
          (whose dispatcher falls back to the normal plan) and the specializer's
          deopt do. None (the default) keeps the root guard in the plan.
""")
rep("""    Threading:
        Plan lookups are lock-free dict reads. Compiles and evictions hold
        `_compile_lock`; a thread that finds a plan compiled while it waited
        uses it. Emitted plans take the normal lane's build locks.
""", """    Threading:
        Plan lookups are lock-free dict reads. Compiles and evictions hold
        `_compile_lock`; a thread that finds a plan compiled while it waited
        uses it. Emitted plans take the normal lane's build locks; the normal
        plan of a door-held root (see Contract) takes every build lock except
        the root's, which its calling door already holds.
""")
rep("""            root_spell: Spell,
            root_instance_key: SiteInstanceKey,
    ) -> None:
        \"\"\"
        Build the runtime: the site graph and the normal plan; override plans compile per key set later.

        Args:
            steps: The lane's no-overrides steps in providers-first order (owned).
            root_spell: The melded root spell (borrowed); its Spellbook's live
                Phase-3 topologies are read here.
            root_instance_key: Instance key of the root step.
""", """            root_spell: Spell,
            root_instance_key: SiteInstanceKey,
            door_route_key: Optional[str] = None,
    ) -> None:
        \"\"\"
        Build the runtime: the site graph and the normal plan; override plans compile per key set later.

        Args:
            steps: The lane's no-overrides steps in providers-first order (owned).
            root_spell: The melded root spell (borrowed); its Spellbook's live
                Phase-3 topologies are read here.
            root_instance_key: Instance key of the root step.
            door_route_key: Route key of the doors that call the normal plan,
                which hold that route's build lock across the call; None when a
                caller may not hold it. Read once, for the normal plan only;
                override key-set plans keep their root guard.
""")
rep("""        self.execute_normal: Callable[[Any], Any] = self._compile_normal_plan()
""", """        self.execute_normal: Callable[[Any], Any] = self._compile_normal_plan(door_route_key)
""")
rep("""    def _compile_normal_plan(self) -> Callable[[Any], Any]:
        \"\"\"
        Build the site graph and compile the empty key set in normal mode (S2b-2).

        Contract:
            - Runs at construction, before the runtime is shared, so no lock is
              taken. Site-graph build errors propagate unwrapped: they are not
              override key errors.
            - The plan is `(meld) -> instance`: every demanded step, shared sites
              as hit reads with out-of-line misses (B2), the family's store
              routing, build guards and registration.

        Returns:
            Callable[[Any], Any]: The normal-lane executor.
        \"\"\"
""", """    def _compile_normal_plan(self, door_route_key: Optional[str]) -> Callable[[Any], Any]:
        \"\"\"
        Build the site graph and compile the empty key set in normal mode (S2b-2).

        Contract:
            - Runs at construction, before the runtime is shared, so no lock is
              taken. Site-graph build errors propagate unwrapped: they are not
              override key errors.
            - The plan is `(meld) -> instance`: every demanded step, shared sites
              as hit reads with out-of-line misses (B2), the family's store
              routing, build guards and registration. With an eligible
              `door_route_key` the root's miss relies on the calling door's
              slot guard (`SitePlanEmission`, 0.2.73).

        Args:
            door_route_key: Route key of the doors that call this plan, or None.

        Returns:
            Callable[[Any], Any]: The normal-lane executor.
        \"\"\"
""")
rep("""            arity=0,
            normal_mode=True,
        )
        self._owned_masked_steps.extend(masked)
        code = get_or_compile_executor_code(source=source, source_name=SitePlanLowering.PLAN_SOURCE_NAME)
        exec(code, namespace)
        normal: Callable[[Any], Any] = namespace[SitePlanLowering.PLAN_FUNCTION_NAME]
        return normal
""", """            arity=0,
            normal_mode=True,
            door_route_key=door_route_key,
        )
        self._owned_masked_steps.extend(masked)
        code = get_or_compile_executor_code(source=source, source_name=SitePlanLowering.PLAN_SOURCE_NAME)
        exec(code, namespace)
        normal: Callable[[Any], Any] = namespace[SitePlanLowering.PLAN_FUNCTION_NAME]
        return normal
""")
p.write_bytes(t.encode("utf-8"))
print("site_plan_override_runtime.py edited")
