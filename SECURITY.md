# Security policy

## What counts as a security issue here

This repository ships a specification, a reference derivation runner,
conformance fixtures, and CI gate scripts. Security-relevant reports
include:

- a derivation rule (as specified or as implemented in
  `conformance/runner.py`) that lets a work producer raise their own
  effective grade, evade a rank operation, or mint a grade the derivation
  would not produce;
- a gate script defect that lets residue or a policy violation pass as
  clean (including ways to make a gate report green without scanning);
- a fixture or registration artifact defect that makes a non-conforming
  implementation appear conforming;
- vulnerabilities in the release tooling or workflows (for example, a way
  to publish a release custody record that a failing gate should have
  blocked).

The specification's normative anti-claim applies to this policy too: a
grade states evidence strength, never correctness. A report that an
implementation treats a grade as a correctness verdict is a conformance
bug, and welcome.

## How to report

Use GitHub's **private vulnerability reporting** on this repository
(Security tab, "Report a vulnerability"). Do not open a public issue for a
report that could be exploited before a fix lands.

Please include: the affected file and line or spec section, a minimal
reproduction (a fixture-shaped input is ideal), and the outcome you
expected versus what happens.

## What to expect

- Acknowledgement within 7 days.
- An assessment of whether the report is a specification defect (errata or
  a versioned change per `governance/GOVERNANCE.md`) or a tooling defect
  (fixed forward in the scripts or workflows).
- Credit in the changelog on request.

There is no bug bounty.
