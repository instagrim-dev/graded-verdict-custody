#!/usr/bin/env python3
"""Build the release's verdict custody record (self-grading release).

Runs the repository's own gates and derives a custody record for the release
artifacts through the reference derivation in `conformance/runner.py` — the
record is never hand-constructed:

- the conformance-fixture run is the release's declared oracle at tier
  constructed_check (its honest ceiling: the judge is authored inside the
  same repository that produces the release, so declaring higher would only
  be capped by the same-chain rule);
- the declared oracle is fed to the reference derivation as a
  DeclaredOracle-shaped input; the derivation's output supplies the record's
  effective grade, evidence kind, applied rank operations, conflict flag,
  and counted populations;
- the record binds to the released commit via --content-identity.

A failing gate mints no record: the builder exits non-zero before any
derivation runs.

Per the specification's normative anti-claim, the record states evidence
strength for the release artifacts — never that the specification is
correct.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "conformance"))

import runner  # reference derivation; import follows the path setup above

GATES = [
    ["python3", "conformance/runner.py"],
    ["python3", "scripts/check_prose_registration_parity.py"],
    ["python3", "scripts/check_publication_boundary.py"],
    ["python3", "scripts/check_publication_boundary.py", "--self-test"],
]

REPO_IDENTITY = "instagrim-dev/graded-verdict-custody"


def build_declared_input(content_identity: str, gates_passed: bool) -> dict:
    """DeclaredOracle-shaped input for the reference derivation.

    The gate suite is the release's single declared oracle. Its author is
    this repository (the judge is authored where the release is produced),
    declared honestly at constructed_check, sharing the producer's chain.
    """
    gate_command = " && ".join(" ".join(g) for g in GATES)
    author = {"identity": REPO_IDENTITY, "kind": "human", "chain_id": REPO_IDENTITY}
    return {
        "work_producer": {
            "identity": REPO_IDENTITY,
            "kind": "human",
            "chain_id": REPO_IDENTITY,
        },
        "current_content_identity": content_identity,
        "declared": [
            {
                "tier": "constructed_check",
                "author": author,
                "command": gate_command,
                "content_identity": content_identity,
                "ran": True,
                "passed": gates_passed,
            }
        ],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content-identity", required=True,
                        help="commit sha the release is cut from")
    parser.add_argument("--runner-identity", default="github-actions",
                        help="identity that executed the judges")
    parser.add_argument("--out", default="release-custody-record.json")
    args = parser.parse_args(argv)

    for gate in GATES:
        result = subprocess.run(gate, cwd=ROOT)
        if result.returncode != 0:
            print(f"FAIL: gate {' '.join(gate)} exited {result.returncode}; "
                  "no custody record is minted for a failing judge")
            return 1

    case_input = build_declared_input(args.content_identity, gates_passed=True)
    vocab = runner.Vocabulary(runner.load_order())
    derived, counters = runner.derive(vocab, case_input)

    declared_oracle = case_input["declared"][0]
    record = {
        "schema": "gvc-release-custody-record/v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "statement": "This record states evidence strength for the release artifacts, never correctness.",
        "derived_by": "conformance/runner.py reference derivation",
        "effective_grade": derived["effective_grade"],
        "evidence_kind": derived["evidence_kind"],
        "applied_rank_ops": derived["applied_rank_ops"],
        "conflicting_evidence": derived["conflicting_evidence"],
        "counters": counters,
        "content_identity": args.content_identity,
        "oracle_author": declared_oracle["author"],
        "oracle_runner": {
            "identity": args.runner_identity,
            "kind": "agent",
            "chain_id": REPO_IDENTITY,
        },
        "work_producer": case_input["work_producer"],
        "same_chain_note": (
            "The judge is authored in the repository it judges; the oracle is "
            "declared at constructed_check, its honest ceiling under the "
            "same-chain rule, so the cap is a no-op rather than a surprise."
        ),
        "judges": [
            {
                "tier": declared_oracle["tier"],
                "command": declared_oracle["command"],
                "ran": declared_oracle["ran"],
                "passed": declared_oracle["passed"],
            }
        ],
    }

    out = ROOT / args.out
    out.write_text(json.dumps(record, indent=2) + "\n")
    print(f"custody record: {record['effective_grade']} -> {out.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
