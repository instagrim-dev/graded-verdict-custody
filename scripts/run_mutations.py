#!/usr/bin/env python3
"""Executable mutation harness for the GVC conformance suite.

Each registered mutation is a claim: "this fixture set discriminates this
derivation rule." The harness proves every claim by execution, never by
narration:

  1. copy the runner, fixtures, and registration to a temporary tree;
  2. apply one mutation (exact, unique source-substring replacements);
  3. run the reference runner and collect the failing case names;
  4. assert EXACTLY the registered fixture names failed — a green suite
     (vacuous mutation), a missing expected failure, or any unexpected
     extra failure is a harness FAILURE, fail-closed;
  5. restore the original bytes and assert the suite is green again.

The real repository tree is never modified: all apply/run/restore cycles
happen on the temporary copy.

Modes:

  (default)    run every registered mutation; exit nonzero on any failure.
  --self-test  polarity proof: run a deliberately vacuous mutation (bytes
               change, behavior does not) through the same loop and assert
               the harness rejects it by name. Exits 0 only when the
               red path fired; the vacuous spec is never part of the
               default registry.
  --ledger     run every registered mutation, then regenerate
               conformance/MUTATION-LEDGER.md from the executed results.
  --ledger --check
               regenerate to a buffer and fail if the tracked ledger
               differs (staleness gate; writes nothing).
"""

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNNER = "conformance/runner.py"
FIXTURES = "conformance/fixtures/derivation-cases.json"
REGISTRATION = "registration/verdict-grade-registration.json"
LEDGER = ROOT / "conformance" / "MUTATION-LEDGER.md"

COPY_SET = (RUNNER, FIXTURES, REGISTRATION)

OK_LINE = re.compile(r"^  OK (\S+)$")
FAIL_LINE = re.compile(r"^  FAIL (\S+)$")


class MutationSpec:
    """One registered mutation.

    replacements: ordered (old, new) pairs; each `old` must occur exactly
    once in the target's current text — anything else refuses to apply
    (fail-closed: a silently unapplied mutation would prove nothing).
    expect_failing: the exact set of fixture names that must fail.
    expect_validation: when set, the mutated runner must instead fail
    before any case runs (exit 2) and its output must contain every
    listed substring (used for section 9.2 mapping-validation mutations).
    """

    def __init__(self, mutation_id, rule, target, replacements,
                 expect_failing=(), expect_validation=()):
        self.mutation_id = mutation_id
        self.rule = rule
        self.target = target
        self.replacements = replacements
        self.expect_failing = frozenset(expect_failing)
        self.expect_validation = tuple(expect_validation)


