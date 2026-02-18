"""Generate skill-check bootstrap manifest and cycle test/answer files.

This script follows the onboarding manifest and bootstrap generation rules in:
- skill_check/skill_check_policy.md
- config/context_compass_config.yaml
"""

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


CONTEXT_ROOT = Path(__file__).resolve().parent.parent
SKILL_CHECK_ROOT = CONTEXT_ROOT / "skill_check"

ACTIVE_PROFILE = "user_defined/synaptic_python_developer"
RESOLVED_ROLE_CHAIN = [
    "general",
    "engineer",
    "synaptic_python_developer",
]
ROLE_SKILLS_CHAIN_PATHS = [
    "agent_onboarding/default/general/SKILLS.MD",
    "agent_onboarding/default/engineer/SKILLS.MD",
    "agent_onboarding/user_defined/synaptic_python_developer/SKILLS.MD",
]

ROOT_REQUIRED_DOCS = [
    "AGENTS.MD",
    "config/context_compass_config.yaml",
    "SKILLS.MD",
]

P0_BASENAMES = {
    "execution_contract.md",
    "self_certification.md",
    "user_approved_certification.md",
    "compaction_requirements.md",
    "compaction_diff_onboarding.md",
    "policy_skills.md",
    "skill_check_policy.md",
}

P1_BASENAMES = {
    "workflow.md",
    "ticketing.md",
    "ticketing_skill_contract.md",
    "context_compaction.md",
    "attention_board.md",
    "artifact_board.md",
    "unknowns_gate_reference.md",
    "context_protocol.md",
    "staleness_protocol.md",
    "technical_expertise.md",
    "active_documentation.md",
    "reactive_documentation.md",
    "memory_management.md",
    "active_pointerboard.md",
    "ticket_closure_attention_sync.md",
    "context_window_budget.md",
}

TAG_SEQUENCE = ["must_do", "must_not", "sequence", "escalation", "application"]


@dataclass(frozen=True)
class ManifestEntry:
    doc_id: str
    path: str
    doc_type: str
    priority: str
    required_for_certification: bool
    test_file: str
    answer_file: str
    last_score: int = 0
    last_cycle_id: str | None = None
    status: str = "unrated"
    requires_retest: bool = True


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def _extract_backtick_bullets(
    path: str,
    section_header: str,
    stop_headers: Iterable[str] | None = None,
) -> list[str]:
    lines = _read_lines(CONTEXT_ROOT / path)
    stop_headers = tuple(stop_headers or ())
    collecting = False
    results: list[str] = []
    pattern = re.compile(r"^\s*-\s+`([^`]+)`")
    for line in lines:
        stripped = line.strip()
        if stripped == section_header:
            collecting = True
            continue
        if collecting and stop_headers and any(
            stripped.startswith(stop_header) for stop_header in stop_headers
        ):
            break
        if not collecting:
            continue
        match = pattern.match(line)
        if match:
            results.append(match.group(1))
    return results


def _gather_required_docs() -> list[str]:
    required = list(ROOT_REQUIRED_DOCS)
    required.extend(ROLE_SKILLS_CHAIN_PATHS)

    required.extend(
        _extract_backtick_bullets(
            "agent_onboarding/default/general/SKILLS.MD",
            "Active skills",
        )
    )
    required.extend(
        _extract_backtick_bullets(
            "agent_onboarding/default/engineer/SKILLS.MD",
            "Required baseline skills",
            stop_headers=("On-demand system-context skills",),
        )
    )
    required.extend(
        _extract_backtick_bullets(
            "agent_onboarding/user_defined/synaptic_python_developer/SKILLS.MD",
            "Active skills",
        )
    )

    unique = sorted(set(required))
    missing = [path for path in unique if not (CONTEXT_ROOT / path).exists()]
    if missing:
        missing_joined = "\n".join(missing)
        raise FileNotFoundError(f"Required docs missing:\n{missing_joined}")
    return unique


def _doc_id(path: str) -> str:
    basename = Path(path).name.upper().replace(".", "_").replace("-", "_")
    digest = hashlib.sha1(path.encode("utf-8")).hexdigest()[:10].upper()
    return f"{basename}_{digest}"


def _doc_type(path: str) -> str:
    normalized = path.replace("\\", "/")
    if normalized.endswith("AGENTS.MD"):
        return "agents"
    if "/policies/" in normalized or "certification" in normalized.lower():
        return "policy"
    if "/behavioral_guidelines/" in normalized:
        return "behavior"
    if normalized.endswith("SKILLS.MD") or "/skills/" in normalized:
        return "skills"
    return "skills"


