# Conformance mutation ledger

Each derivation rule is proven load-bearing by mutating the reference runner
alone, observing the named fixture fail, and restoring to green. One
mutation per rank operation. All runs executed 2026-08-18 against the
13-case fixture set; restored baseline: `all 13 case(s) passed`.

| Rank operation | Mutation applied to the runner | Fixture that failed |
| --- | --- | --- |
| `same_chain_cap` (proof exemption) | removed the proof-exemption condition | `same_chain_cap_exempts_proof` |
| `unrun_declared_cap` | disabled the cap branch | `unrun_declared_cap_fires` |
| `conflict_demotion` | demotion returned the same tier | `conflict_demotion_fires_one_ordinal_tier` |
| `staleness_reversion` | reversion condition forced false | `staleness_reversion_fires_on_content_identity_change` |

Every mutation failed exactly one named case and the restore returned the
full set to green, so each fixture discriminates its rule rather than
passing vacuously.

## 2026-08-18 — Keyed per-population comparison (spec §9.2)

Runs executed against the 17-case fixture set after the runner moved from
whole-structure counter equality to keyed per-canonical-population
comparison with a declared local-spelling mapping. Restored baseline:
`all 17 case(s) passed`.

| Rule under proof | Mutation applied to the runner | Observed failure |
| --- | --- | --- |
| §9.2 wrong mapping fails a named fixture | swapped the mapping targets for `unbindable_content_identity` and `same_chain_indeterminate` (still injective/total) | exactly `same_chain_indeterminate_is_counted_not_assumed` and `staleness_unbindable_is_counted_not_exempted_silently` failed (the two solo-witness fixtures); exit 1 |
| §9.2 fold is non-conformance by rule | mapped both local counters onto canonical `unbindable_content_identity` | mapping validation failed loudly before any case ran: `not injective` + `not total`; exit 2 |

## 2026-08-18 — Derivation major: tied-set MAX, failed-declared visibility, kernel-gated proof exemption, chain-keyed cap, derived conflict, custody triples, fail-closed admission

Runs executed against the 27-case fixture set; restored baseline after every
row: `all 27 case(s) passed`. The pre-repair witness for order dependence
(two tied top-tier passing oracles graded differently by JSON array order)
now has order-swapped twin fixtures with byte-identical expectations; the
pre-repair witness for the kind-gated cap escape (human author, matching
chain, silently uncapped and uncounted) is `human_author_same_chain_caps`.
Note: the former `same_chain_cap_exempts_proof` fixture was renamed
`same_chain_cap_exempts_kernel_proof` with its author flipped to
`kind: kernel`; agent-authored same-chain `proof` is now capped and has its
own fixture.

| Rule under proof | Mutation applied to the runner | Observed failing case(s) |
| --- | --- | --- |
| §5 tied-set MAX is order-independent | tie-break reverted to input-array order (sort removed) | `tied_top_tier_uncapped_member_wins_order_ab`, `tied_top_tier_all_capped_folds_once` — the swapped twin stays green because one order coincides with pre-repair behavior, which is exactly why the twins exist |
| §5/§7 tied-uncap observability | `tied_uncap` increment zeroed | both order-swapped twins |
| §5 failed-declared counted per oracle | `failed_declared` increment zeroed | `conflict_demotion_fires_one_ordinal_tier`, `conflict_demotion_unverified_demotes_to_itself`, `failed_declared_counted_and_flagged`, `composed_ops_retained_in_application_order` |
| §5 flag polarity (not counted when none failed) | `failed_declared_evidence` hardcoded true | `passed_only_not_flagged_failed_declared` |
| §5 step 3.1 proof exemption requires kernel kind | kernel-kind requirement dropped from the exemption | `agent_authored_proof_same_chain_capped` |
| §7 kernel exemptions counted | `proof_kernel_exempt` increment zeroed | `same_chain_cap_exempts_kernel_proof` |
| §5 step 3.1 cap is kind-free | cap re-gated on `kind: agent` (pre-repair behavior) | `same_chain_cap_exempts_kernel_proof`, `author_chain_unbound_counted_distinctly`, `human_author_same_chain_caps` |
| §5 step 3.1 unbound is distinct from indeterminate | unbound folded into `same_chain_indeterminate` | `author_chain_unbound_counted_distinctly` |
| §5 step 3.2 conflict derived, not caller-supplied | derivation forced to no-conflict | `conflict_demotion_fires_one_ordinal_tier`, `conflict_demotion_unverified_demotes_to_itself`, `composed_ops_retained_in_application_order` |
| §5 step 4 ops retained in application order | `applied_rank_ops` reversed | `composed_ops_retained_in_application_order` |
| §3 custody triples carried on the record | `oracle_runner` triple dropped | `conflict_demotion_fires_one_ordinal_tier`, `composed_ops_retained_in_application_order` |
| §8 fail-closed admission | missing-admission branch disabled | `missing_admission_evidence_fails_closed` |

Every mutation failed at least one named case, no mutation left the suite
green, and each restore returned the full set to `all 27 case(s) passed`.
