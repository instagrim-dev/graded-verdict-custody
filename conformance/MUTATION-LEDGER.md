# Conformance mutation ledger

GENERATED FILE — regenerated from executed harness output by
`python3 scripts/run_mutations.py --ledger`; do not edit by hand
(CI re-derives it and fails on drift).

Each derivation rule is proven load-bearing by executing
`scripts/run_mutations.py`: every registered mutation is applied to a
temporary copy of the reference runner, the suite is run, the harness
asserts EXACTLY the named fixture(s) fail and nothing else, the
original bytes are restored, and the suite is asserted green again.
A mutation under which every case passes is a harness FAILURE
(fail-closed), and that polarity is itself proven by
`python3 scripts/run_mutations.py --self-test`, which pushes a
deliberately vacuous mutation through the same loop and requires its
rejection.

Restored baseline after every row: `all 28 case(s) passed`.

| Mutation | Rule under proof | Observed failing case(s) |
| --- | --- | --- |
| `proof_exemption_removed` | section 5 step 3.1: the kernel proof exemption is load-bearing | exactly `same_chain_cap_exempts_kernel_proof` |
| `unrun_cap_disabled` | section 5 step 2: the unrun-declared cap is load-bearing | exactly `conflict_demotion_unverified_demotes_to_itself`, `unbindable_not_counted_at_unverified`, `unrun_declared_cap_fires` |
| `conflict_demotion_returns_same_tier` | section 5 step 3.2: demotion moves one ordinal tier | exactly `composed_ops_retained_in_application_order`, `conflict_demotion_fires_one_ordinal_tier` |
| `staleness_condition_forced_false` | section 5 step 3.3: staleness reversion is load-bearing | exactly `composed_ops_retained_in_application_order`, `relabel_evasion_staleness_still_fires`, `staleness_reversion_fires_on_content_identity_change` |
| `mapping_targets_swapped` | section 9.2: a wrong (still injective/total) mapping fails its witness fixtures | exactly `same_chain_indeterminate_is_counted_not_assumed`, `staleness_unbindable_is_counted_not_exempted_silently` |
| `mapping_folds_two_populations` | section 9.2: folding two canonical populations is non-conformance by rule | mapping validation failed loudly before any case ran (exit 2: `not injective`; `not total`) |
| `tie_break_reverted_to_array_order` | section 5 tied-set MAX is order-independent (the twins exist because one order coincides with pre-repair behavior) | exactly `tied_top_tier_all_capped_folds_once`, `tied_top_tier_uncapped_member_wins_order_ab` |
| `tied_uncap_increment_zeroed` | section 5/7: tied-uncap observability population is load-bearing | exactly `tied_top_tier_uncapped_member_wins_order_ab`, `tied_top_tier_uncapped_member_wins_order_ba` |
| `failed_declared_increment_zeroed` | section 5: ran-and-failed declared oracles are counted per oracle | exactly `composed_ops_retained_in_application_order`, `conflict_demotion_fires_one_ordinal_tier`, `conflict_demotion_unverified_demotes_to_itself`, `failed_declared_counted_and_flagged` |
| `failed_flag_hardcoded_true` | section 5: failed_declared_evidence flag polarity (not set when none failed) | exactly `passed_only_not_flagged_failed_declared` |
| `kernel_kind_requirement_dropped` | section 5 step 3.1: the proof exemption requires kernel kind | exactly `agent_authored_proof_same_chain_capped` |
| `proof_kernel_exempt_increment_zeroed` | section 7: kernel-kind proof exemptions are counted | exactly `same_chain_cap_exempts_kernel_proof` |
| `cap_regated_on_agent_kind` | section 5 step 3.1: the same-chain cap is kind-free (pre-repair kind gating fails) | exactly `author_chain_unbound_counted_distinctly`, `human_author_same_chain_caps` |
| `unbound_folded_into_indeterminate` | section 5 step 3.1: author-chain-unbound is distinct from same-chain-indeterminate | exactly `author_chain_unbound_counted_distinctly` |
| `conflict_derivation_forced_false` | section 5 step 3.2: conflict is derived from the declared set, never caller-supplied | exactly `composed_ops_retained_in_application_order`, `conflict_demotion_fires_one_ordinal_tier`, `conflict_demotion_unverified_demotes_to_itself` |
| `applied_ops_reversed` | section 5 step 4: applied rank operations are retained in application order | exactly `composed_ops_retained_in_application_order` |
| `oracle_runner_triple_dropped` | section 3: custody role triples are carried on the record | exactly `composed_ops_retained_in_application_order`, `conflict_demotion_fires_one_ordinal_tier` |
| `missing_admission_branch_disabled` | section 8: fail-closed admission is load-bearing | exactly `missing_admission_evidence_fails_closed` |
| `base_derivation_min_instead_of_max` | section 5 step 1: the base grade is the rank-MAXIMUM over ran-and-passed tiers | exactly `passed_only_not_flagged_failed_declared` |
| `producer_mint_admitted` | section 6: a producer-supplied grade is never admitted; the derived record governs | exactly `producer_mint_rejected_derived_governs` |
| `unknown_grade_ranks_above_all` | section 2: a value outside the vocabulary ranks strictly below every member | exactly `unknown_grade_ranks_zero_below_unverified` |
| `unbindable_increment_zeroed` | section 5 step 3.3 / section 7: unbindable content identity is counted, never silently exempted | exactly `staleness_unbindable_is_counted_not_exempted_silently` |
| `indeterminate_increment_zeroed` | section 5 step 3.1 / section 7: same-chain-indeterminate is counted, never assumed | exactly `same_chain_indeterminate_is_counted_not_assumed` |
| `degraded_increments_zeroed` | section 7: the degraded population counts each applied step-3 rank operation | exactly `agent_authored_proof_same_chain_capped`, `composed_ops_retained_in_application_order`, `conflict_demotion_fires_one_ordinal_tier`, `human_author_same_chain_caps`, `relabel_evasion_staleness_still_fires`, `same_chain_cap_fires_for_same_chain_agent_author`, `staleness_reversion_fires_on_content_identity_change`, `tied_top_tier_all_capped_folds_once` |

Executed registry size: 24 mutation(s) over the 28-case fixture set. Every mutation failed exactly its
registered fixture(s), no mutation left the suite green, and each
restore returned the full set to green.