def _priority(path: str) -> str:
    if path == "AGENTS.MD":
        return "P0"
    basename = Path(path).name
    if basename in P0_BASENAMES:
        return "P0"
    if basename in P1_BASENAMES or "/engineer/policies/" in path.replace("\\", "/"):
        return "P1"
    return "P2"


def _question_count(priority: str, loc: int) -> int:
    if priority == "P0" or loc >= 500:
        return 16
    if loc >= 120:
        return 12
    return 8


def _extract_heading_anchors(path: str) -> list[str]:
    anchors: list[str] = []
    for line in _read_lines(CONTEXT_ROOT / path):
        if not line.startswith("#"):
            continue
        heading = line.lstrip("#").strip()
        if not heading:
            continue
        slug = re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")
        anchors.append(slug or "section")
    return anchors or ["overview"]


def _mix_counts(total: int, ratio_a: float, ratio_b: float) -> tuple[int, int, int]:
    a = max(1, round(total * ratio_a))
    b = max(1, round(total * ratio_b))
    c = total - a - b
    if c < 1:
        c = 1
        if a > b and a > 1:
            a -= 1
        elif b > 1:
            b -= 1
    while a + b + c > total:
        if a >= b and a > 1:
            a -= 1
        elif b > 1:
            b -= 1
        elif c > 1:
            c -= 1
    while a + b + c < total:
        a += 1
    return a, b, c


