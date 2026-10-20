"""Apply S6 part A to src/: the managed settings leave the spell_id; a same-id rebind re-composes its pool.

Run from the repository root:  python3 context_compass/artifacts/correctness_defects_20261017/scripts/s6_part_a_src.py [--dry-run]
Files: bind.py (fingerprint, inspector, docstrings; `_managed_fingerprint_part` removed), managed_spell_quantity.py
(`_rebind_spell` re-composes), creations.py (the rebind after the store lock), caching_system.py (generation 22),
managed_spell_mode.py and spell_crystal.py (docstrings). Every replacement must match exactly once.
"""
import pathlib
import sys

DRY = "--dry-run" in sys.argv
writes = {}


def load(path):
    p = pathlib.Path(path)
    if p not in writes:
        writes[p] = p.read_text(encoding="utf-8")
    return p


def sub(path, old, new):
    p = load(path)
    assert writes[p].count(old) == 1, (path, old[:90], writes[p].count(old))
    writes[p] = writes[p].replace(old, new, 1)


BIND = "src/melder/aether/spellbook/bind/bind.py"
POOL = "src/melder/aether/conduit/creations/managed_spell_quantity.py"
STORE = "src/melder/aether/conduit/creations/creations.py"
CACHE = "src/melder/utilities/caching_system/caching_system.py"
MODE = "src/melder/aether/spellbook/existence/managed_spell_mode.py"
CRYSTAL = "src/melder/crystallizer/crystals/spell_crystal.py"

# --- bind.py -------------------------------------------------------------------------------------------------------
sub(BIND,
    "        * Validates and normalizes the four managed options once\n"
    "          (`_normalize_managed_options`), after the profile and before the fingerprint;\n"
    "          a managed binding hashes them as one extra part and the Spell keeps them.\n",
    "        * Validates and normalizes the four managed options once\n"
    "          (`_normalize_managed_options`), after the profile; the Spell keeps them. They are\n"
    "          settings of the one spell, not its identity: the fingerprint never reads them\n"
    "          (owner ruling 2026-10-17), so a managed class bound with other settings at the same\n"
    "          address, existence and disposal list gets the same spell_id.\n")
sub(BIND,
    "            # Managed options (Existence.managed_spell_quantity): validated and normalized here, once,\n"
    "            # because they are hashed into a managed spell's id and kept by its Spell; any other\n"
    "            # existence must leave all four unset. Refusals happen before a Spell or index exists.\n",
    "            # Managed options (Existence.managed_spell_quantity): validated and normalized here, once,\n"
    "            # and kept by the Spell. They are settings, not identity: the fingerprint below never reads\n"
    "            # them (owner ruling 2026-10-17). Any other existence must leave all four unset. Refusals\n"
    "            # happen before a Spell or index exists.\n")
sub(BIND,
    "                disposal_method_names=resolved_disposal_method_names,\n"
    "                resolvable=resolvable,\n"
    "                managed_spell_mode=normalized_managed_mode,\n"
    "                managed_spell_limit=normalized_managed_limit,\n"
    "                managed_spell_timeout_seconds=normalized_managed_timeout,\n"
    "                managed_spell_reset_methods=normalized_managed_reset_methods,\n"
    "            )\n"
    "            spell_index = SpellIndex(initial_id=fingerprint)\n",
    "                disposal_method_names=resolved_disposal_method_names,\n"
    "                resolvable=resolvable,\n"
    "            )\n"
    "            spell_index = SpellIndex(initial_id=fingerprint)\n")
sub(BIND,
    "            - Normalizes and checks the managed options with bind's own\n"
    "              `_normalize_managed_options`, so a managed fingerprint matches bind's.\n",
    "            - Checks the managed options with bind's own `_normalize_managed_options`,\n"
    "              so it refuses exactly what bind refuses; like bind, it never hashes them\n"
    "              (a managed spell_id does not depend on its settings).\n")
