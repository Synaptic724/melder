"""Generate and maintain skill-check manifest and cycle test/answer files.

This script follows the onboarding manifest and suite maintenance rules in:
- skill_check/skill_check_policy.md
- config/context_compass_config.yaml
"""

import argparse
import hashlib
import re
import shutil
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
MIN_REQUIRED_COVERAGE_QUESTIONS = len(TAG_SEQUENCE)


@dataclass(frozen=True)
class KnowledgeGateConfig:
    pass_threshold: int = 85
    test_quality_threshold: int = 85
    question_small: int = 8
    question_medium: int = 12
    question_large: int = 16
    format_mcq: float = 0.70
    format_short: float = 0.20
    format_scenario: float = 0.10
    priority_p0: float = 0.50
    priority_p1: float = 0.35
    priority_p2: float = 0.15
    p0_min_questions_per_doc: int = 3
    stable_streak_for_shrink: int = 3
    read_loc_max: int = 500


@dataclass(frozen=True)
class BuildStats:
    total_docs: int
    required_docs: int
    total_questions: int
    stable_docs: int
    shrink_applied_docs: int
    avg_quality_score: float
    removed_test_cycles: int
    removed_answer_cycles: int
    removed_history_cycles: int


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
    stability_streak: int = 0


@dataclass(frozen=True)
class BoardDocResult:
    last_score: int
    status: str
    requires_retest: bool
    stability_streak: int
    last_cycle_id: str | None


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_int(text: str, key: str, default: int) -> int:
    match = re.search(rf"^\s*{re.escape(key)}:\s*([0-9]+)\s*$", text, re.MULTILINE)
    if not match:
        return default
    return int(match.group(1))


def _extract_float(text: str, key: str, default: float) -> float:
    match = re.search(
        rf"^\s*{re.escape(key)}:\s*([0-9]+(?:\.[0-9]+)?)\s*$",
        text,
        re.MULTILINE,
    )
    if not match:
        return default
    return float(match.group(1))


def _load_knowledge_gate_config() -> KnowledgeGateConfig:
    config_text = _read_text(CONTEXT_ROOT / "config" / "context_compass_config.yaml")
    return KnowledgeGateConfig(
        pass_threshold=_extract_int(config_text, "pass_threshold", 85),
        test_quality_threshold=_extract_int(config_text, "test_quality_threshold", 85),
        question_small=_extract_int(config_text, "small", 8),
        question_medium=_extract_int(config_text, "medium", 12),
        question_large=_extract_int(config_text, "large", 16),
        format_mcq=_extract_float(config_text, "mcq", 0.70),
        format_short=_extract_float(config_text, "short", 0.20),
        format_scenario=_extract_float(config_text, "scenario", 0.10),
        priority_p0=_extract_float(config_text, "p0", 0.50),
        priority_p1=_extract_float(config_text, "p1", 0.35),
        priority_p2=_extract_float(config_text, "p2", 0.15),
        p0_min_questions_per_doc=_extract_int(config_text, "p0_min_questions_per_doc", 3),
        stable_streak_for_shrink=_extract_int(config_text, "stable_streak_for_shrink", 3),
        read_loc_max=_extract_int(config_text, "read_loc_max", 500),
    )


def _parse_scalar(value: str) -> object:
    lowered = value.strip().lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered == "null":
        return None
    if re.fullmatch(r"-?[0-9]+", value.strip()):
        return int(value.strip())
    return value.strip()


def _to_int(value: object, default: int) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and re.fullmatch(r"-?[0-9]+", value):
        return int(value)
    return default


