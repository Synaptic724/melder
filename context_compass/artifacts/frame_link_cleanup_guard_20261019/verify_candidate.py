"""Bind the local runtime qualification to its exact input files and preserved documentation."""
import argparse
import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import re
import subprocess
import sys
import sysconfig
import tomllib


def git(root: Path, *arguments: str) -> bytes:
    """Read Git metadata with optional index locking disabled."""
    return subprocess.run(
        ['C:/Program Files/Git/cmd/git.exe', '--no-optional-locks', *arguments],
        cwd=root, capture_output=True, check=True,
    ).stdout


def input_identity(root: Path) -> dict:
    """Return a path-aware aggregate of tracked runtime/test inputs plus actual interpreter pins."""
    paths = git(
        root, 'ls-files', '-z', '--', 'src', 'tests', '.github', 'pyproject.toml', 'uv.lock',
        'llm_support', 'context_compass/system_docs/tests_components.md',
        'context_compass/system_docs/tests_components_index.md',
    ).decode().strip('\0').split('\0')
    aggregate = hashlib.sha256()
    for name in sorted(paths):
        aggregate.update(name.encode() + b'\0' + hashlib.sha256((root / name).read_bytes()).digest())
    pins = tomllib.loads((root / '.github/python/tests/3.14.7.toml').read_text(encoding='utf-8'))
    reported_pins = tomllib.loads((root / '.github/python/tests/3.14.3.toml').read_text(encoding='utf-8'))
    assert pins['dependencies'] == reported_pins['dependencies']
    dependencies = {}
    for requirement in pins['dependencies']:
        name, expected = requirement.split(';', 1)[0].strip().split('==')
        dependencies[name] = version(name)
        assert dependencies[name] == expected, (name, dependencies[name], expected)
    assert sysconfig.get_config_var('Py_GIL_DISABLED') == 1 and not sys._is_gil_enabled()
    assert git(root, 'diff', '--name-only', '--', 'src').strip() == b'', 'Production source changed'
    test = root / 'tests/unit/melder/aether/test_frame_link_runtime_contracts.py'
    return {
        'base_revision': git(root, 'rev-parse', 'HEAD').decode().strip(),
        'tracked_input_count': len(paths), 'tracked_inputs_sha256': aggregate.hexdigest(),
        'test_sha256': hashlib.sha256(test.read_bytes()).hexdigest(),
        'python': sys.version, 'executable': sys.executable, 'gil_enabled': sys._is_gil_enabled(),
        'dependencies': dependencies,
    }


def document_identity(root: Path, evidence: Path) -> dict:
    """Account for removed lines, verify the original fixture and check the new test-flow citation."""
    before = (evidence / 'before/tests_components.md').read_text(encoding='utf-8')
    document = root / 'context_compass/system_docs/tests_components.md'
    raw = document.read_bytes()
    after = raw.decode('utf-8')
    baseline_lines = Counter(' '.join(line.split()) for line in before.splitlines() if line.strip())
    current_lines = Counter(' '.join(line.split()) for line in after.splitlines() if line.strip())
    removed = baseline_lines - current_lines
    assert removed == Counter({'- Updated: 2026-10-20T00:13:14Z': 1}), removed
    assert b'\r' not in raw
    assert not re.search(r'context_compass/|agent_onboarding/|tools/system_documents/|index_document\.py|system_docs/|patches/active/', after)
    test_name = 'tests/unit/melder/aether/test_frame_link_runtime_contracts.py'
    original = git(root, 'show', f'e6b41f3220082ac604c42839d26bbca21336bf41:{test_name}').decode()
    preserved = (evidence / 'before/test_frame_link_runtime_contracts.py').read_text(encoding='utf-8')
    assert ast.dump(ast.parse(original), include_attributes=False) == ast.dump(ast.parse(preserved), include_attributes=False)
    test_text = (root / test_name).read_text(encoding='utf-8')
    test_loc = len(test_text.splitlines())
    function = next(node for node in ast.parse(test_text).body if isinstance(node, ast.FunctionDef)
                    and node.name == 'test_frame_link_cleanup_rechecks_cleaned_inside_lock')
    assert f'{test_name}:{function.lineno}-{function.end_lineno}' in after
    assert after.count('### Flow: FrameLink Cleanup Guard Stand-In\n') == 1
    return {
        'preserved_prior_claims': True, 'intentional_metadata_replacements': dict(removed),
        'document_sha256': hashlib.sha256(raw).hexdigest(), 'document_loc': len(after.splitlines()),
        'test_loc': test_loc, 'test_citation': f'{function.lineno}-{function.end_lineno}',
        'original_control_matches_base_ast': True, 'line_ending': 'lf',
    }


def main() -> None:
    """Capture before a qualification run, or verify all qualification inputs still match afterward."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('capture', 'check'))
    mode = parser.parse_args().mode
    root = Path('C:/Users/Mark/PycharmProjects/melder_private')
    evidence = root / 'context_compass/artifacts/frame_link_cleanup_guard_20261019'
    inputs = input_identity(root)
    documentation = document_identity(root, evidence)
    target = evidence / 'qualification_inputs.json'
    if mode == 'capture':
        assert not target.exists(), 'Refusing to replace an existing input capture'
        target.write_text(json.dumps(inputs, indent=2) + '\n', encoding='utf-8')
    else:
        assert inputs == json.loads(target.read_text(encoding='utf-8')), 'Qualification inputs changed'
    receipt = {'verified_at': datetime.now(timezone.utc).isoformat(), 'mode': mode, **documentation}
    (evidence / 'documentation_verification.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(f'OK {mode}: {inputs["tracked_input_count"]} input hashes, original fixture and document preservation verified')


if __name__ == '__main__':
    main()