sub(BIND,
    "        (\n"
    "            normalized_managed_mode,\n"
    "            normalized_managed_limit,\n"
    "            normalized_managed_timeout,\n"
    "            normalized_managed_reset_methods,\n"
    "        ) = Bind._normalize_managed_options(\n"
    "            spell,\n"
    "            profile.binding_profile,\n"
    "            str(display_name),\n",
    "        # Checked as bind checks them, never hashed: a managed spell's settings are not part of its spell_id.\n"
    "        Bind._normalize_managed_options(\n"
    "            spell,\n"
    "            profile.binding_profile,\n"
    "            str(display_name),\n")
sub(BIND,
    "            disposal_method_names=tuple(disposal_method_names),\n"
    "            resolvable=resolvable,\n"
    "            managed_spell_mode=normalized_managed_mode,\n"
    "            managed_spell_limit=normalized_managed_limit,\n"
    "            managed_spell_timeout_seconds=normalized_managed_timeout,\n"
    "            managed_spell_reset_methods=normalized_managed_reset_methods,\n"
    "        )\n",
    "            disposal_method_names=tuple(disposal_method_names),\n"
    "            resolvable=resolvable,\n"
    "        )\n")
sub(BIND,
    "            disposal_method_names: Sequence[str] = (),\n"
    "            resolvable: bool = True,\n"
    "            managed_spell_mode: Optional[ManagedSpellMode] = None,\n"
    "            managed_spell_limit: Optional[int] = None,\n"
    "            managed_spell_timeout_seconds: Optional[float] = None,\n"
    "            managed_spell_reset_methods: Sequence[str] = (),\n"
    "    ) -> str:\n",
    "            disposal_method_names: Sequence[str] = (),\n"
    "            resolvable: bool = True,\n"
    "    ) -> str:\n")
sub(BIND,
    "            - A managed binding (a `managed_spell_mode` is given) appends one last part,\n"
    "              `managed:<mode>:<limit>:<timeout>:<reset names>` (`_managed_fingerprint_part`).\n"
    "              Callers pass normalized values (`_normalize_managed_options`). Without a mode\n"
    "              nothing is appended, so every other binding hashes exactly as before (S2,\n"
    "              2026-10-15).\n",
    "            - Never hashes a managed binding's settings (mode, limit, queue timeout, reset\n"
    "              names): they are settings of the one spell, not its identity (owner ruling\n"
    "              2026-10-17: \"the bind call itself shouldn't impact the actual SHA256\"), so a\n"
    "              managed binding hashes exactly the inputs above. From 0.2.8242 to 0.2.8253 a\n"
    "              managed binding appended a `managed:<mode>:<limit>:<timeout>:<reset names>`\n"
    "              part; every managed spell_id moved once when it left (0.2.8254), and no other\n"
    "              spell_id ever had it.\n")
sub(BIND,
    "        parts.extend(tuple(disposal_method_names))\n"
    "\n"
    "        # Managed bindings only: one part carrying the normalized options closes the key.\n"
    "        if managed_spell_mode is not None:\n"
    "            parts.append(\n"
    "                Bind._managed_fingerprint_part(\n"
    "                    managed_spell_mode,\n"
    "                    managed_spell_limit,\n"
    "                    managed_spell_timeout_seconds,\n"
    "                    managed_spell_reset_methods,\n"
    "                )\n"
    "            )\n"
    "\n"
    "        key = \"::\".join(parts)\n",
    "        parts.extend(tuple(disposal_method_names))\n"
    "\n"
    "        key = \"::\".join(parts)\n")
p = load(BIND)
text = writes[p]
start = text.index("    @staticmethod\n    def _managed_fingerprint_part(\n")
end = text.index("    @staticmethod\n    def _normalize_managed_options(\n")
removed = text[start:end]
assert removed.count("def ") == 1 and "managed:{0}:{1}:{2}:{3}" in removed, removed[:200]
writes[p] = text[:start] + text[end:]
assert "_managed_fingerprint_part" not in writes[p]