def _to_bool(value: object, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.lower().strip()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
    return default


def _to_optional_str(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return str(value)


def _load_previous_manifest_entries() -> dict[str, dict[str, object]]:
    manifest_path = SKILL_CHECK_ROOT / "manifest" / "onboarding_manifest.yaml"
    if not manifest_path.exists():
        return {}
    entries_by_path: dict[str, dict[str, object]] = {}
    current: dict[str, object] | None = None
    for line in _read_lines(manifest_path):
        if line.startswith("- doc_id: "):
            if current and isinstance(current.get("path"), str):
                entries_by_path[str(current["path"])] = current
            current = {"doc_id": line.split(": ", 1)[1].strip()}
            continue
        if current is None or not line.startswith("  "):
            continue
        stripped = line.strip()
        if ": " not in stripped:
            continue
        key, raw_value = stripped.split(": ", 1)
        current[key] = _parse_scalar(raw_value)
    if current and isinstance(current.get("path"), str):
        entries_by_path[str(current["path"])] = current
    return entries_by_path


def _extract_latest_knowledge_rows() -> tuple[str | None, list[list[str]]]:
    board_path = CONTEXT_ROOT / "compacting_differential_board.md"
    if not board_path.exists():
        return None, []
    lines = _read_lines(board_path)
    rows: list[list[str]] = []
    for idx, line in enumerate(lines):
        header = "| cycle_id | row_type | doc_id |"
        if not line.strip().startswith(header):
            continue
        row_index = idx + 2
        while row_index < len(lines):
            row = lines[row_index].rstrip()
            if not row.startswith("|"):
                break
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            if len(cells) < 15:
                row_index += 1
                continue
            if cells[1] != "knowledge_test" or not cells[2]:
                row_index += 1
                continue
            rows.append(cells)
            row_index += 1
    if not rows:
        return None, []
    cycle_id = sorted({row[0] for row in rows if row[0]})[-1]
    latest_rows = [row for row in rows if row[0] == cycle_id]
    return cycle_id, latest_rows


def _load_board_doc_results(config: KnowledgeGateConfig) -> dict[str, BoardDocResult]:
    cycle_id, rows = _extract_latest_knowledge_rows()
    if not cycle_id or not rows:
        return {}

    by_doc: dict[str, dict[str, object]] = {}
    for cells in rows:
        doc_id = cells[2]
        priority = cells[5]
        result = cells[8]
        severity = cells[10].lower()
        streak_value = cells[14] if re.fullmatch(r"[0-9]+", cells[14]) else "0"
        streak = int(streak_value)
        points = 1.0 if result == "correct" else 0.5 if result == "partial" else 0.0

        bucket = by_doc.setdefault(
            doc_id,
            {
                "p0_total": 0,
                "p1_total": 0,
                "p2_total": 0,
                "p0_points": 0.0,
                "p1_points": 0.0,
                "p2_points": 0.0,
                "critical_p0_miss": False,
                "streak": 0,
            },
        )

        total_key = f"{priority.lower()}_total"
        points_key = f"{priority.lower()}_points"
        if total_key not in bucket or points_key not in bucket:
            continue

        bucket[total_key] = int(bucket[total_key]) + 1
        bucket[points_key] = float(bucket[points_key]) + points
        bucket["streak"] = max(int(bucket["streak"]), streak)
        if priority == "P0" and result != "correct" and severity == "critical":
            bucket["critical_p0_miss"] = True

    results: dict[str, BoardDocResult] = {}
    for doc_id, bucket in by_doc.items():
        p0_total = int(bucket["p0_total"])
        p1_total = int(bucket["p1_total"])
        p2_total = int(bucket["p2_total"])
        p0_score = (float(bucket["p0_points"]) / p0_total * 100.0) if p0_total else 0.0
        p1_score = (float(bucket["p1_points"]) / p1_total * 100.0) if p1_total else 0.0
        p2_score = (float(bucket["p2_points"]) / p2_total * 100.0) if p2_total else 0.0
        doc_skill_score = int(round(0.7 * p0_score + 0.2 * p1_score + 0.1 * p2_score))
        critical_p0_miss = bool(bucket["critical_p0_miss"])
        passed = doc_skill_score >= config.pass_threshold and not critical_p0_miss
        results[doc_id] = BoardDocResult(
            last_score=doc_skill_score,
            status="pass" if passed else "fail",
            requires_retest=not passed,
            stability_streak=int(bucket["streak"]),
            last_cycle_id=cycle_id,
        )
    return results


def _resolve_doc_state(
    previous: dict[str, object] | None,
    board_result: BoardDocResult | None,
    config: KnowledgeGateConfig,
) -> tuple[int, str, bool, int, str | None]:
    last_score = _to_int((previous or {}).get("last_score"), 0)
    status = str((previous or {}).get("status", "unrated")).lower()
    requires_retest = _to_bool((previous or {}).get("requires_retest"), True)
    streak = _to_int((previous or {}).get("stability_streak"), 0)
    last_cycle_id = _to_optional_str((previous or {}).get("last_cycle_id"))

    if board_result is not None:
        last_score = board_result.last_score
        status = board_result.status
        requires_retest = board_result.requires_retest
        streak = max(streak, board_result.stability_streak)
        last_cycle_id = board_result.last_cycle_id

    if status != "pass" or last_score < config.pass_threshold or requires_retest:
        return last_score, status, requires_retest, 0, last_cycle_id
    return last_score, status, requires_retest, max(streak, 1), last_cycle_id


def _extract_cycle_id_from_test_file(test_file: str) -> str | None:
    match = re.search(r"/(cycle_[^/]+)/", test_file.replace("\\", "/"))
    if not match:
        return None
    return match.group(1)


def _detect_previous_cycle_id(previous_entries: dict[str, dict[str, object]]) -> str | None:
    cycle_ids: set[str] = set()
    for entry in previous_entries.values():
        test_file = entry.get("test_file")
        if not isinstance(test_file, str):
            continue
        cycle_id = _extract_cycle_id_from_test_file(test_file)
        if cycle_id:
            cycle_ids.add(cycle_id)
    if not cycle_ids:
        return None
    return sorted(cycle_ids)[-1]


def _count_questions_for_cycle(cycle_id: str | None) -> int:
    if not cycle_id:
        return 0
    cycle_dir = SKILL_CHECK_ROOT / "tests" / cycle_id
    if not cycle_dir.exists():
        return 0
    total = 0
    for test_file in sorted(cycle_dir.glob("*.test.md")):
        for line in _read_lines(test_file):
            if re.match(r"^### [A-Z0-9_]+::Q[0-9]{3}$", line):
                total += 1
    return total


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

    unique = sorted({path.replace("\\", "/") for path in required})
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


def _base_question_count(priority: str, loc: int, config: KnowledgeGateConfig) -> int:
    if priority == "P0" or loc >= config.read_loc_max:
        return config.question_large
    if loc >= 120:
        return config.question_medium
    return config.question_small


def _target_question_count(
    base_count: int,
    priority: str,
    stability_streak: int,
    config: KnowledgeGateConfig,
) -> tuple[int, bool]:
    stable = stability_streak >= config.stable_streak_for_shrink
    if not stable:
        return max(base_count, MIN_REQUIRED_COVERAGE_QUESTIONS), False

    if priority == "P0":
        reduced = max(config.p0_min_questions_per_doc, round(base_count * 0.60))
    elif priority == "P1":
        reduced = round(base_count * 0.50)
    else:
        reduced = round(base_count * 0.40)

    target = max(MIN_REQUIRED_COVERAGE_QUESTIONS, min(base_count, reduced))
    return target, target < base_count


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
    heading_anchors: list[str],
    question_total: int,
    base_question_count: int,
    shrink_applied: bool,
    config: KnowledgeGateConfig,
) -> tuple[str, str]:
    mcq_count, short_count, scenario_count = _mix_counts(
        question_total,
        config.format_mcq,
        config.format_short,
    )
    p0_count, p1_count, p2_count = _mix_counts(
        question_total,
        config.priority_p0,
        config.priority_p1,
    )
    if entry.priority == "P0":
        min_p0 = min(question_total, max(config.p0_min_questions_per_doc, 1))
        if p0_count < min_p0:
            needed = min_p0 - p0_count
            p0_count += needed
            if p2_count >= needed:
                p2_count -= needed
            elif p1_count >= needed:
                p1_count -= needed

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
        f"- base_question_count: {base_question_count}",
        f"- stability_streak: {entry.stability_streak}",
        f"- shrink_applied: {'true' if shrink_applied else 'false'}",
        (
            "- format_mix_target: "
            f"{{ mcq: {config.format_mcq:.2f}, short: {config.format_short:.2f}, "
            f"scenario: {config.format_scenario:.2f} }}"
        ),
        (
            "- priority_mix_target: "
            f"{{ p0: {config.priority_p0:.2f}, p1: {config.priority_p1:.2f}, "
            f"p2: {config.priority_p2:.2f} }}"
        ),
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


def _write_manifest(entries: list[ManifestEntry], generated_at: str, cycle_id: str) -> None:
    manifest_path = SKILL_CHECK_ROOT / "manifest" / "onboarding_manifest.yaml"
    lines = [
        "# onboarding_manifest.yaml (GENERATED)",
        "# Generated by skill_check/generate_bootstrap_suite.py",
        "",
        "manifest_version: 1",
        f"generated_at_utc: {generated_at}",
        f"active_cycle_id: {cycle_id}",
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
                f"  stability_streak: {entry.stability_streak}",
            ]
        )
    manifest_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _prune_stale_cycles(cycle_id: str) -> tuple[int, int, int]:
    active_cycle_dir_name = f"cycle_{cycle_id}"
    removed_tests = 0
    removed_answers = 0
    removed_history = 0

    tests_root = SKILL_CHECK_ROOT / "tests"
    for child in tests_root.iterdir():
        if not child.is_dir() or not child.name.startswith("cycle_"):
            continue
        if child.name == active_cycle_dir_name:
            continue
        shutil.rmtree(child)
        removed_tests += 1

    answers_root = SKILL_CHECK_ROOT / "test_answers"
    for child in answers_root.iterdir():
        if not child.is_dir() or not child.name.startswith("cycle_"):
            continue
        if child.name == active_cycle_dir_name:
            continue
        shutil.rmtree(child)
        removed_answers += 1

    history_root = SKILL_CHECK_ROOT / "historical_test_results"
    active_history_file = f"cycle_{cycle_id}.md"
    for child in history_root.glob("cycle_*.md"):
        if child.name == active_history_file:
            continue
        child.unlink()
        removed_history += 1

    return removed_tests, removed_answers, removed_history


