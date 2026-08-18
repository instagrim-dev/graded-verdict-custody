#!/usr/bin/env python3
"""Leg A — producer self-consistency.

The ladder enumerated in the spec's normative prose (between the
LADDER:BEGIN/END markers) must match the canonical registration artifact's
ordered_grades exactly, and the registration's producer field must name this
repository — never an implementation. Exit non-zero naming the drift.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "spec" / "graded-verdict-custody.md"
README = ROOT / "README.md"
REGISTRATION = ROOT / "registration" / "verdict-grade-registration.json"
EXPECTED_PRODUCER = "instagrim-dev/graded-verdict-custody"

# Section 9.1's exhaustively enumerated conformance-identity fields. The
# spec section, the README's conformance paragraph, and the registration
# artifact must all agree on exactly this list.
IDENTITY_FIELDS = ["schema_version", "ordered_grades"]

LADDER_BLOCK = re.compile(
    r"<!-- LADDER:BEGIN -->\n(?P<body>.*?)<!-- LADDER:END -->", re.DOTALL
)
LADDER_ITEM = re.compile(r"^\d+\.\s+`([a-z_]+)`\s*$", re.MULTILINE)
BACKTICKED = re.compile(r"`([a-z_]+)`")


def section_text(text: str, heading: str) -> str:
    """Return the body of a markdown section up to the next heading."""
    pattern = re.compile(
        rf"^#+\s+{re.escape(heading)}.*?$(?P<body>.*?)(?=^#+\s|\Z)",
        re.DOTALL | re.MULTILINE,
    )
    match = pattern.search(text)
    return match.group("body") if match else ""


def identity_field_failures() -> list:
    """Leg B — conformance-identity field parity across the three surfaces
    that name it: spec section 9.1, README's conformance section, and the
    registration artifact itself."""
    failures = []

    spec_body = section_text(SPEC.read_text(), "9.1 Registration identity")
    if not spec_body:
        return ["spec has no '9.1 Registration identity' section"]
    spec_fields = [
        f for f in BACKTICKED.findall(spec_body) if not f.endswith(".json")
    ]
    if spec_fields != IDENTITY_FIELDS:
        failures.append(
            f"spec 9.1 identity fields {spec_fields} != {IDENTITY_FIELDS}"
        )

    readme_body = section_text(README.read_text(), "Conformance")
    if not readme_body:
        return failures + ["README has no 'Conformance' section"]
    readme_fields = [f for f in BACKTICKED.findall(readme_body)]
    if readme_fields != IDENTITY_FIELDS:
        failures.append(
            f"README conformance section names {readme_fields}; it must name "
            f"exactly the section 9.1 identity fields {IDENTITY_FIELDS}"
        )

    registration = json.loads(REGISTRATION.read_text())
    missing = [f for f in IDENTITY_FIELDS if f not in registration]
    if missing:
        failures.append(f"registration lacks identity field(s) {missing}")
    return failures


def main() -> int:
    match = LADDER_BLOCK.search(SPEC.read_text())
    if not match:
        print("FAIL: spec has no LADDER:BEGIN/END block")
        return 2
    prose_ladder = LADDER_ITEM.findall(match.group("body"))
    if not prose_ladder:
        print("FAIL: LADDER block enumerates no grades")
        return 2

    registration = json.loads(REGISTRATION.read_text())
    registered = registration.get("ordered_grades", [])

    failures = 0
    if prose_ladder != registered:
        failures += 1
        print("FAIL: prose ladder != registration ordered_grades")
        print(f"  prose:        {prose_ladder}")
        print(f"  registration: {registered}")

    producer = registration.get("producer", "")
    if producer != EXPECTED_PRODUCER:
        failures += 1
        print(
            f"FAIL: registration producer is {producer!r}; the canonical "
            f"artifact must name {EXPECTED_PRODUCER!r} — an implementation "
            "identity here means the authority flip silently did not happen"
        )

    for failure in identity_field_failures():
        failures += 1
        print(f"FAIL: {failure}")

    if failures:
        return 1
    print(
        f"parity: prose ladder == registration ({len(registered)} grades); "
        f"producer ok; identity fields {IDENTITY_FIELDS} agree across "
        "spec 9.1, README, and registration"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