# --- managed_spell_quantity.py ---------------------------------------------------------------------------------------
sub(POOL,
    "        - Built only by `Creations.ensure_managed_quantity(spell)`: one pool per (root store, managed version).\n",
    "        - Built only by `Creations.ensure_managed_quantity(spell)`: one pool per (root store, managed version).\n"
    "        - A managed spell's settings are not part of its spell_id (owner ruling 2026-10-17), so a definition bound\n"
    "          again under the spell_id with another mode, limit, timeout or reset names meets this pool, which takes\n"
    "          the new settings and keeps every object alive and counted (`_rebind_spell`).\n")
sub(POOL,
    "        - Descriptive fields copied from the Spell at construction: spell id, name, binding name, frame, mode,\n"
    "          limit, timeout, reset names; the Spell's disposal list (borrowed, by reference); the owner root's id.\n",
    "        - Fields copied from the Spell at construction: spell id, name, binding name, frame; the policy - mode,\n"
    "          limit, timeout, reset names - which a rebind under the same spell_id replaces with the new Spell's\n"
    "          settings (`_rebind_spell`); the Spell's disposal list (borrowed, by reference); the owner root's id.\n")
sub(POOL,
    "            The current Spell object of the spell_id: a rebind that meets this pool under the same id re-points\n"
    "            it (`Creations.ensure_managed_quantity`). It may be cleaned by its Book while the pool lives on.\n",
    "            The current Spell object of the spell_id: a rebind that meets this pool under the same id re-points\n"
    "            it and gives the pool its settings (`Creations.ensure_managed_quantity`). It may be cleaned by its\n"
    "            Book while the pool lives on.\n")
p = load(POOL)
text = writes[p]
start = text.index("    def _rebind_spell(self, spell: Spell) -> None:\n")
end = text.index("    def _torn_down_error(self, consequence: str) -> RuntimeError:\n")
old_method = text[start:end]
assert "hence the same options" in old_method and old_method.count("def ") == 1
new_method = '''    def _rebind_spell(self, spell: Spell) -> None:
        """
        Point the pool at the current Spell object of its spell_id and take that Spell's settings.

        Purpose:
            A definition removed and bound again under the same content-stable id meets its old pool (as a slotted
            replacement meets its old slot, 0.2.8219). Its managed settings are not part of the spell_id (owner
            ruling 2026-10-17: the bind call's settings must not change the SHA256), so the rebind may carry another
            mode, limit, queue timeout or reset names; the pool then describes, resolves releases against and leases
            under the live Spell and its settings rather than the cleaned one's.

        Contract:
            - Called only by `Creations.ensure_managed_quantity`, after it released the store lock, for a Spell
              with this pool's spell_id - hence the same class profile, address, existence and disposal names.
            - Always re-points `_spell`, `_managed_class` and `_disposal_method_names` (the new Spell's list, equal
              in content). The class key is re-captured because a redefined class is a new class object under the
              same content-stable id; the store re-registers the pool under it.
            - Equal settings: nothing else changes - the elastic target, the decay clock and the count stay as they
              were (an ownership transfer's restamp of the same Spell is such a rebind).
            - Other settings: the mode, limit, timeout, reset names and `_notify_on_return` take the Spell's values,
              and the retention sizes follow them exactly as `__init__` sizes them (elastic: baseline
              min(20, limit), ceiling limit; limited_quantity and queue: baseline = ceiling = limit); the target
              restarts at the new baseline and the decay step is recomputed from it. Every queue waiter is woken to
              re-check under the new policy.
            - Destroys nothing: objects alive stay alive and counted, idle ones included. A count above a smaller
              new limit stays until destroys bring it down - limited_quantity and queue build again only below the
              limit, and their fixed capacity evicts the oldest idle object on each release above it; elastic
              trims through its band.
            - A pool torn down meanwhile (its store cleaned after `ensure_managed_quantity` checked it) is left as
              it is.

        Args:
            spell: The current Spell of this spell_id.

        Threading:
            Reads the Spell's settings before taking `_lock` (the caller holds the Spell's lock, as owner stamping
            does), then writes under `_condition`, the pool's leaf lock; no user code runs under it and no store
            lock is held. A lease or a release racing the rebind sees the old or the new policy for that one call:
            `reserve()` reads the mode once before its lock and checks the limit in force under it, `put_back`
            reads the reset names once, and a plan's lock-free idle pop serves an object built for this spell_id
            under either policy.

        Returns:
            None.
        """
        mode = spell.managed_spell_mode
        limit = spell.managed_spell_limit
        timeout_seconds = spell.managed_spell_timeout_seconds
        reset_method_names = spell.managed_spell_reset_methods
        condition = self._condition
        with condition:
            if self._cleaned:
                return
            self._spell = spell
            self._managed_class = spell.spell
            self._disposal_method_names = spell.disposal_method_names
            if (
                    mode is self._mode
                    and limit == self._limit
                    and timeout_seconds == self._timeout_seconds
                    and reset_method_names == self._reset_method_names
            ):
                return
            baseline_idle = min(self._ELASTIC_BASELINE_IDLE, limit) if mode is ManagedSpellMode.elastic else limit
            self._mode = mode
            self._limit = limit
            self._timeout_seconds = timeout_seconds
            self._reset_method_names = reset_method_names
            # Only queue leases wait, so only a queue release has a waiter to wake.
            self._notify_on_return = mode is ManagedSpellMode.queue
            self._baseline_idle = baseline_idle
            self._max_idle = limit
            self._target_idle = baseline_idle
            self._decay_step = max(1, (max(baseline_idle, 1) * self._decay_percent_per_interval) // 100)
            condition.notify_all()

'''
writes[p] = text[:start] + new_method + text[end:]

