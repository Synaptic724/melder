"""Build a hard multiple-choice question pool for blind skill checks.

This generator creates:
1) A public question pool (`question_pool/hard_mcq_pool.jsonl`) without
   correct answers.
2) A sealed truth-key file (`.sealed/pool_truth_keys.jsonl`) used only by
   exam generation and grading scripts.

Design goals:
- All questions are MCQ-only.
- Each question has 4 options: 1 truth + 3 close, deterministic lies.
- Pool size target defaults to 10x current question volume.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


CONTEXT_ROOT = Path(__file__).resolve().parent.parent
SKILL_CHECK_ROOT = CONTEXT_ROOT / "skill_check"
MANIFEST_PATH = SKILL_CHECK_ROOT / "manifest" / "onboarding_manifest.yaml"
PUBLIC_POOL_PATH = SKILL_CHECK_ROOT / "question_pool" / "hard_mcq_pool.jsonl"
POOL_META_PATH = SKILL_CHECK_ROOT / "question_pool" / "hard_mcq_pool_meta.json"
SEALED_KEY_PATH = SKILL_CHECK_ROOT / ".sealed" / "pool_truth_keys.jsonl"

QUESTION_HEADER_RE = re.compile(r"^### [A-Z0-9_]+::Q[0-9]{3}$")

NORMATIVE_KEYWORDS = (
    "must",
    "must not",
    "required",
    "require",
    "do not",
    "cannot",
    "never",
    "always",
    "before",
    "after",
    "only",
    "blocked",
    "approval",
    "certification",
    "gate",
)

PROMPT_TEMPLATES = (
    "Select the single true statement for this policy claim.",
    "Choose the exact rule that remains valid under this source anchor.",
    "Pick the one statement that is true for this document context.",
    "Identify the only correct claim from this near-match option set.",
    "Choose the true invariant; the other three options are close lies.",
    "Pick the statement that preserves the policy gate exactly.",
    "Choose the only option that remains policy-compliant.",
    "Select the statement that matches the source rule without drift.",
    "Find the single option that preserves execution ordering and gate semantics.",
    "Pick the exact constraint that still holds under this source anchor.",
    "Identify the one option that does not violate the stated policy.",
    "Choose the only claim that is aligned with the cited rule text.",
    "Select the sole option that remains valid under strict interpretation.",
    "Pick the one option that keeps certification gate behavior unchanged.",
    "Find the only option that survives close-policy scrutiny.",
    "Choose the statement that exactly preserves required behavior.",
    "Select the only policy-preserving statement among close distractors.",
    "Pick the single option that is operationally correct for this source.",
    "Choose the only non-regressing interpretation of this claim.",
    "Select the exact policy claim that remains true.",
)

MODALITY_SWAPS = (
    (r"\bmust not\b", "must"),
    (r"\bmust\b", "must not"),
    (r"\brequired\b", "optional"),
    (r"\bcannot\b", "can"),
    (r"\bnever\b", "sometimes"),
    (r"\balways\b", "usually"),
    (r"\bdo not\b", "do"),
    (r"\bblocked\b", "allowed"),
    (r"\bstrict\b", "flexible"),
)

SEQUENCE_SWAPS = (
    (r"\bbefore\b", "after"),
    (r"\bafter\b", "before"),
    (r"\bfirst\b", "last"),
    (r"\bthen\b", "before that"),
    (r"\bprior to\b", "after"),
    (r"\bpre\b", "post"),
    (r"\bpost\b", "pre"),
)

SCOPE_SWAPS = (
    (r"\bonly\b", "primarily"),
    (r"\ball\b", "some"),
    (r"\bevery\b", "some"),
    (r"\bexact\b", "approximate"),
    (r"\bimmediate\b", "eventual"),
    (r"\bglobal\b", "partial"),
    (r"\bentire\b", "partial"),
)

CONDITION_SWAPS = (
    (r"\bif\b", "unless"),
    (r"\bunless\b", "if"),
    (r"\bwhen\b", "only after"),
    (r"\buntil\b", "after"),
)

ACTOR_SWAPS = (
    (r"\bagent\b", "user"),
    (r"\buser\b", "agent"),
    (r"\bmaintainer\b", "observer"),
    (r"\bowner\b", "consumer"),
)

OPTION_IDS = ("OPT_1", "OPT_2", "OPT_3", "OPT_4")

TRUTH_EQUIVALENT_SWAPS = (
    (r"\bmust not\b", "cannot"),
    (r"\bmust not\b", "is forbidden to"),
    (r"\bmust not\b", "is disallowed from"),
    (r"\bdo not\b", "avoid"),
    (r"\bdo not\b", "refrain from"),
    (r"\bcannot\b", "is prohibited from"),
    (r"\bcannot\b", "is not allowed to"),
    (r"\brequired\b", "mandatory"),
    (r"\brequired\b", "non-optional"),
    (r"\balways\b", "consistently"),
    (r"\bonly\b", "exclusively"),
    (r"\bbefore\b", "prior to"),
    (r"\bafter\b", "subsequent to"),
    (r"\bbefore\b", "prior to"),
    (r"\bafter\b", "following"),
)

TRUTH_FALLBACKS = (
    "The required policy behavior is: {truth}",
    "Under this rule, the correct behavior is: {truth}",
    "Policy-compliant execution requires: {truth}",
    "The valid interpretation here is: {truth}",
    "This policy remains correct only as: {truth}",
    "The source-aligned rule is: {truth}",
    "The acceptable behavior under this policy is: {truth}",
    "This remains the governing rule: {truth}",
    "The normative constraint is: {truth}",
    "The compliant statement is: {truth}",
    "The policy-safe action is: {truth}",
    "The expected gate-respecting behavior is: {truth}",
    "This is the only policy-preserving claim: {truth}",
    "Correct enforcement requires: {truth}",
    "The source-supported claim is: {truth}",
)

MODALITY_FALLBACKS = (
    "{truth} unless explicitly waived by the user",
    "{truth} only when no policy gate is affected",
    "Treat this as optional rather than required: {truth}",
    "Apply this only in low-risk contexts: {truth}",
    "Assume this is advisory, not mandatory: {truth}",
    "Skip this constraint when under time pressure: {truth}",
    "Treat this as non-blocking guidance: {truth}",
    "Apply this only if no certification gate depends on it: {truth}",
    "Enforce this only when convenient: {truth}",
    "Treat this as discretionary behavior: {truth}",
    "Only enforce this when policy misses are already zero: {truth}",
    "Use this as soft guidance, not a hard requirement: {truth}",
    "Apply this constraint only for secondary tasks: {truth}",
    "Treat this as optional if throughput would drop: {truth}",
    "De-prioritize this rule when deadlines are tight: {truth}",
)

SEQUENCE_FALLBACKS = (
    "Treat this as a post-certification step: {truth}",
    "Apply this only after implementation is complete: {truth}",
    "Defer this until after grading is finished: {truth}",
    "Move this to the final cleanup phase: {truth}",
    "Run this after the release decision: {truth}",
    "Apply this only after user approval is granted: {truth}",
    "Perform this after all coding work is done: {truth}",
    "Execute this after ticket closure: {truth}",
    "Handle this at the very end of the cycle: {truth}",
    "Delay this until post-validation: {truth}",
    "Apply this after onboarding is complete: {truth}",
    "Treat this as a follow-up step, not an entry gate: {truth}",
    "Run this only once output has been published: {truth}",
    "Push this after remediation, not before: {truth}",
    "Schedule this in a later pass: {truth}",
)

SCOPE_FALLBACKS = (
    "Apply this to selected workflows only: {truth}",
    "Apply this to non-critical paths instead of all applicable paths: {truth}",
    "Apply this only to one subsystem tier: {truth}",
    "Limit this to secondary tickets: {truth}",
    "Restrict this to non-gating policies: {truth}",
    "Apply this only for partial board updates: {truth}",
    "Use this for optional docs only: {truth}",
    "Apply this only where there is no P0 impact: {truth}",
    "Restrict this to local checks, not global checks: {truth}",
    "Apply this only for exploratory cycles: {truth}",
    "Use this on a subset of required docs: {truth}",
    "Scope this to low-priority items only: {truth}",
    "Apply this only within one lane: {truth}",
    "Constrain this to handoff notes, not core policies: {truth}",
    "Use this only when no certification gate relies on it: {truth}",
)

CONDITION_FALLBACKS = (
    "Apply this only if no blockers are open: {truth}",
    "Apply this only if the user does not challenge onboarding fidelity: {truth}",
    "Apply this only if current score already exceeds threshold: {truth}",
    "Apply this only if anti-cheat checks are skipped: {truth}",
    "Apply this only if all unknowns have been forced to facts: {truth}",
    "Apply this only if no policy drift is detected: {truth}",
    "Apply this only if there are no unresolved tickets: {truth}",
    "Apply this only if the cycle is already marked pass: {truth}",
    "Apply this only if compaction did not trigger: {truth}",
    "Apply this only if no P0 docs are in scope: {truth}",
)

ACTOR_FALLBACKS = (
    "Have the user perform this instead of the agent: {truth}",
    "Delegate this to a reviewer role by default: {truth}",
    "Treat this as maintainer-only work and skip agent ownership: {truth}",
    "Shift this responsibility to downstream consumers: {truth}",
    "Assume an external operator owns this step: {truth}",
    "Reserve this rule for human-only execution: {truth}",
    "Assign this to a passive observer role: {truth}",
    "Move this obligation from agent to approver: {truth}",
    "Treat this as out-of-band owner responsibility: {truth}",
    "Require a different role to execute this gate: {truth}",
)


@dataclass(frozen=True)
class ManifestDoc:
    doc_id: str
    path: str
    required_for_certification: bool


@dataclass(frozen=True)
class Claim:
    doc_id: str
    path: str
    anchor: str
    line_no: int
    text: str


def _slugify(heading: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")
    return slug or "section"


def _load_manifest_docs(required_only: bool) -> list[ManifestDoc]:
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Manifest not found: {MANIFEST_PATH}")

    docs: list[ManifestDoc] = []
    current: dict[str, object] | None = None
    for raw in MANIFEST_PATH.read_text(encoding="utf-8").splitlines():
        if raw.startswith("- doc_id: "):
            if current is not None:
                docs.append(
                    ManifestDoc(
                        doc_id=str(current.get("doc_id", "")),
                        path=str(current.get("path", "")),
                        required_for_certification=bool(
                            current.get("required_for_certification", False)
                        ),
                    )
                )
            current = {"doc_id": raw.split(": ", 1)[1].strip()}
            continue
        if current is None or not raw.startswith("  "):
            continue
        stripped = raw.strip()
        if ": " not in stripped:
            continue
        key, value = stripped.split(": ", 1)
        if key == "required_for_certification":
            current[key] = value.strip().lower() == "true"
        else:
            current[key] = value.strip()
    if current is not None:
        docs.append(
            ManifestDoc(
                doc_id=str(current.get("doc_id", "")),
                path=str(current.get("path", "")),
                required_for_certification=bool(current.get("required_for_certification", False)),
            )
        )

    filtered = [doc for doc in docs if doc.path]
    if required_only:
        filtered = [doc for doc in filtered if doc.required_for_certification]
    return filtered


def _count_existing_questions() -> int:
    total = 0
    tests_root = SKILL_CHECK_ROOT / "tests"
    if not tests_root.exists():
        return 0
    for test_file in tests_root.rglob("*.test.md"):
        for line in test_file.read_text(encoding="utf-8").splitlines():
            if QUESTION_HEADER_RE.match(line):
                total += 1
    return total


def _normalize_claim(line: str) -> str:
    value = line.strip()
    value = re.sub(r"^[-*]\s+", "", value)
    value = re.sub(r"^[0-9]+\)\s+", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value.rstrip(".")


def _is_candidate_claim(line: str) -> bool:
    if not line.strip():
        return False
    normalized = line.lower()
    if len(normalized) < 35:
        return False
    return any(keyword in normalized for keyword in NORMATIVE_KEYWORDS)


def _extract_claims(doc: ManifestDoc) -> list[Claim]:
    path = CONTEXT_ROOT / doc.path
    if not path.exists():
        return []

    lines = path.read_text(encoding="utf-8").splitlines()
    claims: list[Claim] = []
    current_anchor = "overview"

    for idx, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if stripped.startswith("#"):
            current_anchor = _slugify(stripped.lstrip("#").strip())
            continue
        if not _is_candidate_claim(raw):
            continue
        text = _normalize_claim(raw)
        if len(text) < 30:
            continue
        claims.append(
            Claim(
                doc_id=doc.doc_id,
                path=doc.path,
                anchor=current_anchor,
                line_no=idx,
                text=text,
            )
        )

    if claims:
        return claims

    # Fallback: if no normative lines are found, use non-empty prose lines.
    for idx, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if stripped.startswith("#"):
            current_anchor = _slugify(stripped.lstrip("#").strip())
            continue
        if len(stripped) < 35:
            continue
        claims.append(
            Claim(
                doc_id=doc.doc_id,
                path=doc.path,
                anchor=current_anchor,
                line_no=idx,
                text=_normalize_claim(stripped),
            )
        )
        if len(claims) >= 8:
            break
    return claims


def _swap_first(text: str, swaps: Iterable[tuple[str, str]]) -> str:
    for pattern, replacement in swaps:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return re.sub(pattern, replacement, text, count=1, flags=re.IGNORECASE)
    return text


def _lower_first(text: str) -> str:
    if not text:
        return text
    return text[0].lower() + text[1:]


def _paraphrase_truth(truth: str, rng: random.Random) -> str:
    swaps = list(TRUTH_EQUIVALENT_SWAPS)
    rng.shuffle(swaps)
    for pattern, replacement in swaps:
        if re.search(pattern, truth, flags=re.IGNORECASE):
            candidate = re.sub(pattern, replacement, truth, count=1, flags=re.IGNORECASE)
            if candidate != truth:
                return candidate
    return rng.choice(TRUTH_FALLBACKS).format(truth=_lower_first(truth))


def _make_modality_lie(truth: str, rng: random.Random) -> str:
    candidate = _swap_first(truth, MODALITY_SWAPS)
    if candidate != truth:
        return candidate
    return rng.choice(MODALITY_FALLBACKS).format(truth=_lower_first(truth))


def _make_sequence_lie(truth: str, rng: random.Random) -> str:
    candidate = _swap_first(truth, SEQUENCE_SWAPS)
    if candidate != truth:
        return candidate
    return rng.choice(SEQUENCE_FALLBACKS).format(truth=_lower_first(truth))


def _make_scope_lie(truth: str, rng: random.Random) -> str:
    candidate = _swap_first(truth, SCOPE_SWAPS)
    if candidate != truth:
        return candidate
    return rng.choice(SCOPE_FALLBACKS).format(truth=_lower_first(truth))


def _make_condition_lie(truth: str, rng: random.Random) -> str:
    candidate = _swap_first(truth, CONDITION_SWAPS)
    if candidate != truth:
        return candidate
    return rng.choice(CONDITION_FALLBACKS).format(truth=_lower_first(truth))


def _make_actor_lie(truth: str, rng: random.Random) -> str:
    candidate = _swap_first(truth, ACTOR_SWAPS)
    if candidate != truth:
        return candidate
    return rng.choice(ACTOR_FALLBACKS).format(truth=_lower_first(truth))


def _hash_token(value: str, length: int = 12) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:length].upper()


def _build_question(
    claim: Claim,
    variant_index: int,
    rng: random.Random,
) -> tuple[dict[str, object], dict[str, object]]:
    truth = claim.text
    truth_surface = _paraphrase_truth(truth, rng)

    lie_builders = [
        _make_modality_lie,
        _make_sequence_lie,
        _make_scope_lie,
        _make_condition_lie,
        _make_actor_lie,
    ]
    rng.shuffle(lie_builders)
    lies: list[str] = [builder(truth, rng) for builder in lie_builders]

    # Prevent duplicate options within a question to keep answerability stable.
    normalized_seen: set[str] = {truth_surface.lower()}
    unique_lies: list[str] = []
    for lie in lies:
        normalized = lie.lower()
        if normalized in normalized_seen:
            continue
        normalized_seen.add(normalized)
        unique_lies.append(lie)
    while len(unique_lies) < 3:
        filler = f"Apply this rule opportunistically rather than consistently: {_lower_first(truth)}"
        if filler.lower() not in normalized_seen:
            unique_lies.append(filler)
            normalized_seen.add(filler.lower())
            continue
        filler = f"Treat this as advisory guidance instead of a hard gate: {_lower_first(truth)}"
        if filler.lower() not in normalized_seen:
            unique_lies.append(filler)
            normalized_seen.add(filler.lower())

    option_payload = [{"text": truth_surface, "is_truth": True}] + [
        {"text": lie, "is_truth": False} for lie in unique_lies[:3]
    ]
    rng.shuffle(option_payload)

    prompt_template = PROMPT_TEMPLATES[variant_index % len(PROMPT_TEMPLATES)]
    question_id_seed = (
        f"{claim.doc_id}|{claim.path}|{claim.anchor}|{claim.line_no}|"
        f"{variant_index}|{truth}"
    )
    question_id = f"{claim.doc_id}::H{_hash_token(question_id_seed)}"

    option_rows: list[dict[str, str]] = []
    truth_option_id = ""
    for idx, payload in enumerate(option_payload):
        text = payload["text"]
        option_id = OPTION_IDS[idx]
        option_rows.append({"option_id": option_id, "text": text})
        if payload["is_truth"] and not truth_option_id:
            truth_option_id = option_id

    public_row: dict[str, object] = {
        "question_id": question_id,
        "doc_id": claim.doc_id,
        "source_path": claim.path,
        "source_anchor": claim.anchor,
        "source_line": claim.line_no,
        "difficulty": "hard",
        "variant_index": variant_index,
        "prompt": (
            f"{prompt_template} Source: `{claim.path}#{claim.anchor}`. "
            "Choose one option."
        ),
        "options": option_rows,
    }
    sealed_row: dict[str, object] = {
        "question_id": question_id,
        "truth_option_id": truth_option_id,
        "truth_sha256": hashlib.sha256(truth.encode("utf-8")).hexdigest(),
    }
    return public_row, sealed_row


def _ensure_dirs() -> None:
    (SKILL_CHECK_ROOT / "question_pool").mkdir(parents=True, exist_ok=True)
    (SKILL_CHECK_ROOT / ".sealed").mkdir(parents=True, exist_ok=True)


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build hard MCQ question pool.")
    parser.add_argument(
        "--multiplier",
        type=int,
        default=10,
        help="Target pool size as N x current question count (default: 10).",
    )
    parser.add_argument(
        "--required-only",
        action="store_true",
        help="Use required-for-certification docs only.",
    )
    parser.add_argument(
        "--min-total",
        type=int,
        default=0,
        help="Minimum absolute question count regardless of multiplier.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.multiplier < 1:
        raise ValueError("--multiplier must be >= 1")

    docs = _load_manifest_docs(required_only=args.required_only)
    if not docs:
        raise RuntimeError("No docs available from manifest.")

    claims: list[Claim] = []
    for doc in docs:
        claims.extend(_extract_claims(doc))
    if not claims:
        raise RuntimeError("No claims extracted from source docs.")

    existing_total = _count_existing_questions()
    loc_based_min = 0
    for doc in docs:
        loc = len((CONTEXT_ROOT / doc.path).read_text(encoding="utf-8").splitlines())
        loc_based_min += max(1, (loc + 99) // 100)

    target_total = max(existing_total * args.multiplier, loc_based_min * args.multiplier, args.min_total)

    questions: list[dict[str, object]] = []
    sealed_rows: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    per_doc_counts: dict[str, int] = {}
    rng_seed_monotonic_ns = time.monotonic_ns()
    rng = random.Random(rng_seed_monotonic_ns)

    variant = 0
    while len(questions) < target_total:
        made_progress = False
        for claim in claims:
            public_row, sealed_row = _build_question(claim, variant, rng)
            question_id = str(public_row["question_id"])
            if question_id in seen_ids:
                continue
            seen_ids.add(question_id)
            questions.append(public_row)
            sealed_rows.append(sealed_row)
            per_doc_counts[claim.doc_id] = per_doc_counts.get(claim.doc_id, 0) + 1
            made_progress = True
            if len(questions) >= target_total:
                break
        if not made_progress:
            raise RuntimeError("Unable to generate enough unique questions.")
        variant += 1

    _ensure_dirs()
    _write_jsonl(PUBLIC_POOL_PATH, questions)
    _write_jsonl(SEALED_KEY_PATH, sealed_rows)

    meta = {
        "pool_version": 1,
        "required_only": bool(args.required_only),
        "multiplier": args.multiplier,
        "existing_question_count": existing_total,
        "loc_based_minimum": loc_based_min,
        "target_total": target_total,
        "generated_total": len(questions),
        "doc_count": len(docs),
        "claims_extracted": len(claims),
        "max_variant_index": variant,
        "rng_seed_monotonic_ns": rng_seed_monotonic_ns,
        "public_pool_path": str(PUBLIC_POOL_PATH.relative_to(CONTEXT_ROOT)).replace("\\", "/"),
        "sealed_key_path": str(SEALED_KEY_PATH.relative_to(CONTEXT_ROOT)).replace("\\", "/"),
        "per_doc_counts": per_doc_counts,
    }
    POOL_META_PATH.write_text(json.dumps(meta, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    print(f"generated_total={len(questions)}")
    print(f"target_total={target_total}")
    print(f"existing_question_count={existing_total}")
    print(f"doc_count={len(docs)}")
    print(f"claims_extracted={len(claims)}")
    print(f"public_pool={PUBLIC_POOL_PATH}")
    print(f"sealed_keys={SEALED_KEY_PATH}")


if __name__ == "__main__":
    main()