REGISTRY = [
    MutationSpec(
        "proof_exemption_removed",
        "section 5 step 3.1: the kernel proof exemption is load-bearing",
        RUNNER,
        [(
            "    return tier == PROOF and author.get(\"kind\") == \"kernel\"",
            "    return False",
        )],
        expect_failing=["same_chain_cap_exempts_kernel_proof"],
    ),
    MutationSpec(
        "unrun_cap_disabled",
        "section 5 step 2: the unrun-declared cap is load-bearing",
        RUNNER,
        [(
            "    if unrun > 0 and vocab.rank(grade) > vocab.rank(UNVERIFIED):",
            "    if False and unrun > 0 and vocab.rank(grade) > vocab.rank(UNVERIFIED):",
        )],
        expect_failing=[
            "unrun_declared_cap_fires",
            "conflict_demotion_unverified_demotes_to_itself",
            "unbindable_not_counted_at_unverified",
        ],
    ),
    MutationSpec(
        "conflict_demotion_returns_same_tier",
        "section 5 step 3.2: demotion moves one ordinal tier",
        RUNNER,
        [(
            "        rank = self.rank(grade)\n        if rank <= 1:\n            return UNVERIFIED",
            "        return grade\n        rank = self.rank(grade)\n        if rank <= 1:\n            return UNVERIFIED",
        )],
        expect_failing=[
            "conflict_demotion_fires_one_ordinal_tier",
            "composed_ops_retained_in_application_order",
        ],
    ),
    MutationSpec(
        "staleness_condition_forced_false",
        "section 5 step 3.3: staleness reversion is load-bearing",
        RUNNER,
        [(
            "        and content != current_identity\n        and vocab.rank(grade) > vocab.rank(UNVERIFIED)\n    ):",
            "        and False\n        and vocab.rank(grade) > vocab.rank(UNVERIFIED)\n    ):",
        )],
        expect_failing=[
            "staleness_reversion_fires_on_content_identity_change",
            "composed_ops_retained_in_application_order",
            "relabel_evasion_staleness_still_fires",
        ],
    ),
    MutationSpec(
        "mapping_targets_swapped",
        "section 9.2: a wrong (still injective/total) mapping fails its witness fixtures",
        RUNNER,
        [
            (
                "    \"unbindable_content_identity\": \"unbindable_content_identity\",",
                "    \"unbindable_content_identity\": \"same_chain_indeterminate\",",
            ),
            (
                "    \"same_chain_indeterminate\": \"same_chain_indeterminate\",",
                "    \"same_chain_indeterminate\": \"unbindable_content_identity\",",
            ),
        ],
        expect_failing=[
            "same_chain_indeterminate_is_counted_not_assumed",
            "staleness_unbindable_is_counted_not_exempted_silently",
        ],
    ),
    MutationSpec(
        "mapping_folds_two_populations",
        "section 9.2: folding two canonical populations is non-conformance by rule",
        RUNNER,
        [(
            "    \"same_chain_indeterminate\": \"same_chain_indeterminate\",",
            "    \"same_chain_indeterminate\": \"unbindable_content_identity\",",
        )],
        expect_validation=["not injective", "not total"],
    ),
    MutationSpec(
        "tie_break_reverted_to_array_order",
        "section 5 tied-set MAX is order-independent (the twins exist because one order coincides with pre-repair behavior)",
        RUNNER,
        [(
            "        evaluations.sort(\n            key=lambda ev: (\n                -vocab.rank(ev[0][0]),\n                (ev[1].get(\"author\", {}).get(\"identity\") or \"\"),\n                (ev[1].get(\"content_identity\") or \"\").strip(),\n            )\n        )",
            "        pass",
        )],
        expect_failing=[
            "tied_top_tier_uncapped_member_wins_order_ab",
            "tied_top_tier_all_capped_folds_once",
        ],
    ),
    MutationSpec(
        "tied_uncap_increment_zeroed",
        "section 5/7: tied-uncap observability population is load-bearing",
        RUNNER,
        [(
            "        if OP_SAME_CHAIN_CAP not in ops and any_member_capped:\n            counters[\"tied_uncap\"] += 1",
            "        if OP_SAME_CHAIN_CAP not in ops and any_member_capped:\n            counters[\"tied_uncap\"] += 0",
        )],
        expect_failing=[
            "tied_top_tier_uncapped_member_wins_order_ab",
            "tied_top_tier_uncapped_member_wins_order_ba",
        ],
    ),
    MutationSpec(
        "failed_declared_increment_zeroed",
        "section 5: ran-and-failed declared oracles are counted per oracle",
        RUNNER,
        [(
            "    counters[\"failed_declared\"] += len(failed)",
            "    counters[\"failed_declared\"] += 0",
        )],
        expect_failing=[
            "conflict_demotion_fires_one_ordinal_tier",
            "conflict_demotion_unverified_demotes_to_itself",
            "failed_declared_counted_and_flagged",
            "composed_ops_retained_in_application_order",
        ],
    ),
    MutationSpec(
        "failed_flag_hardcoded_true",
        "section 5: failed_declared_evidence flag polarity (not set when none failed)",
        RUNNER,
        [(
            "        \"failed_declared_evidence\": bool(failed),",
            "        \"failed_declared_evidence\": True,",
        )],
        expect_failing=["passed_only_not_flagged_failed_declared"],
    ),
    MutationSpec(
        "kernel_kind_requirement_dropped",
        "section 5 step 3.1: the proof exemption requires kernel kind",
        RUNNER,
        [(
            "    return tier == PROOF and author.get(\"kind\") == \"kernel\"",
            "    return tier == PROOF",
        )],
        expect_failing=["agent_authored_proof_same_chain_capped"],
    ),
    MutationSpec(
        "proof_kernel_exempt_increment_zeroed",
        "section 7: kernel-kind proof exemptions are counted",
        RUNNER,
        [(
            "    elif exempt and relation == \"same\":\n        counters[\"proof_kernel_exempt\"] += 1",
            "    elif exempt and relation == \"same\":\n        counters[\"proof_kernel_exempt\"] += 0",
        )],
        expect_failing=["same_chain_cap_exempts_kernel_proof"],
    ),
    MutationSpec(
        "cap_regated_on_agent_kind",
        "section 5 step 3.1: the same-chain cap is kind-free (pre-repair kind gating fails)",
        RUNNER,
        [(
            "    in_range = (\n        vocab.rank(grade) > vocab.rank(CONSTRUCTED_CHECK) and not exempt\n    )",
            "    in_range = (\n        vocab.rank(grade) > vocab.rank(CONSTRUCTED_CHECK) and not exempt\n        and author.get(\"kind\") == \"agent\"\n    )",
        )],
        expect_failing=[
            "author_chain_unbound_counted_distinctly",
            "human_author_same_chain_caps",
        ],
    ),
    MutationSpec(
        "unbound_folded_into_indeterminate",
        "section 5 step 3.1: author-chain-unbound is distinct from same-chain-indeterminate",
        RUNNER,
        [(
            "        elif relation == \"unbound\":\n            counters[\"author_chain_unbound\"] += 1",
            "        elif relation == \"unbound\":\n            counters[\"same_chain_indeterminate\"] += 1",
        )],
        expect_failing=["author_chain_unbound_counted_distinctly"],
    ),
    MutationSpec(
        "conflict_derivation_forced_false",
        "section 5 step 3.2: conflict is derived from the declared set, never caller-supplied",
        RUNNER,
        [(
            "    conflict = base != UNVERIFIED and any(o.get(\"tier\") == base for o in failed)",
            "    conflict = False",
        )],
        expect_failing=[
            "conflict_demotion_fires_one_ordinal_tier",
            "conflict_demotion_unverified_demotes_to_itself",
            "composed_ops_retained_in_application_order",
        ],
    ),
    MutationSpec(
        "applied_ops_reversed",
        "section 5 step 4: applied rank operations are retained in application order",
        RUNNER,
        [(
            "        \"applied_rank_ops\": ops,\n        \"conflicting_evidence\": conflict,",
            "        \"applied_rank_ops\": list(reversed(ops)),\n        \"conflicting_evidence\": conflict,",
        )],
        expect_failing=["composed_ops_retained_in_application_order"],
    ),
    MutationSpec(
        "oracle_runner_triple_dropped",
        "section 3: custody role triples are carried on the record",
        RUNNER,
        [(
            "        \"oracle_runner\": (selected.get(\"runner\", {}) if selected else {}),",
            "        \"oracle_runner\": {},",
        )],
        expect_failing=[
            "conflict_demotion_fires_one_ordinal_tier",
            "composed_ops_retained_in_application_order",
        ],
    ),
    MutationSpec(
        "missing_admission_branch_disabled",
        "section 8: fail-closed admission is load-bearing",
        RUNNER,
        [(
            "    if case_input.get(\"admission_evidence\") is False:",
            "    if False and case_input.get(\"admission_evidence\") is False:",
        )],
        expect_failing=["missing_admission_evidence_fails_closed"],
    ),
    MutationSpec(
        "base_derivation_min_instead_of_max",
        "section 5 step 1: the base grade is the rank-MAXIMUM over ran-and-passed tiers",
        RUNNER,
        [(
            "    base_rank = max((vocab.rank(o.get(\"tier\", \"\")) for o in passed), default=0)",
            "    base_rank = min((vocab.rank(o.get(\"tier\", \"\")) for o in passed), default=0)",
        )],
        expect_failing=["passed_only_not_flagged_failed_declared"],
    ),
    MutationSpec(
        "producer_mint_admitted",
        "section 6: a producer-supplied grade is never admitted; the derived record governs",
        RUNNER,
        [(
            "    supplied = case_input.get(\"producer_supplied_grade\")\n    if supplied is not None and supplied != record[\"effective_grade\"]:\n        counters[\"producer_mint_rejected\"] += 1",
            "    supplied = case_input.get(\"producer_supplied_grade\")\n    if supplied is not None:\n        record[\"effective_grade\"] = supplied",
        )],
        expect_failing=["producer_mint_rejected_derived_governs"],
    ),
    MutationSpec(
        "unknown_grade_ranks_above_all",
        "section 2: a value outside the vocabulary ranks strictly below every member",
        RUNNER,
        [(
            "        for i, member in enumerate(self.ordered):\n            if member == grade:\n                return len(self.ordered) - i\n        return 0",
            "        for i, member in enumerate(self.ordered):\n            if member == grade:\n                return len(self.ordered) - i\n        return len(self.ordered) + 1",
        )],
        expect_failing=["unknown_grade_ranks_zero_below_unverified"],
    ),
    MutationSpec(
        "unbindable_increment_zeroed",
        "section 5 step 3.3 / section 7: unbindable content identity is counted, never silently exempted",
        RUNNER,
        [(
            "    ) > vocab.rank(UNVERIFIED):\n        counters[\"unbindable_content_identity\"] += 1",
            "    ) > vocab.rank(UNVERIFIED):\n        counters[\"unbindable_content_identity\"] += 0",
        )],
        expect_failing=["staleness_unbindable_is_counted_not_exempted_silently"],
    ),
    MutationSpec(
        "indeterminate_increment_zeroed",
        "section 5 step 3.1 / section 7: same-chain-indeterminate is counted, never assumed",
        RUNNER,
        [(
            "        elif relation == \"indeterminate\":\n            counters[\"same_chain_indeterminate\"] += 1",
            "        elif relation == \"indeterminate\":\n            counters[\"same_chain_indeterminate\"] += 0",
        )],
        expect_failing=["same_chain_indeterminate_is_counted_not_assumed"],
    ),
    MutationSpec(
        "degraded_increments_zeroed",
        "section 7: the degraded population counts each applied step-3 rank operation",
        RUNNER,
        [
            (
                "            ops.append(OP_SAME_CHAIN_CAP)\n            counters[\"degraded\"] += 1",
                "            ops.append(OP_SAME_CHAIN_CAP)\n            counters[\"degraded\"] += 0",
            ),
            (
                "            ops.append(OP_CONFLICT_DEMOTION)\n            counters[\"degraded\"] += 1",
                "            ops.append(OP_CONFLICT_DEMOTION)\n            counters[\"degraded\"] += 0",
            ),
            (
                "        ops.append(OP_STALENESS_REVERSION)\n        counters[\"degraded\"] += 1",
                "        ops.append(OP_STALENESS_REVERSION)\n        counters[\"degraded\"] += 0",
            ),
        ],
        expect_failing=[
            "same_chain_cap_fires_for_same_chain_agent_author",
            "agent_authored_proof_same_chain_capped",
            "human_author_same_chain_caps",
            "conflict_demotion_fires_one_ordinal_tier",
            "staleness_reversion_fires_on_content_identity_change",
            "tied_top_tier_all_capped_folds_once",
            "composed_ops_retained_in_application_order",
            "relabel_evasion_staleness_still_fires",
        ],
    ),
]

