# Graded Verdict Custody — Specification v1 (draft)

The key words MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are to be
interpreted as described in RFC 2119.

## 1. Purpose and anti-claim

Graded Verdict Custody (GVC) types the evidence behind a delegated unit of
work. Every terminalized unit carries a **verdict custody record**: an
effective grade from a closed, ordered vocabulary, the true evidence kind
that was produced, custody role triples, and the rank operations applied.

**Normative anti-claim.** A grade states **evidence strength**. A conformer
MUST NOT present any grade — including the strongest — as a statement that
the work is *correct*. Rendering, documentation, or tooling that presents
graded work as correct — rather than as evidenced — does not conform.
Every rendering surface that shows a grade MUST also show the record's
`failed_declared_evidence` flag when it is set (section 5): a flagged grade
rendered bare presents evidence strength the record itself disclaims, and
does not conform.

## 2. The grade vocabulary

The vocabulary is closed and ordered by evidence strength, strongest first:

<!-- LADDER:BEGIN -->
1. `proof`
2. `known_answer`
3. `interop`
4. `constructed_check`
5. `review_only`
6. `unverified`
<!-- LADDER:END -->

- The canonical machine-readable form is
  `registration/verdict-grade-registration.json`. That artifact is the
  **single producer** of this vocabulary. A conformer MUST derive or assert
  its vocabulary against it and MUST NOT restate the ladder as an
  independent source of truth.
- Ordering MUST be exposed to consumers through an order predicate derived
  from the registration, never through string comparison. Rank is ordinal —
  strictly ordered, no arithmetic meaning; for example, an implementation
  may assign `proof` = 6 down to `unverified` = 1.
- A value outside the vocabulary MUST order strictly below every
  vocabulary member — below `unverified` — so an unknown grade can never
  outrank a real one (in the example assignment above, rank 0).
- Vocabulary membership, names, and order are frozen within a major version
  (see `governance/GOVERNANCE.md`).

### 2.1 Grade meanings

| Grade | Evidence it states |
| --- | --- |
| `proof` | A machine-checked proof or equivalent kernel-judged evidence |
| `known_answer` | Output matched an answer fixed before the work ran |
| `interop` | An independent implementation or party reproduced/accepted the result |
| `constructed_check` | An executable check constructed for this work ran and passed |
| `review_only` | An intelligent reader examined the work; no executable judge ran |
| `unverified` | No declared judge produced evidence |

**Kernel.** A judge is a *kernel* when its verdict is determined solely by
the checked artifact plus a fixed, versioned, independently re-runnable
checker whose acceptance conditions are not authored within the judged
work's delegation chain. An author triple carries `kind: kernel` only for
such a judge; a judge whose acceptance conditions the delegation chain can
influence is `agent` or `human` authorship, whatever tier it produces.
Like every custody field, `kind` is declared, not attested — see the trust
boundary in section 10.

## 3. Custody roles

A custody record MUST carry three role triples, each `{identity, kind,
chain_id}` with `kind` one of `human`, `agent`, `kernel`:

- **oracle author** — who authored the judge that produced the base grade;
- **oracle runner** — who executed that judge;
- **work producer** — who produced the judged work.

`chain_id` names the delegation chain the identity acted within. Custody
exists so a consumer can always ask *whose tests* — self-judged work is a
visible conflict of interest, not an error.

### 3.1 Chain identity

- **Minting.** A `chain_id` is minted by the system that opens a delegation
  chain (the orchestrator or admission authority), never by a participant
  inside the chain. The work producer's `chain_id` is admission-populated:
  a producer MUST NOT be able to blank or choose it.
- **Granularity.** One `chain_id` covers one delegation chain: the root
  delegated unit and every unit transitively delegated from it. Parallel
  chains from the same operator are distinct chains.
- **Equality.** Chain identity comparison is exact string match. There is
  no prefix, hierarchy, or wildcard semantics; two chains are the same
  chain only when their identifiers are byte-equal.
- **Declared, not attested.** Like every custody field, `chain_id` is a
  declaration under the v1 trust boundary (section 10); nothing in v1
  verifies it cryptographically.

An identity outside any delegation chain (for example a human reviewer
acting outside orchestration) carries an empty `chain_id`; section 5
counts that case distinctly rather than guessing.

