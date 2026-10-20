"""Re-cut apply_followups.py into apply_0_2_8230.py: items 1-2 unchanged, item 3 as documentation of the raise."""
import pathlib, pprint

src = pathlib.Path("apply_followups.py").read_text()
code = src.replace("ROOT = pathlib.Path(sys.argv[1])", "ROOT = None").replace("def edit(rel, ops):", "def _real_edit(rel, ops):")
collected = []
ns = {"__name__": "collect", "edit": lambda rel, ops: collected.append((rel, list(ops)))}
exec(code, ns)

DROP = (
    'Owning conduit when found, otherwise "None".',
    "return self._aether._get_conduit_by_spell_id(",
    'Matching spell when found, otherwise "None".',
    "Optional[Conduit]: The conduit that registered the spell, or None if not found.",
    "Optional[Spell]: The spell object if found, otherwise None.",
)
kept = []
for rel, ops in collected:
    if rel.endswith("aether/aether.py"):
        continue
    ops = [op for op in ops if not any(marker in op[0] for marker in DROP)]
    if ops:
        kept.append((rel, ops))

SB = "src/melder/aether/spellbook/spellbook.py"
CD = "src/melder/aether/conduit/conduit.py"
ITEM3 = [
    (SB, [
        ("""    ) -> Conduit | None:
        \"\"\"
        Internal

        Resolve the conduit that owns the supplied spell id through Aether.
""", """    ) -> Conduit:
        \"\"\"
        Internal

        Resolve the conduit that owns the supplied spell id through Aether.
""", 1),
        ("""        Returns:
            Optional[Conduit]:
                Owning conduit when found, otherwise "None".
        \"\"\"
        if aetheric_frame_name == "default":
""", """        Returns:
            Conduit:
                The root conduit that owns the spell id.

        Raises:
            ValueError: If no conduit in the frame claims the id - unknown or removed, bound in
                another frame, its owner cleaned, or a lineage between owners while an ownership
                transfer runs - or the frame does not exist (`Aether._get_conduit_by_spell_id`).
                It always raised; until 0.2.8230 this docstring promised None.
        \"\"\"
        if aetheric_frame_name == "default":
""", 1),
        ("""        Returns:
            Optional[Spell]:
                Matching spell when found, otherwise "None".
        \"\"\"
        owner = self._get_conduit_by_spell_id(spell_id, aetheric_frame_name)
""", """        Returns:
            Optional[Spell]:
                The live spell of the lineage holding the id, or None when the owning conduit's
                Spellbook does not resolve it (`Spellbook.find_spell_by_id`).

        Raises:
            ValueError: If no conduit in the frame claims the id, or the frame does not exist
                (`_get_conduit_by_spell_id`).
            RuntimeError: If the owning conduit has no spellbook.
        \"\"\"
        owner = self._get_conduit_by_spell_id(spell_id, aetheric_frame_name)
""", 1),
    ]),
    (CD, [
        ("""    def get_conduit_by_spell_id(self, spell_id: str, aetheric_frame_name: str = "default") -> Optional["Conduit"]:
""", """    def get_conduit_by_spell_id(self, spell_id: str, aetheric_frame_name: str = "default") -> "Conduit":
""", 1),
        ("""        Contract:
            - Resolves through the spellbook's Aether-wide lookup, so it can find a
              conduit in ANOTHER frame - it is not scoped to this conduit's frame
              unless you pass one.
            - Runs under the conduit lock.

        Args:
            spell_id (str): The unique identifier of the spell.
            aetheric_frame_name (str): The aetheric frame to check against. Defaults to "default".

        Returns:
            Optional[Conduit]: The conduit that registered the spell, or None if not found.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        \"\"\"
""", """        Contract:
            - Searches ONE frame: this conduit's Spellbook frame by default ("default"
              means that frame), or the frame you name. An id bound only in another
              frame is not found unless you name that frame.
            - A miss RAISES; it never returns None. The `get_*` lookups raise ValueError on
              a miss and the `find_*` lookups return None (owner decision 2026-10-11; the
              convention of the Aether conduit and frame lookups). Until 0.2.8230 this
              docstring and the annotation promised None, which the method never returned.
            - Runs under the conduit lock.

        Args:
            spell_id (str): The unique identifier of the spell.
            aetheric_frame_name (str): The aetheric frame to check against. Defaults to "default".

        Returns:
            Conduit: The root conduit that owns the spell.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            ValueError: If no conduit in the frame claims the id - unknown or removed, bound in
                another frame, its owner cleaned, or a lineage between owners while an
                ownership transfer runs - or the frame does not exist.
        \"\"\"
""", 1),
        ("""          2) Searches that conduit's spellbook for a SpellIndex whose lineage contains
             this version ID.
          3) Returns the corresponding Spell instance if found.
""", """          2) Resolves the id in that conduit's spellbook (`Spellbook.find_spell_by_id`):
             the live spell of the lineage that contains this version ID.
          3) Returns that Spell instance.
""", 1),
        ("""        Returns:
            Optional[Spell]: The spell object if found, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        \"\"\"
        self.check_cleaned()
        return self._spellbook._get_spell_by_id_via_aether(
""", """        Returns:
            Optional[Spell]: The spell object, or None when the owner's spellbook does not
            resolve the id to a live spell.

        Raises:
            RuntimeError: If the Conduit is cleaned, or the owning conduit has no spellbook.
            ValueError: If no conduit in the frame claims the id - unknown or removed, bound in
                another frame, its owner cleaned, or a lineage between owners while an
                ownership transfer runs - or the frame does not exist. A miss raises, as the
                `get_*` lookups do (owner decision 2026-10-11); until 0.2.8230 this docstring
                promised None.
        \"\"\"
        self.check_cleaned()
        return self._spellbook._get_spell_by_id_via_aether(
""", 1),
    ]),
]

out = ['"""Spell-map race fixes and the id-lookup docs (0.2.8230): exact anchors, each file keeps its EOL. usage: <root>"""',
       "import pathlib, sys", "", "ROOT = pathlib.Path(sys.argv[1])", "", "",
       "def edit(rel, ops):",
       "    path = ROOT / rel",
       "    data = path.read_bytes().decode('utf-8')",
       "    crlf = '\\r\\n' in data",
       "    text = data.replace('\\r\\n', '\\n')",
       "    for anchor, new, count in ops:",
       "        found = text.count(anchor)",
       "        if found != count:",
       "            raise SystemExit(f'{rel}: anchor x{found} (want {count}): {anchor[:80]!r}')",
       "        text = text.replace(anchor, new)",
       "    path.write_bytes((text.replace('\\n', '\\r\\n') if crlf else text).encode('utf-8'))",
       "    print(f\"{rel}: {len(ops)} edits ({'CRLF' if crlf else 'LF'})\")",
       "", ""]
for rel, ops in kept + ITEM3:
    out.append(f"edit({rel!r}, {pprint.pformat(ops, width=120)})")
    out.append("")
pathlib.Path("apply_0_2_8230.py").write_text("\n".join(out) + "\n")
print("kept:", [(r.rsplit('/', 1)[1], len(o)) for r, o in kept])