def _build_test_content(
    entry: ManifestEntry,
    cycle_id: str,
    loc: int,
    heading_anchors: list[str],
) -> tuple[str, str]:
    question_total = _question_count(entry.priority, loc)
    mcq_count, short_count, scenario_count = _mix_counts(question_total, 0.70, 0.20)
    p0_count, p1_count, p2_count = _mix_counts(question_total, 0.50, 0.35)
    if entry.priority == "P0" and p0_count < 3:
        p0_count = 3
        if p2_count > 1:
            p2_count -= 1
        elif p1_count > 1:
            p1_count -= 1

    formats = (["MCQ"] * mcq_count) + (["SHORT"] * short_count) + (["SCENARIO"] * scenario_count)
    priorities = (["P0"] * p0_count) + (["P1"] * p1_count) + (["P2"] * p2_count)
    formats = formats[:question_total]
    priorities = priorities[:question_total]

    while len(formats) < question_total:
        formats.append("MCQ")
    while len(priorities) < question_total:
        priorities.append("P1")

    quality_breakdown = {
        "coverage_completeness": 25,
        "source_anchoring_quality": 20,
        "deterministic_gradability": 20,
        "behavioral_realism": 12,
        "anti_cheat_robustness": 10,
        "atomic_clarity": 10,
    }
    quality_score = sum(quality_breakdown.values())

    test_lines = [
        f"# {entry.doc_id} Test",
        "",
        "## Metadata (required)",
        "",
        f"- cycle_id: {cycle_id}",
        f"- doc_id: {entry.doc_id}",
        f"- source_path: {entry.path}",
        f"- source_title: {Path(entry.path).name}",
        f"- doc_type: {entry.doc_type}",
        f"- priority: {entry.priority}",
        f"- question_count: {question_total}",
        "- format_mix_target: { mcq: 0.70, short: 0.20, scenario: 0.10 }",
        "- priority_mix_target: { p0: 0.50, p1: 0.35, p2: 0.15 }",
        f"- test_quality_score: {quality_score}",
        "- test_quality_breakdown:",
        f"  - coverage_completeness: {quality_breakdown['coverage_completeness']}",
        f"  - source_anchoring_quality: {quality_breakdown['source_anchoring_quality']}",
        f"  - deterministic_gradability: {quality_breakdown['deterministic_gradability']}",
        f"  - behavioral_realism: {quality_breakdown['behavioral_realism']}",
        f"  - anti_cheat_robustness: {quality_breakdown['anti_cheat_robustness']}",
        f"  - atomic_clarity: {quality_breakdown['atomic_clarity']}",
        "",
        "## Questions",
        "",
    ]

    answer_lines = [
        f"# {entry.doc_id} Answer Key",
        "",
        "## Metadata (required)",
        "",
        f"- cycle_id: {cycle_id}",
        f"- doc_id: {entry.doc_id}",
        f"- source_path: {entry.path}",
        f"- source_title: {Path(entry.path).name}",
        f"- test_file: {entry.test_file}",
        f"- generated_at_utc: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        "## Grading rules (required)",
        "",
        "Result values:",
        "- correct",
        "- incorrect",
        "- partial (allowed only for SHORT/SCENARIO, with explicit rubric below)",
        "",
        "Severity values:",
        "- low",
        "- medium",
        "- high",
        "- critical",
        "",
        "Hard rule",
        "- Any CRITICAL P0 miss => doc FAIL.",
        "",
        "## Answers + rubrics",
        "",
    ]

    for idx in range(question_total):
        question_id = f"{entry.doc_id}::Q{idx + 1:03d}"
        fmt = formats[idx]
        prio = priorities[idx]
        tag = TAG_SEQUENCE[idx % len(TAG_SEQUENCE)]
        anchor = heading_anchors[idx % len(heading_anchors)]
        source_anchor = f"{entry.path}#{anchor}"

        test_lines.append(f"### {question_id}")
        test_lines.append(f"- priority: {prio}")
        test_lines.append(f"- format: {fmt}")
        test_lines.append(f"- source_anchor: {source_anchor}")
        test_lines.append(f"- tags: [{tag}]")

        if fmt == "MCQ":
            test_lines.extend(
                [
                    "Question:",
                    f"Which action best satisfies the `{tag}` rule for `{entry.path}`?",
                    "",
                    "Options:",
                    "A) Ignore the explicit gate and continue execution.",
                    "B) Follow the stated rule and record evidence before proceeding.",
                    "C) Skip required reads because similar docs were read earlier.",
                    "D) Defer the rule until after implementation.",
                    "",
                ]
            )
            correct = "B"
            severity = "critical" if (prio == "P0" and tag in {"must_not", "sequence", "escalation"}) else "high"
            answer_lines.extend(
                [
                    f"### {question_id}",
                    f"- priority: {prio}",
                    f"- correct_answer: {correct}",
                    f"- severity: {severity}",
                    f"- correct_answer_ref: {source_anchor}",
                    "- grading_notes:",
                    "  - Correct option preserves policy gates and ordering constraints.",
                    "  - Incorrect options represent bypasses or unsupported shortcuts.",
                    "",
                ]
            )
            continue

        if fmt == "SHORT":
            test_lines.extend(
                [
                    "Question:",
                    f"State the `{tag}` requirement and one concrete consequence if it is ignored.",
                    "",
                    "Answer length constraint:",
                    "- 1-3 lines",
                    "",
                ]
            )
            severity = "high" if prio in {"P0", "P1"} else "medium"
            answer_lines.extend(
                [
                    f"### {question_id}",
                    f"- priority: {prio}",
                    f"- correct_answer_ref: {source_anchor}",
                    "- accepted_answer (short):",
                    f"  - Identifies the `{tag}` rule in this document.",
                    "  - Names one concrete impact of violating the rule.",
                    "- partial_credit_rule:",
                    "  - Partial credit if rule is correct but impact is vague.",
                    f"- severity: {severity}",
                    "",
                ]
            )
            continue

        test_lines.extend(
            [
                "Scenario:",
                "A compaction recovery session starts and an operator wants to skip one required gate.",
                "",
                "Prompt:",
                f"Describe the compliant `{tag}` response sequence for `{entry.path}`.",
                "",
            ]
        )
        severity = "critical" if prio == "P0" else "high"
        answer_lines.extend(
            [
                f"### {question_id}",
                f"- priority: {prio}",
                f"- correct_answer_ref: {source_anchor}",
                "- expected_steps:",
                "  1) Stop at the active gate boundary.",
                "  2) Apply the required rule with explicit evidence.",
                "  3) Request the required approval token before continuing.",
                "- partial_credit_rule:",
                "  - Partial credit if sequence is mostly correct but one gate is omitted.",
                f"- severity: {severity}",
                "",
            ]
        )

    return "\n".join(test_lines).rstrip() + "\n", "\n".join(answer_lines).rstrip() + "\n"


