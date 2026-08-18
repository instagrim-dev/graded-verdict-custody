#!/usr/bin/env python3
"""Red-path test for the release custody record builder.

Proves both polarities of the builder's gate contract:

  red   — a failing gate mints NO record (exit non-zero, no output file);
  green — with passing gates the record is produced by the reference
          derivation: constructed_check, no rank operations, counters
          attached, and it re-derives identically through
          conformance/runner.py on the same DeclaredOracle-shaped input.

Run: python3 scripts/test_release_builder_red_path.py
"""

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "conformance"))

import runner  # reference derivation; import follows the path setup above

spec = importlib.util.spec_from_file_location(
    "build_release_custody_record",
    ROOT / "scripts" / "build_release_custody_record.py",
)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def main() -> int:
    failures = 0

    with tempfile.TemporaryDirectory() as tmp:
        out_rel = Path(tmp).name + "-red-record.json"
        out_path = ROOT / out_rel

        # Red path: one failing gate => non-zero exit, no record file.
        original_gates = builder.GATES
        builder.GATES = [["python3", "-c", "raise SystemExit(1)"]]
        try:
            rc = builder.main(["--content-identity", "deadbeef", "--out", out_rel])
        finally:
            builder.GATES = original_gates
        if rc == 0:
            print("  FAIL red-path: builder exited 0 under a failing gate")
            failures += 1
        elif out_path.exists():
            print("  FAIL red-path: a record was minted despite the failing gate")
            failures += 1
        else:
            print("  OK red-path: failing gate => no record minted")

        # Green path: passing (no-op) gate => derivation-produced record.
        out_rel = Path(tmp).name + "-green-record.json"
        out_path = ROOT / out_rel
        builder.GATES = [["python3", "-c", "raise SystemExit(0)"]]
        try:
            rc = builder.main(["--content-identity", "deadbeef", "--out", out_rel])
        finally:
            builder.GATES = original_gates
        try:
            if rc != 0 or not out_path.exists():
                print("  FAIL green-path: builder did not mint a record under passing gates")
                failures += 1
            else:
                record = json.loads(out_path.read_text())
                vocab = runner.Vocabulary(runner.load_order())
                case_input = builder.build_declared_input("deadbeef", gates_passed=True)
                derived, counters = runner.derive(vocab, case_input)
                checks = {
                    "effective_grade": derived["effective_grade"],
                    "evidence_kind": derived["evidence_kind"],
                    "applied_rank_ops": derived["applied_rank_ops"],
                    "conflicting_evidence": derived["conflicting_evidence"],
                    "counters": counters,
                }
                mismatches = {
                    key: (record.get(key), want)
                    for key, want in checks.items()
                    if record.get(key) != want
                }
                if mismatches:
                    print(f"  FAIL green-path: record diverges from reference derivation: {mismatches}")
                    failures += 1
                elif record["effective_grade"] != "constructed_check":
                    print(f"  FAIL green-path: expected constructed_check, got {record['effective_grade']}")
                    failures += 1
                else:
                    print("  OK green-path: record is derivation-produced at constructed_check")
        finally:
            if out_path.exists():
                out_path.unlink()

    if failures:
        print(f"release-builder test: {failures} failure(s)")
        return 1
    print("release-builder test: both polarities pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
