#!/usr/bin/env python3
"""Reference runner for the GVC derivation conformance fixtures.

Implements the derivation in spec/graded-verdict-custody.md section 5, the
producer-mint prohibition in section 6, and the counted populations in
section 7. The grade vocabulary and its order are read from the canonical
registration artifact — this runner never restates the ladder.

Exit 0 when every case passes; non-zero otherwise, naming each failure.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRATION = ROOT / "registration" / "verdict-grade-registration.json"
FIXTURES = ROOT / "conformance" / "fixtures" / "derivation-cases.json"

UNVERIFIED = "unverified"
PROOF = "proof"
CONSTRUCTED_CHECK = "constructed_check"

OP_UNRUN_DECLARED_CAP = "unrun_declared_cap"
OP_SAME_CHAIN_CAP = "same_chain_cap"
OP_CONFLICT_DEMOTION = "conflict_demotion"
OP_STALENESS_REVERSION = "staleness_reversion"

# Section 9.2: canonical population identifiers — the counter keys the
# fixtures speak. Comparison is per canonical population, never by
# whole-structure equality.
CANONICAL_POPULATIONS = (
    "unverified_from_unrun_declared",
    "degraded",
    "producer_mint_rejected",
    "unbindable_content_identity",
    "same_chain_indeterminate",
    "author_chain_unbound",
    "failed_declared",
    "proof_kernel_exempt",
    "tied_uncap",
)

# Section 9.2: this implementation's declared local-spelling mapping —
# static, total over canonical populations, injective, declared once. The
# reference deliberately spells one counter locally ("unrun_capped") to
# demonstrate that spellings are implementation-local while populations are
# canonical.
POPULATION_MAPPING = {
    "unrun_capped": "unverified_from_unrun_declared",
    "degraded": "degraded",
    "producer_mint_rejected": "producer_mint_rejected",
    "unbindable_content_identity": "unbindable_content_identity",
    "same_chain_indeterminate": "same_chain_indeterminate",
    "author_chain_unbound": "author_chain_unbound",
    "failed_declared": "failed_declared",
    "proof_kernel_exempt": "proof_kernel_exempt",
    "tied_uncap": "tied_uncap",
}


def validate_mapping() -> list:
    """Section 9.2 mapping obligations: injective on canonical populations,
    total over them. Violations are non-conformance by rule."""
    problems = []
    canonical_targets = list(POPULATION_MAPPING.values())
    duplicates = {c for c in canonical_targets if canonical_targets.count(c) > 1}
    if duplicates:
        problems.append(
            f"mapping folds canonical population(s) {sorted(duplicates)} — not injective"
        )
    unmapped = [c for c in CANONICAL_POPULATIONS if c not in canonical_targets]
    if unmapped:
        problems.append(
            f"mapping does not cover canonical population(s) {unmapped} — not total"
        )
    return problems


def load_order() -> list:
    registration = json.loads(REGISTRATION.read_text())
    return registration["ordered_grades"]


class Vocabulary:
    def __init__(self, ordered: list):
        self.ordered = ordered

    def rank(self, grade: str) -> int:
        """Ordinal strength; unknown values rank 0, below every member."""
        for i, member in enumerate(self.ordered):
            if member == grade:
                return len(self.ordered) - i
        return 0

    def one_tier_below(self, grade: str) -> str:
        rank = self.rank(grade)
        if rank <= 1:
            return UNVERIFIED
        return self.ordered[len(self.ordered) - (rank - 1)]


def chain_relation(author: dict, producer: dict) -> str:
    """Section 5 step 3.1 chain classification, kind-free (section 3.1):
    'same' when both chains are non-empty and byte-equal; 'unbound' when the
    author's chain is empty (the normal chainless case, counted distinctly);
    'indeterminate' when the admission-populated producer chain is empty;
    'different' otherwise."""
    author_chain = (author.get("chain_id") or "").strip()
    producer_chain = (producer.get("chain_id") or "").strip()
    if author_chain == "":
        return "unbound"
    if producer_chain == "":
        return "indeterminate"
    if author_chain == producer_chain:
        return "same"
    return "different"


def kernel_proof_exempt(tier: str, author: dict) -> bool:
    """The proof exemption holds only for kernel-kind authorship
    (sections 2.1 and 5 step 3.1)."""
    return tier == PROOF and author.get("kind") == "kernel"


def evaluate_member(
    vocab: Vocabulary,
    oracle: dict,
    producer: dict,
    unrun: int,
    conflict: bool,
    current_identity: str,
) -> tuple:
    """Simulate section 5 steps 2-3.3 for one tied-set member ('Tied top
    tier'). Returns (final_grade, applied_ops, member_counters)."""
    counters = {
        "unrun_capped": 0,
        "degraded": 0,
        "unbindable_content_identity": 0,
        "same_chain_indeterminate": 0,
        "author_chain_unbound": 0,
        "proof_kernel_exempt": 0,
    }
    grade = oracle["tier"]
    author = oracle.get("author", {})
    content = (oracle.get("content_identity") or "").strip()
    ops = []

    # Section 5 step 2: unrun-declared cap.
    if unrun > 0 and vocab.rank(grade) > vocab.rank(UNVERIFIED):
        grade = UNVERIFIED
        ops.append(OP_UNRUN_DECLARED_CAP)
        counters["unrun_capped"] += 1

    # Section 5 step 3.1: chain-keyed cap, kind-free; kernel-only proof
    # exemption; empty chains counted, never guessed.
    relation = chain_relation(author, producer)
    exempt = kernel_proof_exempt(grade, author)
    in_range = (
        vocab.rank(grade) > vocab.rank(CONSTRUCTED_CHECK) and not exempt
    )
    if in_range:
        if relation == "same":
            grade = CONSTRUCTED_CHECK
            ops.append(OP_SAME_CHAIN_CAP)
            counters["degraded"] += 1
        elif relation == "indeterminate":
            counters["same_chain_indeterminate"] += 1
        elif relation == "unbound":
            counters["author_chain_unbound"] += 1
    elif exempt and relation == "same":
        counters["proof_kernel_exempt"] += 1

    # Section 5 step 3.2: conflict demotion (conflict derived by caller
    # from the declared set; the flag is set there).
    if conflict:
        demoted = vocab.one_tier_below(grade)
        if demoted != grade:
            grade = demoted
            ops.append(OP_CONFLICT_DEMOTION)
            counters["degraded"] += 1

    # Section 5 step 3.3: staleness reversion; unbindable counted.
    if (
        content != ""
        and current_identity != ""
        and content != current_identity
        and vocab.rank(grade) > vocab.rank(UNVERIFIED)
    ):
        grade = UNVERIFIED
        ops.append(OP_STALENESS_REVERSION)
        counters["degraded"] += 1
    elif (content == "" or current_identity == "") and vocab.rank(
        grade
    ) > vocab.rank(UNVERIFIED):
        counters["unbindable_content_identity"] += 1

    return grade, ops, counters


def derive(vocab: Vocabulary, case_input: dict) -> tuple:
    counters = {local: 0 for local in POPULATION_MAPPING}
    producer = case_input["work_producer"]
    current_identity = (case_input.get("current_content_identity") or "").strip()

    # Section 8: fail-closed admission — no admission evidence surfaces as
    # unverified with labeled provenance, never dropped.
    if case_input.get("admission_evidence") is False:
        record = {
            "effective_grade": UNVERIFIED,
            "evidence_kind": UNVERIFIED,
            "applied_rank_ops": [],
            "conflicting_evidence": False,
            "failed_declared_evidence": False,
            "provenance": "missing_admission_fact",
            "oracle_author": {},
            "oracle_runner": {},
            "work_producer": producer,
        }
        return record, counters

    declared = case_input.get("declared", [])
    unrun = sum(1 for o in declared if not o.get("ran"))
    failed = [o for o in declared if o.get("ran") and not o.get("passed")]
    # Section 5 'Ran-and-failed declared oracles': counted per oracle,
    # flagged on the record, never a cap or demotion.
    counters["failed_declared"] += len(failed)

    # Section 5 step 1: base = rank-maximum over ran-and-passed tiers; the
    # tied set is every passer at that maximum.
    passed = [o for o in declared if o.get("ran") and o.get("passed")]
    base_rank = max((vocab.rank(o.get("tier", "")) for o in passed), default=0)
    tied = (
        [o for o in passed if vocab.rank(o.get("tier", "")) == base_rank]
        if base_rank > 0
        else []
    )
    base = tied[0]["tier"] if tied else UNVERIFIED

    # Section 5 step 3.2: same-tier disagreement derived from the declared
    # set — at the base tier, at least one passer and one ran-and-failed.
    conflict = base != UNVERIFIED and any(o.get("tier") == base for o in failed)

    if tied:
        evaluations = [
            (evaluate_member(vocab, o, producer, unrun, conflict, current_identity), o)
            for o in tied
        ]
        # Tie selection (section 5): most favorable surviving outcome first,
        # then lexicographically least (author.identity, content_identity).
        evaluations.sort(
            key=lambda ev: (
                -vocab.rank(ev[0][0]),
                (ev[1].get("author", {}).get("identity") or ""),
                (ev[1].get("content_identity") or "").strip(),
            )
        )
        (grade, ops, member_counters), selected = evaluations[0]
        for name, value in member_counters.items():
            counters[name] += value
        # Tied-uncap observability: the MAX left the record uncapped while
        # at least one tied member would have been capped.
        any_member_capped = any(
            OP_SAME_CHAIN_CAP in ev[0][1] for ev in evaluations
        )
        if OP_SAME_CHAIN_CAP not in ops and any_member_capped:
            counters["tied_uncap"] += 1
    else:
        grade, ops, selected = UNVERIFIED, [], None

    record = {
        "effective_grade": grade,
        "evidence_kind": base,
        "applied_rank_ops": ops,
        "conflicting_evidence": conflict,
        "failed_declared_evidence": bool(failed),
        "oracle_author": (selected.get("author", {}) if selected else {}),
        "oracle_runner": (selected.get("runner", {}) if selected else {}),
        "work_producer": producer,
    }

    # Section 6: producer-mint prohibition — derived governs, disagreement
    # counted.
    supplied = case_input.get("producer_supplied_grade")
    if supplied is not None and supplied != record["effective_grade"]:
        counters["producer_mint_rejected"] += 1

    return record, counters


def compare_case(record: dict, counters: dict, expected: dict) -> list:
    """Section 9.2 keyed comparison. Record fields compare strictly per
    expected key; counted populations compare per canonical population after
    inverse mapping. Returns a list of human-readable divergences."""
    divergences = []
    for key, want in expected.items():
        if key == "counters":
            continue
        got = record.get(key)
        if got != want:
            divergences.append(f"{key}: expected {want!r}, got {got!r}")

    inverse = {canonical: local for local, canonical in POPULATION_MAPPING.items()}
    expected_counters = expected.get("counters", {})
    for canonical in CANONICAL_POPULATIONS:
        # Absence in the fixture expectation means zero — an expectation,
        # never a skip (section 9.2).
        want = expected_counters.get(canonical, 0)
        local = inverse.get(canonical)
        if local is None or local not in counters:
            divergences.append(
                f"counters[{canonical}]: canonical population unmapped by "
                "this implementation — failure, not a skip"
            )
            continue
        got = counters[local]
        if got != want:
            divergences.append(f"counters[{canonical}]: expected {want!r}, got {got!r}")
    unknown = [key for key in expected_counters if key not in CANONICAL_POPULATIONS]
    if unknown:
        divergences.append(
            f"fixture expects unknown population(s) {unknown} — not canonical"
        )
    return divergences


def main() -> int:
    mapping_problems = validate_mapping()
    if mapping_problems:
        for problem in mapping_problems:
            print(f"FAIL: population mapping: {problem}")
        return 2
    vocab = Vocabulary(load_order())
    cases = json.loads(FIXTURES.read_text())["cases"]
    if not cases:
        print("FAIL: no fixture cases — the runner cannot discriminate")
        return 2
    failures = 0
    for case in cases:
        record, counters = derive(vocab, case["input"])
        divergences = compare_case(record, counters, case["expect"])
        if not divergences:
            print(f"  OK {case['name']}")
            continue
        failures += 1
        print(f"  FAIL {case['name']}")
        for divergence in divergences:
            print(f"    {divergence}")
    if failures:
        print(f"conformance: {failures} of {len(cases)} case(s) failed")
        return 1
    print(f"conformance: all {len(cases)} case(s) passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
