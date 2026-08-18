# Operator discipline: working under graded verdict custody

**Non-normative.** This handbook teaches the working habits the
[specification](../spec/graded-verdict-custody.md) makes possible. Grades and
rank-operation semantics come from the spec; nothing here adds or changes a
rule.

## The inversion

IDE-era trust was comprehension: you believed a change because you read it.
At delegation volume, reading *feels* like verification while providing
`review_only`-grade evidence at best. Custody-as-trust replaces it:

1. **Declare judges before work.**
2. **Read typed evidence after it.**
3. **Spend attention where evidence is weakest.**

## Six literacies

Each replaces a named prior habit.

| # | Literacy | Habit it replaces | New move |
|---|----------|-------------------|----------|
| 1 | Evidence grading | "I read the diff, so it's fine" | Read the ladder first; eyeball review *is* `review_only` — know what it cannot claim |
| 2 | Judge declaration | Prose acceptance criteria checked by hand afterward | Name the executable judge before delegating |
| 3 | Attention routing | Reviewing in arrival order | Work weakest-evidence-first; allocate minutes by evidence deficit × reversibility |
| 4 | Action classing | "Look at everything before anything merges" | Grade × reversibility → act now / ask or look up / hand off |
| 5 | Demotion vocabulary | Binary pass/fail intuition | Each rank operation names a move: unrun → re-run the judge; same-chain-capped → get an independent judge; stale → re-judge; conflict → adjudicate |
| 6 | Custody reading | "Tests pass" with no subject | Ask *whose* tests: oracle author vs runner vs work producer; self-judged work is a visible conflict of interest |

## Two anti-lessons

1. **`unverified` does not mean wrong.** It means no declared judge produced
   evidence — including "you never declared one". Read it as a mirror on the
   delegation, not an alarm about the work.
2. **A confident summary is not evidence.** Producer self-report is the most
   fluent, least trustworthy signal; the spec's producer-mint prohibition
   exists for exactly this.

## The first drill

Run the same small task twice: once bare, once with a declared validation
command. Diff the two verdict records. The `unverified` → resolved-oracle
flip is the doctrine experienced in under two minutes.

## Observability span projection (implementation-local)

Grades and counted populations are natural observability material, but the
specification's conformance identity deliberately covers only
`schema_version` and `ordered_grades` — how an implementation projects
grades onto telemetry span attributes is implementation-local. One habit is
worth carrying anyway: project **fail-closed**. Clamp any value outside the
registered vocabulary to an explicit `unclassified` label that is itself
counted, rather than passing unknown strings through — a silently degrading
projection looks identical to a healthy one.

## What the human still exclusively owns

- **Irreversibility decisions** — weak-evidence irreversible actions route to
  a human by construction.
- **Judge quality** — choosing what constitutes a real oracle is the skill
  that compounds.
- **Product contracts.**
