# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) as specialized by
`governance/GOVERNANCE.md` (vocabulary changes are major; new counted
populations are minor; conformance claims are version-pinned).

## [1.0.0] - 2026-08-18

Initial public release: specification v1 (six-grade ladder, custody role
triples, four rank operations with normative application order, declared-oracle
resolution, admission, custody record, conformance program), canonical grade
registration artifact, 28-case language-neutral fixture corpus with reference
runner, executable mutation harness (24 registered mutations), publication
boundary gate with polarity self-test, operator-discipline handbook, and
governance with version-pinned conformance claims.

### Added

- OSS hygiene baseline: contributing guide with DCO sign-off requirement,
  security policy, code of conduct (Contributor Covenant 2.1), issue and
  pull-request templates, patent non-assert posture (`PATENTS.md`, OWFa 1.0),
  and this changelog.
- Red-path test for the release custody record builder: a failing gate mints
  no record; a passing run's record equals the reference derivation's output.

### Changed

- The release custody record is now produced by the reference derivation in
  `conformance/runner.py`, never hand-constructed. Releases self-grade at
  `constructed_check`, the honest ceiling for a judge authored in the
  repository it judges.
- Governance framing rewritten: honest single-organization stewardship today,
  with a named, countable trigger for shared authority (a specification
  council forms when two or more independent implementations publish passing
  version-pinned conformance runs).
- CI workflows hardened: least-privilege `permissions` and SHA-pinned actions.

### Removed

- The release interop lift: a release record can no longer be raised to
  `interop` by an unverified command-line assertion. A verified
  independent-conformer lift may be specified in a future version.