## 4. Declared oracles

A unit's judges MUST be declared **before** delegation. A declared oracle
carries the grade tier it produces when it passes, its author triple, an
optional way to re-run the judge (for example an executable command), an
optional judged-content identity, and its run/pass state.

- **Observed, not assumed.** A declared oracle's execution MUST be
  observed through evidence the work producer cannot fabricate after the
  fact — for example direct host execution, or a persisted execution
  transcript. A conformer MUST NOT mark an oracle as run because it was
  expected to run.
- **Observed versus declared.** The run/pass state (`ran`, `passed`) is
  observed at derivation time from that execution evidence. The author
  triple and the oracle's judged-content identity are **pure
  declarations**: nothing in v1 verifies them (section 10). A consumer
  reading a custody record MUST NOT treat declared fields as attested.
- Evidence from oracles that were **not** declared before delegation MAY be
  recorded but MUST NOT raise the effective grade.

## 5. Derivation

At terminalization, the effective grade MUST be derived as follows:

1. **Base grade** = the rank-maximum over `{unverified}` and the tiers of
   declared oracles that ran and passed; `unverified` when there are none.
   Because a value outside the vocabulary orders strictly below
   `unverified` (section 2), a passing oracle whose declared tier is not a
   vocabulary member contributes nothing to this maximum, so the base is
   always a vocabulary member. The record's `evidence_kind` is set to the
   base — and is therefore always a vocabulary member — and MUST NOT change
   afterward.

   **Tied top tier.** When two or more declared oracles that ran and passed
   are tied at the rank-maximum tier, the effective grade MUST be the MAX
   over the tied set under every subsequent rank operation: each rank
   operation of step 3 whose predicate depends on the base oracle is
   evaluated against **every** tied oracle, and the derivation keeps the
   most favorable surviving outcome — if any tied oracle escapes a cap, the
   record is uncapped; the record is capped only when every tied oracle is
   capped. A capped fold records the capping operation **once** in
   `applied_rank_ops`, not once per tied member, and an indeterminate
   same-chain question over a tied set counts the indeterminate population
   **once per derivation**, not once per tied member. Derivation MUST NOT
   depend on declaration or input order: the same declared set in any order
   yields byte-identical records.

   **Tie selection.** The record's base-oracle attribution (`author` triple
   and `content_identity`) MUST come from one member of the tied set,
   selected by this rule: prefer the tied oracle that survives the step-3
   predicates uncapped; among those (or among all, when none survives),
   select the lexicographically least `(author.identity, content_identity)`
   pair. The selection is a stable attribution rule, not an evidence
   statement. A derivation in which the tied-set MAX leaves the grade
   uncapped while at least one tied member would have been capped MUST
   count the tied-uncap population (section 7).

   **Ran-and-failed declared oracles.** A declared oracle that ran and did
   not pass contributes nothing to the base grade, and its failure neither
   caps nor demotes the effective grade — failed evidence is weaker
   evidence, not negative evidence. It MUST NOT be invisible: the
   derivation MUST increment the `failed_declared` population once **per
   declared oracle that ran and did not pass**, and MUST set the record
   flag `failed_declared_evidence` when that count is nonzero. The flag is
   distinct from `conflicting_evidence`: a ran-and-failed oracle **at the
   base tier alongside a passing one** additionally constitutes a same-tier
   disagreement (step 3.2); a ran-and-failed oracle at any other tier sets
   only `failed_declared_evidence`. If the `failed_declared` population is
   observed non-trivial after v1, the designated escalation is a cap or
   demotion rule — a pre-agreed revisit, not a v1 behavior.
2. **Unrun-declared cap.** If any declared oracle did not run, the
   effective grade is capped at `unverified`. A declared judge that never
   judged is missing evidence, not a waiver. Applied as rank operation
   `unrun_declared_cap`. The operation is recorded — and the unrun-declared
   population incremented — only when the cap actually lowers the grade: a
   derivation whose effective grade is already `unverified` records no
   `unrun_declared_cap` operation and increments no counter. This cap is
   counted solely in its own population (section 7) and MUST NOT be counted
   in the `degraded` population.