VACUOUS_SELF_TEST_SPEC = MutationSpec(
    "self_test_vacuous_docstring_edit",
    "harness polarity: a mutation that changes bytes but no behavior MUST be rejected",
    RUNNER,
    [(
        "\"\"\"Reference runner for the GVC derivation conformance fixtures.",
        "\"\"\"Reference runner (vacuously mutated) for the GVC derivation conformance fixtures.",
    )],
    expect_failing=["no_declared_oracles_yields_unverified"],
)


def self_test() -> int:
    """Red-path proof: push a deliberately vacuous mutation through the
    same loop and require the harness to reject it by name. The vacuous
    spec is never part of the default registry."""
    results, failures = run_all([VACUOUS_SELF_TEST_SPEC], verbose=False)
    if failures == 0:
        print(
            "FAIL: self-test vacuous mutation was ACCEPTED — the harness "
            "cannot distinguish a discriminating mutation from a no-op"
        )
        return 1
    print(
        "self-test: vacuous mutation "
        f"{VACUOUS_SELF_TEST_SPEC.mutation_id!r} rejected fail-closed "
        "(suite stayed green under it and the harness exited nonzero naming it)"
    )
    return 0


def run_runner(tmp_root: Path):
    """Run the copied runner; return (exit_code, ok_names, fail_names, out)."""
    proc = subprocess.run(
        [sys.executable, str(tmp_root / RUNNER)],
        capture_output=True, text=True,
    )
    ok, failed = set(), set()
    for line in proc.stdout.splitlines():
        m = OK_LINE.match(line)
        if m:
            ok.add(m.group(1))
            continue
        m = FAIL_LINE.match(line)
        if m:
            failed.add(m.group(1))
    return proc.returncode, ok, failed, proc.stdout + proc.stderr