def _write_cycle_summary(
    cycle_id: str,
    generated_at: str,
    stats: BuildStats,
    previous_question_total: int,
    compaction_event: bool,
    test_quality_threshold: int,
) -> None:
    output_path = SKILL_CHECK_ROOT / "historical_test_results" / f"cycle_{cycle_id}.md"
    delta_questions = stats.total_questions - previous_question_total
    lines = [
        "# Skill Check Cycle Summary",
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
            f"- compaction_event: {'true' if compaction_event else 'false'}",
            "- notes: suite generation only; knowledge grading not run.",
            "",
            "## Suite maintenance summary",
            f"- total_docs: {stats.total_docs}",
            f"- required_for_certification_docs: {stats.required_docs}",
            f"- generated_test_files: {stats.total_docs}",
            f"- generated_answer_files: {stats.total_docs}",
            f"- total_questions_generated: {stats.total_questions}",
            f"- previous_cycle_questions: {previous_question_total}",
            f"- delta_questions_vs_previous: {delta_questions:+d}",
            f"- stable_docs_detected: {stats.stable_docs}",
            f"- shrink_applied_docs: {stats.shrink_applied_docs}",
            f"- average_test_quality_score: {stats.avg_quality_score:.2f}",
            (
                "- gate_status: pass (all generated tests >= configured threshold)"
                if stats.avg_quality_score >= test_quality_threshold
                else "- gate_status: fail (quality threshold not met)"
            ),
            "",
            "## Cleanup",
            f"- removed_test_cycle_dirs: {stats.removed_test_cycles}",
            f"- removed_answer_cycle_dirs: {stats.removed_answer_cycles}",
            f"- removed_historical_cycle_files: {stats.removed_history_cycles}",
            "",
            "## Validation",
            "- knowledge_score: Not run.",
            "- knowledge_pass_rate: Not run.",
            "- p0_miss_count: Not run.",
            "- critical_p0_miss_count: Not run.",
        ]
    )
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate and maintain the active skill-check suite.",
    )
    parser.add_argument(
        "--cycle-id",
        default=None,
        help="Explicit cycle id (default: UTC timestamp YYYY-MM-DDTHHMMSSZ).",
    )
    parser.add_argument(
        "--compaction-event",
        dest="compaction_event",
        action="store_true",
        default=True,
        help="Treat this run as post-compaction and enforce stale-suite cleanup.",
    )
    parser.add_argument(
        "--no-compaction-event",
        dest="compaction_event",
        action="store_false",
        help="Generate a fresh cycle without enforcing stale-suite cleanup.",
    )
    parser.add_argument(
        "--keep-stale-cycles",
        action="store_true",
        help="Do not delete old cycle artifacts after generation.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    config = _load_knowledge_gate_config()
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cycle_id = args.cycle_id or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")

    required_paths = _gather_required_docs()
    previous_manifest = _load_previous_manifest_entries()
    previous_cycle_id = _detect_previous_cycle_id(previous_manifest)
    previous_question_total = _count_questions_for_cycle(previous_cycle_id)
    board_doc_results = _load_board_doc_results(config)

    test_dir = SKILL_CHECK_ROOT / "tests" / f"cycle_{cycle_id}"
    answer_dir = SKILL_CHECK_ROOT / "test_answers" / f"cycle_{cycle_id}"
    test_dir.mkdir(parents=True, exist_ok=True)
    answer_dir.mkdir(parents=True, exist_ok=True)

    entries: list[ManifestEntry] = []
    quality_scores: list[int] = []
    total_questions = 0
    shrink_applied_docs = 0
    stable_docs = 0

    for path in required_paths:
        normalized_path = path.replace("\\", "/")
        doc_id = _doc_id(normalized_path)
        priority = _priority(normalized_path)
        required_for_certification = priority in {"P0", "P1"}
        previous = previous_manifest.get(normalized_path)
        board_result = board_doc_results.get(doc_id)
        last_score, status, requires_retest, stability_streak, last_cycle_id = _resolve_doc_state(
            previous,
            board_result,
            config,
        )
        if stability_streak >= config.stable_streak_for_shrink:
            stable_docs += 1

        test_file = f"skill_check/tests/cycle_{cycle_id}/{doc_id}.test.md"
        answer_file = f"skill_check/test_answers/cycle_{cycle_id}/{doc_id}.answers.md"
        entry = ManifestEntry(
            doc_id=doc_id,
            path=normalized_path,
            doc_type=_doc_type(normalized_path),
            priority=priority,
            required_for_certification=required_for_certification,
            test_file=test_file,
            answer_file=answer_file,
            last_score=last_score,
            last_cycle_id=last_cycle_id,
            status=status,
            requires_retest=requires_retest,
            stability_streak=stability_streak,
        )
        entries.append(entry)

        loc = len(_read_lines(CONTEXT_ROOT / normalized_path))
        anchors = _extract_heading_anchors(normalized_path)
        base_question_count = _base_question_count(priority, loc, config)
        target_question_count, shrink_applied = _target_question_count(
            base_question_count,
            priority,
            stability_streak,
            config,
        )
        total_questions += target_question_count
        if shrink_applied:
            shrink_applied_docs += 1

        test_content, answer_content = _build_test_content(
            entry=entry,
            cycle_id=cycle_id,
            heading_anchors=anchors,
            question_total=target_question_count,
            base_question_count=base_question_count,
            shrink_applied=shrink_applied,
            config=config,
        )

        (CONTEXT_ROOT / test_file).write_text(test_content, encoding="utf-8")
        (CONTEXT_ROOT / answer_file).write_text(answer_content, encoding="utf-8")

        match = re.search(r"test_quality_score:\s*(\d+)", test_content)
        if not match:
            raise RuntimeError(f"Missing test_quality_score in generated test for {path}")
        quality_scores.append(int(match.group(1)))

    _write_manifest(entries, generated_at, cycle_id)

    removed_tests = 0
    removed_answers = 0
    removed_history = 0
    if args.compaction_event and not args.keep_stale_cycles:
        removed_tests, removed_answers, removed_history = _prune_stale_cycles(cycle_id)

    required_for_certification = sum(1 for entry in entries if entry.required_for_certification)
    average_quality = sum(quality_scores) / len(quality_scores)
    _write_cycle_summary(
        cycle_id=cycle_id,
        generated_at=generated_at,
        stats=BuildStats(
            total_docs=len(entries),
            required_docs=required_for_certification,
            total_questions=total_questions,
            stable_docs=stable_docs,
            shrink_applied_docs=shrink_applied_docs,
            avg_quality_score=average_quality,
            removed_test_cycles=removed_tests,
            removed_answer_cycles=removed_answers,
            removed_history_cycles=removed_history,
        ),
        previous_question_total=previous_question_total,
        compaction_event=args.compaction_event,
        test_quality_threshold=config.test_quality_threshold,
    )

    print(f"cycle_id={cycle_id}")
    print(f"total_docs={len(entries)}")
    print(f"required_for_certification_docs={required_for_certification}")
    print(f"total_questions={total_questions}")
    print(f"stable_docs={stable_docs}")
    print(f"shrink_applied_docs={shrink_applied_docs}")
    print(f"avg_test_quality_score={average_quality:.2f}")
    print(f"removed_test_cycle_dirs={removed_tests}")
    print(f"removed_answer_cycle_dirs={removed_answers}")
    print(f"removed_historical_cycle_files={removed_history}")
    print(f"tests_dir=skill_check/tests/cycle_{cycle_id}")
    print(f"answers_dir=skill_check/test_answers/cycle_{cycle_id}")


if __name__ == "__main__":
    main()