3. **Rank operations**, in this order:
   1. `same_chain_cap` — if the base oracle's author `chain_id` is
      non-empty and byte-equal to the work producer's `chain_id`
      (section 3.1), the effective grade is capped at `constructed_check`,
      **regardless of the author's `kind`**: the cap keys on chain
      identity because same-chain judgment is a conflict of interest, not
      an error, and the conflict does not depend on whether the author is
      an agent or a human. `proof` is exempt **only when the base oracle's
      author `kind` is `kernel`** (section 2.1): there the kernel, not the
      author, judges. Each kernel-kind proof exemption MUST be counted in
      the `proof_kernel_exempt` population so a relocated `kind` lie stays
      observable. A `proof`-tier base whose author is not a kernel is
      capped like any other tier.
      Empty chains are counted, never guessed. The work producer's
      `chain_id` is admission-populated (section 3.1); if it is
      nonetheless empty, the question is undecidable and the derivation
      MUST count the same-chain-indeterminate population. A base oracle
      author with an empty `chain_id` is the normal chainless case and
      MUST be counted in the **distinct** `author_chain_unbound`
      population — never folded into same-chain-indeterminate, whose
      signal it would destroy. In neither case may the derivation
      silently treat the record as not-same-chain. Both populations are
      counted only when the cap would otherwise be in range — that is,
      when the effective grade at this step ranks above
      `constructed_check` and is not kernel-exempt `proof`. A derivation
      the cap could not have lowered is not counted.
   2. `conflict_demotion` — a same-tier oracle disagreement at the base
      tier demotes the effective grade one ordinal tier and sets the
      conflicting-evidence flag. **A same-tier disagreement exists when,
      among the declared oracles whose tier equals the base grade's tier,
      at least two ran and at least one passed while at least one did not
      pass.** The disagreement MUST be derived by the implementation from
      the declared set at derivation time; it MUST NOT be supplied by the
      caller — a caller-supplied conflict boolean is a producer-controlled
      demotion switch, in both directions. `unverified` demotes to itself.
      Cross-tier disagreement is not conflict. Demotion is ordinal, not
      evidential: `evidence_kind` is retained. The conflicting-evidence
      flag is set by the conflict itself; the `conflict_demotion`
      operation is recorded in `applied_rank_ops` — and counted in
      `degraded` — only when the demotion actually changed the grade.
      A conflict whose effective grade is already `unverified` therefore
      sets the flag while recording no operation and incrementing no
      counter.
   3. `staleness_reversion` — the grade binds to the judged artifact's
      content identity. If the identity at admission differs from the
      identity the base oracle judged, the effective grade reverts to
      `unverified`. There is no triviality exemption. Like the other rank
      operations, the reversion is recorded and counted only when it
      actually lowers the grade: an effective grade already at
      `unverified` cannot revert. If either side of the binding is absent,
      staleness can never fire for the record: the derivation MUST count
      that unbindable population — but only when the surviving effective
      grade at this step ranks above `unverified`. A record whose
      effective grade is already `unverified` has nothing left for
      staleness to protect and is not counted as unbindable.
4. Every applied rank operation MUST be retained on the record, in
   application order.

## 6. Producer-mint prohibition

The effective grade MUST be derived by the consuming system at the single
point where a terminal unit's record is admitted for consumption — exactly
once, with no path that bypasses the derivation ("admission" throughout
this specification names that property, not a particular runtime
component). A grade supplied by the work producer MUST NOT be admitted;
when a producer-supplied grade
disagrees with the derived grade, the implementation MUST reject it, count
the rejection, and let the derived record govern. A producer-supplied grade
that agrees with the derived grade is equally ignored — the derived record
governs in all cases — and only a disagreeing mint increments the rejection
count; agreement increments nothing.

## 7. Counted populations

A conforming derivation MUST keep each of the following populations
separately observable — for example as counters — and MUST NOT fold them
into one figure: derivations capped by an unrun declared oracle; degraded
derivations; producer-mint rejections; unbindable-content-identity
admissions; same-chain-indeterminate admissions; author-chain-unbound
admissions; declared oracles that ran and failed; kernel-kind proof
exemptions; tied-set uncap events.