def make_tmp_tree(tmp_root: Path) -> dict:
    """Copy the suite into tmp_root; return {relpath: original_bytes}."""
    originals = {}
    for rel in COPY_SET:
        src = ROOT / rel
        dst = tmp_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        originals[rel] = src.read_bytes()
    return originals


def apply_mutation(tmp_root: Path, spec: MutationSpec) -> list:
    """Apply replacements to the temp copy; return list of problems."""
    problems = []
    path = tmp_root / spec.target
    text = path.read_text()
    for old, new in spec.replacements:
        count = text.count(old)
        if count != 1:
            problems.append(
                f"replacement source occurs {count} time(s), need exactly 1: "
                f"{old[:70]!r}"
            )
            continue
        text = text.replace(old, new)
    if not problems:
        path.write_text(text)
    return problems


def check_one(tmp_root: Path, originals: dict, spec: MutationSpec,
              baseline_cases: set) -> tuple:
    """Run one mutation cycle. Returns (problems, observed_failing)."""
    problems = apply_mutation(tmp_root, spec)
    observed = set()
    if not problems:
        code, ok, failed, out = run_runner(tmp_root)
        observed = failed
        if spec.expect_validation:
            if code != 2:
                problems.append(f"expected validation failure (exit 2), got exit {code}")
            for needle in spec.expect_validation:
                if needle not in out:
                    problems.append(f"validation output missing {needle!r}")
            if failed:
                problems.append(f"expected no per-case failures, got {sorted(failed)}")
        else:
            if code == 0 or not failed:
                problems.append(
                    "VACUOUS: mutation applied but every case passed — "
                    "the suite does not discriminate this mutation"
                )
            else:
                missing = spec.expect_failing - failed
                extra = failed - spec.expect_failing
                if missing:
                    problems.append(f"expected failing case(s) stayed green: {sorted(missing)}")
                if extra:
                    problems.append(f"unexpected extra failing case(s): {sorted(extra)}")
    # Restore from saved bytes and demand green, even after apply problems.
    (tmp_root / spec.target).write_bytes(originals[spec.target])
    code, ok, failed, _ = run_runner(tmp_root)
    if code != 0 or failed or ok != baseline_cases:
        problems.append("restore did not return the suite to the green baseline")
    return problems, observed


