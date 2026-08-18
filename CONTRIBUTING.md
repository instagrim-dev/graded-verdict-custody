# Contributing

Thank you for your interest in the Graded Verdict Custody specification.
This document covers how to propose changes, what a change must carry, and
the legal terms that travel with a contribution.

## Ground rules

- **Vocabulary changes are major.** Grade membership, names, order, and
  rank-operation semantics are frozen within a major version. See
  `governance/GOVERNANCE.md` for the versioning policy and who decides.
- **Every normative change ships its proof.** A pull request that changes a
  normative rule must include: the migration note (for major changes), the
  updated registration artifact when the vocabulary moves, and updated
  fixtures proving the new rule **both ways** (a fixture that passes under
  the new rule and would fail under the old one, and vice versa).
- **All gates green.** Run the full gate set locally before opening a pull
  request:

```sh
python3 conformance/runner.py
python3 scripts/check_prose_registration_parity.py
python3 scripts/check_publication_boundary.py
python3 scripts/check_publication_boundary.py --self-test
```

## Developer Certificate of Origin (sign-off required)

This repository uses the Developer Certificate of Origin, version 1.1
(the `DCO` file at the repository root). Every commit MUST carry a
`Signed-off-by` line matching the commit author:

```sh
git commit -s
```

The sign-off certifies that you have the right to submit the contribution
under this repository's licenses. Pull requests containing commits without
a sign-off will not be merged.

## Licensing of contributions

- Normative prose (`spec/`, `governance/`, `handbook/`, and root
  documentation): CC-BY-4.0.
- Registration artifact, fixtures, reference runner, and gate scripts:
  Apache-2.0.

By contributing, you agree your contribution is licensed under the license
covering the files it touches. The patent posture for the specification —
including the non-assert covenant that published contributions fall under —
is stated in `PATENTS.md`.

## Conformance claims and naming

Conformance claims are governed by spec section 9: claims MUST be
version-pinned and accompanied by machine-readable runner output. Do not
describe an implementation as "GVC-conformant" in documentation, marketing,
or release notes without a passing, version-pinned conformance run artifact
to point at. See `PATENTS.md` for the full statement of this policy.

## Reporting issues

- Bugs in the runner, fixtures, or gate scripts: open a bug report issue.
- Ambiguities or questions about the specification's normative text: open a
  spec-question issue. Cite the section and quote the sentence at issue.
- Security-sensitive reports: see `SECURITY.md` — do not open a public
  issue.