The `degraded` population covers exactly the rank operations of section 5
step 3 — `same_chain_cap`, `conflict_demotion`, and `staleness_reversion` —
incremented once per operation actually applied. The unrun-declared cap is
NOT part of `degraded`: it is counted solely in its own population, so a
derivation capped for an unrun oracle and untouched by step-3 operations
increments the unrun-declared population once and `degraded` zero times.
The `failed_declared`, `proof_kernel_exempt`, `author_chain_unbound`, and
`tied_uncap` populations are observability populations, not degradations:
none of them accompanies a grade change by itself, and none is ever
counted in `degraded`.

## 8. Fail-closed admission

A terminal unit with no admission evidence MUST surface as `unverified` with
its provenance labeled (for example `missing_admission_fact`), never dropped:
a queue that silently omits ungraded units is indistinguishable from full
coverage.

## 9. Conformance

An implementation conforms when it satisfies sections 9.1, 9.2, and 9.3.

### 9.1 Registration identity

Its exported registration is identical to the canonical
`registration/verdict-grade-registration.json` in exactly these identity
fields, enumerated exhaustively: `schema_version` and `ordered_grades`.
Any other field an implementation ships in its registration is
implementation-local and carries no conformance weight.

### 9.2 Fixture projection

A projection of `conformance/fixtures/` executes against the
implementation's real derivation and every case passes.

Counted populations are compared **per canonical population**, never by
whole-structure equality:

- The **canonical population identifiers** are the counter keys used by
  `conformance/fixtures/` (one per population named in section 7). An
  implementation MAY spell its counters locally, but MUST declare a mapping
  from its local spellings to the canonical population identifiers. The
  mapping MUST be **injective** on canonical populations — folding two
  canonical populations onto one local counter is non-conformance by rule —
  MUST be **static** and **total** over the canonical population
  identifiers, and MUST be declared **once per implementation**, never per
  case.
- A projection MUST compare **every** canonical population the
  specification version declares, for every case. A canonical population
  the fixture's expectation does not name expects a count of zero; absence
  is an expectation, not a skip.
- A canonical population the implementation's mapping does not cover is a
  comparison **failure** for every case — fail-closed, never a skip.
- Implementation-local counters outside the mapping's image are local
  concerns and are not compared.

### 9.3 Anti-claim conformance

It honors the anti-claim in section 1 on every rendering surface.

**Decidable floor.** This clause has a minimum executable check: a
conformer's shipped default rendering surfaces MUST NOT match the
forbidden-vocabulary predicate — the class of phrasings that present a
grade as a correctness verdict rather than an evidence statement. The
predicate is maintained executably in this repository as the
correctness-claim class of `scripts/check_publication_boundary.py` and is
seeded in that gate's self-test fixture, so its polarity is itself tested.
Passing the predicate is necessary, never sufficient: the floor decides
the vocabulary of default surfaces, not every rendering a conformer can
produce.

## 10. Trust and security considerations

**The v1 trust boundary.** Verifying that judges really were declared
before delegation — and that custody fields are what they claim — is an
explicit **non-goal of v1**. `ran` and `passed` are observed from
execution evidence (section 4); everything else in a custody record —
author triples, `kind`, `chain_id`, judged-content identities — is
**declaration, not attestation**. v1 types honest data; it does not
authenticate it.

**Advisory rank operations under v1 trust.** Because author triples are
declared, every rank behavior keyed on them is **advisory against an
adversarial producer**: the same-chain cap (section 5 step 3.1), the
kernel-kind proof exemption (section 5 step 3.1), and tied-set composition
(section 5 step 1). A consumer MUST NOT read the *absence* of a cap as
adversarially-robust evidence of independence — an author triple that lies
about `kind` or `chain_id` evades all three. The observability populations
(`proof_kernel_exempt`, `tied_uncap`, `same_chain_indeterminate`,
`author_chain_unbound`) exist so those patterns stay measurable even when
they cannot be prevented.

**What violating the boundary buys.** A producer who can declare oracles
retroactively — after seeing what passed — converts declaration into grade
inflation: the unrun-declared cap never fires for judges quietly undeclared
after the fact, and a same-chain judge can be re-declared under a fabricated
chain. Deployments SHOULD bind declaration time to an event the producer
does not control.

**Extension point.** A future version MAY define attestation profiles that
bind this boundary (signed declarations, verifiable custody). The tied-set
MAX rule of section 5 is pre-committed for re-examination toward
fail-closed in the same version that ships custody attestation — see
`governance/GOVERNANCE.md`.