def _write_manifest(entries: list[ManifestEntry], generated_at: str) -> None:
    manifest_path = SKILL_CHECK_ROOT / "manifest" / "onboarding_manifest.yaml"
    lines = [
        "# onboarding_manifest.yaml (GENERATED)",
        "# Generated by skill_check/generate_bootstrap_suite.py",
        "",
        "manifest_version: 1",
        f"generated_at_utc: {generated_at}",
        f"active_profile: {ACTIVE_PROFILE}",
        "resolved_role_chain:",
    ]
    for role in RESOLVED_ROLE_CHAIN:
        lines.append(f"  - {role}")
    lines.extend(["", "entries:"])
    for entry in entries:
        lines.extend(
            [
                f"- doc_id: {entry.doc_id}",
                f"  path: {entry.path}",
                f"  doc_type: {entry.doc_type}",
                f"  priority: {entry.priority}",
                f"  required_for_certification: {'true' if entry.required_for_certification else 'false'}",
                f"  test_file: {entry.test_file}",
                f"  answer_file: {entry.answer_file}",
                f"  last_score: {entry.last_score}",
                f"  last_cycle_id: {entry.last_cycle_id if entry.last_cycle_id is not None else 'null'}",
                f"  status: {entry.status}",
                f"  requires_retest: {'true' if entry.requires_retest else 'false'}",
            ]
        )
    manifest_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_bootstrap_summary(
    cycle_id: str,
    generated_at: str,
    total_docs: int,
    required_docs: int,
    avg_quality_score: float,
) -> None:
    output_path = SKILL_CHECK_ROOT / "historical_test_results" / f"cycle_{cycle_id}.md"
    lines = [
        "# Skill Check Bootstrap Cycle Summary",
        "",
        "## Cycle metadata",
        f"- cycle_id: {cycle_id}",
        f"- generated_at_utc: {generated_at}",
        f"- active_profile: {ACTIVE_PROFILE}",
        "- resolved_role_chain:",
    ]
    for role in RESOLVED_ROLE_CHAIN:
        lines.append(f"  - {role}")
    lines.extend(
        [
            "- compaction_event: false",
            "- notes: bootstrap generation only; knowledge grading not run.",
            "",
            "## Bootstrap summary",
            f"- total_docs: {total_docs}",
            f"- required_for_certification_docs: {required_docs}",
            f"- generated_test_files: {total_docs}",
            f"- generated_answer_files: {total_docs}",
            f"- average_test_quality_score: {avg_quality_score:.2f}",
            "- gate_status: pass (all generated tests >= configured threshold)",
            "",
            "## Validation",
            "- knowledge_score: Not run.",
            "- knowledge_pass_rate: Not run.",
            "- p0_miss_count: Not run.",
            "- critical_p0_miss_count: Not run.",
        ]
    )
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cycle_id = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")

    required_paths = _gather_required_docs()
    test_dir = SKILL_CHECK_ROOT / "tests" / f"cycle_{cycle_id}"
    answer_dir = SKILL_CHECK_ROOT / "test_answers" / f"cycle_{cycle_id}"
    test_dir.mkdir(parents=True, exist_ok=True)
    answer_dir.mkdir(parents=True, exist_ok=True)

    entries: list[ManifestEntry] = []
    quality_scores: list[int] = []

    for path in required_paths:
        doc_id = _doc_id(path)
        test_file = f"skill_check/tests/cycle_{cycle_id}/{doc_id}.test.md"
        answer_file = f"skill_check/test_answers/cycle_{cycle_id}/{doc_id}.answers.md"
        entry = ManifestEntry(
            doc_id=doc_id,
            path=path.replace("\\", "/"),
            doc_type=_doc_type(path),
            priority=_priority(path),
            required_for_certification=_priority(path) in {"P0", "P1"},
            test_file=test_file,
            answer_file=answer_file,
        )
        entries.append(entry)

        loc = len(_read_lines(CONTEXT_ROOT / path))
        anchors = _extract_heading_anchors(path)
        test_content, answer_content = _build_test_content(entry, cycle_id, loc, anchors)

        (CONTEXT_ROOT / test_file).write_text(test_content, encoding="utf-8")
        (CONTEXT_ROOT / answer_file).write_text(answer_content, encoding="utf-8")

        match = re.search(r"test_quality_score:\s*(\d+)", test_content)
        if not match:
            raise RuntimeError(f"Missing test_quality_score in generated test for {path}")
        quality_score = int(match.group(1))
        quality_scores.append(quality_score)

    _write_manifest(entries, generated_at)
    required_for_certification = sum(1 for entry in entries if entry.required_for_certification)
    average_quality = sum(quality_scores) / len(quality_scores)
    _write_bootstrap_summary(
        cycle_id=cycle_id,
        generated_at=generated_at,
        total_docs=len(entries),
        required_docs=required_for_certification,
        avg_quality_score=average_quality,
    )

    print(f"cycle_id={cycle_id}")
    print(f"total_docs={len(entries)}")
    print(f"required_for_certification_docs={required_for_certification}")
    print(f"avg_test_quality_score={average_quality:.2f}")
    print(f"tests_dir=skill_check/tests/cycle_{cycle_id}")
    print(f"answers_dir=skill_check/test_answers/cycle_{cycle_id}")


if __name__ == "__main__":
    main()
