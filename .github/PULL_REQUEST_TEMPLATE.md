## What this change does

<!-- One or two sentences. If it changes normative text, name the
section(s) and whether the change is major, minor, or patch under
governance/GOVERNANCE.md. -->

## Checklist

- [ ] All gates pass locally:
      `python3 conformance/runner.py`,
      `python3 scripts/check_prose_registration_parity.py`,
      `python3 scripts/check_publication_boundary.py` (and `--self-test`)
- [ ] Every commit carries a DCO `Signed-off-by` line (`git commit -s`)
- [ ] Normative changes include fixtures proving the rule both ways
- [ ] Major changes include the migration note and updated registration
      artifact
- [ ] No new restatement of the grade ladder (the registration artifact is
      the single producer)