## 11. Prior art and lineage (non-normative)

GVC is small on purpose, and most of its parts have older, larger
relatives. This section records the lineage honestly and, for each
contested design choice, what was considered and why this specification
differs.

**Provenance models — W3C PROV.** The custody role triples (oracle author,
oracle runner, work producer; section 3) are a deliberately simplified
projection of the agent/activity/entity relations in W3C PROV
(PROV-DM, <https://www.w3.org/TR/prov-dm/>). PROV expresses arbitrary
provenance graphs; GVC fixes exactly three roles because its question is
narrower — *whose tests judged this work* — and a closed record can be
compared and gated mechanically where an open graph cannot.

**Supply-chain attestation — in-toto and SLSA.** Binding a verdict to a
judged-content identity (section 5 step 3.3) parallels in-toto attestation
subjects (<https://in-toto.io/>), and a closed ordered ladder of evidence
strength parallels SLSA's build levels (<https://slsa.dev/>). Two honest
deltas: SLSA levels attach to *build integrity process* while GVC grades
attach to *verdict evidence for one unit of work*; and in-toto/SLSA carry
cryptographic attestation, which GVC v1 deliberately does not (section 10)
— its fields are typed declarations, with attestation named as the
extension point.

**Signed transparent statements — IETF SCITT.** SCITT
(<https://datatracker.ietf.org/wg/scitt/about/>) makes claims
tamper-evident and transparently logged, but does not type the *strength*
of the evidence behind a claim. The two are complementary: a SCITT-style
envelope is one candidate binding for the attestation profile section 10
anticipates.

**Assurance cases — GSN and SACM.** Structured argument notations (Goal
Structuring Notation, <https://scsc.uk/gsn>; OMG SACM,
<https://www.omg.org/spec/SACM/>) express *why* a body of evidence
supports a claim, with human-audited argument structure. GVC intentionally
occupies the opposite corner: no argument structure, one mechanical
derivation, so that the result can gate automation at delegation volume.
An assurance case can cite GVC records as evidence nodes.

**Reproducible builds.** The `interop` tier — an independent party
reproduced or accepted the result — inherits its bar from the
reproducible-builds practice (<https://reproducible-builds.org/>): the
strongest practical evidence short of proof is an independent
re-derivation, and independence is a *custody* property, which is exactly
why the same-chain cap exists.

**LLM-judge reliability.** `review_only` deliberately collapses human and
model readers into one tier. The LLM-as-judge literature documents
position bias, verbosity bias, and self-preference in model judges (e.g.
Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena",
2023, <https://arxiv.org/abs/2306.05685>; Panickssery et al., "LLM
Evaluators Recognize and Favor Their Own Generations", 2024,
<https://arxiv.org/abs/2404.13076>). GVC does not adjudicate that
literature; it types the shared property — an intelligent reader, no
executable judge — and leaves reader quality to the custody record
(*whose* review) rather than to the grade.

### Contested choices, considered alternatives

- **A single total order.** Considered: a multi-axis record (evidence
  mechanism × independence × freshness), as the entanglement critique
  suggests. Differ because: rank operations already carry the second axis
  visibly (`applied_rank_ops`, custody triples, counted populations
  preserve what the fold consumed), and a total order is what lets a
  consumer gate mechanically — the axes are recoverable from the record,
  while a partial order would push a comparison policy onto every
  consumer.
- **Six tiers.** Considered: fewer (pass/fail plus provenance) and more
  (SLSA-style sub-levels). Differ because: each tier answers a distinct
  consumer question with a distinct action on failure (re-run, get an
  independent judge, re-judge, adjudicate — see the handbook), and no two
  current tiers collapse without erasing one of those actions; further
  splitting had no fixture-distinguishable semantics to offer.
- **Chain-keyed same-chain cap.** Considered: keying the cap on author
  *kind* (agent self-judgment only), and dropping the cap entirely in
  favor of rendering custody and letting consumers decide. Differ
  because: conflict of interest is a relationship between the judge's
  and producer's delegation chains, not a property of the author's
  species — a human self-judging on their own chain is the same conflict
  — and an uncapped-but-rendered conflict was judged too easy to ignore
  at delegation volume. The cap is an auditor-independence register, not
  an accusation; kind-keying was rejected as the exact escape hatch it
  would create.
