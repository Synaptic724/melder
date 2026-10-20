"""
Apply the elastic-retention fix to a copy of the tree (TASK-2026-10-12-make_kernel_pools_elastic).

Usage: python apply_elastic.py <tree root> <new abstract_elastic_pool.py (LF)>
Edits are line-anchored and keep each file's existing line endings, including the LF-only runs
inside spell_space_pool.py; every anchor must match exactly once.
"""
import pathlib
import sys


def load(path: pathlib.Path) -> list:
    return path.read_bytes().decode("utf-8").splitlines(keepends=True)


def ending_of(line: str) -> str:
    return "\r\n" if line.endswith("\r\n") else "\n"


def replace_block(lines: list, old: list, new: list) -> list:
    """Replace the consecutive lines `old` (compared without endings) by `new`, using the first old line's ending."""
    stripped = [line.rstrip("\r\n") for line in lines]
    hits = [i for i in range(len(lines) - len(old) + 1) if stripped[i:i + len(old)] == old]
    assert len(hits) == 1, (old[0], hits)
    start = hits[0]
    eol = ending_of(lines[start])
    return lines[:start] + [text + eol for text in new] + lines[start + len(old):]


def main() -> int:
    tree = pathlib.Path(sys.argv[1])
    new_pool = pathlib.Path(sys.argv[2]).read_text(encoding="utf-8")

    # 1. AbstractElasticPool: whole module, CRLF like the original.
    pool_path = tree / "src/melder/utilities/general_base/abstract_elastic_pool.py"
    assert b"\r\n" in pool_path.read_bytes()
    pool_path.write_bytes(new_pool.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8"))

    # 2. SpellSpacePool.
    path = tree / "src/melder/aether/conduit/spell_space/spell_space_pool.py"
    lines = load(path)
    lines = replace_block(lines, [
        "            - Clears a reused space's released flag: the lease starts here. A new",
        "              space starts unreleased.",
        '        """',
        "        try:",
        "            space = self._idle.pop()",
        "        except IndexError:",
        "            return self.create_object(*args, **kwargs)",
    ], [
        "            - Clears a reused space's released flag: the lease starts here. A new",
        "              space starts unreleased.",
        "            - A miss records pressure for the elastic retention target",
        "              (`_note_miss`), after the new space is built.",
        '        """',
        "        try:",
        "            space = self._idle.pop()",
        "        except IndexError:",
        "            space = self.create_object(*args, **kwargs)",
        "            self._note_miss()",
        "            return space",
    ])
    lines = replace_block(lines, [
        "        Acquire one spellspace with conduit-local fixed-capacity fast-path rules.",
        "",
        "        Purpose:",
        "            SpellSpace pools are created with fixed `baseline_idle == max_idle`,",
        "            so the generic elastic-pool synchronization work does not add value",
        "            on the hot path. This override keeps the same external acquire",
        "            contract while making the direct deque pop the first operation.",
    ], [
        "        Acquire one spellspace through the conduit-local fast path.",
        "",
        "        Purpose:",
        "            Keep the base acquire contract while making the direct deque pop",
        "            the first operation and skipping the base's advisory in-use",
        "            counter. (Through 0.2.8233 this said the pools were built with a",
        "            fixed `baseline_idle == max_idle`; their retention is elastic now.)",
    ])
    lines = replace_block(lines, [
        "            - Uses one direct deque pop miss path instead of pre-checking idle",
        "              state under an outer Python lock.",
        '        """',
        "        try:",
        "            pooled_space = self._idle.pop()",
        "        except IndexError:",
        "            pooled_space = self.create_object(*args, **kwargs)",
    ], [
        "            - Uses one direct deque pop miss path instead of pre-checking idle",
        "              state under an outer Python lock.",
        "            - A miss records pressure for the elastic retention target",
        "              (`_note_miss`), after the new space is built.",
        '        """',
        "        try:",
        "            pooled_space = self._idle.pop()",
        "        except IndexError:",
        "            pooled_space = self.create_object(*args, **kwargs)",
        "            self._note_miss()",
    ])
    lines = replace_block(lines, [
        "            - Uses a conduit-local fixed-capacity fast path.",
    ], [
        "            - Uses the conduit-local fast path: when at most `baseline_idle`",
        "              spellspaces are idle after the append, the return ends there.",
    ])
    lines = replace_block(lines, [
        "            - Retains returned spellspaces while idle capacity remains at or",
        "              below the current target.",
        "            - Evicts one cold idle spellspace with `popleft()` when retained",
        "              capacity is exceeded.",
    ], [
        "            - Above `baseline_idle`, `_rebalance_after_return()` keeps it while",
        "              the idle set is within the elastic target, stretches the target",
        "              under recent pressure, applies a due decay step, and destroys",
        "              the oldest surplus spellspaces (through 0.2.8233: one overflow",
        "              eviction against a target fixed at 20).",
    ])
    lines = replace_block(lines, [
        "        # Hot path (one release per managed scope): one read of the idle deque",
        "        # serves the append, the capacity check and the overflow eviction.",
        "        idle = self._idle",
        "        idle.append(obj)",
        "        if len(idle) <= self._target_idle:",
        "            return",
        "        try:",
        "            overflow_space = idle.popleft()",
        "        except IndexError:",
        "            return",
        "        self.destroy_object(overflow_space)",
    ], [
        "        # Hot path (one release per managed scope): one read of the idle deque",
        "        # serves the append and the baseline check; only a return into the",
        "        # elastic band (more than `baseline_idle` idle) reads the clock.",
        "        idle = self._idle",
        "        idle.append(obj)",
        "        if len(idle) <= self._baseline_idle:",
        "            return",
        "        self._rebalance_after_return()",
    ])
    path.write_bytes("".join(lines).encode("utf-8"))

    # 3. ConduitPool.
    path = tree / "src/melder/aether/conduit/conduit_pool.py"
    lines = load(path)
    lines = replace_block(lines, [
        "        Pooling lesser conduits per root exists so repeated sub-conduit creation",
        "        inside one root does not churn allocation - the same deque-first",
        "        fixed-capacity policy the SpellSpace pool uses. Scoping the pool to the",
    ], [
        "        Pooling lesser conduits per root exists so repeated sub-conduit creation",
        "        inside one root does not churn allocation - the same deque-first",
        "        elastic retention the SpellSpace pool uses: keep what demand needed, up",
        "        to `max_idle`, and decay toward `baseline_idle` once it is quiet",
        "        (through 0.2.8233 the target stayed fixed at 20). Scoping the pool to the",
    ])
    lines = replace_block(lines, [
        "            - Uses one direct deque pop miss path instead of pre-checking idle",
        "              state under an outer Python lock.",
        '        """',
        "        try:",
        "            return self._idle.pop()",
        "        except IndexError:",
        "            return None",
    ], [
        "            - Uses one direct deque pop miss path instead of pre-checking idle",
        "              state under an outer Python lock.",
        "            - A miss records pressure for the elastic retention target",
        "              (`_note_miss`) before the caller builds the new lesser.",
        '        """',
        "        try:",
        "            return self._idle.pop()",
        "        except IndexError:",
        "            self._note_miss()",
        "            return None",
    ])
    lines = replace_block(lines, [
        "            - Appends the returned conduit first.",
        "            - Retains the conduit while idle capacity remains at or below the",
        "              current target.",
        "            - Evicts one cold idle conduit with `popleft()` when retained",
        "              capacity is exceeded.",
    ], [
        "            - Appends the returned conduit first; when at most `baseline_idle`",
        "              lessers are idle, the return ends there.",
        "            - Above `baseline_idle`, `_rebalance_after_return()` keeps it while",
        "              the idle set is within the elastic target, stretches the target",
        "              under recent pressure, applies a due decay step, and destroys",
        "              the oldest surplus lessers (through 0.2.8233: one overflow eviction",
        "              against a target fixed at 20).",
    ])
    lines = replace_block(lines, [
        "        self._idle.append(conduit)",
        "        if len(self._idle) <= self._target_idle:",
        "            return",
        "        try:",
        "            overflow_conduit = self._idle.popleft()",
        "        except IndexError:",
        "            return",
        "        self.destroy_object(overflow_conduit)",
    ], [
        "        idle = self._idle",
        "        idle.append(conduit)",
        "        if len(idle) <= self._baseline_idle:",
        "            return",
        "        self._rebalance_after_return()",
    ])
    path.write_bytes("".join(lines).encode("utf-8"))

    # 4. Conduit: the pool sizes (baseline 20 kept, ceiling raised).
    path = tree / "src/melder/aether/conduit/conduit.py"
    lines = load(path)
    lines = replace_block(lines, [
        "            spellspace_stack_state=self._spellspace_stack,",
        "            baseline_idle=20,",
        "            max_idle=20,",
        "        )",
        "        if conduit_state is ConduitState.normal:",
        "            self._conduit_pool: ConduitPool = ConduitPool(",
        "                root_conduit=self,",
        "                baseline_idle=20,",
        "                max_idle=20,",
        "            )",
    ], [
        "            spellspace_stack_state=self._spellspace_stack,",
        "            # Elastic retention (0.2.8234): 20 idle shells always kept; under",
        "            # demand the pool keeps up to 256 and decays back when quiet.",
        "            baseline_idle=20,",
        "            max_idle=256,",
        "        )",
        "        if conduit_state is ConduitState.normal:",
        "            self._conduit_pool: ConduitPool = ConduitPool(",
        "                root_conduit=self,",
        "                baseline_idle=20,",
        "                max_idle=256,",
        "            )",
    ])
    lines = replace_block(lines, [
        "                    self._conduit_pool = ConduitPool(root_conduit=self, baseline_idle=20, max_idle=20)",
    ], [
        "                    self._conduit_pool = ConduitPool(root_conduit=self, baseline_idle=20, max_idle=256)",
    ])
    lines = replace_block(lines, [
        "            - Clamped to pool capacity: never builds shells the pool would",
        "              immediately evict and destroy.",
    ], [
        "            - Clamped to pool capacity: never builds shells the pool would",
        "              immediately evict and destroy.",
        "            - Shells above the pool's `baseline_idle` stay idle like any burst",
        "              the pool has seen (the builds count as misses) and decay back",
        "              toward `baseline_idle` once no miss has happened for the pool's",
        "              settle time (0.2.8234; through 0.2.8233 at most 20 were kept).",
    ])
    lines = replace_block(lines, [
        "            - Clamped to pool capacity: ensures at most",
        "              `min(count, pool.max_idle)` idle shells.",
    ], [
        "            - Clamped to pool capacity: ensures at most",
        "              `min(count, pool.max_idle)` idle shells.",
        "            - Shells above the pool's `baseline_idle` stay idle like any burst",
        "              the pool has seen (the builds count as misses) and decay back",
        "              toward `baseline_idle` once no miss has happened for the pool's",
        "              settle time (0.2.8234; through 0.2.8233 at most 20 were kept).",
    ])
    path.write_bytes("".join(lines).encode("utf-8"))
    print("applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
