# Governance and versioning

## Versioning

This specification and its registration artifact version together under
SemVer.

- **Major** — any change to grade vocabulary membership, names, or order;
  any change to a rank operation's trigger or effect; any change that makes
  a previously conforming implementation non-conforming against the version
  its claim pins. A major release MUST ship a migration note naming every
  changed member.
- **Minor** — new non-normative material (handbook chapters, fixtures that
  test already-normative rules), new counted populations, clarifications
  that do not change conformance outcomes for the pinned version.
- **Patch** — editorial fixes with no conformance effect.

Conformance claims are **version-pinned**: a claim names the exact
`major.minor` it was demonstrated against ("conforms to GVC 1.2"), never a
bare major ("conforms to GVC 1"). New counted populations are minor because
they do not invalidate a claim pinned to an earlier minor; under the
specification's fail-closed comparison rule (spec section 9.2) an
earlier-minor conformer visibly **fails** the new population's fixture
rather than silently skipping it, which is exactly what a pinned claim
predicts. Every new counted population MUST ship a solo-witness fixture in
the same release that introduces it.

The ladder is frozen within a major version. Extension happens by major
version, never by a conformer adding local grades: a value outside the
vocabulary orders strictly below every member by rule, so a local extension
is visible as non-conformance rather than silent divergence.

## Pre-agreed revisit triggers

These are measurements agreed in advance, not renegotiations:

- **Custody attestation ships** → the tied-set MAX rule (spec section 5,
  "Tied top tier") is re-opened toward fail-closed in that same version,
  and the trust boundary's attestation alternative (spec section 10) is
  revived. The spec's section 10 extension point and this trigger
  reference each other.
- **The failed-declared population is observed non-trivial post-v1** →
  the ran-and-failed rule is re-opened toward a cap or demotion (spec
  section 5, "Ran-and-failed declared oracles").

## Who decides

Today this specification is stewarded by a single organization: the
maintainers of this repository decide vocabulary changes. That is stated
plainly rather than dressed up — a committee of one is manufactured quorum,
and this document does not pretend to multi-stakeholder process it does not
have. What constrains the maintainers instead is machinery: every change
must survive the same gates, fixtures, and migration obligations that bind
any contributor.

A proposed change enters as a pull request that must include: the migration
note, the updated registration artifact, updated fixtures proving the new
rule both ways, and a passing run of every gate in `scripts/`.
Implementation convenience is an input to the discussion, never an
override; conformer feedback is solicited and weighed on the same terms.

### Path to shared authority

The transition out of single-organization stewardship has a named,
countable, externally observable trigger: **when two or more independent
implementations publish passing version-pinned conformance runs, a
specification council forms with at least one seat per conformer
organization; vocabulary changes thereafter require council approval.**
An implementation is independent when it is produced outside this
repository's maintainer organization; a conformance run counts when it
meets the claim requirements of spec section 9 (version-pinned, with
machine-readable runner output).

### Succession

If the current maintainers become unable or unwilling to steward the
specification before the council trigger fires, stewardship passes to the
most active conformer organization willing to accept it, carrying the
patent non-assert covenant with it (see `PATENTS.md` — the covenant binds
successors and assigns, so a stewardship handoff never narrows the grant
already made).

## Contributions and IPR

Inbound contributions require a Developer Certificate of Origin sign-off
(the `DCO` file; process in `CONTRIBUTING.md`). The outbound patent
posture — an OWFa 1.0 non-assert covenant over the specification's
Necessary Claims — is stated in `PATENTS.md`. Conformance claims are
version-pinned and evidence-backed per spec section 9; the claim policy is
restated in `PATENTS.md` and `CONTRIBUTING.md`.

## Self-grading releases

Every tagged release publishes its own verdict custody record, produced by
the release workflow:

- the conformance-fixture run is the release's declared oracle; the record
  is produced by the reference derivation in `conformance/runner.py`, never
  hand-constructed;
- the release sits honestly at `constructed_check`: the judge is authored
  in the repository it judges, which is that grade's ceiling under the
  same-chain rule — the record does not claim independence it does not have;
- custody triples name the judge author (this repository's maintainers),
  the judge runner (the CI executor), and the release producer;
- the same-chain cap applies honestly: when judge author and release
  producer share a chain, the record says so;
- a failing gate mints no record.

A verified independent-conformer lift may be specified post-v1; until an
independent parity run can be verified — not merely asserted — no release
record claims the independent-reproduction grade.

Per the specification's normative anti-claim, the record states evidence
strength for the release artifacts — never that the specification is
"correct".

## Licenses

Normative prose: CC-BY-4.0. Registration artifact, fixtures, reference
runner, gate scripts: Apache-2.0.