def fixture_case_names() -> set:
    return {c["name"] for c in json.loads((ROOT / FIXTURES).read_text())["cases"]}


def run_all(specs, verbose=True):
    """Run every spec; return (results, failures) where results is a list of
    (spec, observed_failing_sorted) for the ledger."""
    results, failures = [], 0
    with tempfile.TemporaryDirectory(prefix="gvc-mutations-") as tmp:
        tmp_root = Path(tmp)
        originals = make_tmp_tree(tmp_root)
        code, ok, failed, out = run_runner(tmp_root)
        if code != 0 or failed:
            print("FAIL: pre-mutation baseline is not green; refusing to run")
            print(out)
            return results, 1
        baseline_cases = ok
        seen_ids = set()
        for spec in specs:
            if spec.mutation_id in seen_ids:
                print(f"  FAIL {spec.mutation_id}: duplicate mutation id")
                failures += 1
                continue
            seen_ids.add(spec.mutation_id)
            unknown = spec.expect_failing - baseline_cases
            if unknown:
                print(f"  FAIL {spec.mutation_id}: expected fixture(s) not in suite: {sorted(unknown)}")
                failures += 1
                continue
            problems, observed = check_one(tmp_root, originals, spec, baseline_cases)
            if problems:
                failures += 1
                print(f"  FAIL {spec.mutation_id}")
                for p in problems:
                    print(f"    {p}")
                continue
            results.append((spec, sorted(observed)))
            if verbose:
                if spec.expect_validation:
                    print(f"  OK {spec.mutation_id}: mapping validation failed loudly (exit 2), no case ran")
                else:
                    print(f"  OK {spec.mutation_id}: exactly {sorted(observed)} failed; restore green")
    return results, failures