# --- creations.py ------------------------------------------------------------------------------------------------------
sub(STORE,
    "            - Idempotent: one pool per (store, spell id); a second call returns\n"
    "              the same pool. A rebind under the same content-stable id meets the\n"
    "              pool its earlier definition left (as a slotted replacement meets\n"
    "              its slot, 0.2.8219), which is re-pointed at the new Spell object.\n",
    "            - Idempotent: one pool per (store, spell id); a second call returns\n"
    "              the same pool. A rebind under the same content-stable id meets the\n"
    "              pool its earlier definition left (as a slotted replacement meets\n"
    "              its slot, 0.2.8219), which takes the new Spell object and its\n"
    "              settings (`ManagedSpellQuantity._rebind_spell`): a managed spell's\n"
    "              settings are not part of its spell_id (0.2.8254), so a rebind with\n"
    "              another mode, limit, timeout or reset names keeps the pool, its\n"
    "              objects and its count.\n")
sub(STORE,
    "            The map read and write run under the store lock, a leaf; composing a\n"
    "            pool runs no user code. Called under the Spell's lock by owner\n"
    "            stamping, the established build-lock-then-store-lock order. The pool\n"
    "            is registered with `ReleaseManagedSpell` after this lock is released\n"
    "            (its own lock is a leaf held only to publish), so the order is Spell\n"
    "            lock -> registry lock and the store lock stays a leaf.\n",
    "            The map read and write run under the store lock, a leaf; composing a\n"
    "            pool runs no user code. Called under the Spell's lock by owner\n"
    "            stamping, the established build-lock-then-store-lock order. A rebind\n"
    "            runs after this lock is released, because it takes the pool's lock\n"
    "            (a leaf held only for field writes and a notify); the pool is then\n"
    "            registered with `ReleaseManagedSpell` (its own lock is a leaf held\n"
    "            only to publish). So the orders are Spell lock -> store lock, Spell\n"
    "            lock -> pool lock and Spell lock -> registry lock, and the store lock\n"
    "            stays a leaf.\n")
