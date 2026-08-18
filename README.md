# Graded Verdict Custody — specification

**Publication is gated: every tracked byte passes the publication-boundary
check in CI (`scripts/check_publication_boundary.py`), and the flip
procedure additionally runs its `--history` mode.**

Graded Verdict Custody (GVC) is a doctrine for delegated work: every
delegated unit carries a **typed oracle-strength grade** and a **custody
record** naming who authored the judge, who ran it, and who produced the
work. Grades state **evidence strength, never correctness**.

## Layout

| Path | What it is | License |
| --- | --- | --- |
| `spec/graded-verdict-custody.md` | The normative specification (RFC-2119 register) | CC-BY-4.0 |
| `registration/verdict-grade-registration.json` | The canonical vocabulary registration artifact — the single public producer of the grade vocabulary | Apache-2.0 |
| `conformance/` | Language-neutral derivation fixtures + the reference runner | Apache-2.0 |
| `governance/GOVERNANCE.md` | Versioning and change policy (vocabulary changes are major) | CC-BY-4.0 |
| `handbook/operator-discipline.md` | Non-normative operator handbook: the working habits the spec makes possible | CC-BY-4.0 |
| `scripts/` | CI gates (prose↔registration parity, publication boundary) + release custody record builder | Apache-2.0 |

## Checks

```sh
python3 conformance/runner.py                     # all derivation fixtures
python3 scripts/check_prose_registration_parity.py # spec prose == registration
python3 scripts/check_publication_boundary.py      # no private-provenance residue
python3 scripts/check_publication_boundary.py --self-test # gate polarity
```

## Self-grading releases

Every tagged release runs the gates above as its declared judge and attaches
its own verdict custody record, produced by the reference derivation
(`scripts/build_release_custody_record.py`, `.github/workflows/release.yml`).
The record sits honestly at `constructed_check` — the judge is authored in
the repository it judges — and states evidence strength for the release
artifacts, never correctness. See `governance/GOVERNANCE.md`.

## Conformance

The conformance bar is defined **once**, in the specification's section 9,
and this README deliberately does not restate it as a second phrasing:
registration identity on exactly the fields section 9.1 enumerates —
`schema_version` and `ordered_grades` — plus fixture projection per
section 9.2 and the anti-claim per section 9.3.

## Licensing

Normative prose is CC-BY-4.0; the registration artifact, fixtures, reference
runner, and gate scripts are Apache-2.0 so implementations can vendor them.
Full texts: `LICENSE-CC-BY-4.0`, `LICENSE-APACHE-2.0`.

## Contributing and policies

- `CONTRIBUTING.md` — how to propose changes; DCO sign-off is required
- `SECURITY.md` — private reporting for grade-inflation and gate-evasion defects
- `CODE_OF_CONDUCT.md` — Contributor Covenant 2.1
- `PATENTS.md` — OWFa 1.0 patent non-assert covenant + conformance-claim policy
- `CHANGELOG.md` — notable changes, Keep-a-Changelog format