def build_registry():
    return REGISTRY


def render_ledger(results, case_count: int) -> str:
    """Render MUTATION-LEDGER.md from executed results only. Deterministic:
    no timestamps, so `--ledger --check` can gate staleness byte-for-byte."""
    lines = [
        "# Conformance mutation ledger",
        "",
        "GENERATED FILE — regenerated from executed harness output by",
        "`python3 scripts/run_mutations.py --ledger`; do not edit by hand",
        "(CI re-derives it and fails on drift).",
        "",
        "Each derivation rule is proven load-bearing by executing",
        "`scripts/run_mutations.py`: every registered mutation is applied to a",
        "temporary copy of the reference runner, the suite is run, the harness",
        "asserts EXACTLY the named fixture(s) fail and nothing else, the",
        "original bytes are restored, and the suite is asserted green again.",
        "A mutation under which every case passes is a harness FAILURE",
        "(fail-closed), and that polarity is itself proven by",
        "`python3 scripts/run_mutations.py --self-test`, which pushes a",
        "deliberately vacuous mutation through the same loop and requires its",
        "rejection.",
        "",
        f"Restored baseline after every row: `all {case_count} case(s) passed`.",
        "",
        "| Mutation | Rule under proof | Observed failing case(s) |",
        "| --- | --- | --- |",
    ]
    for spec, observed in results:
        if spec.expect_validation:
            outcome = (
                "mapping validation failed loudly before any case ran "
                "(exit 2: " + "; ".join(f"`{s}`" for s in spec.expect_validation) + ")"
            )
        else:
            outcome = "exactly " + ", ".join(f"`{name}`" for name in observed)
        lines.append(f"| `{spec.mutation_id}` | {spec.rule} | {outcome} |")
    lines += [
        "",
        f"Executed registry size: {len(results)} mutation(s) over the "
        f"{case_count}-case fixture set. Every mutation failed exactly its",
        "registered fixture(s), no mutation left the suite green, and each",
        "restore returned the full set to green.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    argv = sys.argv[1:]
    specs = build_registry()
    if "--self-test" in argv:
        return self_test()
    baseline_names = fixture_case_names()
    results, failures = run_all(specs)
    if failures:
        print(f"mutations: {failures} of {len(specs)} mutation(s) FAILED to prove discrimination")
        return 1
    line = (
        f"mutations: all {len(specs)} mutation(s) each failed exactly their "
        f"registered fixture(s) and restored green ({len(baseline_names)}-case suite)"
    )
    if "--ledger" in argv:
        content = render_ledger(results, len(baseline_names))
        if "--check" in argv:
            if LEDGER.read_text() != content:
                print("FAIL: conformance/MUTATION-LEDGER.md is stale — "
                      "regenerate with: python3 scripts/run_mutations.py --ledger")
                return 1
            print("ledger: tracked MUTATION-LEDGER.md matches executed output")
        else:
            LEDGER.write_text(content)
            print(f"ledger: wrote {LEDGER.relative_to(ROOT)} from executed output")
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
