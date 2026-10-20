"""Validate saved execution reports and assemble the final evidence receipt after qualification ends."""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET


def read_report(path: Path) -> dict:
    """Count executed test cases and their explicit failure, error and skip outcomes."""
    cases = ET.parse(path).findall('.//testcase')
    return {
        'cases': len(cases),
        'failures': sum(case.find('failure') is not None for case in cases),
        'errors': sum(case.find('error') is not None for case in cases),
        'skipped_including_xfail': sum(case.find('skipped') is not None for case in cases),
    }


def main() -> None:
    """Require successful driver completion and matching XML/stdout totals before publishing a receipt."""
    evidence = Path('C:/Users/Mark/PycharmProjects/melder_private/context_compass/artifacts/frame_link_cleanup_guard_20261019')
    exit_receipt = json.loads((evidence / 'full_runtime_exit.json').read_text(encoding='utf-8-sig'))
    assert exit_receipt['exit_code'] == 0
    document_receipt = json.loads((evidence / 'documentation_verification.json').read_text(encoding='utf-8'))
    assert document_receipt['mode'] == 'check', 'Recheck the qualified inputs before acceptance'
    reports = {}
    expected_cases = {'focused': 7, 'adjacent': 25, 'repeat_gil0': 200, 'repeat_gil1': 200, 'python3142': 7}
    for label, expected in expected_cases.items():
        result = read_report(evidence / (label + '.xml'))
        assert result == {'cases': expected, 'failures': 0, 'errors': 0, 'skipped_including_xfail': 0}
        reports[label] = result
    for guard in ('inner', 'outer'):
        result = read_report(evidence / f'mutant_{guard}.xml')
        assert result == {'cases': 1, 'failures': 1, 'errors': 0, 'skipped_including_xfail': 0}
        result['disposition'] = 'expected main-thread rejection of removed guard'
        reports['mutant_' + guard] = result
    full = read_report(evidence / 'full_runtime.xml')
    assert full['cases'] >= 14000 and full['failures'] == 0 and full['errors'] == 0
    cases = ET.parse(evidence / 'full_runtime.xml').findall('.//testcase')
    target = [case for case in cases if case.attrib['name'] == 'test_frame_link_cleanup_rechecks_cleaned_inside_lock']
    assert len(target) == 1 and len(target[0]) == 0
    log = (evidence / 'full_runtime.log').read_text(encoding='utf-8')
    summary = next(line for line in reversed(log.splitlines()) if re.match(r'^\d+ passed', line))
    counts = {name: int(count) for count, name in re.findall(r'(\d+) (passed|skipped|xfailed|xpassed)', summary)}
    assert full['cases'] == sum(counts.values())
    assert full['skipped_including_xfail'] == counts.get('skipped', 0) + counts.get('xfailed', 0)
    assert 'PytestUnhandledThreadExceptionWarning' not in log
    reports['full_runtime'] = full
    receipt = {
        'verified_at': datetime.now(timezone.utc).isoformat(),
        'author_and_self_reviewer': 'expert_1 (synaptic_python_developer)',
        'independent_review': False, 'production_changes': False,
        'qualified_inputs': json.loads((evidence / 'qualification_inputs.json').read_text(encoding='utf-8')),
        'reports': reports, 'full_runtime_summary': summary, 'driver_exit_code': 0,
        'repaired_case_executed_in_full_suite': True, 'unhandled_thread_warning_in_full_suite': False,
        'coroutine_shutdown_warning_present': "coroutine 'coro' was never awaited" in log,
        'limits': ['Local Windows Python 3.14.7 GIL-off qualification; hosted Windows Python 3.14.3 not rerun',
                   'Coverage not measured', 'Author self-review; no independent reviewer'],
    }
    (evidence / 'verification_receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(summary)
    print('OK: repaired case executed, no unhandled-thread warning, and XML/driver/stdout outcomes agree')


if __name__ == '__main__':
    main()