sub(STORE,
    "            pool = self._managed_quantities.get(spell_id)\n"
    "            if pool is None:\n"
    "                pool = ManagedSpellQuantity(spell=spell, owner_conduit_id=self._owner_conduit_id)\n"
    "                self._managed_quantities[spell_id] = pool\n"
    "            else:\n"
    "                pool._rebind_spell(spell)\n"
    "            owner_conduit_id = self._owner_conduit_id\n"
    "        ReleaseManagedSpell().register(pool, root_conduit_id=owner_conduit_id)\n",
    "            pool = self._managed_quantities.get(spell_id)\n"
    "            rebind = pool is not None\n"
    "            if pool is None:\n"
    "                pool = ManagedSpellQuantity(spell=spell, owner_conduit_id=self._owner_conduit_id)\n"
    "                self._managed_quantities[spell_id] = pool\n"
    "            owner_conduit_id = self._owner_conduit_id\n"
    "        if rebind:\n"
    "            # Outside the store lock: the rebind takes the pool's lock, and the store lock stays a leaf.\n"
    "            pool._rebind_spell(spell)\n"
    "        ReleaseManagedSpell().register(pool, root_conduit_id=owner_conduit_id)\n")

# --- caching_system.py -----------------------------------------------------------------------------------------------
sub(CACHE,
    "    # bump is the explicit retirement the owner asked for whenever codegen\n"
    "    # changes (2026-10-16, landed with 0.2.8248).\n",
    "    # bump is the explicit retirement the owner asked for whenever codegen\n"
    "    # changes (2026-10-16, landed with 0.2.8248).\n"
    "    # Version 22 retires bundles written while a managed spell's settings were\n"
    "    # part of its spell_id (0.2.8242-0.2.8253): the settings left the\n"
    "    # fingerprint (0.2.8254, owner ruling 2026-10-17), so every managed spell\n"
    "    # has a new spell_id and the ids those bundles were keyed by are gone. A\n"
    "    # release change already cold-starts every bundle (version 9); the bump\n"
    "    # records why, as the owner asked (\"you gotta notch the version for the\n"
    "    # cache because this is a bug\").\n")
sub(CACHE,
    "        21: \"managed_spell_lease_codegen\",\n"
    "    })\n",
    "        21: \"managed_spell_lease_codegen\",\n"
    "        22: \"managed_settings_leave_spell_id\",\n"
    "    })\n")

# --- managed_spell_mode.py and spell_crystal.py docstrings ----------------------------------------------------------
sub(MODE,
    "        The mode is identity data: it is hashed into the spell id of a managed binding (with the limit, the\n"
    "        timeout and the reset names), recorded by the crystallizer and replayed by restore and graft, so two\n"
    "        bindings of one class that differ only in their mode are two spell versions.\n",
    "        The mode is a setting of the spell, not identity data: it is not part of the spell id (nor are the\n"
    "        limit, the timeout and the reset names; owner ruling 2026-10-17, 0.2.8254), so one class bound managed\n"
    "        at one address is one spell whatever its mode. It is recorded by the crystallizer and replayed by\n"
    "        restore and graft. To change it, `cleanup_spell` the spell and bind it again: the spell keeps its spell\n"
    "        id and its pool takes the new settings.\n")
sub(CRYSTAL,
    "            The one reader of the four managed keys for the restore and graft lanes, so each\n"
    "            replayed bind passes a managed version's own options and gets its own spell id back.\n",
    "            The one reader of the four managed keys for the restore and graft lanes, so each\n"
    "            replayed bind passes a managed version's own settings. The settings are not part of\n"
    "            the spell id (0.2.8254), so the replayed bind's spell id is the one its class,\n"
    "            address, existence and disposal names give.\n")

for p, text in writes.items():
    before = set(p.read_text(encoding="utf-8").splitlines())
    long = [line for line in text.splitlines() if line not in before and len(line) > 120]
    assert not long, (p, long[:3])
    if not DRY:
        p.write_text(text, encoding="utf-8")
    print(("checked " if DRY else "wrote ") + str(p))
